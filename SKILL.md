---
name: 工兵铲
display_name: engineer-shovel
description: |
  工兵铲 (Engineer Shovel) — AI 代理多功能开发工具。
  基于 OpenCode + superpowers + ecc + gsd + Caveman + rtk 工具链的完整工作流技能。
  封装为独立指令: /tool-feat /tool-fix /tool-plan /tool-refactor /tool-review /tool-brainstorm /tool-quick /tool-blueprint /tool-research
  覆盖新功能、Bug修复、头脑风暴、重构、代码审查、快速任务、复杂项目、深度研究 8 大场景。
  包含决策树、Token 管理、语言参考、命令速查表。
license: MIT
metadata:
  version: "1.0.0"
  category: workflow
  sources:
    - OhMyOpenCode documentation
    - superpowers plugin
    - ECC (Everything Claude Code)
    - GSD (Get Stuff Done)
    - Caveman plugin
    - rtk
---

# 🪖 工兵铲 — Engineer Shovel

**多合一 AI 代理开发工具** — 涵盖 `superpowers` + `ecc` + `gsd` + `Caveman` + `rtk` 完整工具链。

支持 **OpenCode** 和 **Claude Code** 双环境，每个工作流封装为独立斜杠指令。

> 快速命令: `/tool-feat` `/tool-fix` `/tool-plan` `/tool-refactor` `/tool-review` `/tool-brainstorm` `/tool-quick` `/tool-blueprint` `/tool-research`

---

## 🛠️ Command Reference

| Command | Scenario | Pipeline |
|---------|----------|----------|
| `/tool-feat` | 🆕 New Feature | 分析 → 规划 → 执行 → 验证 → 提交 |
| `/tool-fix` | 🐛 Bug Fix | 调试 → 定位 → 修复 → 验证 → 防回归 → 提交 |
| `/tool-plan` | 📐 Planning | 需求 → 分析 → 蓝图 → 审查 → 执行 |
| `/tool-refactor` | 🔧 Refactoring | 基线 → `/refactor` → 验证 → `/review-work` → 提交 |
| `/tool-review` | 📋 Code Review | 代码 → 审查 → 修复 → 重审 → 批准 |
| `/tool-brainstorm` | 💡 Brainstorming | 想法 → 探索 → 记录 → 评估 → 路由 |
| `/tool-quick` | ⚡ Quick Tasks | 任务 → `/gsd-fast`/cavecrew → 验证 → 提交 |
| `/tool-blueprint` | 🏗️ Complex Projects | 目标 → 蓝图 → 分步执行 → 集成 → 验证 → 发布 |
| `/tool-research` | 🔬 Deep Research | 问题 → 多源搜索 → 综合 → 报告 → 应用 |

Each command is in `commands/tool-*.md` and can be invoked directly in OpenCode or Claude Code.

---

## Environment Detection

This skill has two variants depending on the running environment:

| Aspect | OpenCode | Claude Code |
|--------|----------|-------------|
| **Platform** | OhMyOpenCode IDE | Claude Code CLI |
| **Skills** | `superpowers` + `ecc` + `gsd` | `superpowers` (plugin) + `ecc` + `gsd` |
| **Orchestrator** | Atlas (Master Agent) | Direct task() dispatch |
| **Planning** | `/plan`, `/prp-plan`, `/blueprint` | `/ecc:plan`, `/blueprint`, `/ecc:prp-plan` |
| **Execution** | `/prp-implement`, `task()`, `/gsd-execute-phase` | `task()`, `/ecc:prp-implement`, `/gsd-execute-phase` |
| **Debug** | `/gsd-debug` | `/gsd-debug` |
| **Review** | `/code-review`, `/review-work` | `/ecc:code-review`, `/ecc:review-pr` |
| **Fast Tasks** | `/gsd-fast`, cavecrew builder | `/gsd-fast`, cavecrew builder |
| **Token Mode** | `/caveman`, `/caveman-stats` | `/caveman`, `/caveman-stats` |
| **Context Mgmt** | `/strategic-compact`, `/gsd-thread` | `/strategic-compact`, `/gsd-thread` |

