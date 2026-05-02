#!/usr/bin/env python3
"""Validate local Markdown links without requiring external packages."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#"))


def main() -> int:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in LINK.finditer(line):
                raw = match.group(1).split("#", 1)[0].strip()
                if not raw or is_external(raw):
                    continue
                target = (path.parent / unquote(raw)).resolve()
                if ROOT not in target.parents and target != ROOT:
                    errors.append(f"{path.relative_to(ROOT)}:{line_no}: link escapes repo: {match.group(1)}")
                elif not target.exists():
                    errors.append(f"{path.relative_to(ROOT)}:{line_no}: missing link target: {match.group(1)}")
    if errors:
        print("Markdown link validation failed:", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Markdown link validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
