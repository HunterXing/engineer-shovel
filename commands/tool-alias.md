---
description: Command alias system — short aliases for frequent commands
argument-hint: [alias] [args...]
cost-profile: low
risk-level: low
recommended-mode: --fast
allowed-tools: [Read, Grep, Glob, Edit, Bash]
escalates-to: []
depends-on: []
when-to-use: Use short aliases for faster command entry. Aliases map to full /tool-* commands.
---

# /tool-alias — Command Aliases

**Input**: $ARGUMENTS

Quick reference for command aliases. Use these shortcuts for faster workflow.

## Alias Table

| Alias | Full Command | Description |
|-------|--------------|-------------|
| `/q` | `/tool-quick` | Quick task |
| `/f` | `/tool-fix` | Bug fix |
| `/fe` | `/tool-feat` | New feature |
| `/p` | `/tool-plan` | Planning |
| `/r` | `/tool-review` | Code review |
| `/rf` | `/tool-refactor` | Refactoring |
| `/rs` | `/tool-research` | Research |
| `/b` | `/tool-branch` | Branch management |
| `/g` | `/tool-graph` | Graph diagnostics |
| `/u` | `/tool-update` | Sync & update |

## Cost Mode Shortcuts

| Shortcut | Expansion |
|----------|-----------|
| `--f` | `--fast` |
| `--s` | `--standard` |
| `--d` | `--deep` |

## Usage Examples

```
/q "fix typo"                    → /tool-quick --fast "fix typo"
/f --s "login bug"               → /tool-fix --standard "login bug"
/fe "dark mode"                  → /tool-feat --standard "dark mode"
/p --d "refactor auth"           → /tool-plan --deep "refactor auth"
/r                               → /tool-review --standard
/rs --web "compare frameworks"   → /tool-research --web "compare frameworks"
```

## Implementation

This is a reference card. The actual routing is handled by the main SKILL.md router. When you use an alias, the system automatically expands it to the full command.

## Toolchain Announcements

No external tools needed for alias expansion — this is native routing.
