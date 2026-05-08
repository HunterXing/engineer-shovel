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

Unified planning entry point. This is the first place to clarify scope, order, and acceptance before reaching for heavier systems. Auto-detects complexity and escalates:
- **Durable requirement/spec needed**: OpenSpec artifacts via the repository's OpenSpec workflow
- **≤3 PR implementation work**: inline plan or file-backed implementation plan
- **Milestone-scale**: `skill(name="gsd-new-milestone")` (discuss → plan → execute phases)

Compression: `/caveman lite` for short plans, `/caveman full` for file-backed plans (per SKILL.md enforced mapping). Use RTK only for large shell outputs.

## Phase 0: Brainstorm (auto-triggered when direction unclear)

If the goal description is vague or missing concrete targets, enter clarification first:
- **Product direction unclear** ("what to build") → `skill(name="gsd-explore")`
- **Technical approach unclear** ("how to build") → `/tool-research --quick`
- **Multiple viable paths or architecture decision** → `/tool-research --deep`

Search claude-mem for prior architectural decisions that influence this plan:
- `npx claude-mem search "<goal_keywords>"` for relevant cross-session context.

## Cost Modes

- `--fast`: small task, clear scope → short inline plan → route to `/tool-quick` or `/tool-feat`.
- `--standard` or default: medium work → Phase 0 if needed → implementation order and acceptance. Use OpenSpec only when durable specs are actually needed.
- `--deep`: auto-classify complexity:
- **Spec-first code work** → OpenSpec artifacts first, then plan from accepted specs
- **≤3 PR code work** → file-backed implementation plan with explicit order, risks, and verification
- **>3 PR or milestone-scale** → `skill(name="gsd-new-milestone")` (discuss → plan → execute phases)
- **Architecture change** → `/tool-research --deep`, then convert conclusions into a file-backed plan or milestone plan

## Flow

1. Restate the goal and non-goals.
2. Identify files/modules likely affected via code-review-graph (L2, auto-refreshed):
   - `detect_changes` to assess impact scope from the diff baseline
   - `get_impact_radius(target="<key_module>")` to understand blast radius
   - `get_architecture_overview` for module boundaries (deep mode only)
   If CRG MCP tools are unavailable, use the `code-review-graph` CLI where possible or fall back to targeted Glob/Grep/Read.
3. Define the minimum plan contract: scope/non-goals, affected modules, execution order, verification commands, exit criteria, and escalation triggers.
4. If the work needs agreed requirements, create or update an OpenSpec change. Do not auto-run `openspec init`; ask the user to initialize the project or run it only with explicit approval.
5. If the work touches auth, user data, or security-sensitive paths, add a `/tool-review --deep` checkpoint to the plan before implementation sign-off.
6. For file-backed plans/specs, request review before execution.
7. Execute only after the plan is clear enough to verify.

## Escalation

- Unknown technical approach: use `/tool-research --quick` first.
- Multi-PR or milestone work is handled by `--deep` mode; no separate `/tool-blueprint` needed.
- Do not default to GSD or OpenSpec when a normal implementation plan is enough.
