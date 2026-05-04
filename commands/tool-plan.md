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
- **≤3 PR**: inline plan or `skill(name="writing-plans")`
- **>3 PR**: `skill(name="blueprint")` (code-level dependency graph)
- **Milestone-scale**: `skill(name="gsd-new-milestone")` (discuss → plan → execute phases)

Compression: `/caveman lite` for short plans, `/caveman full` for file-backed plans (per SKILL.md enforced mapping). Use RTK only for large shell outputs.

## Phase 0: Brainstorm (auto-triggered when direction unclear)

If the goal description is vague or missing concrete targets, enter clarification first:
- **Product direction unclear** ("what to build") → `skill(name="gsd-explore")`
- **Technical approach unclear** ("how to build") → `skill(name="brainstorming")`
- **Multiple viable paths or architecture decision** → `skill(name="council")`

## Cost Modes

- `--fast`: small task, clear scope → short inline plan → route to `/tool-quick` or `/tool-feat`.
- `--standard` or default: medium work → Phase 0 if needed → `skill(name="writing-plans")`.
- `--deep`: auto-classify complexity:
- **≤3 PR code work** → `skill(name="blueprint")` + `skill(name="writing-plans")`
- **>3 PR or milestone-scale** → `skill(name="gsd-new-milestone")` (discuss → plan → execute phases)
- **Architecture change** → `skill(name="council")` for structured go/no-go before blueprint

## Flow

1. Restate the goal and non-goals.
2. Identify files/modules likely affected via code-review-graph (L2, auto-refreshed):
   - `detect_changes` to assess impact scope from the diff baseline
   - `get_impact_radius(target="<key_module>")` to understand blast radius
   - `get_architecture_overview` for module boundaries (deep mode only)
3. Define verification commands and exit criteria.
4. If the work touches auth, user data, or security-sensitive paths, add `skill(name="security-review")` as a planning checkpoint.
5. For file-backed plans, request review before execution.
6. Execute only after the plan is clear enough to verify.

## Escalation

- Unknown technical approach: use `/tool-research --quick` first.
- Multi-PR or milestone work is handled by `--deep` mode; no separate `/tool-blueprint` needed.
