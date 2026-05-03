# Engineer Shovel 命令工具链架构

> **⚠️ 重要**: 本文档定义工具在理想状态下的协作架构和各命令的推荐路由。
> **各命令的权威定义以 `commands/tool-*.md` 为准。**
> **v1.4.0**: 8 个活跃命令 + 2 个已废弃 + 2 个辅助命令。brainstorm 已内化、blueprint 已合并到 plan --deep、graph 已后台化。

Engineer Shovel 的命令按**5 层工具架构**编排，每一层解决一类问题。

---

## 5 层工具架构

```
Layer 1: 沟通压缩 (always-on, 无命令)
  caveman → LLM 输出压缩 (lite/full/ultra)
  rtk    → 工具输出压缩 (rtk gain 显式拦截)

Layer 2: 代码智能 (auto-refreshed via git hooks, 无手动词)
  code-review-graph → 架构探索 / 影响分析 / 调试追踪 / 重构辅助 / PR 审查
  {保留 /tool-graph 仅用于手动诊断}

Layer 3: 开发方法论 (process enforcement, on-demand)
  superpowers → brainstorming / writing-plans / tdd-workflow / systematic-debugging / verification

Layer 4: 领域专长 (technical implementation, on-demand)
  ecc → 语言命令 / security-review / review-work / blueprint / council / deep-research / github-ops

Layer 5: 项目管理 (stateful orchestration, 仅多阶段工程)
  gsd → explore / plan-phase / execute-phase / debug / verify-work / ship
```

### 层级原则

1. **从底层往上调用**：命令根据复杂度逐层升级，不越级
2. **压缩层始终开启**：caveman 控制 LLM 冗长，rtk 控制工具输出噪声
3. **代码智能自动运行**：code-review-graph 由 git hooks 自动刷新，命令中静默查询，无需手动管理
4. **ecc vs gsd**：ecc 提供领域专长（怎么做），gsd 管理多阶段工程（做到哪了）
5. **superpowers vs gsd**：superpowers 定义方法纪律，gsd 管理项目阶段状态

---

## 工具总览

| 工具 | 角色 | 触发模式 | Token 成本 |
|------|------|---------|-----------|
| **caveman** | LLM 沟通压缩 | 始终开启，按模式分级 | 降低 ~75% prompt |
| **rtk** | 工具输出压缩 | `rtk gain` 在 test/build/git 前显式调用 | 噪声输出压缩 |
| **code-review-graph** | 代码知识图谱 | git hooks 自动刷新，命令中静默查询 | 低 (~100-500 tokens/查询) |
| **superpowers** | 开发方法论 | 需求不明确/需要纪律时 | 中-高 (多轮对话) |
| **ecc** | 领域专长 | 语言命令、安全审查、深度研究、审查编排、蓝图、架构决策 | 低-高 |
| **gsd** | 项目管理 | 多阶段/里程碑/需持久状态时 | 高 (subagent 并行) |

---

## 核心路由机制

### 成本模式路由

| 模式 | 压缩 | 代码智能 | 方法论 | 领域专长 | 项目管理 |
|------|------|---------|--------|---------|---------|
| `--fast` | caveman lite + rtk | code-review-graph | 不用 | 语言测试 | 不用 |
| `--standard` | caveman full + rtk | code-review-graph | 可选 (brainstorm/tdd) | 语言测试/build | 可选 (explore/debug) |
| `--deep` | caveman full/ultra + rtk | code-review-graph | 可选 (plans/tdd) | security-review/review-work/council | gsd 重量流程 |

### 关键排他规则

以下工具对解决同一问题，按场景选一，**不并列**：

| 场景 | 选 superpowers | 选 gsd | 选 ecc | 判断标准 |
|------|--------------|--------|--------|---------|
| 需求澄清 | brainstorming (技术设计) | gsd-explore (产品方向) | council (多方案架构) | 技术实现 vs 业务目标 vs 高风险决策 |
| 制定计划 | writing-plans (实现计划) | gsd-plan-phase (阶段规划) | blueprint (代码依赖图) | ≤3 PR vs 多阶段 vs 依赖图密集 |
| 并行执行 | subagent-driven-development | gsd-execute-phase | — | 临时并行任务 vs 阶段 wave 编排 |
| 调试 | systematic-debugging (方法论) | gsd-debug (持久状态) | deep-research (新领域) | 单次 vs 跨上下文 vs 技术未知 |
| 审查 | — | gsd-code-review | review-work (5-agent) | — vs 阶段审查 vs 重量并行审查 |
| 蓝图 | — | gsd project (里程碑) | blueprint (代码 PR) | — vs 里程碑工程 vs 代码层多 PR |

