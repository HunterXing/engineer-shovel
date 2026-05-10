<h1 align="center">🪖 工兵铲 · Engineer Shovel</h1>

<p align="center">
  <b>面向 OpenCode / Claude Code 的 token-aware AI 开发工作流路由器。</b><br>
  <sub>快速任务 · Bug 修复 · 新功能 · 分支 · 规划 · 重构 · 审查 · 研究 · 代码图谱 · 同步</sub>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README_zh.md">简体中文</a> |
  <a href="README.ja-JP.md">日本語</a> |
  <a href="README.ko-KR.md">한국어</a>
</p>

<p align="center">
  <a href="https://github.com/HunterXing/engineer-shovel/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/HunterXing/engineer-shovel?style=flat-square"></a>
  <a href="https://github.com/HunterXing/engineer-shovel/forks"><img alt="GitHub forks" src="https://img.shields.io/github/forks/HunterXing/engineer-shovel?style=flat-square"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square"></a>
  <img alt="Commands" src="https://img.shields.io/badge/commands-10_active-5865F2?style=flat-square">
  <img alt="OpenCode" src="https://img.shields.io/badge/OpenCode-supported-2ea44f?style=flat-square">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-supported-6f42c1?style=flat-square">
</p>

---

Engineer Shovel 是一个面向 OpenCode / Claude Code 的轻量工作流路由器。

它提供一组小而明确的 `/tool-*` 指令处理日常开发，同时把 OpenSpec、ECC、GSD、Caveman、RTK、code-review-graph 等保留为按需升级的能力层。即使安装了完整能力，默认执行也应该尽量停留在轻量主路径。

运行时入口 `SKILL.md` 保持精简，长文档放在 `docs/`，避免日常会话反复加载完整手册。

## 如何选命令

| 如果任务是... | 使用 | 原因 |
|---|---|---|
| 明确的小改动 | `/tool-quick` | 1-2 文件低风险任务的最快路径 |
| Bug、回归、失败测试 | `/tool-fix` | 先复现，再定位、修复和验证 |
| 增加新行为 | `/tool-feat` | 做最小可验证功能切片 |
| 范围、顺序、验收不清 | `/tool-plan` | 先澄清再执行 |
| 审查本身就是任务 | `/tool-review` | 以 finding 为中心 |
| 决策前需要证据 | `/tool-research` | 收集本地、网页或深度证据 |
| 分支、图谱、更新维护 | `/tool-branch`、`/tool-graph`、`/tool-update` | 平台生命周期操作 |

## 默认形态

- 主工作流命令：`/tool-quick`、`/tool-fix`、`/tool-feat`、`/tool-plan`
- 工程辅助命令：`/tool-review`、`/tool-refactor`、`/tool-research`
- 平台辅助命令：`/tool-branch`、`/tool-graph`、`/tool-update`
- 核心原则：大多数任务应停留在主工作流层

`plan`、`review`、`research` 不是所有任务的必经前门；外部工具也不是默认仪式，而是遇到特定问题时才升级的能力层。

## 能力边界

Engineer Shovel 原生安装的是轻量路由器和 `/tool-*` 命令（10 个活跃 + 2 个兼容重定向）。完整工作流里更深的能力来自 recommended/full 模式安装或配置的可选外部工具：OpenSpec、ECC、GSD、superpowers、code-review-graph、Caveman 和 RTK。

Minimal 安装会刻意保持小而轻。如果某个流程提到 GSD、ECC、Caveman、RTK 或 code-review-graph 等外部能力，需要对应工具已经安装并处于健康状态。

即使在 `--full` 下，这些工具也应该被理解为职责明确的能力层：

- `code-review-graph`：代码理解与影响面分析
- `caveman`：对话压缩
- `rtk`：shell/tool 输出压缩
- `superpowers`：单任务澄清、调试、TDD 与验证纪律增强
- `ECC`：面向架构、安全、研究与集成权衡的专项能力指导
- `OpenSpec`：可持久化规格与任务
- `GSD`：跨阶段、多会话编排

