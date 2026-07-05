# Toolchain Architecture

Engineer Shovel is a router, not a bundle of mandatory workflows. The architecture is designed around **full capability available, lightweight execution by default**: routine programming work stays near the core, and deeper layers activate only when the task truly needs them.

For a mode-first view of the same system, see [`docs/mode-routing.md`](mode-routing.md). That document answers a different question: not "which command exists", but "how the same commands diverge under `--fast`, `--standard`, and `--deep`." For scenario-first routing examples, see [`docs/command-scenarios.md`](command-scenarios.md).

---

## Product Model

- Main workflow commands: `quick`, `fix`, `feat`, `plan`
- Support commands: `review`, `refactor`, `research`
- Platform commands: `branch`, `graph`, `update`
- Reference commands: `alias` (command shortcuts)
- Escalation layers: `superpowers`, `ECC`, `OpenSpec`, `GSD`

The product promise is simple:

1. Pick the lightest command that matches the job.
2. Stay in the main workflow layer unless a clear trigger forces escalation.
3. Treat external systems as narrow capability layers, not default ceremony.
4. Use aliases for faster entry: `/q`, `/f`, `/fe`, `/p`, `/r`, `/rf`, `/rs`, `/b`, `/g`, `/u`

### Scenario-First Routing

Pick the command from the engineering job first, then decide whether a capability layer is needed:

| Engineering scenario | Default route | Upgrade only when needed |
|---|---|---|
| Tiny obvious edit | `quick` | `code-review-graph` only if target unclear; `rtk` only for noisy shell output |
| Reproducible bug | `fix` | `code-review-graph` for trace/impact, `superpowers` for method, `ECC` for framework/security/external systems |
| Clear feature slice | `feat` | `code-review-graph` for existing patterns, `ECC` for domain guidance, `OpenSpec` only if acceptance must persist |
| Scope/order/acceptance unclear | `plan` | `superpowers` for clarification, `OpenSpec` for durable agreement, `GSD` only when work becomes phased |
| Review or refactor | `review` / `refactor` | `code-review-graph` by default, `ECC` only for specialized platform risk |
| Milestone or cross-session delivery | `plan --deep` | `GSD`, optional `OpenSpec` |

This split matters more than installation mode. A repo may have the full stack installed and still spend almost all of its time in the main workflow commands.

---

## Shared Policy Surface

Keep shared rules in the narrowest stable place:

- `SKILL.md`: router defaults, command groups, cost-mode mapping, security gate, completion pipeline
- `docs/architecture.md`: capability-layer roles, escalation rules, update model, command/tool matrix
- `commands/tool-*.md`: command-local entry guidance only; do not restate the full Caveman/GSD/OpenSpec decision tree
- `docs/install.md` and `docs/dependency-policy.md`: install, repair, scope, and upgrade governance

This keeps command files readable and reduces drift when a shared rule changes.

---

## Layer Architecture

```
Layer 0: Compression (always-on)
  caveman → LLM output compression (lite/full/ultra — enforced by cost mode)
  rtk    → Tool output compression (rtk gain for large outputs only: builds, full suites, long logs)

Layer 0.5: Cache (always-on)
  impact_radius cache → 5min TTL, invalidated on commit
  architecture_overview cache → 30min TTL, invalidated on file change
  test_coverage cache → 10min TTL, invalidated on test file change

Layer 1: Code Intelligence (default when useful)
  code-review-graph → semantic_search_nodes / query_graph / get_impact_radius
                      get_affected_flows / detect_changes / get_review_context
                      get_architecture_overview / refactor_tool
  /tool-graph reserved for manual diagnostics only

Layer 1.5: Session Memory (auto-capture)
  claude-mem → auto-captures tool outputs, decisions, preferences, bug history
               progressive disclosure: search → timeline → get_observations (~10x token savings)
               SQLite (FTS5 full-text) + Chroma (vector semantic)
               Web UI at http://localhost:37777

Layer 2: Development Methodology (on-demand)
  superpowers → clarification / TDD / systematic debugging / verification discipline

Layer 3: Spec Layer (on-demand durable artifacts)
  OpenSpec → proposal / specs / design / tasks / verify / archive

Layer 4: Capability Library (on-demand)
  ECC → language/framework guidance, architecture tradeoffs, security-focused research, external integration patterns

Layer 5: Project Orchestration (deep/milestone only)
  gsd → explore / discuss-phase / plan-phase / execute-phase / debug
        verify-work / code-review / ship / workstreams / health
```

