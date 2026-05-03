---
description: [DEPRECATED] Use /tool-feat or /tool-plan instead. Brainstorming is now built into these commands as Phase 0.
argument-hint: "[redirect — use /tool-plan or /tool-feat instead]"
cost-profile: variable
risk-level: low
recommended-mode: --fast
allowed-tools: []
escalates-to: [/tool-plan, /tool-feat]
depends-on: []
when-to-use: DEPRECATED since v1.4.0. Use `/tool-feat` or `/tool-plan` — both auto-detect when clarification is needed and enter a brainstorm phase. If you specifically need an exploration-only session, use `/tool-plan --fast` with a vague goal.
---

# /tool-brainstorm — DEPRECATED

**This command is deprecated as of v1.4.0.** Brainstorming is now a built-in Phase 0 in `/tool-feat` and `/tool-plan`.

If your feature or plan direction is unclear, just use the target command directly:
- `/tool-feat "add auth to the app"` — will auto-trigger brainstorm if direction is unclear
- `/tool-plan "redesign the database layer"` — will auto-trigger brainstorm before planning

The router auto-detects ambiguity and enters the appropriate clarification path:
- Product direction unclear → `gsd-explore`
- Technical approach unclear → `superpowers:brainstorming`
- Multiple architecture options → `ecc:council`
