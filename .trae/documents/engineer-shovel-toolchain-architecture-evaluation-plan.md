# Engineer Shovel 工具链架构评估与收敛计划

## Summary

目标：基于当前 `engineer-shovel` 仓库现状，形成一套面向 OpenCode / Claude Code 的工具链收敛方案，重点解决以下问题：

- 当前 `/tool-*` 命令对 ECC、GSD、superpowers、code-review-graph、caveman、rtk、OpenSpec 的调用是否贴合真实编程场景。
- 命令职责是否重叠、是否偏重、是否存在默认路径过深的问题。
- 在保持“全量默认安装”的前提下，如何把“轻量优先、必要时升级”的工程体验做得更清晰。
- 如何让安装、更新、健康检查、版本升级更加可控、可观测、可维护。

本计划的输出不是立即改代码，而是定义一轮面向架构和产品形态的收敛改造，优先收敛命令边界、默认路径、安装层次、升级机制，再视需要落到文档和脚本实现。

## Current State Analysis

### 1. Runtime Router 与命令层

- `SKILL.md` 已是轻量路由器，明确了 10 个活跃命令、成本模式、Caveman/RTK 策略、Security Gate、Completion Pipeline。
- 命令主入口位于 `commands/`：
  - `tool-quick.md`
  - `tool-fix.md`
  - `tool-feat.md`
  - `tool-plan.md`
  - `tool-refactor.md`
  - `tool-review.md`
  - `tool-research.md`
  - `tool-graph.md`
  - `tool-branch.md`
  - `tool-update.md`
  - 兼容重定向：`tool-brainstorm.md`、`tool-blueprint.md`
- 当前命令文案已经体现“先轻后重”的意图，但仍然有较明显的“声明性重依赖”问题：很多命令在说明层面同时引用 CRG、claude-mem、superpowers、ECC、OpenSpec、GSD，导致用户感知上容易把标准路径理解为重型编排路径。

### 2. 命令职责边界现状

- `/tool-feat`、`/tool-plan`、`/tool-research` 都承担“澄清问题 + 找方向 + 方案选择”的一部分职责。
- `/tool-fix`、`/tool-refactor`、`/tool-review` 都内含图谱分析、验证、轻审查，存在流程描述重复。
- `/tool-graph` 已降级为诊断工具，但 README 和部分示例仍容易让用户理解成日常显式操作入口。
- `/tool-branch` 是工程流程控制命令，但当前与 `/tool-feat`、`/tool-fix` 的“自动建分支”存在潜在双入口心智。
- `/tool-update` 负责“同步和更新”，但真正执行更新判断的逻辑还散落在 `scripts/sync.py` 与 `scripts/health.py`。

### 3. 外部工具映射现状

- `code-review-graph`
  - 在仓库中被定位为默认代码智能层。
  - 当前适合承担“代码定位、影响面、审查上下文”。
  - 现状问题：在多个命令中被写成默认必经步骤，说明层偏重，容易抬高用户理解成本。
- `caveman`
  - 当前是全局沟通压缩层，角色清晰。
  - 现状问题：命令文档中多次重复映射规则，虽然已在 `SKILL.md` 集中，但命令层仍有大量重复描述。
- `rtk`
  - 当前是 noisy shell/tool output 压缩层，角色也清晰。
  - 现状问题：安装与健康检查中是系统级组件，但在用户心智里不像“可选增强”，更像“需要理解的额外系统”。
- `superpowers`
  - 适合方法论型技能：brainstorming、planning、systematic-debugging、review。
  - 现状问题：与 `/tool-plan`、`/tool-feat` 自身 Phase 0/plan 描述存在边界重叠。
- `ECC`
  - 适合能力库和专项技能，如研究、架构决策、安全、GitHub 工作流。
  - 现状问题：项目中把它既当“能力库”又当“工作流入口”叙述，容易与 superpowers / GSD 冲突。
- `GSD`
  - 适合深度、多阶段、跨会话、多工作流编排。
  - 现状问题：虽然文档已把标准路径从 GSD 中抽离，但命令文本仍频繁露出 deep gate，使“默认不重”这一定位不够强。
- `OpenSpec`
  - 适合 durable spec / task artifacts。
  - 现状问题：在标准规划与深度规划之间的定位还不够稳定，用户不容易判断何时真的值得启动规格层。

