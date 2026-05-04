# Toolchain Architecture

Engineer Shovel commands are organized around a **5-layer tool architecture**, with each layer solving a distinct problem class.

---

## 5-Layer Architecture

```
Layer 1: Communication Compression (always-on, no command)
  caveman → LLM output compression (lite/full/ultra)
  rtk    → Tool output compression (rtk gain explicit interception)

Layer 2: Code Intelligence (auto-refreshed via git hooks, no manual command)
  code-review-graph → architecture exploration / impact analysis / debug tracing / refactoring / PR review
  /tool-graph reserved for manual diagnostics only

Layer 3: Development Methodology (process enforcement, on-demand)
  superpowers → brainstorming / writing-plans / tdd-workflow / systematic-debugging / verification

Layer 4: Domain Expertise (technical implementation, on-demand)
  ecc → language commands / security-review / review-work / blueprint / council / deep-research / github-ops

Layer 5: Project Management (stateful orchestration, multi-phase only)
  gsd → explore / plan-phase / execute-phase / debug / verify-work / ship
```

### Layer Principles

1. Escalate bottom-up — commands move up layers as complexity increases.
2. Compression layer always on — caveman controls LLM verbosity, rtk controls tool output noise.
3. Code intelligence auto-maintained — code-review-graph refreshed by git hooks, queried silently by commands.
4. ecc vs gsd — ecc provides domain expertise (how to do it), gsd manages multi-phase engineering (where we are).
5. superpowers vs gsd — superpowers defines methodological discipline, gsd manages project phase state.

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
| `--fast` | caveman lite + rtk | code-review-graph | skip | language tests | skip |
| `--standard` | caveman full + rtk | code-review-graph | optional (brainstorm/tdd) | language test/build | optional (explore/debug) |
| `--deep` | caveman full/ultra + rtk | code-review-graph | optional (plans/tdd) | security-review/review-work/council | gsd heavy workflows |

---

## Exclusive Routing Rules

When multiple tools could solve the same problem, choose ONE based on context:

| Scenario | superpowers | gsd | ecc | Decision Criteria |
|----------|------------|-----|-----|-------------------|
| Requirement clarification | brainstorming (technical design) | gsd-explore (product direction) | council (multi-path architecture) | Implementation vs. business goal vs. high-risk decision |
| Planning | writing-plans (implementation) | gsd-plan-phase (phase planning) | blueprint (code dependency graph) | ≤3 PR vs. multi-phase vs. dense dependencies |
| Parallel execution | subagent-driven-development | gsd-execute-phase | — | Ad-hoc parallel vs. phase wave orchestration |
| Debugging | systematic-debugging (methodology) | gsd-debug (persistent state) | deep-research (new domain) | Single session vs. cross-context vs. unknown tech |
| Code review | — | gsd-code-review | review-work (5-agent) | — vs. phase review vs. heavy parallel review |
| Project planning | — | gsd project (milestone) | blueprint (code PR) | — vs. milestone engineering vs. code-level multi-PR |

---

## Command × Tool Matrix

| Command | caveman | rtk | code-review-graph | superpowers | gsd | ecc |
|---------|---------|-----|-------------------|-------------|-----|-----|
| **quick** | ✅ | ✅ test/build | ✅ context | ❌ | ❌ | ✅ language tests |
| **fix** | ✅ | ✅ test/log | ✅ trace/impact | ✅ sysdbg/tdd | ✅ debug(deep) | ✅ language/security/deep-research |
| **feat** | ✅ | ✅ test/build | ✅ explore | ✅ brain/plans/tdd | ✅ explore(Phase0) | ✅ language/security/council(deep) |
| **plan** | ✅ | ❌ | ✅ impact | ✅ brain/plans | ✅ explore/project | ✅ council/blueprint |
| **refactor** | ✅ | ✅ test/build | ✅ impact/patterns | ✅ tdd | ✅ execute(deep forced) | ✅ review-work |
| **review** | ✅ | ✅ diff/log | ✅ pr-review | ✅ receiving-review | ❌ | ✅ github-ops/review-work |
| **research** | ✅ | ❌ | ✅ codebase context | ❌ | ❌ | ✅ deep-research/council |
| **graph** | ✅ | ✅ build/update | ✅ all | ❌ | ❌ | ❌ |
| **branch** | ✅ | ❌ | ✅ pr-review | ❌ | ❌ | ❌ |
| **update** | ✅ | ❌ | ⚠️ install | ⚠️ install | ⚠️ install | ⚠️ install |

---

## Token Consumption by Command

| Command | Low Overhead | Medium Overhead | High Overhead |
|---------|-------------|-----------------|---------------|
| quick | --fast (very low) | --standard (low) | — |
| fix | --fast (low) | --standard (medium) | --deep (high) |
| feat | --fast (low) | --standard (medium) | --deep (high) |
| plan | --fast (very low) | --standard (medium) | --deep (medium-high) |
| refactor | --fast (low) | --standard (medium) | --deep (high) |
| review | --fast (low) | --standard (medium) | --deep (high) |
| research | --quick (low) | --web (medium) | --deep (high) |
| graph | status/watch (very low) | build/update/rebuild (medium) | — |
| branch | crud (very low) | review (low) | — |
| update | --check (low) | --full (low) | — |

---

## RTK Trigger Points

| Command | When to call `rtk gain` |
|---------|------------------------|
| quick (--standard) | Before language tests |
| fix | Reproduce/error log → test → before regression tests |
| feat | Before test/build |
| refactor | Baseline test → per-step verify → before final test |
| review | Before diff/log capture |
| graph | Before build/update output |

---

*Based on ECC + GSD + superpowers + code-review-graph + Caveman + RTK deep integration*
*Last updated: 2026-05-03 — v1.4.0*
