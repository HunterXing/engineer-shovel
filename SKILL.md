---
name: 工兵铲
display_name: engineer-shovel
description: |
  工兵铲 (Engineer Shovel) — token-aware AI agent development workflow router.
  Provides 10 active slash commands for feature work, bug fixing, planning, refactoring,
  review, quick tasks, research, code graph diagnostics, and sync.
license: MIT
metadata:
  version: "1.7.5"
  category: workflow
  token_profile: lightweight-router
  sources:
    - superpowers plugin
    - ECC (Everything Claude Code)
    - OpenSpec
    - GSD (Get Stuff Done)
    - Caveman plugin
    - rtk
    - code-review-graph
    - claude-mem
---

# 🪖 工兵铲 — Engineer Shovel

Engineer Shovel is a workflow router for AI-assisted software engineering on OpenCode and Claude Code. It keeps the runtime small, installs broad capability when asked, and routes day-to-day work to the lightest path that still proves the result.

## Product Shape

- Engineer Shovel is a lightweight workflow router, not a heavy mandatory framework.
- Most work should stay in `quick`, `fix`, `feat`, or `plan`.
- `review`, `refactor`, and `research` are support routes, not default front doors.
- `branch`, `graph`, and `update` are platform lifecycle commands.
- External tools are upgrade layers with narrow jobs, not ceremony every task must pass through.
- This file is the router; detailed policy lives in `docs/`.

## Command Groups

| Group | Command | Use for | Default cost |
|---|---|---|---|
| Main workflow | `/tool-quick` | Typos, config edits, 1-2 file surgical changes | Low |
| Main workflow | `/tool-fix` | Bug reports, failing tests, regressions | Low → High by scope |
| Main workflow | `/tool-feat` | New functionality; clarifies when unclear | Medium |
| Main workflow | `/tool-plan` | Requirements, sequencing, specs, implementation direction | Medium |
| Engineering support | `/tool-review` | Local diff, PR, or pre-merge review | Low → High by mode |
| Engineering support | `/tool-refactor` | Behavior-preserving cleanup | Medium |
| Engineering support | `/tool-research` | Decision-focused research with codebase context | Low → High by mode |
| Platform support | `/tool-branch` | Branch create, status, review, merge, abort | Low |
| Platform support | `/tool-graph` | code-review-graph diagnostics only | Low |
| Platform support | `/tool-update` | Router sync, component health, repair guidance | Low |

## Default Routes

- `/tool-quick`: obvious low-risk 1-2 file work
- `/tool-fix`: broken behavior, regression, failing test
- `/tool-feat`: new behavior that is already clear enough to implement
- `/tool-plan`: scope, order, ownership, or acceptance is unclear
- `/tool-review`: review itself is the task
- `/tool-research`: a decision needs evidence before planning or implementation
- `/tool-branch`, `/tool-graph`, `/tool-update`: platform maintenance only

## Engineering Route First

Choose the task route before choosing the capability layer. The command should answer "what kind of engineering job is this?" and the external tool should answer "what extra help does this job genuinely need?"

| Scenario | Start here | Typical upgrade layers | Default non-goals |
|---|---|---|---|
| Typo, tiny config edit, one obvious file | `/tool-quick` | `caveman`, `rtk` only for noisy output | No OpenSpec, no GSD, no deep research |
| Local bug with clear repro | `/tool-fix` | `code-review-graph`, `superpowers` only if root cause unclear | No default GSD, no broad research |
| Small or medium feature with clear intent | `/tool-feat` | `code-review-graph`, `ECC` for framework/security/integration questions | No default OpenSpec, no default GSD |
| Scope/order/acceptance unclear | `/tool-plan` | `superpowers`, `OpenSpec` only if durable agreement matters | No implementation, no generic research detour |
| Review or refactor task | `/tool-review`, `/tool-refactor` | `code-review-graph` first, `ECC` only for specialized risk | No feature expansion |
| Multi-phase, milestone, cross-session delivery | `/tool-plan --deep` then GSD | `GSD`, optional `OpenSpec` | No pretending standard routes are enough |

## Practical Split

- 80% of work: `/tool-quick`, `/tool-fix`, `/tool-feat`
- 15% of work: `/tool-plan`, `/tool-review`, `/tool-research`
- 5% of work: deliberate escalation to OpenSpec, ECC, or GSD
- Full install means these paths are available; it does not change the default route.

## Cost Modes

| Mode | Use when | Typical tools |
|---|---|---|
| `--fast` | Low-risk, known location, small diff | `/caveman lite`, direct edit, targeted verification |
| `--standard` | Normal development work | `/caveman full`, targeted graph context, native tests/build, light review |
| `--deep` | Ambiguous, high-risk, cross-system, security-sensitive | `/caveman full` or `/caveman ultra`, deliberate use of OpenSpec/ECC/GSD |

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

RTK is a shell-output layer, not a planning or code-intelligence layer. It helps when the agent is using Bash commands. It does **not** replace built-in file tools such as `Read`, `Grep`, or `Glob`.

| RTK trigger | When |
|-------------|------|
| `rtk gain` | Full test suites, large builds, git logs >100 lines |
| Skip RTK | Single-file tests, lint, short diffs, small directory listings |

RTK + Caveman stack independently: Caveman compresses LLM communication, RTK compresses tool output. Neither replaces the other.

## Capability Layers

- `code-review-graph`: code understanding and impact analysis for multi-file reasoning, review, trace, and refactor work
- `caveman`: communication compression
- `rtk`: noisy tool output compression
- `superpowers`: session-scoped method upgrade for clarification, TDD, and systematic debugging
- `ECC`: specialized architecture, framework, security, and integration guidance
- `OpenSpec`: durable specs and tasks when agreement must persist in files
- `GSD`: multi-phase or cross-session orchestration with verification gates

