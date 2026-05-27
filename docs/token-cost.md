# Token Cost Model

Engineer Shovel uses cost-aware escalation: start cheap, verify, escalate only when needed.

## Main Cost Drivers

1. Large always-loaded skill files.
2. Repeated workflow definitions in both skill and command files.
3. Durable spec and deep review/orchestration paths (OpenSpec artifacts, `/tool-review --deep`, GSD phase execution).
4. Multi-source research workflows.
5. Loading broad skill sets for small tasks.
6. **Repeated queries** — same impact/architecture queries in one session.

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

## Cache Layer

Cache reduces redundant queries within a session:

| Operation | TTL | Token Savings |
|-----------|-----|---------------|
| `impact_radius` | 5 min | ~80% |
| `architecture_overview` | 30 min | ~90% |
| `test_coverage` | 10 min | ~70% |
| `callers_of` | 5 min | ~80% |
| `callees_of` | 5 min | ~80% |

**Cache behavior**:
- **Hit**: Use cached result, skip tool invocation → saves tokens
- **Miss**: Query tool normally, cache result
- **Stale**: TTL expired, re-query on next access
- **Invalidated**: File changed, cache cleared

**When to skip cache**:
- First query after commit
- Cross-session queries (use claude-mem instead)
- When fresh data is critical

## Default Policy

- Low-cost tools for small, deterministic work.
- Standard workflows for normal implementation.
- Use OpenSpec only when requirements/specs/design/tasks need durable reviewable artifacts.
- High-cost agents only for high-risk reasoning, security, architecture, broad refactors, milestone work, or repeated failures.
- Targeted verification before broad review.
- Caveman compression before escalating to broader agents.
- RTK-wrapped shell output for noisy commands.
- **Cache** repeated queries to save tokens.
- **Smart mode** auto-detects complexity when mode not specified.

## Smart Mode Recommendation

When user doesn't specify a mode, auto-detect based on signals:

| Signal | Recommended Mode | Token Impact |
|--------|------------------|--------------|
| Single file, obvious change | `--fast` | Lowest |
| Multiple files, clear scope | `--standard` | Medium |
| Cross-module, security, ambiguous | `--deep` | Higher |
| Bug with clear repro | `--fast` | Lowest |
| Bug without repro | `--standard` | Medium |
| New feature, clear spec | `--standard` | Medium |
| New feature, vague spec | `--deep` | Higher |

**Auto-escalation triggers** (→ `--deep`):
- Security-sensitive code
- More than 5 files affected
- Cross-module dependencies unclear

**Auto-de-escalation triggers** (→ `--fast`):
- Single file, obvious change
- No dependencies affected
- Clear verification path

## Practical Savings

The runtime `SKILL.md` is a lightweight router. Long-form explanations live in `docs/`, not loaded per session. Use `scripts/token-benchmark.py` for static size estimates.

## Session Statistics

Use upstream tools directly:
- Caveman statistics: `/caveman-stats`.
- RTK statistics: `rtk gain --project --format json` (project), `rtk gain` (global), `rtk session` (adoption).
- code-review-graph: `/tool-graph status`.
- OpenSpec: `openspec --version`; initialize per project with `openspec init` only when specs are needed.
- Cache: check cache hit rate with `/tool-graph status`.
- RTK hook audit: `rtk hook-audit` (requires `RTK_HOOK_AUDIT=1`).
- Avoid `rtk gain --history` (may panic on non-ASCII paths in RTK 0.37.2).

---

*Last updated: 2026-05-27 — v1.7.5*
