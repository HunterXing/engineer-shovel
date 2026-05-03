# Engineer Shovel 12 命令工具链架构

> **⚠️ 重要**: 本文档定义工具在理想状态下的协作架构和各命令的推荐路由。
> **各命令的权威定义以 `commands/tool-*.md` 为准。**

Engineer Shovel 的 12 个 `/tool-*` 命令按**5 层工具架构**编排，每一层解决一类问题。

---

## 5 层工具架构

```
Layer 1: 沟通压缩 (always-on)
  caveman → LLM 输出压缩 (lite/full/ultra)
  rtk    → 工具输出压缩 (rtk gain 显式拦截)

Layer 2: 代码智能 (pre-action, on-demand)
  code-review-graph → 架构探索 / 影响分析 / 调试追踪 / 安全重构 / PR 审查

Layer 3: 开发方法论 (process enforcement)
  superpowers → brainstorming / writing-plans / tdd-workflow / systematic-debugging / verification

Layer 4: 项目管理 (stateful orchestration)
  gsd → explore / plan-phase / execute-phase / debug / verify-work / ship / note

Layer 5: 领域专长 (technical implementation)
  ecc → 语言命令 / security-review / review-work / blueprint / council / deep-research / github-ops
```

### 层级原则

1. **从底层往上调用**：命令根据复杂度逐层升级，不越级
2. **压缩层始终开启**：caveman 控制 LLM 冗长，rtk 控制工具输出噪声
3. **代码智能先于行动**：所有涉及代码理解/修改的命令，先刷新图再操作
4. **方法论 vs 项目管理**：superpowers 定义「怎么做」，gsd 定义「做到哪了」

---

## 工具总览

| 工具 | 角色 | 触发模式 | Token 成本 |
|------|------|---------|-----------|
| **caveman** | LLM 沟通压缩 | 始终开启，按模式分级 | 降低 ~75% prompt |
| **rtk** | 工具输出压缩 | `rtk gain` 在 test/build/git 前显式调用 | 噪声输出压缩 |
| **code-review-graph** | 代码知识图谱 | pre-action 查询（exploring/debugging/impact/refactor/pr-review） | 低 (~100-500 tokens/查询) |
| **superpowers** | 开发方法论 | 需求不明确/需要纪律时 | 中-高 (多轮对话) |
| **gsd** | 项目管理 | 多阶段/里程碑/需持久状态时 | 高 (subagent 并行) |
| **ecc** | 领域专长 | 语言命令、安全审查、深度研究、蓝图 | 低-高 |

---

## 核心路由机制

### 成本模式路由

| 模式 | 压缩 | 代码智能 | 方法论 | 项目管理 | 领域专长 |
|------|------|---------|--------|---------|---------|
| `--fast` | caveman lite + rtk | 可选查询 | 不用 | 不用 | 语言测试 |
| `--standard` | caveman full + rtk | code-review-graph (可选) | 可选 (brainstorm/tdd) | 可选 (explore/debug) | 语言测试/build |
| `--deep` | caveman full/ultra + rtk | code-review-graph (可选) | 可选 (plans/tdd) | gsd 重量流程 | security-review/review-work |

### 关键排他规则

以下工具对解决同一问题，按场景选一，**不并列**：

| 场景 | 选 superpowers | 选 gsd | 判断标准 |
|------|--------------|--------|---------|
| 需求澄清 | brainstorming (技术设计) | gsd-explore (产品方向) | 技术方案不明确 vs 业务目标不清晰 |
| 制定计划 | writing-plans (实现计划) | gsd-plan-phase (阶段规划) | ≤3 PR vs 多阶段里程碑 |
| 并行执行 | subagent-driven-development | gsd-execute-phase | 临时并行任务 vs 阶段 wave 编排 |
| 调试 | systematic-debugging (方法论) | gsd-debug (持久状态) | 单次调试 vs 跨上下文重置 |
| 审查 | code-review-graph:pr-review | gsd-code-review | PR 级代码分析 vs 阶段级项目审查 |

---

## 1. /tool-quick — 简单编辑

> 1-2 文件，逻辑明确 | 默认成本: Low

### 路由

