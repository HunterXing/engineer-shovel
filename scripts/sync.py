#!/usr/bin/env python3
"""Synchronize Engineer Shovel router files with the latest repository version.

This script is intentionally limited to the router layer: `SKILL.md` and `/tool-*`
files. External component health and repair live in `scripts/health.py`. User-facing
workflows should prefer `/tool-update`, which orchestrates both layers.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]

REPO_OWNER = "HunterXing"
REPO_NAME = "engineer-shovel"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main"

from paths import INSTALL_PATHS  # noqa: E402


def print_section(title: str) -> None:
    print(f"\n{title}")
    print("=" * len(title))


def print_update_summary(targets: list[str], scope: str, command: str) -> None:
    mode_label = "--check" if command == "check" else "--full"
    target_label = "both" if len(targets) > 1 else targets[0]
    print_section("TOOL-UPDATE SUMMARY")
    print(f"Mode: {mode_label}")
    print(f"Target: {target_label}")
    print(f"Scope: {scope}")
    print("Router layer: scripts/sync.py")
    print("Component layer: scripts/health.py")
    print("Router statuses: current / missing / outdated / extra")


# Paths to track for sync
TRACKED_FILES = {
    "skill": ["SKILL.md"],
    "commands": [f"tool-{name}.md" for name in [
        "branch", "feat", "fix", "plan", "refactor", "review",
        "quick", "research", "graph", "update", "alias"
    ]],
}

def hash_file(path: Path) -> str | None:
    """Return SHA256 hash of file, or None if file doesn't exist."""
    try:
        if not path.exists():
            return None
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not hash {path}: {e}")
        return None


def get_installed_files(target: str, scope: str, file_type: str) -> list[Path]:
    """Get list of installed files for given target/scope/type."""
    try:
        base = INSTALL_PATHS[target][scope].get(file_type)
        if not base or not base.exists():
            return []
        
        if file_type == "skill":
            return [base / f for f in TRACKED_FILES["skill"]]
        elif file_type == "commands":
            return sorted(base.glob("tool-*.md"))
        return []
    except (KeyError, OSError) as e:
        print(f"Warning: Could not get installed files for {target}/{scope}/{file_type}: {e}")
        return []


def get_repo_files(file_type: str) -> list[Path]:
    """Get list of source files from repository."""
    if file_type == "skill":
        return [ROOT / f for f in TRACKED_FILES["skill"]]
    if file_type == "commands":
        return sorted((ROOT / "commands").glob("tool-*.md"))
    return []


