---
description: Bug fix workflow — reproduce, isolate, fix, verify, and prevent regression
argument-hint: [--fast|--standard|--deep] [bug description | error message]
cost-profile: variable
risk-level: variable
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Edit, Bash, Task]
escalates-to: [/gsd-debug, /security-review, /tool-review]
depends-on: []
when-to-use: Use when behavior is broken, tests fail, logs show regressions, or root cause must be proven before fixing.
---

# /tool-fix — Bug Fixing

**Input**: $ARGUMENTS

Start with the cheapest path that can prove the bug is fixed. Escalate only when reproduction or root cause is unclear.

Compression: caveman full by default, lite for `--fast`, ultra for `--deep`. Call `rtk gain` before test/log commands.

## Cost Modes

- `--fast`: known file/function, obvious cause → code-review-graph trace (L2, auto-refreshed) → direct fix + targeted test.
- `--standard` or default: reproducible bug, local scope → graph-assisted tracing → fix → regression test.
- `--deep`: flaky, cross-module, security, or unknown root cause → L4: `ecc:deep-research` (if flaky/new domain) → L5: `superpowers:systematic-debugging` (4-phase) → L6: `gsd-debug` and L4: `ecc:security-review`.

## Flow

0. Code-review-graph (L2) is auto-refreshed by git hooks. Verify freshness inline.
1. Reproduce or identify the failing assertion/log.
2. Use code-review-graph tracing to trace the error call chain and narrow root cause.
3. Find the smallest root cause, not just the symptom.
4. Apply a surgical fix.
5. Run the failing test first, then related tests/build. Call `rtk gain` before each test run.
6. Use code-review-graph impact analysis to verify no callers broken by the fix.
7. Add regression coverage when the project has a suitable test pattern.
8. **Verification Gate**: run project-native test/build → graph impact check → caveman review → report.

## Security Gate

If the change touches auth, user input parsing, file system, network, secrets, cookies, or SQL, add L4: `ecc:security-review` regardless of cost mode.

## Escalation Rules

- Single-line typo: use `/tool-quick` instead.
- Cross-file state or architecture issue: use `--deep`.
- If systematic debugging fails 3+ times → question architecture, not hypothesis.
