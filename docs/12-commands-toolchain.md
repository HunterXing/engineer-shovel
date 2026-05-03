# Engineer Shovel 12 命令完整工具链分析

Engineer Shovel 的 12 个 `/tool-*` 命令是轻量路由器，每个命令在不同成本模式 (`--fast` / `--standard` / `--deep`) 下调用完全不同的底层工具组合。本文档逐一分析每个命令的完整调用链。

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
  → /gsd-debug "$BUG_DESCRIPTION"
      ├─ 收集症状 (5 问: expected/actual/error/timeline/repro)
      ├─ 创建 .planning/debug/{slug}.md
      ├─ spawn gsd-debug-session-manager
      │   └─ spawn gsd-debugger (新 subagent, 独立 200k context)
      │       ├─ 读错误信息 → 复现 → 检查近期变更
      │       ├─ 多组件诊断: 层层日志定位
      │       ├─ 数据流追踪: 从 bad value 往回追
      │       └─ 输出: ROOT CAUSE FOUND
      └─ specialist_dispatch: 匹配专家 skill
  → 直接修复 或 spawn gsd-code-fixer
  → /superpowers:tdd-workflow
      └─ 回归测试: 先写复现 bug 的失败测试 → RED → GREEN → REFACTOR
  → 语言测试
  → /ai-regression-testing (自动生成回归检查)
  → git commit
```

**调用工具:** caveman + gsd (debug) + superpowers (systematic-debugging 内嵌, tdd) + ecc (语言测试, regression)
**不经过:** code-review-graph, review-work, security-review

### --deep (跨文件/架构问题)

```
caveman full/ultra
  → /gsd-debug --diagnose                        ← 先只诊断
      └─ 输出: 结构化 Root Cause Report
  → 用户确认诊断
  → /gsd-code-fixer                              ← gsd 自动修复
      └─ 读源文件 → 应用修复 → 原子提交
  → /superpowers:tdd-workflow
  → 语言测试
  → /security-review (if security-related)        ← ecc 安全审查
      └─ → /security-scan → fix → re-review
  → /review-work (5 并行审查 agent)               ← ecc 重量级审查
  → git commit
```

**调用工具:** caveman + gsd (debug, code-fixer) + superpowers (systematic-debugging, tdd) + ecc (语言命令, security-review, security-scan, review-work)
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
  → /search-first "existing solutions for $FEATURE"
      ├─ npm/PyPI 搜索
      ├─ MCP server 检查
      ├─ GitHub code search
      └─ 输出: Adopt / Extend / Build 决策
  → /superpowers:brainstorming
      ├─ 探索项目上下文
      ├─ 逐一提问澄清需求
      ├─ 提出 2-3 个方案 + tradeoffs
      ├─ 呈现设计 → 用户批准
      ├─ 写 spec → 自检 → 用户审查
      └─ 终态: 调用 writing-plans ↓
  → /superpowers:writing-plans
      ├─ 文件结构映射
      ├─ TDD 任务分解 (每个 step 2-5 分钟)
      ├─ 无占位符, 完整代码
      └─ 输出: docs/superpowers/plans/xxx.md
  → /superpowers:tdd-workflow
      ├─ RED: 写失败测试 → 运行确认失败 → commit
      ├─ GREEN: 最小实现 → 运行确认通过 → commit
      └─ REFACTOR: 清理 → 测试仍绿 → commit
  → 语言测试/构建
  → 本地审查 (caveman review)
  → git commit
```

**调用工具:** caveman + superpowers (brainstorm, plans, tdd) + ecc (search-first, 语言命令)
**不经过:** gsd, code-review-graph, review-work

### --deep (复杂功能)

```
caveman full/ultra
  → /search-first
  → /superpowers:brainstorming
  → /superpowers:writing-plans
  → /gsd-execute-phase                          ← gsd 介入
      ├─ 波次并行执行 (wave-based)
      ├─ 每个 plan → 独立 subagent
      ├─ 原子提交 per task
      └─ 状态追踪
  → /superpowers:tdd-workflow
  → 语言测试/构建
  → /review-work (5 并行审查 agent)             ← ecc 重量级审查
  → git commit
  → /tool-branch review → merge
```

**调用工具:** caveman + superpowers (brainstorm, plans, tdd) + gsd (execute-phase) + ecc (search-first, 语言命令, review-work)
**不经过:** code-review-graph

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

