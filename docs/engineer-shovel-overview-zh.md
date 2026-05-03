# Engineer Shovel 工具说明

本文档说明 Engineer Shovel 的整体用途、各场景工作原理，以及背后使用的技能和工具链。

## 工具定位

Engineer Shovel，中文名“工兵铲”，是一个面向 OpenCode / Claude Code 的 token-aware AI 软件工程工作流路由器。

它不是单一开发框架，而是一个轻量入口层，用 12 个 `/tool-*` 指令把不同开发场景路由到合适的工作流、技能、命令和验证路径。

核心目标：

1. 降低 AI 开发中的上下文和 token 浪费。
2. 根据任务风险选择最便宜但足够可靠的执行模式。
3. 标准化常见软件工程场景：快速修复、Bug、功能、分支、规划、重构、审查、研究、复杂项目等。
4. 集成上游能力：ECC、GSD、superpowers、Caveman、RTK、code-review-graph。
5. 让 AI 在开始工作前先判断场景，而不是所有任务都走重型 agent 或深度规划。

一句话概括：

```text
Engineer Shovel = AI 软件工程工作流路由器 + token 成本控制层 + 常见开发场景命令集
```

## 整体架构

Engineer Shovel 由几层组成：

| 层级 | 作用 |
|---|---|
| `SKILL.md` | 轻量路由层，告诉 AI 应该选哪个 `/tool-*` 命令 |
| `commands/tool-*.md` | 12 个具体场景命令，定义适用场景、风险、成本模式、流程和升级路径 |
| `docs/workflows.md` | 长文档版工作流说明 |
| `docs/token-cost.md` | token 成本模型，定义什么时候用 fast / standard / deep |
| `docs/install.md` | 安装方式和组件说明 |
| 外部组件 | ECC、GSD、superpowers、Caveman、RTK、code-review-graph 等 |

设计原则是：运行时只加载轻量路由，详细说明放在 `docs/`，避免每次会话都把完整手册塞进上下文。

## 成本模式

Engineer Shovel 的所有命令都围绕 3 个成本模式工作：

| 模式 | 适用场景 | 典型能力 |
|---|---|---|
| `--fast` | 低风险、目标明确、小改动 | 直接编辑、轻量验证、Caveman lite |
| `--standard` | 普通开发任务 | 定向搜索、计划、实现、测试、构建、常规审查 |
| `--deep` | 高风险、跨模块、架构、研究、安全、复杂 Bug | GSD、Blueprint、多 agent、深度研究、深度审查 |

默认策略：

```text
先用最便宜的模式解决问题。
只有证据表明不够时，才升级到更重的流程。
```

这避免了两个常见问题：

1. 小任务过度规划。
2. 大任务没有足够验证。

## Token 控制机制

Engineer Shovel 的 token 控制主要依赖两个工具：

| 工具 | 工作层级 | 作用 |
|---|---|---|
| Caveman | 模型沟通层 | 压缩 AI 回复、review、commit、总结等自然语言输出 |
| RTK | 工具输出层 | 压缩 Bash、git、测试、构建、日志等命令输出 |

区别：

```text
Caveman 压缩 AI 说话方式。
RTK 压缩工具输出进入上下文前的噪声。
```

推荐用法：

| 场景 | 推荐压缩 |
|---|---|
| `/tool-quick --fast` | `/caveman lite` |
| `/tool-fix --standard` | `/caveman full` |
| `/tool-feat --standard` | `/caveman full` |
| `/tool-refactor --standard` | `/caveman full` |
| `/tool-blueprint` | `/caveman full` |
| `/tool-research --deep` | 上下文压力大时用 `/caveman ultra` |
| git/test/build/log 输出 | RTK |

## 12 个场景命令

### `/tool-quick`：快速任务

适用场景：拼写错误、README 小改动、配置微调、1-2 个文件的确定性小修改。

工作原理：

1. 从上下文确认目标文件或符号。
2. 做最小安全改动。
3. 运行最近、最有意义的验证，例如格式化、lint、测试或构建。
4. 汇报改了什么、验证通过了什么。

成本模式：

| 模式 | 行为 |
|---|---|
| `--fast` | typo、配置、小修，直接编辑或 `/gsd-fast` |
| `--standard` | 1-2 文件小变更，定向编辑加测试 |

会用到的能力：

| 能力 | 用途 |
|---|---|
| Grep / Glob / Read | 快速定位文件和符号 |
| Edit / Bash | 编辑与验证 |
| Caveman lite | 保持输出简短 |
| RTK | 压缩测试、构建、git 输出 |

### `/tool-fix`：Bug 修复

