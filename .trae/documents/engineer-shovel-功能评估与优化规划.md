# Engineer Shovel 功能评估与优化规划

## Summary

- 目标：对当前项目功能做一次产品设计导向的盘点，判断整体设计是否合理，并给出一组可执行的优化方案。
- 结论预览：当前项目的核心定位基本合理，即“轻量工作流路由器 + 可选能力层”；但命令边界、模式叙事、外部能力升级、文档密度与实现一致性之间仍有明显摩擦，导致用户认知成本偏高。
- 本计划优先级：先收敛产品心智模型与文档结构，再修复与产品承诺直接冲突的实现问题，最后补强验证与一致性约束。
- 用户偏好：本轮以“产品设计优先”为主，不把脚本级 bug 修复作为唯一目标，但会把高风险实现缺口纳入计划，作为“当前设计是否合理”的证据。

## Current State Analysis

### 1. 当前实际功能版图

- 入口层：
  - `SKILL.md` 提供轻量路由器入口。
  - `commands/` 下有 12 个命令文件，其中 10 个活跃命令，2 个兼容重定向命令。
- 长文档层：
  - `README.md`、`README_zh.md` 负责对外介绍、安装说明、功能边界。
  - `docs/architecture.md`、`docs/mode-routing.md`、`docs/token-cost.md` 等负责深度规则与方法论。
- 安装与维护层：
  - `install.sh` 负责首次安装、模式选择、组件安装。
  - `scripts/sync.py` 负责路由器文件同步。
  - `scripts/health.py` 负责外部组件健康检查与 repair。
  - `commands/tool-update.md` 将上述能力包装成统一更新入口。
- 质量保障层：
  - `.github/workflows/ci.yml` 负责 schema、引用、链接、安装器 dry-run、脚本编译与 pytest。
  - `tests/test_validation_scripts.py` 已覆盖部分验证脚本与安装/健康检查行为。

### 2. 目前设计中“合理”的部分

- 产品定位基本清晰：
  - `README.md`
  - `SKILL.md`
  - `docs/architecture.md`
  三者都围绕“full capability available, lightweight execution by default”展开，主张一致。
- 命令分层本身是合理的：
  - 主工作流：`quick` / `fix` / `feat` / `plan`
  - 支持命令：`review` / `refactor` / `research`
  - 平台命令：`branch` / `graph` / `update`
- 更新链路职责划分是合理的：
  - `install.sh` 负责安装
  - `scripts/sync.py` 负责 router 同步
  - `scripts/health.py` 负责组件健康
  - `/tool-update` 作为统一入口
- CI 已经开始把“文档型产品”的一致性纳入自动校验，这点是成熟方向。

### 3. 目前设计中“不够合理”或存在摩擦的部分

- 心智模型仍然偏重：
  - README 与多份文档反复解释命令、模式、能力层、压缩层、图谱层、记忆层，虽然信息完整，但首次理解成本高。
- 命令职责有局部重叠：
  - `tool-plan`、`tool-feat`、`tool-research` 都内置了不同形式的 “Phase 0 / clarify / research”。
  - `tool-review` 既是独立任务入口，又被作为其他命令的补充收尾，用户容易误解其默认触发边界。
  - `tool-graph` 被定义为“只做诊断”，但其他命令文本中仍频繁要求用户理解 graph 行为，放大了平台层存在感。
- 模式体系存在一处认知断层：
  - 全局主叙事是 `--fast / --standard / --deep`。
  - 但 `tool-research` 使用 `--quick / --web / --deep`，虽然文档解释过，但仍破坏了统一性。
- 命令文档复用不足：
  - 多个 `commands/tool-*.md` 重复描述相同的共享策略，和 `SKILL.md`、`docs/architecture.md` 形成重复信息。
  - `docs/token-cost.md` 已经明确把“重复 workflow definitions”列为成本来源，说明问题已被识别，但尚未彻底落到内容瘦身。
