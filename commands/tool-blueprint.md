---
description: [DEPRECATED] Use /tool-plan --deep instead. Multi-step project planning is now auto-escalated from /tool-plan.
argument-hint: "[redirect — use /tool-plan --deep instead]"
cost-profile: high
risk-level: high
recommended-mode: --standard
allowed-tools: []
escalates-to: [/tool-plan]
depends-on: []
when-to-use: DEPRECATED since v1.4.0. Use `/tool-plan --deep` — it auto-classifies complexity and escalates to `ecc:blueprint` (≤3 PR code) or `gsd project` (milestone-scale engineering). If you specifically need a code-level dependency graph plan, use `/tool-plan --deep "your goal"`.
---

# /tool-blueprint — DEPRECATED

**This command is deprecated as of v1.4.0.** Multi-step project planning is now part of `/tool-plan --deep`.

`/tool-plan --deep` auto-classifies your project and routes to the right engine:
- **≤3 PR code work** → `ecc:blueprint` (dependency graph + `superpowers:writing-plans`)
- **>3 PR or milestone-scale** → `gsd project` (discuss → plan → execute phases)
- **Architecture change** → `ecc:council` for structured go/no-go before blueprint

Use `/tool-plan --deep "your goal description"` — it provides everything `/tool-blueprint` did, plus automatic complexity classification.
