# 最佳开发方案 (Optimal Workflow)

基于 **OpenCode + superpowers + ecc + gsd + omo + Caveman + rtk** 工具链的最优开发流程。

> Claude Code 环境: **superpowers + ecc + gsd + Caveman + rtk**

---

## 🚀 快速入口

```bash
# 加载完整工作流指南 (推荐)
skill(name="optimal-workflow")

# 然后按场景选择对应流程
```

> 完整的工作流说明书在 `/root/.agents/skills/optimal-workflow/SKILL.md`，包含：
> - 8 大场景的详细步骤
> - OpenCode vs Claude Code 双环境分支
> - 决策树、Token 管理、命令速查表

---

## 快速参考表

| 场景 | 命令 | 文档章节 |
|------|------|----------|
| 🆕 新功能 | `/plan` → `/prp-implement` | 1. New Feature |
| 🐛 Bug 修复 | `/gsd-debug` → fix → test | 2. Bug Fixing |
| 💡 头脑风暴 | `/gsd-explore` or `/superpowers:brainstorming` | 3. Brainstorming |
| 🔧 重构 | `/refactor` → verify → `/review-work` | 4. Refactoring |
| 📋 代码审查 | `/code-review` or `/review-pr <url>` | 5. Code Review |
| ⚡ 快速任务 | `/gsd-fast` or cavecrew builder | 6. Quick Tasks |
| 🏗️ 复杂项目 | `/blueprint` or GSD phases | 7. Complex Projects |
| 🔬 深度研究 | `/deep-research` | 8. Deep Research |

---

## 核心原则

1. **Search before build** — `/search-first` 或先搜索现有方案
2. **Test-first** — `/tdd-workflow` 测试驱动开发
3. **Surgical changes** — ≤3 files/task, 复杂任务拆解
4. **Verify every step** — 构建→测试→审查, 从不跳过验证
5. **Token awareness** — `/caveman-stats` 监控, `/caveman` 省 token
6. **Parallel when independent** — 独立任务并行执行
7. **Right model for the job** — `visual-engineering` 做 UI, `ultrabrain` 做复杂逻辑, `deep` 做自主任务

---

## 🔧 按语言/框架专用命令

| 语言/框架 | 测试 | 构建 | 审查 |
|-----------|------|------|------|
| Go | `/go-test` | `/go-build` | `/go-review` |
| Rust | `/rust-test` | `/rust-build` | `/rust-review` |
| C++ | `/cpp-test` | `/cpp-build` | `/cpp-review` |
| Flutter | `/flutter-test` | `/flutter-build` | `/flutter-review` |
| Kotlin | `/kotlin-test` | `/kotlin-build` | `/kotlin-review` |
| Python | `pytest` | - | `/python-review` |
| Laravel | `/laravel-tdd` | - | `/laravel-verification` |
| Django | `/django-tdd` | - | `/django-verification` |
| Spring Boot | `/springboot-tdd` | - | `/springboot-verification` |
| TypeScript/JS | `bun test` | `bun run build` | `/code-review` |

---

## 💡 Token 管理

```bash
/caveman lite    # 轻度压缩 (25-50% context)
/caveman full    # 完全压缩 (50-75% context)
/caveman ultra   # 最大压缩 (>75% context)
/caveman-stats   # 查看实时用量
/strategic-compact  # 上下文压缩
/gsd-thread      # 跨 session 连续性
```

---

## 其他
- 尽可能给用户中文回答
- 完整工作流参考: `skill(name="optimal-workflow")`
*最后更新: 2026-05-01*
