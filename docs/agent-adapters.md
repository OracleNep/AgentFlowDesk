# Agent Adapters

The MVP uses a simple command wrapper instead of hard-coding model APIs.

Example:

```bash
agentflow run AF-20260613-001 --command "claude < {prompt}" --check "pytest -q"
agentflow run AF-20260613-001 --command "codex exec --prompt-file {prompt}" --check "pytest -q"
agentflow run AF-20260613-001 --command "cat {prompt}" --agent manual
```

`{prompt}` is replaced with the generated context-pack path.

## Planned adapter presets

Future versions can define presets like:

```json
{
  "agents": {
    "claude-code": {
      "command": "claude < {prompt}"
    },
    "codex-cli": {
      "command": "codex exec --prompt-file {prompt}"
    },
    "gemini-cli": {
      "command": "gemini --prompt-file {prompt}"
    }
  }
}
```

## Worktree isolation

The next major feature is to run each task in its own `git worktree`, so multiple agents can work in parallel without overwriting each other's files.