如果任务涉及安全敏感路径，不应继续停留在常规路线，应提升到对应的 deep 路径，并在完成前补一个 `/tool-review --deep` 检查点。

## 快速开始

```bash
# 下载、检查、运行（默认：全量安装所有组件）
curl -fsSL -o install.sh https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh
less install.sh
bash install.sh

# 非交互安装：OpenCode 全量（默认）
bash install.sh --target opencode

# 非交互安装：同时安装到 OpenCode 和 Claude Code
bash install.sh --target all

# 如果你已经信任来源，也可以使用快捷方式：
# curl -fsSL https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh | bash

# 其他模式
./install.sh --target opencode --recommended  # 核心栈：Caveman、RTK、CRG、superpowers、OpenSpec
./install.sh --target opencode --minimal      # 只安装 Skill + 命令
./install.sh --target opencode --full --with-graph-build  # 同时构建初始 code-review-graph 索引
```

安装器会在 staging 可选依赖前校验外部仓库的 pinned SHA。相比直接 pipe 到 Bash，先下载再执行更安全，因为你可以检查脚本内容，也能避免服务端根据 pipe 场景返回不同内容。

## 兼容性说明

这轮优化保持了公开接口不变：

- `skill(name="engineer-shovel")` 不变。
- `/tool-*` 指令名称保持兼容；10 个活跃命令 + 2 个 legacy 重定向仍会安装。
- `--minimal`、`--recommended`、`--full`、`--dry-run` 不变。
- 新增 `--target opencode|claude|all|auto`，新机器可以明确选择安装到 OpenCode、Claude Code 或两者都装。

新增的 guardrail：

- 文档层面默认推荐“先下载、检查、再执行”。
- 安装器保留 SHA 校验，并对外部 installer 失败给出更清晰的边界。
- Python 校验脚本新增了轻量 pytest 回归测试。

会话中使用：

```text
skill(name="engineer-shovel")
```

或直接调用命令：

```text
/tool-quick --fast "修一个 README typo"
/tool-fix --standard "排查登录测试失败"
/tool-feat --standard "增加最小可验证功能切片"
/tool-plan --standard "规划 X 的落地顺序"
```

## 实际推荐路线

- 80% 任务：`/tool-quick`、`/tool-fix`、`/tool-feat`
- 15% 任务：`/tool-plan`、`/tool-review`、`/tool-research`
- 5% 任务：显式升级到 OpenSpec、ECC、GSD

这也是 `--full` 模式的目标体验：能力都在，但默认执行仍然应保持轻量。

### 工具适配速查

- `code-review-graph`：适合多文件理解、影响面分析、review context、重构；不适合每个微小改动都默认先查。
- `superpowers`：适合方法升级、TDD、系统化调试；不要把它当成所有任务的默认能力包。
- `ECC`：适合框架、安全、研究、外部集成深水区；不适合作为普通本地代码查找的默认入口。
- `OpenSpec`：适合需要落成 proposal/spec/tasks 文件的持久协议。
- `GSD`：适合阶段化、跨会话、多代理交付。
- `caveman` 与 `rtk`：属于压缩层，不替代规划、实现或代码理解职责。

## 安装与更新分工

- `install.sh`：首次安装、显式引导，以及 installer 自己负责的 repair hooks
- `/tool-update --check`：比较路由文件、检查组件健康，并区分漂移、可自动修复、受限阻塞、手动升级建议
- `/tool-update --full`：先同步路由文件，再执行支持的 repair，并重新校验健康状态
- `--scope global|local`：路由同步两者都支持；部分组件本质上仍是全局集成，会明确报告，不假装支持本地修复

## 成本模式

| 模式 | 适用场景 |
|---|---|
| `--fast` | 低风险、目标明确、小改动 |
| `--standard` | 普通开发任务；可选 OpenSpec 规格层；原生测试 + 轻量审查 |
| `--deep` | 高风险、跨模块、复杂研究、架构决策或 GSD 阶段编排 |

