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

Compression: follow `docs/token-cost.md`; default to `/caveman full`, lite for `--fast`, and RTK for logs/tests/traces.

## Cost Modes

- `--fast`: known file/function, obvious cause → direct fix + targeted test.
- `--standard` or default: reproducible bug, local scope → reproduce → inspect related code → fix → regression test.
- `--deep`: flaky, cross-module, security, or unknown root cause → `/gsd-debug` and optional Oracle after failed attempts.

## Flow

1. Reproduce or identify the failing assertion/log.
2. Find the smallest root cause, not just the symptom.
3. Apply a surgical fix.
4. Run the failing test first, then related tests/build.
5. Add regression coverage when the project has a suitable test pattern.

## Escalation Rules

- Single-line typo: use `/tool-quick` instead.
- Cross-file state or architecture issue: use `--deep`.
- Security vulnerability: add `/security-review` and `/security-scan` before finalizing.
