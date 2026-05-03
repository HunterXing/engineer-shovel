# /tool-update Component Health Design

## Goal

Extend `/tool-update` so it does more than synchronize Engineer Shovel files. It must also check whether the local machine has the required base dependencies and Full-mode components installed and configured. When run in full mode, it should install or configure missing pieces using the same official or project-approved paths documented by `install.sh` and `docs/install.md`.

In `--full`, Engineer Shovel should make architecture-level default choices instead of asking the user for every component detail. The default policy is: install and configure the complete productivity stack when it has low runtime cost and reversible configuration; avoid only choices that add persistent background processes, high context overhead, telemetry, secrets, or broad language-specific rule payloads without project evidence.

## Current Behavior

`scripts/sync.py` compares repository files with installed Engineer Shovel files:

- `SKILL.md`
- `commands/tool-*.md`

It does not check external components such as `code-review-graph`, GSD, RTK, Caveman, superpowers, ECC, or base executables like `python3`, `pipx`, `npx`, `claude`, and `opencode`.

## Proposed Architecture

Add a new script, `scripts/health.py`, responsible for component health checks and repair actions. Keep `scripts/sync.py` focused on file synchronization.

`/tool-update` will become the orchestration command:

- `--check`: run file sync check and health check without installing or modifying external components.
- `--full`: run file sync, then run health repair for missing or unconfigured components.
- `--target opencode|claude|both`: pass target scope to both sync and health checks.

This keeps the existing sync behavior stable while making component checks explicit and testable.

## Default Configuration Policy

`--full` is an opinionated best-practice install. It should choose sensible defaults automatically:

- Install missing CLI tools and agent integrations when they are required by the Full-mode stack.
- Configure integrations that are idle unless invoked, such as slash commands, skills, MCP server entries, hooks, and plugin references.
- Prefer official installers and official plugin/marketplace paths over hand-copying when upstream supports them.
- Prefer global installation for developer-machine tooling unless the user explicitly asks for local scope.
- Do not start persistent background daemons, watch processes, or long-running services without explicit approval.
- Do not enable telemetry or cloud-backed optional services unless upstream defaults are already opt-in.
- Do not install every language/framework rule pack when that would increase session context. Install common/core rules by default; install language-specific rules only when project files indicate that stack or the user selects it.
- Preserve and back up existing config before editing it.

## Health Check Scope

The health checker covers base dependencies plus Full-mode components.

Base dependencies:

- `git`
- `python3`
- `pipx`
- `node`
- `npx`
- `opencode`, when target includes OpenCode
- `claude`, when target includes Claude Code

Full-mode components:

- `code-review-graph`
- GSD / `get-shit-done-cc`
- `superpowers`
- Caveman
- RTK
- ECC

## Component Rules

These rules are aligned with the upstream installation docs for the supported components:

- ECC: `https://github.com/affaan-m/everything-claude-code`
- GSD: `https://github.com/gsd-build/get-shit-done`
- superpowers: `https://github.com/obra/superpowers`
- code-review-graph: `https://github.com/tirth8205/code-review-graph`
- Caveman: `https://github.com/JuliusBrussee/caveman`
- RTK: `https://github.com/rtk-ai/rtk`

### code-review-graph

Check:

- `command -v code-review-graph`
- `code-review-graph status`, when installed
- whether `.code-review-graph/` exists in the current git repository

Repair in `--full`:

- Install with `pipx install code-review-graph` when `pipx` exists.
- Fall back to `python3 -m pip install --user code-review-graph` when needed.
- Run `code-review-graph install` to let the official installer auto-detect and configure all supported platforms, including MCP/rules.
- If the user requested a single target and the upstream CLI supports that platform flag, prefer `code-review-graph install --platform <platform>` for a narrower configuration.
- Run `code-review-graph build` inside git worktrees.
- Do not start `code-review-graph watch` or `crg-daemon` automatically.

### superpowers

OpenCode check:

- Inspect `~/.config/opencode/opencode.json` for the plugin entry `superpowers@git+https://github.com/obra/superpowers.git`.

Claude check:

- Run `claude plugin list` and search for `superpowers`.

Repair in `--full`:

- OpenCode: follow the upstream `.opencode/INSTALL.md` path. The known stable configuration is adding `superpowers@git+https://github.com/obra/superpowers.git` to the `plugin` array in `~/.config/opencode/opencode.json`, preserving existing config and writing a backup first.
- Claude: run `claude plugin install superpowers@claude-plugins-official`.
- Install for all requested targets because the plugin/skill surface is idle until invoked and does not start background work by itself.

### Caveman

OpenCode check:

