---
description: New feature development workflow — explore, plan, implement, verify
argument-hint: [--fast|--standard|--deep] [feature description | path/to/plan.md]
cost-profile: medium
risk-level: medium
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Edit, Bash, Task]
escalates-to: [/tool-plan, /tool-blueprint, /tool-review]
depends-on: [/tool-research]
when-to-use: Use for adding new functionality after choosing the smallest verifiable feature slice.
---

# /tool-feat — New Feature Development

**Input**: $ARGUMENTS

Build the smallest feature slice that can be verified. Use deep workflows only for unclear or multi-component work.

Compression: follow `docs/token-cost.md`; default to `/caveman full`, lite for `--fast`, and RTK for git/test/build output.

## Cost Modes

- `--fast`: known area, small feature → targeted search → implement → tests.
- `--standard` or default: normal feature, 3-8 files → explore patterns → plan → implement → verify.
- `--deep`: ambiguous, external deps, multi-system → librarian/explore → `/tool-plan` or `/tool-blueprint`.

## Flow

1. Search existing code for matching patterns before adding new structure.
2. Decide the smallest useful increment and verification target.
3. Implement using project conventions.
4. Run diagnostics, related tests, typecheck/build when applicable.
5. Use `/tool-review --fast` or default review by risk.

## Skill Routing

Use project-native skills and commands from `docs/language-reference.md` instead of loading broad skill sets by default.