### 4. 安装、同步、升级链路

- `install.sh` 已承担大量职责：
  - Engineer Shovel 自身安装
  - Caveman / RTK / CRG / superpowers / OpenSpec / claude-mem / ECC / GSD 的安装与初始化
  - target/scope 选择
  - 部分配置注入
- `scripts/sync.py` 负责：
  - 对比仓库与已安装的 skill/commands 文件
  - 可选 `git fetch` / `git pull`
  - 调用 `scripts/health.py`
- `scripts/health.py` 负责：
  - 基础依赖检查
  - 各组件是否存在、是否配置完成
  - 部分 repair 动作

当前问题：

- 更新链路被拆成“安装器、同步器、健康检查器”三套逻辑，虽有分工，但用户入口不够统一。
- `install.sh` 已很重，既要做首次安装，又要理解每个外部组件差异化安装逻辑。
- 版本策略不统一：
  - ECC、RTK 在安装脚本里使用显式 SHA。
  - OpenSpec、GSD、claude-mem 等更多使用 `latest` / `npx` 实时安装。
  - 这会导致“全量默认安装”在升级时的可复现性与稳定性不一致。

### 5. 项目已经具备的优点

- `SKILL.md` 已成功缩成 router，而不是把全部手册塞进运行时。
- 已经明确区分 `minimal` / `recommended` / `full`。
- 兼容层处理较好：废弃命令保留 redirect，不强行破坏旧用户入口。
- CI 已覆盖 schema、文档引用、安装 dry-run、shellcheck、pytest，说明仓库已经具备继续架构收敛的工程基础。

## Assumptions & Decisions

### 已确认偏好

- 默认目标用户不是只做轻量任务，也不是只做重度编排，而是“双层兼顾”。
- 安装策略保持“全量默认”。
- 本轮更偏向“架构收敛方案”，不是单独做安装器重写。

### 决策原则

- 保持公开入口稳定：
  - `skill(name="engineer-shovel")`
  - `/tool-*` 名称
  - `--minimal | --recommended | --full`
- 保持“全量默认安装”，但默认执行路径必须明确“先轻后重”，不能让 full install 等于 full workflow。
- 明确三层概念边界：
  - Engineer Shovel：路由与策略层
  - 外部工具：能力层
  - install/update/health：平台运维层
- 优先减少命令语义重叠，而不是继续新增命令。

## Proposed Changes

### A. 收敛命令心智模型

目标：把现有 10 个活跃命令收敛为“4 个主工作流 + 3 个工程辅助 + 3 个平台辅助”的清晰心智，不改命令名，先改定位与文档。

#### 受影响文件

- `SKILL.md`
- `README.md`
- `README_zh.md`
- `docs/architecture.md`
- `commands/tool-feat.md`
- `commands/tool-fix.md`
- `commands/tool-plan.md`
- `commands/tool-review.md`
- `commands/tool-research.md`
- `commands/tool-quick.md`
- `commands/tool-refactor.md`
- `commands/tool-branch.md`
- `commands/tool-graph.md`
- `commands/tool-update.md`

#### 具体改动

- 将命令分为 3 组并在 `SKILL.md` / README 首屏统一呈现：
  - 主工作流：`quick`、`fix`、`feat`、`plan`
  - 工程辅助：`review`、`refactor`、`research`
  - 平台辅助：`branch`、`graph`、`update`
- 强化“默认入口”建议：
  - 小改直接 `quick`
  - 出错走 `fix`
  - 新功能走 `feat`
  - 不清楚怎么做才走 `plan`
- 把 `review`、`research` 从“常规每次都要显式调用”改成“辅助命令/补充命令”的叙述。
- 在 `tool-feat`、`tool-plan` 中减少重复的 brainstorm / council / OpenSpec / GSD 决策树文案，保留“何时升级”的硬规则，其余跳转到 `docs/architecture.md`。

#### 为什么

- 当前命令不是太多，而是“每个命令背后露出的外部工具太多”，导致心理重量高于实际重量。
- 先收敛入口认知，比继续扩展深度工作流更能提升编程工程使用体验。

### B. 重写外部工具定位表，避免能力层互相抢职责

目标：把外部工具定义成“专长型能力”，而不是多个可替代总工作流。

