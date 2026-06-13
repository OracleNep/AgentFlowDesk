from __future__ import annotations

from pathlib import Path

from .git_tools import git_status, project_tree, run_cmd
from .models import Task
from .storage import Store

BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".jar", ".war", ".class",
    ".exe", ".dll", ".so", ".dylib", ".ico", ".woff", ".woff2", ".ttf",
}


def detect_commands(root: Path) -> dict[str, str]:
    if (root / "pom.xml").exists():
        return {"test": "mvn test", "lint": "", "format": ""}
    if (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        return {"test": "./gradlew test", "lint": "", "format": ""}
    if (root / "package.json").exists():
        return {"test": "npm test", "lint": "npm run lint", "format": "npm run format"}
    if (root / "pyproject.toml").exists():
        return {"test": "pytest", "lint": "ruff check .", "format": "ruff format ."}
    return {"test": "", "lint": "", "format": ""}


def read_text_excerpt(path: Path, max_chars: int) -> str:
    if path.suffix.lower() in BINARY_EXTS:
        return f"<binary file omitted: {path.name}>"
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"<failed to read: {exc}>"
    except OSError as exc:
        return f"<failed to read: {exc}>"
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n... <truncated by AgentFlowDesk>"
    return text


def build_task_brief(task: Task, project_name: str, description: str) -> str:
    acceptance = "\n".join(f"- [ ] {item}" for item in task.acceptance) or "- [ ] User review required"
    files = "\n".join(f"- `{item}`" for item in task.files) or "- No files specified yet"
    return f"""# Task Brief: {task.title}

## Project

**Name:** {project_name}

{description or "No project description configured."}

## Task ID

`{task.id}`

## Goal

{task.goal}

## Relevant files

{files}

## Acceptance criteria

{acceptance}

## Notes

{task.notes or "No extra notes."}
"""


def build_agent_instructions(task: Task) -> str:
    return f"""# Agent Instructions

You are working on task `{task.id}`: **{task.title}**.

Follow these rules:

1. Read the task brief before editing.
2. Keep the diff focused on the stated goal.
3. Do not make unrelated refactors.
4. Prefer small, reviewable changes.
5. Run the relevant checks if commands are available.
6. Summarize what changed, what was tested, and any remaining risk.

When you finish, provide:

- Changed files
- Implementation summary
- Tests/checks run
- Known limitations
- Review checklist
"""


def build_relevant_files(root: Path, task: Task, max_chars: int) -> str:
    if not task.files:
        return "# Relevant Files\n\nNo files were specified for this task.\n"
    parts = ["# Relevant Files"]
    for item in task.files:
        p = (root / item).resolve()
        try:
            p.relative_to(root.resolve())
        except ValueError:
            parts.append(f"\n## `{item}`\n\n<skipped: outside project root>")
            continue
        if not p.exists():
            parts.append(f"\n## `{item}`\n\n<missing>")
            continue
        if p.is_dir():
            parts.append(f"\n## `{item}`\n\nDirectory tree:\n\n```text\n{project_tree(p, 80)}\n```")
            continue
        excerpt = read_text_excerpt(p, max_chars)
        parts.append(f"\n## `{item}`\n\n```text\n{excerpt}\n```")
    return "\n".join(parts) + "\n"


def build_commands(root: Path, configured: dict[str, str]) -> str:
    detected = detect_commands(root)
    commands = {**detected, **{k: v for k, v in configured.items() if v}}
    lines = ["# Project Commands", ""]
    for name in ["test", "lint", "format"]:
        value = commands.get(name, "")
        lines.append(f"- **{name}:** `{value or '<not configured>'}`")
    lines.append("")
    return "\n".join(lines)


def build_environment(root: Path, include_tree: bool, include_git: bool) -> str:
    parts = ["# Project Environment", ""]
    if include_tree:
        parts.append("## File tree")
        parts.append("```text")
        parts.append(project_tree(root))
        parts.append("```")
    if include_git:
        parts.append("## Git status")
        parts.append("```text")
        parts.append(git_status(root))
        parts.append("```")
    return "\n".join(parts) + "\n"


def build_context_pack(store: Store, task_id: str) -> Path:
    store.require()
    task = store.get_task(task_id)
    config = store.read_config()
    max_chars = int(config.get("context", {}).get("max_file_chars", 12000))
    include_tree = bool(config.get("context", {}).get("include_tree", True))
    include_git = bool(config.get("context", {}).get("include_git_status", True))

    out_dir = store.base / "context" / task.id
    out_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "task-brief.md": build_task_brief(task, config.get("project_name", store.root.name), config.get("description", "")),
        "agent-instructions.md": build_agent_instructions(task),
        "relevant-files.md": build_relevant_files(store.root, task, max_chars),
        "commands.md": build_commands(store.root, config.get("commands", {})),
        "environment.md": build_environment(store.root, include_tree, include_git),
    }
    for name, content in files.items():
        (out_dir / name).write_text(content, encoding="utf-8")

    combined = ["# AgentFlowDesk Context Pack", ""]
    for name in ["task-brief.md", "agent-instructions.md", "commands.md", "environment.md", "relevant-files.md"]:
        combined.append(f"\n---\n\n<!-- {name} -->\n")
        combined.append((out_dir / name).read_text(encoding="utf-8"))
    (out_dir / "context-pack.md").write_text("\n".join(combined), encoding="utf-8")
    return out_dir
