#!/usr/bin/env python3
"""Synchronize engineer-shovel installation with latest repository version."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Paths to track for sync
TRACKED_FILES = {
    "skill": ["SKILL.md"],
    "commands": [f"tool-{name}.md" for name in [
        "feat", "fix", "plan", "refactor", "review",
        "brainstorm", "quick", "blueprint", "research", "statistic", "update"
    ]],
    "hooks": [
        ".claude/hooks/pre-tool-use/10-caveman-output-compress.sh",
        ".claude/hooks/pre-tool-use/00-engineer-shovel-gate.sh",
    ]
}

# Standard installation locations
INSTALL_PATHS = {
    "opencode": {
        "global": {
            "skill": Path.home() / ".agents/skills/engineer-shovel",
            "commands": Path.home() / ".config/opencode/commands",
        },
        "local": {
            "skill": Path("./.agents/skills/engineer-shovel"),
            "commands": Path("./.opencode/commands"),
        }
    },
    "claude": {
        "global": {
            "skill": Path.home() / ".claude/skills/engineer-shovel",
            "commands": Path.home() / ".claude/commands",
        },
        "local": {
            "skill": Path("./.claude/skills/engineer-shovel"),
            "commands": Path("./.claude/commands"),
        }
    }
}


def hash_file(path: Path) -> str | None:
    """Return SHA256 hash of file, or None if file doesn't exist."""
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_installed_files(target: str, scope: str, file_type: str) -> list[Path]:
    """Get list of installed files for given target/scope/type."""
    base = INSTALL_PATHS[target][scope].get(file_type)
    if not base or not base.exists():
        return []
    
    if file_type == "skill":
        return [base / f for f in TRACKED_FILES["skill"]]
    elif file_type == "commands":
        return sorted(base.glob("tool-*.md"))
    return []


def get_repo_files(file_type: str) -> list[Path]:
    """Get list of source files from repository."""
    if file_type == "skill":
        return [ROOT / f for f in TRACKED_FILES["skill"]]
    elif file_type == "commands":
        return sorted((ROOT / "commands").glob("tool-*.md"))
    elif file_type == "hooks":
        return [ROOT / f for f in TRACKED_FILES["hooks"]]
    return []


def compare_files(installed: list[Path], repo: list[Path], repo_root: Path) -> dict:
    """Compare installed files with repo versions."""
    result = {
        "missing": [],
        "outdated": [],
        "extra": [],
        "up_to_date": []
    }
    
    repo_names = {f.name: f for f in repo}
    installed_names = {f.name: f for f in installed}
    
    for name, repo_path in repo_names.items():
        installed_path = installed_names.get(name)
        if not installed_path:
            result["missing"].append(repo_path)
        else:
            repo_hash = hash_file(repo_path)
            installed_hash = hash_file(installed_path)
            if repo_hash != installed_hash:
                result["outdated"].append({
                    "installed": installed_path,
                    "repo": repo_path
                })
            else:
                result["up_to_date"].append(installed_path)
    
    for name, installed_path in installed_names.items():
        if name not in repo_names:
            result["extra"].append(installed_path)
    
    return result


def sync_files(comparisons: dict, dry_run: bool = False) -> int:
    """Sync installed files with repo versions. Returns count of updated files."""
    updated = 0
    
    # Copy missing files
    for repo_path in comparisons["missing"]:
        if dry_run:
            print(f"  DRY-RUN: Would copy {repo_path.name}")
            continue
        # Determine target based on repo structure
        if repo_path.parent.name == "commands":
            target_dir = Path.home() / ".config/opencode/commands"
        else:
            target_dir = Path.home() / ".agents/skills/engineer-shovel"
        
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / repo_path.name
        target_path.write_bytes(repo_path.read_bytes())
        print(f"  + Added {repo_path.name}")
        updated += 1
    
    # Update outdated files
    for entry in comparisons["outdated"]:
        installed_path = entry["installed"]
        repo_path = entry["repo"]
        if dry_run:
            print(f"  DRY-RUN: Would update {installed_path.name}")
            continue
        installed_path.write_bytes(repo_path.read_bytes())
        print(f"  ~ Updated {installed_path.name}")
        updated += 1
    
    return updated