#### 受影响文件

- `SKILL.md`
- `docs/architecture.md`
- `README.md`
- `README_zh.md`

#### 具体改动

- 统一定义以下角色：
  - `code-review-graph`: 默认代码理解与影响面分析层
  - `caveman`: 默认对话压缩层
  - `rtk`: 默认 noisy output 压缩层
  - `superpowers`: 单任务方法论增强层
  - `ECC`: 专项能力库层
  - `OpenSpec`: durable 规格层
  - `GSD`: 跨阶段/跨会话/多工作流编排层
- 明确排它性路由规则：
  - “澄清需求”优先 `plan` 自带流程，只有出现明确 tradeoff 才升级 `superpowers` 或 `ECC council`
  - “项目级分阶段”才升级到 `GSD`
  - “需要持久规格文件”才触发 `OpenSpec`
  - “研究外部信息”优先 `research`，不要在 `feat`/`fix` 中默认展开 deep-research
- 将“全量默认安装”解释为“能力可用”，而不是“默认路径必经”。

#### 为什么

- 当前重感主要不是来自命令数量，而是来自 superpowers / ECC / GSD / OpenSpec 叙述上存在部分重叠。
- 一旦职责表清晰，full 模式也可以保持不显重。

### C. 把“标准路径”继续压轻，深度路径显式升级

目标：让标准编程工程体验更像“默认轻量 + 明确升级”，而不是“默认带一堆深度挂件”。

#### 受影响文件

- `commands/tool-feat.md`
- `commands/tool-fix.md`
- `commands/tool-plan.md`
- `commands/tool-refactor.md`
- `commands/tool-review.md`
- `docs/architecture.md`

#### 具体改动

- 重新表述 `--standard`：
  - 默认使用项目原生命令验证
  - 默认仅用 CRG + 轻审查
  - 将 claude-mem / OpenSpec / superpowers 写成“条件触发”
- 将 `--deep` 的升级门槛显式化，避免笼统：
  - 跨模块且接口未定
  - 多 PR / 多阶段
  - 安全敏感
  - 外部系统联动
  - 需要 durable spec / acceptance
- `tool-review` 改成更清晰的三档：
  - `--fast`: 本地小 diff sanity check
  - `--standard`: 正常 PR / local diff review
  - `--deep`: 大改动、重构、安全、交付前总审查
- `tool-research` 强化成“决策前证据命令”，不要把它写成普通 feature/fix 的默认前置步骤。

#### 为什么

- 你的目标是更适合编程工程。
- 编程工程的主流需求是：快速定位、最小改动、跑验证、少切换工作流。

### D. 平台层重构：把 update / sync / health 收成单一心智入口

目标：解决“怎么更方便更新，包括内部各种依赖组件升级”的核心问题。

#### 受影响文件

- `commands/tool-update.md`
- `install.sh`
- `scripts/sync.py`
- `scripts/health.py`
- `docs/install.md`
- `README.md`
- `README_zh.md`

#### 具体改动

- 确立单一用户入口：
  - `/tool-update --check`
  - `/tool-update --full`
  - 文档中不再同时强调 `scripts/sync.py` 作为主入口，只保留为底层脚本
- 调整职责：
  - `install.sh`: 首次安装 + 显式 repair/upgrade hooks
  - `scripts/sync.py`: 只负责 Engineer Shovel 自身文件同步与版本检查
  - `scripts/health.py`: 只负责外部依赖健康检查与 repair
  - `/tool-update`: 编排 sync + health，对用户呈现统一结果
- 为外部组件增加“版本策略矩阵”文档：
  - pinned SHA
  - pinned tag/version
  - latest channel
  - 不同组件为什么采用不同策略
- 将“全量默认安装”下的升级行为拆分为两类：
  - `router update`: 仅更新 Engineer Shovel 自身 skill/commands/docs
  - `component repair/upgrade`: 检查并升级外部组件

#### 为什么

- 当前系统不是不能升级，而是升级路径和内部实现路径没有被同一个心智模型统一起来。
- 用户最需要的是“一个命令知道现在缺什么、旧了什么、能自动修什么、哪些需要手动确认”。

### E. 建立依赖版本治理清单

目标：让全量默认模式不因为上游变化太快而变成不可控的重安装体验。