### 子命令

```
/tool-branch create feat/xxx   → 创建分支
/tool-branch status            → 查看状态
/tool-branch review            → 审查 diff
/tool-branch merge             → 合并
/tool-branch abort             → 放弃分支
```

### create (创建分支)

```
caveman lite
  → git checkout -b feat/xxx
  → 显示分支状态
```

**调用工具:** caveman + ecc (github-ops)
**Token:** 极低

### status (查看状态)

```
caveman lite
  → git status + git log --oneline
  → 显示: 未提交变更、领先/落后远程、分支 diff 统计
```

**调用工具:** caveman only
**Token:** 极低

### review (审查分支 diff)

```
caveman full
  → git diff main...HEAD
  → /caveman:caveman-review                      ← 压缩审查
      └─ 每个 finding 一行: path:line: problem. fix.
  → (可选) code-review-graph: pr-review          ← 深度审查
      └─ 知识图谱分析变更影响
  → 显示: 是否可以合并
```

**调用工具:** caveman (caveman-review) + code-review-graph (可选)
**Token:** 低-中

### merge (合并分支)

```
caveman lite
  → 确认: 有未提交变更? 测试通过?
  → git merge 或 gh pr create
  → 显示合并结果
```

**调用工具:** caveman + ecc (github-ops)
**Token:** 极低

### abort (放弃分支)

```
caveman lite
  → 确认: 真的放弃? 有未推送提交?
  → git checkout main && git branch -D feat/xxx
```

**调用工具:** caveman only
**Token:** 极低

---

## 5. /tool-plan — 需求和实现规划

> Requirements and implementation planning | 默认成本: Medium

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
  → /gsd-explore "I have an idea: $IDEA"
      ├─ 苏格拉底式提问
      ├─ 探索想法 → 澄清需求
      └─ 输出: 明确的需求描述
  → /superpowers:brainstorming
      ├─ 项目上下文探索
      ├─ 多轮提问 (一次一个)
      ├─ 2-3 方案 + tradeoffs
      ├─ 设计分节呈现 → 用户批准
      ├─ 写 spec → 自检 → 用户审查
      └─ 终态: 调用 writing-plans ↓
  → /superpowers:writing-plans
      ├─ 文件结构映射
      ├─ TDD 任务分解 (每个 step 2-5 分钟)
      ├─ 完整代码, 无占位符
      └─ 输出: docs/superpowers/plans/xxx.md
  → 路由到执行
      ├─ 简单: /gsd-fast
      ├─ 中等: /tool-feat (跳过 plan 阶段)
      └─ 暂存: /gsd-pause-work
```

**调用工具:** caveman + gsd (explore) + superpowers (brainstorm, plans)
**不经过:** gsd-plan-phase, gsd-review

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
  → /superpowers:tdd-workflow
      └─ 每步后运行测试, 确认行为不变
  → 语言测试/构建
  → /caveman:caveman-review                      ← 压缩审查
  → git commit (每步原子提交)
```

**调用工具:** caveman + superpowers (tdd) + ecc (语言测试)
**不经过:** gsd, code-review-graph

### --deep (架构级重构)

```
caveman full/ultra
  → 运行现有测试 (基线)
  → /superpowers:writing-plans                    ← 重构计划
      └─ 分阶段重构, 每阶段独立可验证
  → /gsd-execute-phase                            ← gsd 阶段执行
      └─ 波次并行, 每阶段测试 → commit
  → /superpowers:tdd-workflow
  → 语言测试/构建
  → /review-work (5 并行审查 agent)               ← 深度审查
      ├─ 目标/约束验证 (行为不变)
      ├─ 代码质量
      ├─ 安全审计
      ├─ 实操 QA
      └─ 上下文挖掘
  → /e2e-testing (if applicable)                  ← E2E 回归
  → git commit
```

**调用工具:** caveman + superpowers (plans, tdd) + gsd (execute-phase) + ecc (语言测试, review-work, e2e)
**不经过:** code-review-graph

### 重构核心原则

