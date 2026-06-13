# AgentFlowDesk

English | [简体中文](README.zh-CN.md)

AgentFlowDesk is a **local-first workflow manager for AI coding agents**.

It is **not** a Claude Skill, MCP server, IDE extension, browser plugin, or another chatbot. It is a small Python CLI that sits **outside** your AI coding agent and helps you manage the work around it:

```text
Task → Context Pack → Agent instructions → Agent command → Logs + Diff + Checks → Review Report
```

In plain terms: AgentFlowDesk prepares clean task context for tools like Claude Code, Codex CLI, Cursor, Gemini CLI, and OpenCode, then records what was sent, what ran, what changed, and what still needs human review.

> MVP status: v0.1.0, CLI-first. No server is required. The web task board is planned after the core workflow is stable.
>
> CI note: the test workflow validates installation and the core Context Pack/export/run path on Python 3.10, 3.11, and 3.12.

## What exactly is it?

AgentFlowDesk is a **local Python command-line tool** for developers who already use AI coding agents.

It gives those agents a structured workflow layer:

- **Task manager**: define a small coding task with goal, files, notes, and acceptance criteria.
- **Context Pack builder**: generate a reproducible prompt bundle for that task.
- **Instruction exporter**: write `AGENTS.md`, `CLAUDE.md`, Cursor rules, Codex instructions, and `GEMINI.md` from the same task context.
- **Command wrapper**: optionally run an installed local agent CLI with the generated prompt.
- **Run recorder**: save prompt, stdout, stderr, git diff, check results, and review report under `.agentflow/`.

It does **not** provide a model by itself. It does **not** call Claude, Codex, OpenCode, or Gemini unless you explicitly configure a command for it.

## Compatibility

AgentFlowDesk is compatible in two ways:

1. **File-based context**: export a task into instruction files that coding agents already understand or that users can paste into them.
2. **Command-wrapper mode**: run any local CLI command and replace `{prompt}` with the generated Context Pack path.

| Tool | Current support | How to use it |
|---|---|---|
| Claude Code | Yes | Export `CLAUDE.md`, or run a local command such as `claude < {prompt}` if your installed Claude Code CLI accepts stdin. |
| Codex CLI | Yes | Export `AGENTS.md` and `.codex/instructions.md`, or wrap your installed Codex command with `{prompt}`. |
| OpenCode | Yes, generic CLI mode | Export `AGENTS.md` / use the generated `context-pack.md`, or wrap your installed `opencode` command if it accepts a prompt file or stdin. Dedicated preset is planned. |
| Cursor | Yes, file export | Export `.cursor/rules/agentflow.mdc`; then use Cursor normally in the project. |
| Gemini CLI | Yes | Export `GEMINI.md`, or wrap your local Gemini CLI command. |
| Any other coding agent CLI | Usually yes | Works if the tool can read a prompt file, read stdin, or use a project instruction file. |

Compatibility here means **workflow-level integration**, not an official plugin contract. Agent-specific command flags change over time, so AgentFlowDesk keeps the core generic: you decide the command, AgentFlowDesk provides `{prompt}` and records the run.

## Installation

### Requirements

- Python 3.10+
- Git, recommended for diff capture
- Optional: Claude Code, Codex CLI, OpenCode, Gemini CLI, or another local coding-agent CLI

### Install from source

```bash
git clone https://github.com/OracleNep/AgentFlowDesk.git
cd AgentFlowDesk
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e .[dev]
```

Verify installation:

```bash
agentflow --help
pytest -q
```

## Deploy / start in a real project

AgentFlowDesk has no daemon and no web service in the MVP. To "deploy" it, install the CLI and initialize it inside the codebase where you want to use agents.

```bash
cd /path/to/your/project
agentflow init --name MyProject --description "Project managed with AI coding agents"
```

This creates local metadata under:

```text
.agentflow/
  config.json
  tasks.json
  runs.json
  context/
  runs/
```

By default, AgentFlowDesk stores data locally and does not upload your code or prompt anywhere.

