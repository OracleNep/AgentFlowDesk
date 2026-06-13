# AgentFlowDesk

[English](README.md) | 简体中文

AgentFlowDesk 是一个 **local-first 的 AI Coding Agent 工作流管理器**。

它 **不是** Claude Skill、不是 MCP Server、不是 IDE 扩展、不是浏览器插件，也不是新的聊天机器人。它是一个运行在本地的 Python CLI，位于你的 AI Coding Agent 外层，用来管理 Agent 工作前后的工程流程：

```text
任务 → Context Pack → Agent 指令文件 → Agent 命令 → 日志 + Diff + 检查结果 → Review Report
```

简单说：AgentFlowDesk 会为 Claude Code、Codex CLI、Cursor、Gemini CLI、OpenCode 等工具准备干净的任务上下文，然后记录这次给了 Agent 什么、执行了什么、改了什么、测试结果如何，以及最后是否需要人工 review。

> 当前状态：v0.1.0 MVP，CLI 优先。MVP 不需要启动服务器。Web 任务板会在核心流程稳定后再做。
>
> CI 说明：测试 workflow 会在 Python 3.10、3.11、3.12 上验证安装流程，以及 Context Pack / export / run 的核心路径。

## 它到底是什么？

AgentFlowDesk 是一个给已经在使用 AI Coding Agent 的开发者准备的 **本地 Python 命令行工具**。

它给这些 Agent 加了一层工程化工作流：

- **任务管理器**：把需求拆成带目标、相关文件、备注和验收标准的小任务。
- **Context Pack 生成器**：为每个任务生成可复现的 prompt 上下文包。
- **指令文件导出器**：从同一份任务上下文导出 `AGENTS.md`、`CLAUDE.md`、Cursor Rules、Codex instructions、`GEMINI.md`。
- **命令包装器**：可选地调用你本机已经安装好的 Agent CLI。
- **运行记录器**：把 prompt、stdout、stderr、git diff、检查结果和 review report 保存到 `.agentflow/`。

它本身 **不提供模型能力**。除非你明确配置 `--command`，否则它不会主动调用 Claude、Codex、OpenCode、Gemini 或其他远程服务。

## 兼容哪些工具？

AgentFlowDesk 的兼容方式有两种：

1. **文件型上下文**：把任务上下文导出为常见 Agent 指令文件，给对应工具读取，或者人工复制粘贴。
2. **命令包装器模式**：运行任意本地 CLI 命令，并把 `{prompt}` 替换为当前任务生成的 Context Pack 路径。

| 工具 | 当前支持情况 | 用法 |
|---|---|---|
| Claude Code | 支持 | 导出 `CLAUDE.md`，或者在你的 Claude Code CLI 支持 stdin 时使用 `claude < {prompt}`。 |
| Codex CLI | 支持 | 导出 `AGENTS.md` 和 `.codex/instructions.md`，或者用 `{prompt}` 包装你本地安装的 Codex 命令。 |
| OpenCode | 支持，通用 CLI 模式 | 导出 `AGENTS.md` / 使用生成的 `context-pack.md`，或者在你的 `opencode` 命令支持 prompt 文件或 stdin 时用命令包装器调用。专用 preset 后续补。 |
| Cursor | 支持，文件导出模式 | 导出 `.cursor/rules/agentflow.mdc`，然后在项目里正常使用 Cursor。 |
| Gemini CLI | 支持 | 导出 `GEMINI.md`，或者用命令包装器调用本地 Gemini CLI。 |
| 其他 Coding Agent CLI | 通常支持 | 只要这个工具能读 prompt 文件、读 stdin，或者支持项目级指令文件，就可以接入。 |

这里的“兼容”指的是 **工作流层兼容**，不是官方插件协议。不同 Agent CLI 的命令参数可能会变化，所以 AgentFlowDesk 的核心设计保持通用：你决定具体命令，AgentFlowDesk 负责提供 `{prompt}` 并记录运行过程。

## 安装

### 环境要求

- Python 3.10+
- 推荐安装 Git，用于捕获 diff
- 可选：Claude Code、Codex CLI、OpenCode、Gemini CLI 或其他本地 Agent CLI

### 从源码安装

```bash
git clone https://github.com/OracleNep/AgentFlowDesk.git
cd AgentFlowDesk
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e .[dev]
```

验证安装：

```bash
agentflow --help
pytest -q
```

## 怎么部署 / 怎么启动？

MVP 版本没有后台服务，也没有 Web Server，所以不需要 `docker compose up` 或 `npm run dev`。

所谓“部署”，就是把 CLI 安装好，然后在你要使用 AI Agent 的代码仓库里初始化：

```bash
cd /path/to/your/project
agentflow init --name MyProject --description "Project managed with AI coding agents"
```

初始化后会在当前项目下生成：

```text
.agentflow/
  config.json
  tasks.json
  runs.json
  context/
  runs/
```

AgentFlowDesk 默认只写本地 `.agentflow/` 目录，不会主动上传你的代码或 prompt。

## 基础工作流

### 1. 创建任务

```bash
agentflow task create \
  --title "Add SARIF ruleId support" \
  --goal "Modify the SARIF reporter so each finding has a stable ruleId." \
  --file src/reporters/sarif.py \
  --acceptance "Unit tests pass" \
  --acceptance "No unrelated files changed" \
  --agent claude-code
```

查看任务：

```bash
agentflow task list
agentflow task show AF-20260613-001
```

### 2. 生成 Context Pack

```bash
agentflow context build AF-20260613-001
```

生成目录：

