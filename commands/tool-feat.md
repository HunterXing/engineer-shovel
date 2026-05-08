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

Build the smallest feature slice that can be verified. This is a main workflow command; standard mode should stay close to native implementation and verification.

Compression: per SKILL.md enforced mapping — `/caveman lite` for `--fast`, `/caveman full` for `--standard`, `/caveman full` (escalate to `ultra` if subagent≥3) for `--deep`. Wrap large test/build output with `rtk gain`.

## Phase 0: Brainstorm (auto-triggered when requirements unclear)

If the feature description does not name specific files, classes, and expected behavior, enter clarification phase first:
- **Product direction unclear** ("what to build") → `skill(name="gsd-explore")`
- **Technical approach unclear** ("how to build") → `/tool-research --quick`
- **Multiple viable paths for architecture** → `/tool-research --deep`, then `/tool-plan --deep` if the decision must drive implementation order

Before implementing, search claude-mem for related prior decisions and patterns:
- `npx claude-mem search "<feature_keywords>"` for cross-session context on similar work.

Route result to the appropriate cost mode below. Do not implement until direction is clear.

## Cost Modes

- `--fast`: known area, small feature → confirm pattern → implement → tests → caveman review.
- `--standard` or default: normal feature, 3-8 files → targeted CRG context → implement → native tests/build → light review. Use OpenSpec only when acceptance must persist as files.
- `--deep`: ambiguous, external deps, multi-system, or milestone-scale → add OpenSpec/ECC/GSD deliberately.

## Flow

0. Record baseline: run `/caveman-stats` (L2) to capture session starting token count.
   Before editing, verify you are not on `main`/`master`; if you are, run `/tool-branch create feat <description>` first.
1. Explore via code-review-graph (L2, auto-refreshed):
   - `get_architecture_overview` for high-level structure and module boundaries
   - `semantic_search_nodes(query="<similar_feature_or_pattern>")` to find existing implementations
   - `query_graph(imports_of="<target_module>")` to understand dependencies
   If CRG MCP tools are unavailable in the current harness, use `code-review-graph` CLI or fall back to targeted Glob/Grep/Read.
   Use existing project patterns plus `docs/language-reference.md` to choose project-native verification and implementation conventions.
2. Search existing code for matching patterns before adding new structure.
3. **Shortcut**: If the feature description already names specific files, classes, and expected behavior, skip Phase 0 and go directly to implement → verify.
4. If requirements are unclear (less than specific files+classes+behavior), run **Phase 0: Brainstorm** above.
5. If acceptance criteria need durable agreement, create or update OpenSpec proposal/spec/task artifacts through the repository's OpenSpec workflow. Do not run `openspec init` automatically from this command.
6. Implement using project conventions.
7. Run diagnostics, related tests, typecheck/build. Wrap large test/build output with `rtk gain`.
8. Run `/caveman-stats` (L2) to report session token consumption and savings.
   For `--standard` features, use `/tool-review --fast` after implementation.
   For `--deep` features, skip `/tool-review` (GSD gates handle review in completion pipeline).

## Completion Gate

### `--fast`
8. Run project-native test/build → `/tool-review --fast` or Caveman-compressed sanity check → report. Done.

### `--standard`
9. Run project-native verification against the requirement or OpenSpec tasks/specs.
10. `/tool-review --fast` or a Caveman-compressed diff sanity check.
11. Offer `/caveman-commit` suggestion (do NOT auto-commit without user request).

### `--deep`
9. `skill(name="gsd-verify-work")` — structured acceptance verification against plan/spec.
10. `skill(name="gsd-code-review")` — phase-scoped review with severity-classified findings.
11. `skill(name="gsd-ship")` — create PR, run review gates, prepare for merge.
12. Offer `/caveman-commit` suggestion.

## Security Gate

If change touches auth, user input, file system, network, secrets, cookies, or SQL, promote it to a security-sensitive route and add `/tool-review --deep` before completion.

## Skill Routing

Use project-native skills and commands from `docs/language-reference.md` instead of loading broad skill sets by default.
Escalate to superpowers, ECC, OpenSpec, or GSD only when the feature cannot remain decision-light and still be implemented safely.
