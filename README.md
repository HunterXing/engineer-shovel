<h1 align="center">🪖 Engineer Shovel</h1>

<p align="center">
  <b>Token-aware AI agent development workflow router</b><br>
  <sub>Quick Tasks · Bug Fix · Feature · Branch · Plan · Refactor · Review · Brainstorm · Blueprint · Research · Graph · Sync</sub>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README_zh.md">简体中文</a> |
  <a href="README.ja-JP.md">日本語</a> |
  <a href="README.ko-KR.md">한국어</a>
</p>

<p align="center">
  <a href="https://github.com/HunterXing/engineer-shovel/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/HunterXing/engineer-shovel?style=flat-square"></a>
  <a href="https://github.com/HunterXing/engineer-shovel/forks"><img alt="GitHub forks" src="https://img.shields.io/github/forks/HunterXing/engineer-shovel?style=flat-square"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square"></a>
  <img alt="Commands" src="https://img.shields.io/badge/commands-12-5865F2?style=flat-square">
  <img alt="OpenCode" src="https://img.shields.io/badge/OpenCode-supported-2ea44f?style=flat-square">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-supported-6f42c1?style=flat-square">
</p>

---

## What is this?

Engineer Shovel is a lightweight skill + slash-command pack for OpenCode and Claude Code. It routes development work to the cheapest workflow that can still verify the outcome, then escalates to deeper agent workflows only when risk requires it.

The runtime `SKILL.md` is intentionally small; long-form documentation lives in `docs/` so routine sessions do not pay for the full manual.

## Capability Boundary

Native Engineer Shovel installs the lightweight router and 12 `/tool-*` commands. The deeper capabilities advertised in full workflows come from optional external tools installed or configured by recommended/full modes: ECC, GSD, superpowers, code-review-graph, Caveman, and RTK.

Minimal installs are intentionally small. If a workflow mentions external commands such as GSD, ECC, Caveman, RTK, or code-review-graph behavior, those capabilities require the corresponding optional tool to be installed and healthy.

## Quick Start

```bash
# Download, inspect, then run (default: full mode with all components)
curl -fsSL -o install.sh https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh
less install.sh
bash install.sh

# Non-interactive: full install for OpenCode (default)
bash install.sh --target opencode

# Non-interactive: full install for both OpenCode and Claude Code
bash install.sh --target all

# Shortcut if you already trust the source:
# curl -fsSL https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh | bash

# Other modes
./install.sh --target opencode --recommended  # Skill + commands + Caveman
./install.sh --target opencode --minimal      # Skill + commands only
./install.sh --target opencode --full --with-graph-build  # Also build initial code-review-graph index
```

The installer verifies pinned external repository SHAs before staging optional dependencies. Download-first installation is safer than piping directly into Bash because it lets you inspect the script and avoids server-side pipe detection differences.

## Compatibility Notes

This optimization cycle keeps the public interface stable:

- `skill(name="engineer-shovel")` is unchanged.
- All 12 `/tool-*` commands remain installed with the same names.
- `--minimal`, `--recommended`, `--full`, and `--dry-run` are unchanged.
- `--target opencode|claude|all|auto` lets fresh machines choose OpenCode, Claude Code, or both explicitly.

New guardrails added:

- Download-first installation is now the recommended documented path.
- The installer keeps SHA pin verification and now surfaces clearer failure behavior around external installer execution.
- Validation scripts now have lightweight pytest regression coverage.

Then use either:

```text
skill(name="engineer-shovel")
```

or call a command directly:

```text
/tool-quick --fast "fix typo in README"
/tool-review --fast
/tool-research --deep "compare options for X"
/tool-graph update
```

## Cost Modes

| Mode | Use when | Typical path |
|---|---|---|
| `--fast` | low-risk, known target | `/caveman lite`, direct edit, `/gsd-fast`, Caveman review |
| `--standard` | normal development | `/caveman full`, targeted search, implementation, tests/build |
| `--deep` | ambiguous, high-risk, multi-system | `/caveman full` or `ultra`, GSD, deep research, Oracle/review-work |

RTK is complementary when installed: it compresses noisy Bash/tool outputs such as git, tests, builds, and logs before they enter model context.

## Commands

| Command | Use for |
|---|---|
| `/tool-quick` | Obvious small edits |
| `/tool-fix` | Bugs, failing tests, regressions |
| `/tool-feat` | New functionality (auto-brainstorms) |
| `/tool-branch` | Branch workflow: create, review, merge, abort |
| `/tool-plan` | Requirements and planning (auto-escalates to blueprint/gsd) |
| `/tool-refactor` | Behavior-preserving cleanup |
| `/tool-review` | Local diff, PR, or deep review |
| `/tool-brainstorm` | **[DEPRECATED]** — use `/tool-feat` or `/tool-plan` |
| `/tool-blueprint` | **[DEPRECATED]** — use `/tool-plan --deep` |
| `/tool-research` | Evidence gathering and synthesis (codebase-aware) |
| `/tool-graph` | code-review-graph diagnostics (auto-refreshed) |
| `/tool-update` | Sync and update installation |

## Structure

```text
engineer-shovel/
├── commands/          # 12 executable slash commands
├── docs/              # long-form references kept out of runtime context
├── scripts/           # sync and validation utilities
├── SKILL.md           # lightweight router
├── install.sh         # minimal/recommended/full installer
├── README.md
├── README_zh.md
└── LICENSE
```

## Documentation

- Toolchain architecture: [`docs/architecture.md`](docs/architecture.md)
- Token cost model: [`docs/token-cost.md`](docs/token-cost.md)
- Installation modes: [`docs/install.md`](docs/install.md)
- Language reference: [`docs/language-reference.md`](docs/language-reference.md)

## License

MIT — see [LICENSE](LICENSE).

## Upstream Tool Versions

Engineer Shovel integrates and configures these upstream tools in `--full` mode.

| Tool | Repository | Current referenced version | Role |
|---|---|---:|---|
| ECC | https://github.com/affaan-m/everything-claude-code | v1.10.0 | AI agent harness performance system: skills, rules, hooks, MCP, security, research-first workflows |
| GSD | https://github.com/gsd-build/get-shit-done | v1.39.0 | Spec-driven planning, phase execution, verification, and context engineering |
| superpowers | https://github.com/obra/superpowers | v5.0.7 | Mandatory skill workflows: brainstorming, TDD, planning, review, branch finishing |
| code-review-graph | https://github.com/tirth8205/code-review-graph | v2.3.2 | Local code knowledge graph, MCP review context, blast-radius analysis |
| Caveman | https://github.com/JuliusBrussee/caveman | v1.7.0 | Output-token compression, terse review/commit helpers, MCP shrink |
| RTK | https://github.com/rtk-ai/rtk | v0.38.0 | Shell and tool output compression proxy plus command rewrite hooks |