---

## 1. /tool-quick — 简单编辑

> 1-2 文件，逻辑明确 | 默认成本: Low

### 路由

```
--fast (默认): caveman lite → code-review-graph 上下文 → 直接编辑 → rtk gain → 语法验证 → 验证门
--standard:    caveman full → code-review-graph 上下文 → 编辑 → rtk gain → 语言测试 → caveman review → 验证门
```

**调用**: caveman + rtk + code-review-graph + ecc (语言测试)
**不经过**: superpowers, gsd

---

## 2. /tool-fix — Bug 修复

> Bug / 失败测试 / 回归 | 默认成本: Low → High

### 路由

```
--fast:
  caveman lite → code-review-graph 追踪 → 直接修复 → rtk gain → 语言测试 → 验证门

--standard (默认):
  caveman full → rtk gain → 复现 → code-review-graph 追踪
  → [简单→直接修复 | 复杂→superpowers:systematic-debugging]
  → rtk gain → 语言测试 → code-review-graph 影响分析
  → 可选: superpowers:tdd-workflow (回归测试)
  → 验证门 (test → graph impact → caveman review)

--deep:
  caveman full/ultra → rtk gain → ecc:deep-research (flaky/新领域)
  → gsd-debug (持久状态)
  → superpowers:systematic-debugging
  → code-review-graph 追踪 + 影响分析
  → 修复 → rtk gain → 语言测试 → security-review (如涉安全)
  → 验证门
```

**调用**: caveman + rtk + code-review-graph + superpowers + ecc + gsd (debug)
**安全门**: 涉及 auth/input/secret/cookie/sql/fs → 自动加 security-review

---

## 3. /tool-feat — 新功能

> 新功能开发 (内置脑暴) | 默认成本: Medium

### 路由

```
Phase 0 (需求不明确时自动触发):
  产品方向不清 → gsd-explore
  技术方案不清 → superpowers:brainstorming
  多方案决策 → ecc:council

--fast (≤2 文件):
  caveman lite → code-review-graph 架构探索 → 实现 → rtk gain → 语言测试 → 验证门

--standard (默认, 3-8 文件):
  caveman full → rtk gain → code-review-graph 探索现有架构
  → 需求明确? → 直接实现
  → 需求模糊? → Phase 0 (脑暴)
  → superpowers:tdd-workflow (可选)
  → rtk gain → 语言测试/build → caveman review → 验证门

--deep (多组件/有歧义):
  caveman full → rtk gain → code-review-graph 探索
  → Phase 0 (脑暴)
  → superpowers:writing-plans
  → 实现 → rtk gain → 语言测试 → security-review (内容感知)
  → /tool-review --deep 或 ecc:review-work (重大实现)
```

**调用**: caveman + rtk + code-review-graph + superpowers + ecc + gsd (explore)
**短路**: 用户描述已明确命名文件和类 → 跳过 Phase 0
**安全门**: 涉及 auth/input/secret/cookie → 自动加 security-review

---

## 4. /tool-plan — 统一规划

> 规划 → 自动升级 → 路由执行 | 默认成本: Medium

### 路由

```
Phase 0 (方向不明确时自动触发):
  产品方向不清 → gsd-explore
  技术方案不清 → superpowers:brainstorming
  多方案决策 → ecc:council

--fast:
  简短内联计划 → 路由 /tool-feat 或 /tool-quick

--standard (默认):
  caveman full → Phase 0 (如需要)
  → superpowers:writing-plans → 路由执行

--deep (自动分类):
  caveman full → Phase 0 (如需要)
  → 自动判断复杂度:
    • ≤3 PR 代码工作 → ecc:blueprint + superpowers:writing-plans
    • >3 PR / 里程碑级 → gsd project (discuss → plan → execute phases)
    • 系统架构变更 → ecc:council → 必要时转 blueprint
```

