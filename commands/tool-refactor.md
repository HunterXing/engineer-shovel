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

Compression: use `/caveman full`; switch to `/caveman ultra` for broad diffs or long verification output. Use RTK for git diff, tests, and build logs when available.

## Cost Modes

| Mode | Use when | Review path |
|---|---|---|
| `--fast` | 1-2 file cleanup | targeted tests + `/tool-review --fast` |
| `--standard` or default | normal refactor | baseline tests → refactor → tests/build → local review |
| `--deep` | broad, risky, security-sensitive, or performance-critical | `/refactor` + `/review-work` + E2E if applicable |

## Flow

1. Run baseline verification before edits.
2. Refactor one logical unit at a time.
3. Re-run the same verification after edits.
4. Compare behavior, public APIs, and performance-sensitive paths.
5. Escalate review only when the risk justifies the agent cost.

## Stop Conditions

- If baseline tests fail, switch to `/tool-fix` first.
- If behavior changes are required, split that work into `/tool-feat`.
