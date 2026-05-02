> ⚠️ Reference doc — commands are not executable. Follow the steps manually.

# /tool-refactor — Refactoring

**工兵铲 · 重构工作流**

## Pipeline
```
目标 → 基线 → 执行 → 验证 → 审查 → 提交
```

## Steps

### 1. 建立基线
```bash
bun test  # 先确保所有测试通过
```

### 2. 执行重构
```bash
/refactor "描述重构目标"
# 自动完成:
#   1. LSP + AST-grep 分析代码
#   2. 创建架构图
#   3. 分阶段重构
#   4. 每阶段 TDD 验证
```

### 3. 验证行为不变
```bash
bun test         # 所有测试必须通过
bun run build    # 构建必须成功
```

### 4. 全面审查
```bash
/review-work
# 5 个并行审查代理
```

### 5. E2E 检查
```bash
/playwright    # 前端 E2E
/e2e-testing   # 后端 E2E
```

### 6. 提交
```bash
git add . && git commit -m "refactor: $SCOPE"
```

## 原则
1. 不改行为 — 测试是安全网
2. 小步提交 — 每次一个逻辑单元
3. 不混入新功能 — refactor + feature 分开
4. 性能不降 — 对比基准
5. 必须有审查 — 重构容易引入隐蔽 bug

---
> Load the skill first: `skill(name="engineer-shovel")`
