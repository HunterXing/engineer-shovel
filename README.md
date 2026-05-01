<p align="center">
  <img src="https://img.shields.io/github/stars/HunterXing/engineer-shovel?style=for-the-badge&color=6366f1" alt="Stars">
  <img src="https://img.shields.io/github/license/HunterXing/engineer-shovel?style=for-the-badge&color=22c55e" alt="License">
  <img src="https://img.shields.io/badge/OpenCode-Ready-8b5cf6?style=for-the-badge" alt="OpenCode">
  <img src="https://img.shields.io/badge/Claude_Code-Ready-d97706?style=for-the-badge" alt="Claude Code">
</p>

<h1 align="center">🪖 工兵铲 · Optimal Workflow</h1>

<p align="center">
  <b>多合一 AI 代理开发工具</b><br>
  <sub>新功能 · Bug修复 · 头脑风暴 · 重构 · 代码审查 · 快速任务 · 复杂项目 · 深度研究</sub>
</p>

<p align="center">
  <code>/tool-feat</code> <code>/tool-fix</code> <code>/tool-plan</code> <code>/tool-refactor</code> <code>/tool-review</code> <code>/tool-brainstorm</code> <code>/tool-quick</code> <code>/tool-blueprint</code> <code>/tool-research</code>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-workflow-quick-reference">Workflows</a> •
  <a href="#-toolchain">Toolchain</a> •
  <a href="README_zh.md">中文</a>
</p>

<p align="center">
  <code>skill(name="engineer-shovel")</code>
</p>

---

## 📖 What is this?

**工兵铲** — 如同一把真正的工兵铲，集铲、镐、锯、量于一身。这个技能将完整开发工具链的最佳实践封装为 **9 个独立斜杠指令**，覆盖开发生命周期全部场景。

```
OpenCode   + superpowers + ecc + gsd + omo + Caveman + rtk
Claude Code + superpowers + ecc + gsd      + Caveman + rtk
```

每条指令对应一个完整工作流 — 从规划到验证，从修复到发布。

---

## 🚀 Quick Start

**New user? One command setup:**

```bash
curl -fsSL https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh | bash
```

This auto-installs **ECC**, **GSD**, **superpowers**, **Caveman**, **RTK** and the `engineer-shovel` skill.

**In session:**

```
skill(name="engineer-shovel")
```

Then navigate to your needed workflow.

---

## 🌟 Features

| Category | Description |
|----------|------------|
| 🎯 **8 Scenarios** | New Feature, Bug Fix, Brainstorming, Refactoring, Code Review, Quick Tasks, Complex Projects, Deep Research |
| 🔀 **Dual Environment** | Explicit `[OC]` / `[CC]` command branching |
| 🧭 **Decision Trees** | Primary router + complexity router |
| 🛠️ **Skill Loading** | Category + skills tables per feature type |
| ⚡ **Token Mgmt** | Caveman lite/full/ultra + context preservation |
| 🌐 **Lang Reference** | Test / Build / Review for 10 languages |
| 📋 **Quick Lookup** | 17-scenario command summary |

---

## 📋 Commands & Workflows

| Command | Scenario | Pipeline |
|---------|----------|----------|
| `/tool-feat` | 🆕 New Feature | `/plan` → `/prp-implement` → `/verify` → commit |
| `/tool-fix` | 🐛 Bug Fix | `/gsd-debug` → fix → test → commit |
| `/tool-plan` | 📐 Planning | `/plan` / `/blueprint` → review → execute |
| `/tool-refactor` | 🔧 Refactoring | `/refactor` → verify → `/review-work` → commit |
| `/tool-review` | 📋 Code Review | `/code-review` / `/review-pr` / `/review-work` |
| `/tool-brainstorm` | 💡 Brainstorming | `/gsd-explore` / `/superpowers:brainstorming` |
| `/tool-quick` | ⚡ Quick Tasks | `/gsd-fast` / cavecrew builder |
| `/tool-blueprint` | 🏗️ Complex Projects | `/blueprint` / GSD phases → `/gsd-ship` |
| `/tool-research` | 🔬 Deep Research | `/deep-research` → synthesize → apply |

> Each `commands/tool-*.md` is self-contained — env-aware steps with OpenCode `[OC]` and Claude Code `[CC]` variants.

---

## 🔧 Toolchain

| Tool | Purpose | Install |
|------|---------|---------|
| **ECC** | Plugin & skill framework | `/plugin install ecc@ecc` |
| **GSD** | Project management | Part of ECC |
| **superpowers** | Brainstorming & planning | `/plugin install superpowers@claude-plugins-official` |
| **Caveman** | Token compression | `/plugin install caveman@caveman` |
| **RTK** | CLI token optimization | `cargo install rtk` |

---

## 📂 Structure

```
engineer-shovel/
├── SKILL.md          # Main skill (681 lines)
├── install.sh        # One-command installer
├── README.md         # English docs
├── README_zh.md      # 中文文档
└── LICENSE           # MIT
```

---

## 📝 License

MIT — see [LICENSE](LICENSE)

<p align="center">
  <sub>Built for OpenCode + superpowers + ecc + gsd + omo + Caveman + rtk</sub>
</p>
