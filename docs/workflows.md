# Engineer Shovel Workflows

This document is the long-form reference for the 12 `/tool-*` commands. Keep runtime prompts short; use this file for documentation and maintenance.

## `/tool-quick`

Use for obvious, low-risk work: typo fixes, config changes, simple renames, or 1-2 file edits.

Default path: execute inline, run targeted verification, then commit only if the user explicitly asked for a commit.

## `/tool-fix`

Use for broken behavior, failing tests, or regressions.

Cost routing:
- `--fast`: known file/function, clear cause, direct fix.
- `--standard`: reproduce, inspect related code, add or run regression tests.
- `--deep`: cross-file, flaky, security-sensitive, or not reproducible; use GSD debugging and optionally Oracle.

## `/tool-feat`

Use for new functionality.

Cost routing:
- `--fast`: small feature in known location.
- `--standard`: targeted exploration, plan, implement, test/build.
- `--deep`: multi-component or ambiguous feature; use blueprint/GSD phases.

## `/tool-branch`

Use for managing feature branch lifecycle with squash merge and diff review.

Subcommands:
- `create [type] <description>`: Create branch from current with auto-detected type (feat/fix/refactor/docs).
- `status`: Show branch info and diff stats vs source.
- `review`: Show full diff for review before merge.
- `merge`: Squash merge to source branch, prompt for commit message, delete branch.
- `abort`: Discard branch and return to source.

Auto-detection rules:
- fix/bug/error/broken/crash/issue/problem → `fix`
- add/new/feature/implement/support/create → `feat`
- refactor/clean/optimize/improve/restructure → `refactor`
- doc/readme/comment/typo/docs → `docs`
- Default → `feat`

Branch naming: `{type}/{slugified-description}`

## `/tool-plan`

Use before implementation when requirements, dependencies, or verification criteria are unclear.

Planning depth:
- Simple: short inline plan.
- Medium: file-backed plan with risks and verification.
- Complex: blueprint or GSD project phase plan.

## `/tool-refactor`

Use when external behavior must remain unchanged.

Required pattern:
1. Establish baseline tests/build.
2. Make one logical refactor at a time.
3. Re-run verification.
4. Review using the cheapest mode that fits risk.

Use `/review-work` only for broad or high-risk refactors.

## `/tool-review`

Modes:
- `--fast`: Caveman-compressed review for routine local diffs.
- default: local or PR review using normal review tools.
- `--deep`: post-implementation review for significant, risky, or security-sensitive work.

## `/tool-brainstorm`

Use when the idea is not implementation-ready. Capture the decision and route to quick, feature, plan, research, or backlog.

## `/tool-blueprint`

Use for multi-step projects, multi-session work, or changes that need dependency ordering. Prefer one independently verifiable step per PR.

## `/tool-research`

Modes:
- `--quick`: local docs and known references.
- `--web`: add current web/docs search.
- `--deep`: multi-source research, code examples, synthesis, and conflict analysis.

## `/tool-graph`

Use when you need to manually manage the `code-review-graph` index.

Modes:
- `status`: show install and graph health.
- `build`: full initial graph build.
- `update`: incremental graph refresh after code changes.
- `rebuild`: full refresh for stale or damaged graphs; ask before deleting graph storage.
- `watch`: explain or start continuous graph updates only with user approval.

Integration:
- Run `/tool-graph update` before deep `/tool-review` and before `/tool-branch review` or merge.
- Use `/caveman-stats` directly for Caveman session statistics.
- Use `rtk gain` directly for RTK output-compression statistics.
