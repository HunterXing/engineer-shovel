#!/usr/bin/env bash
set -euo pipefail

# Branch workflow management for Engineer Shovel
# Usage: branch-workflow.sh <subcommand> [args...]

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "")"
if [[ -z "$REPO_ROOT" ]]; then
    echo "Error: Not in a git repository"
    exit 1
fi

SOURCE_FILE="$REPO_ROOT/.git/.branch-source"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

get_current_branch() {
    git rev-parse --abbrev-ref HEAD
}

get_source_branch() {
    if [[ -f "$SOURCE_FILE" ]]; then
        cat "$SOURCE_FILE"
    else
        echo ""
    fi
}

is_feature_branch() {
    local branch="$1"
    [[ "$branch" =~ ^(feat|fix|refactor|docs)/ ]]
}

slugify() {
    local input="$1"
    local slug
    slug=$(python3 -c "
import sys
s = sys.argv[1].lower()
slug = ''.join('-' if not (c.isalnum() and ord(c) < 128) else c for c in s)
slug = slug.replace('--', '-').strip('-')[:50]
print(slug if slug else 'branch-' + str(int(__import__('time').time())))
" "$input")
    echo "$slug"
}

detect_type() {
    local desc="$1"
    local lower_desc
    lower_desc=$(echo "$desc" | tr '[:upper:]' '[:lower:]')
    
    if [[ "$lower_desc" =~ (fix|bug|error|broken|crash|issue|problem) ]]; then
        echo "fix"
    elif [[ "$lower_desc" =~ (refactor|clean|optimize|improve|restructure) ]]; then
        echo "refactor"
    elif [[ "$lower_desc" =~ (doc|readme|comment|typo|docs) ]]; then
        echo "docs"
    elif [[ "$lower_desc" =~ (add|new|feature|implement|support|create) ]]; then
        echo "feat"
    else
        echo "feat"
    fi
}

cmd_create() {
    local type="${1:-}"
    local description="${2:-}"
    
    # If only description provided, auto-detect type
    if [[ -z "$description" && -n "$type" ]]; then
        description="$type"
        type=$(detect_type "$description")
    fi
    
    if [[ -z "$description" ]]; then
        echo -e "${RED}Error: Description required${NC}"
        echo "Usage: branch-workflow.sh create [type] <description>"
        exit 1
    fi
    
    # Auto-detect type if not provided
    if [[ -z "$type" ]]; then
        type=$(detect_type "$description")
    fi
    
    local current_branch
    current_branch=$(get_current_branch)
    local slug
    slug=$(slugify "$description")
    local branch_name="${type}/${slug}"
    
    # Check if branch already exists
    if git show-ref --verify --quiet "refs/heads/$branch_name" 2>/dev/null; then
        echo -e "${RED}Error: Branch '$branch_name' already exists${NC}"
        echo "Use 'git checkout $branch_name' to switch to it"
        exit 1
    fi
    
    # Stash uncommitted changes if any
    if ! git diff --quiet HEAD 2>/dev/null || ! git diff --cached --quiet HEAD 2>/dev/null; then
        echo -e "${YELLOW}Stashing uncommitted changes...${NC}"
        git stash push -m "branch-workflow: auto-stash before creating $branch_name"
    fi
    
    # Create and checkout new branch
    git checkout -b "$branch_name"
    
    # Record source branch
    echo "$current_branch" > "$SOURCE_FILE"
    
    echo -e "${GREEN}Created branch: $branch_name${NC}"
    echo -e "Source branch: $current_branch"
    echo -e "Type: $type"
    echo ""
    echo "Next steps:"
    echo "  1. Make your changes and commit"
    echo "  2. Run '/tool-branch review' to see diff"
    echo "  3. Run '/tool-branch merge' when ready"
}

cmd_status() {
    local current_branch
    current_branch=$(get_current_branch)
    local source_branch
    source_branch=$(get_source_branch)
    
    if ! is_feature_branch "$current_branch"; then
        echo -e "${YELLOW}Not on a feature branch${NC}"
        echo "Current branch: $current_branch"
        exit 0
    fi
    
    echo -e "${BLUE}Branch Status${NC}"
    echo "Current: $current_branch"
    echo "Source:  ${source_branch:-unknown}"
    echo ""
    
    if [[ -n "$source_branch" ]]; then
        echo -e "${BLUE}Changes vs source:${NC}"
        git diff --stat "$source_branch...$current_branch" 2>/dev/null || echo "  (no diff available)"
        echo ""
        echo "Commits ahead: $(git rev-list --count "$source_branch..$current_branch" 2>/dev/null || echo '?')"
    fi
}

cmd_review() {
    local current_branch
    current_branch=$(get_current_branch)
    local source_branch
    source_branch=$(get_source_branch)
    
    if ! is_feature_branch "$current_branch"; then
        echo -e "${RED}Error: Not on a feature branch${NC}"
        exit 1
    fi
    
    if [[ -z "$source_branch" ]]; then
        echo -e "${RED}Error: Source branch not found. Was this branch created with /tool-branch?${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Diff Review: $source_branch → $current_branch${NC}"
    echo ""
    echo -e "${YELLOW}--- File Summary ---${NC}"
    git diff --stat "$source_branch...$current_branch"
    echo ""
    echo -e "${YELLOW}--- Full Diff ---${NC}"
    git diff "$source_branch...$current_branch"
}

cmd_merge() {
    local current_branch
    current_branch=$(get_current_branch)
    local source_branch
    source_branch=$(get_source_branch)
    
    if ! is_feature_branch "$current_branch"; then
        echo -e "${RED}Error: Not on a feature branch${NC}"
        exit 1
    fi
    
    if [[ -z "$source_branch" ]]; then
        echo -e "${RED}Error: Source branch not found. Was this branch created with /tool-branch?${NC}"
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff --quiet HEAD 2>/dev/null || ! git diff --cached --quiet HEAD 2>/dev/null; then
        echo -e "${RED}Error: Uncommitted changes. Please commit or stash first.${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Merging $current_branch → $source_branch (squash)${NC}"
    echo ""
    
    # Show what will be merged
    echo -e "${YELLOW}Changes to merge:${NC}"
    git diff --stat "$source_branch...$current_branch"
    echo ""
    
    # Switch to source branch
    git checkout "$source_branch"
    
    # Squash merge
    if ! git merge --squash "$current_branch"; then
        echo -e "${RED}Merge conflict! Please resolve manually.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Squash merge complete. Changes staged.${NC}"
    echo ""
    echo "Staged changes:"
    git diff --cached --stat
    echo ""
    echo -e "${YELLOW}Please provide a commit message (or press Enter for default):${NC}"
    read -r commit_msg
    
    if [[ -z "$commit_msg" ]]; then
        commit_msg="Merge $current_branch into $source_branch"
    fi
    
    git commit -m "$commit_msg"
    
    # Delete feature branch
    git branch -D "$current_branch"
    rm -f "$SOURCE_FILE"
    
    echo ""
    echo -e "${GREEN}Done! Branch $current_branch merged and deleted.${NC}"
}

cmd_abort() {
    local current_branch
    current_branch=$(get_current_branch)
    local source_branch
    source_branch=$(get_source_branch)
    
    if ! is_feature_branch "$current_branch"; then
        echo -e "${RED}Error: Not on a feature branch${NC}"
        exit 1
    fi
    
    if [[ -z "$source_branch" ]]; then
        echo -e "${RED}Error: Source branch not found. Was this branch created with /tool-branch?${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Abandoning branch: $current_branch${NC}"
    echo -e "Returning to: $source_branch"
    echo ""
    read -p "Are you sure? (y/N) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Abort cancelled"
        exit 0
    fi
    
    # Switch to source
    git checkout "$source_branch"
    
    # Delete feature branch
    git branch -D "$current_branch"
    rm -f "$SOURCE_FILE"
    
    echo -e "${GREEN}Branch $current_branch deleted. Back on $source_branch.${NC}"
    
    # Restore stash if any
    if git stash list | grep -q "branch-workflow: auto-stash"; then
        echo -e "${YELLOW}Restoring stashed changes...${NC}"
        git stash pop
    fi
}

# Main dispatcher
case "${1:-}" in
    create)
        shift
        cmd_create "$@"
        ;;
    status)
        cmd_status
        ;;
    review)
        cmd_review
        ;;
    merge)
        cmd_merge
        ;;
    abort)
        cmd_abort
        ;;
    *)
        echo "Usage: branch-workflow.sh <create|status|review|merge|abort> [args...]"
        echo ""
        echo "Subcommands:"
        echo "  create [type] <description>  Create feature branch"
        echo "  status                        Show branch status"
        echo "  review                        Show diff for review"
        echo "  merge                         Squash merge to source"
        echo "  abort                         Abandon branch"
        exit 1
        ;;
esac