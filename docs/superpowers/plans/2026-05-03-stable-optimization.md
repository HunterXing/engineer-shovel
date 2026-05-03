# Stable Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Engineer Shovel safer and clearer by fixing GSD flag drift, OpenCode GSD health detection, default graph-build behavior, and capability-boundary documentation.

**Architecture:** Keep the existing Bash installer and Python health script structure. Apply surgical changes to current functions and add regression tests in the existing single pytest file.

**Tech Stack:** Bash, Python 3 stdlib, pytest, Markdown docs, GitHub Actions-compatible validation commands.

---

## File Structure

- Modify: `install.sh`
  - Add `WITH_GRAPH_BUILD` option parsing.
  - Change GSD both-target flag from `--both` to `--all`.
  - Gate `code-review-graph build` behind `--with-graph-build`.
- Modify: `scripts/health.py`
  - Update OpenCode GSD skill marker detection to include `~/.agents/skills`.
- Modify: `tests/test_validation_scripts.py`
  - Add regression tests for GSD flags, GSD marker detection, graph build opt-in, and README capability boundary.
- Modify: `README.md`
  - Clarify native versus external capabilities.
  - Document `--with-graph-build`.
- Modify: `README_zh.md`
  - Mirror the capability boundary and graph-build guidance in Chinese.
- Modify: `docs/install.md`
  - Document graph-build opt-in behavior.

## Task 1: Add Failing Regression Tests

**Files:**
- Modify: `tests/test_validation_scripts.py`

- [ ] **Step 1: Add installer text regression tests**

Add these tests after `test_installer_dry_run_mentions_all_full_mode_integrations`:

```python
def test_installer_uses_all_for_gsd_dual_target():
    install_text = (ROOT / "install.sh").read_text(encoding="utf-8")

    assert 'gsd_target="--all"' in install_text
    assert 'gsd_target="--both"' not in install_text


def test_graph_build_is_explicit_installer_option():
    install_text = (ROOT / "install.sh").read_text(encoding="utf-8")

    assert "WITH_GRAPH_BUILD" in install_text
    assert "--with-graph-build" in install_text
    assert "Skipping code-review-graph build; pass --with-graph-build" in install_text
```

- [ ] **Step 2: Add health marker regression test**

Add this test after `test_health_detects_project_language_markers`:

```python
def test_health_detects_opencode_gsd_agent_skill_marker(tmp_path, monkeypatch):
    module = load_script("health.py")
    monkeypatch.setattr(module, "HOME", tmp_path)
    marker = tmp_path / ".agents" / "skills" / "gsd-core" / "SKILL.md"
    marker.parent.mkdir(parents=True)
    marker.write_text("# GSD\n", encoding="utf-8")

    result = module.check_gsd("opencode")

    assert result.status == module.STATUS_OK
```

- [ ] **Step 3: Add README boundary regression test**

Add this test after `test_readmes_list_upstream_tool_versions`:

```python
def test_readme_clarifies_native_and_external_capabilities():
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Native Engineer Shovel" in text
    assert "optional external tools" in text
    assert "--with-graph-build" in text
```

- [ ] **Step 4: Run targeted tests and confirm failure**

Run: `pytest tests/test_validation_scripts.py -v`

Expected: FAIL because the new behavior is not implemented yet.

## Task 2: Implement Installer Fixes

**Files:**
- Modify: `install.sh`

- [ ] **Step 1: Add graph-build state variable**

Near the existing globals, after `DRY_RUN=0`, add:

```bash
WITH_GRAPH_BUILD=0
```

- [ ] **Step 2: Document the new option in usage**

In the `usage()` heredoc, add this line below `--dry-run`:

```text
  --with-graph-build
                 In full mode, run initial code-review-graph build after install.
```

- [ ] **Step 3: Parse the new option**

In `parse_args()`, add a case next to `--dry-run`:

```bash
      --with-graph-build) WITH_GRAPH_BUILD=1 ;;
```

- [ ] **Step 4: Align GSD dual-target flag**

In `install_gsd()`, replace:

```bash
    gsd_target="--both"
```

with:

```bash
    gsd_target="--all"
```

- [ ] **Step 5: Gate graph build in dry-run output**

In `install_code_review_graph()`, replace the unconditional dry-run build line with:

```bash
    if [[ "$WITH_GRAPH_BUILD" -eq 1 ]]; then
      info "DRY-RUN: code-review-graph build"
    else
      info "DRY-RUN: Skipping code-review-graph build; pass --with-graph-build to run it"
    fi
```

- [ ] **Step 6: Gate graph build execution**

In `install_code_review_graph()`, wrap the real graph build block so it only runs when `WITH_GRAPH_BUILD=1`:

