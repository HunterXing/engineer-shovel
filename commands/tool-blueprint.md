---
description: [DEPRECATED] Use /tool-plan --deep instead. Multi-step project planning is now auto-escalated from /tool-plan.
argument-hint: "[redirect — use /tool-plan --deep instead]"
cost-profile: high
risk-level: high
recommended-mode: --standard
allowed-tools: []
escalates-to: [/tool-plan]
depends-on: []
when-to-use: DEPRECATED since v1.4.0. Use `/tool-plan --deep` — it auto-classifies complexity and escalates to a file-backed implementation plan or `gsd-new-milestone` when needed. If you specifically need a code-level dependency graph plan, use `/tool-plan --deep "your goal"`.
---

# /tool-blueprint — DEPRECATED

**This command is deprecated as of v1.4.0.** Multi-step project planning is now part of `/tool-plan --deep`.

`/tool-plan --deep` auto-classifies your project and routes to the right engine:
- **≤3 PR code work** → file-backed implementation plan with explicit dependency order
- **>3 PR or milestone-scale** → `gsd-new-milestone` (discuss → plan → execute phases)
- **Architecture change** → `/tool-research --deep`, then convert conclusions into a deep plan

Use `/tool-plan --deep "your goal description"` — it provides everything `/tool-blueprint` did, plus automatic complexity classification.
