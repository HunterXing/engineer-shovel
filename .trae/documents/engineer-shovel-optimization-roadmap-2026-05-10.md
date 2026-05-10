# Engineer Shovel 项目优化路线图

## Summary

目标：基于当前仓库的真实实现，形成一套“小步快跑、以可靠性优先”的优化路线图，先修会影响安装/更新/健康检查正确性的缺口，再收敛文档与职责边界，最后补关键行为测试，让项目更稳定、更容易维护，也更符合“full capability available, lightweight execution by default”的产品定位。

本轮计划不追求大重写，优先选择 3 类高收益动作：

- 修复已能从代码直接确认的行为问题。
- 收紧 `install.sh` / `scripts/sync.py` / `scripts/health.py` / `commands/tool-update.md` 之间的职责与心智模型。
- 用少量高价值测试替换部分“只检查字符串存在”的回归覆盖。

## Current State Analysis

### 1. 仓库形态与当前优势

- 主入口清晰：`SKILL.md`、`commands/tool-*.md`、`install.sh`、`scripts/*.py`、`docs/*.md`。
- 文档已经在强调“路由器而不是工具集合”，例如 `README.md`、`SKILL.md`、`docs/architecture.md`。
- CI 已覆盖 schema、链接、安装 dry-run、`py_compile`、`pytest`、`shellcheck`，见 `.github/workflows/ci.yml`。
- 已有测试基础，但当前 `tests/test_validation_scripts.py` 仍以存在性断言、字符串断言为主，关键更新/修复路径的行为覆盖偏薄。

### 2. 可靠性优先的明确问题

#### `scripts/health.py`

- `repair_claude_mem()` 当前把 `"--ide opencode"` / `"--ide claude"` 作为单个参数传给 `runner.run([...])`，这在 Python 参数列表里不会被拆分，实际修复命令大概率失效。
- `repair_caveman()` 针对 Claude 分支使用 `--only claude-code`，而 `install.sh` 中对应官方安装器使用的是 `--only claude`；两条安装链路参数不一致，存在修复路径漂移。
- `check_claude_mem()` 内部直接新建 `CommandRunner(dry_run=False)`，绕过了上层传入的 runner，导致 dry-run / 可测试性 / 依赖注入都不一致。
- `run_health()` 即使接收到 `dry_run=True`，首轮检查依然固定用 `CommandRunner(dry_run=False)`；这会让“只检查”与“演练模式”含义不完全一致。
- `health.py` 完全没有 `scope` 维度，而 `install.sh` 与 `scripts/sync.py` 都支持 `global|local`；这意味着本地安装虽然可装，但更新/健康检查心智与实现不完整。

#### `scripts/sync.py`

- `get_repo_files()` 包含 `hooks` 分支并访问 `TRACKED_FILES["hooks"]`，但 `TRACKED_FILES` 中并不存在该键；虽然当前主流程未触发，但这是明显的死分支和未来故障点。
- `compare_files()` 传入 `repo_root` 却未使用，说明接口曾扩展后未清理，属于轻度设计漂移。
- `check` 路径默认执行 `git fetch origin`，虽然有 `--skip-fetch`，但“状态检查”与“触网探测”的耦合偏紧，不利于离线或低副作用使用。
- `scripts/sync.py` 文案强调自己是 `/tool-update` 的底层，但 `/tool-update` 文档没有把 `scope` 和 router/component 两层限制讲得足够清楚。

#### `install.sh`

- 单文件已承担参数解析、交互选择、核心路由安装、多个外部组件安装与 repair hint、配置注入、verify，职责过重。
- 安装链路内部已经体现出一些组件差异化规则，但这些规则同时散在 `install.sh`、`scripts/health.py`、`docs/install.md` 三处，维护时容易漂移。
- `install.sh` 与 `health.py` 在部分组件上存在轻度实现重复，例如 Caveman、claude-mem、GSD、superpowers 的检查/修复逻辑各自维护一套变体。

### 3. 文档一致性与信息架构问题

- `README.md` 的结构图没有出现 `pages/`、`.github/workflows/`、`.trae/documents/` 等真实目录；这不是功能 bug，但会降低“看仓库即理解结构”的准确性。
- `commands/tool-plan.md`、`tool-feat.md`、`tool-fix.md`、`tool-research.md` 都重复讲了 CRG、claude-mem、OpenSpec、GSD 的升级规则，和 `SKILL.md` / `docs/architecture.md` 有重叠。
- `commands/tool-update.md` 强调“唯一更新入口”，但其底层脚本对 `scope`、dry-run 语义、局部/全局安装差异的表达仍不完整。
- `docs/install.md` 已说明 `global|local`，但 `health.py` 没有实现对应检查能力，这会让文档和行为出现预期差。

