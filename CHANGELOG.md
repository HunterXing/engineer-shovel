# Changelog

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
