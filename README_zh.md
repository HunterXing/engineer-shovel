# 🪖 工兵铲 · Engineer Shovel

**面向 OpenCode / Claude Code 的 token-aware AI 开发工作流路由器。**

它提供 12 个 `/tool-*` 指令，覆盖快速任务、Bug 修复、新功能、分支工作流、规划、重构、审查、头脑风暴、复杂项目、研究、token 统计和同步更新。新版将 `SKILL.md` 保持为轻量路由层，详细说明移动到 `docs/`，避免日常会话反复加载完整手册。

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
./install.sh --target opencode --recommended  # Skill + 命令 + Caveman
./install.sh --target opencode --minimal      # 只安装 Skill + 命令
```

安装器会在 staging 可选依赖前校验外部仓库的 pinned SHA。相比直接 pipe 到 Bash，先下载再执行更安全，因为你可以检查脚本内容，也能避免服务端根据 pipe 场景返回不同内容。

## 兼容性说明

这轮优化保持了公开接口不变：

- `skill(name="engineer-shovel")` 不变。
- 12 个 `/tool-*` 指令名称不变。
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
/tool-statistic --fast
```

## 成本模式

| 模式 | 适用场景 |
|---|---|
| `--fast` | 低风险、目标明确、小改动 |
| `--standard` | 普通开发任务 |
| `--deep` | 高风险、跨模块、复杂研究或架构决策 |

Caveman 建议按模式默认启用：`fast` 用 lite，`standard` 用 full，`deep` 用 full/ultra。RTK 如果已安装，则用于压缩 git、测试、构建、日志等 Bash/tool 输出；它不是模型回复压缩器，而是工具输出压缩层。

## 指令

`/tool-quick`、`/tool-fix`、`/tool-feat`、`/tool-branch`、`/tool-plan`、`/tool-refactor`、`/tool-review`、`/tool-brainstorm`、`/tool-blueprint`、`/tool-research`、`/tool-statistic`、`/tool-update`。

## 文档

- 完整工作流：[`docs/workflows.md`](docs/workflows.md)
- Token 成本模型：[`docs/token-cost.md`](docs/token-cost.md)
- 安装模式：[`docs/install.md`](docs/install.md)
- 语言命令参考：[`docs/language-reference.md`](docs/language-reference.md)
- 仓库评估报告：[`docs/assessment.md`](docs/assessment.md)

## License

MIT — 详见 [LICENSE](LICENSE)。
