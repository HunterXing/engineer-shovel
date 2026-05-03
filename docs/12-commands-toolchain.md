# Engineer Shovel 12 命令能力参考

> **⚠️ 重要**: 本文档描述底层工具在理想状态下可能的协作模式，是**能力参考指南**，非命令的实际执行规范。
> **各命令的权威定义以 `commands/tool-*.md` 为准。** 实际命令是轻量路由器——定义范围、升级路径和验证标准，不硬编码具体工具调用链。

Engineer Shovel 的 12 个 `/tool-*` 命令是轻量路由器。本文档按命令逐一介绍底层工具在不同场景下的可能协作模式。

---

## 底层工具总览

| 工具 | 角色 | 典型 token 消耗 |
|------|------|----------------|
| **caveman** | 沟通压缩层 (LLM 输出) | 降低 ~75% prompt 冗余 |
| **rtk** | 工具输出压缩层 (git/test/build 日志) | 噪声输出压缩 |
| **gsd** | 项目管理、阶段执行、调试、状态追踪 | 高 (subagent 并行) |
| **superpowers** | 结构化工作流 (TDD、brainstorm、planning) | 中-高 (多轮对话) |
| **ecc** | 语言特定命令、GitHub 操作、安全审查 | 低-中 |
| **code-review-graph** | 代码知识图谱、PR 审查、影响分析 | 中 |

---

## 核心设计: 成本模式路由

每个命令支持三种成本模式，调用的工具组合完全不同:

| 模式 | 何时用 | 典型工具 |
|------|--------|----------|
| `--fast` | 低风险、位置明确、小 diff | caveman lite + 直接编辑 |
| `--standard` | 常规开发 (默认) | caveman full + superpowers 结构化工作流 |
| `--deep` | 复杂、跨系统、高风险、安全敏感 | caveman full/ultra + gsd 重量级流程 |

**关键原则:** 默认选择能验证结果的最低成本路径，只有证据显示轻量路径不足时才升级。

---

## 1. /tool-quick — 简单编辑

> Typos, config edits, 1-2 file surgical changes | 默认成本: Low

> **定义文件**: `commands/tool-quick.md`

### 路由判断

```
改动范围?
├─ 1 文件, 逻辑完全明确    → --fast (默认)
├─ 1-2 文件, 需要确认      → --standard
└─ 不适用 tool-quick       → 转 /tool-feat 或 /tool-fix
```

### --fast (直接编辑)

```
caveman lite
  → 直接编辑文件
  → 快速验证 (语法检查 / 读取确认)
  → git commit
```

**调用工具:** caveman only
**不经过:** gsd, superpowers, ecc, code-review-graph, rtk

### --standard (需要确认)

```
caveman full
  → 编辑文件
  → 语言测试 (bun test / pytest / go test ...)
  → caveman review (压缩审查)
  → git commit
```

**调用工具:** caveman + ecc (语言测试)
**不经过:** gsd, superpowers, code-review-graph

### Token 消耗: 极低

---

## 2. /tool-fix — Bug 修复

> Bug reports, failing tests, regressions | 默认成本: Low → High by scope

> **定义文件**: `commands/tool-fix.md`

### 路由判断

```
Bug 范围?
├─ 单行/typo/明确位置     → --fast
├─ 单函数/需要调查        → --standard
└─ 跨文件/架构/安全漏洞   → --deep
```

### --fast (明确位置小修复)

```
caveman lite
  → 直接修复 (1-2 文件)
  → 语言测试
  → git commit
```

**调用工具:** caveman only
**不经过:** gsd, superpowers, ecc, code-review-graph, rtk

### --standard (需要调查的 Bug) ← 默认

```
caveman full
  → reproduce or identify failing assertion/log
  → inspect related code (可升级: /gsd-debug "$BUG_DESCRIPTION")
      ├─ 收集症状: expected/actual/error/timeline/repro
      ├─ 调查: 读错误 → 复现 → 检查近期变更
      ├─ 定位: 从小范围扩展到大范围
      └─ 输出: 根因分析
  → apply surgical fix (只修最小的 root cause)
  → /superpowers:tdd-workflow (可选: 回归测试)
  → 语言测试/building
  → regression coverage (if project has test pattern)
```

**可能调用的工具:** caveman + gsd (debug) + superpowers (systematic-debugging, tdd) + ecc (语言测试/构建, ai-regression-testing)
**不经过:** code-review-graph, review-work, security-review

### --deep (跨文件/架构问题)

```
caveman full/ultra
  → /gsd-debug (复杂场景)                         ← 先只诊断
      └─ 输出: 结构化 Root Cause Report
  → 用户确认诊断
  → 应用修复 (细分小步)
  → /superpowers:tdd-workflow
  → 语言测试
  → /security-review (if security-related)        ← ecc 安全审查
  → /review-work (if high-risk)                   ← ecc 重量级审查
```

