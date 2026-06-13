# Design

AgentFlowDesk is built around one opinion:

> AI-agent work should be structured like engineering work, not like disposable chat history.

## Pipeline

```text
User Task
  ↓
Task Brief
  ↓
Context Pack Builder
  ↓
Agent Export / Agent Command
  ↓
Logs + Diff + Checks
  ↓
Review Report
  ↓
Reusable Skill
```

## Non-goals

- It is not a model provider.
- It is not a universal autonomous agent framework.
- It is not a replacement for GitHub, Jira, Linear, or IDE tools.
- It does not claim to judge code correctness by itself.

## MVP architecture

```text
agentflow/
  cli.py              argparse CLI entrypoint
  storage.py          local .agentflow JSON store
  models.py           Task and RunRecord models
  context_builder.py  context-pack generation
  exporters.py        AGENTS.md / CLAUDE.md / Cursor / Codex / Gemini exports
  runner.py           run command wrapper and report generation
  review.py           markdown review report renderer
  git_tools.py        git status/diff helpers
```

## Why local-first

AI-agent usage often touches private repositories and unfinished code. The MVP stores metadata, prompts, logs, and reports locally under `.agentflow/`. Users decide which agent CLI or external model gets called.
