---
description: Update and synchronize engineer-shovel installation — sync skill, commands, and components
argument-hint: [--check|--full] [--target opencode|claude|both] [--scope global|local]
cost-profile: low
risk-level: low
recommended-mode: --full
allowed-tools: [Bash, Read, Grep]
escalates-to: []
depends-on: []
when-to-use: Use to update installed engineer-shovel files to latest version, check for missing commands, or refresh component installations.
---

# /tool-update — Sync & Update

**Input**: $ARGUMENTS

Single user-facing entry point for keeping Engineer Shovel current. It checks router files first, then component health, and only repairs what is actually needed.

## Modes

- `--check` or default: Read-only. Compare installed Engineer Shovel router files, then inspect base dependencies and optional components.
- `--full`: Sync Engineer Shovel router files first, then repair or upgrade missing/unconfigured components using supported installer paths.

## Target Scope

- `--target opencode`: Update OpenCode installation only
- `--target claude`: Update Claude Code installation only  
- `--target both`: Update both targets (default)
- `--scope global`: Check or repair home-directory installations (default)
- `--scope local`: Check or repair project-local router files and any components that actually support local scope

## Flow

### Router Sync (step 1-3)

There are two sync paths depending on the installation method:

**Path A: Git-based sync** (developer install, has `.git`)
1. Run `python3 scripts/sync.py check --target <target> --scope <scope>` to detect drift.
2. If `--full`: run `python3 scripts/sync.py sync --target <target> --scope <scope>` to update files.

**Path B: Direct download sync** (normal user install via `curl | bash`, no `.git`)
1. Detect installed skill file: `~/.agents/skills/engineer-shovel/SKILL.md` (global) or `./.agents/skills/engineer-shovel/SKILL.md` (local).
2. Read installed version from the `version:` field in SKILL.md frontmatter.
3. Fetch latest version: `curl -fsSL https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/SKILL.md` — extract version from frontmatter.
4. If versions differ (or `--full`): download each file from GitHub raw URL and overwrite installed files:
   - `SKILL.md` → skill directory
   - `commands/tool-{branch,feat,fix,plan,refactor,review,quick,research,graph,update,alias}.md` → commands directory
5. Report: `Upgraded: v<old> → v<new>` or `Already up to date: v<current>`.

**Fallback**: If Path A fails (no git, scripts missing), automatically use Path B.

### Component Health (step 4-7)

6. Check component health for base tools and recommended/full integrations.
   - When checking each component, announce: `🚀 **<component>** → checking health`
7. Classify component results as:
   - repairable automatically
   - blocked by scope/runtime/platform limits
   - manual upgrade recommended
8. If `--full`: repair missing or unconfigured components.
   - When repairing, announce: `🚀 **<component>** → repairing...`
9. Verify router integrity and component health after update.

### Toolchain Announcements

When checking or repairing components, announce them with maximum visibility:
- `🚀 **code-review-graph** → checking MCP config` — when verifying graph setup
- `🚀 **caveman** → checking installation` — when verifying caveman
- `🚀 **rtk** → checking binary` — when verifying RTK
- `🚀 **superpowers** → checking plugin` — when verifying superpowers
- `🚀 **claude-mem** → checking config` — when verifying memory system
- `🚀 **OpenSpec** → checking CLI` — when verifying OpenSpec
- `🚀 **GSD** → checking files` — when verifying GSD
- `🚀 **ECC** → checking installation` — when verifying ECC

## Internal Split

- `install.sh`: first install and explicit repair hooks
- `scripts/sync.py`: router file sync and version comparison only
- `scripts/health.py`: external component health and repair only
- `/tool-update`: user-facing orchestrator over both layers

## Component Health

Checks base tools: `git`, `python3`, `pipx`, `node`, `npx`, `uvx`, plus selected runtimes (`opencode`, `claude`).

Checks recommended/full components: RTK, Caveman, code-review-graph, superpowers, OpenSpec, ECC, and GSD.

Scope model:
- Router files fully support `global` and `local`.
- Some components remain effectively global even when the Engineer Shovel router is local, such as RTK, Caveman, superpowers, claude-mem, and OpenSpec.
- GSD can be checked against the selected scope.
- ECC local installs are not supported; report this explicitly instead of pretending repair is available.

OpenSpec policy:
- Install/check the global CLI only (`openspec`).
- Do not run `openspec init` automatically because it writes project files.
- If Node.js is older than 20.19.0, report an actionable warning and skip repair.

### Component Detection Details

| Component | Detection method | Repair path | Notes |
|---|---|---|---|
| **RTK** | `which rtk` | `curl ... install.sh` | System binary, always global |
| **Caveman** | filesystem markers / `claude plugin list` | upstream installer | Per-target check |
| **code-review-graph** | `which code-review-graph` or `which uvx` + MCP config check | `pipx install` + write MCP config | OpenCode: writes `.opencode/opencode.json` `mcp` key (new format). Claude Code: `code-review-graph install --platform claude-code`. Accepts `uvx` on-demand as alternative to local install. MCP config checked in both global and local locations. |
| **superpowers** | `opencode plugin superpowers` / config file string match | `opencode plugin superpowers -g` | OpenCode 1.15+: uses `opencode plugin` command. Falls back to git URL in config. |
| **claude-mem** | config string match / `claude plugin list` | `npx claude-mem install --ide ...` | Requires Bun. Blocked if Bun missing. |
| **GSD** | filesystem presence of `gsd-*.md` | `npx get-shit-done-cc@latest` | Respects scope and target. |
| **ECC** | filesystem markers / `claude plugin list` | upstream installer | Blocked for local scope. OpenCode repair is manual-only. |

MCP policy:
- code-review-graph MCP uses OpenCode 1.15+ `mcp` config format (`.opencode/opencode.json` with `type: "local"`), not the deprecated `.opencode.json` `mcpServers` format.
- Superpowers has no separate MCP auto-configuration step; it is configured as an OpenCode plugin or Claude Code plugin.
- ECC bundled MCPs are not auto-enabled by default because they may require credentials or duplicate user servers.

Safety:
- Does not start background watch/daemon processes.
- Does not enable telemetry explicitly.
- Does not delete user config.
- Backs up JSON config before editing.
- `--dry-run` skips repair writes; read-only health probes may still run so status stays accurate.

## Missing Component Guidance

When a component is missing or broken, suggest the install command (e.g. `pipx install code-review-graph`, `npm install -g @fission-ai/openspec@latest`, `npx get-shit-done-cc@latest`) instead of silently skipping.

When automatic repair is not supported, say that directly and report the manual path. Do not blur together:

- router drift
- component repair
- blocked local-scope support
- optional manual upgrades

## Error Handling

- If a component repair fails, report the specific error and suggest manual fix.
- If network is unavailable, skip remote checks and report local status only.
- If permission denied, suggest running with appropriate privileges.
- If component version conflicts exist, recommend clean reinstall.

## Positioning

- Remember this command as the only update entry point.
- Use `--check` for status, drift, and repair guidance.
- Use `--full` when you want router sync plus component repair/upgrade in one pass.
- Works for both git-based installs (developers) and curl-based installs (normal users). Path A uses `scripts/sync.py`; Path B downloads directly from GitHub.
- The underlying scripts present one mental model: router layer first, component layer second, with scope called out explicitly.

## Compression

Use concise Caveman-style summaries for check mode output. RTK is not needed for sync operations.
