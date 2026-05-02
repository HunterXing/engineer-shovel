---
description: New feature development workflow — explore, plan, implement, verify
argument-hint: [--fast|--standard|--deep] [feature description | path/to/plan.md]
---

# /tool-feat — New Feature Development

**Input**: $ARGUMENTS

Build the smallest feature slice that can be verified. Use deep workflows only for unclear or multi-component work.

Compression: use `/caveman full` by default; use `/caveman lite` for `--fast`; use RTK-wrapped shell output for git/test/build output when available.

## Cost Modes

| Mode | Use when | Path |
|---|---|---|
| `--fast` | known area, small feature | targeted search → implement → tests |
| `--standard` or default | normal feature, 3-8 files | explore patterns → plan → implement → verify |
| `--deep` | ambiguous, external deps, multi-system | librarian/explore → `/tool-plan` or `/tool-blueprint` |

## Flow

1. Search existing code for matching patterns before adding new structure.
2. Decide the smallest useful increment and verification target.
3. Implement using project conventions.
4. Run diagnostics, related tests, typecheck/build when applicable.
5. Use `/tool-review --fast` or default review by risk.

## Skill Hints

- Frontend/UI: visual-engineering + frontend/UI skills.
- Backend/API: backend-patterns, api-design.
- Full stack: fullstack-dev, tdd-workflow.
- Data/DB: database-migrations, postgres-patterns.
