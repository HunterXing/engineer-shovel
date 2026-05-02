---
description: Quick task execution — surgical changes with minimal overhead
argument-hint: [--fast|--standard] [task description]
cost-profile: low
risk-level: low
recommended-mode: --fast
allowed-tools: [Read, Grep, Glob, Edit, Bash]
escalates-to: [/tool-fix, /tool-feat, /tool-review]
depends-on: []
when-to-use: Use for obvious low-risk work such as typos, tiny config edits, or one to two file surgical changes.
---

# /tool-quick — Quick Tasks

**Input**: $ARGUMENTS

Use this for obvious, low-risk work. Do not run planning, deep research, or broad review for quick tasks.

Compression: follow `docs/token-cost.md`; use `/caveman lite` and RTK for git/test/build noise when available.

## Cost Modes

- `--fast` or default: typo, config tweak, 1-line fix → direct edit or `/gsd-fast`.
- `--standard`: 1-2 file surgical change → cavecrew-builder or targeted edit + tests.

## Flow

1. Confirm the target file or symbol from context.
2. Make the smallest safe change.
3. Run the nearest useful verification: formatter/lint/test/build as applicable.
4. Report what changed and what passed.

## Avoid

- No `/blueprint`.
- No `/deep-research`.
- No `/review-work` unless the change unexpectedly becomes high risk.
