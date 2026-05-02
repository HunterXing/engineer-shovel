---
description: Token statistics workflow — report session token usage and savings from Caveman/RTK where available
argument-hint: [--fast|--full]
cost-profile: low
risk-level: low
recommended-mode: --fast
allowed-tools: [Bash]
escalates-to: []
depends-on: []
when-to-use: Use when reporting measured session token usage or Caveman/RTK savings without inventing precision.
---

# /tool-statistic — Token Statistics

**Input**: $ARGUMENTS

Report token usage and savings without mixing static estimates with measured session data.

Compression: follow `docs/token-cost.md`; use `/caveman lite` and keep this command short.

## Flow

1. Run `/caveman-stats` when Caveman is installed; prefer its real session log numbers over estimates.
2. If RTK is installed, run `rtk gain --project --format json` for current-project measured shell-output savings.
3. If project scope is empty, run `rtk gain` for global measured shell-output savings and clearly label it as global.
4. Optionally run `rtk session` to show adoption across recent sessions.
5. Do not run `rtk gain --history` by default; RTK 0.37.2 can panic on non-ASCII paths in history rendering.
6. Separate static estimates, unknown sources, and measured data.
7. Summarize in this format:
   - Static benchmark: estimate from `scripts/token-benchmark.py`, labeled static proxy.
   - Caveman: measured input/output or saved tokens if `/caveman-stats` reports them; otherwise unknown.
   - RTK project: measured shell-output savings from `rtk gain --project --format json`; otherwise unknown.
   - RTK global: measured shell-output savings from `rtk gain` when project data is empty, labeled global.
   - RTK session adoption: recent adoption from `rtk session` if available.
   - Total: only compute a total when both sources provide measured values.

## Guardrails

- Do not claim exact RTK savings unless `rtk gain` provides them.
- Do not label `scripts/token-benchmark.py` output as measured savings; it is a static Markdown-size estimate.
- Do not mix model-output compression with shell-output compression.
- If no statistics backend is available, explain how to enable `/caveman-stats` and RTK hooks.
- `rtk hook-audit` needs `RTK_HOOK_AUDIT=1`; if no audit log exists, report that audit is disabled rather than failed.
