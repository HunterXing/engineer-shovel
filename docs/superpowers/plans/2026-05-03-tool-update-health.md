# Tool Update Health Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `/tool-update --check/--full` verify and repair Engineer Shovel files plus base dependencies and Full-mode components.

**Architecture:** Keep `scripts/sync.py` focused on Engineer Shovel file synchronization, and add `scripts/health.py` for component health detection and repair. `scripts/sync.py` orchestrates health checks after file checks so `/tool-update` still has one entrypoint.

**Tech Stack:** Python 3 stdlib, pytest, existing shell installer conventions, existing Markdown command docs.

---

## File Structure

- Create `scripts/health.py`: pure-ish health checker with injectable command runner, path checks, target-aware report, and optional repair actions.
- Modify `scripts/sync.py`: add `--skip-health`, invoke `health.py` for `check` and `sync`, and map `sync` to health repair unless `--dry-run` is set.
- Modify `commands/tool-update.md`: document file sync plus component health behavior and safety rules.
- Modify `tests/test_validation_scripts.py`: add unit tests for health target expansion, missing executable detection, project stack detection, and check-mode no-write behavior.
- Keep `install.sh` unchanged for this pass; health repair may reuse the same official commands but should not duplicate the full installer internals more than needed.

## Task 1: Add Health Checker Core

**Files:**
- Create: `scripts/health.py`
- Test: `tests/test_validation_scripts.py`

- [ ] **Step 1: Write failing tests for target expansion and missing executables**

Add this to `tests/test_validation_scripts.py`:

```python
def test_health_expands_both_targets():
    module = load_script("health.py")

    assert module.expand_targets("both") == ["opencode", "claude"]
    assert module.expand_targets("opencode") == ["opencode"]
    assert module.expand_targets("claude") == ["claude"]


def test_health_reports_missing_base_executable(tmp_path, monkeypatch):
    module = load_script("health.py")

    monkeypatch.setattr(module, "which", lambda name: None)
    checks = module.check_base_dependencies(["opencode"], runner=module.CommandRunner(dry_run=True))
    by_name = {check.name: check for check in checks}

    assert by_name["git"].status == "missing"
    assert by_name["python3"].status == "missing"
    assert by_name["opencode"].status == "missing"
    assert "claude" not in by_name
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_validation_scripts.py::test_health_expands_both_targets tests/test_validation_scripts.py::test_health_reports_missing_base_executable -v`

Expected: FAIL because `scripts/health.py` does not exist.

- [ ] **Step 3: Implement minimal health checker data model and base dependency checks**

Create `scripts/health.py`:

```python
#!/usr/bin/env python3
"""Check and repair Engineer Shovel supporting components."""

from __future__ import annotations

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
        proc = subprocess.run(command, text=True, capture_output=True, check=False)
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_validation_scripts.py::test_health_expands_both_targets tests/test_validation_scripts.py::test_health_reports_missing_base_executable -v`

Expected: PASS.

## Task 2: Add Component Detection

**Files:**
- Modify: `scripts/health.py`
- Test: `tests/test_validation_scripts.py`

- [ ] **Step 1: Write failing tests for stack detection and component states**

Add tests:

```python
def test_health_detects_project_language_markers(tmp_path, monkeypatch):
    module = load_script("health.py")
    (tmp_path / "package.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.detect_project_rule_packs() == ["typescript", "python"]


def test_health_code_review_graph_missing_when_binary_absent(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: None)

    result = module.check_code_review_graph(module.CommandRunner(dry_run=True))

    assert result.name == "code-review-graph"
    assert result.status == "missing"
    assert "pipx install code-review-graph" in result.repair
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_validation_scripts.py::test_health_detects_project_language_markers tests/test_validation_scripts.py::test_health_code_review_graph_missing_when_binary_absent -v`

Expected: FAIL because functions are missing.

- [ ] **Step 3: Implement project marker and component check functions**

Append to `scripts/health.py`:

```python
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


def check_gsd(target: str) -> CheckResult:
    command_dir = HOME / ".config/opencode/commands" if target == "opencode" else HOME / ".claude/commands"
    skill_dir = HOME / ".config/opencode/skills" if target == "opencode" else HOME / ".claude/skills"
    has_gsd = any(command_dir.glob("gsd-*.md")) if command_dir.exists() else False
    has_gsd = has_gsd or (skill_dir.exists() and any(skill_dir.glob("gsd-*/SKILL.md")))
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
    checks = [check_code_review_graph(runner), check_rtk(runner)]
    for target in targets:
        checks.extend([
            check_superpowers(target, runner),
            check_caveman(target, runner),
            check_gsd(target),
            check_ecc(target, runner),
        ])
    return checks
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_validation_scripts.py::test_health_detects_project_language_markers tests/test_validation_scripts.py::test_health_code_review_graph_missing_when_binary_absent -v`

Expected: PASS.

## Task 3: Add Repair Actions and CLI

**Files:**
- Modify: `scripts/health.py`
- Test: `tests/test_validation_scripts.py`

- [ ] **Step 1: Write failing tests for repair command selection**

Add tests:

```python
def test_health_repair_code_review_graph_uses_official_commands(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: "/bin/" + name if name in {"pipx", "code-review-graph"} else None)
    runner = module.CommandRunner(dry_run=True)

    module.repair_code_review_graph(runner, ["opencode", "claude"])

    assert ["pipx", "install", "code-review-graph"] in runner.commands
    assert ["code-review-graph", "install"] in runner.commands
    assert ["code-review-graph", "build"] in runner.commands


def test_health_repair_gsd_uses_all_for_both_targets():
    module = load_script("health.py")
    runner = module.CommandRunner(dry_run=True)

    module.repair_gsd(runner, ["opencode", "claude"])

    assert ["npx", "-y", "get-shit-done-cc@latest", "--all", "--global"] in runner.commands
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_validation_scripts.py::test_health_repair_code_review_graph_uses_official_commands tests/test_validation_scripts.py::test_health_repair_gsd_uses_all_for_both_targets -v`