> **Note**: When specific commands differ between environments, this skill marks them as:
> - `[OC]` = OpenCode only
> - `[CC]` = Claude Code only
> - No prefix = works in both

---

## Core Principles

These principles apply to ALL workflows regardless of environment:

| # | Principle | Why |
|---|-----------|-----|
| 1 | **Search before build** | Use `/search-first` or research agents before writing custom code. Existing solutions save time. |
| 2 | **Test-first for anything non-trivial** | `/tdd-workflow` — write tests first, then implement. Prevents regression. |
| 3 | **Surgical changes** | ≤3 files per task. Complex work → break into atomic steps. |
| 4 | **Verify every step** | Build → Test → Lint → Manual review. Never skip verification. |
| 5 | **Token awareness** | Monitor `/caveman-stats`. Use `/caveman` mode for routine work. `/strategic-compact` when >50%. |
| 6 | **Parallel when independent** | Independent tasks → parallel `task()` calls. Dependent tasks → sequential. |
| 7 | **Commit early, commit often** | Each verified step gets an atomic commit with descriptive message. |
| 8 | **Use the right model for the job** | `visual-engineering` for UI, `ultrabrain` for hard logic, `deep` for autonomous work, `quick` for trivial. |

---

## Workflow Scenarios

---

### 1. 🆕 New Feature Development

**Pipeline:**
```
需求 → 分析 → 规划 → 执行 → 验证 → 提交
```

**OpenCode Flow:**
```bash
# Step 1: Search before code
/search-first "existing solutions for $FEATURE"

# Step 2: Create plan (choose one based on complexity)
# Simple feature:
/plan "implement $FEATURE with $REQUIREMENTS"
# Complex feature:
/blueprint project-name "implement $FEATURE across $COMPONENTS"

# Step 3: Execute plan
# After user confirms plan:
/prp-implement plan.md
# Or for GSD-managed projects:
/gsd-execute-phase

# Step 4: Verify
/verify
# Or individually:
bun run build   # or npm run build / cargo build
bun test        # or language-specific test command

# Step 5: Commit
git add .
git commit -m "feat: implement $FEATURE"
```

**Claude Code Flow:**
```bash
# Step 1: Research
task(subagent_type="explore", ..., prompt="Find existing patterns for $FEATURE")

# Step 2: Plan
/ecc:plan "implement $FEATURE with $REQUIREMENTS"
# Or for complex:
/blueprint project-name "implement $FEATURE"

# Step 3: Execute via task() delegation
task(category="deep", load_skills=["search-first", "tdd-workflow", "coding-standards"],
     prompt="[6-section prompt for $FEATURE]")

# Step 4: Verify
/verify
bun run build && bun test

# Step 5: Commit
git add . && git commit -m "feat: implement $FEATURE"
```

**Skill Loading by Feature Type:**

| Feature Type | Category | Skills |
|-------------|----------|--------|
| Frontend/UI | `visual-engineering` | `frontend-dev`, `frontend-design`, `ui-ux-pro-max` |
| Backend API | `deep` | `backend-patterns`, `api-design`, `search-first` |
| Full Stack | `deep` | `fullstack-dev`, `tdd-workflow`, `coding-standards` |
| Data/DB | `deep` | `postgres-patterns`, `database-migrations`, `search-first` |
| Simple tweak | `quick` | `coding-standards` |

**Decision Tree - How Deep to Plan?**

```
需求复杂度?
├── 单文件改动 (< 3 files, 逻辑明确)
│   └── ▶ /gsd-fast 或 cavecrew builder (直接干, 不规划)
├── 中等复杂度 (3-8 files, 需求清晰)
│   └── ▶ /plan → 确认 → /prp-implement
├── 复杂 (多组件/多文件, 有歧义)
│   └── ▶ /blueprint → review plan → 逐步执行
└── 不确定方案 (不知道怎么做)
    └── ▶ /deep-research "topic" → /gsd-explore → /plan
```

---

### 2. 🐛 Bug Fixing

