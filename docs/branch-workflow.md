# Branch Workflow

Feature branch lifecycle management with squash merge and diff review.

## Quick Start

```bash
# Create a feature branch
/tool-branch create add user login

# Work on the branch...
git add . && git commit -m "feat: add login page"

# Review changes before merge
/tool-branch review

# Merge when ready (squash + delete branch)
/tool-branch merge

# Or abandon if needed
/tool-branch abort
```

## Subcommands

### `create [type] <description>`

Create a new feature branch from current branch.

```bash
# Auto-detect type from description
/tool-branch create fix login button crash

# Explicit type
/tool-branch create feat "user authentication"
```

**Auto-detection rules:**
| Keywords | Type |
|----------|------|
| fix, bug, error, broken, crash, issue, problem | `fix` |
| add, new, feature, implement, support, create | `feat` |
| refactor, clean, optimize, improve, restructure | `refactor` |
| doc, readme, comment, typo, docs | `docs` |
| Default | `feat` |

**Branch naming:** `{type}/{slugified-description}`
- Example: `feat/add-user-login`, `fix/null-pointer-error`

### `status`

Show current branch info and diff stats vs source.

```bash
/tool-branch status
```

Output:
- Current branch name
- Source branch
- File changes summary
- Commits ahead count

### `review`

Display full diff for review before merge.

```bash
/tool-branch review
```

Shows:
- File summary (stat)
- Complete diff output

### `merge`

Squash merge current branch to source, then delete branch.

```bash
/tool-branch merge
```

Process:
1. Shows changes to be merged
2. Switches to source branch
3. Performs squash merge
4. Prompts for commit message
5. Commits changes
6. Deletes feature branch

### `abort`

Discard current branch and return to source.

```bash
/tool-branch abort
```

Process:
1. Confirms with user
2. Switches to source branch
3. Deletes feature branch
4. Restores any auto-stashed changes

## Edge Cases

### Uncommitted Changes
- On `create`: auto-stashed, restored on `abort`
- On `merge`: error, must commit first

### Branch Already Exists
- Error with suggestion to checkout existing branch

### Not on Feature Branch
- `merge`, `review`, `abort` require active feature branch
- `status` works on any branch

## Integration with Other Commands

Use `/tool-branch` with other Engineer Shovel commands:

```bash
# Start feature with branch
/tool-branch create feat "add payment system"

# Plan the feature
/tool-plan

# Implement
/tool-feat

# Review
/tool-branch review

# Merge
/tool-branch merge
```

## Git Configuration

The script uses `.git/.branch-source` to track source branch per feature branch. This file is automatically managed and cleaned up on merge/abort.
