---
description: Planning workflow — clarify direction, choose the right planning depth, auto-upgrade to blueprint or GSD project when needed
argument-hint: [--fast|--standard|--deep] [goal description]
cost-profile: medium
risk-level: medium
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Bash, Task]
escalates-to: [/tool-research]
depends-on: []
when-to-use: Use when execution order, affected files, risks, or verification criteria are not obvious. Includes built-in brainstorm phase for unclear requirements.
---

# /tool-plan — Planning

**Input**: $ARGUMENTS

Unified planning entry point. Auto-detects complexity and escalates:
- **≤3 PR**: inline plan or `superpowers:writing-plans`
- **>3 PR**: `ecc:blueprint` (code-level dependency graph)
- **Milestone-scale**: `gsd project` (discuss → plan → execute phases)

Compression: caveman lite for short plans, caveman full for file-backed plans. Use rtk for shell evidence.

## Phase 0: Brainstorm (auto-triggered when direction unclear)

If the goal description is vague or missing concrete targets, enter clarification first:
- **Product direction unclear** ("what to build") → L6: `gsd-explore`
- **Technical approach unclear** ("how to build") → L5: `superpowers:brainstorming`
- **Multiple viable paths or architecture decision** → L6: `ecc:council`

## Cost Modes

- `--fast`: small task, clear scope → short inline plan → route to `/tool-quick` or `/tool-feat`.
- `--standard` or default: medium work → Phase 0 if needed → `superpowers:writing-plans`.
- `--deep`: auto-classify complexity:
  - **≤3 PR code work** → `ecc:blueprint` + `superpowers:writing-plans`
  - **>3 PR or milestone-scale** → L6: `gsd project` (discuss → plan → execute phases)
  - **Architecture change** → L6: `ecc:council` before blueprint

## Flow

1. Restate the goal and non-goals.
2. Identify files/modules likely affected. Code-review-graph (L2, auto-refreshed): run `detect-changes` for impact assessment.
3. Define verification commands and exit criteria.
4. If the work touches auth, user data, or security-sensitive paths, add L4: `ecc:security-review` as a planning checkpoint.
5. For file-backed plans, request review before execution.
6. Execute only after the plan is clear enough to verify.

## Escalation

- Unknown technical approach: use `/tool-research --quick` first.
- Multi-PR or milestone work is handled by `--deep` mode; no separate `/tool-blueprint` needed.
