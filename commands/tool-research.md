---
description: Research workflow — quick, web, or deep evidence gathering
argument-hint: [--quick|--web|--deep] [research topic or question]
cost-profile: variable
risk-level: medium
recommended-mode: --quick
allowed-tools: [Read, Grep, Glob, WebFetch, Task]
escalates-to: [/tool-plan, /tool-feat, /tool-blueprint]
depends-on: []
when-to-use: Use when a decision needs local, official, current, or multi-source evidence before planning or implementation.
---

# /tool-research — Research

**Input**: $ARGUMENTS

Start narrow. Add sources only when the answer needs current or external evidence.

Compression: follow `docs/token-cost.md`; use full for normal research, ultra for deep synthesis, and RTK only for shell/tool output.

## Cost Modes

- `--quick` or default: local docs, known library, simple comparison → targeted docs/search.
- `--web`: current facts or official docs needed → web/docs search + concise synthesis.
- `--deep`: strategic decision, conflicting evidence, unfamiliar ecosystem → L4: load matching ECC research skills → multi-source research + examples + tradeoff report.

## Flow

1. Define the exact decision the research should inform.
2. Search the smallest source set likely to answer it.
3. Cite or name sources when facts are current/external.
4. Highlight conflicts and confidence.
5. Route findings to `/tool-plan` (complex), `/tool-feat` (medium), `/tool-quick` (simple), or documentation. Append routing rationale.

## Avoid

Do not run deep multi-source research for questions answerable from local code or official docs.
