# Changelog

## 1.2.0 (2026-05-02)

### Changed
- Slimmed `SKILL.md` into a lightweight router and moved long-form references into `docs/`.
- Added token-aware `--fast`, `--standard`, and `--deep` cost modes to slash commands.
- Changed installer default to recommended mode with explicit `--minimal`, `--recommended`, and `--full` options.
- Reduced default use of high-cost workflows such as `/review-work`, `/gsd-debug`, and deep research.

### Added
- `docs/workflows.md`, `docs/token-cost.md`, `docs/install.md`, and `docs/language-reference.md`.
- CI guardrails for command frontmatter, token-efficiency footers, skill size, docs presence, and shell syntax.
- `/tool-graph` command for manual code-review-graph status, full build, incremental update, rebuild, and watch workflows.
- `/tool-branch` command for feature branch workflow management with squash merge and diff review.

---

## 1.1.0 (2026-05-01)

### Changed
- Renamed project from `optimal-workflow` to `engineer-shovel` (工兵铲)
- GitHub repo: `HunterXing/optimal-workflow` → `HunterXing/engineer-shovel`
- Skill name: `skill(name="engineer-shovel")`

### Added
- 9 standalone slash commands: `/tool-feat`, `/tool-fix`, `/tool-plan`, `/tool-refactor`, `/tool-review`, `/tool-brainstorm`, `/tool-quick`, `/tool-blueprint`, `/tool-research`
- Mermaid decision flowchart in README
- Chinese documentation (`README_zh.md`)
- One-command bootstrap installer (`install.sh`)

### Removed
- `omo` from toolchain declarations (duplicate of OpenCode)

---

## 1.0.0 (2026-05-01)

### Added
- Initial release as `optimal-workflow`
- SKILL.md covering 8 development scenarios
- Dual environment support: OpenCode and Claude Code
- Decision trees and token management guide
