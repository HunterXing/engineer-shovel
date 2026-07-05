# Changelog

## 1.8.0 (2026-07-05)

> Minor bump: adds a new user-facing capability (`/tool-update --full` auto-upgrades drift) and aligns the install surface to the latest upstream tags (ECC v2, GSD v1.50, superpowers v6, Caveman v1.9, RTK 0.43, claude-mem v13). Backward compatible — every existing `STATUS_OK` for an in-sync install stays OK.

### Added
- **Version drift detection in `/tool-update --full`**: `scripts/health.py` now probes the installed version of each component (rtk via `--version`, code-review-graph via uvx, openspec via `--version`, gsd via VERSION file, ecc + claude-mem + superpowers-claude via npm cache package.json, caveman detection deferred since v1.9+ drops version metadata) and compares it to a fresh upstream query (live `npm view` / GitHub raw `package.json` / Cargo.toml). When drift is detected, the OK status is downgraded to a new `STATUS_OUTDATED`, which is now part of `can_auto_repair` + `needs_repair` so `/tool-update --full` triggers a real upgrade. Every `repair_xxx()` path uses the upstream installer (`npm install -g @latest`, `git clone + node install.js`, `curl | bash -s -- --force`, etc.) which is already latest-installer — so re-running them upgrades for real rather than no-oping. Hardcoded `LATEST_KNOWN` dict in `scripts/health.py` provides offline-safe baseline; live queries fall back to it on failure. Documented in `commands/tool-update.md` under "Version Drift Detection".
- **GitHub Pages sync (`pages/`)**: upstream version table now matches the README 1:1 — OpenSpec `@fission-ai/openspec@latest`, ECC v2.0.0, GSD v1.50.0-canary.0, superpowers v6.1.1, code-review-graph v2.3.6, claude-mem v13.10.0, Caveman v1.9.1, RTK v0.43.0. Quick Start section gains Step 04 ("Stay on Latest") showing `/tool-update --check` and `/tool-update --full` invocations + a tip describing the verified end-to-end drift auto-repair path. Hero badge bumped from v1.7.4 to v1.8.0. New `.step-tip` CSS rule in `pages/styles/main.css` for the inline callout. ZH i18n descriptions in `pages/scripts/main.js` rewritten to match the new upstream capabilities.

### Changed
- **Upstream version alignment + functional adaptation**:
  - README tables (and the matching test in `tests/test_validation_scripts.py`) now declare each upstream tool at its currently published latest tag. Specifically: ECC v2.0.0, GSD **v1.50.0-canary.0**, superpowers v6.1.1, code-review-graph v2.3.6, Caveman v1.9.1 (was wrongly labeled `v0.1.0 (installer)`; GitHub tag is `v1.9.1`), RTK v0.43.0, OpenSpec `@fission-ai/openspec@latest`, claude-mem v13.10.0. New rows added for OpenSpec and claude-mem so the README version table mirrors the full install surface.
  - **ECC v2 functional adaptation**: v2 rewrote its installer to a Node wrapper (`scripts/install-apply.js`) that requires `--target <opencode|claude>` — without it the adapter errors out. `install.sh` `install_ecc` and `scripts/health.py` `repair_ecc` both now pass `--target` derived from the resolved `TARGETS` array; the repair flow also pre-installs `node_modules` if missing so the Node entry doesn't fail on a fresh checkout.
  - **Caveman v1.9.1 adaptation**: pinned `CAVEMAN_INSTALLER_URL` from `main` to `v1.9.1` for first-install determinism (Node wrapper with `--only <target>` flag forwarding unchanged). `scripts/dependency_manifest.json` `repair_hint` updated to the matching curl|bash invocation.
