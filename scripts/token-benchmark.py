#!/usr/bin/env python3
"""Measure static token-cost proxies for Engineer Shovel."""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def estimate_tokens(text: str) -> int:
    cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    ascii_count = len(text) - cjk_count
    return math.ceil(ascii_count / 4 + cjk_count / 1.5)


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
        "measurement_sources": {
            "static_markdown": {
                "kind": "static_proxy",
                "precision": "estimate",
                "method": "ceil(character_count / 4)",
            },
            "caveman_session": {
                "kind": "measured_session",
                "status": "unknown",
                "source": "/caveman-stats",
            },
            "rtk_project": {
                "kind": "measured_tool_output",
                "status": "unknown",
                "source": "rtk gain --project --format json",
            },
        },
        "note": "Counts static Markdown size only; live Caveman/RTK savings remain unknown until those tools report measured data.",
        "skill": file_stats(ROOT / "SKILL.md"),
        "commands": command_stats,
        "commands_total_estimated_tokens": sum(int(item["estimated_tokens"]) for item in command_stats),
        "average_command_estimated_tokens": round(
            sum(int(item["estimated_tokens"]) for item in command_stats) / max(len(command_stats), 1), 2
        ),
        "caveman_session": {"status": "unknown", "measured_tokens_saved": None},
        "rtk_project": {"status": "unknown", "measured_tokens_saved": None},
    }
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
