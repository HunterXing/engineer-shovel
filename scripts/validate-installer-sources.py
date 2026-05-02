#!/usr/bin/env python3
"""Validate that install.sh external repositories are pinned to commit SHAs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "install.sh"
REQUIRED = ("ECC", "CAVEMAN", "SUPERPOWERS", "RTK")


def main() -> int:
    text = INSTALL.read_text(encoding="utf-8")
    errors: list[str] = []
    for prefix in REQUIRED:
        if not re.search(rf'^{prefix}_REPO="https://github\.com/[^"]+"', text, re.MULTILINE):
            errors.append(f"{prefix}_REPO missing or not https GitHub URL")
        if not re.search(rf'^{prefix}_SHA="[0-9a-f]{{40}}"', text, re.MULTILINE):
            errors.append(f"{prefix}_SHA missing 40-character commit pin")
    if "clone_pinned_repo" not in text:
        errors.append("clone_pinned_repo helper missing")
    if errors:
        print("Installer source validation failed:", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Installer source validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
