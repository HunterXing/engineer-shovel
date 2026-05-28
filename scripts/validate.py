#!/usr/bin/env python3
"""Unified validation: schema, references, and markdown links."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
COMMAND_DIR = ROOT / "commands"


# ── schema ──────────────────────────────────────────────────────────

REQUIRED_FIELDS = {
    "description", "argument-hint", "cost-profile", "risk-level",
    "recommended-mode", "allowed-tools", "escalates-to", "depends-on",
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


def validate_schema() -> int:
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


# ── references ──────────────────────────────────────────────────────

DOCS = [
    ROOT / "SKILL.md", ROOT / "SKILL-full.md", ROOT / "README.md", ROOT / "README_zh.md",
    *sorted((ROOT / "docs").glob("*.md")),
    *sorted(COMMAND_DIR.glob("*.md")),
]


def validate_references() -> int:
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
        # Also check for badge count
        badge_count = f"commands-{len(commands)}_active"
        if badge_count not in readme:
            errors.append(f"README.md: structure block command count does not match commands/ directory ({len(commands)} commands)")
    readme_zh = (ROOT / "README_zh.md").read_text(encoding="utf-8")
    for command in sorted(commands):
        if f"/{command}" not in readme_zh:
            errors.append(f"README_zh.md: missing command reference /{command}")
    
    # Check SKILL-full.md (Level 2) for all command references
    skill_full = (ROOT / "SKILL-full.md").read_text(encoding="utf-8")
    for command in sorted(commands):
        if f"/{command}" not in skill_full:
            errors.append(f"SKILL-full.md: missing command table reference /{command}")
    
    # SKILL.md (Level 1) only needs main workflow commands
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    main_commands = {"tool-quick", "tool-fix", "tool-feat", "tool-plan"}
    for command in sorted(main_commands):
        if f"/{command}" not in skill:
            errors.append(f"SKILL.md: missing main workflow command reference /{command}")

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


# ── markdown links ──────────────────────────────────────────────────

LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#"))


def validate_links() -> int:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts or "node_modules" in path.parts:
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


# ── CLI ─────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Engineer Shovel repository")
    parser.add_argument(
        "command",
        choices=["schema", "references", "links", "all"],
        help="Validation to run",
    )
    args = parser.parse_args()

    if args.command == "schema":
        return validate_schema()
    elif args.command == "references":
        return validate_references()
    elif args.command == "links":
        return validate_links()

    rc = 0
    for name, fn in [("schema", validate_schema), ("references", validate_references), ("links", validate_links)]:
        print(f"\n── {name} ──")
        if fn() != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
