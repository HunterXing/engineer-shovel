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

## What Is This?

Engineer Shovel is a lightweight workflow router for OpenCode and Claude Code.

It exposes a small set of `/tool-*` commands for everyday work, while keeping heavier systems such as OpenSpec, ECC, GSD, Caveman, RTK, and code-review-graph as optional capability layers. Full capability may be installed, but normal execution should still stay lightweight by default.

The runtime `SKILL.md` stays intentionally small. Long-form policy lives in `docs/` so routine sessions do not keep paying for the full manual.

## Command Selection

| If the task is... | Use | Why |
|---|---|---|
| Small obvious edit | `/tool-quick` | Fastest path for 1-2 file low-risk work |
| Bug, regression, failing test | `/tool-fix` | Reproduce, isolate, fix, verify |
| New behavior to add | `/tool-feat` | Smallest verifiable feature slice |
| Scope/order/acceptance unclear | `/tool-plan` | Clarifies what to do before execution |
| Review itself is the task | `/tool-review` | Focus on findings, not implementation |
| A decision needs evidence | `/tool-research` | Gather local, web, or deep evidence |
| Branch/graph/update maintenance | `/tool-branch`, `/tool-graph`, `/tool-update` | Platform lifecycle operations |

## Default Shape

- Main workflow: `/tool-quick`, `/tool-fix`, `/tool-feat`, `/tool-plan`
- Support workflow: `/tool-review`, `/tool-refactor`, `/tool-research`
- Platform workflow: `/tool-branch`, `/tool-graph`, `/tool-update`
- Core principle: most work should stop at the main workflow layer

`plan`, `review`, and `research` are not mandatory front doors. External tools are upgrade layers, not default ceremony.

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

This remains the intended experience even in `--full`: capability is available, but the default path should still be light.

### Tool Fit At A Glance

- `code-review-graph`: use for multi-file reasoning, impact radius, review context, and refactors; skip it for tiny obvious edits.
- `superpowers`: use when the task needs better method, TDD, or systematic debugging; do not treat it as a generic capability bundle.
- `ECC`: use for framework, security, research, and integration depth; not for ordinary local code lookup.
- `OpenSpec`: use when agreement must persist as specs/tasks in files.
- `GSD`: use for phased, cross-session, or parallelized delivery.
- `caveman` and `rtk`: compression layers only; they do not replace planning or code intelligence.

## Install Vs Update

- `install.sh`: first install, explicit bootstrap, and installer-owned repair hooks
- `/tool-update --check`: compare router files, inspect component health, classify drift, repairable issues, blocked states, and manual upgrade paths
- `/tool-update --full`: sync router files first, then run supported repair actions and re-verify health
- `--scope global|local`: router sync supports both; some components remain effectively global and are reported that way instead of pretending local repair exists

## Cost Modes

| Mode | Use when | Typical path |
|---|---|---|
| `--fast` | low-risk, known target | `/caveman lite`, direct edit, targeted verification |
| `--standard` | normal development | `/caveman full`, targeted graph context, implementation, tests/build, light review |
| `--deep` | ambiguous, high-risk, multi-system | `/caveman full` or `ultra`, deliberate use of OpenSpec/ECC/GSD |

RTK is complementary when installed: it compresses noisy Bash/tool outputs such as git, tests, builds, and logs before they enter model context. It only helps on shell-command paths; built-in file tools such as `Read`, `Grep`, and `Glob` bypass RTK hooks.

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

## Escalation Layers

- `code-review-graph`: code understanding and impact analysis for multi-file work
- `caveman`: communication compression
- `rtk`: Bash/tool output compression
- `OpenSpec`: durable specs and tasks
- `ECC`: specialized architecture, security, framework, and research guidance
- `GSD`: milestone, multi-phase, or cross-session orchestration

These layers exist to solve specific problems. Installing them does not mean every task should use them.

## Structure

```text
engineer-shovel/
├── .github/           # CI and Pages workflows
├── commands/          # 12 executable slash commands (10 active + 2 legacy redirects)
├── docs/              # long-form references kept out of runtime context
├── pages/             # static project site assets
├── scripts/           # sync and validation utilities
├── SKILL.md           # lightweight router
├── install.sh         # minimal/recommended/full installer
├── README.md
├── README_zh.md
└── LICENSE
```

## Documentation

- Toolchain architecture: [`docs/architecture.md`](docs/architecture.md)
- Scenario routing: [`docs/command-scenarios.md`](docs/command-scenarios.md)
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