**可能调用的工具:** caveman + gsd (debug) + superpowers (tdd) + ecc (语言命令, security-review, review-work)
**不经过:** code-review-graph

### 关键差异: --diagnose 模式

```bash
/tool-fix --diagnose "login 500"
# 只找根因, 不修复
# 输出结构化 Root Cause Report
# 用户确认后再决定修复方式
```

### Token 消耗分布

| 阶段 | 工具 | Token 消耗 | 备注 |
|------|------|-----------|------|
| 症状收集 | gsd-debug 问答 | 低 | 5 个问题 |
| 调查 | gsd-debugger subagent | **最高** | 读大量文件, 多假设验证 |
| 根因分析 | superpowers: systematic-debugging | 中 | 内嵌在 debugger 中 |
| 修复 | gsd-code-fixer | 中 | --deep 模式下独立 subagent |
| TDD | superpowers: tdd-workflow | 中 | 回归测试 |
| 验证 | ecc: 语言命令 + rtk | 低 | rtk 压缩输出 |

---

## 3. /tool-feat — 新功能

> New functionality | 默认成本: Medium

> **定义文件**: `commands/tool-feat.md`

### 路由判断

```
功能复杂度?
├─ ≤2 文件, 逻辑明确     → --fast
├─ 3-8 文件, 需求清晰     → --standard
└─ 多组件/有歧义/跨系统   → --deep
```

### --fast (低风险小功能)

```
caveman lite
  → 直接编辑 (1-2 文件)
  → 语言测试 (bun test / pytest / go test ...)
  → caveman review (压缩审查)
  → git commit
```

**调用工具:** caveman only
**不经过:** brainstorming, search-first, writing-plans, gsd, tdd-workflow

### --standard (常规功能开发) ← 默认

```
caveman full
  → /search-first "existing solutions for $FEATURE" ← 可选: npm/PyPI/GitHub/Context7
  → /superpowers:brainstorming                     ← 可选: 需求不明确时
      ├─ 逐一提问澄清需求
      ├─ 提出 2-3 个方案 + tradeoffs
      └─ 输出: 明确的设计方向
  → /superpowers:writing-plans                     ← 可选: 需要结构化计划时
      ├─ 文件结构映射
      ├─ TDD 任务分解
      └─ 输出: 计划文档
  → explore patterns → implement using conventions
  → /superpowers:tdd-workflow (可选)
  → 语言测试/构建
  → /tool-review --fast or default
```

**可能调用的工具:** caveman + superpowers (brainstorm, plans, tdd) + ecc (search-first, 语言命令)
**不经过:** gsd, code-review-graph, review-work

### --deep (复杂功能)

```
caveman full/ultra
  → /search-first
  → /superpowers:brainstorming
  → /superpowers:writing-plans
  → /tool-plan 或 /tool-blueprint              ← 升级到完整规划或 blueprint
  → 按 plan/blueprint 逐步实现
  → /superpowers:tdd-workflow
  → 语言测试/构建
  → /review-work (5 并行审查 agent)             ← ecc 重量级审查
  → /tool-branch review → merge
```

**调用工具:** caveman + superpowers (brainstorm, plans, tdd) + ecc (search-first, 语言命令, review-work)
**可能升级到:** gsd (执行阶段), code-review-graph (审查辅助)

### Token 消耗分布

| 阶段 | 工具 | Token 消耗 | 可压缩? |
|------|------|-----------|---------|
| 搜索 | ecc: search-first | 中 | caveman full |
| 头脑风暴 | superpowers: brainstorming | **高** | caveman full |
| 写计划 | superpowers: writing-plans | **高** | 不可压缩 |
| 执行 | gsd: execute-phase | **最高** | subagent 内 caveman |
| TDD | superpowers: tdd-workflow | 中 | caveman full |
| 验证 | ecc: 语言命令 + rtk | 低 | rtk 自动 |

---

## 4. /tool-branch — 分支工作流

> Branch workflow: create, review, merge, abort | 默认成本: Low

> **定义文件**: `commands/tool-branch.md`
> **实现**: 委托 `scripts/branch-workflow.sh` 执行

### 子命令

```
/tool-branch create feat/xxx   → 创建分支 (自动检测类型)
/tool-branch status            → 查看状态
/tool-branch review            → 审查 diff
/tool-branch merge             → squash 合并
/tool-branch abort             → 放弃分支
```

### 分支类型自动检测

根据 description 关键词自动判定类型:

| 关键词 | 分支类型 | 示例 |
|--------|---------|------|
| fix, bug, error, broken, crash, issue, problem | `fix` | `fix/null-pointer-error` |
| add, new, feature, implement, support, create | `feat` | `feat/add-login` |
| refactor, clean, optimize, improve, restructure | `refactor` | `refactor/clean-auth` |
| doc, readme, comment, typo, docs | `docs` | `docs/update-readme` |
| 默认 | `feat` | |

### create (创建分支)

