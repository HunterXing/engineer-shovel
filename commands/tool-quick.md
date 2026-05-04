---
description: Quick task execution — surgical changes with minimal overhead
argument-hint: [--fast|--standard] [task description]
cost-profile: low
risk-level: low
recommended-mode: --fast
allowed-tools: [Read, Grep, Glob, Edit, Bash]
escalates-to: [/tool-fix, /tool-feat, /tool-review]
depends-on: []
when-to-use: Use for obvious low-risk work such as typos, tiny config edits, or one to two file surgical changes.
---

# /tool-quick — Quick Tasks

**Input**: $ARGUMENTS

Use this for obvious, low-risk work. Do not run planning, deep research, or broad review for quick tasks.

Compression: per SKILL.md enforced mapping — `/caveman lite` for `--fast`, `/caveman full` for `--standard`. Wrap large test/build output with `rtk gain`; skip RTK for small diffs.

## Cost Modes

- `--fast` or default: typo, config tweak, 1-line fix → direct edit.
- `--standard`: 1-2 file surgical change → targeted edit + tests + caveman review.

## Flow

0. Get code-review-graph context (L2, auto-refreshed by git hooks):
   - For a specific symbol: `semantic_search_nodes(query="<function_or_class_name>")`
   - For file-level context: `query_graph(imports_of="<file_path>")` to see dependencies
   - For structural overview: `get_architecture_overview` (only when target files are unclear)
   If project language is known, load matching L4 ECC pattern reference from `docs/language-reference.md`.
1. Confirm the target file or symbol from context.
2. Make the smallest safe change.
3. Run the nearest useful verification: formatter/lint/test/build as applicable.
   Call `rtk gain` before noisy commands (test runs, builds, diff/log inspection).
4. **Verification Gate**: Run the project-native test/build command. On pass, report what changed and what was verified.

## Security Gate

If change touches auth, user input, file system, network, secrets, cookies, or SQL → escalate to `skill(name="security-review")`.

## Avoid

- No `/blueprint`.
- No `/deep-research`.
- No `/review-work` unless the change unexpectedly becomes high risk.
