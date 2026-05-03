# Engineer Shovel Workflows

This document is the long-form reference for the `/tool-*` commands. Keep runtime prompts short; use this file for documentation and maintenance.

## `/tool-quick`

Use for obvious, low-risk work: typo fixes, config changes, simple renames, or 1-2 file edits.

Default path: code-review-graph context (auto-refreshed) → execute inline → run targeted verification with `rtk gain` → report.

## `/tool-fix`

Use for broken behavior, failing tests, or regressions.

Cost routing:
- `--fast`: known file/function, clear cause → code-review-graph trace → direct fix.
- `--standard`: reproduce → code-review-graph trace → fix → impact analysis → regression tests.
- `--deep`: flaky, cross-file, security-sensitive → ecc:deep-research → systematic-debugging → gsd-debug → security-review.

Unified verification gate: test → graph impact → caveman review.

Security gate: if touching auth/input/secrets/network/sql → add `/security-review` regardless of mode.

## `/tool-feat`

Use for new functionality. Auto-brainstorms when requirements are unclear.

Cost routing:
- `--fast`: small feature in known location → code-review-graph explore → implement.
- `--standard`: code-review-graph explore → skip brainstorm if specific files named → implement → verify.
- `--deep`: multi-component or ambiguous → brainstorm (gsd-explore / superpowers:brainstorming / ecc:council) → implement → ecc:review-work.

Unified verification gate: test → graph impact → caveman review.

Security gate: if touching auth/input/secrets → add `/security-review`.

## `/tool-plan`

Unified planning entry point. Auto-escalates to blueprint or GSD project.

Cost routing:
- `--fast`: small task, clear scope → inline plan → route to quick/feat.
- `--standard`: brainstorm if needed → superpowers:writing-plans.
- `--deep`: auto-classify → ecc:blueprint (≤3 PR) or gsd project (milestone) or council (architecture).

## `/tool-refactor`

Use when external behavior must remain unchanged.

Required pattern:
1. Establish baseline tests/build. Call `rtk gain` before test runs.
2. Code-review-graph impact analysis (auto-refreshed).
3. Make one logical refactor at a time.
4. Re-run verification after each step.
5. `--deep`: mandatory gsd-execute-phase + ecc:review-work.

Unified verification gate: all tests pass → graph impact clean → caveman review.

Security gate: if touching auth/security paths → add `/security-review`.

## `/tool-review`

Modes:
- `--fast`: Caveman-compressed review for routine local diffs.
- default: code-review-graph assisted review + ecc:coding-standards + ecc:github-ops for PRs.
- `--deep`: post-implementation review with `/review-work` (5-agent parallel).

Post-review: superpowers:receiving-code-review for feedback application.

## `/tool-research`

Codebase-aware research with code-review-graph context.

Modes:
- `--quick`: local docs + code-review-graph architecture context.
- `--web`: add current web/docs search + code-review-graph context.
- `--deep`: multi-source research with ecc:deep-research + code-review-graph exploration.

## `/tool-graph`

**Diagnostic only.** The code-review-graph is auto-refreshed via git hooks (post-commit, post-checkout). Use this command only for manual inspection or troubleshooting.

Modes:
- `status`: show install and graph health.
- `build`: full initial graph build.
- `update`: manual refresh (only if hooks not active).
- `rebuild`: full refresh for stale or damaged graphs.
- `watch`: explain or start continuous graph updates.

## `/tool-brainstorm` — DEPRECATED

Brainstorming is now built into `/tool-feat` and `/tool-plan` as Phase 0. Use those commands directly — they auto-detect when clarification is needed.

## `/tool-blueprint` — DEPRECATED

Multi-step project planning is now part of `/tool-plan --deep`. It auto-classifies complexity and escalates to `ecc:blueprint` or `gsd project`.

## `/tool-branch`

Branch lifecycle management (called automatically by feat/fix).

Subcommands:
- `create [type] <description>`: Create branch from current with auto-detected type.
- `status`: Show branch info and diff stats vs source.
- `review`: Show full diff + code-review-graph assisted analysis.
- `merge`: Squash merge to source branch, prompt for commit message, delete branch.
- `abort`: Discard branch and return to source.

## `/tool-update`

Sync Engineer Shovel files and verify component health.

Modes:
- `--check`: read-only comparison + health check.
- `--full`: overwrite files + install missing components.