适用场景：行为异常、测试失败、回归、日志报错、需要证明根因的 Bug。

工作原理：

1. 复现问题或定位失败断言 / 日志。
2. 找最小根因，而不是只修表面症状。
3. 做外科手术式修复。
4. 先跑失败测试，再跑相关测试或构建。
5. 如果项目已有测试模式，补回归测试。

成本模式：

| 模式 | 行为 |
|---|---|
| `--fast` | 已知文件 / 函数，明显原因，直接修复加目标测试 |
| `--standard` | 可复现 Bug，局部范围，复现、检查、修复、回归测试 |
| `--deep` | flaky、跨模块、安全问题、根因未知，升级到 `/gsd-debug` |

会用到的技能 / 工具：

| 技能或工具 | 用途 |
|---|---|
| systematic debugging / GSD debug | 系统性定位复杂 Bug |
| security-review | 安全相关 Bug |
| security-scan | 安全扫描 |
| Bash | 运行失败测试和回归测试 |
| RTK | 压缩日志、trace、测试输出 |
| Caveman full | 压缩调试过程中的上下文 |

升级规则：

```text
单行 typo → 用 /tool-quick。
跨文件状态或架构问题 → 用 --deep。
安全漏洞 → 加 security-review 和 security-scan。
```

### `/tool-feat`：新功能开发

适用场景：添加新功能，并且已经能切出最小可验证功能片。

工作原理：

1. 编辑前确认不在 `main` / `master`，必要时先创建功能分支。
2. 搜索现有代码模式，避免发明第二套架构。
3. 确定最小可用增量和验证目标。
4. 按项目约定实现。
5. 运行诊断、相关测试、类型检查或构建。
6. 根据风险使用 `/tool-review --fast` 或标准审查。

成本模式：

| 模式 | 行为 |
|---|---|
| `--fast` | 已知区域的小功能，搜索、实现、测试 |
| `--standard` | 普通功能，3-8 个文件，探索模式、计划、实现、验证 |
| `--deep` | 多组件、外部依赖、需求模糊，升级到 `/tool-plan` 或 `/tool-blueprint` |

会用到的技能 / 工具：

| 技能或工具 | 用途 |
|---|---|
| brainstorming | 新功能或行为变化前澄清意图 |
| project-native skills | 按语言或框架选择专用能力 |
| `/tool-plan` | 需求或验证标准不清时先规划 |
| `/tool-blueprint` | 多组件或多 PR 功能 |
| `/tool-review` | 实现后审查 |
| Caveman full | 压缩功能开发中的计划和验证输出 |
| RTK | 压缩 git/test/build 输出 |

### `/tool-branch`：分支工作流

适用场景：开始开发、修 Bug、重构，或需要隔离改动并在合并前审查 diff。

子命令：

| 子命令 | 用途 |
|---|---|
| `create` | 从当前分支创建功能分支 |
| `status` | 查看分支信息和 diff 统计 |
| `review` | 查看相对源分支的完整 diff |
| `merge` | squash merge 到源分支并删除功能分支 |
| `abort` | 放弃分支并回到源分支 |

分支类型自动识别：

| 描述关键词 | 类型 |
|---|---|
| fix, bug, error, broken, crash, issue, problem | `fix` |
| add, new, feature, implement, support, create | `feat` |
| refactor, clean, optimize, improve, restructure | `refactor` |
| doc, readme, comment, typo, docs | `docs` |
| 默认 | `feat` |

命名格式：

```text
{type}/{slugified-description}
```

工作原理：

```bash
bash scripts/branch-workflow.sh <subcommand> [args...]
```

会用到的能力：

| 能力 | 用途 |
|---|---|
| Bash | 调用分支脚本 |
| git | 创建、审查、合并、回退分支 |
| RTK | 压缩 diff / status 输出 |
| code-review-graph | 深度审查前可更新图谱 |

### `/tool-plan`：规划

适用场景：执行顺序、影响文件、依赖、风险或验证标准不明显。

工作原理：

1. 重述目标和非目标。
2. 识别可能受影响的文件 / 模块。
3. 定义验证命令和完成标准。
4. 文件型计划需要审查后再执行。
5. 只有计划足够可验证时才开始实现。

成本模式：

| 模式 | 行为 |
|---|---|
| `--fast` | 小任务，短内联计划 |
| `--standard` | 中等任务，使用 `/plan` 或 `/prp-plan` 并定义验证标准 |
| `--deep` | 多 session、多依赖，升级到 `/blueprint` 或 GSD planning |

会用到的技能 / 工具：

