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

Use this for obvious, low-risk work. This is a primary workflow command, not a gateway into heavier process.

Compression: per SKILL.md enforced mapping — `/caveman lite` for `--fast`, `/caveman full` for `--standard`. Wrap large test/build output with `rtk gain`; skip RTK for small diffs.

## Cost Modes

- `--fast` or default: typo, config tweak, 1-line fix → direct edit.
- `--standard`: 1-2 file surgical change → targeted edit + tests + caveman review.

## Flow

0. Stay cheap by default. Only get code-review-graph context when the target file, symbol, or dependency edge is still unclear after a quick local read.
   - For a specific symbol: `semantic_search_nodes(query="<function_or_class_name>")`
   - For file-level context: `query_graph(imports_of="<file_path>")` to see dependencies
   - Skip graph queries entirely when the file and edit are already obvious
   If project language is known, use matching ECC pattern reference from `docs/language-reference.md` only when a framework convention matters.
1. Confirm the target file or symbol from context.
2. Make the smallest safe change.
3. Run the nearest useful verification: formatter/lint/test/build as applicable.
   Call `rtk gain` before noisy commands (test runs, builds, diff/log inspection).
4. **Verification Gate**: Run the project-native test/build command. On pass, report what changed and what was verified.

## Error Handling

- If the edit fails or produces unexpected results, stop and report the issue.
- If verification fails, revert the change and escalate to `/tool-fix`.
- If the task turns out to be more complex than expected, escalate to `/tool-feat` or `/tool-plan`.

## Security Gate

If change touches auth, user input, file system, network, secrets, cookies, or SQL, stop treating it as a quick task; promote it to the matching deep route and add `/tool-review --deep` before completion.

## Avoid

- No `/tool-plan --deep` unless the task is no longer quick.
- No `/deep-research`.
- No OpenSpec.
- No GSD.
- No `/tool-review --deep` unless the change unexpectedly becomes high risk.
- No hidden escalation for cross-file state, external systems, unknown root cause, or durable acceptance needs; promote those to the matching main route instead.
