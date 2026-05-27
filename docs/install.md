# Installation Modes

`install.sh` (macOS/Linux/WSL) and `install.ps1` (Windows) support interactive setup and non-interactive flags for OpenCode, Claude Code, or both.

```bash
./install.sh --target opencode        # OpenCode default
./install.sh --target claude          # Claude Code default
./install.sh --target all             # Both targets
./install.sh --target auto            # Auto-detect (default)
```

## Targets

- `opencode`: installs skill to `~/.agents/skills/engineer-shovel/`, commands to `~/.config/opencode/commands/` (Windows: `%APPDATA%\opencode\commands\`).
- `claude`: installs skill to `~/.claude/skills/engineer-shovel/`, commands to `~/.claude/commands/` (Windows: `%USERPROFILE%\.claude\commands\`).
- `all`: installs to both targets.
- `auto`: detects `opencode` first, then `claude`; defaults to OpenCode paths if neither found.

## Scope

```bash
./install.sh --scope global   # Home directory (default)
./install.sh --scope local    # Project directory
```

Scope `global` uses `~/.agents/skills/`, `~/.config/opencode/`, `~/.claude/`. Scope `local` uses `./.agents/skills/`, `./.opencode/`, `./.claude/`. ECC skips local scope (no upstream project path). RTK always installs globally.

## Modes

### `--minimal`
Skill + slash commands only. No external dependencies.

```bash
./install.sh --target opencode --minimal
```

### `--recommended`
Skill + commands + Caveman + RTK + code-review-graph + superpowers + OpenSpec. Best default engineering stack without ECC/GSD orchestration.

```bash
./install.sh --target opencode --recommended
```

### `--full` (default)
Recommended components plus ECC and GSD. Use this when you want the full capability library ready, while still keeping daily execution on lightweight routes.

```bash
./install.sh --target opencode --full
./install.sh --target opencode --full --with-graph-build  # Also build initial graph
```

**Components installed by --full:**

| Component | OpenCode | Claude Code | Notes |
|-----------|---|---|---|
| Engineer Shovel | ✓ | ✓ | Always installed |
| ECC | ✓ (global) | ✓ (global) | Skipped for local scope |
| OpenSpec | ✓ | ✓ | CLI only; project init remains explicit via `openspec init` |
| GSD | ✓ | ✓ | Via `npx get-shit-done-cc@latest`; full mode only |
| code-review-graph | ✓ | ✓ | Via `pipx` or `pip`, then configured |
| Caveman | ✓ | ✓ | Uses upstream installer |
| superpowers | ✓ | ✓ | Plugin entry per target |
| RTK | ✓ | ✓ | System binary, always global |

OpenSpec requires Node.js 20.19.0 or newer. If Node is too old, installation continues with an actionable warning; run `npm install -g @fission-ai/openspec@latest` after upgrading Node.

Engineer Shovel does not automatically run `openspec init` because that writes project files. Initialize OpenSpec per repository only when durable specs are useful:

```bash
openspec init
openspec change create "add dark mode"
```

## Dry Run

Preview paths and pinned sources without making changes:

```bash
./install.sh --target all --recommended --dry-run
```

## Sync & Update

Use `/tool-update` as the user-facing entry point:

```text
/tool-update --check --target both --scope global
/tool-update --full --target both --scope global
```

Internal scripts still exist, but they now have narrower roles:

```bash
python3 scripts/sync.py check   # router files only
python3 scripts/sync.py sync    # router files only
python3 scripts/health.py check --target both --scope global
python3 scripts/health.py repair --target both --scope global
python3 scripts/startup-check.py  # quick health check on session start
```

Responsibility split:

- `install.sh`: first install and explicit repair hooks
- `scripts/sync.py`: Engineer Shovel router files and version sync
- `scripts/health.py`: external component health and repair
- `scripts/dependency_manifest.json`: shared component strategy metadata for health/reporting/docs
- `/tool-update`: user-facing orchestrator over sync + health

`/tool-update --check` should be read in two passes:

- Router drift: `current` / `missing` / `outdated` / `extra`
- Component health: `ok` / `missing` / `unconfigured` / `blocked` / `manual-upgrade-recommended`

Scope notes:

- Router sync supports both `--scope global` and `--scope local`.
- Health checks now accept `--scope`, but component support is intentionally uneven:
  - RTK, Caveman, superpowers, claude-mem, and OpenSpec are effectively global integrations.
  - GSD can be checked against the selected scope.
  - ECC local scope is not supported and is reported as blocked instead of auto-repaired.
- `--dry-run` on health/update skips repair writes; read-only status probes may still run.

Upgrade notes:

- `install.sh` is for first install.
- `/tool-update --full` is the normal post-install maintenance path.
- Automatic repair is intentionally narrower than "upgrade everything":
  - missing and unconfigured components may be repaired automatically
  - blocked scope/platform cases are reported explicitly
  - some components remain manual upgrade paths by design

Dry-run note:

- `install.sh --dry-run` now prefers non-interactive defaults even in a TTY.
- Defaults for dry-run preview are `--target auto --scope global` unless flags override them.

## Supply Chain

- External helper repos pinned to explicit commit SHAs in `install.sh`.
- `--full` invokes upstream installers after pinned checkout verification.
- `--dry-run` preview recommended before bootstrapping unfamiliar machines.
- Dependency lock strategy is documented in `docs/dependency-policy.md`.
- Component strategy metadata is also recorded in `scripts/dependency_manifest.json` to reduce drift between docs and health reporting.

## Configuration File

Engineer Shovel supports a configuration file for version-controlled settings:

```yaml
# .engineer-shovel.yaml (project root or home directory)
version: "1.7.5"
defaults:
  mode: standard
  target: opencode
  scope: global
aliases:
  q: quick
  f: fix
tools:
  code-review-graph:
    enabled: true
    cache_ttl: 300
cache:
  enabled: true
smart_mode:
  enabled: true
health_check:
  on_startup: true
```

See `.engineer-shovel.yaml` in the repository root for the full template.

## Startup Health Check

On session start, run a quick health check:

```bash
python3 scripts/startup-check.py
```

Output:
```
🪖 Engineer Shovel — Health Check
========================================
✅ Caveman: installed
✅ RTK: installed
✅ Code Review Graph: installed
⚠️ Superpowers: not configured
⚠️ OpenSpec: not installed
========================================
📊 5/7 tools ready
💡 Most tools ready. Use /tool-update --check for details.
```

## Non-interactive Default

In non-interactive contexts: `--target auto --scope global --full`. Use explicit flags for scripts and CI.

## Windows (PowerShell)

Use `install.ps1` for native Windows support (PowerShell 5+ or PowerShell Core 7+):

```powershell
# Quick start (default: full, auto-detect)
powershell -c "iex (iwr -useb https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.ps1)"

# Explicit parameters
powershell -c "iex (iwr -useb https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.ps1)" -- -Mode full -Target opencode -Scope global

# Minimal install
powershell -c "iex (iwr -useb https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.ps1)" -- -Mode minimal

# Dry run
powershell -c "iex (iwr -useb https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.ps1)" -- -DryRun
```

Or download first:

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.ps1 -OutFile install.ps1
Get-Content install.ps1 | Select-Object -First 50  # inspect
.\install.ps1 -Mode full -Target opencode
```

### Windows limitations

- **ECC** is not supported on Windows; use WSL for ECC features.
- **RTK** requires manual install from GitHub releases.
- **Caveman** uses the upstream PowerShell installer.
- **code-review-graph** uses `uvx` (via pip/uv) to run the MCP server.
- **claude-mem** requires Bun (install separately).

For the best experience on Windows, consider using [WSL](https://learn.microsoft.com/en-us/windows/wsl/) and running `install.sh` within the Linux environment.
