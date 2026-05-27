# Changelog

## 1.7.5 (2026-05-27)

### Added
- **Toolchain Awareness**: All 10 commands now announce external tool usage with `🚀 **Tool Name** → action` format, making it impossible to miss which tools are powering the workflow.
- **Error Handling**: Added comprehensive error handling sections to all command files with clear recovery paths.
- **Quality Checklists**: Added verification checklists to `tool-plan`, `tool-review`, and `tool-refactor` commands.

### Fixed
- **install.ps1**: Fixed PowerShell syntax error (`/* */` → `#`) and removed references to non-existent commands (brainstorm, blueprint).
- **paths.py**: Fixed target key inconsistency by adding `claude-code` alias for `claude`.
- **tests**: Fixed typo in test assertions (`write_mcp_confg` → `write_mcp_config`).

### Changed
- **install.sh**: Added version display, improved success summary with next steps, and better error reporting.
- **SKILL.md**: Added Error Recovery section and Toolchain Awareness specification.
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