### Layer Principles

1. Escalate bottom-up — move up layers only when a clear trigger is present.
2. Command first, layer second — choose `quick`/`fix`/`feat`/`plan` before thinking about OpenSpec, ECC, or GSD.
3. Compression is always on — caveman manages LLM verbosity, rtk manages noisy tool output.
4. Cache is always on — repeated queries use cached results to save tokens.
5. Code intelligence is background support — use CRG when available, but keep `/tool-graph` as a diagnostic command.
6. claude-mem persists cross-session context; it complements, not replaces, the router.
7. OpenSpec stores durable agreement; ECC supplies specialized guidance; GSD handles multi-phase orchestration.
8. Full install exposes capability; it does not imply full workflow on every task.
9. Standard work should remain close to native implementation and verification.
10. Progressive disclosure — load only what's needed: Level 1 (lite), Level 2 (standard), Level 3 (full).
11. Smart mode — auto-detect task complexity when mode not specified.

### Tool-Fit Rules

| Tool | Best at | Avoid as default for |
|------|---------|----------------------|
| `code-review-graph` | multi-file reasoning, impact radius, callers/callees, review context, test coverage lookup | tiny single-file edits where direct file reads are cheaper |
| `superpowers` | clarification, TDD, systematic debugging, disciplined execution | serving as a generic capability bundle on every task |
| `ECC` | framework patterns, security, research, integration tradeoffs, language-specific expertise | acting as the first answer for ordinary CRUD or local code search |
| `OpenSpec` | durable proposal/spec/design/tasks that must survive chat context | routine tasks whose agreement fits in normal planning |
| `GSD` | multi-phase execution, parallel agents, cross-session continuity, verify/ship loops | standard `quick`/`fix`/`feat` work that fits in one session |
| `caveman` | response compression and terse reviews/commits | replacing engineering method or architecture decisions |
| `rtk` | Bash/tool output compression for noisy commands | replacing `Read`, `Grep`, `Glob`, or architectural analysis |

---

## Tool Overview

| Tool | Role | Trigger Pattern | Token Cost |
|------|------|----------------|------------|
| **caveman** | LLM communication compression | Always on, tiered by mode | ~75% prompt reduction |
| **rtk** | Tool output compression | `rtk gain` before test/build/git | Noisy output compression |
| **cache** | Query result caching | Always on, TTL-based | ~80% reduction for repeated queries |
| **code-review-graph** | Code knowledge graph | Git hooks auto-refresh, queried silently | Low (~100-500 tokens/query) |
| **claude-mem** | Cross-session memory | Auto-capture via hooks, progressive disclosure | Very Low (~100 tokens/query) |
| **superpowers** | Development methodology | Single-task method upgrade: clarify, debug, TDD, review discipline | Medium-High (multi-turn) |
| **OpenSpec** | Durable spec artifacts | Requirements/spec/design/tasks must persist as reviewable files | Medium |
| **ecc** | Capability library | Specialized guidance: architecture tradeoffs, security, research, external integration patterns | Low-High |
| **gsd** | Project orchestration | Multi-phase, milestone, cross-session execution | High (subagent parallelism) |

---

## Cost Mode Routing

| Mode | Compression | Memory | Code Intelligence | Methodology | Domain Expertise | Project Mgmt |
|------|-------------|--------|-------------------|-------------|-----------------|--------------|
| `--fast` | caveman lite + RTK (large outputs) | auto-capture only | CRG only if target unclear | skip | skip | security only if sensitive | skip |
| `--standard` | caveman full + RTK (large outputs) | search + auto-capture | CRG targeted | optional when stuck | optional only when durable agreement matters | patterns/security/research only if needed | skip |
| `--deep` | caveman full/ultra + RTK (large outputs) | search + auto-capture | CRG architecture | active | active when specs matter | active | active when work spans phases |

---

## Escalation Rules

Escalate only when the command cannot stay lightweight and still be correct:

| Need | Default route | Escalate to | Why |
|------|---------------|-------------|-----|
| Find code, impact, callers, review context | code-review-graph | — | This is the default intelligence layer |
| Clarify a single task's approach | command-local clarification | superpowers | Method upgrade for one task |
| Compare architecture options or specialized domain paths | command-local clarification | ECC | Use the capability library only for hard tradeoffs or domain gaps |
| Persist agreement as specs/tasks | command-local plan | OpenSpec | Durable artifacts, not just chat alignment |
| Run multi-phase or cross-session delivery | command-local execution | GSD | Orchestration state and gates |

