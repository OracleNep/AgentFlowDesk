# Context Pack

A Context Pack is a generated prompt bundle for a specific task.

It contains:

1. `task-brief.md` — what should be done and how it will be reviewed
2. `agent-instructions.md` — behavioral instructions for the coding agent
3. `commands.md` — detected or configured test/lint/format commands
4. `environment.md` — file tree and git status
5. `relevant-files.md` — excerpts from files attached to the task
6. `context-pack.md` — combined prompt for export or agent execution

## Why task-level context

A full repository is usually too large and too noisy. A task-level context pack helps:

- reduce repeated copy-paste
- keep agent runs focused
- improve reviewability
- preserve the exact context used for a run

## Export formats

The same context can be exported to:

- `AGENTS.md`
- `CLAUDE.md`
- `.cursor/rules/agentflow.mdc`
- `.codex/instructions.md`
- `GEMINI.md`
