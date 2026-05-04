---
description: Refactoring workflow — preserve behavior, verify before and after
argument-hint: [--fast|--standard|--deep] [refactoring goal]
cost-profile: medium
risk-level: medium
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Edit, Bash, Task]
escalates-to: [/review-work, /tool-fix, /tool-review]
depends-on: []
when-to-use: Use for behavior-preserving cleanup where baseline and post-change verification can prove equivalence.
---

# /tool-refactor — Refactoring

**Input**: $ARGUMENTS

Behavior must remain identical. Do not mix feature work into a refactor.

Compression: `/caveman full` by default, `/caveman lite` for `--fast`, `/caveman ultra` for broad diffs (per SKILL.md mapping). Wrap large test/build commands with `rtk gain`.

## Cost Modes

- `--fast`: 1-2 file cleanup → baseline tests → refactor → verify → `/tool-review --fast`.
- `--standard` or default: normal refactor → baseline tests → refactor (small steps) → tests/build → local review.
- `--deep`: broad, risky, security-sensitive, or performance-critical → `/tool-plan --deep` first (OpenSpec/blueprint/GSD as appropriate) → execute in small verified steps → `skill(name="review-work")` + E2E if applicable.

## Flow

1. Run baseline tests before any edits. Wrap with `rtk gain` for large suites.
2. Code-review-graph (L2, auto-refreshed):
   - `get_impact_radius(target="<function_or_module>")` to understand affected callers before refactoring
   - `refactor_tool` to check for dead code or plan renames safely
   - `semantic_search_nodes(query="<similar_pattern>")` to identify existing codebase patterns for reference
3. Refactor one logical unit at a time.
4. Re-run the same verification after each step.
5. Compare behavior, public APIs, and performance-sensitive paths.
6. **Verification Gate**: confirm all tests pass → graph impact check clean → caveman review → report.

## Security Gate

If change touches auth, security-sensitive paths, or data handling → escalate to `skill(name="security-review")`.

## Stop Conditions

- If baseline tests fail, switch to `/tool-fix` first.
- If behavior changes are required, split that work into `/tool-feat`.