#### 受影响文件

- `install.sh`
- `CHANGELOG.md`
- `README.md`
- `README_zh.md`
- 新增版本清单文档，例如：`docs/dependency-policy.md`

#### 具体改动

- 建立统一依赖治理表，至少覆盖：
  - 组件名
  - 安装方式
  - 当前锁定策略
  - 升级频率建议
  - 破坏性升级处理方式
- 优先收敛策略不一致问题：
  - 明确哪些组件坚持 pin SHA
  - 哪些允许 latest
  - 哪些应改为“latest only in check/repair recommendation, not auto-upgrade”
- 在 `CHANGELOG.md` 中加入“Upstream dependency changes” 区段，便于跟踪每个版本对外部工具引用策略的变化。

#### 为什么

- 你特别关心内部各种依赖组件的升级。
- 这类问题如果只放在安装脚本里，不形成文档和治理表，后续维护成本会越来越高。

### F. 用“全量默认安装 + 轻量默认执行”作为对外产品主叙事

目标：解决“现在是不是有点重”的对外表述问题。

#### 受影响文件

- `README.md`
- `README_zh.md`
- `SKILL.md`
- `docs/architecture.md`

#### 具体改动

- 统一对外文案：
  - 安装上是 full-by-default，避免用户缺能力
  - 使用上是 lightweight-by-default，避免日常任务走重路径
- 首页增加一个非常短的“实际推荐路线”：
  - 80% 任务：`quick` / `fix` / `feat`
  - 15% 任务：`plan` / `review` / `research`
  - 5% 任务：升级到 OpenSpec / ECC / GSD
- 弱化“工具全家桶”展示，强化“这是一个编程工程路由器”的展示。

#### 为什么

- 当前仓库本质上不是“工具集合”，而是“工具路由产品”。
- 如果对外叙事不改，用户会天然觉得系统重。

## Implementation Steps

### Phase 1: 信息架构与文案收敛

- 更新 `SKILL.md`，重排命令分组与工具定位。
- 更新 `README.md`、`README_zh.md` 首页的命令与工具叙事。
- 更新 `docs/architecture.md`，重写能力层职责表和排它路由规则。

### Phase 2: 命令文档去重与边界收紧

- 精简 `commands/tool-feat.md`、`tool-fix.md`、`tool-plan.md`、`tool-review.md`、`tool-research.md`、`tool-refactor.md` 中重复的升级描述。
- 统一在命令里使用相同的“何时升级”判据。
- 保留 deprecated 命令文件，但进一步缩短 redirect 文案。

### Phase 3: 更新链路收敛

- 重写 `commands/tool-update.md` 的用户心智与流程定义。
- 调整 `scripts/sync.py`、`scripts/health.py` 的职责边界说明。
- 视需要补充 `docs/install.md` 中关于 update / repair / upgrade 的统一入口文档。

### Phase 4: 依赖治理与版本策略

- 新增依赖策略文档。
- 对 `install.sh` 中各依赖的版本固定策略进行统一说明。
- 更新 `CHANGELOG.md` 结构，加入上游依赖策略变化记录。

### Phase 5: 校验与一致性修补

- 确认 `SKILL.md`、README、architecture、commands、install docs 之间术语一致。
- 检查命令数量、deprecated 状态、安装模式、默认路径等是否前后一致。
- 运行现有校验脚本与 CI 等价检查，确保没有引用漂移。

## Verification Steps

- 文档一致性验证：
  - `python3 scripts/validate-command-schema.py`
  - `python3 scripts/validate-references.py`
  - `python3 scripts/validate-markdown-links.py`
- Python 脚本可执行性验证：
  - `python3 -m py_compile scripts/*.py`
  - `pytest`
- 安装器验证：
  - `bash -n install.sh`
  - `bash install.sh --minimal --dry-run`
  - `bash install.sh --recommended --dry-run`
  - `bash install.sh --full --dry-run`
- 架构验收标准：
  - README 首屏能在 1 分钟内说明“默认入口是什么、什么时候升级到重工具”
  - `tool-feat` / `tool-plan` / `tool-research` 的边界不再互相争抢
  - `/tool-update` 成为用户唯一需要记住的更新入口
  - Full install 不再被文案暗示成 full workflow