def check_installation(target: str, scope: str) -> dict:
    """Check installation status for given target/scope."""
    result = {
        "target": target,
        "scope": scope,
        "files": {},
        "summary": {"total": 0, "up_to_date": 0, "issues": 0}
    }
    
    for file_type in ["skill", "commands"]:
        installed = get_installed_files(target, scope, file_type)
        repo = get_repo_files(file_type)
        
        if not installed and repo:
            result["files"][file_type] = {"status": "not_installed", "files": []}
            result["summary"]["issues"] += len(repo)
        else:
            comparison = compare_files(installed, repo, ROOT)
            result["files"][file_type] = {
                "status": "installed",
                "comparison": comparison
            }
            result["summary"]["up_to_date"] += len(comparison["up_to_date"])
            result["summary"]["issues"] += len(comparison["missing"]) + len(comparison["outdated"])
        
        result["summary"]["total"] += len(repo)
    
    return result


def print_check_report(check_result: dict, verbose: bool = False) -> None:
    """Print installation check report."""
    target = check_result["target"]
    scope = check_result["scope"]
    summary = check_result["summary"]
    
    print(f"\n{target.upper()} ({scope})")
    print("=" * 40)
    
    for file_type, info in check_result["files"].items():
        if info["status"] == "not_installed":
            print(f"  ✘ {file_type}: NOT INSTALLED")
        else:
            comp = info["comparison"]
            if comp["missing"]:
                for f in comp["missing"]:
                    print(f"  ✘ {file_type}/{f.name}: MISSING")
            if comp["outdated"]:
                for entry in comp["outdated"]:
                    print(f"  ~ {file_type}/{entry['installed'].name}: OUTDATED")
            if comp["up_to_date"] and verbose:
                for f in comp["up_to_date"]:
                    print(f"  ✔ {file_type}/{f.name}: OK")
    
    status = "OK" if summary["issues"] == 0 else "NEEDS UPDATE"
    print(f"\n  Status: {status} ({summary['up_to_date']}/{summary['total']} files current)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize engineer-shovel installation"
    )
    parser.add_argument(
        "command",
        choices=["check", "sync"],
        help="Command: check (report status) or sync (update files)"
    )
    parser.add_argument(
        "--target",
        choices=["opencode", "claude", "both"],
        default="both",
        help="Target platform (default: both)"
    )
    parser.add_argument(
        "--scope",
        choices=["global", "local"],
        default="global",
        help="Installation scope (default: global)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    targets = ["opencode", "claude"] if args.target == "both" else [args.target]
    
    if args.command == "check":
        all_ok = True
        for target in targets:
            result = check_installation(target, args.scope)
            print_check_report(result, verbose=args.verbose)
            if result["summary"]["issues"] > 0:
                all_ok = False
        
        print()
        if all_ok:
            print("✔ All installations are up to date")
            return 0
        else:
            print("✘ Some installations need updates. Run: /tool-update sync")
            return 1
    
    elif args.command == "sync":
        total_updated = 0
        for target in targets:
            print(f"\nSyncing {target.upper()} ({args.scope})...")
            
            for file_type in ["skill", "commands"]:
                installed = get_installed_files(target, args.scope, file_type)
                repo = get_repo_files(file_type)
                comparison = compare_files(installed, repo, ROOT)
                
                updated = sync_files(comparison, dry_run=args.dry_run)
                total_updated += updated
        
        if args.dry_run:
            print(f"\nDRY-RUN: Would update {total_updated} file(s)")
        else:
            print(f"\n✔ Updated {total_updated} file(s)")
        
        return 0
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
