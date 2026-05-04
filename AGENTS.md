# Engineer Shovel 工作流指南

Engineer Shovel 是 OpenCode 和 Claude Code 的轻量级开发工作流路由器。当前项目以 `SKILL.md` 和 `/tool-*` 命令为公共入口；长文档放在 `docs/`，避免每次会话加载完整手册。

## 工具链边界

原生安装内容：轻量级 `engineer-shovel` 技能和 8 个活跃 `/tool-*` 命令（2 个已废弃）。

## 快速入口

```text
skill(name="engineer-shovel")
```

也可以直接调用命令：

```text
/tool-quick --fast "fix typo in README"
/tool-feat --standard "add smallest verifiable feature slice"
/tool-review --fast
/tool-research --deep "compare options for X"
/tool-graph update
```

## 命令表

| Command | Use for |
|---|---|
| `/tool-quick` | 明确、低风险、1-2 文件小改 |
| `/tool-fix` | Bug、失败测试、回归 |
| `/tool-feat` | 新功能（需求模糊时自动脑暴） |
| `/tool-branch` | 分支创建、状态、审查、合并、放弃（feat/fix 自动调用） |
| `/tool-plan` | 需求与实现规划（--deep 自动升级为 blueprint/gsd） |
| `/tool-refactor` | 行为保持不变的重构 |
| `/tool-review` | 本地 diff、PR、实现后审查 |
| `/tool-research` | 代码库感知的技术研究 |
| `/tool-graph` | code-review-graph 诊断（git hook 自动刷新） |
| `/tool-update` | 同步和更新安装 |
| `/tool-brainstorm` | **[已废弃]** — 已内化为 feat/plan 的 Phase 0 |
| `/tool-blueprint` | **[已废弃]** — 已合并到 plan --deep |

## 成本模式

| Mode | Use when | Typical path |
|---|---|---|
| `--fast` | 低风险、目标明确、小 diff | `/caveman lite`、直接编辑、定向验证、快速审查 |
| `--standard` | 常规开发 | `/caveman full`、搜索模式、实现、测试/构建 |
| `--deep` | 模糊、高风险、跨系统 | `/caveman full` 或 `ultra`、GSD、深度研究、深度审查 |

默认选择能验证结果的最低成本路径。只有证据显示轻量路径不足时才升级。

## 核心原则

1. 先搜索现有模式，再新增结构。
2. 优先做最小可验证切片。
3. 默认小改、保持项目风格，不引入无必要兼容层。
4. 每步运行最小有意义验证；高风险时扩展到测试、构建、审查。
5. 只在用户明确要求时提交 commit。
6. 独立任务可并行；共享状态或顺序依赖任务串行。

## 语言/框架命令

项目原生命令优先。完整表见 `docs/language-reference.md`。

| Language/Framework | Test | Build | Review |
|---|---|---|---|
| Go | `/go-test` or `go test ./...` | `/go-build` or `go build ./...` | `/go-review` |
| Rust | `/rust-test` or `cargo test` | `/rust-build` or `cargo build` | `/rust-review` |
| Python | `pytest` | project-specific | `/python-review` |
| TypeScript/JS | `bun test` / `npm test` | `bun run build` / `npm run build` | `/code-review` |

## Token 和输出压缩

详细策略见 `docs/token-cost.md`。

- Caveman 是默认沟通压缩层：`--fast` 用 `/caveman lite`，`--standard` 用 `/caveman full`，长上下文或多 agent 时可用 `/caveman ultra`。
- RTK 是工具输出压缩层：用于 git、测试、构建、日志等噪声输出；不要把 RTK 描述成 prompt 压缩器。
- Caveman 和 RTK 可叠加：前者压缩模型沟通，后者压缩 Bash/tool 输出。

## 参考文档

- `README.md`：项目概览、安装、能力边界。
- `SKILL.md`：轻量运行时路由器。
- `docs/architecture.md`：工具链架构与路由规则。
- `docs/token-cost.md`：Caveman/RTK 成本模型。
- `docs/language-reference.md`：语言和框架命令参考。

## 其他约定

- 尽可能用中文回答用户。
- 不要把已移除或非当前文档中的组件写回这里。
- 本文件应和 `CLAUDE.md` 保持一致。

最后更新：2026-05-03

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.
