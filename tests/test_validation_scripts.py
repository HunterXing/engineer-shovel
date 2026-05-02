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
