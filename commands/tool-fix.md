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
3. If the bug crosses files, ownership, or call paths, trace the error chain through CRG:
   - `semantic_search_nodes(query="<failing_function>")` to locate the entry point
   - `get_affected_flows(entry_point="<node_id>")` to trace the full execution path
   - `query_graph(callers_of="<suspected_root>", depth=2)` to confirm upstream dependencies
   If CRG MCP tools are unavailable in the current harness, use `code-review-graph detect-changes/status` where possible or fall back to targeted Glob/Grep/Read.
4. If the bug is local and obvious, skip graph work and go straight to the failing file plus targeted verification.
5. When root cause is still unclear after reproduction, upgrade method rather than broadening scope:
   - use `superpowers` / systematic debugging for structured root-cause isolation
   - use ECC only if the failure depends on framework behavior, security rules, or external integration specifics
6. `get_impact_radius(target="<root_cause_node>")` to check blast radius before fixing when the change is cross-file.
7. Apply a surgical fix.
8. Run the failing test first, then related tests/build. Wrap large test output with `rtk gain`.
9. `query_graph(tests_for="<fixed_node>")` to verify test coverage exists for the fix when CRG is already in use.
10. Re-run project-native test/build, then use `/tool-review --fast` for standard work. Deep-mode verify/review/ship stays in the shared completion pipeline from `SKILL.md`.

## Security Gate

If change touches auth, user input, file system, network, secrets, cookies, or SQL, promote it to a security-sensitive route and add `/tool-review --deep` before completion.

## Escalation Rules

- Single-line typo: use `/tool-quick` instead.
- Cross-file state, external systems, or unclear ownership: use `--deep`.
- Prefer `superpowers` for debugging discipline before escalating into broad research.
- Prefer `ECC` only for framework, security, or integration knowledge gaps.
- Do not start with GSD or deep research unless evidence says the normal path is insufficient.
- If systematic debugging fails 3+ times, stop iterating locally and move to `/tool-plan --deep` to reassess architecture or ownership.
