# Token Cost Model

Engineer Shovel optimizes for cost-aware escalation: start cheap, verify, then escalate only when the task demands it.

## Main Cost Drivers

1. Large always-loaded skill files.
2. Repeating the same workflow in both skill and command files.
3. Multi-agent commands such as `/review-work` and GSD phase execution.
4. Multi-source research workflows.
5. Loading broad skill sets for small tasks.

## Cost Tiers

| Tier | Typical trigger | Examples |
|---|---|---|
| Low | Known file, small diff | `/caveman lite`, `/tool-quick`, `/tool-review --fast` |
| Medium | Normal feature/fix/refactor | `/caveman full`, `/tool-feat`, `/tool-fix`, `/tool-plan` |
| High | Ambiguous, cross-system, high-risk | `/caveman full` or `/caveman ultra`, `/tool-blueprint`, `/tool-research --deep`, `/review-work` |

## Caveman Defaults

Caveman should be treated as the default compression layer, not an emergency-only tool. Pick the mode by workflow risk:

| Workflow | Default compression | Why |
|---|---|---|
| `/tool-quick --fast` | `/caveman lite` | Keeps tiny edits readable while trimming boilerplate |
| `/tool-fix --standard` | `/caveman full` | Bug context can grow quickly through logs/tests |
| `/tool-feat --standard` | `/caveman full` | Reduces repeated planning and verification chatter |
| `/tool-refactor --standard` | `/caveman full` | Keeps before/after verification summaries compact |
| `/tool-review --fast` | Caveman review mode | Review findings compress well into one-line issues |
| `/tool-blueprint` | `/caveman full` | Plans and dependency graphs are verbose |
| `/tool-research --deep` | `/caveman ultra` when context pressure is high | Multi-source research can overwhelm context |

Use `/caveman ultra` when multiple agents are running, outputs are mostly summaries, or context usage is already high. Stay on `lite` when the answer must remain comfortable for humans to read.

## RTK Policy

RTK (Rust Token Killer) is a CLI output compression proxy. When installed and hooked into the harness, it can transparently rewrite Bash calls such as `git status` into RTK-wrapped calls, then filter, group, truncate, and deduplicate the command output before it reaches the LLM context.

Use RTK by default when it is available for noisy shell commands:

- git status/diff/log output
- test and build output
- long directory listings
- repeated logs or stack traces

Do not describe RTK as a prompt compressor or as a global simplifier of model replies. It operates at the tool-output layer. Caveman operates at the LLM communication/prompt-verbosity layer. They are complementary and can be stacked.

Recommended wording:

> RTK compresses Bash/tool outputs before they enter the LLM context by filtering, grouping, truncating, and deduplicating noisy command output. It complements Caveman, which compresses the model-facing communication style.

## Default Policy

- Use low-cost tools for small, deterministic work.
- Use standard workflows for normal implementation.
- Reserve high-cost agents for high-risk reasoning, security, architecture, broad refactors, or repeated failures.
- Prefer targeted verification before broad review.
- Prefer Caveman compression before escalating to broader agents.
- Prefer RTK-wrapped shell output for commands likely to produce noisy logs or large diffs.
- Command files should keep only compact mode-specific routing hints; this document remains the canonical detailed Caveman/RTK policy.

## Practical Savings

The runtime skill is now a lightweight router. Long-form workflow explanations live in docs and are not required in every session.

Use `scripts/token-benchmark.py` for static size estimates before and after command or skill edits. Its `static_markdown` source is a proxy estimate (`ceil(character_count / 4)`), not measured session savings. Label live Caveman/RTK data as measured only when those tools report it; otherwise keep those fields as `unknown`.

## Session Statistics

Use the upstream statistics tools directly rather than wrapping them in a separate Engineer Shovel command.

- Caveman statistics should come from `/caveman-stats` when available.
- RTK project statistics should come from `rtk gain --project --format json` when available.
- If project statistics are empty, RTK global statistics can come from `rtk gain` and must be labeled global.
- RTK session adoption can come from `rtk session`.
- code-review-graph status and graph freshness belong in `/tool-graph status`.
- RTK hook rewrite audit can come from `rtk hook-audit`, but only when `RTK_HOOK_AUDIT=1` has been enabled and an audit log exists.
- Avoid `rtk gain --history` as a default statistics source because RTK 0.37.2 can panic on non-ASCII paths in history rendering.
- If one source lacks measured data, report it separately as unknown instead of rolling it into a total.
