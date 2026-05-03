# Installation Modes

`install.sh` supports interactive setup plus explicit non-interactive flags. In a terminal, running `./install.sh` asks whether to install for OpenCode, Claude Code, both, or auto-detection, then asks for the install mode. Use `--dry-run` with any mode to preview target paths and pinned external sources without writing files.

**Default mode is `--full`** which installs all components: ECC, GSD, superpowers, Caveman, RTK, engineer-shovel skill, and commands.

## Sync & Update

Use the `/tool-update` command or `scripts/sync.py` to check and update your installation:

```bash
# Check installation status
python3 scripts/sync.py check

# Check specific target
python3 scripts/sync.py check --target opencode

# Sync all files to latest version
python3 scripts/sync.py sync

# Dry-run sync (preview changes)
python3 scripts/sync.py sync --dry-run

# Sync specific target
python3 scripts/sync.py sync --target claude --scope global
```

Or use the slash command:
```
/tool-update check
/tool-update sync --target opencode
```

## Targets

Choose where the skill and slash commands are installed:

```bash
# Default: full mode with all components
./install.sh --target opencode
./install.sh --target claude
./install.sh --target all
./install.sh --target auto

# Explicit mode selection
./install.sh --target opencode --full        # Same as default
./install.sh --target opencode --recommended # Skill + commands + Caveman
./install.sh --target opencode --minimal     # Skill + commands only
```

- `opencode` installs the skill to `~/.agents/skills/engineer-shovel/` and commands to `~/.config/opencode/commands/`.
- `claude` installs the skill to `~/.claude/skills/engineer-shovel/` and commands to `~/.claude/commands/`.
- `all` installs the core skill and commands to both targets.
- `auto` detects `opencode` first, then `claude`; if neither command exists yet, it defaults to OpenCode paths so fresh OpenCode machines do not accidentally receive Claude-only commands.

## Scope

Scope controls whether files go to your home directory or the current project directory:

```bash
# Global scope (default) — home directory
./install.sh --target opencode --scope global --recommended

# Local scope — project directory
./install.sh --target opencode --scope local --recommended
```

Scope `global` installs to `~/.agents/skills/`, `~/.config/opencode/`, and `~/.claude/`. Scope `local` installs to `./.agents/skills/`, `./.opencode/`, and `./.claude/`.

Scope affects where engineer-shovel skill and commands are placed. ECC is **skipped for local scope** (no project-scoped ECC install path exists upstream). RTK is a system binary and **always installs globally** regardless of scope.

## Minimal

Installs only Engineer Shovel skill and slash commands. No external dependencies.

```bash
./install.sh --target opencode --minimal
./install.sh --target claude --minimal
./install.sh --target all --minimal
```

## Recommended

Installs Engineer Shovel plus Caveman when available. Best token-saving baseline without pulling in the full stack.

```bash
# OpenCode global — Caveman installed via npx skills
./install.sh --target opencode --scope global --recommended

# OpenCode local — Caveman falls back to global with a warning (upstream lacks project scope)
./install.sh --target opencode --scope local --recommended

# Claude Code global — Caveman installed via claude plugin system
./install.sh --target claude --scope global --recommended

# Claude Code local — Caveman falls back to user scope with a warning
./install.sh --target claude --scope local --recommended

# Both targets global
./install.sh --target all --scope global --recommended
```

## Full

Installs the full toolchain: **ECC**, **GSD**, **superpowers**, **Caveman**, **RTK**, plus the Engineer Shovel skill and slash commands.

```bash
# OpenCode global — all components
./install.sh --target opencode --scope global --full

# OpenCode local — ECC skipped (unsupported), RTK installs globally, GSD + Caveman use local paths
./install.sh --target opencode --scope local --full

# Claude Code global — all components
./install.sh --target claude --scope global --full

# Claude Code local — ECC skipped (unsupported), RTK global, GSD + Caveman use local paths
./install.sh --target claude --scope local --full

# Both targets global
./install.sh --target all --scope global --full
```

### What full mode installs

| Component | OpenCode | Claude Code | Notes |
|---|---|---|---|
| Engineer Shovel | ✓ | ✓ | Always installed |
| ECC | ✓ (global only) | ✓ (global only) | Skipped for local scope (no project path upstream) |
| GSD | ✓ | ✓ | Installed via `npx get-shit-done-cc@latest` independently |
| code-review-graph | ✓ | ✓ | Installed from PyPI via `pipx` or `pip`, then configured with `code-review-graph install` |
| Caveman | ✓ | ✓ | OpenCode: `npx skills add`; Claude: `claude plugin` commands |
| superpowers | ✓ | ✓ | OpenCode plugin entry or Claude marketplace plugin |
| RTK | ✓ | ✓ | System binary, always global regardless of scope selection; initialized with target-specific hooks |

### Component details

**ECC** (Everything Claude Code) is installed via its own installer: `bash <checkout>/install.sh --target <opencode|claude> --profile <core|full>`. It is pinned to an explicit commit SHA in this installer.

**GSD** (Get Shit Done) is installed independently via `npx get-shit-done-cc@latest --<target> --<scope>`. It is not bundled with ECC.

**code-review-graph** is installed using the upstream PyPI package: `pipx install code-review-graph` when `pipx` exists, otherwise `python3 -m pip install --user code-review-graph`. Full mode then runs `code-review-graph install` to configure MCP/rules and `code-review-graph build` for the current git repository.

**superpowers** is installed per target. For OpenCode, it adds a plugin entry to `~/.config/opencode/opencode.json`. For Claude Code, it uses `claude plugin install superpowers@claude-plugins-official`.

**Caveman** uses the official installer from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman). It auto-detects installed agents and runs their native install method. For Claude Code, it uses `claude plugin marketplace add && claude plugin install`. For OpenCode, it uses `npx skills add`.

**RTK** (Rust Token Killer) is installed as a system binary via the upstream install script, with pinned cargo fallback when available. It is then initialized with `rtk init -g` for Claude Code or `rtk init -g --opencode` for OpenCode. The binary always installs globally, not to the selected scope path.

## Dry Run

Preview the selected mode without copying files, cloning repositories, or appending memory hints:

```bash
./install.sh --target all --recommended --dry-run
```

Dry run output includes the selected target directories and pinned external sources that would be used.

## Supply Chain Notes

- External helper repositories are pinned to explicit commit SHAs in `install.sh`.
- Pinned clones are checked out in a temporary directory and verified with `git rev-parse HEAD` before files are staged or external installers are attempted.
- `--full` invokes upstream installer behavior for ECC and GSD after the pinned checkout is verified. Use `--dry-run` first when bootstrapping unfamiliar machines.
- If an optional dependency cannot be staged, the installer reports the specific failure and exits non-zero during final verification.

## Non-interactive Default

When no flag is provided in a terminal, the installer prompts for target and mode. In non-interactive contexts, it uses `--target auto --scope global --full`. Use `--target opencode`, `--target claude`, or `--target all` explicitly for scripts and CI.

## Compression Tools

- Caveman is recommended for most workflows and is installed by `--recommended` and `--full` when possible.
- RTK is optional but recommended in `--full` mode. It compresses Bash/tool outputs before they enter the LLM context; it does not compress model replies or prompts. Rust builds can be slow, so RTK is not included by default in recommended mode.
- Use `--full` when you intentionally want every supporting tool installed.