**Pipeline:**
```
Bug 报告 → 定位 → 修复 → 验证 → 防止回归 → 提交
```

**Flow (same for both environments):**
```bash
# Step 1: Systematic debugging
/gsd-debug "$BUG_DESCRIPTION"
# This launches a structured debug session:
#   1. Reproduce the bug
#   2. Isolate the root cause
#   3. Form hypothesis
#   4. Fix
#   5. Verify fix

# Step 2: Implement fix (surgical, minimal change)
# After /gsd-debug identifies the cause, fix directly
# or via subagent:
task(session_id="$SESSION_FROM_DEBUG", prompt="Fix: $ROOT_CAUSE")

# Step 3: Verify
# Language-specific test command:
/go-test          # Go
/rust-test        # Rust
/cpp-test         # C++
/flutter-test     # Flutter/Dart
/kotlin-test      # Kotlin
/laravel-tdd      # Laravel
/django-tdd       # Django
/springboot-tdd   # Spring Boot
bun test          # Node/Bun

# Step 4: Verify no regression
/ai-regression-testing   # Auto-generate regression checks

# Step 5: Commit
git add .
git commit -m "fix: $ROOT_CAUSE_DESCRIPTION"
```

**Fix Magnitude Decision Tree:**

```
Bug scope?
├── Single line / typo
│   └── ▶ cavecrew builder: 直接修复 (1-2 file edit)
├── Single function (明确逻辑错误)
│   └── ▶ 直接修复 → 运行对应测试
├── Cross-file / architecture issue
│   └── ▶ /gsd-debug → task(category="deep", ...) → test
└── Security vulnerability
    └── ▶ /security-review → fix → /security-scan → commit
```

---

### 3. 💡 Brainstorming & Exploration

**Pipeline:**
```
想法 → 探索 → 记录 → 评估 → 执行决策
```

**Flow:**
```bash
# Step 1: Socratic exploration [OC]
/gsd-explore "I have an idea: $IDEA"

# Step 2: Capture the idea [both]
/gsd-note "capture: $IDEA_DESCRIPTION"

# Step 3: Structured brainstorming [both]
/superpowers:brainstorming
# The brainstorming skill explores:
#   - Intent hidden in the request
#   - Requirements and edge cases
#   - Design before implementation
#   - Assumptions and risks

# Step 4: Record decisions [both]
# Append to decisions.md with context

# Step 5: If proceeding → route to appropriate workflow
#   - Prototype: /gsd-fast "build poc for $IDEA"
#   - Full feature: /plan → /prp-implement
#   - Research first: /deep-research "$TOPIC"
#   - Backlog: /gsd-note "backlog: $IDEA"
```

**When to use which:**

| Signal | Tool | Why |
|--------|------|-----|
| "I have an idea but not sure" | `/gsd-explore` | Socratic questioning to refine |
| "How should I implement X?" | `/superpowers:brainstorming` | Structured design exploration |
| "Is there existing work?" | `/search-first` or `/deep-research` | Research before building |
| Quick thought capture | `/gsd-note` | Zero-friction capture |
| Multi-option decision | `/council` | 4-voice adversarial debate |

---

### 4. 🔧 Refactoring

**Pipeline:**
```
目标 → 规划 → 执行 → 验证 → 审查 → 提交
```

**Flow:**
```bash
# Step 1: Define goal (what NOT to change)
# External behavior MUST remain identical

# Step 2: Run existing tests first (baseline)
bun test   # or equivalent
# All must pass before we start

# Step 3: Execute refactor
/refactor "describe refactoring goal"
# The /refactor command:
#   1. Analyzes codebase with LSP + AST-grep
#   2. Creates architecture codemap
#   3. Executes refactoring in phases
#   4. Runs TDD verification after each phase

# Step 4: Verify behavior unchanged
bun test         # All tests must still pass
bun run build    # Build must pass

# Step 5: Comprehensive review
/review-work
# Launches 5 parallel review agents:
#   - Goal/constraint verification
#   - Code quality
#   - Security
#   - Hands-on QA
#   - Context mining

# Step 6: E2E check (if applicable)
/playwright   # Frontend E2E
# or
/e2e-testing  # Backend E2E

# Step 7: Commit
git add .
git commit -m "refactor: $SCOPE_DESCRIPTION"
```

