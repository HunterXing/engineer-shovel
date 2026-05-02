> ⚠️ Reference doc — commands are not executable. Follow the steps manually.

# /tool-quick — Quick Tasks

**工兵铲 · 快速任务工作流**

## Pipeline
```
任务 → 执行 → 验证 → 提交
```

## Options

### 选项 A: GSD Quick（通用）
```bash
/gsd-fast "fix typo in README.md"
/gsd-fast "update dependency version to 2.0"
/gsd-fast "rename variable x to y in file.ts"
```

### 选项 B: Caveman Builder（最省 token）
```bash
# 1-2 文件精确编辑 — 使用 cavecrew-builder
# subagent 输出 caveman 压缩 (~60% 省 token)
```

### 选项 C: 直接 task()
```bash
task(category="quick", load_skills=[], prompt="Change X to Y in file.ts")
```

## Choice
| 任务类型 | 最佳工具 | 原因 |
|----------|----------|------|
| Typo, 1 行 | `/gsd-fast` | 零开销 |
| 1-2 文件编辑 | Cavecrew builder | ~60% token 节省 |
| 配置修改 | `/gsd-fast` | 快速安全 |
| 简单重命名 | `/gsd-fast` 或 LSP rename | 内置工具 |
| 非平凡任务 | 走完整工作流 | 不能跳过规划 |

---
> Load the skill first: `skill(name="engineer-shovel")`