- 产品承诺与实现存在至少一个直接冲突：
  - `scripts/sync.py` 中 `compare_files()` 只定义了 2 个参数，但在 `main()` 的 sync 分支里被以 3 个参数调用。
  - 这意味着 `/tool-update --full` 对应的 router sync 主路径可能在运行时报错，削弱“统一更新入口”这一核心产品承诺。
- 测试覆盖更偏“存在性/文案一致性”，对主流程行为的覆盖还不够：
  - `tests/test_validation_scripts.py` 覆盖了不少 helper 和 repair command 组装，但没有锁住 `scripts/sync.py` 的 sync 主路径参数正确性。

## Assumptions & Decisions

- 假设 1：本轮优化的目标不是增加新命令，而是在不破坏现有 public interface 的前提下，降低认知成本并修复关键断裂点。
- 假设 2：应保持以下公共接口稳定：
  - `skill(name="engineer-shovel")`
  - 现有 `/tool-*` 命令名
  - `--minimal / --recommended / --full`
- 决策 1：将“产品设计优化”拆成三层推进：
  - 第一层：收敛对外叙事和用户心智模型
  - 第二层：收缩命令文档重复与边界重叠
  - 第三层：补足直接影响产品可信度的实现与测试
- 决策 2：不建议本轮重做命令体系；更适合做“减法优化”而不是“推倒重构”。
- 决策 3：把 `tool-research` 的模式命名一致性、`tool-plan` 与 `tool-feat` 的前置澄清重复、`tool-review` 的职责边界，视为产品设计优先级最高的问题。

## Proposed Changes

### A. 收敛“项目到底是什么”的单一句子叙事

- 文件：
  - `README.md`
  - `README_zh.md`
  - `SKILL.md`
  - `docs/architecture.md`
- 变更：
  - 统一将项目表述压缩为：
    - “一个面向 OpenCode / Claude Code 的轻量工作流路由器”
    - “默认只在主命令层工作，外部工具是可升级能力层”
  - 将“安装了很多组件”与“默认会走很重工作流”进一步拆开表达，减少用户误读。
- 原因：
  - 现在叙事已经基本正确，但篇幅和重复度过高，影响第一印象与可理解性。

### B. 重新压缩命令边界文案，减少职责重叠感

- 文件：
  - `commands/tool-plan.md`
  - `commands/tool-feat.md`
  - `commands/tool-fix.md`
  - `commands/tool-review.md`
  - `commands/tool-research.md`
  - `commands/tool-quick.md`
  - `docs/mode-routing.md`
- 变更：
  - 将“Phase 0 / clarify / research”抽成统一规则，只在最适合承接它的地方保留主定义。
  - 建议边界改写方向：
    - `tool-plan`：只负责范围、顺序、验收、执行条件不清时的规划。
    - `tool-feat`：只负责“已决定要做”的功能切片实现，不再承担过多前置策略解释。
    - `tool-research`：只负责为一个具体决策收集证据，不再像“通用预处理器”。
    - `tool-review`：明确是“审查本身是任务”时使用，而不是所有主命令的默认前门。
  - `docs/mode-routing.md` 保留矩阵与全局决策树；命令文件只写差异，不再重复共享规则。
- 原因：
  - 当前最大问题不是命令数量，而是命令之间的边界叙事还不够“互斥”。

### C. 简化模式体系，让全局与局部更一致

- 文件：
  - `docs/mode-routing.md`
  - `commands/tool-research.md`
  - `README.md`
  - `README_zh.md`
- 变更：
  - 评估是否将 `tool-research` 的 `--quick / --web / --deep` 重命名或包装成更贴近全局模式的表达。
  - 如果不改 CLI 形态，也应在文档中明确：
    - “research 是特例模式轴”
    - “这是内容来源维度，而不是成本维度”
  - 在 README 中只保留一张最小决策表，避免多处重复解释模式。
- 原因：
  - 统一模式是用户快速上手的关键；即便保留特例，也要把特例讲得更短更清楚。

### D. 先修复与产品承诺直接冲突的实现问题

- 文件：
  - `scripts/sync.py`
  - `tests/test_validation_scripts.py`