### 4. 测试结构上的主要缺口

- 现有测试多验证“文本里提到了某个命令/字段”，例如对 README、安装脚本、命令文件的字符串断言。
- 缺少针对 `scripts/health.py` 修复命令参数是否正确拆分的测试。
- 缺少针对 `dry_run` 是否真的不执行有副作用命令的测试。
- 缺少针对 `local` 安装/检查矩阵的回归测试。
- 缺少针对 `scripts/sync.py` 的真实比较/更新行为覆盖，只检查了“是否提到 health.py”。

## Assumptions & Decisions

### 已确认偏好

- 优先级：可靠性 > 文档一致性 > 架构简化 > 测试补强。
- 节奏：小步快跑，优先做 3-5 个高收益小改。
- 交付形态：阶段路线图，而不是一次性大重构。

### 本计划决策

- 保持公开接口稳定：不改 `skill(name="engineer-shovel")`、不改 `/tool-*` 命令名、不断言用户必须迁移已有安装方式。
- 第一阶段只修“代码里已经能证实的问题”，避免把“架构优化”变成重写。
- 任何架构性调整都必须服务于两件事：
  - `/tool-update` 真的能成为统一心智入口。
  - full install 不等于复杂的日常执行路径。
- 优先补行为测试，不扩张低价值文档快照测试。

## Proposed Changes

### Phase 1: 修复更新与健康检查中的确定性问题

目标：先让已有路径“说到做到”，消除最可能导致更新/修复命令失效的实现问题。

#### 受影响文件

- `scripts/health.py`
- `scripts/sync.py`
- `tests/test_validation_scripts.py`
- `commands/tool-update.md`

#### 具体改动

- 修复 `repair_claude_mem()` 的参数拆分，确保 `npx claude-mem install --ide opencode|claude` 以正确 argv 形式执行。
- 统一 Caveman Claude 目标参数，确保 `health.py` 与 `install.sh` 使用同一套官方 installer flag。
- 把 `check_claude_mem()` 改为复用上层 runner，而不是内部私建执行器。
- 让 `run_health(..., dry_run=True)` 的检查阶段也遵守 dry-run 语义，至少做到“可注入 runner、可测试、无隐藏副作用”。
- 清理 `scripts/sync.py` 中未使用或错误的分支，例如 `hooks` 死分支与无效参数。
- 在 `commands/tool-update.md` 中补充 `scope` 现状、dry-run 边界、router/component 分层说明，避免文档暗示比实现更强的能力。

#### 为什么

- 这批改动不需要改变产品形态，却能直接提升安装/修复命令可信度。
- 它们都能从当前代码直接确认，不需要额外产品决策。

### Phase 2: 对齐 local/global 安装的更新与健康模型

目标：收敛“支持 local 安装，但更新/健康检查主要按 global 假设”的断层。

#### 受影响文件

- `scripts/health.py`
- `scripts/sync.py`
- `commands/tool-update.md`
- `docs/install.md`
- `README.md`
- `README_zh.md`

#### 具体改动

- 为 `scripts/health.py` 增加 `--scope global|local`，至少覆盖 Engineer Shovel 自己安装目标与能明确检查的组件路径。
- 明确组件按 scope 的真实能力边界：
  - 哪些组件始终 global，例如 RTK。
  - 哪些组件 local 安装有限支持，例如 ECC 跳过 local。
  - 哪些组件只检查 router 层、不承诺 local component health。
- 将 `/tool-update` 文档与 `docs/install.md` 统一成一个矩阵：`target × scope × router/component`。
- 若 `health.py` 暂时无法完整支持某些 local 组件，文档明确写出“部分支持/仅报告/不自动 repair”，不再模糊化。

#### 为什么

- 当前“能安装但不容易维护”的体验，会直接削弱 local scope 的可信度。
- 这是文档一致性和可靠性同时受益的一步，但实现仍可保持保守。

### Phase 3: 拆轻 `install.sh` 的职责边界，不做大重写

目标：不推翻安装脚本，只把最容易漂移的组件逻辑收口，降低未来维护成本。

#### 受影响文件

- `install.sh`
- `scripts/health.py`
- `docs/install.md`
- `docs/dependency-policy.md`

#### 具体改动

- 先做轻量收敛，不直接拆成多个新脚本：
  - 提炼组件安装/检查的共享常量或注释分区。
  - 对与 `health.py` 重复的 flag 语义加注释，并统一术语。
- 统一组件状态语言，例如 `missing / unconfigured / blocked / ok` 的定义与文档说明。
- 在 `docs/dependency-policy.md` 或 `docs/install.md` 中补一张“组件安装/检查/repair 来源矩阵”：
  - 安装入口在哪。
  - repair 入口在哪。
  - 是否支持 dry-run。
  - 是否支持 local。

