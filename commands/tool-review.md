---
description: Code review workflow — fast, standard, or deep review by risk
argument-hint: [--fast|--standard|--deep] [pr-number | pr-url | blank for local review]
---

# /tool-review — Code Review

**Input**: $ARGUMENTS

Choose the cheapest review mode that can catch the relevant failure class.

Compression: `--fast` should use Caveman review style; default to `/caveman full`; use `/caveman ultra` for deep review summaries. Use RTK for diff/log-producing shell commands.

## Cost Modes

| Mode | Use when | Command |
|---|---|---|
| `--fast` | quick sanity check or small local diff | `/caveman:caveman-review` |
| `--standard` or default | local diff or normal PR | `/code-review` or `/review-pr $ARGUMENTS` |
| `--deep` | major implementation, security, broad refactor | `/review-work` |

## Flow

1. Select local, PR, or post-implementation mode from the input.
2. Review for correctness, regressions, security, and maintainability.
3. Fix critical/high findings surgically.
4. Re-run the same or stronger review mode until clean.

## Security-Sensitive Code

Add `/security-review` and `/security-scan` before approval.
