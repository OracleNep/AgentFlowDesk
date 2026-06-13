from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

Status = Literal["backlog", "running", "review", "done", "blocked"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class Task:
    id: str
    title: str
    goal: str
    status: Status = "backlog"
    files: list[str] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)
    notes: str = ""
    preferred_agent: str = ""
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            goal=str(data.get("goal", "")),
            status=data.get("status", "backlog"),
            files=list(data.get("files", [])),
            acceptance=list(data.get("acceptance", [])),
            notes=str(data.get("notes", "")),
            preferred_agent=str(data.get("preferred_agent", "")),
            created_at=str(data.get("created_at", utc_now())),
            updated_at=str(data.get("updated_at", utc_now())),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "goal": self.goal,
            "status": self.status,
            "files": self.files,
            "acceptance": self.acceptance,
            "notes": self.notes,
            "preferred_agent": self.preferred_agent,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass(slots=True)
class RunRecord:
    id: str
    task_id: str
    agent: str
    command: str
    status: str
    started_at: str
    finished_at: str = ""
    prompt_path: str = ""
    report_path: str = ""
    stdout_path: str = ""
    stderr_path: str = ""
    diff_path: str = ""
    checks: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunRecord":
        return cls(
            id=str(data["id"]),
            task_id=str(data["task_id"]),
            agent=str(data.get("agent", "manual")),
            command=str(data.get("command", "")),
            status=str(data.get("status", "unknown")),
            started_at=str(data.get("started_at", "")),
            finished_at=str(data.get("finished_at", "")),
            prompt_path=str(data.get("prompt_path", "")),
            report_path=str(data.get("report_path", "")),
            stdout_path=str(data.get("stdout_path", "")),
            stderr_path=str(data.get("stderr_path", "")),
            diff_path=str(data.get("diff_path", "")),
            checks=list(data.get("checks", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "agent": self.agent,
            "command": self.command,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "prompt_path": self.prompt_path,
            "report_path": self.report_path,
            "stdout_path": self.stdout_path,
            "stderr_path": self.stderr_path,
            "diff_path": self.diff_path,
            "checks": self.checks,
        }
