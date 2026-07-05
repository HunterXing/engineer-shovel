---
name: 工兵铲-full
display_name: engineer-shovel-full
description: |
  Engineer Shovel Full — Complete workflow router with all details.
  Load this when Level 1 (SKILL.md) is insufficient.
license: MIT
metadata:
  version: "1.8.0"
  category: workflow
  token_profile: full-router
  level: 2
  base_skill: engineer-shovel
---

# 🪖 Engineer Shovel — Full Router

**Level 2**: Complete routing with all details, escalation rules, and toolchain guidance.

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
| Reference | `/tool-alias` | Command aliases and shortcuts | N/A |

## Command Aliases

| Alias | Full Command | Example |
|-------|--------------|---------|
| `/q` | `/tool-quick` | `/q "fix typo"` |
| `/f` | `/tool-fix` | `/f --s "login bug"` |
| `/fe` | `/tool-feat` | `/fe "dark mode"` |
| `/p` | `/tool-plan` | `/p --d "refactor auth"` |
| `/r` | `/tool-review` | `/r` |
| `/rf` | `/tool-refactor` | `/rf "clean utils"` |
| `/rs` | `/tool-research` | `/rs --web "compare X"` |
| `/b` | `/tool-branch` | `/b create feat add-login` |
| `/g` | `/tool-graph` | `/g status` |
| `/u` | `/tool-update` | `/u --check` |

Cost mode shortcuts: `--f` = `--fast`, `--s` = `--standard`, `--d` = `--deep`

## Default Routes

- `/tool-quick`: obvious low-risk 1-2 file work
- `/tool-fix`: broken behavior, regression, failing test
- `/tool-feat`: new behavior that is already clear enough to implement
- `/tool-plan`: scope, order, ownership, or acceptance is unclear
- `/tool-review`: review itself is the task
- `/tool-research`: a decision needs evidence before planning or implementation
- `/tool-branch`, `/tool-graph`, `/tool-update`: platform maintenance only

## Engineering Route First

Choose the task route before choosing the capability layer:

| Scenario | Start here | Typical upgrade layers | Default non-goals |
|---|---|---|---|
| Typo, tiny config edit, one obvious file | `/tool-quick` | `caveman`, `rtk` only for noisy output | No OpenSpec, no GSD, no deep research |
| Local bug with clear repro | `/tool-fix` | `code-review-graph`, `superpowers` only if root cause unclear | No default GSD, no broad research |
| Small or medium feature with clear intent | `/tool-feat` | `code-review-graph`, `ECC` for framework/security/integration questions | No default OpenSpec, no default GSD |
| Scope/order/acceptance unclear | `/tool-plan` | `superpowers`, `OpenSpec` only if durable agreement matters | No implementation, no generic research detour |
| Review or refactor task | `/tool-review`, `/tool-refactor` | `code-review-graph` first, `ECC` only for specialized risk | No feature expansion |
| Multi-phase, milestone, cross-session delivery | `/tool-plan --deep` then GSD | `GSD`, optional `OpenSpec` | No pretending standard routes are enough |

## Cost Modes

| Mode | Use when | Typical tools |
|---|---|---|
| `--fast` | Low-risk, known location, small diff | `/caveman lite`, direct edit, targeted verification |
| `--standard` | Normal development work | `/caveman full`, targeted graph context, native tests/build, light review |
| `--deep` | Ambiguous, high-risk, cross-system, security-sensitive | `/caveman full` or `/caveman ultra`, deliberate use of OpenSpec/ECC/GSD |

## Smart Mode Recommendation

When user doesn't specify a mode, auto-detect based on signals:

| Signal | Recommended Mode |
|--------|------------------|
| Single file, obvious change | `--fast` |
| Multiple files, clear scope | `--standard` |
| Cross-module, security, ambiguous | `--deep` |
| Bug with clear repro | `--fast` |
| Bug without repro | `--standard` |
| New feature, clear spec | `--standard` |
| New feature, vague spec | `--deep` |