**Refactoring Principles:**
```
原则 1: 不改行为 → 测试是安全网, 先确保测试全绿
原则 2: 小步提交 → 每次重构一个逻辑单元, 原子提交
原则 3: 不混入新功能 → refactor + feature 分开提交
原则 4: 性能不降 → 重构后对比基准性能
原则 5: 审查必须有 → 重构容易引入隐蔽 bug
```

---

### 5. 📋 Code Review

**Pipeline:**
```
代码 → 审查 → 修复 → 重新审查 → 批准
```

**Three modes:**

```bash
# Mode 1: Local uncommitted changes [OC]
/code-review
# Reviews staged/unstaged diff against local codebase

# Mode 2: GitHub PR [both]
/review-pr https://github.com/user/repo/pull/123
# or
/code-review https://github.com/user/repo/pull/123

# Mode 3: Post-implementation review [both]
/review-work
# Launches 5 parallel reviewers:
#   agent1: Goal/constraint check (Oracle)
#   agent2: Code quality check (Oracle)
#   agent3: Security audit (Oracle)
#   agent4: Hands-on QA (unspecified-high)
#   agent5: Context mining (unspecified-high)
# ALL must pass for review to pass.

# Mode 4: Caveman-compressed review [both - token efficient]
/caveman:caveman-review
# One-line per finding: path:line: <emoji> severity: problem. fix.
```

**Review Decision Tree:**

```
What to review?
├── Local diff (< 10 files)
│   └── ▶ /code-review (OpenCode) or /caveman:caveman-review (token efficient)
├── GitHub PR
│   └── ▶ /review-pr <url>
├── Major implementation (post-build)
│   └── ▶ /review-work (5 parallel agents)
├── Security-sensitive
│   └── ▶ /security-review → /security-scan → fix → re-review
└── Quick sanity check
    └── ▶ /caveman:caveman-review (cheapest option)
```

---

### 6. ⚡ Quick Tasks (Trivial)

**Pipeline:**
```
任务 → 直接执行 → 验证 → 提交
```

```bash
# Option A: GSD Quick [both]
/gsd-fast "fix typo in README.md"              # Text fix
/gsd-fast "update dependency version to 2.0"   # Config change
/gsd-fast "rename variable x to y in *.ts"     # Rename

# Option B: Caveman Builder [both - most token efficient]
# For 1-2 file surgical edits - uses cavecrew-builder subagent
# This is the CHEAPEST option available.
# The subagent output is caveman-compressed (~60% smaller context)

# Option C: Direct task() [both]
task(category="quick", load_skills=[],
     prompt="Change X to Y in file.ts")
```

**Task → Tool Mapping:**

| Task Type | Best Tool | Why |
|-----------|-----------|-----|
| Typo fix, 1 line | `/gsd-fast` | Inline, no overhead |
| 1-2 file edit, obvious | Cavecrew builder | ~60% token savings |
| Config change | `/gsd-fast` | Quick, safe |
| Simple rename | `/gsd-fast` or LSP rename | Built-in tooling |
| Any non-trivial | Full workflow | Don't skip planning |

---

### 7. 🏗️ Complex Multi-Step Projects

**Pipeline:**
```
目标 → 蓝图 → 分步执行 → 集成 → 验证
```