Expected: FAIL because repair functions are missing.

- [ ] **Step 3: Implement repair functions and CLI main**

Append to `scripts/health.py`:

```python
def repair_code_review_graph(runner: CommandRunner, targets: list[str]) -> None:
    del targets
    if which("pipx"):
        runner.run(["pipx", "install", "code-review-graph"])
    else:
        runner.run(["python3", "-m", "pip", "install", "--user", "code-review-graph"])
    runner.run(["code-review-graph", "install"])
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
    if "gsd" in names:
        repair_gsd(runner, targets)
    if "caveman" in names:
        repair_caveman(runner, targets)
    for target in targets:
        if any(check.name == "superpowers" and check.target == target and check.needs_repair for check in checks):
            repair_superpowers(runner, target)
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
    runner = CommandRunner(dry_run=dry_run or command == "check")
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_validation_scripts.py::test_health_repair_code_review_graph_uses_official_commands tests/test_validation_scripts.py::test_health_repair_gsd_uses_all_for_both_targets -v`

Expected: PASS.

## Task 4: Wire Health Into Sync and Command Docs

**Files:**
- Modify: `scripts/sync.py`
- Modify: `commands/tool-update.md`
- Test: `tests/test_validation_scripts.py`

- [ ] **Step 1: Write failing tests for CLI docs and sync integration marker**

Add tests:

```python
def test_tool_update_mentions_component_health_checks():
    text = (ROOT / "commands" / "tool-update.md").read_text(encoding="utf-8")

    assert "component health" in text.lower()
    assert "code-review-graph" in text
    assert "superpowers" in text
    assert "MCP" in text


def test_sync_script_invokes_health_script():
    text = (ROOT / "scripts" / "sync.py").read_text(encoding="utf-8")

    assert "health.py" in text
    assert "--skip-health" in text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_validation_scripts.py::test_tool_update_mentions_component_health_checks tests/test_validation_scripts.py::test_sync_script_invokes_health_script -v`

Expected: FAIL until files are updated.

- [ ] **Step 3: Update `scripts/sync.py`**

Patch imports and helper:

```python
import subprocess
```

Add before `main()`:

```python
def run_health(command: str, target: str, dry_run: bool = False) -> int:
    health_command = "check" if command == "check" else "repair"
    args = [sys.executable, str(ROOT / "scripts" / "health.py"), health_command, "--target", target]
    if dry_run:
        args.append("--dry-run")
    proc = subprocess.run(args, text=True, check=False)
    return proc.returncode
```

Add parser argument:

```python
    parser.add_argument(
        "--skip-health",
        action="store_true",
        help="Only sync Engineer Shovel files; skip external component health checks"
    )
```

In `check` branch before final status:

```python
        health_rc = 0 if args.skip_health else run_health("check", args.target, dry_run=True)
        if health_rc != 0:
            all_ok = False
```

In `sync` branch before return:

```python
        if not args.skip_health:
            health_rc = run_health("sync", args.target, dry_run=args.dry_run)
            if health_rc != 0:
                return health_rc
```

- [ ] **Step 4: Update `/tool-update` docs**

Replace the command body with concise behavior:

```markdown
Synchronize Engineer Shovel files and verify supporting component health.

## Modes

- `--check` or default: Compare installed Engineer Shovel files and check base dependencies plus Full-mode components. Read-only.
- `--full`: Update Engineer Shovel files, then install/configure missing low-risk components using official installers.

## Component Health

Checks base tools: `git`, `python3`, `pipx`, `node`, `npx`, plus selected runtimes (`opencode`, `claude`).

Checks Full-mode components: `code-review-graph`, GSD, `superpowers`, Caveman, RTK, ECC.

MCP policy:
- `code-review-graph install` may configure MCP/rules because upstream explicitly supports this.
- Superpowers has no separate MCP auto-configuration step; it is configured as a plugin/skills provider.
- ECC bundled MCPs are not auto-enabled by default because they may require credentials or duplicate user servers.

Safety:
- Does not start background watch/daemon processes.
- Does not enable telemetry explicitly.
- Does not delete user config.
- Backs up JSON config before editing.
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_validation_scripts.py::test_tool_update_mentions_component_health_checks tests/test_validation_scripts.py::test_sync_script_invokes_health_script -v`

Expected: PASS.

## Task 5: Full Verification

**Files:**
- All touched files

- [ ] **Step 1: Run focused test file**

Run: `pytest tests/test_validation_scripts.py -v`

Expected: PASS all tests.

- [ ] **Step 2: Run check mode without repair side effects**

Run: `python3 scripts/health.py check --target both --dry-run`

Expected: reports health status and exits non-zero if components are missing; no installs run.

- [ ] **Step 3: Run sync check with health enabled**

Run: `python3 scripts/sync.py check --target both --scope global`

Expected: file status plus health status; exits non-zero if any component needs repair.

- [ ] **Step 4: Inspect diff**

Run: `git diff -- scripts/health.py scripts/sync.py commands/tool-update.md tests/test_validation_scripts.py docs/superpowers/specs/2026-05-03-tool-update-health-design.md docs/superpowers/plans/2026-05-03-tool-update-health.md`

Expected: only planned changes are present.
