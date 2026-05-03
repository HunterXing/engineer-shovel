---
description: Complex multi-step project workflow — blueprint, execute, integrate, verify, ship
argument-hint: [--standard|--deep] [project-name] [goal description]
cost-profile: high
risk-level: high
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Bash, Task]
escalates-to: [/blueprint, GSD]
depends-on: [/tool-plan, /tool-research]
when-to-use: Use for multi-step or multi-session projects that cannot safely fit in a single small plan or PR.
---

# /tool-blueprint — Complex Multi-Step Projects

**Input**: $ARGUMENTS

Use this only when the work cannot fit safely in a single small plan or PR.

Compression: caveman full by default, caveman ultra for GSD/multi-agent summaries. Use rtk for scans/logs.

## Cost Modes

- `--standard` or default: multi-step but clear project → follow Decision Tree 3 in `docs/decision-trees.md`:
  - Code-centric multi-PR → L4: `ecc:blueprint` + L5: `superpowers:writing-plans`
- `--deep`: milestone-scale engineering → follow Decision Tree 3 in `docs/decision-trees.md`:
  - Milestone → L6: `gsd project` (discuss/plan/execute phases)
  - Architecture change → L6: `council`

## Flow

1. Create a blueprint with independently verifiable steps.
2. Mark dependencies and parallelizable work.
3. Execute each step with the matching `/tool-*` workflow.
4. If the blueprint touches auth, user data, or security boundaries, add L4: `ecc:security-review` as a project-level gate.
5. Run integration verification after dependent steps connect.
6. Use deep review/ship flow only after verification passes.

## Guardrail

If the task is under 3 files and requirements are clear, use `/tool-quick` or `/tool-feat` instead.