- 变更：
  - 修复 `compare_files(installed, repo, ROOT)` 的错误调用，使 `sync` 主路径可执行。
  - 为 `sync` 的主流程补充最小测试，至少覆盖：
    - `sync` 分支不会因参数错误崩溃
    - `--target both`、`--scope local/global` 的主循环能正确调用 compare/sync
    - `--skip-health` 和 `run_health()` 的组合路径正确
- 原因：
  - 产品设计再合理，如果更新入口主路径会报错，就会直接破坏可信度。

### E. 强化“文档型产品”的一致性验证，而不是只做文案校验

- 文件：
  - `tests/test_validation_scripts.py`
  - `scripts/validate-references.py`
  - 可能新增：`scripts/validate-product-shape.py` 或在现有验证脚本中扩展
- 变更：
  - 增加面向产品约束的验证：
    - 主命令数量与 README / SKILL / localized README 一致
    - `tool-research` 的特例模式是否被 README 和 mode-routing 清楚说明
    - `tool-graph` 是否仍被表达为“诊断命令”，避免再次漂移为普通入口
    - `tool-update` 是否仍明确为唯一更新入口
  - 对“共享规则只保留在少数文件”建立静态检查，避免后续重复膨胀。
- 原因：
  - 当前仓库的主要资产是“产品规则 + 安装编排 + 文档路由”；验证脚本应对这些规则负责。

### F. 对外输出一份更短的“命令选择表”

- 文件：
  - `README.md`
  - `README_zh.md`
  - 可选新增：`docs/command-selection.md`
- 变更：
  - 将用户最常见的问题压缩成一张表：
    - 小改动用什么
    - Bug 用什么
    - 新功能用什么
    - 不知道怎么做时用什么
    - 研究/审查/平台维护何时才出现
  - 如果新增文档，则 README 只保留摘要，不再承载全部解释。
- 原因：
  - 现在信息很全，但用户需要先读很多内容才能形成“下一步该点哪个命令”的确定感。

## Execution Order

1. 先完成产品边界收敛：
   - `README.md`
   - `README_zh.md`
   - `SKILL.md`
   - `docs/architecture.md`
2. 再完成命令文案瘦身与分工清晰化：
   - `docs/mode-routing.md`
   - `commands/tool-plan.md`
   - `commands/tool-feat.md`
   - `commands/tool-research.md`
   - `commands/tool-review.md`
   - 视需要调整 `commands/tool-quick.md`、`commands/tool-fix.md`
3. 然后修复关键实现缺口：
   - `scripts/sync.py`
4. 最后补验证与回归保护：
   - `tests/test_validation_scripts.py`
   - 相关验证脚本

## Verification

- 文档与结构验证：
  - 运行 `python3 scripts/validate-command-schema.py`
  - 运行 `python3 scripts/validate-references.py`
  - 运行 `python3 scripts/validate-markdown-links.py`
  - 运行 `python3 scripts/validate-installer-sources.py`
- Python 回归：
  - 运行 `pytest`
- 安装器与更新链路验证：
  - 运行 `bash install.sh --minimal --dry-run`
  - 运行 `bash install.sh --recommended --dry-run`
  - 运行 `bash install.sh --full --dry-run`
  - 定向验证 `scripts/sync.py` 的 `check` / `sync --dry-run` 路径
- 人工验收：
  - 只阅读 `README.md` 和 `README_zh.md` 顶部内容，确认用户能在 1 分钟内理解：
    - 项目是什么
    - 什么时候用 `quick/fix/feat/plan`
    - 什么时候才需要 `review/research/graph/update`
  - 只阅读单个 `commands/tool-*.md`，确认不需要再重复读完整架构文档也能理解该命令的职责边界

## Expected Outcome

- 保持现有 public interface 不变。
- 用户更容易理解项目的主价值与命令选择。
- 命令间职责边界更清晰，减少“到底该用 plan 还是 feat/research”的犹豫。
- 文档重复度下降，长期维护成本降低。
- `/tool-update` 相关主路径更可信，产品承诺与实现更加一致。
