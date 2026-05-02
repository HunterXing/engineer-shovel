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

Synchronize the installed engineer-shovel skill and commands with the latest repository version.

## Modes

- `--check` or default: Compare installed files with latest repo and report missing/outdated.
- `--full`: Update all installed components (skill, commands, hooks) to latest version.

## Target Scope

- `--target opencode`: Update OpenCode installation only
- `--target claude`: Update Claude Code installation only  
- `--target both`: Update both targets (default)

## Flow

1. Detect installed locations based on target(s).
2. Compare local installed files with latest repo versions.
3. Report missing, outdated, or extra files.
4. If `--full`: overwrite installed files with latest versions.
5. Verify installation integrity after update.

## Compression

Use Caveman review style for check mode output. RTK not needed for sync operations.
