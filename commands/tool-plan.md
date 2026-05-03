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

Compression: caveman lite for short plans, caveman full for file-backed plans. Use rtk for shell evidence.

## Cost Modes

- `--fast`: small task, clear scope → short inline plan.
- `--standard` or default: medium work → follow Decision Tree 1 in `docs/decision-trees.md`:
  - **Product direction unclear** → L6: `gsd-explore`
  - **Technical approach unclear** → L5: `superpowers:brainstorming`
  → Then: ≤3 PR → `superpowers:writing-plans` | >3 PR → `/tool-blueprint`
- `--deep`: multi-session, ambiguous, many dependencies → gsd-plan-phase (phase-level) or `/blueprint` (code-level).

## Flow

1. Restate the goal and non-goals.
2. Identify files/modules likely affected. If code-review-graph installed (L3), run `code-review-graph detect-changes` for impact assessment first.
3. Define verification commands and exit criteria.
3b. If the work touches auth, user data, or security-sensitive paths, add L4: `ecc:security-review` as a planning checkpoint.
4. For file-backed plans, request review before execution.
5. Execute only after the plan is clear enough to verify.

## Escalation

- Unknown technical approach: use `/tool-research --quick` first.
- Multiple PRs or milestones: use `/tool-blueprint`.
