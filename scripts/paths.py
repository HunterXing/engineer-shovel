"""Shared install path definitions for Engineer Shovel."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

INSTALL_PATHS = {
    "opencode": {
        "global": {
            "skill": HOME / ".agents/skills/engineer-shovel",
            "commands": HOME / ".config/opencode/commands",
        },
        "local": {
            "skill": ROOT / ".agents/skills/engineer-shovel",
            "commands": ROOT / ".opencode/commands",
        },
    },
    "claude": {
        "global": {
            "skill": HOME / ".claude/skills/engineer-shovel",
            "commands": HOME / ".claude/commands",
        },
        "local": {
            "skill": ROOT / ".claude/skills/engineer-shovel",
            "commands": ROOT / ".claude/commands",
        },
    },
}

# Alias: "claude-code" maps to "claude" for compatibility with install.sh
INSTALL_PATHS["claude-code"] = INSTALL_PATHS["claude"]


def install_paths(target: str, scope: str) -> dict:
    """Get install paths for a given target/scope, including extra key defaults.

    Accepts "claude" or "claude-code" as target (both map to the same paths).
    """
    # Normalize target: "claude-code" -> "claude"
    normalized = "claude" if target == "claude-code" else target
    base = dict(INSTALL_PATHS[normalized][scope])
    base.setdefault("gsd_skills", _default_gsd_skills(normalized, scope))
    return base


def _default_gsd_skills(target: str, scope: str) -> list[Path]:
    if target == "opencode":
        if scope == "global":
            return [HOME / ".agents/skills", HOME / ".config/opencode/skills"]
        return [ROOT / ".agents/skills", ROOT / ".opencode/skills"]
    if scope == "global":
        return [HOME / ".claude/skills"]
    return [ROOT / ".claude/skills"]
