#!/usr/bin/env python3
"""Measure static token-cost proxies for Engineer Shovel."""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def estimate_tokens(text: str) -> int:
    # Conservative static proxy: 1 token ~= 4 UTF-8 chars for English-heavy docs.
    return math.ceil(len(text) / 4)


def file_stats(path: Path) -> dict[str, int | str]:
    text = path.read_text(encoding="utf-8")
    return {
        "path": str(path.relative_to(ROOT)),
        "lines": len(text.splitlines()),
        "chars": len(text),
        "estimated_tokens": estimate_tokens(text),
    }


def main() -> int:
    command_files = sorted((ROOT / "commands").glob("tool-*.md"))
    command_stats = [file_stats(path) for path in command_files]
    report = {
        "measurement_kind": "static_proxy",
        "precision": "estimate",
        "note": "Counts static Markdown size only; live model/session savings remain unknown unless Caveman/RTK provide measured data.",
        "skill": file_stats(ROOT / "SKILL.md"),
        "commands": command_stats,
        "commands_total_estimated_tokens": sum(int(item["estimated_tokens"]) for item in command_stats),
        "average_command_estimated_tokens": round(
            sum(int(item["estimated_tokens"]) for item in command_stats) / max(len(command_stats), 1), 2
        ),
        "caveman_session": "unknown",
        "rtk_project": "unknown",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
