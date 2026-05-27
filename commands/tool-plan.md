---
description: Planning workflow — clarify direction, choose the right planning depth, and escalate to durable artifacts only when needed
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

Unified planning entry point. Use this command when the work is not yet executable because scope, order, ownership, or acceptance is unclear.

This command owns planning. It should not become a generic research prelude or a duplicate feature command. The outcome should be a plan an implementer can execute without needing fresh product decisions.

Shared policy: mode mapping and completion behavior come from `SKILL.md`; escalation rules and capability-layer roles live in `docs/architecture.md`. Use RTK only for large shell outputs.

## Before Planning

If the work is not ready for a plan yet:
- **What to build is unclear** → `skill(name="gsd-explore")`
- **A decision needs evidence first** → `/tool-research`
- **A small task is already clear** → skip planning and use `/tool-quick` or `/tool-feat`

Search claude-mem only when prior architectural decisions are likely to change the plan.

## Cost Modes

- `--fast`: small task, clear scope → short execution plan → route to `/tool-quick` or `/tool-feat`
- `--standard` or default: medium work → define order, risks, verification, exit criteria
- `--deep`: spec-first, multi-PR, milestone, or architecture-heavy work → escalate deliberately per `docs/architecture.md`

## Flow

1. Restate goal, non-goals, and what must be true before execution can start.
2. Identify likely affected files/modules via code-review-graph (L2, auto-refreshed):
   - `detect_changes` to assess impact scope from the diff baseline
   - `get_impact_radius(target="<key_module>")` to understand blast radius
   - `get_architecture_overview` for module boundaries (deep mode only)
   If CRG MCP tools are unavailable, use the `code-review-graph` CLI where possible or fall back to targeted Glob/Grep/Read.
3. Define the minimum plan contract:
   - scope and non-goals
   - affected files/modules
   - execution order
   - verification method
   - exit criteria
   - escalation triggers
4. Use this command as the engineering decision router:
   - if a decision needs evidence -> `/tool-research`
   - if requirements must persist as artifacts -> OpenSpec
   - if work becomes phased, milestone-scale, or cross-session -> GSD
5. Use OpenSpec only if the agreement must persist as reviewable artifacts. Do not auto-run `openspec init`.
6. If the work touches auth, user data, or security-sensitive paths, add `/tool-review --deep` before sign-off.
7. Execute only after the plan is specific enough that implementation no longer needs new product decisions.

## Escalation

- Unknown technical approach: use `/tool-research` first.
- Multi-PR, milestone, or cross-session work is handled by `--deep`.
- Do not default to GSD or OpenSpec when a normal implementation plan is enough.