```bash
# Step 1: Create blueprint [both]
/blueprint project-name "migrate database from SQLite to PostgreSQL"
# Produces plans/PLAN.md with:
#   - Step-by-step breakdown (1 PR per step)
#   - Dependency graph
#   - Parallel vs serial ordering
#   - Rollback strategy per step

# OR: Initialize GSD project [both]
/gsd-new-project "project description"
# Produces:
#   - PROJECT.md with goals, scope, milestones
#   - ROADMAP.md with phased execution plan
# Then:
/gsd-plan-phase    # Plan each phase
/gsd-execute-phase # Execute each phase

# Step 2: Execute each step
# For each step, use the appropriate workflow:
#   - New feature: Feature workflow
#   - Refactor: Refactor workflow
#   - Bug fix: Bug workflow

# Step 3: Cross-phase integration check [both]
# When multiple phases touch the same code:
/gsd-verify-work   # Conversational UAT
/gsd-audit-uat     # Cross-phase UAT audit

# Step 4: Final review
/review-work

# Step 5: Create PR branch [both]
/gsd-pr-branch     # Clean PR branch (filters .planning/)
/gsd-ship          # PR + review + merge

# Step 6: Milestone management [both]
/gsd-milestone-summary   # Generate milestone report
/gsd-complete-milestone  # Archive and move on
```

**Blueprint Output Structure:**
```
plans/
└── $PROJECT-$FEATURE.md
    Each step contains:
    ├── Context Brief (enough for fresh agent to execute cold)
    ├── Task Checklist
    ├── Verification Commands
    └── Exit Criteria
```

---

### 8. 🔬 Deep Research

**Pipeline:**
```
问题 → 多源搜索 → 综合 → 报告 → 应用
```

```bash
# Step 1: Multi-source research [both]
/deep-research "How to implement $TECHNOLOGY for $USE_CASE"
# Searches: web, docs, GitHub, academic sources
# Returns: cited report with attribution

# Step 2: Code/pattern search [both]
# Library docs:
task(subagent_type="librarian", load_skills=[],
     prompt="Find examples of $PATTERN in $FRAMEWORK")

# Web search:
MiniMax_web_search(query="$TOPIC best practices 2026")

# Code search:
ecc_github_search_code(q="$TECHNIQUE language:typescript")

# Step 3: Synthesize findings
# Use /council for conflicting recommendations
/council "Option A vs Option B for $DECISION"

# Step 4: Route to implementation
# Decide: /plan → execute, or /gsd-fast for prototype
```

---

## Decision Trees

### Primary Router: What kind of work?

```
┌─────────────────────────────────────────────┐
│              NEW REQUEST                     │
└─────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  What kind of work?     │
        └──────┬──────┬──────┬────┘
               │      │      │
     ┌─────────┘      │      └──────────┐
     ▼                ▼                  ▼
┌──────────┐   ┌──────────┐      ┌──────────────┐
│ New      │   │ Bug Fix  │      │  Unknown/     │
│ Feature  │   │          │      │  Exploratory  │
└────┬─────┘   └────┬─────┘      └──────┬───────┘
     │              │                    │
     ▼              ▼                    ▼
  Check          /gsd-debug          /gsd-explore
  complexity      → fix              → understand
     │            → test             → route
     ▼            → commit
  /plan or
  /blueprint

┌──────────┐   ┌──────────┐      ┌──────────────┐
│ Refactor │   │ Review   │      │  Quick Task   │
└────┬─────┘   └────┬─────┘      └──────┬───────┘
     │              │                    │
     ▼              ▼                    ▼
  /refactor      /code-review         /gsd-fast or
  → verify       or /review-pr        cavecrew builder
  → /review-work or /review-work      → verify
  → commit       → approve            → commit
```

### Task Complexity Router (for feature work)

```
Task scope?
├── Trivial (< 3 files, obvious)
│   ├── Text/typo: /gsd-fast "fix ..."
│   ├── 1-2 file edit: Cavecrew builder
│   └── Any: task(category="quick", ...)
├── Medium (3-8 files, clear spec)
│   ├── [OC]: /plan → /prp-implement
│   ├── [CC]: /ecc:plan → task(deep, ...)
│   └── ALWAYS: /verify after
├── Complex (many files, ambiguous)
│   ├── /blueprint → multi-step execution
│   └── OR /gsd-new-project → phases
└── Unknown approach
    ├── /deep-research "solve $PROBLEM"
    └── /gsd-explore "approach for $GOAL"
```

---

## Token & Context Management

### Caveman Modes

Caveman compresses communication by ~75%, drastically extending context window life:

