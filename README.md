<h1 align="center">🪖 Engineer Shovel</h1>

<p align="center">
  <b>Token-aware AI agent development workflow router</b><br>
  <sub>Quick Tasks · Bug Fix · Feature · Plan · Refactor · Review · Brainstorm · Blueprint · Research · Statistics</sub>
</p>

<p align="center">
  <code>/tool-quick</code> <code>/tool-fix</code> <code>/tool-feat</code> <code>/tool-plan</code> <code>/tool-refactor</code> <code>/tool-review</code> <code>/tool-brainstorm</code> <code>/tool-blueprint</code> <code>/tool-research</code> <code>/tool-statistic</code>
</p>

---

## What is this?

Engineer Shovel is a lightweight skill + slash-command pack for OpenCode and Claude Code. It routes development work to the cheapest workflow that can still verify the outcome, then escalates to deeper agent workflows only when risk requires it.

The runtime `SKILL.md` is intentionally small; long-form documentation lives in `docs/` so routine sessions do not pay for the full manual.

## Quick Start

```bash
# Default: recommended mode (skill + commands + Caveman staging)
curl -fsSL https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh | bash

# Minimal: only engineer-shovel skill and slash commands
./install.sh --minimal

# Full: ECC/GSD + superpowers + Caveman + RTK + engineer-shovel
./install.sh --full
```

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
| `/tool-plan` | Requirements and implementation planning |
| `/tool-refactor` | Behavior-preserving cleanup |
| `/tool-review` | Local diff, PR, or deep review |
| `/tool-brainstorm` | Clarify ideas before building |
| `/tool-blueprint` | Multi-step or multi-session projects |
| `/tool-research` | Evidence gathering and synthesis |
| `/tool-statistic` | Session token usage and savings report |

## Structure

```text
engineer-shovel/
├── commands/          # 10 executable slash commands
├── docs/              # long-form references kept out of runtime context
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

## License

MIT — see [LICENSE](LICENSE).
