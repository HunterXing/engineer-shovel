---
description: Bug fix workflow — reproduce, isolate, fix, verify, and prevent regression
argument-hint: [--fast|--standard|--deep] [bug description | error message]
cost-profile: variable
risk-level: variable
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Edit, Bash, Task]
escalates-to: [/tool-review, /tool-plan]
depends-on: []
when-to-use: Use when behavior is broken, tests fail, logs show regressions, or root cause must be proven before fixing.
---

# /tool-fix — Bug Fixing

**Input**: $ARGUMENTS

Start with the cheapest path that can prove the bug is fixed. This is a main workflow command; escalate only when reproduction or root cause is unclear.

Shared policy: mode mapping, security gate, and completion pipeline come from `SKILL.md`; capability-layer roles and escalation rules live in `docs/architecture.md`. Wrap large test/log output with `rtk gain`.

## Cost Modes

- `--fast`: known file/function, obvious cause → confirm location → direct fix + targeted test.
- `--standard` or default: reproducible bug, local scope → CRG trace + surgical fix + failing test + regression verification + light review.
- `--deep`: flaky, cross-module, security, or unknown root cause → escalate deliberately per `docs/architecture.md`.

## Flow

0. Code-review-graph (L2) is auto-refreshed by git hooks. Verify freshness inline.
1. Reproduce or identify the failing assertion/log.
2. Search claude-mem for similar bug history when the failure looks familiar or cross-session context matters.
3. Trace the error call chain through CRG:
   - `semantic_search_nodes(query="<failing_function>")` to locate the entry point
   - `get_affected_flows(entry_point="<node_id>")` to trace the full execution path
   - `query_graph(callers_of="<suspected_root>", depth=2)` to confirm upstream dependencies
   If CRG MCP tools are unavailable in the current harness, use `code-review-graph detect-changes/status` where possible or fall back to targeted Glob/Grep/Read.
4. `get_impact_radius(target="<root_cause_node>")` to check blast radius before fixing.
5. Apply a surgical fix.
6. Run the failing test first, then related tests/build. Wrap large test output with `rtk gain`.
7. `query_graph(tests_for="<fixed_node>")` to verify test coverage exists for the fix.
8. Re-run project-native test/build, then use `/tool-review --fast` for standard work. Deep-mode verify/review/ship stays in the shared completion pipeline from `SKILL.md`.

## Security Gate

If change touches auth, user input, file system, network, secrets, cookies, or SQL, promote it to a security-sensitive route and add `/tool-review --deep` before completion.

## Escalation Rules

- Single-line typo: use `/tool-quick` instead.
- Cross-file state, external systems, or unclear ownership: use `--deep`.
- Do not start with GSD or deep research unless evidence says the normal path is insufficient.
- If systematic debugging fails 3+ times, stop iterating locally and move to `/tool-plan --deep` to reassess architecture or ownership.