def _is_git_repo() -> bool:
    """Check if ROOT is inside a git repository."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(ROOT), capture_output=True, text=True, check=False
        )
        return proc.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def _download_file(url: str) -> bytes | None:
    """Download a file from URL. Returns bytes or None on failure."""
    try:
        req = Request(url, headers={"User-Agent": "engineer-shovel-sync"})
        with urlopen(req, timeout=30) as resp:
            return resp.read()
    except (URLError, OSError, TimeoutError) as e:
        print(f"  Warning: Could not download {url}: {e}")
        return None


def _download_remote_files(file_type: str, tmp_dir: Path) -> list[Path]:
    """Download latest files from GitHub raw URL into tmp_dir. Returns list of paths."""
    paths = []
    if file_type == "skill":
        for name in TRACKED_FILES["skill"]:
            url = f"{RAW_BASE}/{name}"
            content = _download_file(url)
            if content:
                out = tmp_dir / name
                out.write_bytes(content)
                paths.append(out)
    elif file_type == "commands":
        cmd_dir = tmp_dir / "commands"
        cmd_dir.mkdir(exist_ok=True)
        for name in TRACKED_FILES["commands"]:
            url = f"{RAW_BASE}/commands/{name}"
            content = _download_file(url)
            if content:
                out = cmd_dir / name
                out.write_bytes(content)
                paths.append(out)
    return paths


def compare_files(installed: list[Path], repo: list[Path]) -> dict:
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
            if repo_hash is None or installed_hash is None:
                # If we can't hash, assume outdated
                result["outdated"].append({
                    "installed": installed_path,
                    "repo": repo_path
                })
            elif repo_hash != installed_hash:
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


def sync_files(comparisons: dict, target: str = "opencode", scope: str = "global", dry_run: bool = False) -> int:
    """Sync installed files with repo versions. Returns count of updated files."""
    updated = 0
    try:
        skill_dir = INSTALL_PATHS[target][scope]["skill"]
        command_dir = INSTALL_PATHS[target][scope]["commands"]
    except KeyError as e:
        print(f"Error: Invalid target/scope combination: {e}")
        return 0

    for repo_path in comparisons["missing"]:
        if dry_run:
            print(f"  DRY-RUN: Would copy {repo_path.name}")
            updated += 1
            continue
        try:
            if repo_path.parent.name == "commands":
                target_dir = command_dir
            else:
                target_dir = skill_dir

            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / repo_path.name
            target_path.write_bytes(repo_path.read_bytes())
            print(f"  + Added {repo_path.name}")
            updated += 1
        except (OSError, PermissionError) as e:
            print(f"  ✘ Failed to add {repo_path.name}: {e}")

    for entry in comparisons["outdated"]:
        installed_path = entry["installed"]
        repo_path = entry["repo"]
        if dry_run:
            print(f"  DRY-RUN: Would update {installed_path.name}")
            updated += 1
            continue
        try:
            installed_path.write_bytes(repo_path.read_bytes())
            print(f"  ~ Updated {installed_path.name}")
            updated += 1
        except (OSError, PermissionError) as e:
            print(f"  ✘ Failed to update {installed_path.name}: {e}")

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
            comparison = compare_files(installed, repo)
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
    
    print_section(f"{target.upper()} ({scope})")
    
    for file_type, info in check_result["files"].items():
        if info["status"] == "not_installed":
            print(f"  ✘ router/{file_type}: NOT INSTALLED")
        else:
            comp = info["comparison"]
            if comp["missing"]:
                for f in comp["missing"]:
                    print(f"  ✘ router/{file_type}/{f.name}: MISSING")
            if comp["outdated"]:
                for entry in comp["outdated"]:
                    print(f"  ~ router/{file_type}/{entry['installed'].name}: OUTDATED")
            if comp["extra"]:
                for f in comp["extra"]:
                    print(f"  ! router/{file_type}/{f.name}: EXTRA")
            if comp["up_to_date"] and verbose:
                for f in comp["up_to_date"]:
                    print(f"  ✔ router/{file_type}/{f.name}: CURRENT")
    
    status = "CURRENT" if summary["issues"] == 0 else "DRIFT DETECTED"
    print(f"\n  Router status: {status} ({summary['up_to_date']}/{summary['total']} files current)")


def extract_version(skill_md_path: Path) -> str | None:
    """Extract metadata.version from SKILL.md YAML frontmatter."""
    if not skill_md_path.exists():
        return None
    content = skill_md_path.read_text()
    m = re.search(r'version:\s*"([^"]+)"', content)
    return m.group(1) if m else None


def check_remote_updates() -> dict:
    """Check if local installation is behind remote. Works with or without git."""
    result = {
        "fetched": False,
        "behind": False,
        "behind_count": 0,
        "remote_version": None,
        "local_version": None,
        "error": None,
        "has_git": False,
    }

    # Try git-based check first
    if _is_git_repo():
        result["has_git"] = True
        result["local_version"] = extract_version(ROOT / "SKILL.md")

        try:
            proc = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=str(ROOT), capture_output=True, text=True, check=False
            )
            if proc.returncode != 0:
                result["error"] = f"git fetch failed: {proc.stderr.strip()}"
                return result
            result["fetched"] = True
        except FileNotFoundError:
            result["error"] = "git not found"
            return result

        try:
            upstream_ref = _get_upstream_ref()
            proc = subprocess.run(
                ["git", "rev-list", "--count", f"HEAD..{upstream_ref}"],
                cwd=str(ROOT), capture_output=True, text=True, check=False
            )
            if proc.returncode == 0 and proc.stdout.strip().isdigit():
                behind = int(proc.stdout.strip())
                if behind > 0:
                    result["behind"] = True
                    result["behind_count"] = behind

                    remote_skill = subprocess.run(
                        ["git", "show", f"{upstream_ref}:SKILL.md"],
                        cwd=str(ROOT), capture_output=True, text=True, check=False
                    )
                    if remote_skill.returncode == 0:
                        result["remote_version"] = extract_version_str(remote_skill.stdout)
        except Exception:
            pass
    else:
        # No git repo — download SKILL.md from GitHub to check version
        print("  No git repo found; checking remote version via GitHub...")
        # Find installed SKILL.md
        from paths import HOME
        installed_skill = HOME / ".agents/skills/engineer-shovel/SKILL.md"
        if not installed_skill.exists():
            installed_skill = ROOT / "SKILL.md"
        if installed_skill.exists():
            result["local_version"] = extract_version(installed_skill)

        remote_content = _download_file(f"{RAW_BASE}/SKILL.md")
        if remote_content:
            result["fetched"] = True
            result["remote_version"] = extract_version_str(remote_content.decode("utf-8", errors="replace"))
            if result["local_version"] and result["remote_version"]:
                if result["local_version"] != result["remote_version"]:
                    result["behind"] = True
                    result["behind_count"] = 1  # unknown exact count
        else:
            result["error"] = "Could not fetch remote SKILL.md from GitHub"

    return result


def _get_upstream_ref() -> str:
    """Resolve the upstream tracking ref, falling back to origin/<current-branch>."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "@{upstream}"],
            cwd=str(ROOT), capture_output=True, text=True, check=False
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return "@{upstream}"
    except Exception:
        pass

    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(ROOT), capture_output=True, text=True, check=False
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return f"origin/{proc.stdout.strip()}"
    except Exception:
        pass

    return "origin/main"


