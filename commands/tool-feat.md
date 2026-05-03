---
description: New feature development workflow — clarify, explore, plan, implement, verify
argument-hint: [--fast|--standard|--deep] [feature description | path/to/plan.md]
cost-profile: medium
risk-level: medium
recommended-mode: --standard
allowed-tools: [Read, Grep, Glob, Edit, Bash, Task]
escalates-to: [/tool-plan, /tool-review]
depends-on: [/tool-research]
when-to-use: Use for adding new functionality. Includes built-in brainstorm phase when requirements are unclear. Choose the smallest verifiable feature slice.
---

# /tool-feat — New Feature Development

**Input**: $ARGUMENTS

Build the smallest feature slice that can be verified. Use deep workflows only for unclear or multi-component work.

Compression: caveman full by default, lite for `--fast`, ultra for `--deep`. Call `rtk gain` before test/build commands.

## Phase 0: Brainstorm (auto-triggered when requirements unclear)

If the feature description does not name specific files, classes, and expected behavior, enter clarification phase first:
- **Product direction unclear** ("what to build") → L6: `gsd-explore`
- **Technical approach unclear** ("how to build") → L5: `superpowers:brainstorming`
- **Multiple viable paths for architecture** → L6: `ecc:council`

Route result to the appropriate cost mode below. Do not implement until direction is clear.

## Cost Modes

- `--fast`: known area, small feature → graph-assisted exploration → implement → tests.
- `--standard` or default: normal feature, 3-8 files → explore patterns → implement → verify.
- `--deep`: ambiguous, external deps, multi-system → brainstorm (Phase 0) → plan → implement → L4: `ecc:review-work`.

## Flow

0. Record baseline: run `caveman-stats` (L2) to capture session starting token count.
   Verify you are not on `main`/`master`; if you are, run `/tool-branch create feat <description>` first.
1. Code-review-graph (L2, auto-refreshed) to explore existing architecture and patterns before implementing.
   Auto-load L4 ECC matching pattern skill (e.g. `golang-patterns`, `python-patterns`, `springboot-patterns`). Use `docs/language-reference.md` for mapping.
2. Search existing code for matching patterns before adding new structure.
3. **Shortcut**: If the feature description already names specific files, classes, and expected behavior, skip Phase 0 and go directly to implement → verify.
4. If requirements are unclear (less than specific files+classes+behavior), run **Phase 0: Brainstorm** above.
5. Implement using project conventions.
6. Run diagnostics, related tests, typecheck/build. Call `rtk gain` before each noisy command.
7. **Verification Gate**: run project-native test/build → graph impact check → caveman review → report.
8. Run `caveman-stats` (L2) to report session token consumption and savings.
   For standard features, use `/tool-review --fast` or default. For deep features, use `/tool-review --deep` (or L4: `ecc:review-work` for major implementations).

## Security Gate

If the change touches auth, user input parsing, file system, network, secrets, or cookies, add L4: `ecc:security-review` regardless of cost mode.

## Skill Routing

Use project-native skills and commands from `docs/language-reference.md` instead of loading broad skill sets by default.
