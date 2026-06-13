from __future__ import annotations

import os
from pathlib import Path

from agentflow.context_builder import build_context_pack
from agentflow.exporters import export_context
from agentflow.runner import run_task
from agentflow.storage import Store


def test_task_context_export_and_run(tmp_path: Path):
    root = tmp_path / "demo"
    root.mkdir()
    (root / "hello.py").write_text("print('hello')\n", encoding="utf-8")
    store = Store(root)
    store.root = root
    store.base = root / ".agentflow"
    store.tasks_file = store.base / "tasks.json"
    store.runs_file = store.base / "runs.json"
    store.config_file = store.base / "config.json"
    store.init("demo")

    task = store.add_task(
        title="Add a hello test",
        goal="Create a small test around hello.py",
        files=["hello.py"],
        acceptance=["Context pack is generated"],
    )

    context_dir = build_context_pack(store, task.id)
    assert (context_dir / "context-pack.md").exists()
    assert "hello.py" in (context_dir / "relevant-files.md").read_text(encoding="utf-8")

    written = export_context(store, task.id, ["agents"], force=True)
    assert written[0].name == "AGENTS.md"
    assert written[0].exists()

    run = run_task(store, task.id, agent="manual", command="python hello.py", checks=["python hello.py"])
    assert run.status == "finished"
    assert (root / run.report_path).exists()