```
caveman lite
  → bash scripts/branch-workflow.sh create "description"
  → 根据关键词自动检测 type → 生成 {type}/{slug} 分支名
  → 显示状态
```

### status (查看状态)

```
caveman lite
  → bash scripts/branch-workflow.sh status
  → 未提交变更、领先/落后远程、diff 统计
```

### review (审查分支 diff)

```
caveman full
  → bash scripts/branch-workflow.sh review
  → diff vs source 分支展示
  → 可选: code-review-graph: pr-review (知识图谱辅助)
  → 显示: 是否可以合并
```

### merge (合并分支)

```
caveman lite
  → bash scripts/branch-workflow.sh merge
  → squash merge → 提示 commit message → 删除分支
```

### abort (放弃分支)

```
caveman lite
  → bash scripts/branch-workflow.sh abort
  → 确认 → 切回 source 分支 → 删除 feature 分支
  → 有 uncommitted changes 时: auto-stash → 切换 → 恢复 stash
```

### 边界情况

- **未提交变更**: auto-stash before switch, restore on abort
- **同名分支存在**: error + 建议使用已有分支
- **不在 feature 分支**: merge/review/abort 需要当前在 feature 分支

---

## 5. /tool-plan — 需求和实现规划

> Requirements and implementation planning | 默认成本: Medium

> **定义文件**: `commands/tool-plan.md`

### 路由判断

```
需求清晰度?
├─ 明确, 想快速记录       → --fast
├─ 需要探索方向           → --standard
└─ 多方案/多阶段/需评审   → --deep
```

### --fast (快速捕获想法)

```
caveman lite
  → /gsd-note "capture: $IDEA_DESCRIPTION"
  → 简短选项列表
  → 路由到 /tool-feat 或 backlog
```

**调用工具:** caveman + gsd (note)
**不经过:** brainstorming, writing-plans, explore

### --standard (需要规划方向) ← 默认

```
caveman full
  → /gsd-explore (可选: 想法不清晰时)
      ├─ 苏格拉底式提问 → 澄清需求
      └─ 输出: 明确的需求描述
  → /superpowers:brainstorming (可选)
      ├─ 2-3 方案 + tradeoffs
      └─ 终态: 调用 writing-plans
  → /superpowers:writing-plans (可选)
      ├─ 文件结构映射 + 任务分解
      └─ 输出: 计划文档
  → /plan 或 /prp-plan (结构化计划 + verification criteria)
  → 路由到执行:
      ├─ 简单: /tool-quick 或 /tool-feat
      ├─ 中等: /tool-feat (跳过 plan 阶段)
      └─ 暂存: 暂停/backlog
```

**可能调用的工具:** caveman + gsd (explore) + superpowers (brainstorm, plans, /plan, /prp-plan)
**不经过:** gsd (plan-phase, review)

### --deep (多方案/多阶段项目)

```
caveman full
  → /gsd-explore
  → /superpowers:brainstorming
  → /superpowers:writing-plans
  → /gsd-plan-phase                               ← gsd 重量级规划
      ├─ 验证阶段号
      ├─ 研究领域 (spawn gsd-phase-researcher)
      │   └─ 输出: RESEARCH.md
      ├─ 生成 PLAN.md (spawn gsd-planner)
      ├─ 验证循环 (spawn gsd-plan-checker)
      │   ├─ 目标回溯分析
      │   └─ 不通过 → 重新规划 (max 3 轮)
      └─ 输出: .planning/phases/N/PLAN.md
  → /gsd-review (可选)                             ← gsd 跨 AI 评审
      └─ 外部 AI CLI 评审 PLAN.md → REVIEWS.md
  → /tool-plan --reviews (如有评审反馈)
  → 路由到执行
      └─ /gsd-execute-phase 或 /tool-feat --deep
```

**调用工具:** caveman + gsd (explore, plan-phase, review) + superpowers (brainstorm, plans)
**不经过:** ecc, code-review-graph

### /tool-plan 与 /tool-feat 的关系

```
/tool-plan 是 /tool-feat 的前半段 (规划子集)

/tool-feat = plan + execute + verify + commit
/tool-plan = 只到计划, 不执行

典型用法:
  /tool-plan → 用户审查计划 → 确认后 → /tool-feat 或 /gsd-execute-phase
```

### Token 消耗分布

| 阶段 | 工具 | Token 消耗 | 备注 |
|------|------|-----------|------|
| 探索 | gsd: gsd-explore | 中 | --standard 起步 |
| 头脑风暴 | superpowers: brainstorming | **高** | 多轮对话 |
| 写计划 | superpowers: writing-plans | **高** | 完整代码块 |
| GSD 规划 | gsd: gsd-plan-phase | 中 | --deep 模式, 含研究 + 验证循环 |
| 评审 | gsd: gsd-review | 中 | --deep 模式, 可选 |

---

## 6. /tool-refactor — 重构