```text
.agentflow/context/<task-id>/
  task-brief.md
  agent-instructions.md
  commands.md
  environment.md
  relevant-files.md
  context-pack.md
```

### 3. 导出给不同 Agent 使用

```bash
agentflow export AF-20260613-001 \
  --target agents \
  --target claude \
  --target cursor \
  --target codex \
  --target gemini \
  --force
```

导出目标：

| Target | 输出文件 |
|---|---|
| `agents` | `AGENTS.md` |
| `claude` | `CLAUDE.md` |
| `cursor` | `.cursor/rules/agentflow.mdc` |
| `codex` | `.codex/instructions.md` |
| `gemini` | `GEMINI.md` |

### 4. 执行命令并记录结果

先用安全的本地命令试跑：

```bash
agentflow run AF-20260613-001 \
  --agent manual \
  --command "cat {prompt}" \
  --check "pytest -q"
```

如果你的 Claude Code CLI 支持 stdin，可以这样接：

```bash
agentflow run AF-20260613-001 \
  --agent claude-code \
  --command "claude < {prompt}" \
  --check "pytest -q"
```

如果要接 OpenCode，可以先用通用命令包装器：

```bash
agentflow run AF-20260613-001 \
  --agent opencode \
  --command "opencode < {prompt}" \
  --check "pytest -q"
```

如果你的 Agent CLI 使用的是 `--prompt-file`、`--file`、`run`、`exec` 等其他参数，直接替换 `--command` 即可。`{prompt}` 永远会被 AgentFlowDesk 替换为生成的 `context-pack.md` 路径。

运行后会生成：

```text
.agentflow/runs/<run-id>/
  prompt.md
  stdout.txt
  stderr.txt
  diff.patch
  review-report.md
```

## 为什么做这个项目

AI Coding Agent 已经很强，但实际使用时仍然有很多操作层痛点：

1. **上下文需要反复复制和重写**：每次都要重新解释项目结构、文件作用、编码风格、验收标准。
2. **结果难以复盘**：Agent 改完代码后，prompt、日志、diff、测试命令、人工验收状态往往分散在不同地方。
3. **并行任务很麻烦**：想让多个 Agent 或多个分支同时跑任务，需要手动准备目录、分支、上下文和检查命令。
4. **成功经验难以沉淀**：一次效果很好的 prompt 或任务拆解，很难变成下次可复用的 workflow。
5. **不同 Agent 工具割裂**：Claude Code、Codex、Cursor、Gemini 等工具的指令文件和上下文组织方式不同，用户缺少统一管理层。

AgentFlowDesk 的目标是把一次性 Agent 会话变成可 review 的工程产物。

## 示例 Review 流程

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

## 当前功能

- [x] CLI 项目初始化
- [x] 任务创建、列表、查看、状态更新
- [x] Context Pack 生成
- [x] 导出到常见 Agent 指令文件
- [x] 运行记录：prompt、日志、diff、检查结果、review report
- [x] GitHub Actions CI
- [x] 基础测试覆盖核心流程

## Roadmap

- [ ] Git worktree 隔离运行，让多个 Agent 可以并行处理不同任务
- [ ] YAML sprint batch runner，一次性批量调度多个任务
- [ ] Web UI 任务板
- [ ] 可复用 Skill / Prompt Library
- [ ] Token / 成本估算
- [ ] Claude Code、Codex CLI、Gemini CLI、OpenCode、Cursor 的 Agent adapter presets
- [ ] 更细粒度的 diff scope 检查
- [ ] 自动生成任务复盘和可复用 workflow 模板

## 设计原则

### 1. Local-first

AgentFlowDesk 默认只在项目本地 `.agentflow/` 目录下保存数据，不主动上传代码或 prompt。

如果你通过它调用外部 Agent CLI，则实际数据传输行为取决于对应 Agent 工具本身。

### 2. 不替代 Agent，只管理 Agent 工作流

AgentFlowDesk 不试图替代 Claude Code、Codex、Cursor、Gemini、OpenCode 等工具。

它做的是这些工具之上的工程化管理层：

```text
任务管理 + 上下文组织 + 执行记录 + 结果验收 + 经验复用
```

### 3. 人类仍然负责最终 Review

AgentFlowDesk 不假装能自动判断代码一定正确。

它的目标是帮助用户更容易回答这些问题：

- Agent 到底看了什么上下文？
- 它执行了什么命令？
- 它改了哪些文件？
- 测试是否跑过？
- 这次修改是否符合验收标准？
- 这次成功经验能不能复用？

## 仓库结构

```text
AgentFlowDesk/
  agentflow/
    cli.py              # CLI 入口
    storage.py          # .agentflow 本地 JSON 存储
    models.py           # Task / RunRecord 模型
    context_builder.py  # Context Pack 生成
    exporters.py        # AGENTS / Claude / Cursor / Codex / Gemini 导出
    runner.py           # Agent 命令包装与运行记录
    review.py           # Review Report 渲染
    git_tools.py        # git status / diff 辅助函数
  docs/
    pain-points.md
    design.md
    context-pack.md
    agent-adapters.md
  examples/
    sprint.yml
  tests/
    test_agentflow.py
  .github/workflows/
    ci.yml
```

## 安全与隐私

AgentFlowDesk 本身是本地优先工具。它不会主动把你的代码、prompt 或日志发送到远程服务。

但如果你配置了外部 Agent 命令，例如：

```bash
agentflow run AF-20260613-001 --command "claude < {prompt}"
```

那么数据会如何处理，取决于该 Agent CLI 的实现和隐私策略。

## 许可证

MIT
