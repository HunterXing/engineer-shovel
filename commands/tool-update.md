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

1. Detect installed locations based on target(s) and scope.
2. Compare local installed router files (`SKILL.md`, `/tool-*`) with latest repo versions.
3. Report router drift explicitly as: current, missing, outdated, or extra.
4. Check component health for base tools and recommended/full integrations.
5. Classify component results as:
   - repairable automatically
   - blocked by scope/runtime/platform limits
   - manual upgrade recommended
6. If `--full`: sync router files first, then repair missing or unconfigured components.
7. Verify router integrity and component health after update.

## Internal Split

- `install.sh`: first install and explicit repair hooks
- `scripts/sync.py`: router file sync and version comparison only
- `scripts/health.py`: external component health and repair only
- `/tool-update`: user-facing orchestrator over both layers

## Component Health

Checks base tools: `git`, `python3`, `pipx`, `node`, `npx`, plus selected runtimes (`opencode`, `claude`).

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

MCP policy:
- `code-review-graph install` may configure MCP/rules because upstream explicitly supports this.
- Superpowers has no separate MCP auto-configuration step; it is configured as a plugin/skills provider.
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

## Positioning

- Remember this command as the only update entry point.
- Use `--check` for status, drift, and repair guidance.
- Use `--full` when you want router sync plus component repair/upgrade in one pass.
- The underlying scripts present one mental model: router layer first, component layer second, with scope called out explicitly.

## Compression

Use concise Caveman-style summaries for check mode output. RTK is not needed for sync operations.
