# AgentFlowDesk

[English](README.md) | 简体中文

AgentFlowDesk 是一个 **local-first 的 AI Coding Agent 任务工作台与上下文管理器**。

它不是新的聊天机器人，也不是新的大模型封装层，而是给 Claude Code、Codex CLI、Cursor、Gemini CLI、OpenCode 等 AI Coding Agent 提供一层更工程化的工作流管理能力。

它帮助开发者把一次性的 AI 对话，变成可拆分、可追踪、可复盘、可复用的工程流程：

- 在把需求交给 Agent 前，先拆成结构化任务
- 为每个任务生成紧凑的 **Context Pack**
- 导出到 `AGENTS.md`、`CLAUDE.md`、Cursor Rules、Codex instructions、`GEMINI.md`
- 调用本地 Agent 命令，并记录 prompt、日志、diff、检查结果和 review report
- 避免 AI Agent 工作过程散落在多个聊天窗口里，难以追踪和复盘

> 当前状态：v0.1.0 MVP，CLI 优先。Web 任务板会在核心流程稳定后再做。
>
> CI 说明：测试 workflow 会在 Python 3.10、3.11、3.12 上验证安装流程，以及 Context Pack / export / run 的核心路径。

## 为什么做这个项目

AI Coding Agent 已经很强，但实际使用时仍然有很多操作层痛点：

1. **上下文需要反复复制和重写**：每次都要重新解释项目结构、文件作用、编码风格、验收标准。
2. **结果难以复盘**：Agent 改完代码后，prompt、日志、diff、测试命令、人工验收状态往往分散在不同地方。
3. **并行任务很麻烦**：想让多个 Agent 或多个分支同时跑任务，需要手动准备目录、分支、上下文和检查命令。
4. **成功经验难以沉淀**：一次效果很好的 prompt 或任务拆解，很难变成下次可复用的 workflow。
5. **不同 Agent 工具割裂**：Claude Code、Codex、Cursor、Gemini 等工具的指令文件和上下文组织方式不同，用户缺少统一管理层。

AgentFlowDesk 的目标是把：

```text
一次性聊天窗口
```

变成：

```text
任务 → Context Pack → Agent Run → Diff + Checks → 人工 Review → 可复用 Workflow
```

## 快速开始

在项目根目录安装并初始化：

```bash
python -m pip install -e .
agentflow init --name MyProject --description "Demo project using AI coding agents"
```

创建一个任务：

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

生成 Context Pack：

```bash
agentflow context build AF-20260613-001
```

导出给不同 Agent 使用：

```bash
agentflow export AF-20260613-001 \
  --target agents \
  --target claude \
  --target cursor \
  --target codex \
  --target gemini \
  --force
```

运行一个 Agent 命令或普通本地命令：

```bash
agentflow run AF-20260613-001 \
  --agent manual \
  --command "cat {prompt}" \
  --check "pytest -q"
```

`{prompt}` 会被替换为当前任务生成的 Context Pack 路径。

运行后会生成：

```text
.agentflow/runs/<run-id>/
  prompt.md
  stdout.txt
  stderr.txt
  diff.patch
  review-report.md
```

## 核心概念

### Task

Task 是最小的 Agent 工作单元。它描述“这次要让 Agent 做什么”。

示例：

```yaml
title: Add SARIF ruleId support
goal: Modify the SARIF reporter so each finding has a stable ruleId.
files:
  - src/reporters/sarif.py
acceptance:
  - Unit tests pass
  - No unrelated files changed
agent:
  preferred: claude-code
```

一个好的 Task 应该尽量包含：

- 明确目标
- 相关文件或目录
- 验收标准
- 额外注意事项
- 推荐使用的 Agent

### Context Pack

Context Pack 是按任务生成的上下文包，核心目标是减少重复复制粘贴，并让每次 Agent Run 都可复现。

它包含：

- 任务说明
- Agent 操作规则
- 项目命令
- 文件树
- Git 状态
- 相关文件摘录
- 合并后的 `context-pack.md`

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

### Export Target

AgentFlowDesk 可以把同一个任务上下文导出为多个工具常用的指令文件：

| Target | 输出文件 |
|---|---|
| `agents` | `AGENTS.md` |
| `claude` | `CLAUDE.md` |
| `cursor` | `.cursor/rules/agentflow.mdc` |
| `codex` | `.codex/instructions.md` |
| `gemini` | `GEMINI.md` |

这样你可以用同一份任务上下文，在不同 AI Coding Agent 之间切换。

### Run

Run 表示某个任务的一次执行尝试。它会记录：

- 本次传给 Agent 的 prompt
- stdout / stderr
- Git diff
- 检查命令结果
- Review Report

这让每次 Agent 修改都可以被复盘，而不是只留下一段聊天记录。

## 示例工作流

```bash
agentflow init

agentflow task create \
  --title "Refactor report renderer" \
  --goal "Split Markdown and HTML report rendering into separate modules." \
  --file agentflow/report.py \
  --acceptance "pytest passes" \
  --acceptance "public CLI behavior remains unchanged"

agentflow export AF-20260613-001 --target claude --force

# 使用你偏好的 Agent，或者用命令包装器调用：
agentflow run AF-20260613-001 --command "claude < {prompt}" --check "pytest -q"

# 查看本次运行报告：
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

AgentFlowDesk 不试图替代 Claude Code、Codex、Cursor、Gemini 等工具。

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