> Behavior-preserving cleanup | 默认成本: Medium

> **定义文件**: `commands/tool-refactor.md`

### 路由判断

```
重构范围?
├─ 单文件内提取/重命名    → --fast
├─ 跨文件但逻辑清晰       → --standard
└─ 架构级重构             → --deep
```

### --fast (单文件重构)

```
caveman lite
  → 语言 LSP 重构 (rename / extract / move)
  → 语言测试 (确认行为不变)
  → git commit
```

**调用工具:** caveman + ecc (语言测试)
**不经过:** gsd, superpowers, code-review-graph

### --standard (跨文件重构) ← 默认

```
caveman full
  → 运行现有测试 (建立基线, 全绿才继续)
  → 执行重构 (小步, 每次一个逻辑单元)
  → /superpowers:tdd-workflow (可选: 每步验证)
  → 语言测试/构建
  → /tool-review --fast or default
```

**可能调用的工具:** caveman + superpowers (tdd) + ecc (语言测试)
**不经过:** gsd, code-review-graph

### --deep (架构级重构)

```
caveman full/ultra
  → 运行现有测试 (基线)
  → /superpowers:writing-plans (可选: 分阶段重构计划)
  → 逐步执行, 每阶段独立可验证
  → /superpowers:tdd-workflow
  → 语言测试/构建
  → /refactor + /review-work (深度审查)
  → /e2e-testing (if applicable)
```

**可能调用的工具:** caveman + superpowers (plans, tdd) + gsd (execute-phase, 可选) + ecc (语言测试, review-work, e2e)
**不经过:** code-review-graph

### 停止条件 (参考 `commands/tool-refactor.md`)

- 基线测试失败 → 先 `/tool-fix`
- 行为变更 → 拆分到 `/tool-feat`
- 性能不降 → 对比基准性能

### 重构核心原则

```
1. 不改行为 → 测试是安全网, 先确保测试全绿
2. 小步提交 → 每次重构一个逻辑单元, 原子提交
3. 不混入新功能 → refactor + feature 分开提交
4. 审查必须有 → 重构容易引入隐蔽 bug
```

### Token 消耗分布

| 阶段 | 工具 | Token 消耗 | 备注 |
|------|------|-----------|------|
| 基线测试 | ecc: 语言测试 | 低 | 确认全绿 |
| 重构执行 | 直接编辑 | 中 | 小步进行 |
| TDD 验证 | superpowers: tdd-workflow | 中 | 每步验证 |
| 计划 | superpowers: writing-plans | 中 | --deep 模式 |
| 阶段执行 | gsd: execute-phase | **最高** | --deep 模式 |
| 审查 | ecc: review-work | 中 | --deep 模式 |

---

## 7. /tool-review — 代码审查

> Local diff, PR, or post-implementation review | 默认成本: Low → High by mode

> **定义文件**: `commands/tool-review.md`

### 模式选择

```
审查什么?
├─ 本地未提交变更 (< 10 文件)    → --fast
├─ GitHub PR                     → --standard (default)
├─ 重大实现 (完成后)             → --deep
└─ 快速检查                      → --fast + caveman-review
```

### --fast (快速审查)

```
caveman full
  → git diff (staged/unstaged)
  → /caveman:caveman-review                      ← 压缩审查
      └─ 每个 finding 一行: path:line: emoji severity: problem. fix.
  → 输出: 问题列表 + 建议
```

**调用工具:** caveman (caveman-review)
**不经过:** gsd, superpowers, code-review-graph, ecc

### --standard (PR 审查) ← 默认

```
caveman full
  → gh pr view <url>                              ← 获取 PR 信息 (if PR)
  → git diff (if local diff)
  → /code-review 或 /review-pr $ARGUMENTS          ← 结构化审查
      ├─ 分析变更影响范围
      ├─ 检查依赖关系
      ├─ 识别潜在风险
      └─ 输出: 结构化审查报告
  → /caveman:caveman-review (可选)                ← 压缩输出
  → 输出: 审查意见 + 合并建议
```

**可能调用的工具:** caveman + code-review-graph (pr-review, exploring) + ecc (github-ops)
**不经过:** gsd, superpowers

### --deep (深度审查)

```
caveman full/ultra
  → /review-work                                  ← 5 并行审查 agent
      ├─ agent1: 目标/约束检查 (Oracle)
      ├─ agent2: 代码质量 (Oracle)
      ├─ agent3: 安全审计 (Oracle)
      ├─ agent4: 实操 QA
      └─ agent5: 上下文挖掘
  → code-review-graph: pr-review + exploring (可选) ← 知识图谱辅助
  → /security-review (if security-sensitive)
  → /caveman:caveman-review (可选)
  → 输出: 全面审查报告 + 行动项
```

**可能调用的工具:** caveman + ecc (review-work, security-review) + code-review-graph (pr-review, exploring)
**不经过:** gsd, superpowers

### Token 消耗分布