Caveman 建议按模式默认启用：`fast` 用 lite，`standard` 用 full，`deep` 用 full/ultra。RTK 如果已安装，则用于压缩 git、测试、构建、日志等 Bash/tool 输出；它不是模型回复压缩器，也不能替代 `Read`、`Grep`、`Glob` 这类内建文件工具。

## 指令

| 分组 | 指令 | 适用场景 |
|---|---|---|
| 主工作流 | `/tool-quick` | 明确、小改、低风险 |
| 主工作流 | `/tool-fix` | Bug、回归、失败测试 |
| 主工作流 | `/tool-feat` | 新功能、最小可验证实现 |
| 主工作流 | `/tool-plan` | 需求不清、顺序不清、验收不清 |
| 工程辅助 | `/tool-review` | 本地 diff、PR、交付前审查 |
| 工程辅助 | `/tool-refactor` | 行为保持不变的整理 |
| 工程辅助 | `/tool-research` | 决策前证据收集 |
| 平台辅助 | `/tool-branch` | 分支生命周期管理 |
| 平台辅助 | `/tool-graph` | code-review-graph 诊断 |
| 平台辅助 | `/tool-update` | 路由同步、组件健康、升级修复 |

> **v1.4.0**: `/tool-brainstorm` 已内化为 `/tool-feat` 和 `/tool-plan` 的 Phase 0；`/tool-blueprint` 已合并到 `/tool-plan --deep`。这两个命令文件保留重定向说明。

## 能力升级层

- `code-review-graph`：多文件代码理解与影响面分析
- `caveman`：对话压缩
- `rtk`：Bash/tool 输出压缩
- `OpenSpec`：持久化规格与任务
- `ECC`：架构、安全、框架、研究与集成指导
- `GSD`：里程碑、多阶段或跨会话编排

这些能力层各有职责。即使已经安装，也不意味着每个任务都要进入更重工作流。

## 文档

- 工具链架构：[`docs/architecture.md`](docs/architecture.md)
- 场景路由：[`docs/command-scenarios.md`](docs/command-scenarios.md)
- 模式路由图：[`docs/mode-routing.md`](docs/mode-routing.md)
- 安装与升级：[`docs/install.md`](docs/install.md)
- 依赖治理：[`docs/dependency-policy.md`](docs/dependency-policy.md)
- Token 成本：[`docs/token-cost.md`](docs/token-cost.md)
- 语言参考：[`docs/language-reference.md`](docs/language-reference.md)

## License

MIT — 详见 [LICENSE](LICENSE)。

## 上游工具版本

Engineer Shovel 在 `--full` 模式下会安装并配置这些上游工具。

| 工具 | 仓库 | 当前参考版本 | 作用 |
|---|---|---:|---|
| OpenSpec | https://github.com/Fission-AI/OpenSpec | latest | 规格驱动产物：proposal、specs、design、tasks、verify、archive |
| ECC | https://github.com/affaan-m/everything-claude-code | v1.10.0 | AI agent harness 性能系统：skills、rules、hooks、MCP、安全与 research-first 工作流 |
| GSD | https://github.com/gsd-build/get-shit-done | v1.39.0 | 深度项目编排、阶段执行、验证和上下文工程 |
| superpowers | https://github.com/obra/superpowers | v5.0.7 | 方法层：澄清、TDD、调试与验证纪律 |
| code-review-graph | https://github.com/tirth8205/code-review-graph | v2.3.2 | 本地代码知识图谱、MCP review context、影响面分析 |
| Caveman | https://github.com/JuliusBrussee/caveman | v1.7.0 | 输出 token 压缩、精简 review/commit、MCP shrink |
| RTK | https://github.com/rtk-ai/rtk | v0.38.0 | Shell/tool 输出压缩代理和命令 rewrite hooks |
