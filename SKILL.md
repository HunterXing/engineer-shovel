---
name: 工兵铲
display_name: engineer-shovel
description: |
  工兵铲 (Engineer Shovel) — token-aware AI agent development workflow router.
  Provides 12 slash commands for feature work, bug fixing, branch workflow, planning, refactoring,
  review, brainstorming, quick tasks, complex projects, research, and token statistics.
license: MIT
metadata:
  version: "1.2.0"
  category: workflow
  token_profile: lightweight-router
  sources:
    - OhMyOpenCode documentation
    - superpowers plugin
    - ECC (Everything Claude Code)
    - GSD (Get Stuff Done)
    - Caveman plugin
    - rtk
---

# 🪖 工兵铲 — Engineer Shovel

Engineer Shovel is a lightweight router for AI-assisted software engineering. It intentionally keeps this skill file short: use it to choose the right `/tool-*` command, then let the selected command carry the detailed workflow.

## Commands

| Command | Use for | Default cost |
|---|---|---|
| `/tool-quick` | Typos, config edits, 1-2 file surgical changes | Low |
| `/tool-fix` | Bug reports, failing tests, regressions | Low → High by scope |
| `/tool-feat` | New functionality | Medium |
| `/tool-branch` | Branch workflow: create, review, merge, abort | Low |
| `/tool-plan` | Requirements and implementation planning | Medium |
| `/tool-refactor` | Behavior-preserving cleanup | Medium |
| `/tool-review` | Local diff, PR, or post-implementation review | Low → High by mode |
| `/tool-brainstorm` | Explore unclear ideas before building | Low → Medium |
| `/tool-blueprint` | Multi-step, multi-session projects | High |
| `/tool-research` | Current-state technical research | Low → High by mode |
| `/tool-statistic` | Session token usage and savings report | Low |
| `/tool-update` | Sync and update installation | Low |

## Router

- If the change is obvious and touches at most 2 files, use `/tool-quick`.
- If something is broken, use `/tool-fix`; only escalate to GSD debugging when the cause crosses files or is not reproducible locally.
- If you need to build a feature, use `/tool-feat`; use `/tool-plan` first when requirements are unclear.
- If starting any non-trivial task, use `/tool-branch create` first to isolate changes in a feature branch.
- If behavior must remain identical, use `/tool-refactor` and verify before/after.
- If you need review, use `/tool-review --fast` for routine checks, default mode for local/PR review, and `--deep` only for high-risk work. Use `/tool-branch review` to see diff before merging.
- If the work spans phases, milestones, or multiple PRs, use `/tool-blueprint`.
- If you need external/current information, use `/tool-research`; start with `--quick` and escalate only when evidence is insufficient.
- If you need session token usage or savings, use `/tool-statistic`; it reports measured Caveman/RTK data when available and avoids fake precision.

## Cost Modes

| Mode | Use when | Typical tools |
|---|---|---|
| `--fast` | Low-risk, known location, small diff | `/caveman lite`, direct edit, `/gsd-fast`, Caveman review |
| `--standard` | Normal development work | `/caveman full`, targeted exploration, tests, build, local review |
| `--deep` | Ambiguous, high-risk, cross-system, security-sensitive | `/caveman full` or `/caveman ultra`, GSD, deep research, Oracle/review-work |

Default to the cheapest mode that still verifies the outcome. Escalate only when evidence shows the lighter mode is insufficient.

## Compression Defaults

- Use Caveman by default because it reduces prompt/context verbosity before and during workflows.
- `--fast`: prefer `/caveman lite` so tiny tasks stay readable.
- `--standard`: prefer `/caveman full` to reduce repeated workflow and verification chatter.
- `--deep`: prefer `/caveman full`; switch to `/caveman ultra` for multi-agent, long-context, or context-pressure work.
- RTK is complementary when installed: it compresses Bash/tool output before it enters context, while Caveman compresses LLM communication and prompt verbosity.

## Core Principles

1. Search before building when the approach is unknown.
2. Prefer surgical changes and preserve existing style.
3. Run the smallest meaningful verification first, then expand if risk demands it.
4. Keep high-cost agents for high-risk decisions, not routine work.
5. Use Caveman or compact handoffs when context usage grows.

## Token Guidance

- This file is a router, not the full manual. Detailed docs live in `docs/`.
- Use `/tool-quick` or `/tool-review --fast` with `/caveman lite` for routine work.
- Use RTK-enabled Bash output for noisy commands such as git, tests, builds, and logs when the environment supports it.
- Use `/tool-research --deep`, `/review-work`, and GSD phase workflows deliberately; they can launch multiple agents and consume substantially more context.
- If context exceeds 50%, use `/caveman full` or `/strategic-compact` before continuing long work; use `/caveman ultra` when context pressure is severe.

## References

- Full workflows: `docs/workflows.md`
- Token cost model: `docs/token-cost.md`
- Installation modes: `docs/install.md`
- Language command reference: `docs/language-reference.md`