| 阶段 | 工具 | Token 消耗 | 备注 |
|------|------|-----------|------|
| PR 信息 | ecc: github-ops | 低 | gh pr view |
| 图谱分析 | code-review-graph | 中 | --standard 起步 |
| 压缩审查 | caveman-review | 低 | 已压缩 |
| 5-agent 审查 | ecc: review-work | **最高** | --deep 模式 |
| 安全审查 | ecc: security-review | 中 | --deep + security |

---

## 8. /tool-brainstorm — 头脑风暴

> Explore unclear ideas before building | 默认成本: Low → Medium

> **定义文件**: `commands/tool-brainstorm.md`

### 路由判断

```
想法清晰度?
├─ 有模糊想法, 需要记录    → --fast
├─ 需要探索方向和方案      → --standard
└─ 多方案需要决策          → --deep
```

### --fast (快速记录想法)

```
caveman lite
  → /gsd-note "capture: $IDEA"
  → 简短描述 + 可能方向
  → 路由到 backlog
```

**调用工具:** caveman + gsd (note)
**Token:** 极低

### --standard (探索性头脑风暴) ← 默认

```
caveman full
  → /gsd-explore "$IDEA"
      ├─ 苏格拉底式提问
      ├─ 探索想法边界
      ├─ 识别假设和约束
      └─ 输出: 澄清后的需求描述
  → /superpowers:brainstorming
      ├─ 探索项目上下文
      ├─ 逐一提问 (一次一个)
      ├─ 提出 2-3 个方案 + tradeoffs
      ├─ 呈现设计 → 用户批准
      ├─ 写 spec → 自检 → 用户审查
      └─ 终态: 调用 writing-plans
  → 路由到 /tool-plan 或 /tool-feat
```

**调用工具:** caveman + gsd (explore) + superpowers (brainstorming)
**不经过:** gsd-plan-phase, ecc, code-review-graph

### --deep (多方案决策)

```
caveman full
  → /gsd-explore
  → /superpowers:brainstorming
  → /council                                      ← 4-voice 决策
      ├─ 4 个角色: 工程师/产品/安全/反对派
      ├─ 结构化辩论
      └─ 输出: 推荐方案 + 理由
  → /deep-research (if needed)                    ← 外部研究
  → 写 spec → 用户审查
  → 路由到 /tool-plan
```

**调用工具:** caveman + gsd (explore) + superpowers (brainstorming) + ecc (council, deep-research)
**不经过:** gsd-plan-phase, code-review-graph

### Token 消耗分布

| 阶段 | 工具 | Token 消耗 | 备注 |
|------|------|-----------|------|
| 捕获 | gsd: note | 极低 | --fast |
| 探索 | gsd: explore | 中 | --standard 起步 |
| 头脑风暴 | superpowers: brainstorming | **高** | 多轮对话 |
| 决策 | ecc: council | 中 | --deep 模式 |
| 研究 | ecc: deep-research | 中 | --deep 模式, 可选 |

---

## 9. /tool-blueprint — 多步骤项目

> Multi-step, multi-session projects | 默认成本: High

> **定义文件**: `commands/tool-blueprint.md`

### 路由判断

```
项目规模?
├─ 单 PR 可完成       → 不用 blueprint, 转 /tool-feat
├─ 2-3 PR, 线性       → --standard
└─ 多 PR, 有依赖/并行 → --deep
```

### --standard (多 PR 线性项目)

```
caveman full
  → /superpowers:brainstorming                    ← 需求澄清
  → /superpowers:writing-plans                    ← 整体计划
  → /blueprint $PROJECT "$OBJECTIVE"
      ├─ Research: 读项目结构、现有计划、记忆文件
      ├─ Design: 拆分为 3-12 个 PR-sized step
      │   ├─ 依赖边
      │   ├─ 并行/串行排序
      │   ├─ 模型层级 (strongest vs default)
      │   └─ 回滚策略 per step
      ├─ Draft: 写 plans/$PROJECT-xxx.md
      │   └─ 每 step: 上下文简报 + 任务清单 + 验证命令 + 退出标准
      ├─ Review: 最强模型 adversarial 审查
      │   └─ 完整性 / 依赖正确性 / 反模式检测
      └─ Register: 保存计划 + 更新记忆索引
  → 逐步执行 (每步用 /tool-feat 或 /tool-quick)
```

**调用工具:** caveman + superpowers (brainstorm, plans) + ecc (blueprint)
**不经过:** gsd

### --deep (多 PR 复杂依赖项目)

```
caveman full/ultra
  → /superpowers:brainstorming
  → /superpowers:writing-plans
  → /blueprint $PROJECT "$OBJECTIVE"
  → GSD project → discuss/plan/execute phases     ← gsd 介入
      ├─ 初始化 .planning/ 目录
      ├─ 逐阶段规划 + 执行
      ├─ UAT 验证
      └─ PR + merge + milestone summary
```

