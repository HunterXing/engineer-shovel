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
        "ECC": "v2.0.0-rc.1",
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


def test_installer_dry_run_mentions_all_full_mode_integrations():
    install_text = (ROOT / "install.sh").read_text(encoding="utf-8")

    for marker in (
        "install_ecc",
        "install_gsd",
        "install_superpowers",
        "install_caveman_for_target",
        "install_rtk",
        "install_code_review_graph",
        "rtk init",
        "code-review-graph install",
        "code-review-graph build",
    ):
        assert marker in install_text


def test_feature_workflow_requires_branch_gate():
    text = (ROOT / "commands" / "tool-feat.md").read_text(encoding="utf-8")

    assert "/tool-branch create" in text
    assert "before editing" in text.lower()