**调用**: caveman + gsd (explore, project) + superpowers (brainstorm, plans) + ecc (council, blueprint)
**排他**: gsd-explore vs brainstorming vs council 三选一；ecc:blueprint vs gsd project 二选一

---

## 5. /tool-refactor — 重构

> 行为不变的结构优化 | 默认成本: Medium

### 路由

```
--fast (单文件):
  caveman lite → 基线测试 → code-review-graph 辅助重构 → 验证测试 → 验证门

--standard (默认):
  caveman full → rtk gain → 基线测试 (全绿)
  → code-review-graph 影响分析
  → 小步重构 → 每步验证 → rtk gain → 语言测试
  → 验证门

--deep (架构级):
  caveman full/ultra → rtk gain → 基线测试
  → code-review-graph 全调用链分析
  → gsd-execute-phase (强制分阶段管理)
  → superpowers:tdd-workflow
  → rtk gain → 语言测试/build → ecc:review-work (5-agent 审查)
  → e2e-testing (如适用)
  → 验证门
```

**调用**: caveman + rtk + code-review-graph + superpowers (tdd) + gsd (execute, 强制) + ecc (review-work)
**安全门**: 涉及安全敏感路径 → 自动加 security-review

---

## 6. /tool-review — 代码审查

> 本地 diff / PR / 实现后 | 默认成本: Low → High

### 路由

```
--fast (快速检查):
  caveman review mode → git diff → 压缩审查 → 问题列表

--standard (默认, PR/本地):
  caveman full → rtk gain → code-review-graph 辅助分析
  → [本地 diff → caveman review | PR → ecc:coding-standards + ecc:github-ops]
  → 结构化报告 + 合并建议

--deep (重大实现):
  caveman full/ultra → rtk gain → code-review-graph 辅助分析
  → ecc:github-ops (PR 管理) → ecc:review-work (5-agent 并行)
  → security-review (如涉安全) → 全面报告 + 行动项

Post-review:
  superpowers:receiving-code-review (反馈应用)
```

**调用**: caveman + rtk + code-review-graph + ecc (github-ops, review-work, security-review) + superpowers (receiving-review)
**不经过**: gsd

---

## 7. /tool-research — 技术研究

> 代码库感知的快速查证 / Web 搜索 / 深度研究 | 默认成本: Low → High

### 路由

```
--quick (默认): code-review-graph 架构上下文 → 本地文档/已知库 → 总结 + 引用
--web:          code-review-graph 上下文 → web/docs 搜索 → 结构化对比表
--deep:         code-review-graph 架构探索 → ecc:deep-research → 综合报告 → 可选 ecc:council
```

**调用**: code-review-graph + Web search + context7 + ecc (deep-research, council)
**不经过**: superpowers, gsd

---

## 8. /tool-graph — 知识图谱诊断

> 手动诊断 | 默认成本: Low

### 子命令

```
status:   查看图谱 state + 统计
build:    全量构建 (首次安装时)
update:   手动更新 (仅当 git hook 不可用时)
rebuild:  清空 + 全量构建
watch:    文件监听自动更新 (需用户批准)
```

### 自动刷新机制

图谱由 git hooks 自动保持新鲜，其他命令无需手动刷新：
- `post-commit` → `code-review-graph update`
- `post-checkout` → `code-review-graph update`

**调用**: caveman + rtk + code-review-graph
**不经过**: superpowers, gsd, ecc

---

## 已废弃命令

### /tool-brainstorm — DEPRECATED

脑暴已内化为 `/tool-feat` 和 `/tool-plan` 的 Phase 0。命令文件保留重定向说明。

### /tool-blueprint — DEPRECATED

蓝图已合并到 `/tool-plan --deep`。命令文件保留重定向说明。

---

## /tool-branch — 辅助命令

> 分支生命周期 (feat/fix 自动调用) | 默认成本: Low

```
create/status/merge/abort:
  caveman lite → bash scripts/branch-workflow.sh

review:
  caveman full → code-review-graph 辅助审查
  → bash scripts/branch-workflow.sh review
```

**调用**: caveman + code-review-graph (review) + scripts
**不经过**: rtk, superpowers, gsd, ecc

---

## /tool-update — 同步更新

