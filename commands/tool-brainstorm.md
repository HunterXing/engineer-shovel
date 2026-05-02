---
description: Brainstorming workflow — refine ideas and route to action
argument-hint: [--fast|--standard|--deep] [idea or topic]
---

# /tool-brainstorm — Brainstorming & Exploration

**Input**: $ARGUMENTS

Use this when the idea is not yet implementation-ready.

Compression: use `/caveman lite` for ideation readability; use `/caveman full` when options, tradeoffs, or captured notes become long.

## Cost Modes

| Mode | Use when | Path |
|---|---|---|
| `--fast` | capture and rough route | `/gsd-note` + short options |
| `--standard` or default | clarify product/technical direction | `/gsd-explore` or brainstorming |
| `--deep` | multiple viable paths or go/no-go decision | `/council` after options are clear |

## Flow

1. State the idea, goal, and uncertainty.
2. Surface assumptions and hidden constraints.
3. Generate options with tradeoffs.
4. Route to `/tool-quick`, `/tool-feat`, `/tool-plan`, `/tool-research`, or backlog.

## Avoid

Do not start implementation from brainstorming unless the next action is clear and verifiable.
