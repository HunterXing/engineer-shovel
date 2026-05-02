# 🪖 工兵铲 · Engineer Shovel

**面向 OpenCode / Claude Code 的 token-aware AI 开发工作流路由器。**

它提供 10 个 `/tool-*` 指令，覆盖快速任务、Bug 修复、新功能、规划、重构、审查、头脑风暴、复杂项目、研究和 token 统计。新版将 `SKILL.md` 保持为轻量路由层，详细说明移动到 `docs/`，避免日常会话反复加载完整手册。

## 快速开始

```bash
# 默认 recommended：安装 skill、commands，并尽量 staging Caveman
curl -fsSL https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh | bash

# 最小安装：只安装 engineer-shovel skill 和命令
./install.sh --minimal

# 全量安装：ECC/GSD + superpowers + Caveman + RTK + engineer-shovel
./install.sh --full
```

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

`/tool-quick`、`/tool-fix`、`/tool-feat`、`/tool-plan`、`/tool-refactor`、`/tool-review`、`/tool-brainstorm`、`/tool-blueprint`、`/tool-research`、`/tool-statistic`。

## 文档

- 完整工作流：[`docs/workflows.md`](docs/workflows.md)
- Token 成本模型：[`docs/token-cost.md`](docs/token-cost.md)
- 安装模式：[`docs/install.md`](docs/install.md)
- 语言命令参考：[`docs/language-reference.md`](docs/language-reference.md)

## License

MIT — 详见 [LICENSE](LICENSE)。
