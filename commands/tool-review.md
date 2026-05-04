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

Compression: Caveman review mode for `--fast`, `/caveman full` by default, `/caveman ultra` for deep summaries. Wrap large diff/log commands with `rtk gain`.

## Cost Modes

- `--fast`: quick sanity check or small local diff → `skill(name="caveman-review")`.
- `--standard` or default: local diff or normal PR → code-review-graph assisted analysis → `skill(name="coding-standards")` (by language) → `/code-review` or `/review-pr $ARGUMENTS`.
- `--deep`: major implementation, security, broad refactor → `skill(name="security-review")` (if security-sensitive) → `/review-work`.

## Flow

1. Select local, PR, or post-implementation mode from the input.
2. Code-review-graph (L2, auto-refreshed):
   - `detect_changes` for risk-scored diff analysis
   - `get_review_context(changes="<diff>")` for token-efficient review snippets
   - `get_impact_radius(target="<changed_module>")` for blast-radius detection
3. For PR review with `--standard` or `--deep`: use `skill(name="github-ops")` to manage PR lifecycle (review comments, merge status, CI checks).
4. Review for correctness, regressions, security, and maintainability.
5. Fix critical/high findings surgically.
6. Re-run the same or stronger review mode until clean.
7. Post-review: use `skill(name="receiving-code-review")` to apply feedback when review results return.
8. Review findings auto-captured to claude-mem for cross-session pattern detection.

## Security-Sensitive Code

Route to `skill(name="security-review")` or `skill(name="security-scan")` based on scope.
