from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
    module = load_script("validate-command-schema.py")
    command_dir = tmp_path / "commands"
    command_dir.mkdir()
    write_command(command_dir / "tool-test.md")
    monkeypatch.setattr(module, "COMMAND_DIR", command_dir)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.main() == 0


def test_validate_command_schema_rejects_missing_fields(tmp_path, monkeypatch):
    module = load_script("validate-command-schema.py")
    command_dir = tmp_path / "commands"
    command_dir.mkdir()
    write_command(command_dir / "tool-broken.md", include_required=False)
    monkeypatch.setattr(module, "COMMAND_DIR", command_dir)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.main() == 1


def test_validate_markdown_links_accepts_existing_local_link(tmp_path, monkeypatch):
    module = load_script("validate-markdown-links.py")
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text("[Doc](docs/page.md)\n", encoding="utf-8")
    (tmp_path / "docs" / "page.md").write_text("# Page\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.main() == 0


def test_validate_markdown_links_rejects_missing_local_link(tmp_path, monkeypatch):
    module = load_script("validate-markdown-links.py")
    (tmp_path / "README.md").write_text("[Missing](docs/missing.md)\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)

    assert module.main() == 1


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


def test_command_set_stays_at_twelve_with_graph_replacing_statistic():
    commands = sorted(path.stem for path in (ROOT / "commands").glob("tool-*.md"))

    assert len(commands) == 12
    assert "tool-graph" in commands
    assert "tool-statistic" not in commands


def test_readmes_list_upstream_tool_versions():
    expected = {
        "ECC": "v1.10.0",
        "GSD": "v1.39.0",
        "superpowers": "v5.0.7",
        "code-review-graph": "v2.3.2",
        "Caveman": "v1.7.0",
        "RTK": "v0.38.0",
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
    monkeypatch.setattr(module, "HOME", tmp_path)
    marker = tmp_path / ".agents" / "skills" / "gsd-core" / "SKILL.md"
    marker.parent.mkdir(parents=True)
    marker.write_text("# GSD\n", encoding="utf-8")

    result = module.check_gsd("opencode", "global")

    assert result.status == module.STATUS_OK


def test_health_detects_local_gsd_command_marker(tmp_path, monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    marker = tmp_path / ".opencode" / "commands" / "gsd-test.md"
    marker.parent.mkdir(parents=True)
    marker.write_text("# GSD\n", encoding="utf-8")

    result = module.check_gsd("opencode", "local")

    assert result.status == module.STATUS_OK


def test_health_code_review_graph_missing_when_binary_absent(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: None)

    result = module.check_code_review_graph(module.CommandRunner(dry_run=True))

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

    module.repair_code_review_graph(runner, ["opencode", "claude"])

    assert ["code-review-graph", "install", "--platform", "opencode"] in runner.commands
    assert ["code-review-graph", "install", "--platform", "claude-code"] in runner.commands
    assert ["code-review-graph", "build"] in runner.commands


def test_health_repair_code_review_graph_installs_when_missing(monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "which", lambda name: "/bin/" + name if name == "pipx" else None)
    runner = module.CommandRunner(dry_run=True)

    module.repair_code_review_graph(runner, ["opencode"])

    assert ["pipx", "install", "code-review-graph"] in runner.commands
    assert ["code-review-graph", "install", "--platform", "opencode"] in runner.commands


def test_health_repair_gsd_uses_all_for_both_targets():
    module = load_script("health.py")
    runner = module.CommandRunner(dry_run=True)

    module.repair_gsd(runner, ["opencode", "claude"], "global")

    assert ["npx", "-y", "get-shit-done-cc@latest", "--all", "--global"] in runner.commands


def test_health_repair_gsd_uses_local_scope_flag():
    module = load_script("health.py")
    runner = module.CommandRunner(dry_run=True)

    module.repair_gsd(runner, ["opencode"], "local")

    assert ["npx", "-y", "get-shit-done-cc@latest", "--opencode", "--local"] in runner.commands


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

    assert runner.commands == [[
        "bash",
        "-lc",
        "curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash -s -- --only claude",
    ]]


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
