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

Compression: follow `docs/token-cost.md`; use full for normal research, ultra for deep synthesis, and RTK only for shell/tool output.

## Cost Modes

- `--quick` or default: local docs, known library, simple comparison → targeted docs/search. Supplement with code-review-graph (L2) for existing codebase architecture context.
- `--web`: current facts or official docs needed → web/docs search + concise synthesis. Include code-review-graph context for how the current codebase relates.
- `--deep`: strategic decision, conflicting evidence, unfamiliar ecosystem → code-review-graph architecture exploration → L4: load matching ECC research skills → multi-source research (ecc:deep-research) + examples + tradeoff report.

## Flow

1. Define the exact decision the research should inform.
2. Query code-review-graph (L2) for relevant existing implementation and patterns.
3. Search the smallest source set likely to answer it.
4. Cite or name sources when facts are current/external.
5. Highlight conflicts and confidence.
6. Route findings to `/tool-plan` (complex), `/tool-feat` (medium), `/tool-quick` (simple), or documentation. Append routing rationale.

## Avoid

Do not run deep multi-source research for questions answerable from local code or official docs.
