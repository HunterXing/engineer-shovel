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

## Cost Modes (Self-Contained)

| Mode | When | Caveman | Typical path |
|------|------|---------|--------------|
| `--fast` | Small task, clear scope | `/caveman lite` | Short execution plan → route to `/tool-quick` or `/tool-feat` |
| `--standard` | Medium work (default) | `/caveman full` | Define order, risks, verification, exit criteria |
| `--deep` | Spec-first, multi-PR, milestone, architecture-heavy | `/caveman full` → `ultra` | Deliberate escalation per architecture |

**Smart mode**: If no mode specified:
- Clear scope, small task → `--fast`
- Normal planning → `--standard`
- Complex, cross-system, security → `--deep`

## Security Gate (Self-Contained)

If work touches **auth, user data, or security-sensitive paths**:
→ Add `/tool-review --deep` before sign-off.

## Before Planning

If the work is not ready for a plan yet:
- **What to build is unclear** → `skill(name="gsd-explore")`
- **A decision needs evidence first** → `/tool-research`
- **A small task is already clear** → skip planning and use `/tool-quick` or `/tool-feat`

## Flow

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

## Plan Quality Checklist

- [ ] Goal is clear and measurable
- [ ] Non-goals are explicitly stated
- [ ] Affected files/modules are identified
- [ ] Execution order is defined
- [ ] Verification method is specified
- [ ] Exit criteria are clear
- [ ] Escalation triggers are documented

## Error Handling

- If the goal is too vague, ask clarifying questions before planning.
- If scope is too large for a single plan, break into phases and recommend GSD.
- If technical approach is unknown, escalate to `/tool-research` first.
- If planning reveals security concerns, add `/tool-review --deep` checkpoint.

## Toolchain Announcements

When using external tools, announce them with maximum visibility:
- `🚀 **code-review-graph** → <action>` — when analyzing code structure or impact
- `🚀 **ECC** → loading <domain> guidance` — when consulting specialized knowledge
- `🚀 **OpenSpec** → creating durable spec` — when generating persistent artifacts
- `🚀 **GSD** → orchestrating multi-phase delivery` — when planning milestone work
- `🚀 **superpowers** → loading writing-plans skill` — when using structured planning methods

## Escalation

- Unknown technical approach: use `/tool-research` first.
- Multi-PR, milestone, or cross-session work is handled by `--deep`.
- Do not default to GSD or OpenSpec when a normal implementation plan is enough.

## References

- Full router: `skill(name="engineer-shovel")` or `SKILL.md`
- Architecture: `docs/architecture.md`
