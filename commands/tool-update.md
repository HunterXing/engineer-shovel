---
description: Update and synchronize engineer-shovel installation — sync skill, commands, and components
argument-hint: [--check|--full] [--target opencode|claude|both]
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

Synchronize Engineer Shovel files and verify supporting component health.

## Modes

- `--check` or default: Compare installed Engineer Shovel files and check base dependencies plus recommended/full components. Read-only.
- `--full`: Update Engineer Shovel files, then install/configure missing low-risk components using official installers.

## Target Scope

- `--target opencode`: Update OpenCode installation only
- `--target claude`: Update Claude Code installation only  
- `--target both`: Update both targets (default)

## Flow

1. Detect installed locations based on target(s).
2. Compare local installed files with latest repo versions.
3. Report missing, outdated, or extra files.
4. Check component health for base tools and recommended/full integrations.
5. If `--full`: overwrite installed files and repair missing/unconfigured components.
6. Verify installation integrity after update.

## Component Health

Checks base tools: `git`, `python3`, `pipx`, `node`, `npx`, plus selected runtimes (`opencode`, `claude`).

Checks recommended/full components: RTK, Caveman, code-review-graph, superpowers, OpenSpec, ECC, and GSD.

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

## Missing Component Guidance

When a component is missing or broken, suggest the install command (e.g. `pipx install code-review-graph`, `npm install -g @fission-ai/openspec@latest`, `npx get-shit-done-cc@latest`) instead of silently skipping.

## Compression

Use L2: `/caveman-review` style for check mode output. RTK not needed for sync operations.