```
1. 不改行为 → 测试是安全网, 先确保测试全绿
2. 小步提交 → 每次重构一个逻辑单元, 原子提交
3. 不混入新功能 → refactor + feature 分开提交
4. 性能不降 → 重构后对比基准性能
5. 审查必须有 → 重构容易引入隐蔽 bug
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
  → gh pr view <url>                              ← 获取 PR 信息
  → code-review-graph: pr-review                  ← 知识图谱分析
      ├─ 分析变更影响范围
      ├─ 检查依赖关系
      ├─ 识别潜在风险
      └─ 输出: 结构化审查报告
  → code-review-graph: exploring                  ← 代码探索
      ├─ 追踪调用链
      ├─ 理解上下文
      └─ 识别遗漏测试
  → /caveman:caveman-review                      ← 压缩输出
  → 输出: 审查意见 + 合并建议
```

**调用工具:** caveman + code-review-graph (pr-review, exploring) + ecc (github-ops)
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
  → code-review-graph: pr-review + exploring      ← 知识图谱辅助
  → /security-review (if security-sensitive)      ← 安全审查
  → /caveman:caveman-review                      ← 压缩汇总
  → 输出: 全面审查报告 + 行动项
```

**调用工具:** caveman + ecc (review-work, security-review) + code-review-graph (pr-review, exploring)
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
      └─ 同上, 但:
          ├─ 更多并行步骤
          ├─ 依赖图更复杂
          └─ adversarial review 更严格
  → /gsd-new-project "$OBJECTIVE"                 ← gsd 项目管理
      ├─ PROJECT.md (目标/范围/里程碑)
      ├─ ROADMAP.md (阶段执行计划)
      └─ 初始化 .planning/ 目录
  → /gsd-plan-phase (per phase)                   ← 逐阶段规划
  → /gsd-execute-phase (per phase)                ← 逐阶段执行
  → /gsd-verify-work                              ← UAT 验证
  → /gsd-pr-branch → /gsd-ship                    ← PR + 合并
  → /gsd-milestone-summary                        ← 里程碑报告
```

**调用工具:** caveman + superpowers (brainstorm, plans) + ecc (blueprint) + gsd (new-project, plan-phase, execute-phase, verify-work, pr-branch, ship, milestone-summary)
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

### 路由判断

```
研究深度?
├─ 快速查证 (1-2 个问题)    → --fast
├─ 需要对比和推荐           → --standard
└─ 多源深度研究 + 引用      → --deep
```

### --fast (快速查证)

```
caveman lite
  → MiniMax_web_search(query="$TOPIC")            ← web 搜索
  → 简要总结 + 链接
```

**调用工具:** caveman + web search
**Token:** 低

### --standard (对比研究) ← 默认

```
caveman full
  → 多个搜索源:
      ├─ MiniMax_web_search (web)
      ├─ context7_resolve-library-id + context7_query-docs (库文档)
      └─ GitHub code search (代码示例)
  → 评估候选方案:
      ├─ 功能性 / 维护性 / 社区 / 文档 / 许可证
      └─ 输出: 结构化对比表 + 推荐
  → 路由到 /tool-feat 或 /tool-plan
```

**调用工具:** caveman + web search + context7 + GitHub search
**不经过:** gsd, superpowers, code-review-graph

### --deep (深度研究 + 引用)

```
caveman full/ultra
  → /deep-research "$TOPIC"
      ├─ 分解为 3-5 个子问题
      ├─ 多源搜索 (firecrawl + exa MCP)
      │   ├─ firecrawl_search (每个子问题)
      │   ├─ web_search_exa (多关键词变体)
      │   └─ 目标: 15-30 个独立来源
      ├─ 深度阅读 3-5 个关键源
      │   ├─ firecrawl_scrape (全文)
      │   └─ crawling_exa (5000 tokens)
      ├─ 综合报告:
      │   ├─ Executive Summary
      │   ├─ 主题分析 (带引用)
      │   ├─ Key Takeaways
      │   └─ 来源列表 + 方法论
      └─ 输出: cited report
  → /council (if conflicting recommendations)     ← 决策
  → 路由到 /tool-plan 或 /tool-feat
```

**调用工具:** caveman + ecc (deep-research, firecrawl/exa MCP) + ecc (council, 可选)
**不经过:** gsd, superpowers, code-review-graph

### Token 消耗分布

| 阶段 | 工具 | Token 消耗 | 备注 |
|------|------|-----------|------|
| 快速搜索 | web search | 低 | --fast |
| 库文档 | context7 | 低 | --standard |
| 深度搜索 | firecrawl + exa | **高** | --deep, 多源 |
| 深度阅读 | firecrawl_scrape | **高** | 全文抓取 |
| 综合报告 | LLM 生成 | 中 | --deep |
| 决策 | council | 中 | 可选 |

