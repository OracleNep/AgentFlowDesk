from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .errors import AgentFlowError
from .models import RunRecord, Task, utc_now
from .paths import AGENTFLOW_DIR, find_project_root

DEFAULT_CONFIG = {
    "project_name": "",
    "description": "",
    "default_agent": "manual",
    "commands": {
        "test": "",
        "lint": "",
        "format": "",
    },
    "context": {
        "max_file_chars": 12000,
        "include_git_status": True,
        "include_tree": True,
    },
}


class Store:
    def __init__(self, root: str | Path | None = None):
        self.root = find_project_root(root)
        self.base = self.root / AGENTFLOW_DIR
        self.tasks_file = self.base / "tasks.json"
        self.runs_file = self.base / "runs.json"
        self.config_file = self.base / "config.json"

    def exists(self) -> bool:
        return self.base.is_dir()

    def init(self, project_name: str | None = None, description: str = "") -> None:
        self.base.mkdir(parents=True, exist_ok=True)
        for name in ["context", "exports", "runs", "tmp"]:
            (self.base / name).mkdir(parents=True, exist_ok=True)
        if not self.tasks_file.exists():
            self._write_json(self.tasks_file, {"tasks": []})
        if not self.runs_file.exists():
            self._write_json(self.runs_file, {"runs": []})
        if not self.config_file.exists():
            cfg = dict(DEFAULT_CONFIG)
            cfg["project_name"] = project_name or self.root.name
            cfg["description"] = description
            self._write_json(self.config_file, cfg)

    def require(self) -> None:
        if not self.exists():
            raise AgentFlowError("AgentFlowDesk is not initialized. Run: agentflow init")

    def read_config(self) -> dict[str, Any]:
        self.require()
        cfg = self._read_json(self.config_file)
        merged = dict(DEFAULT_CONFIG)
        merged.update(cfg)
        merged["commands"] = {**DEFAULT_CONFIG["commands"], **cfg.get("commands", {})}
        merged["context"] = {**DEFAULT_CONFIG["context"], **cfg.get("context", {})}
        return merged

    def write_config(self, config: dict[str, Any]) -> None:
        self.require()
        self._write_json(self.config_file, config)

    def list_tasks(self, status: str | None = None) -> list[Task]:
        self.require()
        data = self._read_json(self.tasks_file)
        tasks = [Task.from_dict(item) for item in data.get("tasks", [])]
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def save_tasks(self, tasks: list[Task]) -> None:
        self.require()
        self._write_json(self.tasks_file, {"tasks": [t.to_dict() for t in tasks]})

    def next_task_id(self) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"AF-{today}-"
        max_n = 0
        for task in self.list_tasks():
            if task.id.startswith(prefix):
                try:
                    max_n = max(max_n, int(task.id.rsplit("-", 1)[-1]))
                except ValueError:
                    pass
        return f"{prefix}{max_n + 1:03d}"

    def add_task(self, title: str, goal: str, files: list[str] | None = None,
                 acceptance: list[str] | None = None, notes: str = "",
                 preferred_agent: str = "") -> Task:
        task = Task(
            id=self.next_task_id(),
            title=title,
            goal=goal,
            files=files or [],
            acceptance=acceptance or [],
            notes=notes,
            preferred_agent=preferred_agent,
        )
        tasks = self.list_tasks()
        tasks.append(task)
        self.save_tasks(tasks)
        return task

    def get_task(self, task_id: str) -> Task:
        for task in self.list_tasks():
            if task.id == task_id:
                return task
        raise AgentFlowError(f"Task not found: {task_id}")

    def update_task(self, task: Task) -> None:
        tasks = self.list_tasks()
        for idx, existing in enumerate(tasks):
            if existing.id == task.id:
                task.updated_at = utc_now()
                tasks[idx] = task
                self.save_tasks(tasks)
                return
        raise AgentFlowError(f"Task not found: {task.id}")

    def list_runs(self, task_id: str | None = None) -> list[RunRecord]:
        self.require()
        data = self._read_json(self.runs_file)
        runs = [RunRecord.from_dict(item) for item in data.get("runs", [])]
        if task_id:
            runs = [r for r in runs if r.task_id == task_id]
        return runs

    def add_run(self, run: RunRecord) -> None:
        runs = self.list_runs()
        runs.append(run)
        self._write_json(self.runs_file, {"runs": [r.to_dict() for r in runs]})

    def update_run(self, run: RunRecord) -> None:
        runs = self.list_runs()
        for idx, existing in enumerate(runs):
            if existing.id == run.id:
                runs[idx] = run
                self._write_json(self.runs_file, {"runs": [r.to_dict() for r in runs]})
                return
        raise AgentFlowError(f"Run not found: {run.id}")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8") or "{}")

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
