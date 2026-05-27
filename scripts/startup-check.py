#!/usr/bin/env python3
"""Startup health check for Engineer Shovel.

Quick check of tool availability on session start.
Output is formatted for direct display to user.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# Tool definitions: (name, check_command, display_name)
TOOLS = [
    ("caveman", None, "Caveman"),
    ("rtk", "rtk", "RTK"),
    ("code-review-graph", "code-review-graph", "Code Review Graph"),
    ("superpowers", None, "Superpowers"),
    ("openspec", "openspec", "OpenSpec"),
    ("gsd", None, "GSD"),
    ("ecc", None, "ECC"),
]


def check_tool(name: str, cmd: str | None) -> tuple[str, bool, str]:
    """Check if a tool is available. Returns (name, available, detail)."""
    if cmd:
        path = shutil.which(cmd)
        if path:
            return (name, True, path)
        return (name, False, "not in PATH")
    
    # For tools without direct commands, check common markers
    from paths import HOME
    markers = {
        "caveman": [
            HOME / ".agents/skills/caveman",
            HOME / ".config/opencode/commands/caveman.md",
        ],
        "superpowers": [
            HOME / ".config/opencode/commands/superpowers:brainstorm.md",
        ],
        "gsd": [
            HOME / ".config/opencode/commands/gsd-explore.md",
        ],
        "ecc": [
            HOME / ".config/opencode/ecc",
            HOME / ".config/opencode/commands/plan.md",
        ],
    }
    
    for marker in markers.get(name, []):
        if marker.exists():
            return (name, True, str(marker))
    
    return (name, False, "not configured")


def run_health_check() -> int:
    """Run startup health check and print results."""
    print("🪖 Engineer Shovel — Health Check")
    print("=" * 40)
    
    ready = 0
    total = len(TOOLS)
    
    for name, cmd, display in TOOLS:
        tool_name, available, detail = check_tool(name, cmd)
        if available:
            print(f"✅ {display}: installed")
            ready += 1
        else:
            print(f"⚠️  {display}: {detail}")
    
    print("=" * 40)
    print(f"📊 {ready}/{total} tools ready")
    
    if ready == total:
        print("🚀 All tools available!")
    elif ready >= total - 2:
        print("💡 Most tools ready. Use /tool-update --check for details.")
    else:
        print("⚠️  Several tools missing. Run: bash install.sh --recommended")
    
    return 0 if ready >= total - 2 else 1


if __name__ == "__main__":
    sys.exit(run_health_check())