def extract_version_str(content: str) -> str | None:
    """Extract version from SKILL.md content string."""
    m = re.search(r'version:\s*"([^"]+)"', content)
    return m.group(1) if m else None


def pull_repo() -> bool:
    """Pull latest changes from remote. Returns True on success."""
    try:
        proc = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=str(ROOT), capture_output=True, text=True, check=False
        )
        return proc.returncode == 0
    except Exception:
        return False


def run_health(command: str, target: str, scope: str, dry_run: bool = False) -> int:
    health_command = "check" if command == "check" else "repair"
    args = [
        sys.executable,
        str(ROOT / "scripts" / "health.py"),
        health_command,
        "--target",
        target,
        "--scope",
        scope,
    ]
    if dry_run:
        args.append("--dry-run")
    proc = subprocess.run(args, text=True, check=False)
    return proc.returncode


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
    parser.add_argument(
        "--skip-health",
        action="store_true",
        help="Only sync Engineer Shovel files; skip external component health checks"
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip checking remote for updates (offline mode)"
    )
    
    args = parser.parse_args()
    
    targets = ["opencode", "claude"] if args.target == "both" else [args.target]
    print_update_summary(targets, args.scope, args.command)

    remote_status = None
    if not args.skip_fetch:
        remote_status = check_remote_updates()
        if remote_status["behind"]:
            lv = remote_status["local_version"] or "?"
            rv = remote_status["remote_version"] or "?"
            print(f"⚠  Remote has {remote_status['behind_count']} new commit(s) (local: v{lv}, remote: v{rv})")
    
    if args.command == "check":
        all_ok = True
        
        if remote_status and remote_status.get("error"):
            print(f"  Remote check: {remote_status['error']}")
        
        if remote_status and remote_status.get("behind"):
            all_ok = False
            if remote_status.get("remote_version"):
                print(f"  Remote version: v{remote_status['remote_version']}")
        
        for target in targets:
            installed_version = extract_version(
                INSTALL_PATHS[target][args.scope]["skill"] / "SKILL.md"
            )
            if installed_version:
                print(f"\n{target.upper()} installed: v{installed_version}")
            
            result = check_installation(target, args.scope)
            print_check_report(result, verbose=args.verbose)
            if result["summary"]["issues"] > 0:
                all_ok = False
        
        health_rc = 0 if args.skip_health else run_health("check", args.target, args.scope, dry_run=True)
        if health_rc != 0:
            all_ok = False
        
        print()
        if all_ok:
            print("✔ All installations are up to date")
            return 0
        else:
            print("✘ Some installations need updates. Run: /tool-update --full")
            return 1
    
    elif args.command == "sync":
        use_download = remote_status and not remote_status.get("has_git", False)

        if use_download:
            # Path B: download from GitHub (no git repo)
            if remote_status and remote_status.get("behind"):
                print(f"\n⟳ Upgrading from v{remote_status['local_version']} to v{remote_status['remote_version']}...")
            elif remote_status and remote_status.get("fetched"):
                print(f"\n✔ Already up to date: v{remote_status['local_version']}")
                if not args.skip_health:
                    health_rc = run_health("sync", args.target, args.scope, dry_run=args.dry_run)
                    return health_rc
                return 0

            total_updated = 0
            with tempfile.TemporaryDirectory(prefix="es-sync-") as tmp:
                tmp_dir = Path(tmp)
                for target in targets:
                    print(f"\nSyncing {target.upper()} ({args.scope})...")
                    for file_type in ["skill", "commands"]:
                        installed = get_installed_files(target, args.scope, file_type)
                        remote = _download_remote_files(file_type, tmp_dir)
                        if not remote:
                            print(f"  Warning: Could not download {file_type} files")
                            continue
                        comparison = compare_files(installed, remote)
                        updated = sync_files(comparison, target=target, scope=args.scope, dry_run=args.dry_run)
                        total_updated += updated

            if args.dry_run:
                print(f"\nDRY-RUN: Would update {total_updated} file(s)")
            else:
                print(f"\n✔ Updated {total_updated} file(s)")
                for target in targets:
                    paths = INSTALL_PATHS[target][args.scope]
                    skill_path = paths.get("skill")
                    if skill_path:
                        new_ver = extract_version(skill_path / "SKILL.md")
                        if new_ver:
                            print(f"  {target.upper()} now at v{new_ver}")

            if not args.skip_health:
                health_rc = run_health("sync", args.target, args.scope, dry_run=args.dry_run)
                if health_rc != 0:
                    return health_rc
            return 0

        # Path A: git-based sync
        if remote_status and remote_status.get("behind"):
            print("\n⟳ Pulling latest from remote...")
            if not args.dry_run:
                if pull_repo():
                    print("✔ Repo updated to latest")
                else:
                    print("✘ Failed to pull latest changes from remote")
                    print(f"  Try: cd {ROOT} && git pull")
                    return 1
            else:
                print("  DRY-RUN: Would pull latest from remote")

        total_updated = 0
        for target in targets:
            print(f"\nSyncing {target.upper()} ({args.scope})...")

            for file_type in ["skill", "commands"]:
                installed = get_installed_files(target, args.scope, file_type)
                repo = get_repo_files(file_type)
                comparison = compare_files(installed, repo)

                updated = sync_files(comparison, target=target, scope=args.scope, dry_run=args.dry_run)
                total_updated += updated

        if args.dry_run:
            print(f"\nDRY-RUN: Would update {total_updated} file(s)")
        else:
            print(f"\n✔ Updated {total_updated} file(s)")

            if total_updated > 0:
                for target in targets:
                    new_ver = extract_version(
                        INSTALL_PATHS[target][args.scope]["skill"] / "SKILL.md"
                    )
                    if new_ver:
                        print(f"  {target.upper()} now at v{new_ver}")

        if not args.skip_health:
            health_rc = run_health("sync", args.target, args.scope, dry_run=args.dry_run)
            if health_rc != 0:
                return health_rc

        return 0
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