| 技能或工具 | 用途 |
|---|---|
| writing-plans | 多步骤任务前制定计划 |
| `/tool-research --quick` | 技术方案未知时先研究 |
| `/tool-blueprint` | 多 PR 或 milestone 级任务 |
| GSD planning | 阶段化复杂项目 |
| Caveman lite/full | 根据计划长度压缩输出 |

### `/tool-refactor`：重构

适用场景：行为必须保持不变的清理、结构调整、命名整理、模块拆分等。

工作原理：

1. 编辑前先跑 baseline 验证。
2. 一次只做一个逻辑重构。
3. 修改后重跑相同验证。
4. 比较行为、公开 API、性能敏感路径。
5. 风险高时升级审查。

成本模式：

| 模式 | 行为 |
|---|---|
| `--fast` | 1-2 文件清理，目标测试加 `/tool-review --fast` |
| `--standard` | baseline 测试、重构、测试 / 构建、本地审查 |
| `--deep` | 大范围、高风险、安全敏感、性能关键，使用 `/refactor` 和 `/review-work` |

会用到的技能 / 工具：

| 技能或工具 | 用途 |
|---|---|
| refactoring / code-review-graph | 安全重构 |
| `/tool-review` | 重构后审查 |
| `/tool-fix` | baseline 失败时先修 Bug |
| RTK | 压缩 diff、测试、构建日志 |
| Caveman full/ultra | 压缩大范围重构说明 |

### `/tool-review`：代码审查

适用场景：本地 diff、PR、实现后审查、安全或高风险变更审查。

工作原理：

1. 根据输入判断是本地审查、PR 审查还是实现后审查。
2. 检查正确性、回归、安全、可维护性。
3. 对 critical / high findings 做外科手术式修复。
4. 重新运行相同或更强审查模式直到干净。

成本模式：

| 模式 | 行为 |
|---|---|
| `--fast` | 小 diff 快速 sanity check，使用 Caveman review 风格 |
| `--standard` | 本地 diff 或普通 PR，使用 `/code-review` 或 `/review-pr` |
| `--deep` | 重大实现、安全、广泛重构，使用 `/review-work` |

会用到的技能 / 工具：

| 技能或工具 | 用途 |
|---|---|
| caveman-review | 一行式高信号审查意见 |
| code-review / review-pr | 常规代码审查 |
| review-work | 深度实现后审查 |
| security-review | 安全敏感代码 |
| security-scan | 安全扫描 |
| code-review-graph | 提供图谱上下文和影响面分析 |
| RTK | 压缩 diff / log 输出 |

### `/tool-brainstorm`：头脑风暴

适用场景：想法还不能直接实现，需要澄清目标、假设、约束和选项。

工作原理：

1. 表述想法、目标和不确定性。
2. 暴露隐藏假设和约束。
3. 生成可选方案和 tradeoff。
4. 路由到 `/tool-quick`、`/tool-feat`、`/tool-plan`、`/tool-research` 或 backlog。

成本模式：

| 模式 | 行为 |
|---|---|
| `--fast` | 快速捕获和粗略路由，使用 `/gsd-note` |
| `--standard` | 澄清产品或技术方向，使用 `/gsd-explore` 或 brainstorming |
| `--deep` | 多条可行路径或 go/no-go 决策，使用 `/council` |

会用到的技能 / 工具：

| 技能或工具 | 用途 |
|---|---|
| brainstorming | 创造性工作和行为变化前澄清需求 |
| gsd-explore | 苏格拉底式探索想法 |
| gsd-note | 捕获想法 |
| council | 多路径决策 |
| Caveman lite/full | 保持探索输出可读但不浪费上下文 |

重要约束：除非下一步清晰且可验证，否则不要从 brainstorming 直接开始实现。

### `/tool-blueprint`：复杂多步骤项目

适用场景：单个小计划或单个 PR 无法安全承载的多步骤、多 session、多依赖项目。

工作原理：

1. 创建 blueprint，拆成独立可验证步骤。
2. 标记依赖关系和可并行工作。
3. 每个步骤使用匹配的 `/tool-*` 工作流执行。
4. 依赖步骤连接后运行集成验证。
5. 验证通过后再进入深度审查或发布流程。

成本模式：

| 模式 | 行为 |
|---|---|
| `--standard` | 多步骤但目标清晰，使用 `/blueprint` 和依赖图 |
| `--deep` | milestone 级或长期工作，使用 GSD 项目流程：discuss / plan / execute phases |

会用到的技能 / 工具：

