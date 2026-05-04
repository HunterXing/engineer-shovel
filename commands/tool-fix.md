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

Compression: per SKILL.md enforced mapping — `/caveman lite` for `--fast`, `/caveman full` for `--standard`, `/caveman full` (escalate to `ultra` if subagent≥3) for `--deep`. Wrap large test/log output with `rtk gain`.

## Cost Modes

- `--fast`: known file/function, obvious cause → `semantic_search_nodes` to confirm location → direct fix + targeted test.
- `--standard` or default: reproducible bug, local scope → full CRG trace pipeline (semantic_search → get_affected_flows → query_graph) → fix → gsd-verify-work.
- `--deep`: flaky, cross-module, security, or unknown root cause → CRG trace pipeline → `skill(name="deep-research")` if unfamiliar domain → `skill(name="systematic-debugging")` (superpowers, 4-phase) → `skill(name="gsd-debug")` if persistent state needed → `skill(name="security-review")`.

## Flow

0. Code-review-graph (L2) is auto-refreshed by git hooks. Verify freshness inline.
1. Reproduce or identify the failing assertion/log.
2. Trace the error call chain through CRG:
   - `semantic_search_nodes(query="<failing_function>")` to locate the entry point
   - `get_affected_flows(entry_point="<node_id>")` to trace the full execution path
   - `query_graph(callers_of="<suspected_root>", depth=2)` to confirm upstream dependencies
3. `get_impact_radius(target="<root_cause_node>")` to check blast radius before fixing.
4. Apply a surgical fix.
5. Run the failing test first, then related tests/build. Wrap large test output with `rtk gain`.
6. `query_graph(tests_for="<fixed_node>")` to verify test coverage exists for the fix.
7. **Verification Gate**: run project-native test/build → graph impact check clean → proceed to completion gate.

## Completion Gate

### `--fast`
8. Run project-native test/build. Report: what changed, what was verified. Done.

### `--standard`
8. `skill(name="gsd-verify-work")` — confirm the bug is fixed and no regression introduced.
9. `skill(name="caveman-review")` — compressed code quality check on the diff.
10. Offer `/caveman-commit` suggestion (do NOT auto-commit without user request).

### `--deep`
8. `skill(name="gsd-verify-work")` — structured acceptance verification against bug report.
9. `skill(name="gsd-code-review")` — phase-scoped review with severity-classified findings.
10. `skill(name="gsd-ship")` — create PR, run review gates, prepare for merge.
11. Offer `/caveman-commit` suggestion.

## Security Gate

If change touches auth, user input, file system, network, secrets, cookies, or SQL → escalate to `skill(name="security-review")`.

## Escalation Rules

- Single-line typo: use `/tool-quick` instead.
- Cross-file state or architecture issue: use `--deep`.
- If systematic debugging fails 3+ times → question architecture, not hypothesis.
