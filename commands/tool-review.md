---
description: Code review workflow — fast, standard, or deep review by risk
argument-hint: [--fast|--standard|--deep] [pr-number | pr-url | blank for local review]
cost-profile: variable
risk-level: variable
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Bash, Task]
escalates-to: [/tool-fix, /tool-refactor, /tool-feat]
depends-on: []
when-to-use: Use for local diffs, pull requests, or post-implementation review where risk determines review depth.
---

# /tool-review — Code Review

**Input**: $ARGUMENTS

Choose the cheapest review mode that can catch the relevant failure class. Review is a support task, not the default front door for routine implementation.

Shared policy: mode mapping and security gate come from `SKILL.md`; escalation rules live in `docs/architecture.md`. Wrap large diff/log commands with `rtk gain`.

## Cost Modes

- `--fast`: quick sanity check or small local diff → Caveman-compressed findings summary.
- `--standard` or default: local diff or normal PR → graph-assisted analysis + normal review path.
- `--deep`: major implementation, security, broad refactor, or pre-merge audit → heavier review stack.

## Flow

1. Select local, PR, or post-implementation mode from the input.
2. Code-review-graph (L2, auto-refreshed):
   - `detect_changes` for risk-scored diff analysis
   - `get_review_context(changes="<diff>")` for token-efficient review snippets
   - `get_impact_radius(target="<changed_module>")` for blast-radius detection
3. For PR review with `--standard` or `--deep`, inspect repository-native review comments, CI status, and merge blockers if available; keep this command focused on findings rather than platform automation.
4. Review for correctness, regressions, security, and maintainability.
5. Report critical/high findings with a recommended next route:
   - `/tool-fix` for defects or regressions
   - `/tool-refactor` for cleanup or structure issues
   - `/tool-feat` for missing behavior or acceptance gaps
6. Re-run the same or stronger review mode after changes until findings are resolved or explicitly accepted.
7. Review findings may be captured by claude-mem when cross-session pattern detection is useful.

## Positioning

- Use this command when review itself is the task.
- Do not require it as a front door before every `quick`, `fix`, or `feat` execution.
- Default behavior is to report findings, not to mutate code.

## Security-Sensitive Code

Use `--deep` and expand the checklist for auth, user input, file system, network, secrets, cookies, SQL, and serialization paths.
