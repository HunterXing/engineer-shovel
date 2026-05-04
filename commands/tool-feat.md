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

Build the smallest feature slice that can be verified. Use deep workflows only for unclear or multi-component work.

Compression: per SKILL.md enforced mapping — `/caveman lite` for `--fast`, `/caveman full` for `--standard`, `/caveman full` (escalate to `ultra` if subagent≥3) for `--deep`. Wrap large test/build output with `rtk gain`.

## Phase 0: Brainstorm (auto-triggered when requirements unclear)

If the feature description does not name specific files, classes, and expected behavior, enter clarification phase first:
- **Product direction unclear** ("what to build") → `skill(name="gsd-explore")`
- **Technical approach unclear** ("how to build") → `skill(name="brainstorming")`
- **Multiple viable paths for architecture** → `skill(name="council")`

Route result to the appropriate cost mode below. Do not implement until direction is clear.

## Cost Modes

- `--fast`: known area, small feature → `semantic_search_nodes` to confirm patterns → implement → tests → caveman review.
- `--standard` or default: normal feature, 3-8 files → `get_architecture_overview` + `semantic_search_nodes` for patterns → implement → gsd-verify-work.
- `--deep`: ambiguous, external deps, multi-system → Phase 0 brainstorm → plan → implement → gsd-verify-work → gsd-code-review → gsd-ship.

## Flow

0. Record baseline: run `/caveman-stats` (L2) to capture session starting token count.
   Verify you are not on `main`/`master`; if you are, run `/tool-branch create feat <description>` first.
1. Explore architecture via code-review-graph (L2, auto-refreshed):
   - `get_architecture_overview` for high-level structure and module boundaries
   - `semantic_search_nodes(query="<similar_feature_or_pattern>")` to find existing implementations
   - `query_graph(imports_of="<target_module>")` to understand dependencies
   Auto-load matching ECC pattern skill (e.g. `skill(name="golang-patterns")`, `skill(name="python-patterns")`). Use `docs/language-reference.md` for mapping.
2. Search existing code for matching patterns before adding new structure.
3. **Shortcut**: If the feature description already names specific files, classes, and expected behavior, skip Phase 0 and go directly to implement → verify.
4. If requirements are unclear (less than specific files+classes+behavior), run **Phase 0: Brainstorm** above.
5. Implement using project conventions.
6. Run diagnostics, related tests, typecheck/build. Wrap large test/build output with `rtk gain`.
7. Run `/caveman-stats` (L2) to report session token consumption and savings.
   For `--standard` features, use `/tool-review --fast` after implementation.
   For `--deep` features, skip `/tool-review` (GSD gates handle review in completion pipeline).

## Completion Gate

### `--fast`
8. Run project-native test/build → `skill(name="caveman-review")` → report. Done.

### `--standard`
8. `skill(name="gsd-verify-work")` — confirm feature behavior against requirements.
9. `skill(name="caveman-review")` — compressed code quality check on the diff.
10. Offer `/caveman-commit` suggestion (do NOT auto-commit without user request).

### `--deep`
8. `skill(name="gsd-verify-work")` — structured acceptance verification against plan.
9. `skill(name="gsd-code-review")` — phase-scoped review with severity-classified findings.
10. `skill(name="gsd-ship")` — create PR, run review gates, prepare for merge.
11. Offer `/caveman-commit` suggestion.

## Security Gate

If change touches auth, user input, file system, network, secrets, cookies, or SQL → escalate to `skill(name="security-review")`.

## Skill Routing

Use project-native skills and commands from `docs/language-reference.md` instead of loading broad skill sets by default.
