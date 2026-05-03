# Engineer Shovel Workflows

This document is the long-form reference for the 12 `/tool-*` commands. Keep runtime prompts short; use this file for documentation and maintenance.

## `/tool-quick`

Use for obvious, low-risk work: typo fixes, config changes, simple renames, or 1-2 file edits.

Default path: execute inline, run targeted verification. Call `rtk gain` before test/build output.

## `/tool-fix`

Use for broken behavior, failing tests, or regressions.

Cost routing:
- `--fast`: known file/function, clear cause, direct fix.
- `--standard`: reproduce → code-review-graph trace → fix → impact analysis → regression tests.
- `--deep`: cross-file, flaky, security-sensitive → gsd-debug + systematic-debugging + security-review.

Security gate: if touching auth/input/secrets/network/sql → add `/security-review` regardless of mode.

## `/tool-feat`

Use for new functionality.

Cost routing:
- `--fast`: small feature in known location → code-review-graph explore → implement.
- `--standard`: code-review-graph explore → implement (skip brainstorm if feature is clearly described).
- `--deep`: multi-component or ambiguous → brainstorm → plan → blueprint if needed.

Security gate: if touching auth/input/secrets → add `/security-review`.

## `/tool-branch`

Use for managing feature branch lifecycle with squash merge and diff review.

Subcommands:
- `create [type] <description>`: Create branch from current with auto-detected type (feat/fix/refactor/docs).
- `status`: Show branch info and diff stats vs source.
- `review`: Show full diff + code-review-graph assisted analysis.
- `merge`: Squash merge to source branch, prompt for commit message, delete branch.
- `abort`: Discard branch and return to source.

## `/tool-plan`

Use before implementation when requirements, dependencies, or verification criteria are unclear.

Planning paths (pick one, not both):
- Product direction unclear → `gsd-explore`
- Technical approach unclear → `superpowers:brainstorming`
- Then: ≤3 PR → `writing-plans` | >3 PR → `/tool-blueprint`

## `/tool-refactor`

Use when external behavior must remain unchanged.

Required pattern:
1. Establish baseline tests/build. Call `rtk gain` before test runs.
2. If code-review-graph installed, check impact before refactoring.
3. Make one logical refactor at a time.
4. Re-run verification after each step.
5. Review using the cheapest mode that fits risk.

Security gate: if touching auth/security paths → add `/security-review`.

## `/tool-review`

Modes:
- `--fast`: Caveman-compressed review for routine local diffs.
- default: code-review-graph assisted review for PRs.
- `--deep`: post-implementation review with `/review-work` (5-agent parallel).

## `/tool-brainstorm`

Use when the idea is not implementation-ready. Capture the decision and route to quick, feature, plan, research, or backlog.

Paths:
- Product direction → `gsd-explore`
- Technical approach → `superpowers:brainstorming`

## `/tool-blueprint`

Use for multi-step projects, multi-session work, or changes that need dependency ordering.

Paths:
- Code-centric multi-PR → `ecc:blueprint`
- Milestone-scale engineering → `gsd project`

## `/tool-research`

Modes:
- `--quick`: local docs and known references.
- `--web`: add current web/docs search.
- `--deep`: multi-source research with deep-research.

## `/tool-graph`

Manage the `code-review-graph` index.

Modes:
- `status`: show install and graph health.
- `build`: full initial graph build.
- `update`: incremental graph refresh after code changes.
- `rebuild`: full refresh for stale or damaged graphs.
- `watch`: explain or start continuous graph updates.

Integration: other commands use graph implicitly for exploring, debugging, impact analysis, and review.

## `/tool-update`

Sync Engineer Shovel files and verify component health.

Modes:
- `--check`: read-only comparison + health check.
- `--full`: overwrite files + install missing components.