---

## 11. /tool-graph — 知识图谱操作

> code-review-graph status, full build, incremental update, rebuild, watch | 默认成本: Low

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

### 流程

```
caveman lite
  → gsd-update                                   ← 更新 GSD
      ├─ 检查远程版本
      ├─ 拉取最新代码
      ├─ 显示 changelog
      └─ 确认 → 更新
  → configure-ecc (可选)                          ← 更新 ECC
      ├─ 检查已安装 skills
      ├─ 对比远程版本
      └─ 确认 → 更新
  → 显示: 更新摘要 + 版本号
```

**调用工具:** caveman + gsd (update) + ecc (configure-ecc, 可选)
**Token:** 低

---

## 全量对比矩阵

### 12 命令 × 成本模式 × 工具调用

| 命令 | --fast | --standard | --deep |
|------|--------|-----------|--------|
| **quick** | caveman | caveman + ecc(测试) | N/A (转 feat/fix) |
| **fix** | caveman | caveman + gsd(debug) + superpowers(sysdbg,tdd) + ecc(测试,regression) | + gsd(code-fixer) + ecc(security,review-work) |
| **feat** | caveman | caveman + superpowers(brainstorm,plans,tdd) + ecc(search,测试) | + gsd(execute-phase) + ecc(review-work) |
| **branch** | caveman + ecc(git) | caveman + code-review-graph(pr-review) | N/A |
| **plan** | caveman + gsd(note) | caveman + gsd(explore) + superpowers(brainstorm,plans) | + gsd(plan-phase,review) |
| **refactor** | caveman + ecc(测试) | caveman + superpowers(tdd) + ecc(测试) | + superpowers(plans) + gsd(execute-phase) + ecc(review-work,e2e) |
| **review** | caveman(caveman-review) | caveman + code-review-graph(pr-review,exploring) + ecc(github-ops) | + ecc(review-work,security-review) |
| **brainstorm** | caveman + gsd(note) | caveman + gsd(explore) + superpowers(brainstorming) | + ecc(council,deep-research) |
| **blueprint** | N/A (转 feat) | caveman + superpowers(brainstorm,plans) + ecc(blueprint) | + gsd(new-project,plan-phase,execute-phase,verify,ship) |
| **research** | caveman + web-search | + context7 + GitHub-search | + deep-research(firecrawl,exa) + council |
| **graph** | caveman + code-review-graph(只读) | caveman + code-review-graph(build/update) + rtk | N/A |
| **update** | caveman + gsd(update) + ecc(configure-ecc) | N/A | N/A |

### 按工具的触发条件 (12 命令)

| 工具 | 触发的命令 |
|------|-----------|
| **caveman lite** | quick(--fast), fix(--fast), feat(--fast), branch(全部), plan(--fast), refactor(--fast), review(--fast), brainstorm(--fast), research(--fast), graph(status/watch), update |
| **caveman full** | quick(--standard), fix(--standard), feat(--standard), branch(review), plan(--standard), refactor(--standard), review(--standard), brainstorm(--standard), blueprint(--standard), research(--standard), graph(build/update/rebuild) |
| **caveman ultra** | fix(--deep), feat(--deep), refactor(--deep), review(--deep), brainstorm(--deep), blueprint(--deep), research(--deep) |
| **rtk** | fix(可选), feat(可选), refactor(可选), graph(build/update/rebuild, 可选) |
| **superpowers: brainstorming** | feat(--standard+), plan(--standard+), brainstorm(--standard+), blueprint(--standard+) |
| **superpowers: writing-plans** | feat(--standard+), plan(--standard+), brainstorm(--standard+), blueprint(--standard+), refactor(--deep) |
| **superpowers: tdd-workflow** | fix(--standard+), feat(--standard+), refactor(--standard+) |
| **superpowers: systematic-debugging** | fix(--standard+), 内嵌在 gsd-debug 中 |
| **superpowers: search-first** | feat(--standard+) |
| **gsd: note** | plan(--fast), brainstorm(--fast) |
| **gsd: explore** | plan(--standard+), brainstorm(--standard+) |
| **gsd: debug** | fix(--standard+) |
| **gsd: code-fixer** | fix(--deep) |
| **gsd: execute-phase** | feat(--deep), refactor(--deep), blueprint(--deep) |
| **gsd: plan-phase** | plan(--deep), blueprint(--deep) |
| **gsd: review** | plan(--deep) |
| **gsd: new-project** | blueprint(--deep) |
| **gsd: verify-work** | blueprint(--deep) |
| **gsd: pr-branch / ship** | blueprint(--deep) |
| **gsd: milestone-summary** | blueprint(--deep) |
| **gsd: update** | update |
| **ecc: 语言测试/构建** | quick(--standard), fix(全部), feat(全部), refactor(全部) |
| **ecc: search-first** | feat(--standard+) |
| **ecc: review-work** | fix(--deep), feat(--deep), refactor(--deep), review(--deep) |
| **ecc: security-review** | fix(--deep, if security), review(--deep, if security) |
| **ecc: ai-regression-testing** | fix(--standard+) |
| **ecc: blueprint** | blueprint(--standard+) |
| **ecc: council** | brainstorm(--deep), research(--deep) |
| **ecc: deep-research** | brainstorm(--deep), research(--deep) |
| **ecc: github-ops** | branch(create/merge), review(--standard+) |
| **ecc: configure-ecc** | update |
| **code-review-graph** | branch(review), review(--standard+), graph(全部) |