These layers solve specific problems. Availability does not imply automatic use.

## Memory Layer

claude-mem provides auto-capture cross-session memory:
- Decisions, preferences, bug history, and architectural context persist across sessions.
- New sessions auto-inject relevant memories via progressive disclosure (search → timeline → get_observations).
- Complements caveman: caveman compresses single-session communication, claude-mem persists cross-session knowledge.
- Web UI: http://localhost:37777
- Manual search: `npx claude-mem search "<query>"`

## Escalation Rules

- Escalate to `code-review-graph` when the answer depends on callers, impact radius, review context, or tests for a changed node. Skip it for obvious single-file edits.
- Escalate to `superpowers` when a single task needs clearer method, debugging discipline, or TDD pressure.
- Escalate to `OpenSpec` only when requirements, acceptance, or tasks must persist as reviewable artifacts.
- Escalate to `ECC` for specialized research, architecture tradeoffs, framework patterns, security, or external integration questions.
- Escalate to `GSD` only for milestone-scale, multi-phase, parallel, or cross-session delivery.
- Full installation means these capabilities are ready; it does not mean the default route should become heavy.

## Core Principles

1. Search before building when the approach is unknown.
2. Prefer surgical changes and preserve existing style.
3. Run the smallest meaningful verification first, then expand if risk demands it.
4. Keep heavy methodology and orchestration for high-risk work, not routine edits.
5. Use Caveman or compact handoffs when context usage grows.
6. Treat external tools as capability layers with distinct jobs; avoid overlapping routes by default.
7. Code-review-graph is auto-refreshed by git hooks — never manually refresh during workflow.
8. Always have a fallback plan if external tools are unavailable.
9. Document decisions and rationale for future reference.

## Cross-cutting Security Gate

Enforced on ALL `/tool-*` commands regardless of cost mode. If any change touches:
**auth, user input parsing, file system paths, network I/O, secrets, cookies, SQL, or serialization** —
immediately promote the task to the matching deep route and add a `/tool-review --deep` checkpoint before sign-off.

Individual command files reference this gate with one line; do not repeat the full text.

## Error Recovery

When a workflow encounters errors:
1. **Tool unavailable**: Fall back to native tools (Grep, Glob, Read, Bash)
2. **Verification failure**: Revert changes and reassess approach
3. **External service down**: Use cached data or skip non-critical steps
4. **Scope creep**: Split work into smaller slices and defer additional scope
5. **Repeated failures**: Escalate to `/tool-plan --deep` for architectural review

## Toolchain Awareness

**IMPORTANT**: When using any external tool or capability layer, you MUST explicitly announce it to the user. This helps developers understand what tools are powering their workflow and builds trust in the AI harness.

### Announcement Format

Use this format when activating a tool — make it **impossible to miss**:

```
🚀 **[Tool Name]** → <what it's doing>
```

Examples:
```
🚀 **code-review-graph** → analyzing impact radius for auth module
🚀 **caveman** → compressing output (full mode)
🚀 **rtk** → wrapping large test suite output
🚀 **superpowers** → loading systematic-debugging skill
🚀 **claude-mem** → searching for similar bug history
🚀 **ECC** → loading security guidance for auth patterns
```

### When to Announce

Announce tool usage at these moments:
1. **First activation**: When a tool is first invoked in the workflow
2. **Key operations**: When performing impact analysis, review, or research
3. **Mode switches**: When escalating from fast to standard to deep
4. **External queries**: When calling MCP tools, web fetches, or external APIs
5. **Compression**: When caveman or rtk compresses output

### Native vs External

Clearly distinguish between:
- **Native tools**: Read, Grep, Glob, Edit, Bash (no announcement needed)
- **External tools**: code-review-graph, caveman, rtk, superpowers, ECC, OpenSpec, GSD, claude-mem (MUST announce with 🚀)

This transparency helps developers learn the toolchain and understand what capabilities are available.

## Completion Pipeline

For implementation work (`/tool-feat`, `/tool-fix`), default verification stays lightweight. GSD is reserved for deep, milestone, or cross-session work.

### `--standard` completion
1. Run project-native targeted tests/build/typecheck.
2. Use `/tool-review --fast` or a Caveman-compressed diff sanity check.
3. Offer `/caveman-commit` suggestion — **NEVER** auto-commit without explicit user request.

### `--deep` completion
1. `skill(name="gsd-verify-work")` — structured acceptance verification against plan/spec.
2. `skill(name="gsd-code-review")` — phase-scoped review with severity-classified findings.
3. `skill(name="gsd-ship")` — create PR, run review gates, prepare for merge.
4. Offer `/caveman-commit` suggestion

`/tool-quick` and `/tool-refactor` use lighter verification (formatter/lint/test) and skip full GSD gates unless risk escalates.

## Token Guidance

- This file is a router, not the full manual. Detailed docs live in `docs/`.
- Use `/tool-quick`, `/tool-fix`, or `/tool-feat` for most routine work.
- RTK is only for noisy commands (large test suites, builds, long git logs); skip for small outputs.
- Use OpenSpec, deep research, and GSD deliberately; they create durable artifacts or broader orchestration state.
- If context exceeds 50%, switch to `/caveman ultra` before continuing long work.

## References

- Toolchain architecture: `docs/architecture.md`
- Scenario routing: `docs/command-scenarios.md`
- Token cost model: `docs/token-cost.md`
- Installation modes: `docs/install.md`
- Language command reference: `docs/language-reference.md`
