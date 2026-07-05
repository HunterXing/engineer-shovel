from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = str(ROOT / "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


def load_script(name: str):
    path = ROOT / "scripts" / name
    module_name = name.replace("-", "_").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_command(path: Path, *, include_required: bool = True) -> None:
    if include_required:
        path.write_text(
            """---
description: Test command
argument-hint: [--fast]
cost-profile: low
risk-level: low
recommended-mode: --fast
allowed-tools: [Read]
escalates-to: []
depends-on: []
when-to-use: Use this fixture for command schema validation tests.
---

# /tool-test
""",
            encoding="utf-8",
        )
    else:
        path.write_text(
            """---
description: Broken command
cost-profile: low
---

# /tool-broken
""",
            encoding="utf-8",
        )


def test_validate_command_schema_accepts_valid_frontmatter(tmp_path, monkeypatch):
    module = load_script("validate.py")
    command_dir = tmp_path / "commands"
    command_dir.mkdir()
    write_command(command_dir / "tool-test.md")
    monkeypatch.setattr(module, "COMMAND_DIR", command_dir)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.validate_schema() == 0


def test_validate_command_schema_rejects_missing_fields(tmp_path, monkeypatch):
    module = load_script("validate.py")
    command_dir = tmp_path / "commands"
    command_dir.mkdir()
    write_command(command_dir / "tool-broken.md", include_required=False)
    monkeypatch.setattr(module, "COMMAND_DIR", command_dir)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.validate_schema() == 1


def test_validate_markdown_links_accepts_existing_local_link(tmp_path, monkeypatch):
    module = load_script("validate.py")
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text("[Doc](docs/page.md)\n", encoding="utf-8")
    (tmp_path / "docs" / "page.md").write_text("# Page\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.validate_links() == 0


def test_validate_markdown_links_rejects_missing_local_link(tmp_path, monkeypatch):
    module = load_script("validate.py")
    (tmp_path / "README.md").write_text("[Missing](docs/missing.md)\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.validate_links() == 1


def test_token_benchmark_reports_static_and_unknown_sources(capsys):
    module = load_script("token-benchmark.py")

    assert module.main() == 0
    report = json.loads(capsys.readouterr().out)
    assert report["measurement_kind"] == "static_proxy"
    assert report["measurement_sources"]["static_markdown"]["kind"] == "static_proxy"
    assert report["measurement_sources"]["caveman_session"]["status"] == "unknown"
    assert report["measurement_sources"]["rtk_project"]["status"] == "unknown"
    assert report["caveman_session"]["measured_tokens_saved"] is None
    assert report["rtk_project"]["measured_tokens_saved"] is None


def test_command_set_stays_at_eleven_after_alias_addition():
    commands = sorted(path.stem for path in (ROOT / "commands").glob("tool-*.md"))

    assert len(commands) == 11
    assert "tool-graph" in commands
    assert "tool-alias" in commands
    assert "tool-brainstorm" not in commands
    assert "tool-blueprint" not in commands


def test_readmes_list_upstream_tool_versions():
    expected = {
        "ECC": "v2.0.0",
        "GSD": "v1.50.0-canary.0",
        "superpowers": "v6.1.1",
        "code-review-graph": "v2.3.6",
        "Caveman": "v1.9.1",
        "RTK": "v0.43.0",
        "OpenSpec": "@fission-ai/openspec@latest",
        "claude-mem": "v13.10.0",
    }

    for readme_name in ("README.md", "README_zh.md"):
        text = (ROOT / readme_name).read_text(encoding="utf-8")
        for tool, version in expected.items():
            assert tool in text, f"{readme_name} missing {tool}"
            assert version in text, f"{readme_name} missing {version}"


def test_readme_clarifies_native_and_external_capabilities():
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Native Engineer Shovel" in text
    assert "optional external tools" in text
    assert "--with-graph-build" in text


def test_installer_dry_run_mentions_all_full_mode_integrations():
    install_text = (ROOT / "install.sh").read_text(encoding="utf-8")

    for marker in (
        "install_ecc",
        "install_gsd",
        "install_superpowers",
        "install_caveman_for_target",
        "install_rtk",
        "install_openspec",
        "install_code_review_graph",
        "rtk init",
        "code-review-graph install",
        "code-review-graph build",
        "@fission-ai/openspec",
    ):
        assert marker in install_text


def test_installer_uses_all_for_gsd_dual_target():
    install_text = (ROOT / "install.sh").read_text(encoding="utf-8")

    assert 'gsd_target="--all"' in install_text
    assert 'gsd_target="--both"' not in install_text


def test_graph_build_is_explicit_installer_option():
    install_text = (ROOT / "install.sh").read_text(encoding="utf-8")

    assert "WITH_GRAPH_BUILD" in install_text
    assert "--with-graph-build" in install_text
    assert "Skipping code-review-graph build; pass --with-graph-build" in install_text


def test_feature_workflow_requires_branch_gate():
    text = (ROOT / "commands" / "tool-feat.md").read_text(encoding="utf-8")

    assert "/tool-branch create" in text
    assert "before editing" in text.lower()


def test_readme_header_has_language_links_and_badges_without_command_wall():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    header = text.split("---", 1)[0]

    for label in ("English", "简体中文", "日本語", "한국어"):
        assert label in header
    for badge in ("GitHub stars", "GitHub forks", "License", "Commands", "OpenCode"):
        assert badge in header
    assert "/tool-quick" not in header
    assert "/tool-update" not in header


def test_localized_readme_files_exist_for_header_links():
    for name in ("README_zh.md", "README.ja-JP.md", "README.ko-KR.md"):
        assert (ROOT / name).exists()


def test_health_expands_both_targets():
    module = load_script("health.py")

    assert module.expand_targets("both") == ["opencode", "claude"]
    assert module.expand_targets("opencode") == ["opencode"]
    assert module.expand_targets("claude") == ["claude"]


def test_health_reports_missing_base_executable(monkeypatch):
    module = load_script("health.py")

    monkeypatch.setattr(module, "which", lambda name: None)
    checks = module.check_base_dependencies(["opencode"], runner=module.CommandRunner(dry_run=True))
    by_name = {check.name: check for check in checks}

    assert by_name["git"].status == "missing"
    assert by_name["python3"].status == "missing"
    assert by_name["opencode"].status == "missing"
    assert "claude" not in by_name


def test_health_detects_project_language_markers(tmp_path, monkeypatch):
    module = load_script("health.py")
    (tmp_path / "package.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.detect_project_rule_packs() == ["typescript", "python"]


def test_health_detects_opencode_gsd_agent_skill_marker(tmp_path, monkeypatch):
    module = load_script("health.py")
    import paths as p
    monkeypatch.setattr(module, "HOME", tmp_path)
    monkeypatch.setattr(p, "HOME", tmp_path)
    marker = tmp_path / ".agents" / "skills" / "gsd-core" / "SKILL.md"
    marker.parent.mkdir(parents=True)
    marker.write_text("# GSD\n", encoding="utf-8")

    result = module.check_gsd("opencode", "global")
    assert result.status == module.STATUS_OK


def test_health_detects_local_gsd_command_marker(tmp_path, monkeypatch):
    module = load_script("health.py")
    import paths as p
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(p, "ROOT", tmp_path)
    monkeypatch.setattr(p, "HOME", tmp_path)
    marker = tmp_path / ".opencode" / "commands" / "gsd-test.md"
    marker.parent.mkdir(parents=True)
    marker.write_text("# GSD\n", encoding="utf-8")

    result = module.check_gsd("opencode", "local")
    assert result.status == module.STATUS_OK


def test_health_code_review_graph_missing_when_binary_absent(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: None)

    result = module.check_code_review_graph(module.CommandRunner(dry_run=True), "global")

    assert result.name == "code-review-graph"
    assert result.status == "missing"
    assert "pipx install code-review-graph" in result.repair


def test_health_openspec_missing_when_binary_absent(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: None)

    result = module.check_openspec()

    assert result.name == "openspec"
    assert result.status == "missing"
    assert "@fission-ai/openspec" in result.repair


def test_health_repair_code_review_graph_uses_official_commands(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: "/bin/" + name if name in {"pipx", "code-review-graph"} else None)
    runner = module.CommandRunner(dry_run=True)

    module.repair_code_review_graph(runner, ["opencode", "claude"], "global")

    assert any("write_mcp_config" in str(c) for c in runner.commands)
    assert ["code-review-graph", "install", "--platform", "claude-code"] in runner.commands
    assert ["code-review-graph", "build"] in runner.commands


def test_health_repair_code_review_graph_installs_when_missing(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: "/bin/" + name if name == "pipx" else None)
    runner = module.CommandRunner(dry_run=True)

    module.repair_code_review_graph(runner, ["opencode"], "global")

    assert ["pipx", "install", "code-review-graph"] in runner.commands
    assert any("write_mcp_config" in str(c) for c in runner.commands)
    assert ["code-review-graph", "build"] in runner.commands


def test_health_repair_gsd_uses_all_for_both_targets():
    module = load_script("health.py")
    runner = module.CommandRunner(dry_run=True)

    module.repair_gsd(runner, ["opencode", "claude"], "global")

    # v1.50+ canary install path: git clone + npm install + npm run build on
    # `sdk` + node bin/install.js. The `get-shit-done-cc@latest` npx form is
    # deprecated and would only yield v1.42.3.
    bash_cmds = [c[2] for c in runner.commands if c and len(c) >= 3 and c[0] == "bash" and c[1] == "-c"]
    assert any("git clone" in cmd and "--all --global" in cmd for cmd in bash_cmds)
    assert any("--all --global" in cmd and "install.js" in cmd for cmd in bash_cmds)
    assert any("sdk" in cmd and "npm run build" in cmd for cmd in bash_cmds)


def test_health_repair_gsd_uses_local_scope_flag():
    module = load_script("health.py")
    runner = module.CommandRunner(dry_run=True)

    module.repair_gsd(runner, ["opencode"], "local")

    bash_cmds = [c[2] for c in runner.commands if c and len(c) >= 3 and c[0] == "bash" and c[1] == "-c"]
    assert any("git clone" in cmd and "--opencode --local" in cmd for cmd in bash_cmds)
    assert any("--opencode --local" in cmd and "install.js" in cmd for cmd in bash_cmds)
    assert any("sdk" in cmd and "npm run build" in cmd for cmd in bash_cmds)


def test_health_repair_claude_mem_splits_argv():
    module = load_script("health.py")
    runner = module.CommandRunner(dry_run=True)

    module.repair_claude_mem(runner, ["opencode", "claude"])

    assert ["npx", "-y", "claude-mem", "install", "--ide", "opencode"] in runner.commands
    assert ["npx", "-y", "claude-mem", "install", "--ide", "claude"] in runner.commands


def test_health_repair_caveman_uses_claude_flag():
    module = load_script("health.py")
    runner = module.CommandRunner(dry_run=True)

    module.repair_caveman(runner, ["claude"])

    assert len(runner.commands) == 1
    cmd = runner.commands[0]
    assert cmd[0] == "bash"
    assert cmd[1] == "-lc"
    assert "--only claude" in cmd[2]
    assert "JuliusBrussee/caveman" in cmd[2]


def test_health_check_claude_mem_uses_runner(monkeypatch):
    module = load_script("health.py")
    calls = []

    def fake_exec(command):
        calls.append(command)
        return module.CommandResult(0, "claude-mem\n")

    runner = module.CommandRunner(executor=fake_exec)
    result = module.check_claude_mem("claude", runner)

    assert calls == [["claude", "plugin", "list"]]
    assert result.status == module.STATUS_OK


def test_tool_update_mentions_component_health_checks():
    text = (ROOT / "commands" / "tool-update.md").read_text(encoding="utf-8")

    assert "component health" in text.lower()
    assert "code-review-graph" in text
    assert "superpowers" in text
    assert "MCP" in text
    assert "--scope global|local" in text
    assert "read-only health probes" in text


def test_product_shape_docs_keep_command_boundaries_clear():
    research = (ROOT / "commands" / "tool-research.md").read_text(encoding="utf-8")
    mode_routing = (ROOT / "docs" / "mode-routing.md").read_text(encoding="utf-8")
    tool_graph = (ROOT / "commands" / "tool-graph.md").read_text(encoding="utf-8").lower()
    tool_update = (ROOT / "commands" / "tool-update.md").read_text(encoding="utf-8")

    assert "special mode axis" in research
    assert "--quick" in research
    assert "--web" in research
    assert "tool-research" in mode_routing
    assert "--quick / --web / --deep" in mode_routing
    assert "diagnostic" in tool_graph
    assert "Single user-facing entry point" in tool_update


def test_sync_script_invokes_health_script():
    text = (ROOT / "scripts" / "sync.py").read_text(encoding="utf-8")

    assert "health.py" in text
    assert "--skip-health" in text


def test_sync_run_health_passes_scope(monkeypatch):
    module = load_script("sync.py")
    calls = []

    class Proc:
        returncode = 0

    def fake_run(args, text, check=False):
        calls.append(args)
        return Proc()

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module.run_health("check", "both", "local", dry_run=True) == 0
    assert calls == [[
        module.sys.executable,
        str(module.ROOT / "scripts" / "health.py"),
        "check",
        "--target",
        "both",
        "--scope",
        "local",
        "--dry-run",
    ]]


def test_sync_main_sync_dry_run_compares_each_target_and_file_type(monkeypatch):
    module = load_script("sync.py")
    compare_calls = []
    sync_calls = []

    monkeypatch.setattr(
        module.sys,
        "argv",
        ["sync.py", "sync", "--target", "both", "--scope", "local", "--dry-run", "--skip-fetch", "--skip-health"],
    )
    monkeypatch.setattr(module, "get_installed_files", lambda target, scope, file_type: [f"{target}:{scope}:{file_type}:installed"])
    monkeypatch.setattr(module, "get_repo_files", lambda file_type: [f"{file_type}:repo"])

    def fake_compare(installed, repo):
        compare_calls.append((installed, repo))
        return {"missing": [], "outdated": [], "extra": [], "up_to_date": installed}

    def fake_sync(comparison, target, scope, dry_run):
        sync_calls.append((comparison, target, scope, dry_run))
        return 1

    monkeypatch.setattr(module, "compare_files", fake_compare)
    monkeypatch.setattr(module, "sync_files", fake_sync)

    assert module.main() == 0
    assert len(compare_calls) == 4
    assert len(sync_calls) == 4
    assert {call[1] for call in sync_calls} == {"opencode", "claude"}
    assert {call[2] for call in sync_calls} == {"local"}
    assert all(call[3] is True for call in sync_calls)


def test_sync_main_sync_runs_health_when_not_skipped(monkeypatch):
    module = load_script("sync.py")
    health_calls = []

    monkeypatch.setattr(
        module.sys,
        "argv",
        ["sync.py", "sync", "--target", "opencode", "--scope", "global", "--dry-run", "--skip-fetch"],
    )
    monkeypatch.setattr(module, "get_installed_files", lambda target, scope, file_type: [])
    monkeypatch.setattr(module, "get_repo_files", lambda file_type: [])
    monkeypatch.setattr(module, "compare_files", lambda installed, repo: {"missing": [], "outdated": [], "extra": [], "up_to_date": []})
    monkeypatch.setattr(module, "sync_files", lambda comparison, target, scope, dry_run: 0)
    monkeypatch.setattr(
        module,
        "run_health",
        lambda command, target, scope, dry_run=False: health_calls.append((command, target, scope, dry_run)) or 0,
    )

    assert module.main() == 0
    assert health_calls == [("sync", "opencode", "global", True)]


#
# health.py — remaining check/repair functions
#

def test_health_check_caveman_opencode_marker_found(tmp_path, monkeypatch):
    module = load_script("health.py")
    marker = tmp_path / ".agents" / "skills" / "caveman"
    marker.mkdir(parents=True)
    monkeypatch.setattr(module, "HOME", tmp_path)

    result = module.check_caveman("opencode", module.CommandRunner(dry_run=True))

    assert result.name == "caveman"
    assert result.status == module.STATUS_OK


def test_health_check_caveman_opencode_missing(tmp_path, monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "HOME", tmp_path)

    result = module.check_caveman("opencode", module.CommandRunner(dry_run=True))

    assert result.status == module.STATUS_MISSING


def test_health_check_caveman_claude_installed(monkeypatch):
    module = load_script("health.py")
    runner = module.CommandRunner(
        executor=lambda cmd: module.CommandResult(0, "caveman\n")
    )

    result = module.check_caveman("claude", runner)

    assert result.status == module.STATUS_OK


def test_health_check_caveman_claude_missing(monkeypatch):
    module = load_script("health.py")
    runner = module.CommandRunner(
        executor=lambda cmd: module.CommandResult(0, "")
    )

    result = module.check_caveman("claude", runner)

    assert result.status == module.STATUS_MISSING


def test_health_check_rtk_missing(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: None)

    result = module.check_rtk(module.CommandRunner(dry_run=True))

    assert result.name == "rtk"
    assert result.status == module.STATUS_MISSING
    assert "install.sh" in result.repair


def test_health_check_rtk_found(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: "/usr/local/bin/rtk")

    result = module.check_rtk(module.CommandRunner(dry_run=True))

    assert result.name == "rtk"
    assert result.status == module.STATUS_OK


def test_health_check_superpowers_opencode_plugin_ok(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: "/usr/local/bin/opencode")
    monkeypatch.setattr(module, "HOME", Path("/tmp/test_home_sp_op"))
    runner = module.CommandRunner(
        executor=lambda cmd: module.CommandResult(0, "installed\n")
    )

    result = module.check_superpowers("opencode", runner)

    assert result.name == "superpowers"
    assert result.status == module.STATUS_OK


def test_health_check_superpowers_claude_installed(monkeypatch):
    module = load_script("health.py")
    runner = module.CommandRunner(
        executor=lambda cmd: module.CommandResult(0, "superpowers\n")
    )

    result = module.check_superpowers("claude", runner)

    assert result.name == "superpowers"
    assert result.status == module.STATUS_OK


def test_health_check_ecc_local_blocked():
    module = load_script("health.py")
    runner = module.CommandRunner(dry_run=True)

    result = module.check_ecc("opencode", runner, "local")

    assert result.name == "ecc"
    assert result.status == module.STATUS_BLOCKED


def test_health_check_ecc_opencode_missing(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "HOME", Path("/tmp/test_home_ecc_missing"))
    monkeypatch.setattr(module, "_ecc_cmd_dir", lambda: None)
    runner = module.CommandRunner(dry_run=True)

    result = module.check_ecc("opencode", runner, "global")

    assert result.name == "ecc"
    assert result.status == module.STATUS_MISSING
    assert result.can_auto_repair, "missing ECC for OpenCode must be auto-repairable under latest-installer strategy"


def test_health_repair_openspec(monkeypatch):
    module = load_script("health.py")
    runner = module.CommandRunner(dry_run=True)

    module.repair_openspec(runner, ["opencode", "claude"])

    assert ["npm", "install", "-g", "@fission-ai/openspec@latest"] in runner.commands


def test_health_repair_rtk_missing(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: None)
    runner = module.CommandRunner(dry_run=True)

    module.repair_rtk(runner, ["opencode"])

    assert any("rtk" in str(c) for c in runner.commands)
    assert ["rtk", "init", "-g", "--opencode"] in runner.commands


def test_health_repair_rtk_already_installed(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: "/usr/local/bin/rtk")
    runner = module.CommandRunner(dry_run=True)

    module.repair_rtk(runner, ["claude"])

    assert ["rtk", "init", "-g"] in runner.commands


def test_health_repair_superpowers_opencode(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: "/usr/local/bin/opencode")
    monkeypatch.setattr(module, "HOME", Path("/tmp/test_home_sp_repair"))
    runner = module.CommandRunner(dry_run=True)

    module.repair_superpowers(runner, "opencode")

    assert ["opencode", "plugin", "superpowers", "-g"] in runner.commands


def test_health_repair_superpowers_claude(monkeypatch):
    module = load_script("health.py")
    runner = module.CommandRunner(dry_run=True)

    module.repair_superpowers(runner, "claude")

    # v6 install prefers obra marketplace; claude-plugins-official (v5) is fallback.
    bash_cmd = next(c for c in runner.commands if c and c[0] == "bash")
    rendered = " ".join(bash_cmd)
    assert "obra/superpowers" in rendered
    assert "superpowers-dev" in rendered
    assert "claude-plugins-official" in rendered  # fallback still present


def test_health_check_components_includes_all(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: None)
    runner = module.CommandRunner(dry_run=True)

    checks = module.check_components(["opencode"], runner, "global")
    names = {c.name for c in checks}

    assert "code-review-graph" in names
    assert "rtk" in names
    assert "openspec" in names
    assert "superpowers" in names
    assert "caveman" in names
    assert "claude-mem" in names
    assert "gsd" in names
    assert "ecc" in names


def test_health_command_runner_file_not_found():
    module = load_script("health.py")
    runner = module.CommandRunner()

    result = runner.run(["/nonexistent/binary"])

    assert result.returncode == 127


def test_health_check_result_properties():
    module = load_script("health.py")

    ok = module.CheckResult("test", module.STATUS_OK)
    assert not ok.needs_repair
    assert not ok.can_auto_repair

    missing = module.CheckResult("test", module.STATUS_MISSING)
    assert missing.needs_repair
    assert missing.can_auto_repair

    blocked = module.CheckResult("test", module.STATUS_BLOCKED)
    assert blocked.needs_repair
    assert not blocked.can_auto_repair


#
# sync.py — remaining functions
#

def test_sync_compare_files_all_scenarios(tmp_path):
    module = load_script("sync.py")
    installed_dir = tmp_path / "installed"
    repo_dir = tmp_path / "repo"
    installed_dir.mkdir()
    repo_dir.mkdir()

    (repo_dir / "tool-a.md").write_text("a2", encoding="utf-8")
    (repo_dir / "tool-b.md").write_text("b", encoding="utf-8")
    (repo_dir / "tool-c.md").write_text("c", encoding="utf-8")

    (installed_dir / "tool-a.md").write_text("a1", encoding="utf-8")
    (installed_dir / "tool-b.md").write_text("b", encoding="utf-8")
    (installed_dir / "tool-d.md").write_text("d", encoding="utf-8")

    installed = sorted(installed_dir.glob("tool-*.md"))
    repo = sorted(repo_dir.glob("tool-*.md"))

    result = module.compare_files(installed, repo)

    assert len(result["missing"]) == 1
    assert result["missing"][0].name == "tool-c.md"
    assert len(result["outdated"]) == 1
    assert result["outdated"][0]["installed"].name == "tool-a.md"
    assert len(result["extra"]) == 1
    assert result["extra"][0].name == "tool-d.md"
    assert len(result["up_to_date"]) == 1
    assert result["up_to_date"][0].name == "tool-b.md"


def test_sync_compare_files_empty(tmp_path):
    module = load_script("sync.py")

    result = module.compare_files([], [])

    assert result["missing"] == []
    assert result["outdated"] == []
    assert result["extra"] == []
    assert result["up_to_date"] == []


def test_sync_sync_files_dry_run(tmp_path, capsys):
    module = load_script("sync.py")
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "tool-new.md").write_text("new", encoding="utf-8")
    (repo_dir / "tool-old.md").write_text("old", encoding="utf-8")

    comparison = {
        "missing": [repo_dir / "tool-new.md"],
        "outdated": [{"installed": tmp_path / "tool-old.md", "repo": repo_dir / "tool-old.md"}],
        "extra": [],
        "up_to_date": [],
    }
    monkeypatch = __import__("pytest").MonkeyPatch()

    updated = module.sync_files(comparison, target="opencode", scope="global", dry_run=True)
    captured = capsys.readouterr().out

    assert updated == 2
    assert "DRY-RUN: Would copy" in captured
    assert "DRY-RUN: Would update" in captured


def test_sync_extract_version(tmp_path):
    module = load_script("sync.py")
    skill = tmp_path / "SKILL.md"
    skill.write_text('version: "2.0.0"\n', encoding="utf-8")

    ver = module.extract_version(skill)

    assert ver == "2.0.0"


def test_sync_extract_version_missing(tmp_path):
    module = load_script("sync.py")
    skill = tmp_path / "SKILL.md"

    ver = module.extract_version(skill)

    assert ver is None


def test_sync_get_installed_files_nonexistent(tmp_path):
    module = load_script("sync.py")
    fake_path = tmp_path / "nonexistent"
    monkeypatch = __import__("pytest").MonkeyPatch()
    monkeypatch.setattr(module, "INSTALL_PATHS", {
        "opencode": {
            "global": {
                "skill": fake_path,
                "commands": fake_path / "commands",
            }
        }
    })

    result = module.get_installed_files("opencode", "global", "commands")

    assert result == []


def test_sync_get_repo_files(monkeypatch):
    module = load_script("sync.py")

    result = module.get_repo_files("commands")

    assert len(result) > 0
    assert all(f.suffix == ".md" for f in result)


def test_sync_get_repo_files_skill(monkeypatch):
    module = load_script("sync.py")

    result = module.get_repo_files("skill")

    assert len(result) == 1
    assert "SKILL.md" in result[0].name


#
# inventory.py
#

def test_inventory_reports_structure(capsys):
    module = load_script("inventory.py")

    rc = module.main()
    report = json.loads(capsys.readouterr().out)

    assert rc == 0
    assert "command_count" in report
    assert report["command_count"] == 11
    assert "skill_lines" in report
    assert "install_lines" in report
    assert "external_sources" in report


def test_inventory_command_names_matches_files():
    module = load_script("inventory.py")

    names = module.command_names()

    assert len(names) == 11
    assert "tool-graph" in names
    assert "tool-quick" in names
    assert "tool-alias" in names


#
# validate-installer-sources.py
#

def test_validate_installer_sources_main():
    module = load_script("validate-installer-sources.py")

    rc = module.main()

    assert rc == 0


#
# dependency_manifest.json validity
#

def test_dependency_manifest_is_valid_json():
    manifest = ROOT / "scripts" / "dependency_manifest.json"

    data = json.loads(manifest.read_text(encoding="utf-8"))

    assert len(data) >= 8
    for name, entry in data.items():
        assert "strategy" in entry, f"{name} missing strategy"
        assert "scope_model" in entry, f"{name} missing scope_model"
        assert "auto_repair" in entry, f"{name} missing auto_repair"
        assert "repair_hint" in entry, f"{name} missing repair_hint"
