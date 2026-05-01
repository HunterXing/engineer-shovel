# /tool-plan — Planning & Blueprint

**工兵铲 · 规划工作流**

## Pipeline
```
需求 → 分析 → 蓝图 → 审查 → 执行
```

## Steps

### 1. 通用规划（中等复杂度）
```bash
/plan "描述需求和目标"
```

### 2. 复杂多步项目
```bash
/blueprint project-name "描述目标"
# 产出 plans/PLAN.md:
#   - 分步拆解（1 PR/步）
#   - 依赖图
#   - 并行/串行排序
#   - 回滚策略
```

### 3. GSD 项目管理
```bash
/gsd-new-project "项目描述"
/gsd-plan-phase      # 规划每个阶段
/gsd-execute-phase   # 执行每个阶段
```

### 4. 审查计划
```bash
# 计划完成后检查
/gsd-review          # 跨 AI 审查
/ecc:review-pr       # PR 审查
```

## Complexity Decision
| 复杂度 | 工具 |
|--------|------|
| 简单 (< 3 files) | `/gsd-fast` 直接做 |
| 中等 (3-8 files) | `/plan` → `/prp-implement` |
| 复杂 (多组件) | `/blueprint` → 分步执行 |
| 不确定方案 | `/deep-research` → `/gsd-explore` → `/plan` |
