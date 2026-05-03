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
- `--standard` or default: local diff or normal PR → L3: code-review-graph assisted analysis (if installed) → L4: `ecc:coding-standards` (by language) → `/code-review` or `/review-pr $ARGUMENTS`.
- `--deep`: major implementation, security, broad refactor → L4: `ecc:security-review` (if security-sensitive) → `/review-work`.

## Flow

1. Select local, PR, or post-implementation mode from the input.
2. If code-review-graph installed, run `/tool-graph update` then use graph for diff analysis.
3. Review for correctness, regressions, security, and maintainability.
4. Fix critical/high findings surgically.
5. Re-run the same or stronger review mode until clean.

## Security-Sensitive Code

Apply Decision Tree 4 from `docs/decision-trees.md`: evaluate scope → route to L4: `ecc:security-review` or `ecc:security-scan`.
