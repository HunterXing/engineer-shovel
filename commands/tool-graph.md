---
description: Code graph diagnostic tool — inspect and manually manage the auto-refreshed code-review-graph
argument-hint: [status|build|update|rebuild|watch]
cost-profile: low
risk-level: low
recommended-mode: --fast
allowed-tools: [Bash, Read, Grep]
escalates-to: [/tool-review]
depends-on: []
when-to-use: Use ONLY for manual diagnostics. The code-review-graph is auto-refreshed via git hooks for all other commands — no manual update needed during normal workflows.
---

# /tool-graph — Code Review Graph (Diagnostic)

**Input**: $ARGUMENTS

Diagnostic commands for the code-review-graph index. **All other `/tool-*` commands use the graph automatically** — you do NOT need to call `/tool-graph update` manually during normal workflows. The graph is auto-refreshed by git post-commit/post-checkout hooks.

## Commands

- `status` or default: Check whether `code-review-graph` is installed, show graph health, report `.code-review-graph/` state.
- `build`: Run `code-review-graph build` for first-time full graph creation.
- `update`: Run `code-review-graph update` manually. Only needed if auto-refresh hooks are not active.
- `rebuild`: Full rebuild when the graph is stale or damaged.
- `watch`: Explain `code-review-graph watch` / `crg-daemon` for continuous updates.

## Flow

1. Verify `code-review-graph` exists; if missing, tell the user to run `./install.sh --full` or `pipx install code-review-graph && code-review-graph install`.
2. For `status`, run `code-review-graph status` and summarize graph health.
3. For `build`, run `code-review-graph build` and report success or failure.
4. For `update`, run `code-review-graph update` and treat failure as actionable.
5. For `rebuild`, prefer the upstream rebuild path; ask before deleting local graph storage.

## Auto-Refresh Integration

The graph is automatically kept fresh by git hooks configured at install time:
- `post-commit` → `code-review-graph update`
- `post-checkout` → `code-review-graph update`

All `/tool-*` commands query the graph without manual refresh:
- `/tool-fix` → tracing + impact analysis
- `/tool-feat` → architecture exploration
- `/tool-refactor` → impact analysis + pattern reference
- `/tool-review` → diff analysis
- `/tool-research` → codebase context
- `/tool-branch review` → blast-radius analysis
