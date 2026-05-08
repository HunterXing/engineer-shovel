# Changelog

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
