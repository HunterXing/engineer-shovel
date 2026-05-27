# Command Scenarios

Engineer Shovel works best when you route by engineering scenario first, then add capability layers only when they solve a real problem.

## Quick Reference with Aliases

| Scenario | Full Command | Alias | Example |
|----------|--------------|-------|---------|
| Small obvious edit | `/tool-quick` | `/q` | `/q "fix typo"` |
| Reproducible bug | `/tool-fix` | `/f` | `/f --s "login bug"` |
| Clear feature slice | `/tool-feat` | `/fe` | `/fe "dark mode"` |
| Unclear scope/order | `/tool-plan` | `/p` | `/p --d "refactor auth"` |
| Code review | `/tool-review` | `/r` | `/r` |
| Refactoring | `/tool-refactor` | `/rf` | `/rf "clean utils"` |
| Decision needs evidence | `/tool-research` | `/rs` | `/rs --web "compare X"` |
| Branch management | `/tool-branch` | `/b` | `/b create feat add-login` |
| Graph diagnostics | `/tool-graph` | `/g` | `/g status` |
| Sync & update | `/tool-update` | `/u` | `/u --check` |

Cost mode shortcuts: `--f` = `--fast`, `--s` = `--standard`, `--d` = `--deep`

---

## Small Obvious Edit

- Start with: `/tool-quick`
- Good fit:
  - typo fix
  - tiny config tweak
  - one-file surgical rename
- Optional layers:
  - `caveman` for terse communication
  - `rtk` only if shell output gets noisy
  - `code-review-graph` only if the right file or symbol is not obvious
- Avoid:
  - `OpenSpec`
  - `GSD`
  - deep research
- Minimum verification:
  - nearest formatter, lint, or targeted test

## Reproducible Bug

- Start with: `/tool-fix`
- Good fit:
  - failing test
  - local regression
  - runtime error with reproducible path
- Optional layers:
  - `code-review-graph` for cross-file trace, callers, blast radius, tests
  - `superpowers` when root cause is unclear and debugging discipline matters
  - `ECC` for framework-specific, security, or integration-heavy bugs
- Avoid:
  - `GSD` for ordinary local fixes
  - `OpenSpec` unless the bug reveals a missing durable requirement
- Minimum verification:
  - failing test first
  - related tests/build after the fix

## Clear Feature Slice

- Start with: `/tool-feat`
- Good fit:
  - new behavior already understood
  - small or medium feature touching a known area
- Optional layers:
  - `code-review-graph` to find nearby patterns or dependencies
  - `ECC` for framework, security, or external integration guidance
  - `OpenSpec` only if acceptance must persist as files
- Avoid:
  - `GSD` for one-session feature work
  - `research` as a default pre-step
- Minimum verification:
  - implement the smallest slice
  - run native tests/build
  - finish with lightweight review

## Unclear Scope Or Order

- Start with: `/tool-plan`
- Good fit:
  - requirements still fuzzy
  - affected files or order unclear
  - success criteria not stable enough for execution
- Optional layers:
  - `superpowers` for clarification and planning discipline
  - `OpenSpec` for durable reviewable agreement
  - `GSD` only if work becomes phase-based or cross-session
- Avoid:
  - turning planning into default research theater
  - going straight to execution
- Minimum verification:
  - plan includes scope, files/modules, order, verification, exit criteria

## Code Review

- Start with: `/tool-review`
- Good fit:
  - local diff review
  - PR review
  - pre-merge correctness and regression check
- Optional layers:
  - `code-review-graph` for diff risk, blast radius, review context
  - `ECC` only if the review needs platform/security depth
- Avoid:
  - mixing review with automatic repair
- Minimum verification:
  - findings classified by severity
  - recommended next route attached to major findings

## Behavior-Preserving Refactor

- Start with: `/tool-refactor`
- Good fit:
  - cleanup
  - safe rename/extract
  - structure improvement without behavior change
- Optional layers:
  - `code-review-graph` for impact radius and rename/dead-code help
  - `ECC` only when refactor risk depends on framework internals
- Avoid:
  - hidden feature additions
  - skipping baseline verification
- Minimum verification:
  - baseline tests before
  - same tests after

## Decision Needs Evidence

- Start with: `/tool-research`
- Good fit:
  - architecture tradeoff
  - current official guidance needed
  - unfamiliar library or integration choice
- Optional layers:
  - `code-review-graph` for local code context
  - `ECC` for language/framework/security/integration expertise
- Avoid:
  - researching questions already answered by the repo
  - making research a routine prerequisite
- Minimum verification:
  - conclusion routes back to `/tool-plan`, `/tool-feat`, `/tool-quick`, or docs

## Multi-Phase Delivery

- Start with: `/tool-plan --deep`
- Good fit:
  - milestone work
  - multi-PR delivery
  - cross-session execution
  - parallel subagent orchestration
- Optional layers:
  - `GSD` as the orchestration layer
  - `OpenSpec` if phase agreement must persist
  - `ECC` for difficult domain decisions inside the phase
- Avoid:
  - pretending a normal feature route is enough
- Minimum verification:
  - phases, ownership, verification gates, and ship path are explicit
