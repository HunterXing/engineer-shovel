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

Start narrow. Add sources only when the answer needs current or external evidence.

Compression: `/caveman full` by default, `/caveman ultra` for deep synthesis (per SKILL.md mapping). Skip RTK (research is document-heavy, not shell-heavy).

## Cost Modes

- `--quick` or default: local docs, known library, simple comparison → targeted docs/search. Supplement with code-review-graph: `semantic_search_nodes(query="<topic>")` for existing codebase context.
- `--web`: current facts or official docs needed → web/docs search + concise synthesis. Include code-review-graph: `query_graph(imports_of="<related_module>")` for how the current codebase relates.
- `--deep`: strategic decision, conflicting evidence, unfamiliar ecosystem → code-review-graph: `get_architecture_overview` + `semantic_search_nodes` to map codebase → load matching ECC research skills → `skill(name="deep-research")` → tradeoff report.

## Flow

1. Define the exact decision the research should inform.
2. Search claude-mem for prior research conclusions: `npx claude-mem search "<topic_keywords>"` to avoid repeating known findings.
3. Query code-review-graph (L2) for relevant existing implementation and patterns:
   - `semantic_search_nodes(query="<topic_keywords>")` to find related functions/classes
   - `query_graph(callees_of="<related_node>")` to understand dependency context
4. Search the smallest source set likely to answer it.
5. Cite or name sources when facts are current/external.
6. Highlight conflicts and confidence.
7. Route findings to `/tool-plan` (complex), `/tool-feat` (medium), `/tool-quick` (simple), or documentation. Append routing rationale.

## Avoid

Do not run deep multi-source research for questions answerable from local code or official docs.
