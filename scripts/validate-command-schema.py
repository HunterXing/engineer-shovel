#!/usr/bin/env python3
"""Validate command frontmatter for machine-readable routing metadata."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMAND_DIR = ROOT / "commands"

REQUIRED_FIELDS = {
    "description",
    "argument-hint",
    "cost-profile",
    "risk-level",
    "recommended-mode",
    "allowed-tools",
    "escalates-to",
    "depends-on",
    "when-to-use",
}
VALID_COSTS = {"low", "medium", "high", "variable"}
VALID_RISKS = {"low", "medium", "high", "variable"}
VALID_MODES = {"--fast", "--standard", "--deep", "--quick", "--web", "--full"}


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("frontmatter must start at line 1")
    try:
        end = lines[1:].index("---") + 1
    except ValueError as exc:
        raise ValueError("frontmatter must close with ---") from exc
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith(" "):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def validate_list_field(path: Path, fields: dict[str, str], key: str) -> list[str]:
    value = fields[key]
    if not re.fullmatch(r"\[[^\]]*\]", value):
        raise ValueError(f"{key} must use inline list syntax, e.g. [] or [/tool-plan]")
    return [item.strip() for item in value[1:-1].split(",") if item.strip()]


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        fields = parse_frontmatter(path)
        missing = sorted(REQUIRED_FIELDS - fields.keys())
        if missing:
            errors.append(f"missing fields: {', '.join(missing)}")
            return errors
        if fields["cost-profile"] not in VALID_COSTS:
            errors.append(f"invalid cost-profile: {fields['cost-profile']}")
        if fields["risk-level"] not in VALID_RISKS:
            errors.append(f"invalid risk-level: {fields['risk-level']}")
        if fields["recommended-mode"] not in VALID_MODES:
            errors.append(f"invalid recommended-mode: {fields['recommended-mode']}")
        for key in ("allowed-tools", "escalates-to", "depends-on"):
            validate_list_field(path, fields, key)
        if len(fields["when-to-use"]) < 20:
            errors.append("when-to-use must be specific enough for routing")
    except ValueError as exc:
        errors.append(str(exc))
    return errors


def main() -> int:
    failures: list[str] = []
    for path in sorted(COMMAND_DIR.glob("tool-*.md")):
        for error in validate_file(path):
            failures.append(f"{path.relative_to(ROOT)}: {error}")
    if failures:
        print("Command schema validation failed:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("Command schema validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