- **Caveman v1.9.1 actual install + install.sh flag forwarding fix**: prior to this change the engineer's `install_caveman_for_target` built `agent_flag="--only opencode"` as a single string and forwarded it as one argv element to the caveman shim. caveman v1.9.1's `install.js` parses that as one unknown flag (`error: unknown flag: --only opencode`) and the install silently failed (recorded as `failure` but no second-chance recovery). Fix: split into an array `agent_args=(--only opencode)` so each word is a separate argv token; also pass `--force` for clean re-runs and skip empty `mode_flag` (a trailing empty arg parses as another unknown flag in v1.9.1). Verified end-to-end on this host: 6 commands (`caveman.md`, `caveman-{commit,compress,help,review,stats}.md`), 7 skills (`caveman` + 6 sub-skills + `cavecrew`), 3 agents (`cavecrew-{investigator,builder,reviewer}`), 1 plugin at `~/.config/opencode/plugins/caveman/`, and the caveman ruleset appended to `~/.config/opencode/AGENTS.md`. Detection updated to recognize the v1.9.1 layout (`plugins/caveman/` + `commands/caveman.md`) since the legacy `~/.agents/skills/caveman/SKILL.md` path is no longer created.
- **install.sh superpowers wrapper bug**: `local cmd_name="$1" skill_name="$2" desc="$3" target="$cmd_dir/superpowers:${cmd_name}.md"` declared four `local` variables on one line; bash with `set -u` would resolve the right-hand expressions in the outer scope (where `cmd_name` was unset). Moved to separate `local` statements so each assignment binds before the next is evaluated. This had been silently truncating install.sh execution whenever a fresh superpowers install hit the wrapper-generation phase.
  - **GSD v1.50.0-canary.0 adaptation**: the npm `get-shit-done-cc@latest` package is deprecated; upstream rewrote the installer under TÂCHES at `1.50.0-canary.0`. `install.sh` `install_gsd` and `scripts/health.py` `repair_gsd` both now go through `git clone --depth=1` + `npm install` + `node bin/install.js --<runtime> --<scope>` instead of `npx`. Added `GSD_REPO` URL constant alongside the other repo URLs.
  - **superpowers v6 Claude Code adaptation**: v6 is published through the obra/superpowers marketplace (`superpowers-dev`), not the claude-plugins-official marketplace (which still carries v5.1.0). `install.sh` `install_superpowers_claude` and `scripts/health.py` `repair_superpowers(runner, "claude")` now first add `https://github.com/obra/superpowers` and install `superpowers@superpowers-dev`; the v5 path via `superpowers@claude-plugins-official` is kept as the fallback. Verified end-to-end on this host: `/root/.claude/plugins/cache/superpowers-dev/superpowers/6.1.1/` is now the active install.
  - `docs/token-cost.md` rtk-panic caveat updated to reflect the fix in ≥0.43.0.
- **ECC**: dependency strategy changed from `pinned` (fixed SHA `841beea4`) to `latest-installer`. `install.sh` now clones upstream HEAD at install/repair time; `scripts/health.py` reports missing ECC as auto-repairable instead of `manual-upgrade-recommended`. Aligns ECC with caveman/claude-mem/GSD update model. Trade-off: first-install determinism for ECC is no longer guaranteed; downstream users get upstream bug fixes without a manual bump.

### Fixed
- **code-review-graph**: plugin hook was disabled (`.disabled`) on the host while the MCP server itself remained wired. Re-enabled the hook so `crg-plugin.ts` runs and built the graph (279 nodes, 2478 edges in this repo).
- **rtk**: upgraded bundled `rtk` from 0.37.2 to 0.43.0, lifting the documented `rtk gain --history` non-ASCII-path panic.
- **ECC v2 npm-published path**: ECC v2 upstream rewrote its installer to a Node entry that needs a separate `npm run build:opencode` step when invoked via the git clone path. Discovered that the npm-published `ecc-universal@latest` package ships pre-built artifacts and exposes an `ecc-install` bin pointing at `scripts/install-apply.js` — this avoids the build step entirely. `install.sh` `install_ecc` and `scripts/health.py` `repair_ecc` now prefer `npm install -g ecc-universal@latest && ecc-install --target opencode --profile opencode`; the git clone path is kept as fallback. Verified end-to-end on this host: 102 commands / 33 agents / install-state at `/root/.opencode/ecc-install-state.json`.
- **ECC v2 marker detection**: prior `check_ecc` (post-v2 install) was reporting MISSING because v2 drops files directly into `~/.config/opencode/{commands,agents,hooks,skills}/` rather than creating a dedicated `~/.config/opencode/ecc/` marker dir. Detection now reads a curated set of distinctive ECC command file names and treats both real files and symlinks into the ECC plugin cache as evidence.
- **GSD install path**: prior `npx -y get-shit-done-cc@latest` invocation would only yield the deprecated 1.42.3 npm line; the new git-clone + node bin/install.js path actually fetches the canary 1.50.0 build from upstream main.
- **superpowers Claude install path**: prior `claude plugin install superpowers@claude-plugins-official` invocation would resolve to v5.1.0 (still the only version on that marketplace); the new obvia marketplace path yields v6.1.1.
- **superpowers OpenCode install source pinning**: `opencode plugin superpowers` (bare name) silently resolves to the unrelated npm `superpowers@0.0.2` placeholder package (a `"TODO: description"` empty stub by `01studio`) rather than obra's plugin. The `opencode plugin` command then happily registers that placeholder as if the install succeeded, so the active OpenCode plugin never actually loaded any of obra's code. Discovered when verifying the cache: `/root/.cache/opencode/packages/superpowers@latest/node_modules/superpowers/lib/superpowers.js` is a no-op stub, while the real plugin lives in `superpowers@github:obra/superpowers/node_modules/superpowers/.opencode/plugins/superpowers.js` — only fetched when the user explicitly says `superpowers@github:obra/superpowers`. Fix: `install.sh`, `install.ps1`, `scripts/health.py`, `scripts/dependency_manifest.json`, `README*`, and `commands/tool-update.md` now all use the github-source spec. User-level + project-level `opencode.json` `plugin` arrays migrated from `"superpowers"` to `"superpowers@github:obra/superpowers"`; stale `@latest` placeholder cache was cleared. Verified end-to-end on this host: the active install is `6.1.1` from `cache/superpowers@github:obra/...`.

