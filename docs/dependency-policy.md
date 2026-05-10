# Dependency Policy

Engineer Shovel installs a router plus optional external capability layers. This document defines how those dependencies are governed so `--full` stays useful without turning upgrades into uncontrolled drift.

## Policy Goals

- Keep the public router stable even when upstream tools move quickly.
- Make upgrade behavior predictable: users should know what is pinned, what is floating, and what `/tool-update` is allowed to repair.
- Separate router updates from component upgrades.

## Upgrade Model

- `router update`: sync `SKILL.md` and `/tool-*` files from this repository.
- `component repair/upgrade`: inspect installed tools, then repair or upgrade missing or unhealthy components.
- `/tool-update` is the user-facing entry point for both.
- `install.sh` remains the first-install path and the place where install-time pins are enforced.
- `scripts/dependency_manifest.json` is the shared metadata source for component strategy labels, scope notes, and repair guidance.

## Dependency Matrix

| Component | Install path | Repair path | Scope model | Current strategy | Why |
|---|---|---|---|---|---|
| Engineer Shovel router | repo files / sync | `scripts/sync.py` via `/tool-update` | `global` + `local` | repo version | Router files should match the checked-out repository state |
| ECC | pinned checkout in `install.sh` | limited checks in `scripts/health.py` | `global` only | pinned SHA | High-surface dependency; pin for reproducibility |
| RTK | official installer, fallback cargo pinned rev | `scripts/health.py` | effectively global | mixed: installer + pinned fallback | Prefer upstream path, keep deterministic fallback |
| code-review-graph | `pipx` or `pip` | `scripts/health.py` | mixed: global MCP + repo-local graph build | latest package | Fast-moving tool with clear standalone install path |
| Caveman | official installer | `scripts/health.py` | effectively global | latest installer | Plugin-style tool with upstream-managed install flow |
| superpowers | plugin reference | `scripts/health.py` | effectively global | git/plugin reference | Managed as plugin capability rather than binary |
| OpenSpec | `npm install -g @fission-ai/openspec@latest` | `scripts/health.py` | effectively global CLI | latest package | CLI intentionally kept separate from repo-local initialization |
| GSD | `npx -y get-shit-done-cc@latest` | `scripts/health.py` | `global` + `local` | latest installer | Installer is upstream-owned orchestration entry point |
| claude-mem | `npx -y claude-mem install` | `scripts/health.py` | effectively global | latest installer | Session-memory layer is plugin/runtime integrated |

### Health Status Meanings

- `ok`: installed and configured enough for normal use
- `missing`: not present and potentially auto-repairable
- `unconfigured`: installed but not wired correctly; potentially auto-repairable
- `blocked`: known scope/runtime/platform limitation; report clearly, do not fake repair
- `manual-upgrade-recommended`: maintenance path exists, but automatic repair is intentionally not implemented

## Strategy Rules

### Pin When

- The dependency has broad behavioral surface area inside install/setup flow.
- A bad upstream change would make first install or repair non-reproducible.
- The dependency is not expected to be upgraded on every router sync.

### Float When

- The tool already owns its own installer and health path.
- The integration point is thin and recoverable.
- The cost of pin maintenance is higher than the risk of controlled latest installs.

### Mixed Strategy

Use a mixed strategy when:

- the preferred install path is upstream-owned,
- but a deterministic fallback is still needed for resilience or CI.

RTK currently follows this model.

## Rules for `/tool-update`

- `--check` may fetch remote status, compare router files, and inspect component health.
- `--full` may sync router files and run supported repair actions.
- `/tool-update` should not silently initialize project-local artifacts such as `openspec init`.
- `/tool-update` should surface actionable commands when an automatic repair is blocked or unsafe.
- `/tool-update` should clearly separate router drift from component health so users can tell whether a problem is with Engineer Shovel files or external dependencies.

## Documentation Rules

- Any dependency strategy change should be reflected in:
  - `install.sh`
  - `docs/install.md`
  - `README.md`
  - `README_zh.md`
  - `CHANGELOG.md`

## Change Tracking

When an upstream dependency strategy changes, record:

- what changed,
- why the strategy changed,
- whether the user-facing install or update behavior changed.
