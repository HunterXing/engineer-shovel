---
description: Refactoring workflow — preserve behavior, verify before and after
argument-hint: [--fast|--standard|--deep] [refactoring goal]
cost-profile: medium
risk-level: medium
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Edit, Bash, Task]
escalates-to: [/tool-plan, /tool-fix, /tool-review]
depends-on: []
when-to-use: Use for behavior-preserving cleanup where baseline and post-change verification can prove equivalence.
---

# /tool-refactor — Refactoring

**Input**: $ARGUMENTS

Behavior must remain identical. Do not mix feature work into a refactor. This is an engineering support command, not the default path for ordinary feature work.

Shared policy: mode mapping, security gate, and completion behavior come from `SKILL.md`; escalation rules live in `docs/architecture.md`. Wrap large test/build commands with `rtk gain`.

## Cost Modes

- `--fast`: 1-2 file cleanup → baseline tests → refactor → verify → `/tool-review --fast`.
- `--standard` or default: normal refactor → baseline tests → refactor (small steps) → tests/build → local review.
- `--deep`: broad, risky, security-sensitive, or performance-critical → `/tool-plan --deep` first, then add heavier layers deliberately.

## Flow

1. Run baseline tests before any edits. Wrap with `rtk gain` for large suites.
2. Search claude-mem for prior refactor rationale when historical decisions or naming context matter.
3. Code-review-graph (L2, auto-refreshed) is the default structural aid for refactor work:
   - `get_impact_radius(target="<function_or_module>")` to understand affected callers before refactoring
   - `refactor_tool` to check for dead code or plan renames safely
   - `semantic_search_nodes(query="<similar_pattern>")` to identify existing codebase patterns for reference
4. Refactor one logical unit at a time.
5. Re-run the same verification after each step.
6. Compare behavior, public APIs, and performance-sensitive paths.
7. If the work stops being behavior-preserving or grows into a broad multi-area redesign, switch to `/tool-plan --deep` before continuing.
8. **Verification Gate**: confirm all tests pass → graph impact check clean → `/tool-review --fast` or Caveman-compressed sanity check → report.

## Safety Rules

- Never mix feature work into a refactor.
- Always run baseline tests before starting.
- Refactor in small, verifiable steps.
- If tests fail at any point, stop and fix before continuing.
- Keep commits atomic and focused.

## Security Gate

If change touches auth, security-sensitive paths, or data handling, stop treating it as a routine refactor and add a `/tool-review --deep` checkpoint before sign-off.

## Stop Conditions

- If baseline tests fail, switch to `/tool-fix` first.
- If behavior changes are required, split that work into `/tool-feat`.
