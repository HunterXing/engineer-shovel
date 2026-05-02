# Repository Assessment

Engineer Shovel is a lightweight skill + slash-command router for OpenCode and Claude Code. This assessment records the current repository state and the optimization plan across architecture, functionality, performance, security, and token efficiency.

## Evidence Sources
- Baseline inventory: `.sisyphus/evidence/task-1-baseline-inventory.txt`
- Token baseline: `.sisyphus/evidence/task-1-token-baseline.json`
- Inventory baseline JSON: `.sisyphus/evidence/task-1-inventory-baseline.json`
- Installer dry-run baseline: `.sisyphus/evidence/task-1-dry-run-baseline.txt`
- Validation baseline: `.sisyphus/evidence/task-1-validation-baseline.txt`
- Compatibility contract: `.sisyphus/evidence/task-2-compat-contract.md`

## 1. Architecture

### Current State
The project uses a small router architecture:

- `SKILL.md` is the always-loaded routing layer and intentionally stays short.
- `commands/tool-*.md` contains 12 slash-command workflows loaded on demand.
- `docs/` stores long-form guidance kept out of the routine context path.
- `install.sh` handles environment detection, installation, optional plugin staging, and verification.
- `scripts/*.py` and `.github/workflows/ci.yml` form the validation layer.

Evidence:
- `SKILL.md:22-91` — lightweight router, command table, cost modes, token guidance, references.
- `commands/tool-*.md` — command frontmatter and command-specific flows.
- `install.sh:137-188` — environment detection and skill/command installation.
- `.github/workflows/ci.yml:15-72` — repository validation chain.

### Assessment
The architecture is appropriately small for a workflow pack. The main maintainability risks are not structural complexity, but repeated guidance across router, commands, README, and docs, plus string-level coupling to external command names.

### Verification Commands
```bash
python3 scripts/validate-command-schema.py
python3 scripts/validate-references.py
python3 scripts/validate-markdown-links.py
```

## 2. Functionality

### Current State
The public functionality consists of 12 `/tool-*` commands and three installer modes.

Public commands:
- `/tool-quick`
- `/tool-fix`
- `/tool-feat`
- `/tool-branch`
- `/tool-plan`
- `/tool-refactor`
- `/tool-review`
- `/tool-brainstorm`
- `/tool-blueprint`
- `/tool-research`
- `/tool-statistic`

Installer modes:
- `--minimal`
- `--recommended`
- `--full`
- `--dry-run`

Evidence:
- `SKILL.md:26-39` — command table.
- `README.md:20-45` — install and invocation examples.
- `README.md:58-71` — public command table.
- `install.sh:36-60` — CLI mode contract.
- `install.sh:314-333` — mode execution behavior.
- `.sisyphus/evidence/task-2-compat-contract.md` — compatibility contract.

### Assessment
The feature surface is coherent and narrow. Optimization work must preserve command names, installer modes, and dry-run behavior. Documentation drift is the primary functionality risk, especially where README, `SKILL.md`, docs, and command frontmatter describe overlapping concepts.

### Verification Commands
```bash
bash install.sh --minimal --dry-run
bash install.sh --recommended --dry-run
bash install.sh --full --dry-run
python3 scripts/validate-references.py
```

## 3. Performance

### Current State
The repository has no long-running application runtime. Performance-sensitive paths are mostly installation and agent-workflow escalation:

- `install.sh:99-117` clones pinned external repositories.
- `install.sh:217-225` can execute the pinned ECC installer in `--full` mode.
- `/tool-review --deep`, GSD workflows, and deep research commands can launch multiple agents and consume substantial time/context by design.
- `scripts/validate-markdown-links.py`, `scripts/inventory.py`, and `scripts/token-benchmark.py` are bounded by the small repository size.

Evidence:
- `install.sh:99-117` — clone and SHA verification.
- `install.sh:217-225` — ECC installer execution.
- `docs/token-cost.md:5-12` — cost drivers.
- `.sisyphus/evidence/task-1-dry-run-baseline.txt` — baseline dry-run behavior.

### Assessment
Normal validation is lightweight. Heavy operations are mostly opt-in through install modes or deep agent workflows. The best performance optimization is not micro-optimizing scripts, but preserving clear escalation boundaries and adding guardrails around expensive installer/deep-mode paths.

### Verification Commands
```bash
bash install.sh --minimal --dry-run
bash install.sh --recommended --dry-run
bash install.sh --full --dry-run
python3 scripts/inventory.py
```

## 4. Security

### Current State
The project has no secrets, auth system, network listener, or application server. Security-relevant surfaces are supply-chain and installer behavior:

- `README.md:20-31` advertises a `curl | bash` install path.
- `install.sh:99-117` clones external repositories and verifies commit SHAs.
- `install.sh:217-225` executes an external `install.sh` after SHA-pinned clone verification.
- `.github/workflows/ci.yml:31-32` validates installer source pins by format.
- `.gitignore` excludes `.env` and related local secret files.

