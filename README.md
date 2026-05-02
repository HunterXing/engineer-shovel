<h1 align="center">🪖 Engineer Shovel</h1>

<p align="center">
  <b>Token-aware AI agent development workflow router</b><br>
  <sub>Quick Tasks · Bug Fix · Feature · Branch · Plan · Refactor · Review · Brainstorm · Blueprint · Research · Statistics · Sync</sub>
</p>

<p align="center">
  <code>/tool-quick</code> <code>/tool-fix</code> <code>/tool-feat</code> <code>/tool-branch</code> <code>/tool-plan</code> <code>/tool-refactor</code> <code>/tool-review</code> <code>/tool-brainstorm</code> <code>/tool-blueprint</code> <code>/tool-research</code> <code>/tool-statistic</code> <code>/tool-update</code>
</p>

---

## What is this?

Engineer Shovel is a lightweight skill + slash-command pack for OpenCode and Claude Code. It routes development work to the cheapest workflow that can still verify the outcome, then escalates to deeper agent workflows only when risk requires it.

The runtime `SKILL.md` is intentionally small; long-form documentation lives in `docs/` so routine sessions do not pay for the full manual.

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
/tool-statistic --fast
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
| `/tool-feat` | New functionality |
| `/tool-branch` | Branch workflow: create, review, merge, abort |
| `/tool-plan` | Requirements and implementation planning |
| `/tool-refactor` | Behavior-preserving cleanup |
| `/tool-review` | Local diff, PR, or deep review |
| `/tool-brainstorm` | Clarify ideas before building |
| `/tool-blueprint` | Multi-step or multi-session projects |
| `/tool-research` | Evidence gathering and synthesis |
| `/tool-statistic` | Session token usage and savings report |
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

- Full workflows: [`docs/workflows.md`](docs/workflows.md)
- Token cost model: [`docs/token-cost.md`](docs/token-cost.md)
- Installation modes: [`docs/install.md`](docs/install.md)
- Language reference: [`docs/language-reference.md`](docs/language-reference.md)
- Repository assessment: [`docs/assessment.md`](docs/assessment.md)

## License

MIT — see [LICENSE](LICENSE).
