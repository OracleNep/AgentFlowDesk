from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .context_builder import build_context_pack, detect_commands
from .errors import AgentFlowError
from .exporters import TARGET_FILES, export_context
from .runner import run_task
from .storage import Store

VALID_STATUSES = ["backlog", "running", "review", "done", "blocked"]


def print_table(rows: list[list[str]], headers: list[str]) -> None:
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for row in rows:
        print(fmt.format(*row))


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    store = Store(root)
    store.root = root
    store.base = root / ".agentflow"
    store.tasks_file = store.base / "tasks.json"
    store.runs_file = store.base / "runs.json"
    store.config_file = store.base / "config.json"
    store.init(args.name or root.name, args.description or "")
    cfg = store.read_config()
    detected = detect_commands(root)
    cfg["commands"] = {**cfg.get("commands", {}), **{k: v for k, v in detected.items() if v}}
    store.write_config(cfg)
    print(f"Initialized AgentFlowDesk at {store.base}")
    return 0


def cmd_task_create(args: argparse.Namespace) -> int:
    store = Store()
    task = store.add_task(
        title=args.title,
        goal=args.goal,
        files=args.file or [],
        acceptance=args.acceptance or [],
        notes=args.notes or "",
        preferred_agent=args.agent or "",
    )
    print(f"Created task {task.id}: {task.title}")
    return 0


def cmd_task_list(args: argparse.Namespace) -> int:
    store = Store()
    tasks = store.list_tasks(args.status)
    rows = [[t.id, t.status, t.title, ", ".join(t.files[:3])] for t in tasks]
    if rows:
        print_table(rows, ["ID", "Status", "Title", "Files"])
    else:
        print("No tasks found.")
    return 0


def cmd_task_show(args: argparse.Namespace) -> int:
    store = Store()
    task = store.get_task(args.task_id)
    print(f"# {task.id} — {task.title}\n")
    print(f"Status: {task.status}")
    print(f"Preferred agent: {task.preferred_agent or '<none>'}")
    print(f"Created: {task.created_at}")
    print(f"Updated: {task.updated_at}\n")
    print("## Goal\n")
    print(task.goal or "<empty>")
    print("\n## Files")
    for f in task.files or ["<none>"]:
        print(f"- {f}")
    print("\n## Acceptance")
    for item in task.acceptance or ["User review required"]:
        print(f"- [ ] {item}")
    if task.notes:
        print("\n## Notes\n")
        print(task.notes)
    return 0


def cmd_task_status(args: argparse.Namespace) -> int:
    if args.status not in VALID_STATUSES:
        raise AgentFlowError(f"Invalid status: {args.status}. Valid: {', '.join(VALID_STATUSES)}")
    store = Store()
    task = store.get_task(args.task_id)
    task.status = args.status
    store.update_task(task)
    print(f"Updated {task.id} status to {task.status}")
    return 0


def cmd_context_build(args: argparse.Namespace) -> int:
    store = Store()
    out_dir = build_context_pack(store, args.task_id)
    print(f"Context pack generated: {out_dir.relative_to(store.root)}")
    print(f"Combined prompt: {(out_dir / 'context-pack.md').relative_to(store.root)}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    store = Store()
    targets = args.target or ["agents"]
    written = export_context(store, args.task_id, targets, force=args.force)
    for path in written:
        print(f"Exported {path.relative_to(store.root)}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    store = Store()
    task = store.get_task(args.task_id)
    agent = args.agent or task.preferred_agent or store.read_config().get("default_agent", "manual")
    run = run_task(
        store=store,
        task_id=args.task_id,
        agent=agent,
        command=args.command or "",
        checks=args.check or [],
        timeout=args.timeout,
    )
    print(f"Run {run.id} status: {run.status}")
    print(f"Prompt: {run.prompt_path}")
    print(f"Report: {run.report_path}")
    return 0 if run.status == "finished" else 1


def cmd_runs(args: argparse.Namespace) -> int:
    store = Store()
    runs = store.list_runs(args.task_id)
    rows = [[r.id, r.task_id, r.agent, r.status, r.started_at] for r in runs]
    if rows:
        print_table(rows, ["Run", "Task", "Agent", "Status", "Started"])
    else:
        print("No runs found.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentflow",
        description="AgentFlowDesk: local-first workflow manager for AI coding agents.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="Initialize AgentFlowDesk in a project")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--name", default="")
    p.add_argument("--description", default="")
    p.set_defaults(func=cmd_init)

    task = sub.add_parser("task", help="Manage tasks")
    task_sub = task.add_subparsers(dest="task_cmd", required=True)

    p = task_sub.add_parser("create", help="Create a task")
    p.add_argument("--title", required=True)
    p.add_argument("--goal", required=True)
    p.add_argument("--file", action="append", help="Relevant file or directory; repeatable")
    p.add_argument("--acceptance", action="append", help="Acceptance criterion; repeatable")
    p.add_argument("--notes", default="")
    p.add_argument("--agent", default="")
    p.set_defaults(func=cmd_task_create)

    p = task_sub.add_parser("list", help="List tasks")
    p.add_argument("--status", choices=VALID_STATUSES)
    p.set_defaults(func=cmd_task_list)

    p = task_sub.add_parser("show", help="Show a task")
    p.add_argument("task_id")
    p.set_defaults(func=cmd_task_show)

    p = task_sub.add_parser("status", help="Update task status")
    p.add_argument("task_id")
    p.add_argument("status")
    p.set_defaults(func=cmd_task_status)

    p = sub.add_parser("context", help="Build context packs")
    context_sub = p.add_subparsers(dest="context_cmd", required=True)
    p = context_sub.add_parser("build", help="Build a context pack for a task")
    p.add_argument("task_id")
    p.set_defaults(func=cmd_context_build)

    p = sub.add_parser("export", help="Export task context to agent instruction files")
    p.add_argument("task_id")
    p.add_argument("--target", action="append", choices=sorted(TARGET_FILES), help="Export target; repeatable")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("run", help="Create a run, execute an optional agent command, and generate a review report")
    p.add_argument("task_id")
    p.add_argument("--agent", default="")
    p.add_argument("--command", default="", help="Command to execute. Use {prompt} as context-pack placeholder.")
    p.add_argument("--check", action="append", help="Check command to run after the agent; repeatable")
    p.add_argument("--timeout", type=int, default=None)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("runs", help="List run records")
    p.add_argument("--task-id", default=None)
    p.set_defaults(func=cmd_runs)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (AgentFlowError, FileExistsError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