### Routing Shortcuts

- `quick` should not open durable specs or project orchestration.
- `quick` should not default to CRG unless file/symbol targeting is unclear.
- `fix` should not use deep research unless the domain is unfamiliar or the bug is cross-system.
- `feat` should stay on native implementation plus targeted verification in `--standard`; OpenSpec and GSD are opt-in by trigger, not ceremony.
- `plan` is the first place to clarify scope; do not send ordinary planning straight into GSD.
- `review` and `research` are support routes; they should not become the default front door for routine coding.

---

## Command × Tool Matrix

| Command | caveman | rtk | code-review-graph | claude-mem | superpowers | OpenSpec | gsd | ecc |
|---------|---------|-----|-------------------|-----------|-------------|----------|-----|-----|
| **quick** | yes lite/full | large outputs | only if target unclear | auto-cap | no | no | no | patterns/security only if needed |
| **fix** | yes tiered | large outputs | trace/impact | search+cap | sysdbg if needed | no | deep only | patterns/security/research if needed |
| **feat** | yes tiered | large outputs | explore | search+cap | only if blocked | only if durable acceptance matters | deep only | patterns/security/research if needed |
| **plan** | yes tiered | no | impact | search+cap | only if blocked | optional when agreement must persist | milestone only | deep research only for higher-order decisions |
| **refactor** | yes tiered | large outputs | impact/patterns | search+cap | tdd if needed | only if behavior boundaries need explicit spec | milestone only | specialized review only when refactor gets broad |
| **review** | yes tiered | large diffs/logs | pr-review | auto-cap | review discipline | verify if spec exists | no | repository/platform context only if needed |
| **research** | yes tiered | no | codebase context | search+cap | no | no | no | deep research for unfamiliar domains or tradeoffs |
| **graph** | lite | build/update | all | auto-cap | no | no | no | no |
| **branch** | lite | no | pr-review | auto-cap | no | no | no | no |
| **update** | lite | no | install health | install health | install health | install health | install health | install health |

---

## Update Model

User-facing update should be remembered as one command:

- `/tool-update --check [--target ...] [--scope global|local]`: compare router files, inspect component health, report repair actions
- `/tool-update --full [--target ...] [--scope global|local]`: sync router files, then run health-driven repair/upgrade steps

Internal responsibility split:

- `install.sh`: first install and explicit repair hooks
- `scripts/sync.py`: Engineer Shovel router files and version sync
- `scripts/health.py`: external component health and repair
- `/tool-update`: user-facing orchestrator over sync + health

Scope rule:

- Router sync supports both global and project-local installs.
- Component health is scope-aware where the underlying component supports it; otherwise `/tool-update` should report the limitation explicitly instead of pretending local repair exists.

---

## Token Consumption by Command

| Command | Low Overhead | Medium Overhead | High Overhead |
|---------|-------------|-----------------|---------------|
| quick | --fast (very low) | --standard (low) | — |
| fix | --fast (low) | --standard (medium + native regression verify) | --deep (high + gsd-verify→review→ship) |
| feat | --fast (low) | --standard (medium + optional OpenSpec + light review) | --deep (high + OpenSpec/gsd-verify→review→ship) |
| plan | --fast (very low) | --standard (medium) | --deep (medium-high) |
| refactor | --fast (low) | --standard (medium) | --deep (high) |
| review | --fast (low) | --standard (medium) | --deep (high) |
| research | --quick (low) | --web (medium) | --deep (high) |
| graph | status/watch (very low) | build/update/rebuild (medium) | — |
| branch | crud (very low) | review (low) | — |
| update | --check (low) | --full (low) | — |

---

## RTK Trigger Points

| Command | When to wrap with `rtk gain` (skip for small outputs) |
|---------|-------------------------------------------------------|
| quick (--standard) | Full test suites |
| fix | Reproduce logs >100 lines → regression suite → final test |
| feat | Full test/build output |
| refactor | Baseline test suite → per-step verify → final test |
| review | Diff >100 lines or large log capture |
| graph | Build/update output |

RTK notes:

- RTK only helps when shell commands are part of the workflow.
- Built-in IDE tools such as `Read`, `Grep`, and `Glob` bypass RTK hooks, so do not describe RTK as a universal prompt compressor.

---

*Based on claude-mem + OpenSpec + ECC + GSD + superpowers + code-review-graph + Caveman + RTK + Cache + Smart Mode integration*
*Last updated: 2026-07-05 — v1.8.0*
