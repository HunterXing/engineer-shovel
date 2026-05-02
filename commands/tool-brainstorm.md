> ⚠️ Reference doc — commands are not executable. Follow the steps manually.

# /tool-brainstorm — Brainstorming & Exploration

**工兵铲 · 头脑风暴工作流**

## Pipeline
```
想法 → 探索 → 记录 → 评估 → 路由
```

## Steps

### 1. Socratic 探索
```bash
/gsd-explore "I have an idea: $IDEA"
# 通过苏格拉底式提问细化想法
```

### 2. 结构化头脑风暴
```bash
/superpowers:brainstorming
# 探索:
#   - 需求中隐藏的意图
#   - 边界情况
#   - 先设计再实现
#   - 假设和风险
```

### 3. 记录想法
```bash
/gsd-note "capture: $IDEA_DESCRIPTION"
```

### 4. 多方对抗决策
```bash
/council "Option A vs Option B for $DECISION"
# 四个声音的对抗辩论
```

### 5. 路由到执行
- 原型: `/gsd-fast "build poc for $IDEA"`
- 完整功能: `/plan` → `/prp-implement`
- 先研究: `/deep-research "$TOPIC"`
- 加入 backlog: `/gsd-note "backlog: $IDEA"`

## When to Use
| Signal | Tool |
|--------|------|
| 有想法但不确定 | `/gsd-explore` |
| 如何实现 X | `/superpowers:brainstorming` |
| 有没有现成方案 | `/search-first` / `/deep-research` |
| 快速捕捉 | `/gsd-note` |
| 多选项决策 | `/council` |

---
> Load the skill first: `skill(name="engineer-shovel")`