**可能调用的工具:** caveman + superpowers (brainstorm, plans) + ecc (blueprint) + gsd (new-project, plan-phase, execute-phase, verify-work, pr-branch, ship, milestone-summary)
**不经过:** code-review-graph

### Token 消耗: 最高

| 阶段 | 工具 | Token 消耗 | 备注 |
|------|------|-----------|------|
| 头脑风暴 | superpowers: brainstorming | **高** | 多轮对话 |
| 计划 | superpowers: writing-plans + blueprint | **高** | 完整代码 + 多 step |
| 项目管理 | gsd: 全阶段 | **最高** | 多 subagent 并行 |
| 执行 | gsd: execute-phase | **最高** | 波次并行 |
| 验证 | gsd: verify-work | 中 | UAT |

---

## 10. /tool-research — 技术研究

> Current-state technical research | 默认成本: Low → High by mode

> **定义文件**: `commands/tool-research.md`

### 模式说明

实际命令使用 `--quick` / `--web` / `--deep` 三种模式 (非标准 `--fast` / `--standard`):

```
研究深度?
├─ 快速查证 (本地文档/已知库) → --quick (默认)
├─ 需要当前事实/官方文档     → --web
└─ 战略决策/多源深度研究     → --deep
```

### --quick (快速查证) ← 默认

```
搜本地文档、已知库文档 → 简要总结 + 引用来源
路由到 /tool-plan、/tool-feat、/tool-quick 或文档
```

**可能调用的工具:** web search, context7 库文档 (搜索已知库)
**不经过:** gsd, superpowers, code-review-graph
**Token:** 低

### --web (当前事实/官方文档)

```
web/docs 搜索 + 简洁综合
→ 评估候选方案: 功能性 / 维护性 / 社区 / 文档 / 许可证
→ 结构化对比表 + 推荐
→ 路由到 /tool-plan 或 /tool-feat
```

**可能调用的工具:** web search, context7, GitHub code search
**不经过:** gsd, superpowers, code-review-graph
**Token:** 中

### --deep (多源深度研究)

```
多源搜索 → 全文阅读 → 综合报告:
  ├─ Executive Summary
  ├─ 主题分析 (带引用)
  ├─ Key Takeaways
  ├─ 冲突标注和置信度
  └─ 来源列表 (cite or name sources)
→ 路由到 /tool-plan、/tool-feat、/tool-quick 或文档
→ 可选: /council (冲突推荐时)
```

**可能调用的工具:** /deep-research (firecrawl + exa MCP), /council
**不经过:** gsd, superpowers, code-review-graph
**Token:** 高

### Token 消耗分布

| 阶段 | 工具 | Token 消耗 | 备注 |
|------|------|-----------|------|
| 快速搜索 | web search | 低 | --quick |
| 库文档 | context7 | 低 | --web |
| 深度搜索 | firecrawl + exa | **高** | --deep, 多源 |
| 深度阅读 | firecrawl_scrape | **高** | 全文抓取 |
| 综合报告 | LLM 生成 | 中 | --deep |
| 决策 | council | 中 | 可选 |

---

## 11. /tool-graph — 知识图谱操作

> code-review-graph status, full build, incremental update, rebuild, watch | 默认成本: Low

> **定义文件**: `commands/tool-graph.md`

### 子命令

```
/tool-graph status      → 查看图谱状态
/tool-graph build       → 全量构建图谱
/tool-graph update      → 增量更新
/tool-graph rebuild     → 重建 (清空 + 全量)
/tool-graph watch       → 监听变更自动更新
```

### status (查看状态)

```
caveman lite
  → 读取 .code-review-graph/ 目录
  → 显示: 节点数、边数、最后更新时间、覆盖范围
```

**调用工具:** caveman + code-review-graph (只读)
**Token:** 极低

### build (全量构建)

```
caveman full
  → code-review-graph: full build
      ├─ 扫描全部源文件
      ├─ AST 解析 → 节点 (函数/类/模块)
      ├─ 依赖分析 → 边 (调用/导入/继承)
      ├─ 写入 .code-review-graph/ 目录
      └─ 输出: 统计信息
  → rtk 压缩构建输出
```

**调用工具:** caveman + code-review-graph (build) + rtk (可选)
**Token:** 中 (取决于代码库大小)

### update (增量更新)

```
caveman full
  → git diff --name-only (自上次更新)
  → code-review-graph: incremental update
      ├─ 只解析变更文件
      ├─ 更新受影响的节点和边
      └─ 输出: 变更统计
```

**调用工具:** caveman + code-review-graph (update) + rtk (可选)
**Token:** 低

### rebuild (重建)

```
caveman full
  → 清空 .code-review-graph/ 目录
  → code-review-graph: full build
  → 同 build 流程
```

**调用工具:** caveman + code-review-graph (build) + rtk (可选)
**Token:** 中

### watch (监听)