```
--fast (默认): caveman lite → 直接编辑 → rtk gain → 语法验证 → commit
--standard:    caveman full → 编辑 → rtk gain → 语言测试 → caveman review → commit
```

**调用**: caveman + rtk + ecc (语言测试)
**不经过**: code-review-graph, superpowers, gsd

---

## 2. /tool-fix — Bug 修复

> Bug / 失败测试 / 回归 | 默认成本: Low → High

### 路由

```
--fast:
  caveman lite → 直接修复 → rtk gain → 语言测试 → commit

--standard (默认):
  caveman full → rtk gain → 复现 → code-review-graph 追踪
  → [简单→直接修复 | 复杂→superpowers:systematic-debugging]
  → rtk gain → 语言测试 → code-review-graph 影响分析
  → 可选: superpowers:tdd-workflow (回归测试)
  → caveman review → commit

--deep:
  caveman full/ultra → rtk gain → gsd-debug (持久状态)
  → code-review-graph 追踪 + 影响分析
  → superpowers:systematic-debugging
  → 修复 → rtk gain → 语言测试 → security-review (如涉安全)
  → caveman review → commit
```

**调用**: caveman + rtk + code-review-graph + superpowers + gsd (debug) + ecc
**安全门**: 涉及 auth/input/secret/cookie/sql/fs → 自动加 security-review

---

## 3. /tool-feat — 新功能

> 新功能开发 | 默认成本: Medium

### 路由

```
--fast (≤2 文件):
  caveman lite → code-review-graph 架构探索 → 实现 → rtk gain → 语言测试 → commit

--standard (默认, 3-8 文件):
  caveman full → rtk gain → code-review-graph 探索现有架构
  → 需求明确? → 直接实现
  → 需求模糊? → superpowers:brainstorming (技术设计)
  → superpowers:tdd-workflow (可选)
  → rtk gain → 语言测试/build → caveman review → commit

--deep (多组件/有歧义):
  caveman full → rtk gain → code-review-graph 探索
  → superpowers:brainstorming → superpowers:writing-plans
  → [≤3 PR → 按 plan 实现 | >3 PR → /tool-blueprint]
  → rtk gain → 语言测试 → security-review (内容感知) → /tool-review --deep
```

**调用**: caveman + rtk + code-review-graph + superpowers + ecc
**短路**: 用户描述已明确命名文件和类 → 跳过 brainstorm + plan
**安全门**: 涉及 auth/input/secret/cookie → 自动加 security-review

---

## 4. /tool-branch — 分支工作流

> 创建/审查/合并/放弃 | 默认成本: Low

### 路由

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

## 5. /tool-plan — 需求与实现规划

> 规划 → 审查 → 路由执行 | 默认成本: Medium

### 路由

```
--fast:
  简短内联计划 → 路由 /tool-feat 或 /tool-quick

--standard (默认):
  caveman full → [产品方向不清晰 → gsd-explore]
  → [技术方案不明确 → superpowers:brainstorming]
  → [≤3 PR → superpowers:writing-plans | >3 PR → /tool-blueprint]
  → 路由执行

--deep (多阶段/多方案):
  caveman full → gsd-explore → superpowers:brainstorming
  → {gsd-plan-phase (阶段级) | /blueprint (代码级)}
  → /tool-plan --reviews (如有评审反馈)
```

**调用**: caveman + gsd (explore, plan-phase) + superpowers (brainstorm, plans) + ecc (blueprint)
**排他**: gsd-explore vs brainstorming 二选一；gsd-plan-phase vs /blueprint 二选一

---

## 6. /tool-refactor — 重构

> 行为不变的结构优化 | 默认成本: Medium

### 路由

```
--fast (单文件):
  caveman lite → 基线测试 → code-review-graph 辅助重构 → 验证测试 → commit

--standard (默认):
  caveman full → rtk gain → 基线测试 (全绿)
  → code-review-graph 影响分析
  → 小步重构 → 每步验证 → rtk gain → 语言测试
  → caveman review → commit

--deep (架构级):
  caveman full/ultra → rtk gain → 基线测试
  → code-review-graph 全调用链分析
  → gsd-execute-phase (分阶段, 可选)
  → superpowers:tdd-workflow
  → rtk gain → 语言测试/build → review-work (5-agent 审查)
  → e2e-testing (如适用)
```

