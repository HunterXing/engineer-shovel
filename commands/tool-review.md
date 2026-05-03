---
description: Code review workflow — fast, standard, or deep review by risk
argument-hint: [--fast|--standard|--deep] [pr-number | pr-url | blank for local review]
cost-profile: variable
risk-level: variable
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Bash, Task]
escalates-to: [/review-work, /security-review, /security-scan]
depends-on: []
when-to-use: Use for local diffs, pull requests, or post-implementation review where risk determines review depth.
---

# /tool-review — Code Review

**Input**: $ARGUMENTS

Choose the cheapest review mode that can catch the relevant failure class.

Compression: Caveman review style for `--fast`, full by default, ultra for deep summaries. Call `rtk gain` before diff/log commands.

## Cost Modes

- `--fast`: quick sanity check or small local diff → `/caveman:caveman-review`.
- `--standard` or default: local diff or normal PR → code-review-graph assisted analysis (L2, auto-refreshed) → L4: `ecc:coding-standards` (by language) → `/code-review` or `/review-pr $ARGUMENTS`.
- `--deep`: major implementation, security, broad refactor → L4: `ecc:security-review` (if security-sensitive) → `/review-work`.

## Flow

1. Select local, PR, or post-implementation mode from the input.
2. Code-review-graph (L2, auto-refreshed): use graph for diff analysis, blast-radius detection.
3. For PR review with `--standard` or `--deep`: use L4: `ecc:github-ops` to manage PR lifecycle (review comments, merge status, CI checks).
4. Review for correctness, regressions, security, and maintainability.
5. Fix critical/high findings surgically.
6. Re-run the same or stronger review mode until clean.
7. Post-review: use L5: `superpowers:receiving-code-review` to apply feedback when review results return.

## Security-Sensitive Code

Apply Decision Tree 4 from `docs/decision-trees.md`: evaluate scope → route to L4: `ecc:security-review` or `ecc:security-scan`.