## 1.7.5 (2026-05-27)

### Added
- **Command Aliases**: New `/tool-alias` command with short aliases (`/q`, `/f`, `/fe`, `/p`, `/r`, `/rf`, `/rs`, `/b`, `/g`, `/u`) for faster workflow.
- **Startup Health Check**: New `scripts/startup-check.py` for automatic tool availability checking on session start.
- **Smart Mode Recommendation**: Auto-detection of task complexity to recommend `--fast`, `--standard`, or `--deep` mode.
- **Cache Layer**: Intelligent caching for code-review-graph queries (impact_radius, architecture_overview, test_coverage) with configurable TTL.
- **Configuration as Code**: New `.engineer-shovel.yaml` configuration file for version-controlled settings.
- **Progressive Disclosure**: New `SKILL-lite.md` for ultra-lightweight Level 1 loading (essential commands only).
- **Toolchain Awareness**: All 10 commands now announce external tool usage with `🚀 **Tool Name** → action` format, making it impossible to miss which tools are powering the workflow.
- **Error Handling**: Added comprehensive error handling sections to all command files with clear recovery paths.
- **Quality Checklists**: Added verification checklists to `tool-plan`, `tool-review`, and `tool-refactor` commands.

### Fixed
- **install.ps1**: Fixed PowerShell syntax error (`/* */` → `#`) and removed references to non-existent commands (brainstorm, blueprint).
- **paths.py**: Fixed target key inconsistency by adding `claude-code` alias for `claude`.
- **tests**: Fixed typo in test assertions (`write_mcp_confg` → `write_mcp_config`).

### Changed
- **install.sh**: Added version display, improved success summary with next steps, and better error reporting.
- **SKILL.md**: Added Error Recovery section, Toolchain Awareness specification, Quick Start guide, Command Aliases, Smart Mode Recommendation, and Cache Layer documentation.
- **scripts/health.py**: Added timeouts (300s) and better exception handling for subprocess calls.
- **scripts/sync.py**: Added permission error handling for file operations.
- **commands**: Enhanced all 10 commands with toolchain announcements and boundary condition checks.

## 1.7.4 (2026-05-26)

### Added
- **Windows support**: New `install.ps1` PowerShell installer for native Windows (PowerShell 5+/Core 7+).
- **Cross-platform OS detection**: `install.sh` now auto-detects macOS, Linux, and Windows (WSL/Git Bash), with platform-specific hints.

### Fixed
- **superpowers installation**: Changed from manually editing `opencode.json` to `opencode plugin superpowers` command, compatible with OpenCode 1.15+.
- **code-review-graph MCP config**: Replaced the old `code-review-graph install --platform opencode` approach (which wrote unrecognized `.opencode.json` format) with proper OpenCode 1.15 `mcp` key format in `.opencode/opencode.json`. Uses `uvx code-review-graph serve` with `type: "local"`.

### Changed
- `download_file()` now falls back to `wget` if `curl` is unavailable.
- Pre-requisite checks now show platform-specific install hints (brew, apt).
- `ensure_tmp_root()` has a more portable fallback for systems without `mktemp`.

## 1.7.3 (2026-05-10)

### Changed
- Synchronized version markers and product wording across `SKILL.md`, `docs/architecture.md`, GitHub Pages, and the public documentation surface so the router, docs, and site describe the same routing model.
- Updated GitHub Pages route-picker copy and workflow descriptions to match the current command boundaries, especially around `/tool-quick`, `/tool-fix`, `/tool-feat`, `/tool-plan`, and `/tool-update`.
- Refined the GitHub Pages `Choose Your Route` grid so six cards align cleanly in a balanced desktop layout instead of rendering as four cards on the first row and two on the second.

