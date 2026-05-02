---
description: Planning workflow — choose the right planning depth before execution
argument-hint: [--fast|--standard|--deep] [goal description]
cost-profile: medium
risk-level: medium
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Bash, Task]
escalates-to: [/tool-blueprint, /tool-research]
depends-on: []
when-to-use: Use when execution order, affected files, risks, or verification criteria are not obvious.
---

# /tool-plan — Planning

**Input**: $ARGUMENTS

Use planning when execution order, risks, or verification criteria are not obvious.

Compression: follow `docs/token-cost.md`; use lite for short plans, full for file-backed plans, and RTK for shell evidence.

## Cost Modes

- `--fast`: small task, clear scope → short inline plan.
- `--standard` or default: medium work → `/plan` or `/prp-plan` with verification criteria.
- `--deep`: multi-session, ambiguous, many dependencies → `/blueprint` or GSD planning.

## Flow

1. Restate the goal and non-goals.
2. Identify files/modules likely affected.
3. Define verification commands and exit criteria.
4. For file-backed plans, request Momus review before execution.
5. Execute only after the plan is clear enough to verify.

## Escalation

- Unknown technical approach: use `/tool-research --quick` first.
- Multiple PRs or milestones: use `/tool-blueprint`.
