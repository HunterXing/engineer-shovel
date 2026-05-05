#!/usr/bin/env python3
"""Check and repair Engineer Shovel supporting components."""

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

STATUS_OK = "ok"
STATUS_MISSING = "missing"
STATUS_UNCONFIGURED = "unconfigured"
STATUS_BLOCKED = "blocked"


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
        return self.status in {STATUS_MISSING, STATUS_UNCONFIGURED, STATUS_BLOCKED}


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
            repair="pipx install code-review-graph && code-review-graph install && code-review-graph build",
            target="component",
        )
    status = runner.run(["code-review-graph", "status"])
    graph_dir = ROOT / ".code-review-graph"
    if status.returncode != 0:
        return CheckResult("code-review-graph", STATUS_UNCONFIGURED, "status failed", "code-review-graph install", "component")
    if not graph_dir.exists():
        return CheckResult("code-review-graph", STATUS_UNCONFIGURED, "graph not built", "code-review-graph build", "component")
    if not _has_crg_mcp_opencode() and not _has_crg_mcp_claude():
        return CheckResult("code-review-graph", STATUS_UNCONFIGURED, "MCP not configured", "code-review-graph install --platform opencode", "component")
    return CheckResult("code-review-graph", STATUS_OK, path, target="component")


def check_superpowers(target: str, runner: CommandRunner) -> CheckResult:
    if target == "opencode":
        config = HOME / ".config/opencode/opencode.json"
        if config.exists() and "superpowers@git+https://github.com/obra/superpowers.git" in config.read_text(encoding="utf-8"):
            return CheckResult("superpowers", STATUS_OK, str(config), target=target)
        return CheckResult("superpowers", STATUS_UNCONFIGURED, "OpenCode plugin missing", "add plugin entry to opencode.json", target)

    result = runner.run(["claude", "plugin", "list"])
    if result.returncode == 0 and "superpowers" in result.stdout.lower():
        return CheckResult("superpowers", STATUS_OK, "Claude plugin installed", target=target)
    return CheckResult("superpowers", STATUS_MISSING, "Claude plugin missing", "claude plugin install superpowers@claude-plugins-official", target)


def check_caveman(target: str, runner: CommandRunner) -> CheckResult:
    if target == "opencode":
        markers = [
            HOME / ".agents/skills/caveman",
            HOME / ".agents/skills/JuliusBrussee-caveman",
            HOME / ".config/opencode/commands/caveman.md",
        ]
        if any(path.exists() for path in markers):
            return CheckResult("caveman", STATUS_OK, "OpenCode marker found", target=target)
        return CheckResult("caveman", STATUS_MISSING, "OpenCode marker missing", "npx skills add JuliusBrussee/caveman -a opencode", target)

    result = runner.run(["claude", "plugin", "list"])
    if result.returncode == 0 and "caveman" in result.stdout.lower():
        return CheckResult("caveman", STATUS_OK, "Claude plugin installed", target=target)
    if (HOME / ".claude/plugins/caveman").exists():
        return CheckResult("caveman", STATUS_OK, "Claude plugin directory found", target=target)
    return CheckResult("caveman", STATUS_MISSING, "Claude plugin missing", "claude plugin marketplace add JuliusBrussee/caveman && claude plugin install caveman@caveman", target)


def check_rtk(runner: CommandRunner) -> CheckResult:
    path = which("rtk")
    if not path:
        return CheckResult("rtk", STATUS_MISSING, "not found in PATH", "curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh", "component")
    runner.run(["rtk", "init", "--show"])
    return CheckResult("rtk", STATUS_OK, path, target="component")


def check_claude_mem(target: str) -> CheckResult:
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
        return CheckResult("claude-mem", STATUS_MISSING, "not installed for OpenCode", "npx claude-mem install --ide opencode", target)
    result = CommandRunner(dry_run=False).run(["claude", "plugin", "list"])
    if result.returncode == 0 and "claude-mem" in result.stdout.lower():
        return CheckResult("claude-mem", STATUS_OK, "Claude plugin installed", target=target)
    if not has_bun:
        return CheckResult("claude-mem", STATUS_BLOCKED, "Bun required", "curl -fsSL https://bun.sh/install | bash", target)
    return CheckResult("claude-mem", STATUS_MISSING, "not installed for Claude Code", "npx claude-mem install --ide claude", target)


def check_openspec() -> CheckResult:
    path = which("openspec")
    if path:
        return CheckResult("openspec", STATUS_OK, path, target="component")
    return CheckResult(
        "openspec",
        STATUS_MISSING,
        "not found in PATH",
        "npm install -g @fission-ai/openspec@latest && openspec init  # per project",
        "component",
    )


def check_gsd(target: str) -> CheckResult:
    command_dir = HOME / ".config/opencode/commands" if target == "opencode" else HOME / ".claude/commands"
    if target == "opencode":
        skill_dirs = [HOME / ".agents/skills", HOME / ".config/opencode/skills"]
    else:
        skill_dirs = [HOME / ".claude/skills"]
    has_gsd = any(command_dir.glob("gsd-*.md")) if command_dir.exists() else False
    has_gsd = has_gsd or any(
        skill_dir.exists() and any(skill_dir.glob("gsd-*/SKILL.md"))
        for skill_dir in skill_dirs
    )
    if has_gsd:
        return CheckResult("gsd", STATUS_OK, "GSD files found", target=target)
    flag = "--opencode" if target == "opencode" else "--claude"
    return CheckResult("gsd", STATUS_MISSING, "GSD files missing", f"npx -y get-shit-done-cc@latest {flag} --global", target)


