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
from typing import Callable, Optional

from paths import HOME, ROOT, install_paths

DEPENDENCY_MANIFEST_PATH = ROOT / "scripts" / "dependency_manifest.json"

STATUS_OK = "ok"
STATUS_MISSING = "missing"
STATUS_UNCONFIGURED = "unconfigured"
STATUS_BLOCKED = "blocked"
STATUS_MANUAL_UPGRADE = "manual-upgrade-recommended"


def load_dependency_manifest() -> dict[str, dict]:
    try:
        return json.loads(DEPENDENCY_MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load dependency manifest: {e}")
        return {}


DEPENDENCY_MANIFEST = load_dependency_manifest()


def manifest_entry(name: str) -> dict:
    return DEPENDENCY_MANIFEST.get(name, {})


def manifest_repair_hint(name: str, target: Optional[str], fallback: str) -> str:
    repair_hint = manifest_entry(name).get("repair_hint")
    if isinstance(repair_hint, str):
        return repair_hint
    if isinstance(repair_hint, dict):
        if target and repair_hint.get(target):
            return repair_hint[target]
        if repair_hint.get("both"):
            return repair_hint["both"]
    return fallback


def which(name: str) -> Optional[str]:
    """Find executable in PATH with error handling."""
    try:
        return shutil.which(name)
    except Exception:
        return None


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
    executor: Optional[Callable[[list[str]], CommandResult]] = None

    def run(self, command: list[str]) -> CommandResult:
        """Run a command with error handling and timeout."""
        self.commands.append(command)
        if self.dry_run:
            return CommandResult(0, "DRY-RUN")
        if self.executor is not None:
            return self.executor(command)
        try:
            proc = subprocess.run(
                command,
                text=True,
                capture_output=True,
                check=False,
                timeout=300  # 5 minute timeout
            )
        except FileNotFoundError as exc:
            return CommandResult(127, "", str(exc))
        except subprocess.TimeoutExpired as exc:
            return CommandResult(124, "", f"Command timed out after {exc.timeout}s")
        except Exception as exc:
            return CommandResult(1, "", str(exc))
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
        elif name == "pipx":
            checks.append(CheckResult(name="pipx", status=STATUS_MISSING, detail="not found in PATH", repair="python3 -m pip install --user pipx && python3 -m pipx ensurepath", target="base"))
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
    """Check if code-review-graph MCP is configured in OpenCode config (global or local)."""
    candidates = [
        HOME / ".config/opencode/opencode.json",
        HOME / ".config/opencode/opencode.jsonc",
        ROOT / ".opencode/opencode.json",
        ROOT / ".opencode.json",
    ]
    for config in candidates:
        if not config.exists():
            continue
        try:
            data = json.loads(config.read_text(encoding="utf-8"))
            mcp = data.get("mcpServers", data.get("mcp", {}))
            if "code-review-graph" in mcp:
                return True
        except (json.JSONDecodeError, OSError):
            continue
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


def check_code_review_graph(runner: CommandRunner, scope: str) -> CheckResult:
    path = which("code-review-graph")
    has_uvx = which("uvx") is not None
    if not path and not has_uvx:
        return CheckResult(
            name="code-review-graph",
            status=STATUS_MISSING,
            detail="not found in PATH (no code-review-graph or uvx)",
            repair=manifest_repair_hint("code-review-graph", None, "pipx install code-review-graph"),
            target="component",
        )
    if not path and has_uvx:
        # uvx can run code-review-graph on demand for MCP
        if _has_crg_mcp_opencode() or _has_crg_mcp_claude():
            return CheckResult("code-review-graph", STATUS_OK, "via uvx (on-demand)", target="component")
    if path:
        status = runner.run(["code-review-graph", "status"])
        graph_dir = ROOT / ".code-review-graph"
        if status.returncode != 0:
            return CheckResult("code-review-graph", STATUS_UNCONFIGURED, "status failed", "code-review-graph build", "component")
        if not graph_dir.exists():
            return CheckResult("code-review-graph", STATUS_UNCONFIGURED, "graph not built", "code-review-graph build", "component")
    if not _has_crg_mcp_opencode() and not _has_crg_mcp_claude():
        repair_hint = manifest_repair_hint("code-review-graph", None, "add MCP config to opencode.json")
        return CheckResult("code-review-graph", STATUS_UNCONFIGURED, "MCP not configured", repair_hint, "component")
    return CheckResult("code-review-graph", STATUS_OK, path or "via uvx (on-demand)", target="component")


def check_superpowers(target: str, runner: CommandRunner) -> CheckResult:
    if target == "opencode":
        # Check via opencode plugin command first (OpenCode 1.15+)
        result = runner.run(["opencode", "plugin", "superpowers"])
        plugin_ok = "installed" in result.stdout.lower() or "already" in result.stdout.lower()
        # Check command wrappers exist (superpowers:brainstorm, etc.)
        cmd_dir = HOME / ".config/opencode" / "commands"
        wrappers = ["superpowers:brainstorm.md", "superpowers:tdd.md", "superpowers:debug.md", "superpowers:superpowers.md"]
        has_wrappers = all((cmd_dir / w).exists() for w in wrappers)
        if plugin_ok and has_wrappers:
            return CheckResult("superpowers", STATUS_OK, "opencode plugin + /superpowers:* wrappers", target=target)
        if plugin_ok:
            return CheckResult("superpowers", STATUS_OK, "opencode plugin superpowers", target=target)
        # Fallback: check config file for git URL or plugin name
        for config_path in [
            HOME / ".config/opencode/opencode.json",
            HOME / ".config/opencode/opencode.jsonc",
            ROOT / ".opencode/opencode.json",
        ]:
            if config_path.exists():
                raw = config_path.read_text(encoding="utf-8")
                if "superpowers" in raw.lower():
                    status = STATUS_OK if has_wrappers else STATUS_UNCONFIGURED
                    detail = str(config_path) + (" + wrappers" if has_wrappers else " (wrappers missing)")
                    return CheckResult("superpowers", status, detail, target=target)
        return CheckResult("superpowers", STATUS_UNCONFIGURED, "OpenCode plugin missing", manifest_repair_hint("superpowers", target, "opencode plugin superpowers -g"), target)

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
    # GSD v1.39+ installs agent files to ~/.config/opencode/agents/
    agent_dir = HOME / ".config/opencode/agents"
    if not has_gsd and agent_dir.exists():
        has_gsd = any(agent_dir.glob("gsd-*.md"))
    if has_gsd:
        return CheckResult("gsd", STATUS_OK, f"GSD files found ({scope})", target=target)
    flag = "--opencode" if target == "opencode" else "--claude"
    scope_flag = "--local" if scope == "local" else "--global"
    return CheckResult("gsd", STATUS_MISSING, f"GSD files missing ({scope})", manifest_repair_hint("gsd", target, f"npx -y get-shit-done-cc@latest {flag} {scope_flag}"), target)


def _ecc_cmd_dir() -> Optional[Path]:
    """Find ECC commands directory."""
    try:
        result = subprocess.run(["npm", "root", "-g"], text=True, capture_output=True, check=False)
        if result.returncode == 0:
            p = Path(result.stdout.strip()) / "ecc-universal" / "commands"
            if p.exists():
                return p
    except Exception:
        pass
    # Fallback: common install locations
    for prefix in [
        Path("/usr/local/lib/node_modules"),
        Path("/usr/lib/node_modules"),
        HOME / ".local/share/vfox/cache/nodejs",
    ]:
        if prefix.exists():
            for child in prefix.iterdir() if prefix.is_dir() else []:
                p = child / "lib/node_modules/ecc-universal/commands"
                if p.exists():
                    return p
    return None


def _ecc_commands_linked(cmd_dir: Path) -> bool:
    """Check if ECC commands are symlinked into the given commands directory."""
    src = _ecc_cmd_dir()
    if not src:
        return False  # ECC not installed
    linked = 0
    for f in src.iterdir():
        if f.suffix == ".md":
            target = cmd_dir / f.name
            if target.is_symlink() and target.resolve() == f.resolve():
                linked += 1
    # At least one symlink == ECC commands are linked
    return linked > 0


def check_ecc(target: str, runner: CommandRunner, scope: str) -> CheckResult:
    if scope == "local":
        return CheckResult("ecc", STATUS_BLOCKED, "local scope not supported", "use --scope global or skip ECC for project-local installs", target)
    if target == "opencode":
        markers = [HOME / ".config/opencode/ecc", HOME / ".config/opencode/commands/plan.md"]
        has_marker = any(path.exists() for path in markers)
        cmd_dir = HOME / ".config/opencode" / "commands"
        has_symlinks = _ecc_commands_linked(cmd_dir)
        if has_marker and has_symlinks:
            return CheckResult("ecc", STATUS_OK, "installed + commands linked", target=target)
        if has_marker and not has_symlinks:
            return CheckResult("ecc", STATUS_UNCONFIGURED, "ECC installed but commands not linked", "link ECC commands to opencode commands dir", target)
        if has_symlinks:
            return CheckResult("ecc", STATUS_OK, "commands linked", target=target)
        if _ecc_cmd_dir():
            return CheckResult("ecc", STATUS_UNCONFIGURED, "ECC found on disk but not linked for OpenCode", "link ECC commands to opencode commands dir", target)
        return CheckResult("ecc", STATUS_MANUAL_UPGRADE, "OpenCode ECC automatic repair not implemented", manifest_repair_hint("ecc", target, "run the ECC installer manually for OpenCode"), target)

    plugin_list = runner.run(["claude", "plugin", "list"])
    rules = HOME / ".claude/rules/ecc/common"
    if plugin_list.returncode == 0 and "everything-claude-code" in plugin_list.stdout and rules.exists():
        return CheckResult("ecc", STATUS_OK, "Claude plugin and common rules found", target=target)
    if plugin_list.returncode == 0 and "everything-claude-code" in plugin_list.stdout:
        packs = ",".join(detect_project_rule_packs()) or "common"
        return CheckResult("ecc", STATUS_UNCONFIGURED, "ECC plugin installed but common rules missing", f"install ECC common rules and detected packs: {packs}", target)
    return CheckResult("ecc", STATUS_MISSING, "Claude plugin missing", manifest_repair_hint("ecc", target, "claude plugin marketplace add https://github.com/affaan-m/everything-claude-code && claude plugin install everything-claude-code@everything-claude-code"), target)


def _write_crg_mcp_config(config_path: Path) -> None:
    """Write code-review-graph MCP in OpenCode 1.15 format."""
    data = {}
    if config_path.exists():
        data = json.loads(config_path.read_text(encoding="utf-8") or "{}")
    if "$schema" not in data:
        data["$schema"] = "https://opencode.ai/config.json"
    if "mcp" not in data:
        data["mcp"] = {}
    data["mcp"]["code-review-graph"] = {
        "type": "local",
        "command": ["uvx", "code-review-graph", "serve"],
        "enabled": True,
    }
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def repair_code_review_graph(runner: CommandRunner, targets: list[str], scope: str) -> None:
    if not which("code-review-graph") and not which("uvx"):
        if which("pipx"):
            runner.run(["pipx", "install", "code-review-graph"])
        else:
            runner.run(["python3", "-m", "pip", "install", "--user", "code-review-graph"])
    for target in targets:
        if target == "opencode":
            config_path = ROOT / ".opencode/opencode.json" if scope == "local" else HOME / ".config/opencode/opencode.json"
            if runner.dry_run:
                runner.commands.append(["write_mcp_config", str(config_path)])
            else:
                _write_crg_mcp_config(config_path)
            # Remove old-format config if present
            old = ROOT / ".opencode.json"
            if old.exists():
                old.unlink()
        else:
            runner.run(["code-review-graph", "install", "--platform", "claude-code"])
    if (ROOT / ".git").exists():
        runner.run(["code-review-graph", "build"])


def repair_superpowers(runner: CommandRunner, target: str) -> None:
    if target == "claude":
        runner.run(["claude", "plugin", "install", "superpowers@claude-plugins-official"])
        return
    # OpenCode 1.15+: use opencode plugin command
    if which("opencode"):
        runner.run(["opencode", "plugin", "superpowers", "-g"])
        _repair_superpowers_wrappers(runner)
        return
    # Fallback: write git URL to config
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
    _repair_superpowers_wrappers(runner)


SUPERPOWERS_COMMANDS = {
    "superpowers:brainstorm": ("brainstorming", "Structured ideation for design decisions and creative problem-solving"),
    "superpowers:parallel-agents": ("dispatching-parallel-agents", "Orchestrate parallel subagents for independent work streams"),
    "superpowers:execute-plan": ("executing-plans", "Execute structured plans with verification checkpoints"),
    "superpowers:finish-branch": ("finishing-a-development-branch", "Complete and verify a development branch before merge"),
    "superpowers:receive-review": ("receiving-code-review", "Process and respond to code review feedback systematically"),
    "superpowers:request-review": ("requesting-code-review", "Prepare and submit code changes for review"),
    "superpowers:subagent-dev": ("subagent-driven-development", "Decompose complex tasks via specialized subagents"),
    "superpowers:debug": ("systematic-debugging", "Scientific method debugging pipeline with root cause tracing"),
    "superpowers:tdd": ("test-driven-development", "Test-driven development: red-green-refactor workflow"),
    "superpowers:git-worktrees": ("using-git-worktrees", "Manage parallel development with git worktrees"),
    "superpowers:superpowers": ("using-superpowers", "List, discover, and manage available superpowers skills"),
    "superpowers:verify": ("verification-before-completion", "Structured verification checklist before task sign-off"),
    "superpowers:write-plan": ("writing-plans", "Create structured planning documentation and execution roadmaps"),
    "superpowers:write-skill": ("writing-skills", "Create and maintain reusable skill files"),
}


def _repair_superpowers_wrappers(runner: CommandRunner) -> None:
    """Generate /superpowers:* command wrappers for each superpowers skill."""
    cmd_dir = HOME / ".config/opencode" / "commands"
    cmd_dir.mkdir(parents=True, exist_ok=True)
    for cmd_name, (skill_name, desc) in SUPERPOWERS_COMMANDS.items():
        target = cmd_dir / f"{cmd_name}.md"
        if target.exists():
            continue
        if runner.dry_run:
            runner.commands.append(["write", str(target), f"wraps skill({skill_name})"])
            continue
        content = f"""---
description: {desc}
---

# /{cmd_name}

Load the **{skill_name}** skill from superpowers:

```
skill(name="{skill_name}")
```

Follow its instructions exactly.
"""
        target.write_text(content, encoding="utf-8")


def repair_caveman(runner: CommandRunner, targets: list[str]) -> None:
    for target in targets:
        agent = "opencode" if target == "opencode" else "claude"
        runner.run(["bash", "-lc", f"curl -fsSL --retry 3 --retry-delay 2 --max-time 120 https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash -s -- --only {agent}"])


def repair_rtk(runner: CommandRunner, targets: list[str]) -> None:
    if not which("rtk"):
        runner.run(["bash", "-lc", "curl -fsSL --retry 3 --retry-delay 2 --max-time 120 https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh"])
    for target in targets:
        if target == "opencode":
            runner.run(["rtk", "init", "-g", "--opencode"])
        else:
            runner.run(["rtk", "init", "-g"])


def repair_claude_mem(runner: CommandRunner, targets: list[str]) -> None:
    # Auto-install Bun if missing
    if not which("bun"):
        runner.run(["bash", "-lc", "curl -fsSL --retry 3 --retry-delay 2 --max-time 60 https://bun.sh/install | bash"])
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


def _link_ecc_commands(cmd_dir: Path, runner: CommandRunner) -> None:
    """Symlink ECC command files into OpenCode commands directory."""
    src = _ecc_cmd_dir()
    if not src:
        return
    cmd_dir.parent.mkdir(parents=True, exist_ok=True)
    cmd_dir.mkdir(exist_ok=True)
    for f in src.iterdir():
        if f.suffix == ".md":
            target = cmd_dir / f.name
            if not target.exists():
                if runner.dry_run:
                    runner.commands.append(["ln", "-s", str(f), str(target)])
                else:
                    target.symlink_to(f)


def repair_ecc(runner: CommandRunner, targets: list[str], scope: str) -> None:
    if scope == "local":
        runner.commands.append(["blocked", "ecc-local", "use --scope global or skip ECC"])
        return
    if "claude" in targets:
        runner.run(["claude", "plugin", "marketplace", "add", "https://github.com/affaan-m/everything-claude-code"])
        runner.run(["claude", "plugin", "install", "everything-claude-code@everything-claude-code"])
    if "opencode" in targets:
        cmd_dir = HOME / ".config/opencode" / "commands"
        _link_ecc_commands(cmd_dir, runner)


@dataclass
class ComponentDef:
    name: str
    check: Callable[..., CheckResult]
    repair: Callable[..., None]
    needs_target: bool = False
    needs_scope: bool = False
    check_params: tuple[str, ...] = ()
    repair_params: tuple[str, ...] = ("runner", "targets")
    repair_per_target: bool = False


COMPONENTS: list[ComponentDef] = [
    ComponentDef("code-review-graph", check_code_review_graph, repair_code_review_graph,
                 needs_scope=True, check_params=("runner", "scope"), repair_params=("runner", "targets", "scope")),
    ComponentDef("rtk", check_rtk, repair_rtk,
                 check_params=("runner",)),
    ComponentDef("openspec", check_openspec, repair_openspec,
                 check_params=()),
    ComponentDef("superpowers", check_superpowers, repair_superpowers,
                 needs_target=True, check_params=("target", "runner"), repair_per_target=True),
    ComponentDef("caveman", check_caveman, repair_caveman,
                 needs_target=True, check_params=("target", "runner")),
    ComponentDef("claude-mem", check_claude_mem, repair_claude_mem,
                 needs_target=True, check_params=("target", "runner")),
    ComponentDef("gsd", check_gsd, repair_gsd,
                 needs_target=True, needs_scope=True, check_params=("target", "scope"),
                 repair_params=("runner", "targets", "scope")),
    ComponentDef("ecc", check_ecc, repair_ecc,
                 needs_target=True, needs_scope=True, check_params=("target", "runner", "scope"),
                 repair_params=("runner", "targets", "scope")),
]


def _component_args(comp: ComponentDef, target: str, runner: CommandRunner, scope: str) -> tuple:
    param_map = {"target": target, "runner": runner, "scope": scope}
    return tuple(param_map[p] for p in comp.check_params)


def _repair_args(comp: ComponentDef, targets: list[str], runner: CommandRunner, scope: str) -> tuple:
    param_map = {"runner": runner, "targets": targets, "scope": scope}
    return tuple(param_map[p] for p in comp.repair_params)


def check_components(targets: list[str], runner: CommandRunner, scope: str) -> list[CheckResult]:
    # Normalize: ensure targets is always a list of strings
    if isinstance(targets, str):
        targets = expand_targets(targets)
    checks: list[CheckResult] = []
    for comp in COMPONENTS:
        if comp.needs_target:
            for target in targets:
                checks.append(comp.check(*_component_args(comp, target, runner, scope)))
        else:
            checks.append(comp.check(*_component_args(comp, "", runner, scope)))
    return checks


def repair_components(checks: list[CheckResult], targets: list[str], runner: CommandRunner, scope: str) -> None:
    # Normalize: ensure targets is always a list of strings
    if isinstance(targets, str):
        targets = expand_targets(targets)
    names = {check.name for check in checks if check.can_auto_repair}
    if "pipx" in names and not which("pipx"):
        if which("python3"):
            runner.run(["python3", "-m", "pip", "install", "--user", "pipx"])
            runner.run(["python3", "-m", "pipx", "ensurepath"])
        elif which("python"):
            runner.run(["python", "-m", "pip", "install", "--user", "pipx"])
            runner.run(["python", "-m", "pipx", "ensurepath"])

    for comp in COMPONENTS:
        if comp.name not in names:
            continue
        if comp.repair_per_target:
            for target in targets:
                if any(c.name == comp.name and c.target == target and c.needs_repair for c in checks):
                    comp.repair(*_repair_args(comp, [target], runner, scope))
        else:
            comp.repair(*_repair_args(comp, targets, runner, scope))


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
