# 工具选型决策树

此文档被 `/tool-*` 命令引用，用于在 L5 (Superpowers) 和 L6 (GSD) 之间消除重叠。

## 决策树 1: 方向澄清 (已内化到 feat/plan)

```
想法不明确 → feat/plan 自动检测，进入 Phase 0
├── "做什么"不明确 → L6: gsd-explore
│   (产品方向、用户故事、功能边界不清)
│   产出: CONTEXT.md
│
├── "怎么做"不明确 → L5: superpowers:brainstorming
│   (技术方案、架构选型、API 设计不清)
│   产出: design doc + spec
│
└── 多方案架构决策 → L6: ecc:council
    (go/no-go、架构选型、高风险权衡)
    产出: structured decision record
```

应用于: tool-feat Phase 0, tool-plan Phase 0

## 决策树 2: Bug 调试

```
Bug 出现
├── 已知文件/函数，明显原因 → tool-fix --fast
│   直接修复 + 定向测试
│
├── 可复现，局部范围 → tool-fix --standard
│   L2: code-review-graph trace + impact
│   L5: superpowers:systematic-debug
│
└── 跨模块、flaky、安全相关 → tool-fix --deep
    L4: ecc:deep-research (新领域/flaky溯源)
    L6: gsd-debug (checkpoint 持久化)
    L5: systematic-debugging (4阶段科学方法)
    L4: ECC security-review (安全路径)
```

应用于: tool-fix

## 决策树 3: 复杂项目 (plan --deep 自动分类)

```
需求 >3 PR，多会话
├── 代码层多 PR → L4: ecc:blueprint (依赖图)
│   + L5: superpowers:writing-plans (详细计划)
│
├── 里程碑级别 → L6: GSD project
│   (discuss→plan→execute 阶段循环)
│
└── 系统架构变更 → L6: ecc:council (go/no-go)
```

应用于: tool-plan --deep (原 /tool-blueprint 已合并)

## 决策树 4: 安全扫描

```
代码变更涉及 auth/input/secrets/network/SQL
├── 轻量扫描 → L4: ecc:security-review
├── 深度审计 → L4: ecc:security-scan
└── 赏金级别 → security-bounty-hunter
```

应用于: 所有命令的安全门