- Check `~/.agents/skills/caveman`, `~/.agents/skills/JuliusBrussee-caveman`, or `~/.config/opencode/commands/caveman.md`.
- Optionally use `npx skills list` when available.

Claude check:

- Check `claude plugin list` for Caveman.
- Check `~/.claude/plugins/caveman` as a fallback signal.

Repair in `--full`:

- Prefer the official Caveman installer URL already used by `install.sh`.
- Pass `--only <agent>` when repairing a single target, or let the official installer auto-detect when target is `both`.
- For Claude manual fallback, use `claude plugin marketplace add JuliusBrussee/caveman && claude plugin install caveman@caveman`.
- For OpenCode manual fallback, use `npx skills add JuliusBrussee/caveman -a opencode`.
- Use the default installer mode for `--full` because Caveman's token-saving hooks/statusline are aligned with Engineer Shovel's token-efficiency goal. Do not enable per-repo rule drops unless the upstream installer does so for the selected mode or the user asks for repository-local activation.

### RTK

Check:

- `command -v rtk`

Repair in `--full`:

- Use the official RTK installer from `install.sh`.
- Run `rtk init -g --opencode` when target includes OpenCode.
- Run `rtk init -g` when target includes Claude Code.
- Use `rtk init --show` as a verification command when available.
- Keep upstream telemetry defaults; do not explicitly enable telemetry.

### GSD

Check:

- Look for installed GSD directories or manifest files in the target config paths.
- Treat absence as missing.

Repair in `--full`:

- Run `npx -y get-shit-done-cc@latest` with the official non-interactive target and scope flags.
- Use `--opencode --global` for OpenCode global installs.
- Use `--claude --global` for Claude Code global installs.
- Use `--all --global` for both targets. Do not use undocumented aliases unless the installed package confirms support.
- Use the default/full GSD install, not `--minimal`, because `/tool-update --full` means the user opted into the complete workflow surface.

### ECC

Check:

- For Claude Code, check plugin state via `claude plugin list` for `everything-claude-code@everything-claude-code` or check manual install markers when the plugin is absent.
- Check rules under `~/.claude/rules/ecc/`, because upstream docs require rules to be copied separately when using the Claude plugin path.
- For manual installs, look for ECC-managed files or install-state markers in Claude/OpenCode config directories.

Repair in `--full`:

- For Claude Code, prefer the upstream plugin path: `claude plugin marketplace add https://github.com/affaan-m/everything-claude-code` followed by `claude plugin install everything-claude-code@everything-claude-code`.
- Install ECC core/common rules when using the plugin path because upstream says rules are required and they do not add a runtime process.
- Install language-specific ECC rules only when the current project has matching files, for example TypeScript/JavaScript, Python, Go, PHP, Swift, Rust, or Java markers. Do not copy every language pack by default because rules increase always-loaded context.
- For manual ECC installs, use `./install.sh --profile full --target <target>` from a cloned, pinned checkout when practical.
- If a safe direct repair is not practical, report the exact manual command from upstream docs and mark the component as blocked rather than silently skipping it.

## Safety Rules

- `--check` is read-only.
- `--full` may install or configure missing components, but must not delete user files.
- `--full` may make best-practice configuration choices without asking when the change is reversible, idle by default, and aligned with upstream official setup.
- JSON config edits must preserve existing keys and create a backup first.
- Background daemons or watch processes must not be started.
- Broad rule packs, telemetry, cloud credentials, and persistent background services require explicit user approval.
- Failures are actionable and visible in the final report.
- Component repair should continue where safe so one missing component does not hide all later findings.

## Output Design

Use compact output suitable for `/tool-update`:

```text
FILES
- opencode: OK 13/13
- claude: OK 13/13

BASE
- git: OK
- python3: OK
- pipx: MISSING

COMPONENTS
- code-review-graph: MISSING, install available
- superpowers/opencode: CONFIGURED
- superpowers/claude: MISSING

STATUS
- check: needs repair
- next: /tool-update --full --target both
```

In `--full`, output should include what was changed and the final verification result.

## Testing

Add tests for pure detection and report logic where possible. Avoid tests that install real external tools.

Test cases:

- Missing executable detection.
- Target-specific dependency selection.
- File sync check still reports current/missing/outdated files.
- Health report distinguishes `missing`, `installed`, `configured`, `unconfigured`, and `blocked`.
- Dry-run or check mode does not write files.

## Open Decision

ECC repair may need a conservative first implementation because its install path depends on pinned external checkout behavior in `install.sh`. The first version can detect ECC and provide exact repair guidance if direct repair would duplicate too much installer logic.
