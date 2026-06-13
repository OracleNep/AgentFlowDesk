from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from .context_builder import build_context_pack
from .git_tools import git_diff, run_cmd
from .models import RunRecord, utc_now
from .review import render_review_report
from .storage import Store


def make_run_id(task_id: str) -> str:
    return task_id + "-RUN-" + datetime.now().strftime("%H%M%S")


def run_task(store: Store, task_id: str, agent: str = "manual", command: str = "",
             checks: list[str] | None = None, timeout: int | None = None) -> RunRecord:
    store.require()
    task = store.get_task(task_id)
    context_dir = build_context_pack(store, task_id)
    context = (context_dir / "context-pack.md").read_text(encoding="utf-8")

    run_id = make_run_id(task.id)
    run_dir = store.base / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = run_dir / "prompt.md"
    stdout_path = run_dir / "stdout.txt"
    stderr_path = run_dir / "stderr.txt"
    diff_path = run_dir / "diff.patch"
    report_path = run_dir / "review-report.md"

    prompt_path.write_text(context, encoding="utf-8")

    run = RunRecord(
        id=run_id,
        task_id=task.id,
        agent=agent,
        command=command,
        status="running",
        started_at=utc_now(),
        prompt_path=str(prompt_path.relative_to(store.root)),
        stdout_path=str(stdout_path.relative_to(store.root)),
        stderr_path=str(stderr_path.relative_to(store.root)),
        diff_path=str(diff_path.relative_to(store.root)),
        report_path=str(report_path.relative_to(store.root)),
    )
    store.add_run(run)

    stdout = ""
    stderr = ""
    returncode = 0
    if command:
        # The context pack path is passed via env-like shell variable for simple wrappers.
        shell_command = command.replace("{prompt}", str(prompt_path))
        try:
            result = run_cmd(shell_command, store.root, timeout=timeout)
            stdout = result.stdout
            stderr = result.stderr
            returncode = result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = (exc.stderr or "") + f"\n<timeout after {timeout}s>"
            returncode = 124

    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")

    check_results: list[dict] = []
    for check in checks or []:
        try:
            result = run_cmd(check, store.root, timeout=timeout)
            check_results.append({
                "command": check,
                "returncode": result.returncode,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            })
        except subprocess.TimeoutExpired as exc:
            check_results.append({
                "command": check,
                "returncode": 124,
                "stdout": exc.stdout or "",
                "stderr": (exc.stderr or "") + f"\n<timeout after {timeout}s>",
            })

    diff_text = git_diff(store.root)
    diff_path.write_text(diff_text, encoding="utf-8")

    failed_checks = [c for c in check_results if c.get("returncode") != 0]
    if returncode != 0 or failed_checks:
        run.status = "failed"
    else:
        run.status = "finished"
    run.finished_at = utc_now()
    run.checks = check_results
    store.update_run(run)

    report = render_review_report(task, run, diff_text, stdout, stderr)
    report_path.write_text(report, encoding="utf-8")
    return run