```bash
# Activate Caveman mode
/caveman full          # Full compression
/caveman lite          # Light compression (still readable)
/caveman ultra         # Maximum compression

# Check real token usage
/caveman-stats

# Compress memory files
/caveman:compress .claude/CLAUDE.md   # Compress project memory
/caveman:compress .planning/*.md      # Compress planning docs
```

### When to Use Caveman

| Context Usage | Action |
|---------------|--------|
| < 25% | Normal mode — full expressiveness |
| 25% - 50% | `/caveman lite` — light compression |
| 50% - 75% | `/caveman full` — full compression, consider `/strategic-compact` |
| > 75% | `/strategic-compact` — compact context + `/caveman ultra` |

### Context Preservation Strategies

```bash
# 1. Strategic compaction (mid-session)
/strategic-compact
# Suggests manual compaction points at logical intervals

# 2. Cross-session continuity [both]
/gsd-thread "create thread for project-x phase-2"
# Persists context across sessions

# 3. Session handoff [both]
/gsd-pause-work   # Create handoff doc when pausing
/gsd-resume-work  # Resume with full context

# 4. Save session [both]
/save-session     # Save to ~/.claude/session-data/
# Later:
/resume-session   # Load most recent session
```

---

## Language/Framework Quick Reference

| Language/Framework | Test Command | Build Command | Review Command |
|-------------------|--------------|---------------|----------------|
| Go | `/go-test` | `/go-build` | `/go-review` |
| Rust | `/rust-test` | `/rust-build` | `/rust-review` |
| C++ | `/cpp-test` | `/cpp-build` | `/cpp-review` |
| Flutter/Dart | `/flutter-test` | `/flutter-build` | `/flutter-review` |
| Kotlin | `/kotlin-test` | `/kotlin-build` | `/kotlin-review` |
| Python | `pytest` | - | `/python-review` |
| Laravel | `/laravel-tdd` | - | `/laravel-verification` |
| Django | `/django-tdd` | - | `/django-verification` |
| Spring Boot | `/springboot-tdd` | - | `/springboot-verification` |
| TypeScript/JS | `bun test` or `npm test` | `bun run build` | `/code-review` |

---

## Command Reference Summary

| Scenario | Command | Environment | Effort |
|----------|---------|-------------|--------|
| New Feature | `/plan` → `/prp-implement` | OC | Medium |
| New Feature (complex) | `/blueprint` → steps | Both | High |
| New Feature (simple) | `/gsd-fast` | Both | Low |
| Bug Fix | `/gsd-debug` → fix → test | Both | Medium |
| Brainstorming | `/gsd-explore` or `/superpowers:brainstorming` | Both | Low |
| Refactoring | `/refactor` → verify → `/review-work` | Both | High |
| Code Review (local) | `/code-review` | OC | Low |
| Code Review (PR) | `/review-pr <url>` | Both | Low |
| Deep Review | `/review-work` | Both | Medium |
| Quick Task | `/gsd-fast` or cavecrew builder | Both | Low |
| Complex Project | `/blueprint` or GSD phases | Both | High |
| Deep Research | `/deep-research` | Both | Medium |
| Security Review | `/security-review` → `/security-scan` | Both | Medium |
| Token Save | `/caveman` + `/strategic-compact` | Both | - |
| Session Continuity | `/gsd-thread` or `/save-session` | Both | - |
| Decision Help | `/council` | Both | Low |
| UAT Verification | `/gsd-verify-work` | Both | Medium |

---

## Installation & Verification

This skill is installed at:
```
/root/.agents/skills/engineer-shovel/SKILL.md
```

**Verify it's loaded:**
```bash
# Check that engineer-shovel appears in available skills
# via the `skill` tool or look for it in the directory:
ls /root/.agents/skills/engineer-shovel/
```

**Usage:**
```bash
# Load this skill when starting a new development task
skill(name="engineer-shovel")

# Then follow the appropriate workflow from the sections above
```

---

*Generated for OpenCode + superpowers + ecc + gsd + Caveman + rtk toolchain*
*Claude Code variant: superpowers + ecc + gsd + Caveman + rtk*
*Last updated: 2026-05-01*