## Basic workflow

### 1. Create a task

```bash
agentflow task create \
  --title "Add SARIF ruleId support" \
  --goal "Modify the SARIF reporter so each finding has a stable ruleId." \
  --file src/reporters/sarif.py \
  --acceptance "Unit tests pass" \
  --acceptance "No unrelated files changed" \
  --agent claude-code
```

List and inspect tasks:

```bash
agentflow task list
agentflow task show AF-20260613-001
```

### 2. Build a Context Pack

```bash
agentflow context build AF-20260613-001
```

Generated files:

```text
.agentflow/context/<task-id>/
  task-brief.md
  agent-instructions.md
  commands.md
  environment.md
  relevant-files.md
  context-pack.md
```

### 3. Export instructions for your agent

```bash
agentflow export AF-20260613-001 \
  --target agents \
  --target claude \
  --target cursor \
  --target codex \
  --target gemini \
  --force
```

Export targets:

| Target | Output file |
|---|---|
| `agents` | `AGENTS.md` |
| `claude` | `CLAUDE.md` |
| `cursor` | `.cursor/rules/agentflow.mdc` |
| `codex` | `.codex/instructions.md` |
| `gemini` | `GEMINI.md` |

### 4. Run a command and record the result

Use a safe manual smoke test first:

```bash
agentflow run AF-20260613-001 \
  --agent manual \
  --command "cat {prompt}" \
  --check "pytest -q"
```

Example with Claude Code, if your CLI accepts stdin:

```bash
agentflow run AF-20260613-001 \
  --agent claude-code \
  --command "claude < {prompt}" \
  --check "pytest -q"
```

Example with a custom command:

```bash
agentflow run AF-20260613-001 \
  --agent opencode \
  --command "opencode < {prompt}" \
  --check "pytest -q"
```

If your agent CLI uses a different flag for prompt files, just replace the command. `{prompt}` is always substituted with the generated `context-pack.md` path.

After a run, AgentFlowDesk creates:

```text
.agentflow/runs/<run-id>/
  prompt.md
  stdout.txt
  stderr.txt
  diff.patch
  review-report.md
```

## Why this exists

AI coding agents are powerful, but day-to-day usage still has friction:

1. Context has to be copied and rewritten repeatedly.
2. Agent output is hard to review after the session ends.
3. Running multiple agents or tasks in parallel is messy.
4. Successful prompts and workflows are not easy to reuse.
5. Users need a lightweight way to connect task intent, context, diff, tests, and human review.

AgentFlowDesk turns disposable agent sessions into reviewable engineering artifacts.

## Example review flow

```bash
agentflow init

agentflow task create \
  --title "Refactor report renderer" \
  --goal "Split Markdown and HTML report rendering into separate modules." \
  --file agentflow/report.py \
  --acceptance "pytest passes" \
  --acceptance "public CLI behavior remains unchanged"

agentflow export AF-20260613-001 --target claude --force
agentflow run AF-20260613-001 --command "claude < {prompt}" --check "pytest -q"
cat .agentflow/runs/*/review-report.md
```

## Roadmap

- [x] CLI project initialization
- [x] Task creation, listing, display, and status updates
- [x] Context Pack generation
- [x] Export to common agent instruction files
- [x] Run record with prompt, logs, diff, checks, and review report
- [x] GitHub Actions CI
- [x] Basic test coverage for the core workflow
- [ ] Git worktree isolation for parallel agent runs
- [ ] YAML sprint batch runner
- [ ] Web UI task board
- [ ] Reusable skill/prompt library
- [ ] Cost and token estimation
- [ ] Agent adapter presets for Claude Code, Codex CLI, Gemini CLI, OpenCode, and Cursor workflows

## Safety and privacy

AgentFlowDesk is local-first. It stores files under `.agentflow/` inside your project. It does not send code to a remote service by itself.

If you use it to call an external agent CLI, that CLI's own behavior and privacy policy apply.

## License

MIT
