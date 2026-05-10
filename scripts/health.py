#!/usr/bin/env python3
"""Check and repair Engineer Shovel supporting components.

This script is intentionally limited to the component layer: external tools,
plugins, MCP wiring, and runtime prerequisites. Router file sync belongs to
`scripts/sync.py`. User-facing workflows should prefer `/tool-update`, which
combines router sync with component health reporting and repair.
"""

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
DEPENDENCY_MANIFEST_PATH = ROOT / "scripts" / "dependency_manifest.json"

STATUS_OK = "ok"
STATUS_MISSING = "missing"
STATUS_UNCONFIGURED = "unconfigured"
STATUS_BLOCKED = "blocked"
STATUS_MANUAL_UPGRADE = "manual-upgrade-recommended"


def load_dependency_manifest() -> dict[str, dict]:
    try:
        return json.loads(DEPENDENCY_MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


DEPENDENCY_MANIFEST = load_dependency_manifest()


def manifest_entry(name: str) -> dict:
    return DEPENDENCY_MANIFEST.get(name, {})


def manifest_repair_hint(name: str, target: str | None, fallback: str) -> str:
    repair_hint = manifest_entry(name).get("repair_hint")
    if isinstance(repair_hint, str):
        return repair_hint
    if isinstance(repair_hint, dict):
        if target and repair_hint.get(target):
            return repair_hint[target]
        if repair_hint.get("both"):
            return repair_hint["both"]
    return fallback


def which(name: str) -> str | None:
    return shutil.which(name)


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str = ""
    repair: str = ""
    target: str = "system"

    @property
    def needs_repair(self) -> bool:
        return self.status in {STATUS_MISSING, STATUS_UNCONFIGURED, STATUS_BLOCKED, STATUS_MANUAL_UPGRADE}

    @property
    def can_auto_repair(self) -> bool:
        return self.status in {STATUS_MISSING, STATUS_UNCONFIGURED}


@dataclass
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


@dataclass
class CommandRunner:
    dry_run: bool = False
    commands: list[list[str]] = field(default_factory=list)
    executor: Callable[[list[str]], CommandResult] | None = None

    def run(self, command: list[str]) -> CommandResult:
        self.commands.append(command)
        if self.dry_run:
            return CommandResult(0, "DRY-RUN")
        if self.executor is not None:
            return self.executor(command)
        try:
            proc = subprocess.run(command, text=True, capture_output=True, check=False)
        except FileNotFoundError as exc:
            return CommandResult(127, "", str(exc))
        return CommandResult(proc.returncode, proc.stdout, proc.stderr)


def expand_targets(target: str) -> list[str]:
    if target == "both":
        return ["opencode", "claude"]
    return [target]


def install_paths(target: str, scope: str) -> dict[str, Path | list[Path]]:
    return {
        "opencode": {
            "global": {
                "skill": HOME / ".agents/skills/engineer-shovel",
                "commands": HOME / ".config/opencode/commands",
                "gsd_skills": [HOME / ".agents/skills", HOME / ".config/opencode/skills"],
            },
            "local": {
                "skill": ROOT / ".agents/skills/engineer-shovel",
                "commands": ROOT / ".opencode/commands",
                "gsd_skills": [ROOT / ".agents/skills", ROOT / ".opencode/skills"],
            },
        },
        "claude": {
            "global": {
                "skill": HOME / ".claude/skills/engineer-shovel",
                "commands": HOME / ".claude/commands",
                "gsd_skills": [HOME / ".claude/skills"],
            },
            "local": {
                "skill": ROOT / ".claude/skills/engineer-shovel",
                "commands": ROOT / ".claude/commands",
                "gsd_skills": [ROOT / ".claude/skills"],
            },
        },
    }[target][scope]


def check_base_dependencies(targets: list[str], runner: CommandRunner) -> list[CheckResult]:
    del runner
    names = ["git", "python3", "pipx", "node", "npx"]
    if "opencode" in targets:
        names.append("opencode")
    if "claude" in targets:
        names.append("claude")

    checks: list[CheckResult] = []
    for name in names:
        path = which(name)
        if path:
            checks.append(CheckResult(name=name, status=STATUS_OK, detail=path, target="base"))
        else:
            checks.append(CheckResult(name=name, status=STATUS_MISSING, detail="not found in PATH", target="base"))
    return checks


LANGUAGE_MARKERS = {
    "typescript": ["package.json", "tsconfig.json", "vite.config.ts", "next.config.js"],
    "python": ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"],
    "golang": ["go.mod"],
    "php": ["composer.json"],
    "swift": ["Package.swift"],
    "rust": ["Cargo.toml"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
}


def detect_project_rule_packs() -> list[str]:
    detected: list[str] = []
    for pack, markers in LANGUAGE_MARKERS.items():
        if any((ROOT / marker).exists() for marker in markers):
            detected.append(pack)
    return detected


def _has_crg_mcp_opencode() -> bool:
    """Check if code-review-graph MCP is configured in OpenCode config."""
    config = HOME / ".config/opencode/opencode.json"
    if not config.exists():
        return False
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
        mcp = data.get("mcpServers", data.get("mcp", {}))
        return "code-review-graph" in mcp
    except (json.JSONDecodeError, OSError):
        return False


def _has_crg_mcp_claude() -> bool:
    """Check if code-review-graph MCP is configured in Claude Code settings."""
    for path in [
        HOME / ".claude" / "settings.json",
        HOME / ".claude.json",
    ]:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            mcp = data.get("mcpServers", {})
            if "code-review-graph" in mcp:
                return True
        except (json.JSONDecodeError, OSError):
            continue
    return False


def check_code_review_graph(runner: CommandRunner) -> CheckResult:
    path = which("code-review-graph")
    if not path:
        return CheckResult(
            name="code-review-graph",
            status=STATUS_MISSING,
            detail="not found in PATH",
            repair=manifest_repair_hint("code-review-graph", None, "pipx install code-review-graph && code-review-graph install && code-review-graph build"),
            target="component",
        )
    status = runner.run(["code-review-graph", "status"])
    graph_dir = ROOT / ".code-review-graph"
    if status.returncode != 0:
        return CheckResult("code-review-graph", STATUS_UNCONFIGURED, "status failed", "code-review-graph install", "component")
    if not graph_dir.exists():
        return CheckResult("code-review-graph", STATUS_UNCONFIGURED, "graph not built", "code-review-graph build", "component")
    if not _has_crg_mcp_opencode() and not _has_crg_mcp_claude():
        return CheckResult("code-review-graph", STATUS_UNCONFIGURED, "MCP not configured", manifest_repair_hint("code-review-graph", None, "code-review-graph install --platform opencode"), "component")
    return CheckResult("code-review-graph", STATUS_OK, path, target="component")


def check_superpowers(target: str, runner: CommandRunner) -> CheckResult:
    if target == "opencode":
        config = HOME / ".config/opencode/opencode.json"
        if config.exists() and "superpowers@git+https://github.com/obra/superpowers.git" in config.read_text(encoding="utf-8"):
            return CheckResult("superpowers", STATUS_OK, str(config), target=target)
        return CheckResult("superpowers", STATUS_UNCONFIGURED, "OpenCode plugin missing", manifest_repair_hint("superpowers", target, "add plugin entry to opencode.json"), target)

    result = runner.run(["claude", "plugin", "list"])
    if result.returncode == 0 and "superpowers" in result.stdout.lower():
        return CheckResult("superpowers", STATUS_OK, "Claude plugin installed", target=target)
    return CheckResult("superpowers", STATUS_MISSING, "Claude plugin missing", manifest_repair_hint("superpowers", target, "claude plugin install superpowers@claude-plugins-official"), target)


def check_caveman(target: str, runner: CommandRunner) -> CheckResult:
    if target == "opencode":
        markers = [
            HOME / ".agents/skills/caveman",
            HOME / ".agents/skills/JuliusBrussee-caveman",
            HOME / ".config/opencode/commands/caveman.md",
        ]
        if any(path.exists() for path in markers):
            return CheckResult("caveman", STATUS_OK, "OpenCode marker found", target=target)
        return CheckResult("caveman", STATUS_MISSING, "OpenCode marker missing", manifest_repair_hint("caveman", target, "npx skills add JuliusBrussee/caveman -a opencode"), target)

    result = runner.run(["claude", "plugin", "list"])
    if result.returncode == 0 and "caveman" in result.stdout.lower():
        return CheckResult("caveman", STATUS_OK, "Claude plugin installed", target=target)
    if (HOME / ".claude/plugins/caveman").exists():
        return CheckResult("caveman", STATUS_OK, "Claude plugin directory found", target=target)
    return CheckResult("caveman", STATUS_MISSING, "Claude plugin missing", manifest_repair_hint("caveman", target, "claude plugin marketplace add JuliusBrussee/caveman && claude plugin install caveman@caveman"), target)


def check_rtk(runner: CommandRunner) -> CheckResult:
    path = which("rtk")
    if not path:
        return CheckResult("rtk", STATUS_MISSING, "not found in PATH", manifest_repair_hint("rtk", None, "curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh"), "component")
    runner.run(["rtk", "init", "--show"])
    return CheckResult("rtk", STATUS_OK, path, target="component")


def check_claude_mem(target: str, runner: CommandRunner) -> CheckResult:
    has_bun = which("bun") is not None
    if target == "opencode":
        config = HOME / ".config/opencode/opencode.json"
        if config.exists():
            try:
                raw = config.read_text(encoding="utf-8")
                if "claude-mem" in raw.lower():
                    return CheckResult("claude-mem", STATUS_OK, str(config), target=target)
            except Exception:
                return CheckResult("claude-mem", STATUS_UNCONFIGURED, "config unreadable", "npx claude-mem install --ide opencode", target)
        if not has_bun:
            return CheckResult("claude-mem", STATUS_BLOCKED, "Bun required", "curl -fsSL https://bun.sh/install | bash", target)
        return CheckResult("claude-mem", STATUS_MISSING, "not installed for OpenCode", manifest_repair_hint("claude-mem", target, "npx claude-mem install --ide opencode"), target)
    result = runner.run(["claude", "plugin", "list"])
    if result.returncode == 0 and "claude-mem" in result.stdout.lower():
        return CheckResult("claude-mem", STATUS_OK, "Claude plugin installed", target=target)
    if not has_bun:
        return CheckResult("claude-mem", STATUS_BLOCKED, "Bun required", "curl -fsSL https://bun.sh/install | bash", target)
    return CheckResult("claude-mem", STATUS_MISSING, "not installed for Claude Code", manifest_repair_hint("claude-mem", target, "npx claude-mem install --ide claude"), target)


def check_openspec() -> CheckResult:
    path = which("openspec")
    if path:
        return CheckResult("openspec", STATUS_OK, path, target="component")
    return CheckResult(
        "openspec",
        STATUS_MISSING,
        "not found in PATH",
        manifest_repair_hint("openspec", None, "npm install -g @fission-ai/openspec@latest"),
        "component",
    )


def check_gsd(target: str, scope: str) -> CheckResult:
    paths = install_paths(target, scope)
    command_dir = paths["commands"]
    skill_dirs = paths["gsd_skills"]
    has_gsd = any(command_dir.glob("gsd-*.md")) if command_dir.exists() else False
    has_gsd = has_gsd or any(
        skill_dir.exists() and any(skill_dir.glob("gsd-*/SKILL.md"))
        for skill_dir in skill_dirs
    )
    if has_gsd:
        return CheckResult("gsd", STATUS_OK, f"GSD files found ({scope})", target=target)
    flag = "--opencode" if target == "opencode" else "--claude"
    scope_flag = "--local" if scope == "local" else "--global"
    return CheckResult("gsd", STATUS_MISSING, f"GSD files missing ({scope})", manifest_repair_hint("gsd", target, f"npx -y get-shit-done-cc@latest {flag} {scope_flag}"), target)


def check_ecc(target: str, runner: CommandRunner, scope: str) -> CheckResult:
    if scope == "local":
        return CheckResult("ecc", STATUS_BLOCKED, "local scope not supported", "use --scope global or skip ECC for project-local installs", target)
    if target == "opencode":
        markers = [HOME / ".config/opencode/ecc", HOME / ".config/opencode/commands/plan.md"]
        if any(path.exists() for path in markers):
            return CheckResult("ecc", STATUS_OK, "OpenCode ECC marker found", target=target)
        return CheckResult("ecc", STATUS_MANUAL_UPGRADE, "OpenCode ECC automatic repair not implemented", manifest_repair_hint("ecc", target, "run the ECC installer manually for OpenCode"), target)

    plugin_list = runner.run(["claude", "plugin", "list"])
    rules = HOME / ".claude/rules/ecc/common"
    if plugin_list.returncode == 0 and "everything-claude-code" in plugin_list.stdout and rules.exists():
        return CheckResult("ecc", STATUS_OK, "Claude plugin and common rules found", target=target)
    if plugin_list.returncode == 0 and "everything-claude-code" in plugin_list.stdout:
        packs = ",".join(detect_project_rule_packs()) or "common"
        return CheckResult("ecc", STATUS_UNCONFIGURED, "ECC plugin installed but common rules missing", f"install ECC common rules and detected packs: {packs}", target)
    return CheckResult("ecc", STATUS_MISSING, "Claude plugin missing", manifest_repair_hint("ecc", target, "claude plugin marketplace add https://github.com/affaan-m/everything-claude-code && claude plugin install everything-claude-code@everything-claude-code"), target)


def check_components(targets: list[str], runner: CommandRunner, scope: str) -> list[CheckResult]:
    checks = [check_code_review_graph(runner), check_rtk(runner), check_openspec()]
    for target in targets:
        checks.extend([
            check_superpowers(target, runner),
            check_caveman(target, runner),
            check_claude_mem(target, runner),
            check_gsd(target, scope),
            check_ecc(target, runner, scope),
        ])
    return checks


def repair_code_review_graph(runner: CommandRunner, targets: list[str]) -> None:
    if not which("code-review-graph"):
        if which("pipx"):
            runner.run(["pipx", "install", "code-review-graph"])
        else:
            runner.run(["python3", "-m", "pip", "install", "--user", "code-review-graph"])
    for target in targets:
        platform_flag = "opencode" if target == "opencode" else "claude-code"
        runner.run(["code-review-graph", "install", "--platform", platform_flag])
    if (ROOT / ".git").exists():
        runner.run(["code-review-graph", "build"])


def repair_superpowers(runner: CommandRunner, target: str) -> None:
    if target == "claude":
        runner.run(["claude", "plugin", "install", "superpowers@claude-plugins-official"])
        return
    config = HOME / ".config/opencode/opencode.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    if config.exists():
        backup = config.with_suffix(config.suffix + ".bak")
        if not runner.dry_run:
            backup.write_bytes(config.read_bytes())
            data = json.loads(config.read_text(encoding="utf-8") or "{}")
        else:
            data = {}
    else:
        data = {}
    plugins = data.get("plugin", [])
    if isinstance(plugins, str):
        plugins = [plugins]
    entry = "superpowers@git+https://github.com/obra/superpowers.git"
    if entry not in plugins:
        plugins.append(entry)
    data["plugin"] = plugins
    if runner.dry_run:
        runner.commands.append(["write", str(config), entry])
    else:
        config.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def repair_caveman(runner: CommandRunner, targets: list[str]) -> None:
    command = ["bash", "-lc", "curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash"]
    if len(targets) == 1:
        agent = "opencode" if targets[0] == "opencode" else "claude"
        command = ["bash", "-lc", f"curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash -s -- --only {agent}"]
    runner.run(command)


def repair_rtk(runner: CommandRunner, targets: list[str]) -> None:
    if not which("rtk"):
        runner.run(["bash", "-lc", "curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh"])
    for target in targets:
        if target == "opencode":
            runner.run(["rtk", "init", "-g", "--opencode"])
        else:
            runner.run(["rtk", "init", "-g"])


def repair_claude_mem(runner: CommandRunner, targets: list[str]) -> None:
    for target in targets:
        ide = "opencode" if target == "opencode" else "claude"
        runner.run(["npx", "-y", "claude-mem", "install", "--ide", ide])


def repair_openspec(runner: CommandRunner, targets: list[str]) -> None:
    del targets
    runner.run(["npm", "install", "-g", "@fission-ai/openspec@latest"])


def repair_gsd(runner: CommandRunner, targets: list[str], scope: str) -> None:
    scope_flag = "--local" if scope == "local" else "--global"
    if set(targets) == {"opencode", "claude"}:
        runner.run(["npx", "-y", "get-shit-done-cc@latest", "--all", scope_flag])
        return
    flag = "--opencode" if targets == ["opencode"] else "--claude"
    runner.run(["npx", "-y", "get-shit-done-cc@latest", flag, scope_flag])


def repair_ecc(runner: CommandRunner, targets: list[str], scope: str) -> None:
    if scope == "local":
        runner.commands.append(["blocked", "ecc-local", "use --scope global or skip ECC"])
        return
    if "claude" in targets:
        runner.run(["claude", "plugin", "marketplace", "add", "https://github.com/affaan-m/everything-claude-code"])
        runner.run(["claude", "plugin", "install", "everything-claude-code@everything-claude-code"])
    if "opencode" in targets:
        runner.commands.append(["blocked", "ecc-opencode", "manual install required"])


def repair_components(checks: list[CheckResult], targets: list[str], runner: CommandRunner, scope: str) -> None:
    names = {check.name for check in checks if check.can_auto_repair}
    if "code-review-graph" in names:
        repair_code_review_graph(runner, targets)
    if "rtk" in names:
        repair_rtk(runner, targets)
    if "openspec" in names:
        repair_openspec(runner, targets)
    if "gsd" in names:
        repair_gsd(runner, targets, scope)
    if "caveman" in names:
        repair_caveman(runner, targets)
    for target in targets:
        if any(check.name == "superpowers" and check.target == target and check.needs_repair for check in checks):
            repair_superpowers(runner, target)
    if "claude-mem" in names:
        repair_claude_mem(runner, targets)
    if "ecc" in names:
        repair_ecc(runner, targets, scope)


def print_report(title: str, checks: list[CheckResult]) -> None:
    print(title)
    print("=" * len(title))
    for check in checks:
        label = f"{check.name}/{check.target}" if check.target not in {"base", "component", "system"} else check.name
        print(f"- {label}: {check.status.upper()} {check.detail}".rstrip())


def print_health_summary(command: str, target: str, scope: str, checks: list[CheckResult]) -> None:
    mode_label = "--check" if command == "check" else "--full"
    repair_count = sum(1 for check in checks if check.needs_repair)
    auto_repair_count = sum(1 for check in checks if check.can_auto_repair)
    blocked_count = sum(1 for check in checks if check.status == STATUS_BLOCKED)
    manual_count = sum(1 for check in checks if check.status == STATUS_MANUAL_UPGRADE)
    print("\nHEALTH SUMMARY")
    print("==============")
    print(f"Mode: {mode_label}")
    print(f"Target: {target}")
    print(f"Scope: {scope}")
    print(f"Checks: {len(checks)}")
    print(f"Needs repair: {repair_count}")
    print(f"Auto-repairable: {auto_repair_count}")
    print(f"Blocked: {blocked_count}")
    print(f"Manual upgrade recommended: {manual_count}")


def run_health(command: str, target: str, scope: str = "global", dry_run: bool = False) -> int:
    targets = expand_targets(target)
    # Health probes are read-only; dry-run only skips the repair step below.
    runner = CommandRunner(dry_run=False)
    checks = check_base_dependencies(targets, runner) + check_components(targets, runner, scope)
    print_report("HEALTH", checks)
    print_health_summary(command, target, scope, checks)
    if command == "repair":
        repair_components(checks, targets, CommandRunner(dry_run=dry_run), scope)
        checks = check_base_dependencies(targets, runner) + check_components(targets, runner, scope)
        print_report("VERIFY", checks)
        print_health_summary(command, target, scope, checks)
    return 1 if any(check.needs_repair for check in checks) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check and repair Engineer Shovel supporting components")
    parser.add_argument("command", choices=["check", "repair"])
    parser.add_argument("--target", choices=["opencode", "claude", "both"], default="both")
    parser.add_argument("--scope", choices=["global", "local"], default="global")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return run_health(args.command, args.target, scope=args.scope, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
