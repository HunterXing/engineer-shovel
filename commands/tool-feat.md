---
description: New feature development workflow — clarify, explore, plan, implement, verify
argument-hint: [--fast|--standard|--deep] [feature description | path/to/plan.md]
cost-profile: medium
risk-level: medium
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Edit, Bash, Task]
escalates-to: [/tool-plan, /tool-review]
depends-on: [/tool-research]
when-to-use: Use for adding new functionality. Includes built-in brainstorm phase when requirements are unclear. Choose the smallest verifiable feature slice.
---

# /tool-feat — New Feature Development

**Input**: $ARGUMENTS

Build the smallest feature slice that can be verified. This command assumes the feature is already clear enough to implement.

Shared policy: mode mapping, security gate, and completion pipeline come from `SKILL.md`; capability-layer roles and escalation rules live in `docs/architecture.md`. Wrap large test/build output with `rtk gain`.

## Before Implementation

If the feature is not yet clear enough to build:
- **Need scope/order/acceptance** → `/tool-plan`
- **Need evidence for a decision** → `/tool-research`
- **Need product exploration first** → `skill(name="gsd-explore")`

Do not use this command as a generic clarification shell.

## Cost Modes

- `--fast`: known area, small feature → confirm pattern → implement → target verification
- `--standard` or default: normal feature, 3-8 files → targeted CRG context → implement → native tests/build → light review
- `--deep`: external deps, multi-system, milestone, or high-risk feature → escalate deliberately per `docs/architecture.md`

## Flow

0. Record baseline: run `/caveman-stats` (L2) to capture session starting token count.
   Before editing, verify you are not on `main`/`master`; if you are, run `/tool-branch create feat <description>` first.
1. Explore the smallest useful context first:
   - search existing code for matching patterns before adding new structure
   - use `semantic_search_nodes(query="<similar_feature_or_pattern>")` or `query_graph(imports_of="<target_module>")` when CRG will materially reduce search cost
   - use `get_architecture_overview` only when module boundaries are still unclear
   If CRG MCP tools are unavailable in the current harness, use `code-review-graph` CLI or fall back to targeted Glob/Grep/Read.
2. Default `--standard` path:
   - find an existing pattern
   - implement the smallest verifiable slice
   - run project-native tests/build
   - finish with a light review
3. If requirements are still unclear after exploration, stop and route back to `/tool-plan`.
4. Escalate only by trigger:
   - decision needs evidence first -> `/tool-research`
   - durable acceptance or reviewable agreement -> OpenSpec
   - framework/security/integration guidance -> ECC
   - multi-phase or cross-session delivery -> GSD
5. Do not run `openspec init` automatically from this command.
6. Implement the smallest verifiable slice.
7. Run diagnostics, related tests, typecheck/build, then `/tool-review --fast` for `--standard` work. Deep-mode verify/review/ship stays in the shared completion pipeline from `SKILL.md`.
8. Run `/caveman-stats` (L2) to report session token consumption and savings.

## Security Gate

If change touches auth, user input, file system, network, secrets, cookies, or SQL, promote it to a security-sensitive route and add `/tool-review --deep` before completion.

## Skill Routing

Use project-native skills and commands from `docs/language-reference.md` instead of loading broad skill sets by default.
Escalate to superpowers, ECC, OpenSpec, or GSD only when the feature cannot remain decision-light and still be implemented safely.
Standard feature work should stay close to native code search, implementation, tests/build, and lightweight review.
