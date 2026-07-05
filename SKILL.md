---
name: 工兵铲
display_name: engineer-shovel
description: |
  Engineer Shovel — token-aware AI agent development workflow router.
  This is the LEVEL 1 lightweight router. Load full details on demand.
license: MIT
metadata:
  version: "1.8.0"
  category: workflow
  token_profile: ultra-lightweight
  level: 1
  full_skill: engineer-shovel-full
---

# 🪖 Engineer Shovel — Quick Router

**Level 1**: Essential routing only (~50 lines). Load full details when needed.

## Quick Commands

| Task | Command | Alias | Example |
|------|---------|-------|---------|
| Quick edit | `/tool-quick` | `/q` | `/q "fix typo"` |
| Fix bug | `/tool-fix` | `/f` | `/f "login bug"` |
| New feature | `/tool-feat` | `/fe` | `/fe "dark mode"` |
| Plan work | `/tool-plan` | `/p` | `/p "refactor auth"` |
| Review | `/tool-review` | `/r` | `/r` |

## Cost Modes

- `--fast` (alias `--f`): Small, obvious changes
- `--standard` (alias `--s`): Normal development
- `--deep` (alias `--d`): Complex, risky, security-sensitive

## Smart Mode

If no mode specified, system auto-detects:
- Single file → `--fast`
- Multiple files → `--standard`
- Cross-module/security → `--deep`

## Toolchain

External tools announced with 🚀 when active:
code-review-graph, caveman, rtk, superpowers, ECC, OpenSpec, GSD, claude-mem

## Load Full Details

When you need deeper guidance, load the full skill:

```
skill(name="engineer-shovel-full")
```

Or read specific docs:
- `docs/architecture.md` — Layer architecture and escalation rules
- `docs/command-scenarios.md` — Scenario-based routing examples
- `docs/token-cost.md` — Token optimization strategies
- `docs/install.md` — Installation and configuration

## Core Rules

1. Start with main workflow: quick/fix/feat/plan
2. Use cheapest mode that verifies the result
3. External tools are upgrades, not defaults
4. Security-sensitive work → `--deep` + `/tool-review --deep`
