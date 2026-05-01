# /tool-review — Code Review

**工兵铲 · 代码审查工作流**

## Pipeline
```
代码 → 审查 → 修复 → 重新审查 → 批准
```

## Modes

### Mode 1: 本地改动
```bash
/code-review
# 审查 staged/unstaged diff
```

### Mode 2: GitHub PR
```bash
/review-pr https://github.com/user/repo/pull/123
```

### Mode 3: 深度审查（实现完成后）
```bash
/review-work
# 5 个并行审查代理:
#   - 目标/约束验证 (Oracle)
#   - 代码质量 (Oracle)
#   - 安全审计 (Oracle)
#   - 手动 QA (unspecified-high)
#   - 上下文挖掘 (unspecified-high)
# 全部通过才算审查通过
```

### Mode 4: 压缩审查（省 token）
```bash
/caveman:caveman-review
# 一行一条: path:line: severity: problem. fix.
```

## Decision
| 场景 | 命令 |
|------|------|
| 本地 diff (< 10 files) | `/code-review` 或 `/caveman:caveman-review` |
| GitHub PR | `/review-pr <url>` |
| 重大实现 | `/review-work` |
| 安全敏感 | `/security-review` → `/security-scan` |
| 快速检查 | `/caveman:caveman-review` |
