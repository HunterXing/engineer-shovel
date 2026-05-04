# Toolchain Architecture

Engineer Shovel commands are organized around a **default core plus escalation layers**. Routine work stays light; specs, capability libraries, and project orchestration load only when risk requires them.

---

## Layer Architecture

```
Layer 0: Compression (always-on, no command)
  caveman → LLM output compression (lite/full/ultra — enforced by cost mode)
  rtk    → Tool output compression (rtk gain for large outputs only: builds, full suites, long logs)

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
  superpowers → brainstorming / writing-plans / tdd-workflow / systematic-debugging / verification

Layer 3: Spec Layer (on-demand durable artifacts)
  OpenSpec → proposal / specs / design / tasks / verify / archive

Layer 4: Capability Library (on-demand)
  ECC → language/framework skills, security-review, review-work, deep-research, council, github-ops

Layer 5: Project Orchestration (deep/milestone only)
  gsd → explore / discuss-phase / plan-phase / execute-phase / debug
        verify-work / code-review / ship / workstreams / health
```

### Layer Principles

1. Escalate bottom-up — commands move up layers as complexity increases.
2. Compression layer always on — caveman controls LLM verbosity, rtk controls tool output noise (large outputs only).
3. Code intelligence auto-maintained — use CRG MCP tools when available, CRG CLI when not, and Glob/Grep/Read as fallback.
4. claude-mem auto-captures session context across work — decisions, preferences, bug history — and injects relevant memories at session start via progressive disclosure. Complements caveman: caveman compresses single-session communication, claude-mem persists cross-session knowledge.
5. OpenSpec creates durable agreement about what to build; it does not replace code graph context or project orchestration.
6. ECC is a capability library, not a default workflow path.
7. superpowers vs gsd — superpowers defines session-scoped methodology, gsd manages cross-session project phase state.
8. GSD completion gates are deep-only by default; standard feature/fix work uses native verification plus light review.

---

## Tool Overview

| Tool | Role | Trigger Pattern | Token Cost |
|------|------|----------------|------------|
| **caveman** | LLM communication compression | Always on, tiered by mode | ~75% prompt reduction |
| **rtk** | Tool output compression | `rtk gain` before test/build/git | Noisy output compression |
| **code-review-graph** | Code knowledge graph | Git hooks auto-refresh, queried silently | Low (~100-500 tokens/query) |
| **claude-mem** | Cross-session memory | Auto-capture via hooks, progressive disclosure | Very Low (~100 tokens/query) |
| **superpowers** | Development methodology | When requirements unclear or discipline needed | Medium-High (multi-turn) |
| **OpenSpec** | Durable spec artifacts | Requirements/spec/design/tasks need reviewable files | Medium |
| **ecc** | Capability library | Language skills, security review, deep research, review orchestration, architecture decisions | Low-High |
| **gsd** | Project orchestration | Multi-phase/milestone/persistent state | High (subagent parallelism) |

---

## Cost Mode Routing

| Mode | Compression | Memory | Code Intelligence | Methodology | Domain Expertise | Project Mgmt |
|------|-------------|--------|-------------------|-------------|-----------------|--------------|
| `--fast` | caveman lite + RTK (large outputs) | auto-capture only | CRG only if target unclear | skip | skip | security only if sensitive | skip |
| `--standard` | caveman full + RTK (large outputs) | search + auto-capture | CRG targeted | optional (brainstorm/tdd) | optional OpenSpec | patterns/security/research only if needed | skip by default |
| `--deep` | caveman full/ultra + RTK (large outputs) | search + auto-capture | CRG architecture | plans/tdd/debug | OpenSpec when specs matter | L4 skills/review/research | gsd verify→review→ship |

---

## Exclusive Routing Rules

When multiple tools could solve the same problem, choose ONE based on context:

| Scenario | superpowers | OpenSpec | gsd | ecc | Decision Criteria |
|----------|------------|----------|-----|-----|-------------------|
| Requirement clarification | brainstorming (technical design) | proposal/specs when agreement must persist | gsd-explore (product direction) | council (multi-path architecture) | Chat clarification vs. durable spec vs. product/milestone |
| Planning | writing-plans (implementation) | specs/design/tasks | gsd-plan-phase (phase planning) | blueprint (code dependency graph) | Implementation order vs. durable requirements vs. multi-phase vs. dense dependencies |
| Parallel execution | subagent-driven-development | — | gsd-execute-phase | — | Ad-hoc parallel vs. phase wave orchestration |
| Debugging | systematic-debugging (methodology) | — | gsd-debug (persistent state) | deep-research (new domain) | Single session vs. cross-context vs. unknown tech |
| Code review | — | opsx verify (if spec exists) | gsd-code-review (phase review) | review-work (5-agent parallel) | Spec conformance vs. phase-scoped vs. heavy parallel review |
| Project planning | — | specs/design/tasks | gsd-new-milestone (milestone) | blueprint (code PR) | Milestone engineering vs. code-level multi-PR |
| Completion verification | — | opsx verify (spec conformance) | gsd-verify-work (deep structured) | — | Spec conformance vs. deep acceptance |
| Ship/merge | — | archive completed specs | gsd-ship (PR+gates) | github-ops (manual PR) | Spec lifecycle vs. automated pipeline vs. manual PR management |

---

## Command × Tool Matrix

| Command | caveman | rtk | code-review-graph | claude-mem | superpowers | OpenSpec | gsd | ecc |
|---------|---------|-----|-------------------|-----------|-------------|----------|-----|-----|
| **quick** | yes lite/full | large outputs | only if target unclear | auto-cap | no | no | no | patterns/security only if needed |
| **fix** | yes tiered | large outputs | trace/impact | search+cap | sysdbg if needed | no | deep only | patterns/security/research if needed |
| **feat** | yes tiered | large outputs | explore | search+cap | brain/plans if unclear | optional standard/deep | deep only | patterns/council/security if needed |
| **plan** | yes tiered | no | impact | search+cap | brain/plans | optional standard/deep | milestone only | council/blueprint |
| **refactor** | yes tiered | large outputs | impact/patterns | search+cap | tdd if needed | deep plan if behavior boundaries need spec | milestone only | review-work deep |
| **review** | yes tiered | large diffs/logs | pr-review | auto-cap | receiving-review | verify if spec exists | no | github-ops/review-work |
| **research** | yes tiered | no | codebase context | search+cap | no | no | no | deep-research/council |
| **graph** | lite | build/update | all | auto-cap | no | no | no | no |
| **branch** | lite | no | pr-review | auto-cap | no | no | no | no |
| **update** | lite | no | install health | install health | install health | install health | install health | install health |

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

---

*Based on claude-mem + OpenSpec + ECC + GSD + superpowers + code-review-graph + Caveman + RTK integration*
*Last updated: 2026-05-04 — v1.7.0*
