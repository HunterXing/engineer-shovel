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

Compression: caveman lite by default. Call `rtk gain` before tests/validation to compress tool output.

## Cost Modes

- `--fast` or default: typo, config tweak, 1-line fix → direct edit.
- `--standard`: 1-2 file surgical change → targeted edit + tests + caveman review.

## Flow

0. If code-review-graph installed, get minimal context: `get_minimal_context_tool` for the target file(s) (L3).
   If project language is known, load matching L4 ECC pattern reference from `docs/language-reference.md`.
1. Confirm the target file or symbol from context.
2. Make the smallest safe change.
3. Run the nearest useful verification: formatter/lint/test/build as applicable.
   Call `rtk gain` before noisy commands (test runs, builds, diff/log inspection).
4. Report what changed and what passed.

## Security Gate

If the change touches auth, user input parsing, file system, network, secrets, cookies, or SQL, add L4: `ecc:security-review` regardless of cost mode.

## Avoid

- No `/blueprint`.
- No `/deep-research`.
- No `/review-work` unless the change unexpectedly becomes high risk.
