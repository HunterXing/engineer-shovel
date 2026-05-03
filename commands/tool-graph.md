---
description: Code graph workflow — manage code-review-graph build, update, rebuild, status, and watch modes
argument-hint: [status|build|update|rebuild|watch]
cost-profile: low
risk-level: low
recommended-mode: --fast
allowed-tools: [Bash, Read, Grep]
escalates-to: [/tool-review]
depends-on: []
when-to-use: Use when manually refreshing or inspecting the code-review-graph index for review and impact analysis.
---

# /tool-graph — Code Review Graph

**Input**: $ARGUMENTS

Manage the local `code-review-graph` index used for review context, blast-radius analysis, and token-efficient code navigation.

## Commands

- `status` or default: Check whether `code-review-graph` is installed, show graph status, and report whether `.code-review-graph/` exists.
- `build`: Run `code-review-graph build` for first-time full graph creation.
- `update`: Run `code-review-graph update` for incremental refresh after code changes.
- `rebuild`: Run a full rebuild when the graph is stale or damaged. Prefer `code-review-graph build`; do not delete `.code-review-graph/` unless the user explicitly approves.
- `watch`: Start or explain `code-review-graph watch` / `crg-daemon` for continuous updates. Do not leave a background daemon running without user approval.

## Flow

1. Verify `code-review-graph` exists; if missing, tell the user to run `./install.sh --full` or `pipx install code-review-graph && code-review-graph install`.
2. For `status`, run `code-review-graph status` when available and summarize graph health.
3. For `build`, run `code-review-graph build` and report success or the exact failure.
4. For `update`, run `code-review-graph update` and treat failure as actionable, not silent.
5. For `rebuild`, prefer the upstream rebuild path; ask before deleting local graph storage.

## Integration

- `/tool-review` should refresh the graph before deep review when the tool is installed.
- `/tool-branch review` and `/tool-branch merge` should update the graph before impact analysis.
- Full installer mode should run `code-review-graph install` and an initial `code-review-graph build` when possible.
