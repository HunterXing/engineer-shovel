<p align="center">
  <img src="https://img.shields.io/github/stars/HunterXing/optimal-workflow?style=for-the-badge&color=6366f1" alt="Stars">
  <img src="https://img.shields.io/github/license/HunterXing/optimal-workflow?style=for-the-badge&color=22c55e" alt="License">
  <img src="https://img.shields.io/badge/OpenCode-Ready-8b5cf6?style=for-the-badge" alt="OpenCode">
  <img src="https://img.shields.io/badge/Claude_Code-Ready-d97706?style=for-the-badge" alt="Claude Code">
</p>

<h1 align="center">🧠 Optimal Workflow</h1>

<p align="center">
  <b>AI 代理开发工作流技能 — 面向 OpenCode & Claude Code</b><br>
  <sub>新功能 · Bug修复 · 头脑风暴 · 重构 · 代码审查 · 快速任务 · 复杂项目 · 深度研究</sub>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-workflow-quick-reference">Workflows</a> •
  <a href="#-toolchain">Toolchain</a> •
  <a href="README_zh.md">中文</a>
</p>

<p align="center">
  <code>skill(name="optimal-workflow")</code>
</p>

---

## 📖 What is this?

A **single skill** that encodes the optimal development workflow for the full toolchain:

```
OpenCode   + superpowers + ecc + gsd + omo + Caveman + rtk
Claude Code + superpowers + ecc + gsd      + Caveman + rtk
```

Load once — get step-by-step instructions for **any** development scenario.

---

## 🚀 Quick Start

**New user? One command setup:**

```bash
curl -fsSL https://raw.githubusercontent.com/HunterXing/optimal-workflow/main/install.sh | bash
```

This auto-installs **ECC**, **GSD**, **superpowers**, **Caveman**, **RTK** and the `optimal-workflow` skill.

**In session:**

```
skill(name="optimal-workflow")
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

## 📋 Workflow Quick Reference

| Scenario | Commands | Env |
|----------|----------|-----|
| 🆕 New Feature | `/plan` → `/prp-implement` → `/verify` → commit | OC / CC |
| 🆕 Complex | `/blueprint` → steps → `/gsd-execute-phase` | Both |
| 🐛 Bug Fix | `/gsd-debug` → fix → test → commit | Both |
| 💡 Brainstorming | `/gsd-explore` / `/superpowers:brainstorming` | Both |
| 🔧 Refactoring | `/refactor` → verify → `/review-work` → commit | Both |
| 📋 Code Review | `/code-review` / `/review-pr <url>` | Both |
| 📋 Deep Review | `/review-work` (5 parallel agents) | Both |
| ⚡ Quick Task | `/gsd-fast` / cavecrew builder | Both |
| 🏗️ Complex Project | `/blueprint` / GSD phases | Both |
| 🔬 Deep Research | `/deep-research` | Both |

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
optimal-workflow/
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