def check_ecc(target: str, runner: CommandRunner) -> CheckResult:
    if target == "opencode":
        markers = [HOME / ".config/opencode/ecc", HOME / ".config/opencode/commands/plan.md"]
        if any(path.exists() for path in markers):
            return CheckResult("ecc", STATUS_OK, "OpenCode ECC marker found", target=target)
        return CheckResult("ecc", STATUS_BLOCKED, "OpenCode ECC automatic repair not implemented", "run ./install.sh --profile full --target opencode from ECC checkout", target)

    plugin_list = runner.run(["claude", "plugin", "list"])
    rules = HOME / ".claude/rules/ecc/common"
    if plugin_list.returncode == 0 and "everything-claude-code" in plugin_list.stdout and rules.exists():
        return CheckResult("ecc", STATUS_OK, "Claude plugin and common rules found", target=target)
    if plugin_list.returncode == 0 and "everything-claude-code" in plugin_list.stdout:
        packs = ",".join(detect_project_rule_packs()) or "common"
        return CheckResult("ecc", STATUS_UNCONFIGURED, "ECC plugin installed but common rules missing", f"install ECC common rules and detected packs: {packs}", target)
    return CheckResult("ecc", STATUS_MISSING, "Claude plugin missing", "claude plugin marketplace add https://github.com/affaan-m/everything-claude-code && claude plugin install everything-claude-code@everything-claude-code", target)


def check_components(targets: list[str], runner: CommandRunner) -> list[CheckResult]:
    checks = [check_code_review_graph(runner), check_rtk(runner), check_openspec()]
    for target in targets:
        checks.extend([
            check_superpowers(target, runner),
            check_caveman(target, runner),
            check_claude_mem(target),
            check_gsd(target),
            check_ecc(target, runner),
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
        agent = "opencode" if targets[0] == "opencode" else "claude-code"
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
        ide = "--ide opencode" if target == "opencode" else "--ide claude"
        runner.run(["npx", "-y", "claude-mem", "install", ide])


def repair_openspec(runner: CommandRunner, targets: list[str]) -> None:
    del targets
    runner.run(["npm", "install", "-g", "@fission-ai/openspec@latest"])


def repair_gsd(runner: CommandRunner, targets: list[str]) -> None:
    if set(targets) == {"opencode", "claude"}:
        runner.run(["npx", "-y", "get-shit-done-cc@latest", "--all", "--global"])
        return
    flag = "--opencode" if targets == ["opencode"] else "--claude"
    runner.run(["npx", "-y", "get-shit-done-cc@latest", flag, "--global"])


def repair_ecc(runner: CommandRunner, targets: list[str]) -> None:
    if "claude" in targets:
        runner.run(["claude", "plugin", "marketplace", "add", "https://github.com/affaan-m/everything-claude-code"])
        runner.run(["claude", "plugin", "install", "everything-claude-code@everything-claude-code"])
    if "opencode" in targets:
        runner.commands.append(["blocked", "ecc-opencode", "manual install required"])


def repair_components(checks: list[CheckResult], targets: list[str], runner: CommandRunner) -> None:
    names = {check.name for check in checks if check.needs_repair}
    if "code-review-graph" in names:
        repair_code_review_graph(runner, targets)
    if "rtk" in names:
        repair_rtk(runner, targets)
    if "openspec" in names:
        repair_openspec(runner, targets)
    if "gsd" in names:
        repair_gsd(runner, targets)
    if "caveman" in names:
        repair_caveman(runner, targets)
    for target in targets:
        if any(check.name == "superpowers" and check.target == target and check.needs_repair for check in checks):
            repair_superpowers(runner, target)
    if "claude-mem" in names:
        repair_claude_mem(runner, targets)
    if "ecc" in names:
        repair_ecc(runner, targets)


def print_report(title: str, checks: list[CheckResult]) -> None:
    print(title)
    print("=" * len(title))
    for check in checks:
        label = f"{check.name}/{check.target}" if check.target not in {"base", "component", "system"} else check.name
        print(f"- {label}: {check.status.upper()} {check.detail}".rstrip())


def run_health(command: str, target: str, dry_run: bool = False) -> int:
    targets = expand_targets(target)
    runner = CommandRunner(dry_run=False)
    checks = check_base_dependencies(targets, runner) + check_components(targets, runner)
    print_report("HEALTH", checks)
    if command == "repair":
        repair_components(checks, targets, CommandRunner(dry_run=dry_run))
        checks = check_base_dependencies(targets, runner) + check_components(targets, runner)
        print_report("VERIFY", checks)
    return 1 if any(check.needs_repair for check in checks) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check and repair Engineer Shovel supporting components")
    parser.add_argument("command", choices=["check", "repair"])
    parser.add_argument("--target", choices=["opencode", "claude", "both"], default="both")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return run_health(args.command, args.target, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