**调用**: caveman + rtk + code-review-graph + superpowers (tdd) + gsd (execute, 可选) + ecc
**安全门**: 涉及安全敏感路径 → 自动加 security-review

---

## 7. /tool-review — 代码审查

> 本地 diff / PR / 实现后 | 默认成本: Low → High

### 路由

```
--fast (快速检查):
  caveman review mode → git diff → 压缩审查 → 问题列表

--standard (默认, PR/本地):
  caveman full → rtk gain → code-review-graph 辅助分析
  → [本地 diff → caveman review | PR → /code-review 或 /review-pr]
  → 结构化报告 + 合并建议

--deep (重大实现):
  caveman full/ultra → rtk gain → code-review-graph 辅助分析
  → review-work (5-agent 并行) → security-review (如涉安全)
  → caveman review → 全面报告 + 行动项
```

**调用**: caveman + rtk + code-review-graph + ecc (github-ops, review-work, security-review)
**不经过**: superpowers, gsd

---

## 8. /tool-brainstorm — 头脑风暴

> 想法澄清 → 路由执行 | 默认成本: Low → Medium

### 路由

```
--fast:
  快速记录想法 → 路由 backlog

--standard (默认):
  caveman full → [产品方向 → gsd-explore (苏格拉底式)]
  → [技术方案 → superpowers:brainstorming (9 步设计精炼)]
  → 路由 /tool-plan 或 /tool-feat

--deep (多方案决策):
  caveman full → gsd-explore → superpowers:brainstorming
  → council (4-voice 决策) → 路由 /tool-plan
```

**调用**: caveman + gsd (explore) + superpowers (brainstorming) + ecc (council)
**排他**: gsd-explore (产品方向) vs superpowers:brainstorming (技术方案) 二选一

---

## 9. /tool-blueprint — 多步骤项目

> 多 PR / 多阶段工程 | 默认成本: High

### 路由

```
--standard (多 PR 代码项目):
  caveman full → code-review-graph 探索架构
  → superpowers:brainstorming → superpowers:writing-plans
  → ecc:blueprint (PR-sized steps + dependency graph)
  → 逐步用 /tool-feat 或 /tool-quick 执行

--deep (里程碑级工程):
  caveman full/ultra → code-review-graph 架构探索
  → gsd 项目初始化 → discuss → plan → execute phases
  → gsd-verify-work → gsd-ship → gsd-milestone-summary
```

**调用**: caveman + code-review-graph + superpowers + ecc (blueprint) 或 gsd (project phases)
**排他**: ecc:blueprint (代码 PR) vs gsd project (里程碑工程) 二选一

---

## 10. /tool-research — 技术研究

> 快速查证 / Web 搜索 / 深度研究 | 默认成本: Low → High

### 路由

```
--quick (默认): 本地文档/已知库 → 总结 + 引用
--web:           web/docs 搜索 → 结构化对比表
--deep:          多源搜索 → 综合报告 (deep-research) → 可选 council
```

**调用**: Web search + context7 + ecc (deep-research, council)
**不经过**: code-review-graph, superpowers, gsd

---

## 11. /tool-graph — 知识图谱操作

> 状态 / 构建 / 更新 / 重建 / 监听 | 默认成本: Low

### 子命令

```
status:   查看图谱 state + 统计
build:    全量构建 → rtk 压缩输出
update:   增量更新 (git diff → 解析变更文件)
rebuild:  清空 + 全量构建
watch:    文件监听自动更新 (需用户批准)
```

### 集成提示

图谱被以下命令自动利用：
- `/tool-fix` → code-review-graph 追踪 + 影响分析
- `/tool-feat` → code-review-graph 架构探索
- `/tool-refactor` → code-review-graph 重构辅助 + 影响分析
- `/tool-review` → code-review-graph PR 分析
- `/tool-branch review` → code-review-graph diff 分析

**调用**: caveman + code-review-graph + rtk (build/update)
**不经过**: superpowers, gsd, ecc

---

## 12. /tool-update — 同步更新

> 检查/全量更新安装 | 默认成本: Low

### 路由

```
--check: 只读比较 → 报告缺失/过期/多余 → 组件健康检查
--full:  覆盖安装 → 配置缺失组件 → 验证完整性
```