## 1.7.2 (2026-05-10)

### Changed
- Tightened the product message across `README.md`, `README_zh.md`, `SKILL.md`, and `docs/architecture.md` around the lightweight-router model: main workflow first, support routes second, capability layers only when needed.
- Clarified command ownership across planning and execution docs: `/tool-plan` now owns planning, `/tool-feat` assumes the feature is ready to build, `/tool-review` is framed as a support task, and `/tool-research` is explicitly positioned as decision-focused evidence gathering.
- Updated `docs/mode-routing.md` and GitHub Pages to explain that `/tool-research` uses a special `--quick / --web / --deep` evidence axis instead of the main `--fast / --standard / --deep` execution-cost axis.
- Added a visual command-route picker to GitHub Pages while keeping the README command-selection table as the text-first reference.
- Fixed `scripts/sync.py` so the `sync` path calls `compare_files()` with the correct arguments, restoring the router-sync path behind `/tool-update --full`.
- Expanded validation coverage for product-shape rules and sync behavior in `scripts/validate-references.py` and `tests/test_validation_scripts.py`.

## 1.7.1 (2026-05-08)

### Changed
- Unified command routing docs around executable routes only: removed direct references to unavailable skill names and replaced them with existing `/tool-*` routes plus capability-layer descriptions.
- Clarified security handling across the router: security-sensitive work now promotes to the matching deep route and adds `/tool-review --deep` before sign-off.
- Tightened command ownership: `/tool-review` now defaults to reporting findings rather than mutating code, `/tool-branch` is framed as explicit lifecycle control, and `/tool-update` defaults to `--check` as the recommended mode.
- Updated `README.md`, `README_zh.md`, `docs/architecture.md`, `docs/install.md`, `docs/token-cost.md`, and `docs/mode-routing.md` to match the revised routing model.
- Synced GitHub Pages content with the same route model, replacing outdated references such as `caveman-review`, `github-ops`, `writing-plans`, `blueprint`, `review-work`, and dedicated security-review skills.

## 1.7.0 (2026-05-04)

### Added
- **Layer 1.5: Session Memory** — claude-mem for auto-capture cross-session memory (decisions, preferences, bug history, architectural context).
- claude-mem install integration in `install.sh` for recommended and full modes.
- `check_claude_mem()` and `repair_claude_mem()` health checks in `scripts/health.py`.
- Memory routing added to 6 command files: `/tool-feat`, `/tool-fix`, `/tool-plan`, `/tool-research`, `/tool-review`, `/tool-refactor`.
- Memory system documentation in `SKILL.md`, `CLAUDE.md`, and `AGENTS.md`.
- `docs/dependency-policy.md` to document router-vs-component update boundaries and dependency lock strategy.

### Changed
- `docs/architecture.md`: Layer Architecture diagram expanded with Layer 1.5, Cost Mode Routing table added Memory column, Command × Tool Matrix added claude-mem column.
- Tool Overview table in architecture.md now includes claude-mem.
- Router docs now emphasize `full capability available, lightweight execution by default`.
- `/tool-update` is documented as the single user-facing update entry point, with `scripts/sync.py` narrowed to router sync and `scripts/health.py` narrowed to component health.

### Upstream Dependency Changes

- Clarified dependency governance by separating router updates from component repair/upgrade flows.
- Documented which tools are pinned, floating, or mixed-strategy in `docs/dependency-policy.md`.

## 1.6.0 (2026-05-04)

### Changed
- Added OpenSpec as an optional durable spec layer for `/tool-plan` and `/tool-feat`.
- Changed recommended install mode to include the core engineering stack: Caveman, RTK, code-review-graph, superpowers, and OpenSpec.
- Changed standard feature/fix completion from GSD-heavy gates to native verification plus light review. GSD gates are now deep/milestone-oriented by default.
- Updated GitHub Pages and multilingual README content to describe 10 active commands, 7 upstream tools, and the lighter standard path.

### Security
- OpenSpec installation checks Node.js >=20.19.0 and never auto-runs `openspec init`, avoiding surprise project writes.

## 1.5.0 (2026-05-04)