| 技能或工具 | 用途 |
|---|---|
| blueprint | 生成多 session、多 agent 可执行计划 |
| GSD | 阶段化项目管理和验证 |
| dispatching-parallel-agents | 独立任务并行 |
| executing-plans | 执行已有计划 |
| verification-loop | 验证每个阶段 |
| Caveman full/ultra | 压缩长计划和多 agent 总结 |
| RTK | 压缩扫描、测试、日志 |

防误用规则：如果任务少于 3 个文件且需求清楚，用 `/tool-quick` 或 `/tool-feat`。

### `/tool-research`：研究

适用场景：规划或实现前需要本地、官方、当前或多来源证据。

工作原理：

1. 定义研究要支持的具体决策。
2. 搜索能回答问题的最小来源集合。
3. 当前或外部事实需要引用或命名来源。
4. 标明冲突和置信度。
5. 把结论路由到 `/tool-plan`、`/tool-feat`、`/tool-quick` 或文档。

成本模式：

| 模式 | 行为 |
|---|---|
| `--quick` | 本地文档、已知库、简单比较 |
| `--web` | 需要当前事实或官方文档 |
| `--deep` | 战略决策、证据冲突、不熟悉生态，多来源研究、示例和 tradeoff 报告 |

会用到的技能 / 工具：

| 技能或工具 | 用途 |
|---|---|
| research-ops | 研究流程总控 |
| exa-search | 快速当前 Web 发现 |
| deep-research | 多来源综合研究 |
| market-research | 需要推荐或排序时 |
| knowledge-ops | 需要把结果沉淀到知识库时 |
| WebFetch | 拉取外部页面 |
| Read / Grep / Glob | 本地文档研究 |
| Task | 深度研究可调 subagent |
| Caveman full/ultra | 压缩研究摘要 |

不适合：本地代码或官方文档能回答的问题，不要直接开 deep 多来源研究。

### `/tool-graph`：代码图谱

适用场景：手动管理 code-review-graph 索引，用于审查、影响面分析、token-efficient 代码导航。

子命令：

| 子命令 | 用途 |
|---|---|
| `status` | 查看安装和图谱健康状态 |
| `build` | 首次完整构建图谱 |
| `update` | 代码变化后增量刷新 |
| `rebuild` | 图谱陈旧或损坏时完整刷新 |
| `watch` | 连续更新模式，需要用户批准 |

工作原理：

1. 检查 `code-review-graph` 是否安装。
2. `status` 模式运行 `code-review-graph status` 并总结健康状态。
3. `build` 模式运行完整构建。
4. `update` 模式运行增量更新。
5. `rebuild` 优先使用上游 rebuild 路径，删除本地图谱前必须询问用户。
6. `watch` 不应未经批准留下后台 daemon。

会用到的能力：

| 能力 | 用途 |
|---|---|
| code-review-graph | 本地代码知识图谱 |
| MCP / rules | 提供审查上下文 |
| Bash | 运行 graph 命令 |
| `/tool-review` | 深度审查前可刷新图谱 |
| `/tool-branch review` | 合并前影响面分析 |

### `/tool-update`：同步和更新

适用场景：更新 Engineer Shovel 安装、检查缺失命令、刷新组件健康状态。

模式：

| 模式 | 行为 |
|---|---|
| `--check` | 只读检查安装文件、基础依赖和 full-mode 组件 |
| `--full` | 更新文件，并安装 / 配置缺失的低风险组件 |

目标范围：

| 参数 | 作用 |
|---|---|
| `--target opencode` | 只更新 OpenCode 安装 |
| `--target claude` | 只更新 Claude Code 安装 |
| `--target both` | 同时更新两个目标，默认 |

工作原理：

1. 根据 target 检测安装位置。
2. 比较已安装文件和最新仓库版本。
3. 报告缺失、过期或额外文件。
4. 检查基础工具和 full-mode 集成组件健康状态。
5. 如果是 `--full`，覆盖安装文件并修复缺失组件。
6. 最后验证安装完整性。

检查的组件：

| 组件 | 作用 |
|---|---|
| `git` | 基础版本控制 |
| `python3` / `pipx` | Python 工具安装 |
| `node` / `npx` | JS 工具和 installer |
| `opencode` / `claude` | 目标 AI agent runtime |
| code-review-graph | 代码图谱 |
| GSD | 阶段化规划执行 |
| superpowers | 技能工作流 |
| Caveman | 输出压缩 |
| RTK | 工具输出压缩 |
| ECC | agent harness 生态 |

安全边界：

```text
不启动后台 watch / daemon。
不主动启用 telemetry。
不删除用户配置。
修改 JSON 配置前备份。
ECC MCP 不默认自动启用，因为可能需要凭据或与用户已有 MCP 重复。
```

