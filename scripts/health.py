#!/usr/bin/env python3
"""Check and repair Engineer Shovel supporting components.

This script is intentionally limited to the component layer: external tools,
plugins, MCP wiring, and runtime prerequisites. Router file sync belongs to
`scripts/sync.py`. User-facing workflows should prefer `/tool-update`, which
combines router sync with component health reporting and repair.
"""

import argparse
import json
import re
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
STATUS_OUTDATED = "outdated"


# Known latest upstream versions. Updated when new releases land.
# Live npm / GitHub queries would be more accurate but are slow + offline-fragile,
# so we keep this as the deterministic baseline; a fresh /tool-update --full will
# pull whatever is current upstream regardless of this dict.
LATEST_KNOWN = {
    "rtk": "0.43.0",
    "code-review-graph": "2.3.6",
    "gsd": "1.50.0-canary.0",
    "openspec": "1.5.0",
    "claude-mem": "13.10.0",
    "ecc": "2.0.0",
    "superpowers-claude": "6.1.1",
    "caveman": "1.9.1",
}


# ---------------------------------------------------------------------------
# Version drift detection
# ---------------------------------------------------------------------------
#
# `/tool-update --full` should keep users on latest upstream. The original
# STATUS_OK only meant "installed", not "latest". When local drifts behind
# upstream, we want health check to surface OUTDATED so /tool-update --full
# auto-repair re-runs the install path (which already pulls latest via
# latest-installer strategy). OUTDATED is auto-repairable because every
# component's repair_xxx() function is idempotent and re-pulls upstream.

_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?")


def _parse_version(v: Optional[str]) -> Optional[tuple]:
    """Parse '1.50.0-canary.0' / '2.0.0' / 'v1.9.1' into a sortable tuple.

    Format: ((major, minor, patch), pre_tag_string_or_None).
    pre-release tags are compared lexically; missing tag sorts after equal
    numeric components (semver-style). Stable enough for drift comparison;
    not a full semver implementation.
    """
    if not v:
        return None
    v = v.strip().lstrip("v")
    m = _VERSION_RE.match(v)
    if not m:
        return None
    nums = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    pre = m.group(4) or None
    return (nums, pre)


def _is_older(local: str, latest: str) -> bool:
    """Return True iff `local` < `latest`. Equal or unknown → False (no drift)."""
    a = _parse_version(local)
    b = _parse_version(latest)
    if a is None or b is None:
        return False  # unknown → never report drift
    if a[0] != b[0]:
        return a[0] < b[0]
    # Same numeric — compare pre-release tag. Per semver, a version with
    # a pre-release tag is LOWER than the same version without one.
    if a[1] is None and b[1] is None:
        return False
    if a[1] is None:
        return False  # 1.50.0 > 1.50.0-canary.0
    if b[1] is None:
        return True
    return a[1] < b[1]


def _detect_local_version(component: str) -> Optional[str]:
    """Best-effort local version probe. Returns None when version is not
    detectable (caveman SKILL.md has no version metadata, etc.) so health
    check does not false-positive."""
    try:
        if component == "rtk":
            proc = subprocess.run(
                ["rtk", "--version"], capture_output=True, text=True, timeout=10
            )
            m = _VERSION_RE.search(proc.stdout)
            return m.group(0) if m else None
        if component == "code-review-graph":
            proc = subprocess.run(
                ["uvx", "code-review-graph", "--version"],
                capture_output=True, text=True, timeout=10,
            )
            m = _VERSION_RE.search(proc.stdout)
            return m.group(0) if m else None
        if component == "gsd":
            p = HOME / ".config/opencode/get-shit-done/VERSION"
            if p.exists():
                return p.read_text(encoding="utf-8").strip().lstrip("v")
            return None
        if component == "openspec":
            proc = subprocess.run(
                ["openspec", "--version"], capture_output=True, text=True, timeout=10
            )
            m = _VERSION_RE.search(proc.stdout)
            return m.group(0) if m else None
        if component == "claude-mem":
            # npm-published claude-mem doesn't expose --version consistently.
            # Probe known global install paths.
            for prefix in (
                HOME / ".bun/install/cache/claude-mem",
                HOME / ".bun/install/cache/@npm@claude-mem-*" / "node_modules/claude-mem",
            ):
                pkg = Path(prefix) / "package.json"
                if pkg.exists():
                    return json.loads(pkg.read_text()).get("version")
            return None
        if component == "ecc":
            # npm-published ecc-universal package version (v1.x → "ecc@1.x",
            # v2.x → "ecc-universal"). Walk npm root and find package.json.
            npm_roots = []
            try:
                roots = subprocess.run(
                    ["npm", "root", "-g"], capture_output=True, text=True, timeout=10
                ).stdout.strip()
                if roots:
                    npm_roots.append(Path(roots))
            except Exception:
                pass
            npm_roots.extend([
                HOME / ".bun/install/global/node_modules",
                HOME / ".version-fox/cache/nodejs" / "*" / "lib/node_modules",
            ])
            for r in npm_roots:
                for name in ("ecc-universal", "ecc"):
                    pkg = r / name / "package.json"
                    if pkg.exists():
                        return json.loads(pkg.read_text()).get("version")
            return None
        if component == "superpowers-claude":
            # Walk the claude plugins cache and pick the highest-versioned
            # superpowers package.json across marketplaces.
            best = None
            for cache_root in (
                HOME / ".claude/plugins/cache",
            ):
                if not cache_root.exists():
                    continue
                for pkg in cache_root.glob("*/superpowers/*/package.json"):
                    try:
                        data = json.loads(pkg.read_text())
                    except Exception:
                        continue
                    if data.get("name") != "superpowers":
                        continue
                    ver = data.get("version", "")
                    if best is None or _is_older(best, ver):
                        best = ver
            return best
        if component == "caveman":
            # v1.9+ drops no version metadata into ~/.agents/skills/caveman/.
            # Hash comparison against v1.9.1's expected SKILL.md is the cheapest
            # signal; callers may rely on _caveman_v191_marker() helper instead.
            return None
    except Exception:
        pass
    return None