### Changed
- **P0**: 所有 8 个活跃命令添加具体 CRG MCP 工具调用指令 (`semantic_search_nodes`, `get_impact_radius`, `query_graph`, `get_affected_flows`, `detect_changes`, `get_review_context`, `refactor_tool`, `get_architecture_overview`)，替换模糊的 "use graph for impact analysis"。
- **P0**: SKILL.md 新增 `Caveman Mode Mapping (Enforced)` 统一映射表，消除 6 个命令间的模式不一致。
- **P1**: `/tool-feat` 和 `/tool-fix` 新增 GSD 验证闭环：`--standard` 用 `gsd-verify-work → caveman-review`，`--deep` 用 `gsd-verify-work → gsd-code-review → gsd-ship`。
- **P1**: Security Gate 集中化到 SKILL.md (`Cross-cutting Security Gate`)；命令文件保留自包含 1 行版本，独立可用。
- RTK 触发改为智能策略：仅预期输出 >500 行时使用，替换无差别调用。
- ECC 子层拆分：L4a Pattern Reference (自动加载), L4b Specialized Process, L4c Operational。
- 旧 `L4: ecc:xxx` / `L5: superpowers:xxx` / `L6: gsd-xxx` 前缀统一为 `skill(name="xxx")`。
- `docs/architecture.md` 全面更新：Cost Mode Routing、Command×Tool Matrix、Exclusive Routing、RTK Trigger Points、Token Consumption 表对齐新架构。

## 1.4.0 (2026-05-03)

### Changed
- **P0**: code-review-graph now auto-refreshed via git hooks — removed all "if installed" conditionals from 5 commands (`quick`, `fix`, `feat`, `refactor`, `review`). Graph queries are always-on in pre-action phase.
- **P0**: ecc capabilities fully deployed: `ecc:deep-research` added to `fix --deep`, `ecc:council` added to `feat --deep` and `plan --deep`, `ecc:github-ops` added to `review`, `ecc:review-work` added to `feat --deep`.
- **P1**: `/tool-brainstorm` deprecated — brainstorming internalized as Phase 0 in `/tool-feat` and `/tool-plan` with auto-trigger.
- **P1**: `/tool-blueprint` deprecated — merged into `/tool-plan --deep` with automatic complexity classification (≤3 PR → `ecc:blueprint`, >3 PR → `gsd project`).
- **P1**: Unified `Verification Gate` added to all code-modifying commands (`quick`, `fix`, `feat`, `refactor`): test → graph impact → caveman review → report.
- `/tool-graph` demoted to diagnostic-only; graph refresh handled by git hooks.
- `superpowers:receiving-code-review` integrated into `/tool-review` post-feedback flow.

### Architecture
- Active commands: 8 (`quick`, `fix`, `feat`, `plan`, `refactor`, `review`, `research`, `update`)
- Deprecated (redirect): 2 (`brainstorm`, `blueprint`)
- Utility (kept): 2 (`branch`, `graph`)
- Updated 5-layer architecture: Layer 1 compression, Layer 2 auto-managed graph, Layer 3 superpowers methodology, Layer 4 ecc expertise, Layer 5 gsd project management.

---

## 1.3.0 (2026-05-02)

### Changed
- Slimmed `SKILL.md` into a lightweight router and moved long-form references into `docs/`.
- Added token-aware `--fast`, `--standard`, and `--deep` cost modes to slash commands.
- Changed installer default to recommended mode with explicit `--minimal`, `--recommended`, and `--full` options.
- Reduced default use of high-cost workflows such as `/review-work`, `/gsd-debug`, and deep research.

### Added
- `docs/architecture.md`, `docs/token-cost.md`, `docs/install.md`, and `docs/language-reference.md`.
- CI guardrails for command frontmatter, token-efficiency footers, skill size, docs presence, and shell syntax.
- `/tool-graph` command for manual code-review-graph status, full build, incremental update, rebuild, and watch workflows.
- `/tool-branch` command for feature branch workflow management with squash merge and diff review.

---

## 1.1.0 (2026-05-01)

### Changed
- Renamed project to `engineer-shovel` (工兵铲)
- GitHub repo: `HunterXing/engineer-shovel`
- Skill name: `skill(name="engineer-shovel")`

### Added
- 9 standalone slash commands: `/tool-feat`, `/tool-fix`, `/tool-plan`, `/tool-refactor`, `/tool-review`, `/tool-brainstorm`, `/tool-quick`, `/tool-blueprint`, `/tool-research`
- Mermaid decision flowchart in README
- Chinese documentation (`README_zh.md`)
- One-command bootstrap installer (`install.sh`)

### Removed
- Legacy duplicate toolchain alias from toolchain declarations

---

## 1.0.0 (2026-05-01)

### Added
- Initial release of the workflow router
- SKILL.md covering 8 development scenarios
- Dual environment support: OpenCode and Claude Code
- Decision trees and token management guide
