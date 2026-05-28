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
standalone: true
---

# /tool-plan — Planning

**Input**: $ARGUMENTS

Unified planning entry point. Use this command when the work is not yet executable because scope, order, ownership, or acceptance is unclear.

## Cost Modes

| Mode | Caveman | When |
|------|---------|------|
| `--fast` | `/caveman lite` | Clear scope, small task |
| `--standard` | `/caveman full` | Normal planning (default) |
| `--deep` | `/caveman full` → `ultra` | Complex, cross-system, security |

**Security Gate**: If change touches auth/network/SQL/secrets → auto-promote to `--deep` + `/tool-review --deep`.

## Command-Specific Logic

### Smart Mode

- Clear scope, small task → `--fast`
- Normal planning → `--standard`
- Complex, cross-system, security → `--deep`

### Before Planning

If the work is not ready for a plan yet:
- **What to build is unclear** → `skill(name="gsd-explore")`
- **A decision needs evidence first** → `/tool-research`
- **A small task is already clear** → skip planning and use `/tool-quick` or `/tool-feat`

### Flow

1. Restate goal, non-goals, and what must be true before execution can start.
2. Identify likely affected files/modules via code-review-graph (L2, auto-refreshed):
   - `detect_changes` to assess impact scope → announce: `🚀 **code-review-graph** → detecting change scope`
   - `get_impact_radius(target="<key_module>")` → announce: `🚀 **code-review-graph** → analyzing impact radius`
   - `get_architecture_overview` for module boundaries (deep mode only) → announce: `🚀 **code-review-graph** → generating architecture overview`
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

### Plan Quality Checklist

- [ ] Goal is clear and measurable
- [ ] Non-goals are explicitly stated
- [ ] Affected files/modules are identified
- [ ] Execution order is defined
- [ ] Verification method is specified
- [ ] Exit criteria are clear
- [ ] Escalation triggers are documented

### Error Handling

- If the goal is too vague, ask clarifying questions before planning.
- If scope is too large for a single plan, break into phases and recommend GSD.
- If technical approach is unknown, escalate to `/tool-research` first.
- If planning reveals security concerns, add `/tool-review --deep` checkpoint.

### Escalation

- Unknown technical approach: use `/tool-research` first.
- Multi-PR, milestone, or cross-session work is handled by `--deep`.
- Do not default to GSD or OpenSpec when a normal implementation plan is enough.
