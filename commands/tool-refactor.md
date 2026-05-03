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

Compression: caveman full by default, lite for `--fast`, ultra for broad diffs. Call `rtk gain` before test/build commands.

## Cost Modes

- `--fast`: 1-2 file cleanup → baseline tests → refactor → verify → `/tool-review --fast`.
- `--standard` or default: normal refactor → baseline tests → refactor (small steps) → tests/build → local review.
- `--deep`: broad, risky, security-sensitive, or performance-critical → L6: `gsd-execute-phase` (mandatory phase management) → L4: `ecc:review-work` + E2E if applicable.

## Flow

1. Run baseline tests before any edits. Call `rtk gain` before test runs.
2. Code-review-graph (L2, auto-refreshed): use impact analysis to understand affected callers before refactoring. Also identify existing codebase patterns for reference.
3. Refactor one logical unit at a time.
4. Re-run the same verification after each step.
5. Compare behavior, public APIs, and performance-sensitive paths.
6. **Verification Gate**: confirm all tests pass → graph impact check clean → caveman review → report.

## Security Gate

If the change touches auth, security-sensitive paths, or data handling, add L4: `ecc:security-review` regardless of cost mode.

## Stop Conditions

- If baseline tests fail, switch to `/tool-fix` first.
- If behavior changes are required, split that work into `/tool-feat`.
