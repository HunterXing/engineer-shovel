#!/usr/bin/env python3
"""Validate command references and basic repository integrity."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMAND_DIR = ROOT / "commands"
DOCS = [ROOT / "SKILL.md", ROOT / "README.md", ROOT / "README_zh.md", ROOT / "CHANGELOG.md"]
DOCS.extend(sorted((ROOT / "docs").glob("*.md")))
DOCS.extend(sorted(COMMAND_DIR.glob("*.md")))


def main() -> int:
    commands = {path.stem for path in COMMAND_DIR.glob("tool-*.md")}
    errors: list[str] = []
    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"/tool-[a-z-]+", text):
            name = match.group(0).lstrip("/")
            if name not in commands:
                errors.append(f"{path.relative_to(ROOT)}: unknown command reference {match.group(0)}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"# {len(commands)} executable slash commands" not in readme:
        errors.append("README.md: structure block command count does not match commands/ directory")
    readme_zh = (ROOT / "README_zh.md").read_text(encoding="utf-8")
    for command in sorted(commands):
        if f"/{command}" not in readme_zh:
            errors.append(f"README_zh.md: missing command reference /{command}")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for command in sorted(commands):
        if f"/{command}" not in skill:
            errors.append(f"SKILL.md: missing command table reference /{command}")
    if errors:
        print("Reference validation failed:", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Reference validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
