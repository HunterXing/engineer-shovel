<h1 align="center">🪖 Engineer Shovel</h1>

<p align="center">
  <b>Token-aware AI agent development workflow router</b><br>
  <sub>Quick Tasks · Bug Fix · Feature · Branch · Plan · Refactor · Review · Research · Graph · Sync</sub>
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
  <img alt="Commands" src="https://img.shields.io/badge/commands-10_active-5865F2?style=flat-square">
  <img alt="OpenCode" src="https://img.shields.io/badge/OpenCode-supported-2ea44f?style=flat-square">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-supported-6f42c1?style=flat-square">
</p>

---

## What is this?

Engineer Shovel is a skill + slash-command router for OpenCode and Claude Code. It installs a broad engineering stack when requested, but routes daily programming work to the lightest path that can still verify the outcome.

The runtime `SKILL.md` is intentionally small; long-form documentation lives in `docs/` so routine sessions do not pay for the full manual.

## Default Shape

- Install philosophy: full capability can be present by default.
- Execution philosophy: lightweight by default, deeper layers only when justified.
- Main workflow commands: `/tool-quick`, `/tool-fix`, `/tool-feat`, `/tool-plan`
- Support commands: `/tool-review`, `/tool-refactor`, `/tool-research`
- Platform commands: `/tool-branch`, `/tool-graph`, `/tool-update`

Most teams should spend most of their time in `quick`, `fix`, and `feat`. `plan`, `review`, and `research` are support routes, while OpenSpec, ECC, and GSD are deliberate escalation layers rather than mandatory daily steps.

## Capability Boundary

Native Engineer Shovel installs the lightweight router and `/tool-*` commands. Deeper capabilities come from optional external tools installed or configured by recommended/full modes: OpenSpec, ECC, GSD, superpowers, code-review-graph, Caveman, and RTK.

Minimal installs are intentionally small. If a workflow mentions external commands such as GSD, ECC, Caveman, RTK, or code-review-graph behavior, those capabilities require the corresponding optional tool to be installed and healthy.

Even in `--full`, those tools are treated as capability layers with distinct jobs:

- `code-review-graph`: code understanding and impact analysis
- `caveman`: communication compression
- `rtk`: shell/tool output compression
- `superpowers`: session-scoped clarification/debug/TDD discipline
- `ECC`: specialized guidance for architecture, security, research, and integration tradeoffs
- `OpenSpec`: durable specs/tasks
- `GSD`: multi-phase orchestration

Security-sensitive work should not stay on a routine path: promote it to the matching deep route and add `/tool-review --deep` before sign-off.

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
./install.sh --target opencode --recommended  # Core stack: Caveman, RTK, CRG, superpowers, OpenSpec
./install.sh --target opencode --minimal      # Skill + commands only
./install.sh --target opencode --full --with-graph-build  # Also build initial code-review-graph index
```

The installer verifies pinned external repository SHAs before staging optional dependencies. Download-first installation is safer than piping directly into Bash because it lets you inspect the script and avoids server-side pipe detection differences.

## Compatibility Notes

This optimization cycle keeps the public interface stable:

- `skill(name="engineer-shovel")` is unchanged.
- All `/tool-*` command names remain stable; 10 are active and 2 legacy redirects remain installed for compatibility.
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
/tool-fix --standard "investigate failing login test"
/tool-feat --standard "add smallest verifiable feature slice"
/tool-plan --standard "plan rollout for X"
```

## Practical Routing

- 80% of work: `/tool-quick`, `/tool-fix`, `/tool-feat`
- 15% of work: `/tool-plan`, `/tool-review`, `/tool-research`
- 5% of work: explicit escalation to OpenSpec, ECC, or GSD

This is the intended user experience even when `--full` is installed: full capability available, lightweight execution by default.

## Cost Modes

| Mode | Use when | Typical path |
|---|---|---|
| `--fast` | low-risk, known target | `/caveman lite`, direct edit, targeted verification |
| `--standard` | normal development | `/caveman full`, targeted graph context, implementation, tests/build, light review |
| `--deep` | ambiguous, high-risk, multi-system | `/caveman full` or `ultra`, deliberate use of OpenSpec/ECC/GSD |

RTK is complementary when installed: it compresses noisy Bash/tool outputs such as git, tests, builds, and logs before they enter model context.

## Commands

| Group | Command | Use for |
|---|---|---|
| Main workflow | `/tool-quick` | Obvious small edits |
| Main workflow | `/tool-fix` | Bugs, failing tests, regressions |
| Main workflow | `/tool-feat` | New functionality (auto-clarifies) |
| Main workflow | `/tool-plan` | Requirements and planning |
| Engineering support | `/tool-review` | Local diff, PR, or deep review |
| Engineering support | `/tool-refactor` | Behavior-preserving cleanup |
| Engineering support | `/tool-research` | Evidence gathering and synthesis |
| Platform support | `/tool-branch` | Branch workflow: create, review, merge, abort |
| Platform support | `/tool-graph` | code-review-graph diagnostics |
| Platform support | `/tool-update` | Router sync, component health, repair guidance |

Legacy redirects still installed for compatibility: `/tool-brainstorm` and `/tool-blueprint`.

## Structure

```text
engineer-shovel/
├── commands/          # 12 executable slash commands (10 active + 2 legacy redirects)
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
- Global mode routing: [`docs/mode-routing.md`](docs/mode-routing.md)
- Token cost model: [`docs/token-cost.md`](docs/token-cost.md)
- Installation modes: [`docs/install.md`](docs/install.md)
- Dependency policy: [`docs/dependency-policy.md`](docs/dependency-policy.md)
- Language reference: [`docs/language-reference.md`](docs/language-reference.md)

## License

MIT — see [LICENSE](LICENSE).

## Upstream Tool Versions

Engineer Shovel integrates and configures these upstream tools in `--full` mode.

| Tool | Repository | Current referenced version | Role |
|---|---|---:|---|
| OpenSpec | https://github.com/Fission-AI/OpenSpec | latest | Spec-driven artifacts: proposal, specs, design, tasks, verify, archive |
| ECC | https://github.com/affaan-m/everything-claude-code | v1.10.0 | AI agent harness performance system: skills, rules, hooks, MCP, security, research-first workflows |
| GSD | https://github.com/gsd-build/get-shit-done | v1.39.0 | Deep project orchestration, phase execution, verification, and context engineering |
| superpowers | https://github.com/obra/superpowers | v5.0.7 | Method layer for clarification, TDD, debugging, and verification discipline |
| code-review-graph | https://github.com/tirth8205/code-review-graph | v2.3.2 | Local code knowledge graph, MCP review context, blast-radius analysis |
| Caveman | https://github.com/JuliusBrussee/caveman | v1.7.0 | Output-token compression, terse review/commit helpers, MCP shrink |
| RTK | https://github.com/rtk-ai/rtk | v0.38.0 | Shell and tool output compression proxy plus command rewrite hooks |
