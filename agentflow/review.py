from __future__ import annotations

from pathlib import Path

from .models import RunRecord, Task


def render_review_report(task: Task, run: RunRecord, diff_text: str, stdout: str, stderr: str) -> str:
    checks = "\n".join(
        f"- {'✅' if c.get('returncode') == 0 else '❌'} `{c.get('command')}` — exit {c.get('returncode')}"
        for c in run.checks
    ) or "- No checks configured"
    changed_summary = "Diff captured." if diff_text.strip() else "No git diff captured."
    stdout_excerpt = stdout[-4000:] if stdout else ""
    stderr_excerpt = stderr[-4000:] if stderr else ""
    return f"""# AgentFlowDesk Review Report

## Task

- **ID:** `{task.id}`
- **Title:** {task.title}
- **Status:** {task.status}

## Run

- **Run ID:** `{run.id}`
- **Agent:** `{run.agent}`
- **Command:** `{run.command or '<manual / prompt only>'}`
- **Started:** {run.started_at}
- **Finished:** {run.finished_at or '<not finished>'}
- **Status:** {run.status}

## Acceptance criteria

{chr(10).join(f'- [ ] {item}' for item in task.acceptance) or '- [ ] User review required'}

## Automated checks

{checks}

## Diff summary

{changed_summary}

Full diff path: `{run.diff_path or '<none>'}`

## Stdout excerpt

```text
{stdout_excerpt}
```

## Stderr excerpt

```text
{stderr_excerpt}
```

## Human review checklist

- [ ] The diff is focused on the task goal.
- [ ] No unrelated files were changed.
- [ ] Tests/checks are sufficient.
- [ ] Documentation was updated when needed.
- [ ] The task can be marked as done.
"""
