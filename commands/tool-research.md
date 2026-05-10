---
description: Research workflow — quick, web, or deep evidence gathering with codebase-aware context
argument-hint: [--quick|--web|--deep] [research topic or question]
cost-profile: variable
risk-level: medium
recommended-mode: --quick
allowed-tools: [Read, Grep, Glob, WebFetch, Task]
escalates-to: [/tool-plan, /tool-feat]
depends-on: []
when-to-use: Use when a decision needs local, official, current, or multi-source evidence before planning or implementation.
---

# /tool-research — Research

**Input**: $ARGUMENTS

Start narrow. Add sources only when the answer needs current or external evidence. This command exists to inform a decision, not to act as a generic prelude to every feature or fix.

Shared policy: mode mapping comes from `SKILL.md`; escalation rules and capability-layer roles live in `docs/architecture.md`. Skip RTK unless research unexpectedly turns into large shell output.

## Cost Modes

- `--quick` or default: local docs, known library, simple comparison → targeted docs/search plus minimal codebase context.
- `--web`: current facts or official docs needed → web/docs search + concise synthesis.
- `--deep`: strategic decision, conflicting evidence, unfamiliar ecosystem, or architecture tradeoff → escalate deliberately per `docs/architecture.md`.

This command uses a special mode axis:
- `quick / web / deep` describe evidence source and research depth
- they do **not** replace the global `fast / standard / deep` execution model used by the main workflow commands

## Flow

1. Define the exact decision the research should inform.
2. Search claude-mem for prior research conclusions when historical decisions are likely to matter.
3. Query code-review-graph (L2) for relevant existing implementation and patterns:
   - `semantic_search_nodes(query="<topic_keywords>")` to find related functions/classes
   - `query_graph(callees_of="<related_node>")` to understand dependency context
4. Search the smallest source set likely to answer it.
5. Cite or name sources when facts are current/external.
6. Highlight conflicts and confidence.
7. Route findings to `/tool-plan` (scope/order still unclear), `/tool-feat` (decision made), `/tool-quick` (small obvious change), or documentation. Append routing rationale.

## Avoid

Do not run deep multi-source research for questions answerable from local code or official docs.
Do not make this a default prerequisite for normal `feat` or `fix` work.
