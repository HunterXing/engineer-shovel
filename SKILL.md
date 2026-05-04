---
name: 工兵铲
display_name: engineer-shovel
description: |
  工兵铲 (Engineer Shovel) — token-aware AI agent development workflow router.
  Provides 8 slash commands for feature work, bug fixing, planning, refactoring,
  review, quick tasks, research, code graph diagnostics, and sync.
license: MIT
metadata:
  version: "1.5.0"
  category: workflow
  token_profile: lightweight-router
  sources:
    - superpowers plugin
    - ECC (Everything Claude Code)
    - GSD (Get Stuff Done)
    - Caveman plugin
    - rtk
    - code-review-graph
---

# 🪖 工兵铲 — Engineer Shovel

Engineer Shovel is a lightweight router for AI-assisted software engineering. It intentionally keeps this skill file short: use it to choose the right `/tool-*` command, then let the selected command carry the detailed workflow.

## Commands

| Command | Use for | Default cost |
|---|---|---|
| `/tool-quick` | Typos, config edits, 1-2 file surgical changes | Low |
| `/tool-fix` | Bug reports, failing tests, regressions | Low → High by scope |
| `/tool-feat` | New functionality (auto-brainstorms when unclear) | Medium |
| `/tool-plan` | Requirements and implementation planning (auto-escalates to blueprint/gsd) | Medium |
| `/tool-refactor` | Behavior-preserving cleanup | Medium |
| `/tool-review` | Local diff, PR, or post-implementation review | Low → High by mode |
| `/tool-research` | Codebase-aware technical research | Low → High by mode |
| `/tool-graph` | code-review-graph diagnostics only (auto-refreshed via git hooks) | Low |
| `/tool-update` | Sync and update installation | Low |
| `/tool-brainstorm` | **[DEPRECATED]** — use `/tool-feat` or `/tool-plan` | — |
| `/tool-blueprint` | **[DEPRECATED]** — use `/tool-plan --deep` | — |
| `/tool-branch` | Branch create, status, review, merge, abort (auto-called by feat/fix) | Low |

## Router

- If the change is obvious and touches at most 2 files, use `/tool-quick`.
- If something is broken, use `/tool-fix`; only escalate to GSD debugging when the cause crosses files or is not reproducible locally.
- If you need to build a feature, use `/tool-feat` — it auto-brainstorms when requirements are unclear. After implementation, it runs GSD verification gates (verify → review → ship for `--deep`).
- If starting any non-trivial task, `/tool-feat` and `/tool-fix` auto-create a feature branch.
- If behavior must remain identical, use `/tool-refactor` and verify before/after.
- If you need review, use `/tool-review --fast` for routine checks, default mode for local/PR review, and `--deep` only for high-risk work.
- If planning is needed, use `/tool-plan` — `--fast` for inline plans, `--standard` for `writing-plans`, `--deep` auto-escalates to `ecc:blueprint` or `gsd project`.
- If you need external/current information, use `/tool-research` (codebase-aware via graph); start with `--quick` and escalate only when evidence is insufficient.
- If you need to diagnose code-review-graph health, use `/tool-graph status` — graph is auto-refreshed by git hooks.
- If you need manual branch operations, use `/tool-branch create|status|review|merge|abort`.

## Cost Modes

| Mode | Use when | Typical tools |
|---|---|---|
| `--fast` | Low-risk, known location, small diff | `/caveman lite`, direct edit, `/gsd-fast`, Caveman review |
| `--standard` | Normal development work | `/caveman full`, targeted exploration, tests, build, local review |
| `--deep` | Ambiguous, high-risk, cross-system, security-sensitive | `/caveman full` or `/caveman ultra`, GSD, deep research, council, review-work |

Default to the cheapest mode that still verifies the outcome. Escalate only when evidence shows the lighter mode is insufficient.

## Caveman Mode Mapping (Enforced)

ALL commands MUST follow this mapping. Individual commands MUST NOT override it.

| Cost Mode | Caveman Mode | Escalation Trigger |
|-----------|-------------|-------------------|
| `--fast` | `/caveman lite` | Never escalate |
| `--standard` | `/caveman full` | Never escalate |
| `--deep` | `/caveman full` | Switch to `/caveman ultra` when: subagent count ≥3, OR context usage >50%, OR multi-session work |

## RTK Policy

RTK compresses Bash/tool output (git, tests, builds, logs) before it enters LLM context. Skip RTK when the expected output is small — wrapping short outputs adds latency with no benefit.

| RTK trigger | When |
|-------------|------|
| `rtk gain` | Full test suites, large builds, git logs >100 lines |
| Skip RTK | Single-file tests, lint, short diffs, small directory listings |

RTK + Caveman stack independently: Caveman compresses LLM communication, RTK compresses tool output. Neither replaces the other.

## Core Principles

1. Search before building when the approach is unknown.
2. Prefer surgical changes and preserve existing style.
3. Run the smallest meaningful verification first, then expand if risk demands it.
4. Keep high-cost agents for high-risk decisions, not routine work.
5. Use Caveman or compact handoffs when context usage grows.
6. Code-review-graph is auto-refreshed by git hooks — never manually refresh during workflow.

## Cross-cutting Security Gate

Enforced on ALL `/tool-*` commands regardless of cost mode. If any change touches:
**auth, user input parsing, file system paths, network I/O, secrets, cookies, SQL, or serialization** —
immediately escalate to `skill(name="security-review")`.

Individual command files reference this gate with one line; do not repeat the full text.

## GSD Completion Pipeline

For non-trivial implementation work (`/tool-feat`, `/tool-fix`), verification is structured through GSD gates instead of ad-hoc tests.

### `--standard` completion
1. `skill(name="gsd-verify-work")` — confirm behavior against the original requirement or bug description
2. `skill(name="caveman-review")` — compressed code quality check on the diff
3. Offer `/caveman-commit` suggestion — **NEVER** auto-commit without explicit user request

### `--deep` completion
1. `skill(name="gsd-verify-work")` — structured acceptance verification against plan/requirements
2. `skill(name="gsd-code-review")` — phase-scoped review with severity-classified findings
3. `skill(name="gsd-ship")` — create PR, run review gates, prepare for merge
4. Offer `/caveman-commit` suggestion

`/tool-quick` and `/tool-refactor` use lighter verification (formatter/lint/test) and skip full GSD gates unless risk escalates.

## Token Guidance

- This file is a router, not the full manual. Detailed docs live in `docs/`.
- Use `/tool-quick` or `/tool-review --fast` with `/caveman lite` for routine work.
- RTK is only for noisy commands (large test suites, builds, long git logs); skip for small outputs.
- Use `/tool-research --deep`, `/review-work`, and GSD phase workflows deliberately; they can launch multiple agents and consume substantially more context.
- If context exceeds 50%, switch to `/caveman ultra` before continuing long work.

## References

- Toolchain architecture: `docs/architecture.md`
- Token cost model: `docs/token-cost.md`
- Installation modes: `docs/install.md`
- Language command reference: `docs/language-reference.md`