> 检查/全量更新安装 | 默认成本: Low

```
--check: 只读比较 → 报告缺失/过期/多余 → 组件健康检查
--full:  覆盖安装 → 配置缺失组件 → 验证完整性
```

**调用**: caveman + 自定义文件同步 + 组件 installer
**不经过**: code-review-graph, superpowers, gsd, ecc

---

## 全量对比矩阵

### 命令 × 工具调用

| 命令 | caveman | rtk | code-review-graph | superpowers | gsd | ecc |
|------|---------|-----|-------------------|-------------|-----|-----|
| **quick** | ✅ | ✅ test/build | ✅ context | ❌ | ❌ | ✅ 语言测试 |
| **fix** | ✅ | ✅ test/log | ✅ trace/impact | ✅ sysdbg/tdd | ✅ debug(deep) | ✅ 语言/安全/deep-research |
| **feat** | ✅ | ✅ test/build | ✅ explore | ✅ brain/plans/tdd | ✅ explore(Phase0) | ✅ 语言/安全/council(deep) |
| **plan** | ✅ | ❌ | ✅ impact | ✅ brain/plans | ✅ explore/project | ✅ council/blueprint |
| **refactor** | ✅ | ✅ test/build | ✅ impact/patterns | ✅ tdd | ✅ execute(deep 强制) | ✅ review-work |
| **review** | ✅ | ✅ diff/log | ✅ pr-review | ✅ receiving-review | ❌ | ✅ github-ops/review-work |
| **research** | ✅ | ❌ | ✅ codebase context | ❌ | ❌ | ✅ deep-research/council |
| **graph** | ✅ | ✅ build/update | ✅ 全部 | ❌ | ❌ | ❌ |
| **branch** | ✅ | ❌ | ✅ pr-review | ❌ | ❌ | ❌ |
| **update** | ✅ | ❌ | ⚠️ install | ⚠️ install | ⚠️ install | ⚠️ install |

### 排他路由规则表

| 场景 | 轻量路径 | 重量路径 | 重量路径 2 | 判断标准 |
|------|---------|---------|----------|---------|
| 需求澄清 | superpowers:brainstorming | gsd-explore | ecc:council | 技术设计 vs 产品方向 vs 高风险架构 |
| 制定计划 | superpowers:writing-plans | gsd-plan-phase | ecc:blueprint | ≤3 PR vs 多阶段 vs 依赖图密集 |
| 并行执行 | superpowers:subagent-driven | gsd-execute-phase | — | 临时任务 vs 阶段编排 |
| 调试方法论 | superpowers:systematic-debugging | gsd-debug | ecc:deep-research | 单次 vs 跨上下文 vs 技术未知 |
| 代码审查 | caveman-review | gsd-code-review | ecc:review-work | 快速 vs 阶段 vs 重量并行 |
| 项目规划 | ecc:blueprint | gsd project | — | 代码 PR 项目 vs 里程碑工程 |

### Token 消耗总览

| 命令 | 低开销 | 中开销 | 高开销 |
|------|--------|--------|--------|
| quick | --fast (极低) | --standard (低) | - |
| fix | --fast (低) | --standard (中) | --deep (高) |
| feat | --fast (低) | --standard (中) | --deep (高) |
| plan | --fast (极低) | --standard (中) | --deep (中-高) |
| refactor | --fast (低) | --standard (中) | --deep (高) |
| review | --fast (低) | --standard (中) | --deep (高) |
| research | --quick (低) | --web (中) | --deep (高) |
| graph | status/watch (极低) | build/update/rebuild (中) | - |
| branch | create/status/merge/abort (极低) | review (低) | - |
| update | --check (低) | --full (低) | - |

### RTK 触发点速查

| 命令 | 何时调用 `rtk gain` |
|------|-------------------|
| quick (--standard) | 语言测试前 |
| fix | 复现/错误日志 → 测试 → 回归测试前 |
| feat | 测试/build 前 |
| refactor | 基线测试 → 每步验证 → 最终测试前 |
| review | diff/log 获取前 |
| graph | build/update 构建输出前 |

---

*基于 ECC + GSD + superpowers + code-review-graph + Caveman + RTK 深度整合*
*最后更新: 2026-05-03 — v1.4.0*
