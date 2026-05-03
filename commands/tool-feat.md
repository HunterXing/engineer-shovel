---
description: New feature development workflow — explore, plan, implement, verify
argument-hint: [--fast|--standard|--deep] [feature description | path/to/plan.md]
cost-profile: medium
risk-level: medium
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Edit, Bash, Task]
escalates-to: [/tool-plan, /tool-blueprint, /tool-review]
depends-on: [/tool-research, /tool-graph]
when-to-use: Use for adding new functionality after choosing the smallest verifiable feature slice.
---

# /tool-feat — New Feature Development

**Input**: $ARGUMENTS

Build the smallest feature slice that can be verified. Use deep workflows only for unclear or multi-component work.

Compression: caveman full by default, lite for `--fast`, ultra for `--deep`. Call `rtk gain` before test/build commands.

## Cost Modes

- `--fast`: known area, small feature → graph-assisted exploration → implement → tests.
- `--standard` or default: normal feature, 3-8 files → explore patterns → implement → verify.
- `--deep`: ambiguous, external deps, multi-system → brainstorm + plan → blueprint if needed.

## Flow

0. Record baseline: run `caveman-stats` (L2) to capture session starting token count.
   Verify you are not on `main`/`master`; if you are, run `/tool-branch create feat <description>` first.
1. If code-review-graph installed, use it to explore existing architecture and patterns before implementing.
   If project language is known, auto-load L4 ECC matching pattern skill (e.g. `golang-patterns`, `python-patterns`, `springboot-patterns`). Use `docs/language-reference.md` for mapping.
2. Search existing code for matching patterns before adding new structure.
3. **Shortcut**: If the feature description already names specific files, classes, and expected behavior, skip brainstorming + writing-plans and go directly to implement → verify.
4. If requirements are unclear, follow Decision Tree 1 in `docs/decision-trees.md`:
   - Product direction unclear ("what to build") → L6: `gsd-explore`
   - Technical approach unclear ("how to build") → L5: `superpowers:brainstorming`
5. Implement using project conventions.
6. Run diagnostics, related tests, typecheck/build. Call `rtk gain` before each noisy command.
7. Run `caveman-stats` (L2) to report session token consumption and savings.
   Use `/tool-review --fast` or default review by risk.

## Security Gate

If the change touches auth, user input parsing, file system, network, secrets, or cookies, add L4: `ecc:security-review` regardless of cost mode.

## Skill Routing

Use project-native skills and commands from `docs/language-reference.md` instead of loading broad skill sets by default.