#### 为什么

- 目前最大问题不是“文件太长”本身，而是“行为规则分散且易漂移”。
- 先统一术语和边界，比立即物理拆文件更稳妥。

### Phase 4: 压缩命令文档重复，保留单一权威说明

目标：减少命令文件中重复的升级规则，让 `SKILL.md` + `docs/architecture.md` 成为权威解释层，命令文件只保留执行入口需要的最小规则。

#### 受影响文件

- `SKILL.md`
- `docs/architecture.md`
- `commands/tool-plan.md`
- `commands/tool-feat.md`
- `commands/tool-fix.md`
- `commands/tool-research.md`
- `commands/tool-update.md`
- `README.md`
- `README_zh.md`

#### 具体改动

- 把重复出现的 Caveman/RTK/CRG/GSD/OpenSpec 升级描述压缩为短规则，细节统一引用 `docs/architecture.md`。
- 保留每个命令自己的“何时用、何时升级”，删除与其他命令重复的大段背景解释。
- 让 `/tool-update` 的定位更像“平台入口”，不要与 `install.sh` 的首次安装叙事混在一起。
- 顺手修正 README 结构图与真实目录的偏差，至少不要遗漏重要目录或误导性简化。

#### 为什么

- 当前项目“看起来重”的一部分原因不是功能多，而是同一套规则在多个入口重复露出。
- 收掉重复后，维护也更轻，未来变更不会要同时改那么多文档。

### Phase 5: 用少量高价值测试锁住关键路径

目标：让前四阶段改动不靠人工记忆维持。

#### 受影响文件

- `tests/test_validation_scripts.py`
- 如有必要可新增：`tests/test_health_behaviors.py`

#### 具体改动

- 新增 `health.py` 行为测试：
  - `repair_claude_mem()` 是否生成正确 argv。
  - `repair_caveman()` 对 OpenCode / Claude 是否使用正确 target flag。
  - dry-run 模式是否只记录命令、不执行真实副作用。
- 新增 `sync.py` 行为测试：
  - 缺失文件与过期文件的比较结果是否正确。
  - 不再保留无效 `hooks` 分支。
- 仅在确实有价值时保留现有字符串断言；把低价值的“文案存在性测试”控制在必要范围。

#### 为什么

- 这些脚本一旦漂移，用户第一时间感知到的就是“安装坏了/修复没反应/文档说能做但实际上不行”。
- 高价值行为测试比继续堆文案断言更能保护项目。

## Implementation Steps

### 阶段一：可靠性快修

- 修改 `scripts/health.py` 中 argv 组装、runner 传递、dry-run 语义。
- 清理 `scripts/sync.py` 中死分支和无效接口。
- 更新 `commands/tool-update.md` 的边界说明。
- 补最小行为测试，优先覆盖本阶段修复点。

### 阶段二：scope 模型补齐

- 为 `health.py` 设计并实现 `--scope`。
- 对齐 `docs/install.md`、`commands/tool-update.md`、README 中的 scope 描述。
- 明确 local 支持矩阵，避免文档超前于实现。

### 阶段三：安装/更新职责收敛

- 收敛 `install.sh` 与 `health.py` 的组件术语、flag 语义和 repair 说明。
- 在文档中建立清晰的安装/检查/repair 矩阵。

### 阶段四：文档去重与产品表达压轻

- 精简重复的命令说明。
- 强化“路由器而不是重工作流集合”的表达。
- 修正 README 结构展示与实际仓库结构的偏差。

### 阶段五：回归保护

- 增补行为测试。
- 保持 CI 现有检查不退化，并让新增行为测试进入默认 `pytest`。

## Verification Steps

- Python 脚本基础验证：
  - `python3 -m py_compile scripts/*.py`
- 测试验证：
  - `pytest`
- 命令/文档一致性验证：
  - `python3 scripts/validate-command-schema.py`
  - `python3 scripts/validate-references.py`
  - `python3 scripts/validate-markdown-links.py`
- 安装器基础验证：
  - `bash -n install.sh`
  - `bash install.sh --minimal --dry-run`
  - `bash install.sh --recommended --dry-run`
  - `bash install.sh --full --dry-run`
- 验收标准：
  - `/tool-update` 的文档与底层脚本对 `target/scope/router/component` 的描述一致。
  - `health.py` 关键 repair 命令参数正确，可通过 dry-run/测试验证。
  - `sync.py` 不再保留明显死分支或未使用接口。
  - 新增测试覆盖真实行为，而不是只验证文案存在。
