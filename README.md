# Optimal Development Workflow 🚀

**Environment-aware development workflow skill for OpenCode and Claude Code.**

Loaded with `skill(name="optimal-workflow")` — provides step-by-step workflows for every development scenario, including decision trees, tool selection guides, and token management.

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| **8 Scenarios** | New Feature, Bug Fix, Brainstorming, Refactoring, Code Review, Quick Tasks, Complex Projects, Deep Research |
| **Dual Environment** | Branching for OpenCode (`[OC]`) and Claude Code (`[CC]`) |
| **Decision Trees** | Primary router + Task complexity router |
| **Tool Selection** | Skill loading tables (category + skills) per feature type |
| **Token Management** | Caveman modes + context preservation strategies |
| **Language Reference** | 10 language/framework test/build/review command tables |
| **Fast Reference** | 17-scenario command summary table |

---

## 🚀 Quick Start

### New User — One Command Setup

```bash
curl -fsSL https://raw.githubusercontent.com/HunterXing/optimal-workflow/main/install.sh | bash
```

This installs:
- ✅ **ECC** — Everything Claude Code (plugin framework)
- ✅ **GSD** — Get Stuff Done (project management)
- ✅ **superpowers** — Brainstorming, planning, code review plugins
- ✅ **Caveman** — Token-efficient communication mode
- ✅ **RTK** — Rust Token Killer (60-90% token savings on CLI ops)
- ✅ **optimal-workflow** — This skill itself

### In Your AI Coding Session

```bash
# Load the skill
skill(name="optimal-workflow")

# Then follow the workflow for your task:
skill(name="optimal-workflow")  # → see "New Feature" section → /plan → /prp-implement
```

---

## 📋 Workflow Quick Reference

| Scenario | Command Pipeline | Environment |
|----------|-----------------|-------------|
| 🆕 New Feature | `/plan` → `/prp-implement` → `/verify` → commit | OpenCode / Claude Code |
| 🆕 New Feature (complex) | `/blueprint` → steps → `/gsd-execute-phase` | Both |
| 🆕 New Feature (simple) | `/gsd-fast "implement ..."` | Both |
| 🐛 Bug Fix | `/gsd-debug` → fix → test → commit | Both |
| 💡 Brainstorming | `/gsd-explore` or `/superpowers:brainstorming` | Both |
| 🔧 Refactoring | `/refactor` → verify → `/review-work` → commit | Both |
| 📋 Code Review (local) | `/code-review` | OpenCode |
| 📋 Code Review (PR) | `/review-pr <url>` | Both |
| 📋 Deep Review | `/review-work` | Both |
| ⚡ Quick Task | `/gsd-fast` or cavecrew builder | Both |
| 🏗️ Complex Project | `/blueprint` or GSD phases | Both |
| 🔬 Deep Research | `/deep-research` | Both |

---

## 📚 Full Documentation

All workflow details are in the skill itself:

- **File**: `SKILL.md` (681 lines)
- **Load**: `skill(name="optimal-workflow")`
- **Sections**:
  1. Environment Detection
  2. Core Principles (8 rules)
  3. New Feature Development
  4. Bug Fixing
  5. Brainstorming & Exploration
  6. Refactoring
  7. Code Review (4 modes)
  8. Quick Tasks
  9. Complex Multi-Step Projects
  10. Deep Research
  11. Decision Trees
  12. Token & Context Management
  13. Language/Framework Quick Reference
  14. Command Reference Summary

---

## 🔧 Toolchain Requirements

| Tool | Purpose | Install Command |
|------|---------|----------------|
| **ECC** | Everything Claude Code — skill & plugin framework | `/plugin install ecc@ecc` |
| **GSD** | Get Stuff Done — project management | Part of ECC |
| **superpowers** | Brainstorming & planning plugins | `/plugin install superpowers@claude-plugins-official` |
| **Caveman** | Token-efficient communication | `/plugin install caveman@caveman` |
| **RTK** | Rust Token Killer — CLI token optimization | `cargo install rtk --git https://github.com/rtk-ai/rtk` |

---

## 📂 Repository Structure

```
optimal-workflow/
├── SKILL.md            # Main skill file (681 lines)
├── install.sh          # One-command bootstrap installer
├── README.md           # This file
├── LICENSE             # MIT License
└── references/         # Future: per-environment reference docs
```

---

## 🧠 Skill Loading Strategy

This skill is designed to be **loaded on demand**, not auto-loaded:
- Run `skill(name="optimal-workflow")` when you start a new task
- The skill then guides your tool selection based on task type and environment
- Unlike AGENTS.md (auto-loaded), skills only consume context when explicitly requested

---

## 📝 License

MIT — see [LICENSE](LICENSE)

---

*Built for: OpenCode + superpowers + ecc + gsd + omo + Caveman + rtk*
*Also compatible with: Claude Code + superpowers + ecc + gsd + Caveman + rtk*
