# Token Cost Model

Engineer Shovel uses cost-aware escalation: start cheap, verify, escalate only when needed.

## Main Cost Drivers

1. Large always-loaded skill files.
2. Repeated workflow definitions in both skill and command files.
3. Durable spec and deep review/orchestration paths (OpenSpec artifacts, `/tool-review --deep`, GSD phase execution).
4. Multi-source research workflows.
5. Loading broad skill sets for small tasks.

## Cost Tiers

| Tier | Typical trigger | Examples |
|------|----------------|----------|
| Low | Known file, small diff | `/caveman lite`, `/tool-quick`, `/tool-review --fast` |
| Medium | Normal feature/fix/refactor | `/caveman full`, `/tool-feat`, `/tool-fix`, optional OpenSpec, `/tool-plan` |
| High | Ambiguous, cross-system, high-risk | `/caveman full` or `/caveman ultra`, `/tool-plan --deep`, GSD, `/tool-research --deep`, `/tool-review --deep` |

## Caveman Defaults

Caveman is the default compression layer. Mode is chosen by workflow risk:

| Workflow | Default compression | Why |
|----------|-------------------|-----|
| `/tool-quick --fast` | `/caveman lite` | Tiny edits readable, boilerplate trimmed |
| `/tool-fix --standard` | `/caveman full` | Bug context grows through logs/tests |
| `/tool-feat --standard` | `/caveman full` | Keeps normal feature work compact while avoiding deep GSD gates |
| `/tool-refactor --standard` | `/caveman full` | Before/after verification compact |
| `/tool-review --fast` | Caveman review mode | Review findings compress well |
| `/tool-plan --deep` | `/caveman full` | Plans and dependency graphs verbose |
| `/tool-research --deep` | `/caveman ultra` when context pressure high | Multi-source research overwhelms |

Use `/caveman ultra` when multiple agents run, outputs are mostly summaries, or context usage is high. Stay on `lite` when human readability matters.

## RTK Policy

RTK compresses Bash/tool outputs (git, tests, builds, logs) before they enter LLM context — filtering, grouping, truncating, deduplicating. It complements Caveman (which compresses LLM communication). They are independent layers and stack.

Use RTK for: git status/diff/log, test/build output, long directory listings, repeated logs/stack traces.

## Default Policy

- Low-cost tools for small, deterministic work.
- Standard workflows for normal implementation.
- Use OpenSpec only when requirements/specs/design/tasks need durable reviewable artifacts.
- High-cost agents only for high-risk reasoning, security, architecture, broad refactors, milestone work, or repeated failures.
- Targeted verification before broad review.
- Caveman compression before escalating to broader agents.
- RTK-wrapped shell output for noisy commands.

## Practical Savings

The runtime `SKILL.md` is a lightweight router. Long-form explanations live in `docs/`, not loaded per session. Use `scripts/token-benchmark.py` for static size estimates.

## Session Statistics

Use upstream tools directly:
- Caveman statistics: `/caveman-stats`.
- RTK statistics: `rtk gain --project --format json` (project), `rtk gain` (global), `rtk session` (adoption).
- code-review-graph: `/tool-graph status`.
- OpenSpec: `openspec --version`; initialize per project with `openspec init` only when specs are needed.
- RTK hook audit: `rtk hook-audit` (requires `RTK_HOOK_AUDIT=1`).
- Avoid `rtk gain --history` (may panic on non-ASCII paths in RTK 0.37.2).
