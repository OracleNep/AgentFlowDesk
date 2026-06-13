# AgentFlowDesk

AgentFlowDesk is a **local-first task board and context manager for AI coding agents**.

It helps developers turn AI-agent work into structured, reviewable, and reusable workflows:

- Plan coding tasks before sending them to an agent
- Build compact **Context Packs** for each task
- Export instructions to `AGENTS.md`, `CLAUDE.md`, Cursor rules, Codex instructions, and `GEMINI.md`
- Run an optional local agent command and capture prompt, logs, diff, checks, and review report
- Keep AI-agent work auditable instead of scattered across chat windows

> MVP status: CLI-first. The web task board is planned after the core workflow is stable.

## Why this exists

AI coding agents are powerful, but day-to-day usage still has friction:

1. Context has to be copied and rewritten repeatedly.
2. Agent output is hard to review after the session ends.
3. Running multiple agents or tasks in parallel is messy.
4. Successful prompts and workflows are not easy to reuse.
5. Users need a lightweight way to connect task intent, context, diff, tests, and human review.

AgentFlowDesk does not try to replace Claude Code, Codex CLI, Cursor, Gemini CLI, or OpenCode. It gives them a structured workflow layer.

## Quick start

```bash
python -m pip install -e .
agentflow init --name MyProject --description "Demo project using AI coding agents"

agentflow task create \
  --title "Add SARIF ruleId support" \
  --goal "Modify the SARIF reporter so each finding has a stable ruleId." \
  --file src/reporters/sarif.py \
  --acceptance "Unit tests pass" \
  --acceptance "No unrelated files changed" \
  --agent claude-code

agentflow task list
agentflow context build AF-20260613-001
agentflow export AF-20260613-001 --target agents --target claude --force
```

Run an agent command or any local command:

```bash
agentflow run AF-20260613-001 \
  --agent manual \
  --command "cat {prompt}" \
  --check "pytest -q"
```

`{prompt}` is replaced with the generated context-pack path.

After a run, AgentFlowDesk creates:

```text
.agentflow/runs/<run-id>/
  prompt.md
  stdout.txt
  stderr.txt
  diff.patch
  review-report.md
```

## Core concepts

### Task

A task is a small unit of agent work:

```yaml
title: Add SARIF ruleId support
goal: Modify the SARIF reporter so each finding has a stable ruleId.
files:
  - src/reporters/sarif.py
acceptance:
  - Unit tests pass
  - No unrelated files changed
```

### Context Pack

A context pack is a generated prompt bundle containing:

- task brief
- agent instructions
- project commands
- file tree and git status
- relevant file excerpts

### Export Target

AgentFlowDesk can export the same task context to multiple agent instruction formats:

| Target | Output file |
|---|---|
| `agents` | `AGENTS.md` |
| `claude` | `CLAUDE.md` |
| `cursor` | `.cursor/rules/agentflow.mdc` |
| `codex` | `.codex/instructions.md` |
| `gemini` | `GEMINI.md` |

### Run

A run captures one attempt to complete a task. It stores:

- generated prompt
- stdout / stderr
- git diff
- check command results
- review report

## Example workflow

```bash
agentflow init

agentflow task create \
  --title "Refactor report renderer" \
  --goal "Split Markdown and HTML report rendering into separate modules." \
  --file agentflow/report.py \
  --acceptance "pytest passes" \
  --acceptance "public CLI behavior remains unchanged"

agentflow export AF-20260613-001 --target claude --force

# Use your preferred agent manually, or wrap a CLI command:
agentflow run AF-20260613-001 --command "claude < {prompt}" --check "pytest -q"

# Review generated report:
cat .agentflow/runs/*/review-report.md
```

## Roadmap

- [x] CLI project initialization
- [x] Task creation, listing, display, and status updates
- [x] Context Pack generation
- [x] Export to common agent instruction files
- [x] Run record with prompt, logs, diff, checks, and review report
- [ ] Git worktree isolation for parallel agent runs
- [ ] YAML sprint batch runner
- [ ] Web UI task board
- [ ] Reusable skill/prompt library
- [ ] Cost and token estimation
- [ ] Agent adapter presets for Claude Code, Codex CLI, Gemini CLI, OpenCode, and Cursor workflows

## Design goal

AgentFlowDesk is intentionally boring infrastructure. It is not another chatbot.

The goal is to make AI-agent development work:

```text
Task → Context Pack → Agent Run → Diff + Checks → Human Review → Reusable Workflow
```

## Safety and privacy

AgentFlowDesk is local-first. It stores files under `.agentflow/` inside your project. It does not send code to a remote service by itself. If you use it to call an external agent CLI, that CLI's own behavior and privacy policy apply.

## License

MIT