### Auto-escalation triggers (→ `--deep`):
- Security-sensitive code
- More than 5 files affected
- Cross-module dependencies unclear

### Auto-de-escalation triggers (→ `--fast`):
- Single file, obvious change
- No dependencies affected
- Clear verification path

## Caveman Mode Mapping (Enforced)

ALL commands MUST follow this mapping:

| Cost Mode | Caveman Mode | Escalation Trigger |
|-----------|-------------|-------------------|
| `--fast` | `/caveman lite` | Never escalate |
| `--standard` | `/caveman full` | Never escalate |
| `--deep` | `/caveman full` | Switch to `/caveman ultra` when: subagent count ≥3, OR context usage >50%, OR multi-session work |

## RTK Policy

RTK compresses Bash/tool output before it enters LLM context:

| RTK trigger | When |
|-------------|------|
| `rtk gain` | Full test suites, large builds, git logs >100 lines |
| Skip RTK | Single-file tests, lint, short diffs, small directory listings |

## Cache Layer

Cache reduces redundant queries within a session:

| Operation | TTL | Token Savings |
|-----------|-----|---------------|
| `impact_radius` | 5 min | ~80% |
| `architecture_overview` | 30 min | ~90% |
| `test_coverage` | 10 min | ~70% |

## Capability Layers

- `code-review-graph`: code understanding and impact analysis
- `caveman`: communication compression
- `rtk`: noisy tool output compression
- `superpowers`: session-scoped method upgrade
- `ECC`: specialized architecture, framework, security guidance
- `OpenSpec`: durable specs and tasks
- `GSD`: multi-phase or cross-session orchestration
- `claude-mem`: cross-session memory

## Escalation Rules

- Escalate to `code-review-graph` when the answer depends on callers, impact radius, review context, or tests
- Escalate to `superpowers` when a single task needs clearer method, debugging discipline, or TDD pressure
- Escalate to `OpenSpec` only when requirements, acceptance, or tasks must persist as reviewable artifacts
- Escalate to `ECC` for specialized research, architecture tradeoffs, framework patterns, security
- Escalate to `GSD` only for milestone-scale, multi-phase, parallel, or cross-session delivery

## Cross-cutting Security Gate

Enforced on ALL `/tool-*` commands. If any change touches:
**auth, user input parsing, file system paths, network I/O, secrets, cookies, SQL, or serialization** —
immediately promote to `--deep` and add `/tool-review --deep` before sign-off.

## Toolchain Awareness

When using external tools, announce with 🚀:

```
🚀 **code-review-graph** → analyzing impact radius
🚀 **caveman** → compressing output (full mode)
🚀 **rtk** → wrapping test output
🚀 **superpowers** → loading systematic-debugging skill
🚀 **claude-mem** → searching for similar bug history
🚀 **ECC** → loading security guidance
```

## Completion Pipeline

### `--standard` completion
1. Run project-native targeted tests/build/typecheck
2. Use `/tool-review --fast` or Caveman-compressed diff sanity check
3. Offer `/caveman-commit` suggestion — NEVER auto-commit

### `--deep` completion
1. `skill(name="gsd-verify-work")` — structured acceptance verification
2. `skill(name="gsd-code-review")` — phase-scoped review
3. `skill(name="gsd-ship")` — create PR, run review gates

## Token Guidance

- This file is the full router. For quick reference, use SKILL.md (Level 1)
- Use `/tool-quick`, `/tool-fix`, or `/tool-feat` for most routine work
- RTK is only for noisy commands; skip for small outputs
- If context exceeds 50%, switch to `/caveman ultra`

## References

- Quick router: `SKILL.md` (Level 1)
- Toolchain architecture: `docs/architecture.md`
- Scenario routing: `docs/command-scenarios.md`
- Token cost model: `docs/token-cost.md`
- Installation: `docs/install.md`
- Language reference: `docs/language-reference.md`