## 上游技能和组件

Engineer Shovel 在 full 模式下集成这些上游工具：

| 工具 | 作用 |
|---|---|
| ECC | AI agent harness 性能系统，包含 skills、rules、hooks、MCP、安全和 research-first 工作流 |
| GSD | Spec-driven 规划、阶段执行、验证和上下文工程 |
| superpowers | 强制技能工作流，例如 brainstorming、TDD、planning、review、branch finishing |
| code-review-graph | 本地代码知识图谱、MCP review context、影响面分析 |
| Caveman | 模型沟通压缩、review/commit 精简、MCP shrink |
| RTK | Shell/tool 输出压缩代理和命令 rewrite hooks |

安装模式：

| 模式 | 安装内容 |
|---|---|
| `--minimal` | 只安装 Engineer Shovel skill 和 12 个命令 |
| `--recommended` | 安装 Engineer Shovel + Caveman |
| `--full` | 安装完整工具链：ECC、GSD、superpowers、Caveman、RTK、code-review-graph、Engineer Shovel |

目标平台：

| target | 安装位置 |
|---|---|
| `opencode` | skill 到 `~/.agents/skills/engineer-shovel/`，commands 到 `~/.config/opencode/commands/` |
| `claude` | skill 到 `~/.claude/skills/engineer-shovel/`，commands 到 `~/.claude/commands/` |
| `all` | 同时安装到 OpenCode 和 Claude Code |
| `auto` | 优先检测 OpenCode，再检测 Claude Code |

## 典型场景路由

| 用户意图 | 推荐命令 |
|---|---|
| 修 README typo | `/tool-quick --fast` |
| 修一个明确 Bug | `/tool-fix --standard` |
| 修一个 flaky / 跨模块 Bug | `/tool-fix --deep` |
| 加一个小功能 | `/tool-feat --fast` |
| 加普通功能 | `/tool-feat --standard` |
| 做多组件功能 | `/tool-blueprint` |
| 开始新开发分支 | `/tool-branch create` |
| 合并前看 diff | `/tool-branch review` |
| 需求不清 | `/tool-plan` |
| 技术方案不确定 | `/tool-research --quick` |
| 需要当前官方资料 | `/tool-research --web` |
| 需要战略比较 | `/tool-research --deep` |
| 行为不变的整理 | `/tool-refactor` |
| 审查本地 diff | `/tool-review` |
| 审查高风险实现 | `/tool-review --deep` |
| 想法还不清楚 | `/tool-brainstorm` |
| 刷新代码图谱 | `/tool-graph update` |
| 检查安装健康 | `/tool-update --check` |

## 核心工作哲学

Engineer Shovel 的工程哲学：

1. Search before build：技术路径不清楚时先搜索，不要直接写。
2. Surgical changes：优先做最小正确修改。
3. Verify every step：每一步都用测试、构建、lint、审查或 diff 验证。
4. Start cheap, escalate only when needed：先轻量，证据不足再升级。
5. Context is a budget：上下文不是无限资源，要用 Caveman 和 RTK 控制成本。
6. Use the right workflow for the job：Bug、功能、重构、审查、研究不能混用同一套流程。
7. High-cost agents are for high-risk decisions：多 agent、GSD、deep research 不该用于日常小改动。

## 完整示例

如果用户说：

```text
帮我添加登录失败重试限制
```

Engineer Shovel 的理想路由可能是：

1. 这是新功能，先判断需求是否清晰。
2. 如果需求不清，走 `/tool-plan` 或 `/tool-brainstorm`。
3. 如果功能范围清楚，走 `/tool-feat --standard`。
4. 开始前用 `/tool-branch create feat add-login-retry-limit`。
5. 搜索现有认证、rate limit、错误处理模式。
6. 做最小功能片。
7. 添加或运行相关测试。
8. 如果涉及安全，补 `security-review`。
9. 最后 `/tool-review`。
10. 验证通过后按分支流程合并。

## 结论

Engineer Shovel 的价值不是“多一个命令集合”，而是把 AI 软件工程中最容易失控的部分标准化：

```text
什么时候该快？
什么时候该查？
什么时候该计划？
什么时候该开分支？
什么时候该重构？
什么时候该深度审查？
什么时候该节省 token？
什么时候该升级到多 agent / GSD / blueprint？
```

核心收益：

1. 小任务不被重流程拖慢。
2. 大任务不被轻率实现搞坏。
3. AI 上下文消耗可控。
4. 每类工程任务都有明确验证路径。
5. OpenCode 和 Claude Code 可以共享一套一致的开发操作模型。
