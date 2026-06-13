from __future__ import annotations

from pathlib import Path

AGENTFLOW_DIR = ".agentflow"


def find_project_root(start: str | Path | None = None) -> Path:
    """Find the nearest parent containing .agentflow; fallback to cwd."""
    path = Path(start or ".").resolve()
    if path.is_file():
        path = path.parent
    for candidate in [path, *path.parents]:
        if (candidate / AGENTFLOW_DIR).is_dir():
            return candidate
    return path


def agentflow_dir(root: str | Path | None = None) -> Path:
    return find_project_root(root) / AGENTFLOW_DIR