def _live_query_latest(component: str) -> Optional[str]:
    """Best-effort live latest-version probe. Returns None on any failure so
    callers fall back to LATEST_KNOWN. Optional: offline / slow / fragile."""
    try:
        if component == "rtk":
            r = subprocess.run(
                ["curl", "-fsSL", "--max-time", "5",
                 "https://raw.githubusercontent.com/rtk-ai/rtk/master/Cargo.toml"],
                capture_output=True, text=True,
            )
            m = re.search(r'^version\s*=\s*"(\d+\.\d+\.\d+)"', r.stdout, re.MULTILINE)
            return m.group(1) if m else None
        if component == "code-review-graph":
            r = subprocess.run(
                ["uvx", "--from", "code-review-graph", "code-review-graph", "--version"],
                capture_output=True, text=True, timeout=15,
            )
            m = _VERSION_RE.search(r.stdout)
            return m.group(0) if m else None
        if component == "openspec":
            r = subprocess.run(
                ["npm", "view", "@fission-ai/openspec", "version"],
                capture_output=True, text=True, timeout=10,
            )
            v = r.stdout.strip().strip("'\"")
            return v if _VERSION_RE.match(v) else None
        if component == "claude-mem":
            r = subprocess.run(
                ["npm", "view", "claude-mem", "version"],
                capture_output=True, text=True, timeout=10,
            )
            v = r.stdout.strip().strip("'\"")
            return v if _VERSION_RE.match(v) else None
        if component == "ecc":
            r = subprocess.run(
                ["npm", "view", "ecc-universal", "version"],
                capture_output=True, text=True, timeout=10,
            )
            v = r.stdout.strip().strip("'\"")
            return v if _VERSION_RE.match(v) else None
        if component == "superpowers-claude":
            r = subprocess.run(
                ["curl", "-fsSL", "--max-time", "5",
                 "https://raw.githubusercontent.com/obra/superpowers/main/package.json"],
                capture_output=True, text=True,
            )
            data = json.loads(r.stdout)
            return data.get("version")
        if component == "gsd":
            r = subprocess.run(
                ["curl", "-fsSL", "--max-time", "5",
                 "https://raw.githubusercontent.com/gsd-build/get-shit-done/main/package.json"],
                capture_output=True, text=True,
            )
            data = json.loads(r.stdout)
            return data.get("version")
        # caveman: no fast live probe; rely on LATEST_KNOWN (v1.9.1 tag).
    except Exception:
        pass
    return None


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
        return self.status in {STATUS_MISSING, STATUS_UNCONFIGURED, STATUS_BLOCKED, STATUS_MANUAL_UPGRADE, STATUS_OUTDATED}

    @property
    def can_auto_repair(self) -> bool:
        # OUTDATED is auto-repairable: repair_xxx() commands all use the
        # upstream-published installer (latest-installer strategy), so re-running
        # them when drift is detected pulls whatever is current upstream.
        return self.status in {STATUS_MISSING, STATUS_UNCONFIGURED, STATUS_OUTDATED}


