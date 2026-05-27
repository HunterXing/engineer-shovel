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
standalone: true
---

# /tool-fix — Bug Fixing

**Input**: $ARGUMENTS

Start with the cheapest path that can prove the bug is fixed. This is a main workflow command; escalate only when reproduction or root cause is unclear.

## Shared Policies

See `commands/_shared.md` for:
- **Cost Modes** — fast/standard/deep with smart mode auto-detection
- **Security Gate** — auth/network/SQL/secrets → auto-promote to --deep
- **Toolchain Announcements** — 🚀 format for external tools
- **Completion Pipeline** — standard/deep verification steps
- **Error Recovery** — fallback and escalation strategies

## Command-Specific Logic

### Smart Mode

- Bug with clear repro → `--fast` or `--standard`
- Bug without repro → `--standard`
- Cross-module/security → `--deep`

### Flow

0. Code-review-graph (L2) is auto-refreshed by git hooks. Verify freshness inline.
1. Reproduce or identify the failing assertion/log.
2. Search claude-mem for similar bug history when the failure looks familiar or cross-session context matters. → announce: `🚀 **claude-mem** → searching for similar bug history`
3. If the bug crosses files, ownership, or call paths, trace the error chain through CRG:
   - `semantic_search_nodes(query="<failing_function>")` → announce: `🚀 **code-review-graph** → locating <function>`
   - `get_affected_flows(entry_point="<node_id>")` → announce: `🚀 **code-review-graph** → tracing execution flow`
   - `query_graph(callers_of="<suspected_root>", depth=2)` → announce: `🚀 **code-review-graph** → analyzing callers`
4. If the bug is local and obvious, skip graph work and go straight to the failing file plus targeted verification.
5. When root cause is still unclear after reproduction, upgrade method rather than broadening scope:
   - use `superpowers` / systematic debugging → announce: `🚀 **superpowers** → loading systematic-debugging skill`
   - use ECC only if the failure depends on framework behavior, security rules, or external integration specifics → announce: `🚀 **ECC** → loading <domain> guidance`
6. `get_impact_radius(target="<root_cause_node>")` → announce: `🚀 **code-review-graph** → checking blast radius`
7. Apply a surgical fix.
8. Run the failing test first, then related tests/build. Wrap large test output with `rtk gain` → announce: `🚀 **rtk** → wrapping test output`
9. `query_graph(tests_for="<fixed_node>")` → announce: `🚀 **code-review-graph** → verifying test coverage`
10. Re-run project-native test/build, then use `/tool-review --fast` for standard work.

### Error Handling

- If reproduction fails, ask for more details or a minimal reproducible example.
- If the fix introduces new failures, revert and reassess the approach.
- If 3+ fix attempts fail, stop and escalate to `/tool-plan --deep` for architectural review.
- Always verify the fix doesn't break existing functionality.

### Escalation Rules

- Single-line typo: use `/tool-quick` instead.
- Cross-file state, external systems, or unclear ownership: use `--deep`.
- Prefer `superpowers` for debugging discipline before escalating into broad research.
- Prefer `ECC` only for framework, security, or integration knowledge gaps.
- If systematic debugging fails 3+ times, stop iterating locally and move to `/tool-plan --deep`.
