# Shared Policies for Engineer Shovel Commands

This file contains shared policies referenced by all command files.
Do NOT duplicate these sections in command files — reference them instead.

---

## Cost Modes

| Mode | Caveman | When | Token Cost |
|------|---------|------|------------|
| `--fast` | `/caveman lite` | Small, obvious changes, 1-2 files | Lowest |
| `--standard` | `/caveman full` | Normal development (default) | Medium |
| `--deep` | `/caveman full` → `ultra` | Complex, risky, cross-system, security-sensitive | Higher |

**Smart Mode** (auto-detect when mode not specified):
- Single file, obvious change → `--fast`
- Multiple files, clear scope → `--standard`
- Cross-module, security, ambiguous → `--deep`

**Auto-escalation triggers** (→ `--deep`):
- Security-sensitive code touched
- More than 5 files affected
- Cross-module dependencies unclear

**Auto-de-escalation triggers** (→ `--fast`):
- Single file, obvious change
- No dependencies affected
- Clear verification path

---

## Security Gate

**Enforced on ALL commands regardless of cost mode.**

If any change touches:
- auth
- user input parsing
- file system paths
- network I/O
- secrets
- cookies
- SQL
- serialization

**Action**: Immediately promote to `--deep` and add `/tool-review --deep` before sign-off.

---

## Toolchain Announcements

When using external tools, announce with maximum visibility:

```
🚀 **[Tool Name]** → <action description>
```

### Required Announcements

| Tool | When to Announce |
|------|------------------|
| `code-review-graph` | Querying code graph, impact analysis, architecture overview |
| `caveman` | Applying compression, recording stats |
| `rtk` | Wrapping large output (tests, builds, git) |
| `superpowers` | Loading TDD, debugging, verification skills |
| `ECC` | Loading framework, security, domain guidance |
| `OpenSpec` | Creating durable specs |
| `GSD` | Orchestrating multi-phase work |
| `claude-mem` | Searching cross-session memory |
| `WebFetch` | Fetching external docs |

### Native Tools (No Announcement Needed)

- Read, Grep, Glob, Edit, Bash

---

## Completion Pipeline

### `--standard` Completion

1. Run project-native targeted tests/build/typecheck
2. Use `/tool-review --fast` or Caveman-compressed diff sanity check
3. Offer `/caveman-commit` suggestion — **NEVER** auto-commit without explicit user request

### `--deep` Completion

1. `skill(name="gsd-verify-work")` — structured acceptance verification against plan/spec
2. `skill(name="gsd-code-review")` — phase-scoped review with severity-classified findings
3. `skill(name="gsd-ship")` — create PR, run review gates, prepare for merge
4. Offer `/caveman-commit` suggestion

---

## Escalation Rules

| Need | Escalate to | When |
|------|-------------|------|
| Callers, impact radius, test coverage | `code-review-graph` | Multi-file reasoning needed |
| Debugging discipline, TDD | `superpowers` | Single task needs better method |
| Durable specs, reviewable artifacts | `OpenSpec` | Agreement must persist in files |
| Framework, security, integration | `ECC` | Specialized domain knowledge needed |
| Multi-phase, cross-session | `GSD` | Milestone-scale delivery |

---

## Error Recovery

1. **Tool unavailable**: Fall back to native tools (Grep, Glob, Read, Bash)
2. **Verification failure**: Revert changes and reassess approach
3. **External service down**: Use cached data or skip non-critical steps
4. **Scope creep**: Split work into smaller slices and defer additional scope
5. **Repeated failures**: Escalate to `/tool-plan --deep` for architectural review

---

## Cache Layer

Cache reduces redundant queries within a session:

| Operation | TTL | Token Savings |
|-----------|-----|---------------|
| `impact_radius` | 5 min | ~80% |
| `architecture_overview` | 30 min | ~90% |
| `test_coverage` | 10 min | ~70% |
| `callers_of` | 5 min | ~80% |
| `callees_of` | 5 min | ~80% |

**Cache behavior**:
- **Hit**: Use cached result, skip tool invocation → saves tokens
- **Miss**: Query tool normally, cache result
- **Stale**: TTL expired, re-query on next access
- **Invalidated**: File changed, cache cleared

---

## References

- Full router: `skill(name="engineer-shovel")` or `SKILL.md`
- Complete guide: `SKILL-full.md`
- Architecture: `docs/architecture.md`
- Token cost: `docs/token-cost.md`
- Command scenarios: `docs/command-scenarios.md`
- Installation: `docs/install.md`
