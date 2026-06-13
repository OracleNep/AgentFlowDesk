from __future__ import annotations

import os
import subprocess
from pathlib import Path


def run_cmd(command: str | list[str], cwd: Path, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    shell = isinstance(command, str)
    return subprocess.run(
        command,
        cwd=str(cwd),
        shell=shell,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def is_git_repo(root: Path) -> bool:
    return (root / ".git").exists() or run_cmd(["git", "rev-parse", "--is-inside-work-tree"], root).returncode == 0


def git_status(root: Path) -> str:
    if not is_git_repo(root):
        return "Not a git repository."
    result = run_cmd(["git", "status", "--short"], root)
    return result.stdout.strip() or "Clean working tree."


def git_diff(root: Path) -> str:
    if not is_git_repo(root):
        return ""
    result = run_cmd(["git", "diff", "--", ":!*.lock"], root)
    return result.stdout


def project_tree(root: Path, max_entries: int = 200) -> str:
    ignored = {".git", ".agentflow", "__pycache__", ".pytest_cache", "node_modules", "dist", "build", ".venv"}
    rows: list[str] = []
    for current, dirs, files in os.walk(root):
        cur = Path(current)
        dirs[:] = [d for d in sorted(dirs) if d not in ignored and not d.startswith(".")]
        files = [f for f in sorted(files) if f not in ignored and not f.endswith((".pyc", ".class"))]
        rel = cur.relative_to(root)
        depth = 0 if str(rel) == "." else len(rel.parts)
        if depth > 3:
            dirs[:] = []
            continue
        indent = "  " * depth
        if str(rel) != ".":
            rows.append(f"{indent}{cur.name}/")
        for f in files[:25]:
            rows.append(f"{indent}  {f}")
        if len(rows) >= max_entries:
            rows.append("  ...")
            return "\n".join(rows)
    return "\n".join(rows) or "<empty>"
