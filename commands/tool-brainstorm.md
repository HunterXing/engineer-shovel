---
description: Brainstorming workflow — refine ideas and route to action
argument-hint: [--fast|--standard|--deep] [idea or topic]
cost-profile: variable
risk-level: low
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Task]
escalates-to: [/tool-plan, /tool-research, /tool-blueprint]
depends-on: []
when-to-use: Use when an idea is not implementation-ready and needs assumptions, options, or routing clarified first.
---

# /tool-brainstorm — Brainstorming & Exploration

**Input**: $ARGUMENTS

Use this when the idea is not yet implementation-ready.

Compression: caveman lite for readability, caveman full when options/tradeoffs get long.

## Cost Modes

- `--fast`: capture and rough route → short options → route to backlog.
- `--standard` or default: clarify direction → follow Decision Tree 1 in `docs/decision-trees.md`:
  - **Product direction unclear** ("what to build") → L6: `gsd-explore`
  - **Technical approach unclear** ("how to build") → L5: `superpowers:brainstorming`
- `--deep`: multiple viable paths or go/no-go decision → L6: `council` after options are clear.

## Flow

1. State the idea, goal, and uncertainty.
2. Surface assumptions and hidden constraints.
3. Generate options with tradeoffs.
   For domain-specific exploration, load relevant L4 ECC skills based on project context (language, framework, security).
4. Route to `/tool-quick`, `/tool-feat`, `/tool-plan`, `/tool-research`, or backlog.

## Avoid

Do not start implementation from brainstorming unless the next action is clear and verifiable.
