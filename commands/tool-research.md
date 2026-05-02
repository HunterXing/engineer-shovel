> ⚠️ Reference doc — commands are not executable. Follow the steps manually.

# /tool-research — Deep Research

**工兵铲 · 深度研究工作流**

## Pipeline
```
问题 → 多源搜索 → 综合 → 报告 → 应用
```

## Steps

### 1. 多源研究
```bash
/deep-research "How to implement $TECHNOLOGY for $USE_CASE"
# 搜索: web, docs, GitHub, academic sources
# 返回: 有来源引用的报告
```

### 2. 代码/模式搜索
```bash
# 库文档:
task(subagent_type="librarian", load_skills=[], prompt="Find examples of $PATTERN")

# 网页搜索:
MiniMax_web_search(query="$TOPIC best practices 2026")

# GitHub 搜索:
ecc_github_search_code(q="$TECHNIQUE language:typescript")
```

### 3. 综合发现
```bash
# 有冲突建议时:
/council "Option A vs Option B for $DECISION"
```

### 4. 路由到实现
- 原型: `/gsd-fast "build poc"`
- 完整功能: `/tool-plan` → `/tool-feat`
- 先研究: 继续 `/deep-research`

---
> Load the skill first: `skill(name="engineer-shovel")`