def _apply_drift(component: str, result: "CheckResult") -> "CheckResult":
    """If status is OK and version drift is detectable, downgrade to OUTDATED
    so `/tool-update --full` will auto-repair. Pass-through otherwise."""
    if result.status != STATUS_OK:
        return result
    local = _detect_local_version(component)
    if not local:
        return result
    latest = _live_query_latest(component) or LATEST_KNOWN.get(component)
    if not latest:
        return result
    if not _is_older(local, latest):
        return result
    return CheckResult(
        result.name,
        STATUS_OUTDATED,
        f"installed {local}; latest {latest}",
        repair=manifest_repair_hint(component, result.target, ""),
        target=result.target,
    )


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
        # Check via opencode plugin command first (OpenCode 1.15+).
        # IMPORTANT: opencode plugin superpowers resolves to the npm placeholder
        # `superpowers@0.0.2`, NOT obra's package; the github source spec is
        # the only way to get the real plugin.
        result = runner.run(["opencode", "plugin", "superpowers@github:obra/superpowers"])
        plugin_ok = "installed" in result.stdout.lower() or "already" in result.stdout.lower()
        # Check command wrappers exist (superpowers:brainstorm, etc.)
        cmd_dir = HOME / ".config/opencode" / "commands"
        wrappers = ["superpowers:brainstorm.md", "superpowers:tdd.md", "superpowers:debug.md", "superpowers:superpowers.md"]
        has_wrappers = all((cmd_dir / w).exists() for w in wrappers)
        if plugin_ok and has_wrappers:
            return CheckResult("superpowers", STATUS_OK, "opencode plugin + /superpowers:* wrappers", target=target)
        if plugin_ok:
            return CheckResult("superpowers", STATUS_OK, "opencode plugin superpowers@github:obra/superpowers", target=target)
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
        return CheckResult("superpowers", STATUS_UNCONFIGURED, "OpenCode plugin missing", manifest_repair_hint("superpowers", target, "opencode plugin 'superpowers@github:obra/superpowers' -g"), target)

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
    # GSD v1.50 dropped the trailing 's' on the install dir upstream; we have
    # to look in both 'commands/' (legacy/v1.41) and 'command/' (v1.50).
    legacy_command_dir = HOME / ".config/opencode/command"
    skill_dirs = paths["gsd_skills"]
    candidate_dirs = [d for d in (command_dir, legacy_command_dir) if d.exists()]
    has_gsd = False
    for d in candidate_dirs:
        if any(d.glob("gsd-*.md")):
            has_gsd = True
            break
    if not has_gsd:
        has_gsd = any(
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
    # v1.50+ canary must come from upstream main via git clone; npx pulls
    # the deprecated 1.42.3 line. Report the git-clone path as the
    # authoritative repair hint.
    return CheckResult(
        "gsd", STATUS_MISSING, f"GSD files missing ({scope})",
        manifest_repair_hint(
            "gsd", target,
            f"git clone --depth=1 https://github.com/gsd-build/get-shit-done && cd get-shit-done && npm install --no-audit --no-fund --loglevel=error && node bin/install.js {flag} {scope_flag}",
        ),
        target,
    )


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


def _ecc_marker_has_content(marker: Path) -> bool:
    """An empty marker dir is leftover from a half-install and should not
    satisfy `has_marker`. Only treat the marker as evidence when it contains
    real ECC artifacts (commands/, hooks/, rules/, etc.)."""
    if not marker.exists() or not marker.is_dir():
        return False
    return any(child.name in {"commands", "hooks", "rules", "skills", "agents", "agents-md"} for child in marker.iterdir())


_ECC_OPENCODE_DISTINCTIVE_COMMANDS = frozenset({
    "multi-plan.md", "prp-plan.md", "build-fix.md", "feature-dev.md",
    "context-budget.md", "cpp-build.md", "go-build.md", "rust-build.md",
    "gradle-build.md", "kotlin-build.md", "flutter-build.md", "aside.md",
    "claw.md", "code-review.md", "review-pr.md", "verify.md",
})


def _ecc_opencode_v2_installed() -> bool:
    """ECC v2 `--target opencode` install drops a curated set of command files
    directly into ~/.config/opencode/commands/ (and matching agents/hooks).
    Detect by counting distinctive ECC command files OR symlinks pointing
    into the ECC plugin cache; tolerates overlap with other tool plugins
    that may also write the same command names. Threshold 4+."""
    cmd_dir = HOME / ".config/opencode" / "commands"
    if not cmd_dir.is_dir():
        return False
    present = {p.name for p in cmd_dir.iterdir()}
    hits = len(present & _ECC_OPENCODE_DISTINCTIVE_COMMANDS)
    return hits >= 4


def check_ecc(target: str, runner: CommandRunner, scope: str) -> CheckResult:
    if scope == "local":
        return CheckResult("ecc", STATUS_BLOCKED, "local scope not supported", "use --scope global or skip ECC for project-local installs", target)
    if target == "opencode":
        marker_dir = HOME / ".config/opencode/ecc"
        # ECC v2 layout: no dedicated marker dir; install drops files into
        # ~/.config/opencode/{commands,agents,hooks}/. Detect via distinctive
        # command files rather than relying on the v1 marker dir.
        v2_installed = _ecc_opencode_v2_installed()
        legacy_marker = _ecc_marker_has_content(marker_dir)
        sentinel = HOME / ".config/opencode/commands/plan.md"
        has_marker = v2_installed or legacy_marker or sentinel.exists()
        cmd_dir = HOME / ".config/opencode" / "commands"
        has_symlinks = _ecc_commands_linked(cmd_dir)
        if has_marker and has_symlinks:
            return CheckResult("ecc", STATUS_OK, "installed + commands linked", target=target)
        if v2_installed:
            return CheckResult("ecc", STATUS_OK, "ECC v2 commands installed in ~/.config/opencode/commands/", target=target)
        if has_marker and not has_symlinks:
            return CheckResult("ecc", STATUS_UNCONFIGURED, "ECC installed but commands not linked", "link ECC commands to opencode commands dir", target)
        if has_symlinks:
            return CheckResult("ecc", STATUS_OK, "commands linked", target=target)
        if _ecc_cmd_dir():
            return CheckResult("ecc", STATUS_UNCONFIGURED, "ECC found on disk but not linked for OpenCode", "link ECC commands to opencode commands dir", target)
        return CheckResult("ecc", STATUS_MISSING, "OpenCode ECC not installed", manifest_repair_hint("ecc", target, "git clone https://github.com/affaan-m/everything-claude-code ~/.cache/engineer-shovel/ecc && bash ~/.cache/engineer-shovel/ecc/install.sh"), target)

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
        # v6 prefers the obra marketplace; claude-plugins-official fallback
        # yields v5 when the obra marketplace is unreachable.
        runner.run([
            "bash", "-c",
            "set +e; "
            "claude plugin marketplace add https://github.com/obra/superpowers --scope user >/dev/null 2>&1; "
            "claude plugin install superpowers@superpowers-dev --scope user && exit 0; "
            "claude plugin install superpowers@claude-plugins-official; exit $?",
        ])
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
    """GSD v1.50+ canary comes from upstream main via git clone + node bin/install.js.
    The npm `get-shit-done-cc` package is deprecated; `npx @latest` would install
    v1.42.3 + deprecation warning instead of the canary build. Upstream's install.js
    additionally requires that the local `sdk/dist` artifact is already built (run
    `cd sdk && npm install && npm run build`); we mirror that explicitly."""
    scope_flag = "--local" if scope == "local" else "--global"
    if set(targets) == {"opencode", "claude"}:
        runtime_flag = "--all"
    elif targets == ["opencode"]:
        runtime_flag = "--opencode"
    else:
        runtime_flag = "--claude"
    runner.run([
        "bash", "-c",
        "set -e; tmp=\"$(mktemp -d)\"; "
        "git clone --depth=1 --no-tags --filter=blob:none https://github.com/gsd-build/get-shit-done \"$tmp/gsd\"; "
        "(cd \"$tmp/gsd\" && npm install --no-audit --no-fund --loglevel=error); "
        "(cd \"$tmp/gsd/sdk\" && npm install --no-audit --no-fund --loglevel=error && npm run build); "
        "node \"$tmp/gsd/bin/install.js\" " + runtime_flag + " " + scope_flag + "; "
        "rm -rf \"$tmp\"",
    ])


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
        # ECC v2+ ships as the npm-published `ecc-universal` package, which
        # exposes an `ecc-install` bin pointing at scripts/install-apply.js.
        # Pre-built artifacts avoid the upstream `npm run build:opencode`
        # step. The git clone path is kept as fallback; it requires that
        # extra build step on the caller side.
        marker = HOME / ".config/opencode/ecc"
        if not marker.exists() and not _ecc_cmd_dir():
            runner.run([
                "bash", "-c",
                "set -e; "
                "npm install -g ecc-universal@latest 2>&1 | tail -5; "
                "ecc-install --target opencode --profile opencode",
            ])
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
    # Normalize: targets is always a list of strings
    if isinstance(targets, str):
        targets = expand_targets(targets)
    checks: list[CheckResult] = []
    for comp in COMPONENTS:
        if comp.needs_target:
            for target in targets:
                result = comp.check(*_component_args(comp, target, runner, scope))
                checks.append(_apply_drift(comp.name, result))
        else:
            result = comp.check(*_component_args(comp, "", runner, scope))
            checks.append(_apply_drift(comp.name, result))
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