```bash
  if [[ "$WITH_GRAPH_BUILD" -ne 1 ]]; then
    info "Skipping code-review-graph build; pass --with-graph-build to run it."
    return 0
  fi

  if [[ -d ".git" ]]; then
    info "Building code-review-graph for current repository..."
    code-review-graph build 2>&1 || record_failure "code-review-graph build failed; run manually: code-review-graph build"
  else
    info "Skipping code-review-graph build outside a git worktree"
  fi
```

- [ ] **Step 7: Run installer-focused checks**

Run:

```bash
bash -n install.sh
bash install.sh --full --dry-run
bash install.sh --full --with-graph-build --dry-run
```

Expected: syntax passes; default full dry-run says graph build is skipped; explicit full dry-run prints `code-review-graph build`.

## Task 3: Implement Health Detection Fix

**Files:**
- Modify: `scripts/health.py`

- [ ] **Step 1: Update `check_gsd()` skill directories**

Replace the single `skill_dir` assignment and `has_gsd` line with:

```python
    if target == "opencode":
        skill_dirs = [HOME / ".agents/skills", HOME / ".config/opencode/skills"]
    else:
        skill_dirs = [HOME / ".claude/skills"]
    has_gsd = any(command_dir.glob("gsd-*.md")) if command_dir.exists() else False
    has_gsd = has_gsd or any(
        skill_dir.exists() and any(skill_dir.glob("gsd-*/SKILL.md"))
        for skill_dir in skill_dirs
    )
```

- [ ] **Step 2: Run health-focused tests**

Run: `pytest tests/test_validation_scripts.py::test_health_detects_opencode_gsd_agent_skill_marker tests/test_validation_scripts.py::test_health_repair_gsd_uses_all_for_both_targets -v`

Expected: PASS.

## Task 4: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `README_zh.md`
- Modify: `docs/install.md`

- [ ] **Step 1: Update English README capability boundary**

Add this section after the first “What is this?” paragraph:

```markdown
## Capability Boundary

Native Engineer Shovel installs the lightweight router and 12 `/tool-*` commands. The deeper capabilities advertised in full workflows come from optional external tools installed or configured by recommended/full modes: ECC, GSD, superpowers, code-review-graph, Caveman, and RTK.

Minimal installs are intentionally small. If a workflow mentions external commands such as GSD, ECC, Caveman, RTK, or code-review-graph behavior, those capabilities require the corresponding optional tool to be installed and healthy.
```

- [ ] **Step 2: Update English README install examples**

Add this example near the install mode examples:

```bash
./install.sh --target opencode --full --with-graph-build  # Also build initial code-review-graph index
```

- [ ] **Step 3: Update Chinese README capability boundary**

Add the equivalent Chinese section after the “What is this?” / project introduction section:

```markdown
## 能力边界

Engineer Shovel 原生安装的是轻量路由器和 12 个 `/tool-*` 命令。完整工作流里更深的能力来自 recommended/full 模式安装或配置的可选外部工具：ECC、GSD、superpowers、code-review-graph、Caveman 和 RTK。

Minimal 安装会刻意保持小而轻。如果某个流程提到 GSD、ECC、Caveman、RTK 或 code-review-graph 等外部能力，需要对应工具已经安装并处于健康状态。
```

- [ ] **Step 4: Update install docs graph-build behavior**

In `docs/install.md`, add a short note near full mode documentation:

```markdown
Full mode installs and configures code-review-graph but does not build the initial repository graph by default. Pass `--with-graph-build` when you want installation to run `code-review-graph build` for the current git worktree.
```

- [ ] **Step 5: Run docs validators**

Run:

```bash
python3 scripts/validate-references.py
python3 scripts/validate-markdown-links.py
```

Expected: both pass.

## Task 5: Full Verification

**Files:**
- No code edits unless verification exposes failures.

- [ ] **Step 1: Run full validation suite**

Run:

```bash
python3 scripts/validate-command-schema.py
python3 scripts/validate-references.py
python3 scripts/validate-markdown-links.py
python3 scripts/validate-installer-sources.py
python3 -m py_compile scripts/*.py
pytest
bash -n install.sh
bash install.sh --minimal --dry-run
bash install.sh --recommended --dry-run
bash install.sh --full --dry-run
bash install.sh --full --with-graph-build --dry-run
```

Expected: all commands pass. Default full dry-run skips graph build. Explicit full dry-run includes graph build.

- [ ] **Step 2: Inspect git diff**

Run: `git diff -- install.sh scripts/health.py tests/test_validation_scripts.py README.md README_zh.md docs/install.md docs/superpowers/specs/2026-05-03-stable-optimization-design.md docs/superpowers/plans/2026-05-03-stable-optimization.md`

Expected: diff only contains the planned surgical changes.