```
caveman lite
  → 启动文件监听器
  → 文件变更时自动 incremental update
  → 后台运行
```

**调用工具:** caveman + code-review-graph (watch)
**Token:** 低 (后台)

---

## 12. /tool-update — 同步更新

> Sync and update installation | 默认成本: Low

> **定义文件**: `commands/tool-update.md`

### 模式说明

实际命令使用 `--check` / `--full` 模式，支持 `--target opencode|claude|both`:

```
/tool-update --check                 ← 只读比较+检查
/tool-update --full                  ← 全量更新
/tool-update --full --target claude  ← 指定目标
```

### --check (只读检查) ← 默认

```
检测已安装位置 (基于 --target)
  → 本地文件与 repo 最新版比较
  → 报告: 缺失 / 过期 / 多余的 files
  → 检查 base tools: git, python3, pipx, node, npx, opencode, claude
  → 检查 Full-mode 组件: code-review-graph, GSD, superpowers, Caveman, RTK, ECC
  → 安全检查: MCP 策略 (不自动启用需凭证的服务)、备份 JSON config、不启动后台进程
  → 显示: 检查摘要
```

### --full (全量更新 + 修复)

```
--check 全部步骤
  → 覆盖已安装 files 为最新版
  → 安装/配置缺失的低风险组件 (使用官方 installer)
  → code-review-graph: 可能配置 MCP/rules (上游支持)
  → superpowers: 作为 plugin/skills provider 配置 (无独立 MCP 步骤)
  → ECC: 不自动启用 bundled MCP (可能需凭证或重复)
  → 更新后验证安装完整性
```

**调用工具:** 自定义文件同步逻辑 + 组件官方 installer
**Token:** 低

---

## 全量对比矩阵

### 12 命令 × 成本模式 × 工具调用

| 命令 | --fast | --standard | --deep |
|------|--------|-----------|--------|
| **quick** | caveman | caveman + ecc(测试/构建) | N/A (转 feat/fix) |
| **fix** | caveman + ecc(测试) | caveman + gsd(debug, 可选) + superpowers(sysdbg,tdd, 可选) + ecc(测试) | + ecc(security,review-work, 可选) |
| **feat** | caveman + ecc(测试) | caveman + superpowers(brainstorm,plans,tdd, 可选) + ecc(search,测试) | + gsd(execute-phase, 可选) + ecc(review-work) |
| **branch** | caveman + scripts/branch-workflow.sh | caveman + scripts/branch-workflow.sh + code-review-graph(可选) | N/A |
| **plan** | caveman (inline plan) | caveman + gsd(explore,可选) + superpowers(/plan, /prp-plan) | + gsd(plan-phase, review, 可选) + /blueprint |
| **refactor** | caveman + ecc(测试) | caveman + superpowers(tdd, 可选) + ecc(测试) | + superpowers(plans, 可选) + gsd(execute-phase, 可选) + ecc(review-work,e2e) |
| **review** | caveman(caveman-review) | caveman + /code-review or /review-pr + ecc(github-ops) + code-review-graph(可选) | + ecc(review-work,security-review) |
| **brainstorm** | caveman + gsd(note) | caveman + gsd(explore) + superpowers(brainstorming, 可选) | + ecc(council) |
| **blueprint** | N/A (转 feat) | caveman + superpowers(brainstorm,plans, 可选) + ecc(blueprint) | + gsd(project, phases, verify, ship) |
| **research** (--quick/--web/--deep) | caveman + web-search | + context7 + GitHub-search | + /deep-research(firecrawl,exa) + council(可选) |
| **graph** | caveman + code-review-graph(只读) | caveman + code-review-graph(build/update) | N/A |
| **update** (--check/--full) | caveman + 自定义文件同步 | caveman + 组件 installer + health checks | N/A |

### 按工具的触发条件 (12 命令)

工具调用是**场景驱动的可选组合**，命令只定义范围和升级路径，不硬编码工具链路:

| 工具 | 典型触发场景 (非必须) |
|------|----------------------|
| **caveman lite** | quick(--fast), fix(--fast), feat(--fast), branch(create/status/merge/abort), plan(--fast), refactor(--fast), review(--fast), brainstorm(--fast), research(--quick), graph(status/watch), update(--check/--full) |
| **caveman full** | quick(--standard), fix(--standard), feat(--standard), branch(review), plan(--standard), refactor(--standard), review(--standard), brainstorm(--standard), blueprint(--standard), research(--web), graph(build/update/rebuild) |
| **caveman ultra** | fix(--deep), feat(--deep), refactor(--deep), review(--deep), brainstorm(--deep), blueprint(--deep), research(--deep) |
| **rtk** | git/test/build 噪声输出时启用 (按需, 非必须) |
| **superpowers: brainstorming** | feat(需求不明确), plan(需要方向时), brainstorm(--standard), blueprint(需求澄清) |
| **superpowers: writing-plans** | feat(需要结构化计划), plan(需要计划文档), brainstorm(终态路由), blueprint(整体计划), refactor(--deep, 分阶段) |
| **superpowers: tdd-workflow** | fix(需要回归), feat(常规开发), refactor(每步验证) |
| **superpowers: systematic-debugging** | fix(chained with gsd-debug) |
| **superpowers: search-first** | feat(常规开发) |
| **gsd: note** | plan(--fast), brainstorm(--fast) |
| **gsd: explore** | plan(想法不清晰时), brainstorm(--standard) |
| **gsd: debug** | fix(复杂 bug 调查) |
| **gsd: plan-phase** | plan(--deep), blueprint(--deep) |
| **gsd: execute-phase** | feat(--deep, 可选), refactor(--deep, 可选), blueprint(--deep) |
| **gsd: verify/ship** | blueprint(--deep) |
| **ecc: 语言测试/构建** | quick(--standard), fix(全部), feat(全部), refactor(全部) |
| **ecc: review-work** | fix(--deep, 可选), feat(--deep), refactor(--deep), review(--deep) |
| **ecc: security-review** | fix(安全相关), review(安全敏感) |
| **ecc: blueprint** | blueprint(--standard+) |
| **ecc: council** | brainstorm(--deep), research(--deep, 可选) |
| **ecc: deep-research** | research(--deep) |
| **ecc: github-ops** | branch(merge via gh pr create), review(--standard+) |
| **code-review-graph** | branch(review, 可选), review(--standard+, 辅助), graph(全部) |

### Token 消耗总览

| 命令 | 低开销 | 中开销 | 高开销 |
|------|--------|--------|--------|
| quick | `--fast` (极低) | `--standard` (低) | - |
| fix | `--fast` (低) | `--standard` (中) | `--deep` (高) |
| feat | `--fast` (低) | `--standard` (中-高) | `--deep` (最高) |
| branch | create/status/merge/abort (极低) | review (低) | - |
| plan | `--fast` (极低) | `--standard` (中) | `--deep` (中-高) |
| refactor | `--fast` (低) | `--standard` (中) | `--deep` (高) |
| review | `--fast` (低) | `--standard` (中) | `--deep` (高) |
| brainstorm | `--fast` (极低) | `--standard` (中) | `--deep` (中) |
| blueprint | - | `--standard` (高) | `--deep` (最高) |
| research | `--quick` (低) | `--web` (中) | `--deep` (高) |
| graph | status/watch (极低) | build/update/rebuild (中) | - |
| update | `--check` (低) | `--full` (低) | - |

---

## 最大化利用建议

### 1. 从最低成本开始, 按需升级

```
不确定复杂度? 先试最低成本模式
  → 够用? 完成
  → 不够? 升级到标准模式
  → 还不够? 升级到深度模式
```

> 注意: `/tool-research` 用 `--quick`/`--web`/`--deep`; `/tool-update` 用 `--check`/`--full`; 其余命令用 `--fast`/`--standard`/`--deep`.

### 2. caveman 建议使用

caveman 压缩可以按场景选用:
- 小范围改动 `--fast` 可用 `lite` (保持可读性)
- 常规开发 `--standard` 可用 `full` (平衡压缩和可读)
- 长上下文/多 agent 时可用 `ultra`

### 3. rtk 按需启用

只在有噪声输出时启用 (git log/diff 长、测试日志多、构建输出冗长)。

### 4. code-review-graph 的使用场景

code-review-graph 主要在这些场景中有用:
- `/tool-review --standard+` — PR 审查辅助
- `/tool-branch review` — 分支 diff 分析
- `/tool-graph` — 专门操作知识图谱

其他命令可通过 `/tool-graph build` 预构建图谱, 让后续 review 命令获得更好的上下文。

### 5. gsd 的调用场景

gsd 重量级流程的场景 (非硬编码):
- `--fast` 模式: 通常不调用 gsd (note 除外)
- `--standard` 模式: 可能调用轻量 gsd (explore, debug, note)
- `--deep` 模式: 可能调用重量级 gsd (execute-phase, plan-phase 等)

### 6. superpowers 的使用场景

superpowers 提供结构化工作流 (`brainstorming`, `writing-plans`, `tdd-workflow`), 在需求不明确或需要计划时有用。具体是否调用取决于场景, 非强制。

### 7. 命令间路由

```
/tool-brainstorm → 明确后 → /tool-plan 或 /tool-feat
/tool-plan → 审查后 → /tool-feat 或 GSD 执行
/tool-research → 决策后 → /tool-plan 或 /tool-feat
/tool-blueprint → 逐步 → /tool-feat 或 /tool-quick (per step)
/tool-fix --deep → 确认后 → /tool-fix (修复) 或 /tool-refactor (重构)
```

---

*基于 Engineer Shovel SKILL.md + optimal-workflow + superpowers/gsd/ecc/code-review-graph 各 skill 定义*
*最后更新: 2026-05-03*
