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
standalone: true
---

# /tool-quick — Quick Tasks

**Input**: $ARGUMENTS

Use this for obvious, low-risk work. This is a primary workflow command, not a gateway into heavier process.

## Cost Modes (Self-Contained)

| Mode | When | Caveman | Example |
|------|------|---------|---------|
| `--fast` | Typo, config tweak, 1-line fix (default) | `/caveman lite` | Direct edit |
| `--standard` | 1-2 file surgical change | `/caveman full` | Edit + tests + review |

**Smart mode**: If no mode specified, default to `--fast` for quick tasks.

## Security Gate (Self-Contained)

If change touches **auth, user input, file system, network, secrets, cookies, or SQL**:
→ Stop treating it as a quick task; promote to `/tool-fix --deep` or `/tool-feat --deep` and add `/tool-review --deep` before completion.

## Flow

0. Stay cheap by default. Only get code-review-graph context when the target file, symbol, or dependency edge is still unclear after a quick local read.
   - For a specific symbol: `semantic_search_nodes(query="<function_or_class_name>")` → announce: `🚀 **code-review-graph** → searching for <symbol>`
   - For file-level context: `query_graph(imports_of="<file_path>")` → announce: `🚀 **code-review-graph** → analyzing dependencies for <file>`
   - Skip graph queries entirely when the file and edit are already obvious
1. Confirm the target file or symbol from context.
2. Make the smallest safe change.
3. Run the nearest useful verification: formatter/lint/test/build as applicable.
   Call `rtk gain` before noisy commands (test runs, builds, diff/log inspection) → announce: `🚀 **rtk** → wrapping output for compression`
4. **Verification Gate**: Run the project-native test/build command. On pass, report what changed and what was verified.

## Error Handling

- If the edit fails or produces unexpected results, stop and report the issue.
- If verification fails, revert the change and escalate to `/tool-fix`.
- If the task turns out to be more complex than expected, escalate to `/tool-feat` or `/tool-plan`.

## Toolchain Announcements

When using external tools, announce them with maximum visibility:
- `🚀 **code-review-graph** → <action>` — when querying the code graph
- `🚀 **caveman** → <mode>` — when applying communication compression
- `🚀 **rtk** → wrapping <command> output` — when compressing shell output

## Avoid

- No `/tool-plan --deep` unless the task is no longer quick.
- No `/deep-research`.
- No OpenSpec.
- No GSD.
- No `/tool-review --deep` unless the change unexpectedly becomes high risk.

## References

- Full router: `skill(name="engineer-shovel")` or `SKILL.md`
