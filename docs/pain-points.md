# AI Coding Agent Pain Points

AgentFlowDesk focuses on practical user pain points observed in day-to-day AI coding agent usage.

## 1. Context is fragile

Users repeatedly explain architecture, file roles, coding style, and acceptance criteria. This knowledge is scattered across chat windows and not always reproducible.

## 2. Output is hard to review

Agent output often arrives as a large diff plus a narrative summary. The user still needs to connect the task, prompt, diff, logs, and tests manually.

## 3. Sessions are disposable

A good agent session may contain a high-quality task decomposition or prompt strategy, but it is rarely saved as a reusable workflow.

## 4. Parallel work is awkward

Users want to send multiple small tasks to different agents or branches, but manual branch/worktree setup and context copying are inconvenient.

## 5. Agent tools are fragmented

Claude Code, Codex CLI, Cursor, Gemini CLI, OpenCode, and other tools use different instruction files and workflows. Users need a small compatibility layer rather than another agent framework.

## Product response

AgentFlowDesk turns:

```text
one-off chat sessions
```

into:

```text
structured task → context pack → agent run → diff/checks → review report
```
