> ⚠️ Reference doc — commands are not executable. Follow the steps manually.

# /tool-feat — New Feature Development

**工兵铲 · 新功能开发工作流**

## Pipeline
```
需求 → 规划 → 执行 → 验证 → 提交
```

## Steps

### 1. 复杂度判断
- 单文件改动 → 直接用 `/gsd-fast`
- 3-8 文件 → `/plan` → `/prp-implement`
- 多组件/不确定 → `/blueprint` → 分步执行

### 2. OpenCode 环境
```bash
# 分析 + 规划
/plan "实现 $FEATURE"
# 或复杂场景:
/blueprint project-name "实现 $FEATURE"
# 执行
/prp-implement plan.md
```

### 3. Claude Code 环境
```bash
# 规划
task(category="deep", load_skills=["search-first", "tdd-workflow"], prompt="...")
# 或
/blueprint project-name "实现 $FEATURE"
```

### 4. 验证
```bash
/verify
bun test && bun run build  # 或对应语言命令
```

### 5. 提交
```bash
git add . && git commit -m "feat: $DESCRIPTION"
```

## Skill Loading
| 类型 | Category | Skills |
|------|----------|--------|
| Frontend | `visual-engineering` | frontend-dev, frontend-design |
| Backend | `deep` | backend-patterns, api-design |
| Full Stack | `deep` | fullstack-dev, tdd-workflow |
| Data/DB | `deep` | postgres-patterns, database-migrations |

---
> Load the skill first: `skill(name="engineer-shovel")`
