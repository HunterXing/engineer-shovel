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

它提供 `/tool-*` 指令，覆盖快速任务、Bug 修复、新功能、分支工作流、规划、重构、审查、研究、代码图谱诊断和同步更新。新版将 `SKILL.md` 保持为轻量路由层，详细说明移动到 `docs/`，避免日常会话反复加载完整手册。

## 能力边界

Engineer Shovel 原生安装的是轻量路由器和 `/tool-*` 命令（10 个活跃 + 2 个兼容重定向）。完整工作流里更深的能力来自 recommended/full 模式安装或配置的可选外部工具：OpenSpec、ECC、GSD、superpowers、code-review-graph、Caveman 和 RTK。

Minimal 安装会刻意保持小而轻。如果某个流程提到 GSD、ECC、Caveman、RTK 或 code-review-graph 等外部能力，需要对应工具已经安装并处于健康状态。

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
/tool-review --fast
/tool-research --deep "比较 X 的方案"
/tool-graph update
```

## 成本模式

| 模式 | 适用场景 |
|---|---|
| `--fast` | 低风险、目标明确、小改动 |
| `--standard` | 普通开发任务；可选 OpenSpec 规格层；原生测试 + 轻量审查 |
| `--deep` | 高风险、跨模块、复杂研究、架构决策或 GSD 阶段编排 |

Caveman 建议按模式默认启用：`fast` 用 lite，`standard` 用 full，`deep` 用 full/ultra。RTK 如果已安装，则用于压缩 git、测试、构建、日志等 Bash/tool 输出；它不是模型回复压缩器，而是工具输出压缩层。

## 指令

`/tool-quick`、`/tool-fix`、`/tool-feat`、`/tool-branch`、`/tool-plan`、`/tool-refactor`、`/tool-review`、`/tool-research`、`/tool-graph`、`/tool-update`。

> **v1.4.0**: `/tool-brainstorm` 已内化为 `/tool-feat` 和 `/tool-plan` 的 Phase 0；`/tool-blueprint` 已合并到 `/tool-plan --deep`。这两个命令文件保留重定向说明。

## 文档

- 工具链架构：[`docs/architecture.md`](docs/architecture.md)

## License

MIT — 详见 [LICENSE](LICENSE)。

## 上游工具版本

Engineer Shovel 在 `--full` 模式下会安装并配置这些上游工具。

| 工具 | 仓库 | 当前参考版本 | 作用 |
|---|---|---:|---|
| OpenSpec | https://github.com/Fission-AI/OpenSpec | latest | 规格驱动产物：proposal、specs、design、tasks、verify、archive |
| ECC | https://github.com/affaan-m/everything-claude-code | v1.10.0 | AI agent harness 性能系统：skills、rules、hooks、MCP、安全与 research-first 工作流 |
| GSD | https://github.com/gsd-build/get-shit-done | v1.39.0 | 深度项目编排、阶段执行、验证和上下文工程 |
| superpowers | https://github.com/obra/superpowers | v5.0.7 | 强制技能工作流：brainstorming、TDD、planning、review、branch finishing |
| code-review-graph | https://github.com/tirth8205/code-review-graph | v2.3.2 | 本地代码知识图谱、MCP review context、影响面分析 |
| Caveman | https://github.com/JuliusBrussee/caveman | v1.7.0 | 输出 token 压缩、精简 review/commit、MCP shrink |
| RTK | https://github.com/rtk-ai/rtk | v0.38.0 | Shell/tool 输出压缩代理和命令 rewrite hooks |
