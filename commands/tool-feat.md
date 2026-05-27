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
standalone: true
---

# /tool-feat — New Feature Development

**Input**: $ARGUMENTS

Build the smallest feature slice that can be verified. This command assumes the feature is already clear enough to implement.

## Shared Policies

See `commands/_shared.md` for:
- **Cost Modes** — fast/standard/deep with smart mode auto-detection
- **Security Gate** — auth/network/SQL/secrets → auto-promote to --deep
- **Toolchain Announcements** — 🚀 format for external tools
- **Completion Pipeline** — standard/deep verification steps
- **Error Recovery** — fallback and escalation strategies

## Command-Specific Logic

### Smart Mode

- Single file, obvious feature → `--fast`
- Multiple files, clear scope → `--standard`
- Cross-module, security, ambiguous → `--deep`

### Before Implementation

If the feature is not yet clear enough to build:
- **Need scope/order/acceptance** → `/tool-plan`
- **Need evidence for a decision** → `/tool-research`
- **Need product exploration first** → `skill(name="gsd-explore")`

Do not use this command as a generic clarification shell.

### Flow

0. Record baseline: run `/caveman-stats` (L2) to capture session starting token count. → announce: `🚀 **caveman** → recording baseline stats`
   Before editing, verify you are not on `main`/`master`; if you are, run `/tool-branch create feat <description>` first.
1. Explore the smallest useful context first:
   - search existing code for matching patterns before adding new structure
   - use `semantic_search_nodes(query="<similar_feature_or_pattern>")` → announce: `🚀 **code-review-graph** → searching for similar patterns`
   - use `query_graph(imports_of="<target_module>")` → announce: `🚀 **code-review-graph** → analyzing module dependencies`
   - use `get_architecture_overview` only when module boundaries are still unclear → announce: `🚀 **code-review-graph** → generating architecture overview`
2. Default `--standard` path:
   - find an existing pattern
   - implement the smallest verifiable slice
   - run project-native tests/build
   - finish with a light review
3. If requirements are still unclear after exploration, stop and route back to `/tool-plan`.
4. Escalate only by trigger:
   - decision needs evidence first -> `/tool-research`
   - durable acceptance or reviewable agreement -> OpenSpec
   - framework/security/integration guidance -> ECC → announce: `🚀 **ECC** → loading <framework> guidance`
   - multi-phase or cross-session delivery -> GSD
5. Do not run `openspec init` automatically from this command.
6. Implement the smallest verifiable slice.
7. Run diagnostics, related tests, typecheck/build, then `/tool-review --fast` for `--standard` work.
8. Run `/caveman-stats` (L2) to report session token consumption and savings. → announce: `🚀 **caveman** → reporting token stats`

### Error Handling

- If implementation hits unexpected complexity, stop and reassess with `/tool-plan`.
- If tests fail after implementation, switch to `/tool-fix` to address the failures.
- If the feature scope creeps, create a new slice and defer additional work.
