# Toolchain Architecture

Engineer Shovel commands are organized around a **5-layer tool architecture**, with each layer solving a distinct problem class.

---

## 5-Layer Architecture

```
Layer 1: Communication Compression (always-on, no command)
  caveman → LLM output compression (lite/full/ultra — enforced by cost mode)
  rtk    → Tool output compression (rtk gain for large outputs only: builds, full suites, long logs)

Layer 2: Code Intelligence (auto-refreshed via git hooks, no manual command)
  code-review-graph → semantic_search_nodes / query_graph / get_impact_radius
                      get_affected_flows / detect_changes / get_review_context
                      get_architecture_overview / refactor_tool
  /tool-graph reserved for manual diagnostics only

Layer 3: Development Methodology (process enforcement, on-demand)
  superpowers → brainstorming / writing-plans / tdd-workflow / systematic-debugging / verification

Layer 4: Domain Expertise (technical implementation, on-demand)
  L4a (Pattern Reference): language/framework skills (golang-patterns, python-patterns, etc.) — auto-loaded
  L4b (Specialized Process): security-review / review-work / deep-research / blueprint / council
  L4c (Operational): github-ops / deployment-patterns

Layer 5: Project Management (stateful orchestration, multi-phase only)
  gsd → explore / discuss-phase / plan-phase / execute-phase / debug
        verify-work / code-review / ship / workstreams / health
```

### Layer Principles

1. Escalate bottom-up — commands move up layers as complexity increases.
2. Compression layer always on — caveman controls LLM verbosity, rtk controls tool output noise (large outputs only).
3. Code intelligence auto-maintained — code-review-graph refreshed by git hooks, queried silently by commands using concrete MCP tool names.
4. ECC sub-layers — L4a auto-loads pattern references (free), L4b invokes costly process workflows, L4c handles operational tasks.
5. superpowers vs gsd — superpowers defines methodological discipline (session-scoped), gsd manages project phase state (cross-session persistent).
6. GSD completion gates — `/tool-feat` and `/tool-fix` end with gsd-verify-work (→ caveman-review for --standard, → gsd-code-review → gsd-ship for --deep).

---

## Tool Overview

| Tool | Role | Trigger Pattern | Token Cost |
|------|------|----------------|------------|
| **caveman** | LLM communication compression | Always on, tiered by mode | ~75% prompt reduction |
| **rtk** | Tool output compression | `rtk gain` before test/build/git | Noisy output compression |
| **code-review-graph** | Code knowledge graph | Git hooks auto-refresh, queried silently | Low (~100-500 tokens/query) |
| **superpowers** | Development methodology | When requirements unclear or discipline needed | Medium-High (multi-turn) |
| **ecc** | Domain expertise | Language commands, security review, deep research, review orchestration, blueprint, architecture decisions | Low-High |
| **gsd** | Project management | Multi-phase/milestone/persistent state | High (subagent parallelism) |

---

## Cost Mode Routing

| Mode | Compression | Code Intelligence | Methodology | Domain Expertise | Project Mgmt |
|------|-------------|-------------------|-------------|-----------------|--------------|
| `--fast` | caveman lite + RTK (large outputs) | CRG | skip | L4a (auto-load) | skip |
| `--standard` | caveman full + RTK (large outputs) | CRG | optional (brainstorm/tdd) | L4a + L4b (security if needed) | gsd-verify-work (feat/fix completion) |
| `--deep` | caveman full/ultra + RTK (large outputs) | CRG | optional (plans/tdd) | L4a + L4b + L4c | gsd-verify-work → gsd-code-review → gsd-ship |

---

## Exclusive Routing Rules

When multiple tools could solve the same problem, choose ONE based on context:

| Scenario | superpowers | gsd | ecc | Decision Criteria |
|----------|------------|-----|-----|-------------------|
| Requirement clarification | brainstorming (technical design) | gsd-explore (product direction) | council (multi-path architecture) | Implementation vs. business goal vs. high-risk decision |
| Planning | writing-plans (implementation) | gsd-plan-phase (phase planning) | blueprint (code dependency graph) | ≤3 files vs. multi-phase vs. dense dependencies |
| Parallel execution | subagent-driven-development | gsd-execute-phase | — | Ad-hoc parallel vs. phase wave orchestration |
| Debugging | systematic-debugging (methodology) | gsd-debug (persistent state) | deep-research (new domain) | Single session vs. cross-context vs. unknown tech |
| Code review | — | gsd-code-review (phase review) | review-work (5-agent parallel) | Phase-scoped vs. heavy parallel review |
| Project planning | — | gsd-new-milestone (milestone) | blueprint (code PR) | Milestone engineering vs. code-level multi-PR |
| Completion verification | — | gsd-verify-work (structured) | — | Post-implementation acceptance for feat/fix |
| Ship/merge | — | gsd-ship (PR+gates) | github-ops (manual PR) | Automated pipeline vs. manual PR management |

---

## Command × Tool Matrix

| Command | caveman | rtk | code-review-graph | superpowers | gsd | ecc |
|---------|---------|-----|-------------------|-------------|-----|-----|
| **quick** | ✅ lite/full | ✅ large outputs | ✅ context | ❌ | ❌ | ✅ L4a auto-load |
| **fix** | ✅ tiered | ✅ large outputs | ✅ trace/impact | ✅ sysdbg | ✅ verify-work (std)/verify→review→ship (deep) | ✅ L4a/L4b |
| **feat** | ✅ tiered | ✅ large outputs | ✅ explore | ✅ brain/plans | ✅ verify-work (std)/verify→review→ship (deep) | ✅ L4a/L4b/council |
| **plan** | ✅ tiered | ❌ | ✅ impact | ✅ brain/plans | ✅ new-milestone (deep) | ✅ council/blueprint |
| **refactor** | ✅ tiered | ✅ large outputs | ✅ impact/patterns | ✅ tdd | ✅ execute-phase (deep) | ✅ review-work (deep) |
| **review** | ✅ tiered | ✅ large diffs/logs | ✅ pr-review | ✅ receiving-review | ❌ | ✅ github-ops/review-work |
| **research** | ✅ tiered | ❌ | ✅ codebase context | ❌ | ❌ | ✅ deep-research/council |
| **graph** | ✅ lite | ✅ build/update | ✅ all | ❌ | ❌ | ❌ |
| **branch** | ✅ lite | ❌ | ✅ pr-review | ❌ | ❌ | ❌ |
| **update** | ✅ lite | ❌ | ⚠️ install | ⚠️ install | ⚠️ install | ⚠️ install |

---

## Token Consumption by Command

| Command | Low Overhead | Medium Overhead | High Overhead |
|---------|-------------|-----------------|---------------|
| quick | --fast (very low) | --standard (low) | — |
| fix | --fast (low) | --standard (medium + gsd-verify-work) | --deep (high + gsd-verify→review→ship) |
| feat | --fast (low) | --standard (medium + gsd-verify-work) | --deep (high + gsd-verify→review→ship) |
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

*Based on ECC + GSD + superpowers + code-review-graph + Caveman + RTK deep integration*
*Last updated: 2026-05-04 — v1.5.0*
