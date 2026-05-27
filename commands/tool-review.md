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
2. Code-review-graph (L2, auto-refreshed) is the default intelligence layer for real review work:
   - `detect_changes` for risk-scored diff analysis → announce: `🚀 **code-review-graph** → analyzing changes for risk`
   - `get_review_context(changes="<diff>")` for token-efficient review snippets → announce: `🚀 **code-review-graph** → generating review context`
   - `get_impact_radius(target="<changed_module>")` for blast-radius detection → announce: `🚀 **code-review-graph** → checking blast radius`
3. For trivial one-file sanity checks, a fast local diff read may be enough; keep CRG for cases where graph context adds real value.
4. For PR review with `--standard` or `--deep`, inspect repository-native review comments, CI status, and merge blockers if available; keep this command focused on findings rather than platform automation.
5. Review for correctness, regressions, security, and maintainability.
6. Report critical/high findings with a recommended next route:
   - `/tool-fix` for defects or regressions
   - `/tool-refactor` for cleanup or structure issues
   - `/tool-feat` for missing behavior or acceptance gaps
7. Re-run the same or stronger review mode after changes until findings are resolved or explicitly accepted.
8. Review findings may be captured by claude-mem when cross-session pattern detection is useful. → announce: `🚀 **claude-mem** → storing review findings`

## Review Checklist

- [ ] Correctness: Does the code do what it claims?
- [ ] Regressions: Could this break existing functionality?
- [ ] Security: Are there auth, input, or data handling risks?
- [ ] Maintainability: Is the code clear and maintainable?
- [ ] Performance: Are there obvious performance issues?
- [ ] Testing: Is there adequate test coverage?

## Error Handling

- If the diff is too large to review, suggest splitting into smaller PRs.
- If CI status is unavailable, note this limitation in the review.
- If critical findings are found, clearly communicate the severity and required action.
- If review reveals architectural concerns, recommend `/tool-plan --deep`.

## Positioning

- Use this command when review itself is the task.
- Do not require it as a front door before every `quick`, `fix`, or `feat` execution.
- Default behavior is to report findings, not to mutate code.

## Security-Sensitive Code

Use `--deep` and expand the checklist for auth, user input, file system, network, secrets, cookies, SQL, and serialization paths.
