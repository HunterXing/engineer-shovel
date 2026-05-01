# /tool-blueprint — Complex Multi-Step Projects

**工兵铲 · 复杂项目工作流**

## Pipeline
```
目标 → 蓝图 → 分步执行 → 集成 → 验证 → 发布
```

## Steps

### 1. 创建蓝图
```bash
/blueprint project-name "migrate database from SQLite to PostgreSQL"
# 产出 plans/PLAN.md:
#   - 分步拆解（1 PR/步）
#   - 依赖关系图
#   - 并行/串行安排
#   - 每步回滚策略
```

### 2. GSD 替代方案
```bash
/gsd-new-project "项目描述"
/gsd-plan-phase      # 规划各阶段
/gsd-execute-phase   # 执行各阶段
```

### 3. 分步执行
每步使用对应的工作流:
- 新功能 → `/tool-feat`
- 重构 → `/tool-refactor`
- Bug修复 → `/tool-fix`

### 4. 跨阶段集成检查
```bash
/gsd-verify-work   # 对话式 UAT
/gsd-audit-uat     # 跨阶段 UAT 审计
```

### 5. 最终审查
```bash
/review-work
```

### 6. 发布
```bash
/gsd-pr-branch     # 创建干净的 PR 分支
/gsd-ship          # PR + 审查 + 合并
/gsd-complete-milestone  # 归档里程碑
```

## Blueprint 结构
```
plans/$PROJECT-$FEATURE.md
  每步包含:
  ├── Context Brief（新鲜 agent 可直接执行）
  ├── Task Checklist
  ├── Verification Commands
  └── Exit Criteria
```
