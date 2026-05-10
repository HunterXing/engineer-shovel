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
    expected = f"# {len(commands)} executable slash commands"
    if expected not in readme and f"{len(commands)} executable slash commands" not in readme:
        errors.append("README.md: structure block command count does not match commands/ directory")
    readme_zh = (ROOT / "README_zh.md").read_text(encoding="utf-8")
    for command in sorted(commands):
        if f"/{command}" not in readme_zh:
            errors.append(f"README_zh.md: missing command reference /{command}")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for command in sorted(commands):
        if f"/{command}" not in skill:
            errors.append(f"SKILL.md: missing command table reference /{command}")

    research = (COMMAND_DIR / "tool-research.md").read_text(encoding="utf-8")
    if "special mode axis" not in research or "--quick" not in research or "--web" not in research:
        errors.append("commands/tool-research.md: must explain its special quick/web/deep mode axis")

    mode_routing = (ROOT / "docs" / "mode-routing.md").read_text(encoding="utf-8")
    if "tool-research" not in mode_routing or "--quick / --web / --deep" not in mode_routing:
        errors.append("docs/mode-routing.md: must document tool-research as the special mode-axis exception")

    tool_graph = (COMMAND_DIR / "tool-graph.md").read_text(encoding="utf-8").lower()
    if "diagnostic" not in tool_graph:
        errors.append("commands/tool-graph.md: must stay positioned as a diagnostic command")

    tool_update = (COMMAND_DIR / "tool-update.md").read_text(encoding="utf-8")
    if "Single user-facing entry point" not in tool_update:
        errors.append("commands/tool-update.md: must keep single user-facing update entry positioning")
    if errors:
        print("Reference validation failed:", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Reference validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
