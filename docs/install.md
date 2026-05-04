# Installation Modes

`install.sh` supports interactive setup and non-interactive flags for OpenCode, Claude Code, or both.

```bash
./install.sh --target opencode        # OpenCode default
./install.sh --target claude          # Claude Code default
./install.sh --target all             # Both targets
./install.sh --target auto            # Auto-detect (default)
```

## Targets

- `opencode`: installs skill to `~/.agents/skills/engineer-shovel/`, commands to `~/.config/opencode/commands/`.
- `claude`: installs skill to `~/.claude/skills/engineer-shovel/`, commands to `~/.claude/commands/`.
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
Recommended components plus ECC and GSD. Use this when you want the full capability library and deep project orchestration.

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
/opsx:propose "add dark mode"
```

## Dry Run

Preview paths and pinned sources without making changes:

```bash
./install.sh --target all --recommended --dry-run
```

## Sync & Update

Use `/tool-update` or `scripts/sync.py`:

```bash
python3 scripts/sync.py check
python3 scripts/sync.py sync
```

## Supply Chain

- External helper repos pinned to explicit commit SHAs in `install.sh`.
- `--full` invokes upstream installers after pinned checkout verification.
- `--dry-run` preview recommended before bootstrapping unfamiliar machines.

## Non-interactive Default

In non-interactive contexts: `--target auto --scope global --full`. Use explicit flags for scripts and CI.
