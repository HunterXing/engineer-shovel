---
name: 工兵铲-lite
display_name: engineer-shovel-lite
description: |
  Engineer Shovel Lite — Essential commands only (Level 1)
  For full documentation, see SKILL.md (Level 2/3)
license: MIT
metadata:
  version: "1.7.5"
  category: workflow
  token_profile: ultra-lightweight
---

# 🪖 Engineer Shovel — Quick Reference

## Commands (10)

| Command | Use for | Cost |
|---------|---------|------|
| `/tool-quick` | Typo, config, 1-2 files | Low |
| `/tool-fix` | Bug, failing test | Low→High |
| `/tool-feat` | New feature | Medium |
| `/tool-plan` | Requirements, planning | Medium |
| `/tool-review` | Code review | Low→High |
| `/tool-refactor` | Cleanup | Medium |
| `/tool-research` | Evidence gathering | Low→High |
| `/tool-branch` | Branch management | Low |
| `/tool-graph` | Graph diagnostics | Low |
| `/tool-update` | Sync & update | Low |

## Aliases

`/q` `/f` `/fe` `/p` `/r` `/rf` `/rs` `/b` `/g` `/u`

## Cost Modes

`--fast` `--standard` `--deep`

## Toolchain

🚀 Announced when active: code-review-graph, caveman, rtk, superpowers, ECC, OpenSpec, GSD, claude-mem

---

*For full routing rules, escalation logic, and tool details, load `skill(name="engineer-shovel")` (Level 2)*