### Token 消耗总览

| 命令 | --fast | --standard | --deep |
|------|--------|-----------|--------|
| quick | 极低 | 低 | - |
| fix | 低 | 中 | 高 |
| feat | 低 | 中-高 | 最高 |
| branch | 极低 | 低 | - |
| plan | 极低 | 中 | 中-高 |
| refactor | 低 | 中 | 高 |
| review | 低 | 中 | 高 |
| brainstorm | 极低 | 中 | 中 |
| blueprint | - | 高 | 最高 |
| research | 低 | 中 | 高 |
| graph | 极低 | 中 | - |
| update | 低 | - | - |

---

## 最大化利用建议

### 1. 从 --fast 开始, 按需升级

```
不确定复杂度? 先试 --fast
  → 够用? 完成
  → 不够? 升级到 --standard
  → 还不够? 升级到 --deep
```

### 2. caveman 全程开启

无论哪个模式, caveman 都应该激活:
- `--fast` 用 `lite` (保持可读性)
- `--standard` 用 `full` (平衡压缩和可读)
- `--deep` 用 `full`, 长上下文时切 `ultra`

### 3. rtk 按需启用

只在有噪声输出时启用:
- git log/diff 输出很长
- 测试输出大量日志
- 构建输出冗长

### 4. code-review-graph 的使用场景

code-review-graph 只在三个命令中触发:
- `/tool-review --standard+` — PR 审查
- `/tool-branch review` — 分支审查
- `/tool-graph` — 专门操作知识图谱

其他命令不直接调用它, 但可以通过 `/tool-graph build` 预构建图谱, 让后续 review 命令获得更好的上下文。

### 5. gsd 的触发边界

gsd 重量级流程的触发条件:
- `--fast` 模式: 完全不调用 gsd (除 note)
- `--standard` 模式: 只调用轻量 gsd (explore, debug, note)
- `--deep` 模式: 调用重量级 gsd (execute-phase, plan-phase, code-fixer)

### 6. superpowers 是 --standard 的核心骨架

`--standard` 模式主要依赖 superpowers 的结构化工作流:
- brainstorming → 探索需求
- writing-plans → 生成计划
- tdd-workflow → 测试驱动
- systematic-debugging → 科学调试

gsd 只在需要更强的项目管理时才介入。

### 7. 命令间路由

```
/tool-brainstorm → 明确后 → /tool-plan 或 /tool-feat
/tool-plan → 审查后 → /tool-feat 或 /gsd-execute-phase
/tool-research → 决策后 → /tool-plan 或 /tool-feat
/tool-blueprint → 逐步 → /tool-feat 或 /tool-quick (per step)
/tool-fix --diagnose → 确认后 → /tool-fix (修复) 或 /tool-refactor (重构)
```

---

*基于 Engineer Shovel SKILL.md + optimal-workflow + superpowers/gsd/ecc/code-review-graph 各 skill 定义*
*最后更新: 2026-05-03*
