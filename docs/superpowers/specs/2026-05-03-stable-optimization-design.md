# Stable Optimization Design

## Goal

Improve Engineer Shovel reliability and trust without changing the public command surface or restructuring the installer.

## Scope

This optimization targets high-signal issues found in the repository assessment:

- Align GSD target flags between `install.sh` and `scripts/health.py`.
- Detect OpenCode GSD files in the same skill directory family used by this project.
- Stop running `code-review-graph build` by default during full installation; make it explicit.
- Clarify that Engineer Shovel installs 12 native `/tool-*` commands and delegates deeper capabilities to optional external tools.
- Add regression tests for the behavior above.

## Non-Goals

- Do not split `install.sh`.
- Do not add uninstall or rollback flows.
- Do not add a manifest or integration registry.
- Do not rename, add, or remove `/tool-*` commands.
- Do not change the meaning of `--minimal`, `--recommended`, or `--full` beyond making graph build explicit.

## Design

### Installer Behavior

`install.sh` will add a `--with-graph-build` flag. Full installation will still install and configure `code-review-graph`, but it will skip the expensive initial graph build unless the flag is supplied.

GSD installation will use the same dual-target flag as health repair. The existing test contract expects `npx -y get-shit-done-cc@latest --all --global`, so `install.sh` should emit `--all` when both OpenCode and Claude Code targets are selected.

### Health Behavior

`scripts/health.py` will keep command-marker detection as the primary GSD signal and also check OpenCode skill markers under `~/.agents/skills`, matching the project install layout. Claude Code detection remains under `~/.claude/skills`.

### Documentation Behavior

README documentation will state the capability boundary plainly:

- Native Engineer Shovel install provides the router and 12 `/tool-*` commands.
- Recommended/full modes install or configure optional external tools.
- Commands such as GSD, ECC, Caveman, RTK, and code-review-graph capabilities depend on those optional tools being present.

Install docs will mention that graph build is opt-in through `--with-graph-build`.

### Testing

Regression tests will cover:

- Installer text uses `--all` for GSD and no longer uses `--both`.
- OpenCode GSD health detection recognizes `~/.agents/skills/gsd-*/SKILL.md`.
- Full-mode integration marker tests reflect `code-review-graph install` as default and graph build as opt-in.
- README documents native versus external capability boundaries.

## Verification

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

## Acceptance Criteria

- All verification commands pass.
- Full dry-run does not print `code-review-graph build` unless `--with-graph-build` is present.
- GSD install and health repair use the same dual-target flag.
- README makes native and external capabilities distinguishable.
