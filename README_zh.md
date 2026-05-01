<p align="center">
  <img src="https://img.shields.io/github/stars/HunterXing/optimal-workflow?style=for-the-badge&color=6366f1" alt="Stars">
  <img src="https://img.shields.io/github/license/HunterXing/optimal-workflow?style=for-the-badge&color=22c55e" alt="License">
  <img src="https://img.shields.io/badge/OpenCode-支持-8b5cf6?style=for-the-badge" alt="OpenCode">
  <img src="https://img.shields.io/badge/Claude_Code-支持-d97706?style=for-the-badge" alt="Claude Code">
</p>

<h1 align="center">🧠 Optimal Workflow（最优开发工作流）</h1>

<p align="center">
  <b>面向 AI 编码代理的开发工作流技能</b><br>
  <sub>覆盖从需求分析到代码提交的完整开发生命周期</sub>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> •
  <a href="#工作流速查">工作流速查</a> •
  <a href="#工具链">工具链</a> •
  <a href="README.md">English</a>
</p>

<p align="center">
  <code>skill(name="optimal-workflow")</code>
</p>

---

## 📖 这是什么？

一个 **单一技能（Skill）**，将完整工具链的最佳实践编码为可执行的工作流：

```
OpenCode   + superpowers + ecc + gsd + omo + Caveman + rtk
Claude Code + superpowers + ecc + gsd      + Caveman + rtk
```

加载一次 — 即可获得**任意**开发场景的分步指导。

---

## 🚀 快速开始

**新用户？一条命令搞定：**

```bash
curl -fsSL https://raw.githubusercontent.com/HunterXing/optimal-workflow/main/install.sh | bash
```

自动安装 **ECC**、**GSD**、**superpowers**、**Caveman**、**RTK** 和 `optimal-workflow` 技能本身。

**在编码会话中使用：**

```
skill(name="optimal-workflow")
```

然后根据你的任务选择对应场景即可。

---

## 🌟 功能特性

| 分类 | 说明 |
|------|------|
| 🎯 **8 大场景** | 新功能开发、Bug修复、头脑风暴、重构、代码审查、快速任务、复杂项目、深度研究 |
| 🔀 **双环境支持** | OpenCode `[OC]` 和 Claude Code `[CC]` 命令分支 |
| 🧭 **决策树** | 主任务路由 + 复杂度路由 |
| 🛠️ **技能加载** | 按功能类型的 category + skills 组合表 |
| ⚡ **Token 管理** | Caveman 三级压缩 + 上下文持久化策略 |
| 🌐 **语言参考** | 10 种语言的 测试/构建/审查 命令速查 |
| 📋 **命令速查** | 17 个场景的一键查找表 |

---

## 📋 工作流速查

| 场景 | 命令 | 环境 |
|------|------|------|
| 🆕 新功能开发 | `/plan` → `/prp-implement` → `/verify` → commit | OC / CC |
| 🆕 复杂新功能 | `/blueprint` → 分步执行 → `/gsd-execute-phase` | 通用 |
| 🆕 简单功能 | `/gsd-fast "..."` | 通用 |
| 🐛 Bug 修复 | `/gsd-debug` → 修复 → 测试 → commit | 通用 |
| 💡 头脑风暴 | `/gsd-explore` / `/superpowers:brainstorming` | 通用 |
| 🔧 重构 | `/refactor` → 验证 → `/review-work` → commit | 通用 |
| 📋 代码审查 | `/code-review`（本地）/ `/review-pr <url>`（PR） | 通用 |
| 📋 深度审查 | `/review-work`（5 个并行代理） | 通用 |
| ⚡ 快速任务 | `/gsd-fast` / cavecrew builder | 通用 |
| 🏗️ 复杂项目 | `/blueprint` / GSD 阶段管理 | 通用 |
| 🔬 深度研究 | `/deep-research` | 通用 |

---

## 🔧 工具链

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| **ECC** | Everything Claude Code — 技能与插件框架 | `/plugin install ecc@ecc` |
| **GSD** | Get Stuff Done — 项目管理 | ECC 内置 |
| **superpowers** | 头脑风暴与规划插件 | `/plugin install superpowers@claude-plugins-official` |
| **Caveman** | Token 高效通信 | `/plugin install caveman@caveman` |
| **RTK** | Rust Token Killer — CLI Token 优化 | `cargo install rtk` |

---

## 📂 仓库结构

```
optimal-workflow/
├── SKILL.md          # 核心技能文件（681 行）
├── install.sh        # 一键安装脚本
├── README.md         # 英文文档
├── README_zh.md      # 中文文档（本文件）
└── LICENSE           # MIT 许可证
```

---

## 🎯 核心原则

该技能内置的 8 条原则适用于所有工作流：

| # | 原则 | 原因 |
|---|------|------|
| 1 | **先搜索再编码** | 先用 `/search-first` 查找现有方案，避免重复造轮子 |
| 2 | **测试驱动** | `/tdd-workflow` 先写测试再实现 |
| 3 | **精准改动** | 单次任务 ≤3 个文件，复杂任务拆解为原子步骤 |
| 4 | **每步验证** | 构建 → 测试 → 检查，绝不跳过验证 |
| 5 | **Token 意识** | 用 `/caveman-stats` 监控，超过 50% 时 `/strategic-compact` |
| 6 | **独立并行** | 独立任务用 `task()` 并行执行 |
| 7 | **早提交、常提交** | 每个验证通过的步骤做原子提交 |
| 8 | **用对模型** | UI 用 `visual-engineering`，复杂逻辑用 `ultrabrain`，自主任务用 `deep` |

---

## 🧠 技能加载策略

此技能设计为**按需加载**，非自动加载：

- 开始新任务时执行 `skill(name="optimal-workflow")`
- 技能根据任务类型和环境引导你选择合适工具
- 与 AGENTS.md（自动加载）不同，技能只在显式请求时才消耗上下文

---

## 📝 许可证

MIT — 详见 [LICENSE](LICENSE)

<p align="center">
  <sub>基于 OpenCode + superpowers + ecc + gsd + omo + Caveman + rtk 构建</sub><br>
  <sub>同时兼容 Claude Code + superpowers + ecc + gsd + Caveman + rtk</sub>
</p>
