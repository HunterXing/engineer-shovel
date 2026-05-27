---
description: Branch workflow management — create, review, merge, abort feature branches with squash merge
argument-hint: create|status|review|merge|abort [type] [description]
cost-profile: low
risk-level: low
recommended-mode: --fast
allowed-tools: [Bash, Read]
escalates-to: []
depends-on: []
when-to-use: Use for explicit branch lifecycle operations. `tool-feat` and `tool-fix` may create branches automatically; use this command when you want direct control.
---

# /tool-branch — Branch Workflow Management

**Input**: $ARGUMENTS

Manage feature branch lifecycle with automatic type detection, diff review, and squash merge. This is a platform support command for explicit branch operations.

## Subcommands

| Subcommand | Usage | Example |
|---|---|---|
| `create` | Create branch from current | `/tool-branch create feat add login` |
| `status` | Show branch info and diff stats | `/tool-branch status` |
| `review` | Show full diff + CRG blast-radius analysis | `/tool-branch review` |
| `merge` | Squash merge, L2 caveman-commit message, delete branch | `/tool-branch merge` |
| `abort` | Discard branch, return to source | `/tool-branch abort` |

## Flow

1. **Start task or take control explicitly**: `/tool-branch create [description]` — auto-detects type (feat/fix/refactor/docs)
2. **Work**: Make commits on the feature branch
3. **Review**: `/tool-branch review` — shows diff vs source branch with CRG analysis:
   - `detect_changes` → announce: `🚀 **code-review-graph** → analyzing branch changes`
   - `get_impact_radius` for blast radius → announce: `🚀 **code-review-graph** → checking blast radius`
4. **Confirm**: `/tool-branch merge` — squash merge, prompts for commit message, deletes branch
   - Use `/caveman-commit` for commit message → announce: `🚀 **caveman** → generating commit message`
5. **Or discard**: `/tool-branch abort` — abandon branch, return to source

## Auto-Detection Rules

| Keywords in description | Branch type |
|---|---|
| fix, bug, error, broken, crash, issue, problem | `fix` |
| add, new, feature, implement, support, create | `feat` |
| refactor, clean, optimize, improve, restructure | `refactor` |
| doc, readme, comment, typo, docs | `docs` |
| Default | `feat` |

## Branch Naming

Pattern: `{type}/{slugified-description}`

- Slug: lowercase, spaces → hyphens, alphanumeric only
- Example: `feat/add-login`, `fix/null-pointer-error`

## Implementation

Run `scripts/branch-workflow.sh` with the subcommand:

```bash
bash scripts/branch-workflow.sh <subcommand> [args...]
```

## Compression

Use `/caveman lite` (L2) for branch operations output (per SKILL.md mapping for `--fast`-equivalent operations). Use `/caveman-commit` (L2) for merge commit messages.

## Error Handling

- If branch creation fails, check for naming conflicts or invalid characters.
- If merge has conflicts, pause and let user resolve manually.
- If abort is rejected, ensure user confirms before discarding work.

## Edge Cases

- Uncommitted changes: auto-stashed before branch switch, restored on abort
- Branch exists: error with suggestion to use existing branch
- Not on feature branch: merge/review/abort require active feature branch