Evidence:
- `README.md:20-31` — quick-start install commands.
- `install.sh:11-19` — external repository URLs and pinned SHAs.
- `install.sh:99-117` — clone + `rev-parse HEAD` verification.
- `install.sh:217-225` — external installer execution.
- `scripts/validate-installer-sources.py` — source pin validation.

### Assessment
SHA pinning is a strong defense and must be preserved. The remaining risks are documentation-level `curl | bash` trust, external installer execution without a stronger timeout/failure boundary, and the absence of a lightweight security scan in CI.

### Verification Commands
```bash
python3 scripts/validate-installer-sources.py
bash -n install.sh
shellcheck install.sh
bash install.sh --full --dry-run
```

## 5. Token Efficiency

### Current State
Token efficiency is a core design goal:

- `SKILL.md` is 91 lines and acts as a router, not a full manual.
- `docs/` keeps long-form guidance off the routine context path.
- Each command defines cost profile, risk level, recommended mode, allowed tools, and escalation path.
- `scripts/token-benchmark.py` provides static token estimates.
- `docs/token-cost.md` defines Caveman/RTK policy and distinguishes static estimates from measured session data.

Evidence:
- `SKILL.md:52-84` — cost modes and token guidance.
- `docs/token-cost.md:1-79` — token model and session statistics policy.
- `scripts/token-benchmark.py:28-45` — static proxy output.
- `.sisyphus/evidence/task-1-token-baseline.json` — baseline token estimate.

### Assessment
The major token optimization opportunity is reducing duplicated cost/compression guidance across `SKILL.md`, README, docs, and command files while preserving command self-containment. The second opportunity is clarifying the difference between static estimates and real measured Caveman/RTK data so the project never reports fake precision.

### Verification Commands
```bash
python3 scripts/token-benchmark.py
python3 scripts/inventory.py
python3 scripts/validate-command-schema.py
```

## Optimization Plan Summary

1. Establish baseline metrics and compatibility contracts.
2. Reduce duplicated token/cost guidance without breaking command self-containment.
3. Clarify static versus measured token reporting.
4. Harden installer documentation and external installer execution behavior.
5. Add minimal regression coverage for validation scripts.
6. Re-run full validation and publish before/after results.

## Before / After Summary

| Area | Before | After |
|---|---|---|
| Command token estimate total | 3816 estimated tokens (`.sisyphus/evidence/task-1-token-baseline.json`) | 3724 estimated tokens (`.sisyphus/evidence/task-10-full-verification.txt`) |
| Average command token estimate | 381.6 | 372.4 |
| Python regression tests | None | `pytest` with 5 passing tests covering 3 validation scripts |
| Installer guidance | README promoted `curl \| bash` one-liner first | README/README_zh now recommend download-first install, keep one-liner as trusted shortcut |
| External installer guardrail | No explicit timeout or clone error details | ECC external installer wrapped with timeout and clearer failure reporting; clone errors surfaced |
| Documentation consistency | `docs/workflows.md` still claimed 9 commands | Router/docs/README now aligned on 10 commands |
| Token semantics | Static estimate vs measured data boundary implied but not machine-readable | `scripts/token-benchmark.py` now exposes explicit `measurement_sources` and keeps measured data `unknown` when unavailable |

Evidence:
- `.sisyphus/evidence/task-1-token-baseline.json`
- `.sisyphus/evidence/task-5-token-diff.json`
- `.sisyphus/evidence/task-9-python-tests.txt`
- `.sisyphus/evidence/task-10-full-verification.txt`

## Remaining Risks / Deliberate Non-Goals

- `shellcheck` is not available in the current local environment, so local evidence records that state while CI remains the authoritative shell lint layer.
- Live Caveman and RTK savings are still environment-dependent and remain `unknown` until those tools report measured values.
- This repo still references external commands/tools by string name; this is acceptable for current scope and was intentionally not expanded into upstream ecosystem refactors.
- No heavy Python quality stack was added (`mypy`, `ruff`, `bandit`, coverage gates) because the chosen minimum-sufficient approach for this iteration was fixture-based pytest regression coverage.

## Final Assessment Summary

This optimization cycle improved the repository in the areas the user asked for without changing its public shape. The project remains a lightweight router centered on `SKILL.md`, but now has clearer compatibility contracts, lower repeated token overhead in command docs, safer installer guidance and execution behavior, stronger validation regression protection, and explicit separation between static token estimates and real measured savings.

The remaining unresolved items are either intentionally deferred (heavier Python quality tooling) or fundamentally dependent on external tool availability (live Caveman/RTK measured data). For the current repository scope, the project is in a meaningfully stronger state across architecture clarity, functionality consistency, installer/security posture, and token-efficiency discipline.

## Known Unresolved Items
- Live Caveman/RTK measurements may remain unavailable in environments without those tools; such values must stay `unknown` rather than estimated as measured.
- Installer hardening should improve safety without changing the project into a package-manager-specific distribution.
- External command ecosystem references remain string-coupled by design; this plan scopes only this repository.