**调用**: caveman + 自定义文件同步 + 组件 installer
**不经过**: code-review-graph, superpowers, gsd, ecc

---

## 全量对比矩阵

### 12 命令 × 工具调用

| 命令 | caveman | rtk | code-review-graph | superpowers | gsd | ecc |
|------|---------|-----|-------------------|-------------|-----|-----|
| **quick** | ✅ | ✅ test/build | ❌ | ❌ | ❌ | ✅ 语言测试 |
| **fix** | ✅ | ✅ test/log | ✅ debugging/impact | ✅ sysdbg/tdd(可选) | ✅ debug(deep) | ✅ 语言/安全 |
| **feat** | ✅ | ✅ test/build | ✅ exploring | ✅ brainstorm/plans/tdd | ⚠️ execute(deep) | ✅ 语言/安全 |
| **branch** | ✅ | ❌ | ✅ pr-review(review) | ❌ | ❌ | ❌ |
| **plan** | ✅ | ❌ | ❌ | ✅ brainstorm/plans | ✅ explore/plan-phase | ⚠️ blueprint(deep) |
| **refactor** | ✅ | ✅ test/build | ✅ refactoring/impact | ✅ tdd | ⚠️ execute(deep) | ✅ 语言/review-work |
| **review** | ✅ | ✅ diff/log | ✅ pr-review | ❌ | ❌ | ✅ gh-ops/review-work |
| **brainstorm** | ✅ | ❌ | ❌ | ✅ brainstorming | ✅ explore | ✅ council(deep) |
| **blueprint** | ✅ | ❌ | ✅ exploring | ✅ brainstorm/plans | ⚠️ project(deep) | ✅ blueprint(standard) |
| **research** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ deep-research |
| **graph** | ✅ | ✅ build/update | ✅ 全部 | ❌ | ❌ | ❌ |
| **update** | ✅ | ❌ | ⚠️ install | ⚠️ install | ⚠️ install | ⚠️ install |

### 排他路由规则表

| 场景 | 轻量路径 | 重量路径 | 判断标准 |
|------|---------|---------|---------|
| 需求澄清 | superpowers:brainstorming | gsd-explore | 技术设计 vs 产品方向 |
| 制定计划 | superpowers:writing-plans | gsd-plan-phase | ≤3 PR vs 多阶段 |
| 并行执行 | superpowers:subagent-driven | gsd-execute-phase | 临时任务 vs 阶段编排 |
| 调试方法论 | superpowers:systematic-debugging | gsd-debug | 单次 vs 跨上下文 |
| 代码审查 | code-review-graph:pr-review | gsd-code-review | PR 分析 vs 阶段审查 |
| 蓝图规划 | ecc:blueprint | gsd project | 代码 PR 项目 vs 里程碑工程 |

### Token 消耗总览

| 命令 | 低开销 | 中开销 | 高开销 |
|------|--------|--------|--------|
| quick | --fast (极低) | --standard (低) | - |
| fix | --fast (低) | --standard (中) | --deep (高) |
| feat | --fast (低) | --standard (中) | --deep (高) |
| branch | create/status/merge/abort (极低) | review (低) | - |
| plan | --fast (极低) | --standard (中) | --deep (中-高) |
| refactor | --fast (低) | --standard (中) | --deep (高) |
| review | --fast (低) | --standard (中) | --deep (高) |
| brainstorm | --fast (极低) | --standard (中) | --deep (中) |
| blueprint | - | --standard (高) | --deep (最高) |
| research | --quick (低) | --web (中) | --deep (高) |
| graph | status/watch (极低) | build/update/rebuild (中) | - |
| update | --check (低) | --full (低) | - |

### RTK 触发点速查

| 命令 | 何时调用 `rtk gain` |
|------|-------------------|
| quick (--standard) | 语言测试前 |
| fix | 复现/错误日志 → 测试 → 回归测试前 |
| feat | 测试/build 前 |
| branch | review diff 前 |
| refactor | 基线测试 → 每步验证 → 最终测试前 |
| review | diff/log 获取前 |
| graph | build/update 构建输出前 |

---

*基于 ECC + GSD + superpowers + code-review-graph + Caveman + RTK 深度调研*
*最后更新: 2026-05-03*
