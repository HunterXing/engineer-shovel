#!/usr/bin/env python3
"""Report repository structure and token-cost inventory for Engineer Shovel."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMAND_DIR = ROOT / "commands"
DOCS_DIR = ROOT / "docs"


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def command_names() -> list[str]:
    return sorted(path.stem for path in COMMAND_DIR.glob("tool-*.md"))


def external_sources() -> dict[str, str]:
    install = (ROOT / "install.sh").read_text(encoding="utf-8")
    sources: dict[str, str] = {}
    for name, url in re.findall(r'^(\w+_REPO)="([^"]+)"', install, re.MULTILINE):
        sources[name] = url
    for name, sha in re.findall(r'^(\w+_SHA)="([0-9a-f]{40})"', install, re.MULTILINE):
        sources[name] = sha
    return sources


def repeated_lines() -> list[str]:
    counts: dict[str, int] = {}
    for path in COMMAND_DIR.glob("tool-*.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            normalized = line.strip()
            if len(normalized) < 30 or normalized.startswith("---"):
                continue
            counts[normalized] = counts.get(normalized, 0) + 1
    return sorted(line for line, count in counts.items() if count > 1)


def main() -> int:
    commands = command_names()
    docs = sorted(path.name for path in DOCS_DIR.glob("*.md"))
    command_lines = {path.name: line_count(path) for path in COMMAND_DIR.glob("tool-*.md")}
    report = {
        "commands": commands,
        "command_count": len(commands),
        "docs": docs,
        "docs_count": len(docs),
        "skill_lines": line_count(ROOT / "SKILL.md"),
        "install_lines": line_count(ROOT / "install.sh"),
        "command_lines": command_lines,
        "average_command_lines": round(sum(command_lines.values()) / max(len(command_lines), 1), 2),
        "external_sources": external_sources(),
        "repeated_command_lines": repeated_lines(),
        "token_hotspots": [
            "SKILL.md standing context",
            "commands/tool-*.md repeated cost-mode text",
            "deep modes that invoke GSD, review-work, or multi-source research",
            "install.sh external repository bootstrap paths",
        ],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
