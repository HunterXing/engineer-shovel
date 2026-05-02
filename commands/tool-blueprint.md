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

Compression: use `/caveman full` by default; use `/caveman ultra` for GSD phases or multi-agent summaries. Use RTK for repository scans and verification logs when available.

## Cost Modes

| Mode | Use when | Path |
|---|---|---|
| `--standard` or default | multi-step but clear project | `/blueprint` with dependency graph |
| `--deep` | milestone-scale or long-running work | GSD project → discuss/plan/execute phases |

## Flow

1. Create a blueprint with independently verifiable steps.
2. Mark dependencies and parallelizable work.
3. Execute each step with the matching `/tool-*` workflow.
4. Run integration verification after dependent steps connect.
5. Use deep review/ship flow only after verification passes.

## Guardrail

If the task is under 3 files and requirements are clear, use `/tool-quick` or `/tool-feat` instead.
