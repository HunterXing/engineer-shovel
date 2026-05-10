/* ================================================
   ENGINEER SHOVEL — GITHUB PAGES JAVASCRIPT
   v1.7.2 · Mode tabs · CRG-aware · claude-mem · OpenSpec-aware
   ================================================ */

const i18n = {
  en: {
    'hero.badge': 'v1.7.2 · MIT License',
    'hero.subtitle': 'Lightweight AI development workflow router for OpenCode / Claude Code',
    'hero.desc': 'Start with the main workflow commands. Keep review, research, and external tooling as deliberate upgrades instead of mandatory ceremony.',
    'hero.note': 'Default route: quick / fix / feat / plan. Support routes: review / refactor / research. Platform routes: branch / graph / update.',
    'picker.title': 'Choose Your Route',
    'picker.sub': 'Keep the README command table for quick reading. Use this visual picker on the site when you want a faster route into the right command.',
    'picker.quick.label': 'Small obvious edit',
    'picker.quick.desc': 'Typos, tiny config edits, 1-2 file surgical changes.',
    'picker.fix.label': 'Bug or regression',
    'picker.fix.desc': 'Broken behavior, failing tests, logs, or regressions.',
    'picker.feat.label': 'New behavior to build',
    'picker.feat.desc': 'Add the smallest verifiable feature slice once the goal is clear.',
    'picker.plan.label': 'Scope or order unclear',
    'picker.plan.desc': 'Use when execution is blocked by unclear scope, ownership, order, or acceptance.',
    'picker.review.label': 'Review is the task',
    'picker.review.desc': 'Use when you need findings on a diff, PR, or implementation.',
    'picker.research.label': 'Decision needs evidence',
    'picker.research.desc': 'Gather local, web, or deep evidence before planning or implementation.',
    'picker.note': 'Platform operations still live in `/tool-branch`, `/tool-graph`, and `/tool-update`.',
    'commands.sub': 'Choose commands by task type first. Main workflow commands handle most work; support and platform commands appear only when needed.',
    'modes.note': 'Special case: `/tool-research` uses `--quick / --web / --deep` because it routes by evidence source and research depth, not the main execution-cost axis.',
    'copy': 'Copy',
    'copied': 'copied',
    'wf.close': 'Close'
  },
  zh: {
    'nav.commands': '命令',
    'nav.modes': '成本模式',
    'nav.start': '快速开始',
    'nav.upstream': '上游工具',
    'hero.btn.start': '快速开始',
    'hero.btn.commands': '查看命令',
    'hero.stats.commands': '命令',
    'hero.stats.tools': '上游工具',
    'hero.stats.modes': '安装模式',
    'hero.stats.langs': '语言文档',
    'hero.scroll': '向下滚动探索',
    'hero.badge': 'v1.7.2 · MIT License',
    'hero.subtitle': '面向 OpenCode / Claude Code 的轻量 AI 开发工作流路由器',
    'hero.desc': '先走主工作流命令。把 review、research 和外部工具保留为按需升级，而不是默认仪式。',
    'hero.note': '默认路线：quick / fix / feat / plan。辅助路线：review / refactor / research。平台路线：branch / graph / update。',
    'picker.title': '怎么选命令',
    'picker.sub': 'README 里继续保留文本版命令选择表；页面这里额外提供一个可视化快速入口。',
    'picker.quick.label': '明确的小改动',
    'picker.quick.desc': 'Typo、小配置修改、1-2 文件手术式改动。',
    'picker.fix.label': 'Bug 或回归',
    'picker.fix.desc': '行为异常、失败测试、日志报错或回归问题。',
    'picker.feat.label': '要新增行为',
    'picker.feat.desc': '当目标已经清楚时，做最小可验证功能切片。',
    'picker.plan.label': '范围或顺序不清',
    'picker.plan.desc': '当执行被范围、归属、顺序或验收不清阻塞时使用。',
    'picker.review.label': '审查本身是任务',
    'picker.review.desc': '当你需要针对 diff、PR 或实现结果产出问题列表时使用。',
    'picker.research.label': '决策前需要证据',
    'picker.research.desc': '在规划或实现前，收集本地、网页或深度证据。',
    'picker.note': '平台类操作仍然在 `/tool-branch`、`/tool-graph`、`/tool-update`。',
    'commands.title': '10 个命令',
    'commands.sub': '先按任务类型选命令。大多数工作停留在主工作流层；辅助命令和平台命令只在需要时出现。',
    'modes.title': '成本模式',
    'modes.sub': '根据任务复杂度选择对应模式，默认选择能验证结果的最低成本路径。',
    'modes.note': '特例：`/tool-research` 使用 `--quick / --web / --deep`，表达的是证据来源与研究深度，而不是主工作流的执行成本轴。',
    'modes.fast.title': '低风险 · 明确目标',
    'modes.fast.1': 'Typo 修复 / 配置修改',
    'modes.fast.2': '1-2 文件手术编辑',
    'modes.fast.3': '已知位置的小改动',
    'modes.standard.title': '常规开发任务',
    'modes.standard.1': '新功能实现 (可选 OpenSpec)',
    'modes.standard.2': '可复现 Bug 修复',
    'modes.standard.3': '中等重构 / PR review',
    'modes.deep.title': '高风险 · 跨系统 · 模糊',
    'modes.deep.1': '架构决策 / 跨模块',
    'modes.deep.2': '深度研究 / 复杂调试',
    'modes.deep.3': 'OpenSpec / 文件化计划 / GSD 阶段编排',
    'start.title': '快速开始',
    'start.sub': '下载 → 检查 → 运行，三步完成安装。',
    'start.step1.title': '下载安装脚本',
    'start.step1.desc': '先下载、检查内容，再执行。默认全量安装所有组件。',
    'start.step2.title': '选择安装模式',
    'start.step2.desc': '支持 OpenCode / Claude Code。recommended 安装核心栈；full 额外安装 ECC 和 GSD。',
    'start.step3.title': '开始使用',
    'start.step3.desc': '在会话中加载技能或直接调用命令。优先使用主工作流命令，再按需进入辅助或平台路线。',
    'upstream.title': '上游工具',
    'upstream.sub': 'recommended 安装核心栈；full 额外加入 ECC 和 GSD 做深度编排。',
    'upstream.col.tool': '工具',
    'upstream.col.ver': '版本',
    'upstream.col.role': '作用',
    'upstream.openspec': '规格驱动产物：proposal、specs、design、tasks、verify、archive。只安装 CLI，不自动初始化项目。',
    'upstream.ecc': '按需能力库：skills、rules、hooks、MCP、安全与 research-first 工作流 (L4)',
    'upstream.gsd': '深度项目编排：阶段执行、结构化验证闭环 (verify-work / code-review / ship) (L5)',
    'upstream.sp': '方法层：澄清、TDD、调试与验证纪律 (L3)',
    'upstream.crg': '本地代码知识图谱、MCP review context、影响面分析 (L2, auto-refreshed)',
    'upstream.cmem': '自动捕获跨会话记忆: 决策、偏好、bug 历史。渐进式披露。SQLite + Chroma 双存储 (L1.5)',
    'upstream.caveman': 'LLM 输出 token 压缩 (lite/full/ultra 三模式强制映射) (L1)',
    'upstream.rtk': 'Shell/tool 输出压缩代理，智能触发策略 (输出 >500 行) (L1)',
    'boundary.title': '能力边界',
    'boundary.core.title': '原生安装（最小模式）',
    'boundary.core.desc': 'Engineer Shovel 原生安装的是轻量路由器、10 个活跃 /tool-* 命令和 legacy 重定向。',
    'boundary.core.1': '轻量级 SKILL.md 路由层',
    'boundary.core.2': '10 个活跃 /tool-* 命令',
    'boundary.core.3': 'install.sh 安装脚本',
    'boundary.ext.title': '可选外部工具（recommended / full 模式）',
    'boundary.ext.desc': '推荐/完整工作流里更深的能力来自 recommended / full 模式安装或配置的可选外部工具。',
    'footer.docs': '文档',
    'footer.install': '安装',
    'footer.cost': '成本模型',
    'copy': '复制',
    'copied': '已复制',
    'wf.close': '关闭',
    'wf.mode.fast': '快速',
    'wf.mode.standard': '标准',
    'wf.mode.deep': '深度',
    'wf.mode.quick': '快速',
    'wf.mode.web': '网页',
    'wf.mode.check': '检查',
    'wf.mode.full': '完整',
    'wf.deprecated': '已废弃'
  }
};

let currentLang = 'en';

function captureOriginalText() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.dataset.i18nOriginal = el.textContent.trim();
  });
}

function setLanguage(lang) {
  currentLang = lang;
  document.documentElement.lang = lang;
  localStorage.setItem('es-pages-lang', lang);
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    if (i18n[lang] && i18n[lang].hasOwnProperty(key)) {
      el.textContent = i18n[lang][key];
    } else if (lang === 'en' && el.dataset.i18nOriginal) {
      el.textContent = el.dataset.i18nOriginal;
    }
  });
  document.querySelectorAll('.copy-btn').forEach(btn => {
    const isCopied = btn.classList.contains('copied');
    btn.textContent = isCopied
      ? (i18n[lang]['copied'] !== undefined ? i18n[lang]['copied'] : 'copied')
      : (i18n[lang]['copy'] !== undefined ? i18n[lang]['copy'] : 'Copy');
  });
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
  renderCommands();
}

function initLanguageToggle() {
  captureOriginalText();
  const saved = localStorage.getItem('es-pages-lang') || 'en';
  setLanguage(saved);
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => setLanguage(btn.dataset.lang));
  });
}

function initRoutePicker() {
  document.querySelectorAll('.route-card[data-command]').forEach(card => {
    card.addEventListener('click', () => {
      const name = card.dataset.command;
      const cmd = commands.find(item => item.name === name);
      if (cmd) openWorkflowModal(cmd);
    });
  });
}

// ---- Command Data ---- (10 active, no deprecated)
const commands = [
  { name: '/tool-feat',     color: '#4f8ef7', key: 'cmd.feat',     tag: 'Medium',   modes: ['--fast','--standard','--deep'], defaultMode: '--standard' },
  { name: '/tool-quick',    color: '#3dd590', key: 'cmd.quick',    tag: 'Low',      modes: ['--fast','--standard'],            defaultMode: '--fast' },
  { name: '/tool-fix',      color: '#f56f6f', key: 'cmd.fix',      tag: 'Low→High', modes: ['--fast','--standard','--deep'], defaultMode: '--standard' },
  { name: '/tool-branch',   color: '#9b6dff', key: 'cmd.branch',   tag: 'Low',      subcommands: ['create','status','review','merge','abort'], defaultMode: 'review' },
  { name: '/tool-plan',     color: '#f5a84f', key: 'cmd.plan',     tag: 'Medium',   modes: ['--fast','--standard','--deep'], defaultMode: '--standard' },
  { name: '/tool-refactor', color: '#3dd6f5', key: 'cmd.refactor', tag: 'Medium',   modes: ['--fast','--standard','--deep'], defaultMode: '--standard' },
  { name: '/tool-review',   color: '#4f8ef7', key: 'cmd.review',   tag: 'Low→High', modes: ['--fast','--standard','--deep'], defaultMode: '--standard' },
  { name: '/tool-research', color: '#3dd6f5', key: 'cmd.research', tag: 'Low→High', modes: ['--quick','--web','--deep'],       defaultMode: '--quick' },
  { name: '/tool-graph',    color: '#3dd590', key: 'cmd.graph',    tag: 'Low',      subcommands: ['status','build','update','rebuild','watch'], defaultMode: 'status' },
  { name: '/tool-update',   color: '#4f8ef7', key: 'cmd.update',   tag: 'Low',      modes: ['--check','--full'],               defaultMode: '--check' }
];

const commandLabels = {
  'cmd.quick': {
    en: { usefor: 'Typos, config edits, 1-2 file surgical changes', modes: ['--fast (direct edit)', '--standard (edit + test + review)'] },
    zh: { usefor: 'Typo 修复、配置修改、1-2 文件手术编辑', modes: ['--fast (直接编辑)', '--standard (编辑+测试+审查)'] }
  },
  'cmd.fix': {
    en: { usefor: 'Bugs, failing tests, regressions — prove root cause', modes: ['--fast (known location)', '--standard (CRG trace)', '--deep (debug pipeline)'] },
    zh: { usefor: 'Bug 修复、失败测试、回归 — 证明根因', modes: ['--fast (已知位置)', '--standard (CRG 追踪)', '--deep (调试管线)'] }
  },
  'cmd.feat': {
    en: { usefor: 'New behavior that is already clear enough to implement', modes: ['--fast (small, known)', '--standard (native build + light review)', '--deep (spec/verify→review→ship)'] },
    zh: { usefor: '已经清楚要做什么时的新功能实现', modes: ['--fast (小型/已知)', '--standard (原生验证 + 轻审查)', '--deep (规格/验证→审查→发布)'] }
  },
  'cmd.branch': {
    en: { usefor: 'Branch lifecycle: create, review, merge, abort', modes: ['create', 'status', 'review (CRG)', 'merge', 'abort'] },
    zh: { usefor: '分支生命周期：创建、审查、合并、放弃', modes: ['create', 'status', 'review (含 CRG)', 'merge', 'abort'] }
  },
  'cmd.plan': {
    en: { usefor: 'Use when scope, order, ownership, or acceptance is still unclear', modes: ['--fast (inline)', '--standard (execution plan)', '--deep (spec/milestone)'] },
    zh: { usefor: '范围、顺序、归属或验收仍不清楚时使用', modes: ['--fast (内联)', '--standard (执行计划)', '--deep (规格/里程碑)'] }
  },
  'cmd.refactor': {
    en: { usefor: 'Behavior-preserving cleanup with before/after verification', modes: ['--fast (1-2 files)', '--standard (CRG impact)', '--deep (plan first)'] },
    zh: { usefor: '行为保持不变的重构，含前后验证', modes: ['--fast (1-2 文件)', '--standard (CRG 影响)', '--deep (先规划)'] }
  },
  'cmd.review': {
    en: { usefor: 'Use when review itself is the task', modes: ['--fast (compressed sanity check)', '--standard (CRG+findings)', '--deep (security+deep review)'] },
    zh: { usefor: '当审查本身就是任务时使用', modes: ['--fast (压缩 sanity check)', '--standard (CRG+发现问题)', '--deep (安全+深度审查)'] }
  },
  'cmd.research': {
    en: { usefor: 'Gather evidence for a specific decision before planning or implementation', modes: ['--quick (local+CRG)', '--web (docs/search)', '--deep (multi-source)'] },
    zh: { usefor: '在规划或实现前，为具体决策收集证据', modes: ['--quick (本地+CRG)', '--web (文档/搜索)', '--deep (多源)'] }
  },
  'cmd.graph': {
    en: { usefor: 'code-review-graph diagnostics (auto-refreshed via git hooks)', modes: ['status', 'build', 'update', 'rebuild', 'watch'] },
    zh: { usefor: 'code-review-graph 诊断 (git hook 自动刷新)', modes: ['status', 'build', 'update', 'rebuild', 'watch'] }
  },
  'cmd.update': {
    en: { usefor: 'Sync and update engineer-shovel installation', modes: ['--check (read-only)', '--full (update + repair)'] },
    zh: { usefor: '同步和更新 engineer-shovel 安装', modes: ['--check (只读)', '--full (更新+修复)'] }
  }
};

// ---- Mode-specific Workflow Data ----
const commandWorkflows = {
  '/tool-quick': {
    tag: 'Low',
    sub: { en: 'Obvious, low-risk work. No planning, no deep research.', zh: '明显、低风险的工作。不规划、不深度研究。' },
    tools: { en: 'Tools: CRG semantic_search_nodes / query_graph', zh: '工具: CRG semantic_search_nodes / query_graph' },
    modes: {
      '--fast': {
        label: { en: 'Direct edit', zh: '直接编辑' },
        steps: [
          { phase: '01', label: { en: 'CRG Locate', zh: 'CRG 定位' },
            desc: { en: 'semantic_search_nodes(query="target") — confirm file/symbol', zh: 'semantic_search_nodes(query="目标") — 确认文件/符号' },
            tools: ['CRG'] },
          { phase: '02', label: { en: 'Edit', zh: '编辑' },
            desc: { en: 'Smallest safe change. No refactoring.', zh: '最小的安全改动。不重构。' },
            tools: [] },
          { phase: '03', label: { en: 'Verify', zh: '验证' },
            desc: { en: 'Run nearest verification: lint/test/build. Skip RTK for small output.', zh: '运行最近的验证: lint/单测/构建。小输出跳过 RTK。' },
            tools: ['RTK (large)'] },
          { phase: '04', label: { en: 'Report', zh: '报告' },
            desc: { en: 'Report what changed and what was verified.', zh: '报告变更内容和验证结果。' },
            tools: [] }
        ]
      },
      '--standard': {
        label: { en: 'Tested edit', zh: '测试编辑' },
        steps: [
          { phase: '01', label: { en: 'CRG Context', zh: 'CRG 上下文' },
            desc: { en: 'semantic_search_nodes / query_graph(imports_of="file") — use project patterns and language-reference only as needed.', zh: 'semantic_search_nodes / query_graph(imports_of="文件") — 仅在需要时参考项目模式和 language-reference。' },
            tools: ['CRG'] },
          { phase: '02', label: { en: 'Edit', zh: '编辑' },
            desc: { en: 'Targeted surgical change. Preserve project style.', zh: '定向手术编辑。保持项目风格。' },
            tools: [] },
          { phase: '03', label: { en: 'Test', zh: '测试' },
            desc: { en: 'Run tests/build. Wrap large output with rtk gain.', zh: '运行测试/构建。大输出用 rtk gain 压缩。' },
            tools: ['RTK'] },
          { phase: '04', label: { en: 'Review', zh: '审查' },
            desc: { en: '/tool-review --fast or Caveman-compressed sanity check → report.', zh: '/tool-review --fast 或 Caveman 压缩 sanity check → 报告。' },
            tools: ['Caveman'] }
        ]
      }
    }
  },
  '/tool-fix': {
    tag: 'Low→High',
    sub: { en: 'Broken behavior, failing tests, regressions. Find root cause, prove fix.', zh: '行为异常、测试失败、回归。找到根因，证明修复。' },
    tools: { en: 'Tools: CRG trace pipeline · native regression verification · Caveman review', zh: '工具: CRG 追踪管线 · 原生回归验证 · Caveman 审查' },
    modes: {
      '--fast': {
        label: { en: 'Quick fix', zh: '快速修复' },
        steps: [
          { phase: '01', label: { en: 'Locate', zh: '定位' },
            desc: { en: 'semantic_search_nodes(query="failing_fn") — confirm location', zh: 'semantic_search_nodes(query="失败函数") — 确认位置' },
            tools: ['CRG'] },
          { phase: '02', label: { en: 'Fix', zh: '修复' },
            desc: { en: 'Apply surgical fix directly.', zh: '直接进行手术修复。' },
            tools: [] },
          { phase: '03', label: { en: 'Test', zh: '测试' },
            desc: { en: 'Run targeted test. Report done.', zh: '运行定向测试。报告完成。' },
            tools: [] }
        ]
      },
      '--standard': {
        label: { en: 'Trace + verify', zh: '追踪 + 验证' },
        steps: [
          { phase: '01', label: { en: 'Reproduce', zh: '复现' },
            desc: { en: 'Identify failing assertion/log entry point.', zh: '确认失败的断言/日志入口。' },
            tools: [] },
          { phase: '02', label: { en: 'CRG Trace', zh: 'CRG 追踪' },
            desc: { en: 'semantic_search_nodes → get_affected_flows → query_graph(callers_of, depth=2)', zh: 'semantic_search_nodes → get_affected_flows → query_graph(callers_of, depth=2)' },
            tools: ['CRG'] },
          { phase: '03', label: { en: 'Impact', zh: '影响分析' },
            desc: { en: 'get_impact_radius(target="root") → check blast radius before fix.', zh: 'get_impact_radius(target="根因") → 修复前检查影响范围。' },
            tools: ['CRG'] },
          { phase: '04', label: { en: 'Fix + Test', zh: '修复+测试' },
            desc: { en: 'Surgical fix. Run failing test → related tests. rtk gain for large output.', zh: '手术修复。运行失败测试 → 相关测试。大输出用 rtk gain。' },
            tools: ['RTK'] },
          { phase: '05', label: { en: 'Coverage', zh: '覆盖率' },
            desc: { en: 'query_graph(tests_for="fixed_node") — verify test coverage.', zh: 'query_graph(tests_for="修复节点") — 验证测试覆盖。' },
            tools: ['CRG'] },
          { phase: '06', label: { en: 'Regression Verify', zh: '回归验证' },
            desc: { en: 'Re-run failing test first, then related regression tests/build.', zh: '先重跑失败测试，再跑相关回归测试/构建。' },
            tools: [] },
          { phase: '07', label: { en: 'Review', zh: '审查' },
            desc: { en: '/tool-review --fast or Caveman-compressed sanity check → offer /caveman-commit (no auto-commit).', zh: '/tool-review --fast 或 Caveman 压缩 sanity check → 提示 /caveman-commit (不自动提交)。' },
            tools: ['Caveman'] }
        ]
      },
      '--deep': {
        label: { en: 'Full pipeline', zh: '完整管线' },
        steps: [
          { phase: '01', label: { en: 'CRG Trace', zh: 'CRG 追踪' },
            desc: { en: 'Full CRG trace pipeline (same as standard).', zh: '完整 CRG 追踪管线 (同 standard)。' },
            tools: ['CRG'] },
          { phase: '02', label: { en: 'Add Method Layer', zh: '增加方法层' },
            desc: { en: 'Only when reproduction or root cause remains unclear: add deeper research, systematic debugging, or cross-session debugging deliberately.', zh: '仅当复现或根因仍不清楚时，按需增加深研究、系统调试或跨会话调试。' },
            tools: ['ECC', 'Superpowers', 'GSD'] },
          { phase: '03', label: { en: 'Security Route', zh: '安全路线' },
            desc: { en: 'If auth, input, filesystem, network, secrets, cookies, or SQL are involved, add /tool-review --deep before sign-off.', zh: '如果涉及 auth、输入、文件系统、网络、secrets、cookies 或 SQL，完成前补 /tool-review --deep。' },
            tools: [] },
          { phase: '04', label: { en: 'GSD Verify', zh: 'GSD 验证' },
            desc: { en: 'skill(gsd-verify-work) — structured acceptance.', zh: 'skill(gsd-verify-work) — 结构化验收。' },
            tools: ['GSD'] },
          { phase: '05', label: { en: 'GSD Review', zh: 'GSD 审查' },
            desc: { en: 'skill(gsd-code-review) → severity-classified findings.', zh: 'skill(gsd-code-review) → 严重度分级审查。' },
            tools: ['GSD'] },
          { phase: '06', label: { en: 'GSD Ship', zh: 'GSD 发布' },
            desc: { en: 'skill(gsd-ship) → create PR, run gates, prepare merge.', zh: 'skill(gsd-ship) → 创建 PR，运行门控，准备合并。' },
            tools: ['GSD'] }
        ]
      }
    }
  },
  '/tool-feat': {
    tag: 'Medium',
    sub: { en: 'Implement the smallest verifiable feature slice once the target behavior is already clear.', zh: '当目标行为已经清楚时，实现最小可验证功能切片。' },
    tools: { en: 'Tools: CRG explore · optional OpenSpec · caveman-stats · light review', zh: '工具: CRG 探索 · 可选 OpenSpec · caveman-stats · 轻量审查' },
    modes: {
      '--fast': {
        label: { en: 'Small feature', zh: '小功能' },
        steps: [
          { phase: '00', label: { en: 'Baseline', zh: '基线' },
            desc: { en: '/caveman-stats — token baseline. Check not on main → /tool-branch create.', zh: '/caveman-stats — token 基线。检查不在 main → /tool-branch create。' },
            tools: ['Caveman'] },
          { phase: '01', label: { en: 'CRG Explore', zh: 'CRG 探索' },
            desc: { en: 'semantic_search_nodes(query="pattern") — confirm existing patterns.', zh: 'semantic_search_nodes(query="模式") — 确认现有模式。' },
            tools: ['CRG'] },
          { phase: '02', label: { en: 'Implement', zh: '实现' },
            desc: { en: 'Use project conventions. No new patterns unless necessary.', zh: '使用项目规范。非必要不引入新模式。' },
            tools: [] },
          { phase: '03', label: { en: 'Test', zh: '测试' },
            desc: { en: 'Run tests/build → /caveman-stats report.', zh: '运行测试/构建 → /caveman-stats 报告。' },
            tools: ['Caveman'] }
        ]
      },
      '--standard': {
        label: { en: 'Normal feature', zh: '常规功能' },
        steps: [
          { phase: '00', label: { en: 'Baseline', zh: '基线' },
            desc: { en: 'caveman-stats + branch check.', zh: 'caveman-stats + 分支检查。' },
            tools: ['Caveman'] },
          { phase: '01', label: { en: 'CRG Explore', zh: 'CRG 探索' },
            desc: { en: 'Targeted CRG context: semantic_search_nodes + query_graph(imports_of). Use architecture overview only if boundaries are unclear.', zh: '定向 CRG 上下文: semantic_search_nodes + query_graph(imports_of)。边界不清时才用架构概览。' },
            tools: ['CRG', 'ECC'] },
          { phase: '02', label: { en: 'Route Back If Needed', zh: '必要时回退' },
            desc: { en: 'If requirements remain unclear after exploration, stop and route to /tool-plan or /tool-research.', zh: '如果探索后需求仍不清楚，停止实现并回退到 /tool-plan 或 /tool-research。' },
            tools: [] },
          { phase: '03', label: { en: 'Implement', zh: '实现' },
            desc: { en: 'Search existing patterns first. Implement with project conventions.', zh: '先搜索现有模式。按项目规范实现。' },
            tools: [] },
          { phase: '04', label: { en: 'Test', zh: '测试' },
            desc: { en: 'Tests/build. rtk gain for large output. /caveman-stats report.', zh: '测试/构建。大输出用 rtk gain。/caveman-stats 报告。' },
            tools: ['RTK', 'Caveman'] },
          { phase: '05', label: { en: 'Light Review', zh: '轻量审查' },
            desc: { en: '/tool-review --fast or Caveman-compressed sanity check. Offer /caveman-commit, no auto-commit.', zh: '/tool-review --fast 或 Caveman 压缩 sanity check。提示 /caveman-commit，不自动提交。' },
            tools: ['Caveman'] }
        ]
      },
      '--deep': {
        label: { en: 'Major feature', zh: '重大功能' },
        steps: [
          { phase: '00', label: { en: 'Baseline', zh: '基线' },
            desc: { en: 'caveman-stats + branch check.', zh: 'caveman-stats + 分支检查。' },
            tools: ['Caveman'] },
          { phase: '01', label: { en: 'Plan First', zh: '先规划' },
            desc: { en: 'If the feature is still decision-heavy, route through /tool-plan or /tool-research before implementation.', zh: '如果功能仍需要做高影响决策，先经过 /tool-plan 或 /tool-research 再实现。' },
            tools: ['ECC'] },
          { phase: '02', label: { en: 'Spec + Plan', zh: '规格 + 规划' },
            desc: { en: 'Use OpenSpec or a file-backed plan only when durable agreement improves execution.', zh: '只有在持久化共识确实能提高执行质量时，才使用 OpenSpec 或文件化计划。' },
            tools: ['OpenSpec', 'CRG'] },
          { phase: '03', label: { en: 'Implement', zh: '实现' },
            desc: { en: 'Follow plan. Surgical changes per step.', zh: '按计划执行。每步手术改动。' },
            tools: [] },
          { phase: '04', label: { en: 'Test', zh: '测试' },
            desc: { en: 'rtk gain for full suite. /caveman-stats report.', zh: '全量套件用 rtk gain。/caveman-stats 报告。' },
            tools: ['RTK', 'Caveman'] },
          { phase: '05', label: { en: 'GSD Verify', zh: 'GSD 验收' },
            desc: { en: 'skill(gsd-verify-work) — structured acceptance against plan.', zh: 'skill(gsd-verify-work) — 对照计划的结构化验收。' },
            tools: ['GSD'] },
          { phase: '06', label: { en: 'GSD Review', zh: 'GSD 审查' },
            desc: { en: 'skill(gsd-code-review) → severity-classified findings.', zh: 'skill(gsd-code-review) → 严重度分级审查。' },
            tools: ['GSD'] },
          { phase: '07', label: { en: 'GSD Ship', zh: 'GSD 发布' },
            desc: { en: 'skill(gsd-ship) → create PR, run gates, prepare merge.', zh: 'skill(gsd-ship) → 创建 PR，运行门控，准备合并。' },
            tools: ['GSD'] }
        ]
      }
    }
  },
  '/tool-branch': {
    tag: 'Low',
    sub: { en: 'Feature branch lifecycle with auto-detection and CRG review.', zh: '功能分支生命周期，自动检测类型 + CRG 审查。' },
    tools: { en: 'Tools: CRG detect_changes · caveman-commit', zh: '工具: CRG detect_changes · caveman-commit' },
    subcommands: {
      'create': {
        label: { en: 'Create branch', zh: '创建分支' },
        steps: [
          { phase: '01', label: { en: 'Detect', zh: '检测' },
            desc: { en: 'Auto-detect type from description keywords: feat/fix/refactor/docs.', zh: '从描述关键词自动检测类型: feat/fix/refactor/docs。' },
            tools: [] },
          { phase: '02', label: { en: 'Create', zh: '创建' },
            desc: { en: 'Create branch: {type}/{slug}. Auto-stash uncommitted changes.', zh: '创建分支: {类型}/{slug}。自动 stash 未提交变更。' },
            tools: [] }
        ]
      },
      'review': {
        label: { en: 'Review diff', zh: '审查差异' },
        steps: [
          { phase: '01', label: { en: 'CRG', zh: 'CRG' },
            desc: { en: 'detect_changes + get_impact_radius → blast-radius analysis.', zh: 'detect_changes + get_impact_radius → 影响面分析。' },
            tools: ['CRG'] },
          { phase: '02', label: { en: 'Diff', zh: '差异' },
            desc: { en: 'Show full diff vs source branch.', zh: '显示与源分支的完整差异。' },
            tools: [] }
        ]
      },
      'merge': {
        label: { en: 'Squash merge', zh: '压缩合并' },
        steps: [
          { phase: '01', label: { en: 'Commit', zh: '提交' },
            desc: { en: '/caveman-commit → compressed conventional commit message.', zh: '/caveman-commit → 压缩式 conventional commit 消息。' },
            tools: ['Caveman'] },
          { phase: '02', label: { en: 'Merge', zh: '合并' },
            desc: { en: 'Squash merge → delete feature branch.', zh: '压缩合并 → 删除功能分支。' },
            tools: [] }
        ]
      },
      'abort': {
        label: { en: 'Discard branch', zh: '放弃分支' },
        steps: [
          { phase: '01', label: { en: 'Abort', zh: '放弃' },
            desc: { en: 'Discard branch. Restore stash. Return to source branch.', zh: '丢弃分支。恢复 stash。返回源分支。' },
            tools: [] }
        ]
      },
      'status': {
        label: { en: 'Branch status', zh: '分支状态' },
        steps: [
          { phase: '01', label: { en: 'Status', zh: '状态' },
            desc: { en: 'Show current branch info and diff stats.', zh: '显示当前分支信息和差异统计。' },
            tools: [] }
        ]
      }
    }
  },
  '/tool-plan': {
    tag: 'Medium',
    sub: { en: 'Use this when the work is not yet executable because scope, order, ownership, or acceptance is unclear.', zh: '当工作因为范围、顺序、归属或验收不清楚而还不能直接执行时，使用这个命令。' },
    tools: { en: 'Tools: OpenSpec · CRG detect_changes · file-backed plans · gsd-new-milestone', zh: '工具: OpenSpec · CRG detect_changes · 文件化计划 · gsd-new-milestone' },
    modes: {
      '--fast': {
        label: { en: 'Inline plan', zh: '内联计划' },
        steps: [
          { phase: '01', label: { en: 'Clarify Inputs', zh: '澄清输入' },
            desc: { en: 'If the work is not plan-ready, use gsd-explore for product direction or /tool-research for decision evidence first.', zh: '如果工作还不具备规划条件，先用 gsd-explore 处理产品方向，或用 /tool-research 收集决策证据。' },
            tools: ['GSD', 'ECC'] },
          { phase: '02', label: { en: 'Plan', zh: '规划' },
            desc: { en: 'Short inline plan → route to /tool-quick or /tool-feat.', zh: '简短内联计划 → 路由到 /tool-quick 或 /tool-feat。' },
            tools: [] }
        ]
      },
      '--standard': {
        label: { en: 'Normal plan', zh: '常规计划' },
        steps: [
          { phase: '01', label: { en: 'Clarify Inputs', zh: '澄清输入' },
            desc: { en: 'Use gsd-explore or /tool-research only if the work is still not ready for planning.', zh: '只有在工作还不具备规划条件时，才进入 gsd-explore 或 /tool-research。' },
            tools: ['GSD', 'ECC'] },
          { phase: '02', label: { en: 'CRG Impact', zh: 'CRG 影响' },
            desc: { en: 'detect_changes + get_impact_radius(target="module").', zh: 'detect_changes + get_impact_radius(target="模块")。' },
            tools: ['CRG'] },
          { phase: '03', label: { en: 'Spec or Plan', zh: '规格或计划' },
            desc: { en: 'Define scope, affected modules, execution order, verification, and exit criteria. Use OpenSpec or a file-backed plan only when it adds value.', zh: '定义范围、影响模块、执行顺序、验证与退出条件。只有确实增益时才升级到 OpenSpec 或文件化计划。' },
            tools: ['OpenSpec'] },
          { phase: '04', label: { en: 'Security', zh: '安全' },
            desc: { en: 'Check: if touches auth/data/FS/network/SQL, add /tool-review --deep as a checkpoint.', zh: '检查：如果涉及 auth/data/FS/network/SQL，把 /tool-review --deep 加进检查点。' },
            tools: [] }
        ]
      },
      '--deep': {
        label: { en: 'Spec / Milestone', zh: '规格 / 里程碑' },
        steps: [
          { phase: '01', label: { en: 'Clarify Inputs', zh: '澄清输入' },
            desc: { en: 'If direction is still vague, clarify first. Planning should own execution order, not generic exploration.', zh: '如果方向仍然模糊，先做澄清。规划负责执行顺序，不负责兜底所有探索。' },
            tools: ['GSD', 'ECC'] },
          { phase: '02', label: { en: 'Classify', zh: '分级' },
            desc: { en: 'Auto-classify: spec-first → OpenSpec, ≤3 PR → file-backed plan, >3 PR → gsd-new-milestone, architecture → deep research then milestone/file-backed plan.', zh: '自动分级：规格优先 → OpenSpec，≤3 PR → 文件化计划，>3 PR → gsd-new-milestone，架构变更 → 先深研究，再转里程碑或文件化计划。' },
            tools: ['OpenSpec', 'ECC', 'GSD'] },
          { phase: '03', label: { en: 'CRG Arch', zh: 'CRG 架构' },
            desc: { en: 'get_architecture_overview for module boundaries (deep mode).', zh: 'get_architecture_overview 了解模块边界 (deep 模式)。' },
            tools: ['CRG'] },
          { phase: '04', label: { en: 'Execute Plan', zh: '执行计划' },
            desc: { en: 'Discuss → plan → execute phases. Review before execution.', zh: '讨论 → 规划 → 执行阶段。执行前审查。' },
            tools: ['GSD', 'ECC'] }
        ]
      }
    }
  },
  '/tool-refactor': {
    tag: 'Medium',
    sub: { en: 'Behavior-preserving cleanup. Baseline before/after must match.', zh: '行为保持不变的重构。前后基线必须一致。' },
    tools: { en: 'Tools: CRG impact · refactor_tool · deep plan when broad', zh: '工具: CRG 影响分析 · refactor_tool · 广泛重构先深度规划' },
    modes: {
      '--fast': {
        label: { en: 'Quick clean', zh: '快速清理' },
        steps: [
          { phase: '01', label: { en: 'Baseline', zh: '基线' },
            desc: { en: 'Run baseline tests. If fail → /tool-fix first.', zh: '运行基线测试。失败 → 先 /tool-fix。' },
            tools: [] },
          { phase: '02', label: { en: 'CRG', zh: 'CRG' },
            desc: { en: 'get_impact_radius(target="fn") — check callers.', zh: 'get_impact_radius(target="函数") — 检查调用方。' },
            tools: ['CRG'] },
          { phase: '03', label: { en: 'Refactor', zh: '重构' },
            desc: { en: 'One logical unit. Verify after each step.', zh: '一个逻辑单元。每步验证。' },
            tools: [] },
          { phase: '04', label: { en: 'Review', zh: '审查' },
            desc: { en: '/tool-review --fast → confirm behavior identical.', zh: '/tool-review --fast → 确认行为一致。' },
            tools: [] }
        ]
      },
      '--standard': {
        label: { en: 'Safe refactor', zh: '安全重构' },
        steps: [
          { phase: '01', label: { en: 'Baseline', zh: '基线' },
            desc: { en: 'Run full baseline. rtk gain for large suites.', zh: '运行完整基线。大型套件用 rtk gain。' },
            tools: ['RTK'] },
          { phase: '02', label: { en: 'CRG Analysis', zh: 'CRG 分析' },
            desc: { en: 'get_impact_radius + refactor_tool (dead code) + semantic_search_nodes (patterns).', zh: 'get_impact_radius + refactor_tool (死代码) + semantic_search_nodes (模式)。' },
            tools: ['CRG'] },
          { phase: '03', label: { en: 'Small Steps', zh: '小步重构' },
            desc: { en: 'One logical unit at a time. Re-verify after each.', zh: '每次一个逻辑单元。每步重新验证。' },
            tools: [] },
          { phase: '04', label: { en: 'Verify', zh: '验证' },
            desc: { en: 'Compare behavior, public APIs, performance paths.', zh: '对比行为、公开 API、性能路径。' },
            tools: [] },
          { phase: '05', label: { en: 'Review', zh: '审查' },
            desc: { en: '/tool-review --fast or Caveman-compressed sanity check → report. Graph impact check clean.', zh: '/tool-review --fast 或 Caveman 压缩 sanity check → 报告。图影响检查为 clean。' },
            tools: ['Caveman', 'CRG'] }
        ]
      },
      '--deep': {
        label: { en: 'Phased refactor', zh: '阶段化重构' },
        steps: [
          { phase: '01', label: { en: 'Baseline', zh: '基线' },
            desc: { en: 'Full baseline + CRG full analysis.', zh: '完整基线 + CRG 完整分析。' },
            tools: ['CRG', 'RTK'] },
          { phase: '02', label: { en: 'Deep Plan', zh: '深度规划' },
            desc: { en: '/tool-plan --deep first. Use OpenSpec/file-backed plan/GSD only if the refactor needs durable boundaries or phase state.', zh: '先 /tool-plan --deep。仅当需要持久边界或阶段状态时使用 OpenSpec/文件化计划/GSD。' },
            tools: ['OpenSpec', 'GSD', 'ECC'] },
          { phase: '03', label: { en: 'Review', zh: '审查' },
            desc: { en: 'Run /tool-review --deep and add E2E tests if applicable.', zh: '运行 /tool-review --deep，并在适用时补 E2E 测试。' },
            tools: [] }
        ]
      }
    }
  },
  '/tool-review': {
    tag: 'Low→High',
    sub: { en: 'Review is a support task. Use it when review itself is the job.', zh: '审查是辅助任务。当审查本身就是工作内容时使用。' },
    tools: { en: 'Tools: CRG detect_changes · review checklist · repository-native PR context', zh: '工具: CRG detect_changes · 审查清单 · 仓库原生 PR 上下文' },
    modes: {
      '--fast': {
        label: { en: 'Quick check', zh: '快速检查' },
        steps: [
          { phase: '01', label: { en: 'Review', zh: '审查' },
            desc: { en: 'Caveman-compressed code quality sanity check.', zh: 'Caveman 压缩代码质量 sanity check。' },
            tools: ['Caveman'] }
        ]
      },
      '--standard': {
        label: { en: 'Normal review', zh: '常规审查' },
        steps: [
          { phase: '01', label: { en: 'CRG Diff', zh: 'CRG 差异' },
            desc: { en: 'detect_changes → risk-scored diff. get_review_context → token-efficient snippets.', zh: 'detect_changes → 风险评分 diff。get_review_context → 高效 token 片段。' },
            tools: ['CRG'] },
          { phase: '02', label: { en: 'Impact', zh: '影响面' },
            desc: { en: 'get_impact_radius(target="changed") — blast-radius detection.', zh: 'get_impact_radius(target="变更") — 影响面检测。' },
            tools: ['CRG'] },
          { phase: '03', label: { en: 'PR Ops', zh: 'PR 操作' },
            desc: { en: '(PR mode) inspect repository-native comments, CI status, and merge blockers if available.', zh: '(PR 模式) 检查仓库原生评论、CI 状态和合并阻塞项。' },
            tools: [] },
          { phase: '04', label: { en: 'Standards', zh: '规范' },
            desc: { en: 'Review for correctness, regressions, security, and maintainability.', zh: '围绕正确性、回归、安全和可维护性进行审查。' },
            tools: [] },
          { phase: '05', label: { en: 'Route Findings', zh: '路由问题' },
            desc: { en: 'Report HIGH findings and route them to /tool-fix, /tool-refactor, or /tool-feat. Re-review after changes.', zh: '报告 HIGH 发现，并路由到 /tool-fix、/tool-refactor 或 /tool-feat。改完后再审。' },
            tools: [] }
        ]
      },
      '--deep': {
        label: { en: 'Deep review', zh: '深度审查' },
        steps: [
          { phase: '01', label: { en: 'CRG Full', zh: 'CRG 完整' },
            desc: { en: 'Full CRG diff + impact analysis.', zh: '完整 CRG diff + 影响面分析。' },
            tools: ['CRG'] },
          { phase: '02', label: { en: 'Security', zh: '安全' },
            desc: { en: 'Expand the checklist for auth, user input, filesystem, network, secrets, cookies, SQL, and serialization.', zh: '把检查范围扩展到 auth、用户输入、文件系统、网络、secrets、cookies、SQL 和序列化。' },
            tools: [] },
          { phase: '03', label: { en: 'Parallel', zh: '并行审查' },
            desc: { en: 'Run a deep review pass, route HIGH findings to the owning command, then re-review until clean.', zh: '执行一次深度审查，把 HIGH 发现交回对应命令修复，再复审直到 clean。' },
            tools: [] },
          { phase: '04', label: { en: 'Post', zh: '收尾' },
            desc: { en: 'Summarize residual risk, accepted debt, and next route.', zh: '总结残余风险、接受的技术债和下一步路由。' },
            tools: [] }
        ]
      }
    }
  },
  '/tool-research': {
    tag: 'Low→High',
    sub: { en: 'Codebase-aware evidence gathering for a specific decision. Start narrow, escalate only when needed.', zh: '面向具体决策的代码库感知证据收集。从窄开始，按需升级。' },
    tools: { en: 'Special mode axis: quick / web / deep. Tools: CRG semantic_search · multi-source synthesis · tradeoff report', zh: '特殊模式轴: quick / web / deep。工具: CRG semantic_search · 多源综合 · 权衡报告' },
    modes: {
      '--quick': {
        label: { en: 'Quick search', zh: '快速搜索' },
        steps: [
          { phase: '01', label: { en: 'Define', zh: '定义' },
            desc: { en: 'Define the exact decision this research should inform.', zh: '定义本次研究要为哪个决策提供依据。' },
            tools: [] },
          { phase: '02', label: { en: 'CRG', zh: 'CRG' },
            desc: { en: 'semantic_search_nodes(query="topic") + query_graph(callees_of="node").', zh: 'semantic_search_nodes(query="主题") + query_graph(callees_of="节点")。' },
            tools: ['CRG'] },
          { phase: '03', label: { en: 'Search', zh: '搜索' },
            desc: { en: 'Search smallest source set. Cite sources.', zh: '搜索最小源集。引用来源。' },
            tools: [] },
          { phase: '04', label: { en: 'Route', zh: '路由' },
            desc: { en: 'Route: complex → /tool-plan, medium → /tool-feat, simple → /tool-quick.', zh: '路由: 复杂 → /tool-plan, 中等 → /tool-feat, 简单 → /tool-quick。' },
            tools: [] }
        ]
      },
      '--web': {
        label: { en: 'Web search', zh: '网页搜索' },
        steps: [
          { phase: '01', label: { en: 'CRG + Web', zh: 'CRG + 网页' },
            desc: { en: 'query_graph(imports_of="module") → web search for current docs.', zh: 'query_graph(imports_of="模块") → 网页搜索最新文档。' },
            tools: ['CRG'] },
          { phase: '02', label: { en: 'Synthesize', zh: '综合' },
            desc: { en: 'Concise synthesis. Highlight conflicts.', zh: '精确综合。高亮冲突。' },
            tools: [] },
          { phase: '03', label: { en: 'Route', zh: '路由' },
            desc: { en: 'Route findings with rationale.', zh: '附带理由路由发现结果。' },
            tools: [] }
        ]
      },
      '--deep': {
        label: { en: 'Deep research', zh: '深度研究' },
        steps: [
          { phase: '01', label: { en: 'CRG Arch', zh: 'CRG 架构' },
            desc: { en: 'get_architecture_overview + semantic_search_nodes — map entire codebase context.', zh: 'get_architecture_overview + semantic_search_nodes — 映射完整代码库上下文。' },
            tools: ['CRG'] },
          { phase: '02', label: { en: 'Deep Search', zh: '深度搜索' },
            desc: { en: 'Use deeper multi-source research only when the decision needs unfamiliar ecosystem knowledge, current facts, or conflicting evidence.', zh: '只有当决策需要陌生生态知识、最新事实或冲突证据时，才进入更深的多源研究。' },
            tools: ['ECC'] },
          { phase: '03', label: { en: 'Report', zh: '报告' },
            desc: { en: 'Tradeoff report with conflicts, confidence levels, and routing.', zh: '权衡报告: 冲突、置信度、路由建议。' },
            tools: [] }
        ]
      }
    }
  },
  '/tool-graph': {
    tag: 'Low',
    sub: { en: 'Code-review-graph diagnostic only. Graph is auto-refreshed by git hooks.', zh: 'code-review-graph 诊断。图由 git hook 自动刷新。' },
    tools: { en: 'CRG is auto-refreshed — do NOT manually update during normal workflow.', zh: 'CRG 自动刷新 — 正常工作时不需要手动更新。' },
    subcommands: {
      'status': {
        label: { en: 'Health check', zh: '健康检查' },
        steps: [
          { phase: '01', label: { en: 'Status', zh: '状态' },
            desc: { en: 'Check CRG installed + graph health + .code-review-graph/ state.', zh: '检查 CRG 安装状态 + 图健康度 + 存储目录状态。' },
            tools: [] }
        ]
      },
      'build': {
        label: { en: 'First build', zh: '首次构建' },
        steps: [
          { phase: '01', label: { en: 'Build', zh: '构建' },
            desc: { en: 'code-review-graph build — first-time full graph creation.', zh: 'code-review-graph build — 首次全量图谱构建。' },
            tools: [] }
        ]
      },
      'update': {
        label: { en: 'Manual refresh', zh: '手动刷新' },
        steps: [
          { phase: '01', label: { en: 'Update', zh: '更新' },
            desc: { en: 'code-review-graph update — manual refresh (only if hooks not active).', zh: 'code-review-graph update — 手动刷新 (仅当 hook 未激活时)。' },
            tools: [] }
        ]
      },
      'rebuild': {
        label: { en: 'Rebuild', zh: '重建' },
        steps: [
          { phase: '01', label: { en: 'Rebuild', zh: '重建' },
            desc: { en: 'Full rebuild when graph is stale or damaged.', zh: '图损坏或过时时全面重建。' },
            tools: [] }
        ]
      },
      'watch': {
        label: { en: 'Watch mode', zh: '监听模式' },
        steps: [
          { phase: '01', label: { en: 'Watch', zh: '监听' },
            desc: { en: 'code-review-graph watch / crg-daemon — continuous updates.', zh: 'code-review-graph watch / crg-daemon — 持续更新。' },
            tools: [] }
        ]
      }
    }
  },
  '/tool-update': {
    tag: 'Low',
    sub: { en: 'Sync and update engineer-shovel. Check component health for all 8 upstream tools.', zh: '同步更新 engineer-shovel。检查所有 8 个上游组件健康度。' },
    tools: { en: 'Checks: RTK · Caveman · CRG · claude-mem · superpowers · OpenSpec · ECC · GSD', zh: '检查: RTK · Caveman · CRG · claude-mem · superpowers · OpenSpec · ECC · GSD' },
    modes: {
      '--check': {
        label: { en: 'Read-only', zh: '只读检查' },
        steps: [
          { phase: '01', label: { en: 'Detect', zh: '检测' },
            desc: { en: 'Detect installed locations for target(s).', zh: '检测目标环境的安装位置。' },
            tools: [] },
          { phase: '02', label: { en: 'Compare', zh: '对比' },
            desc: { en: 'Compare installed files with latest repo versions.', zh: '对比已安装文件与最新仓库版本。' },
            tools: [] },
          { phase: '03', label: { en: 'Health', zh: '健康' },
            desc: { en: 'Check component health. Report missing/outdated/extra files.', zh: '检查组件健康度。报告缺失/过时/多余文件。' },
            tools: [] }
        ]
      },
      '--full': {
        label: { en: 'Sync + repair', zh: '同步 + 修复' },
        steps: [
          { phase: '01', label: { en: 'Check', zh: '检查' },
            desc: { en: 'Same as --check: detect + compare + health audit.', zh: '同 --check: 检测 + 对比 + 健康审计。' },
            tools: [] },
          { phase: '02', label: { en: 'Update', zh: '更新' },
            desc: { en: 'Overwrite installed files with latest versions.', zh: '用最新版本覆盖已安装文件。' },
            tools: [] },
          { phase: '03', label: { en: 'Repair', zh: '修复' },
            desc: { en: 'Install/configure missing components via official installers.', zh: '通过官方安装器安装/配置缺失组件。' },
            tools: [] },
          { phase: '04', label: { en: 'Verify', zh: '验证' },
            desc: { en: 'Verify installation integrity post-update.', zh: '验证更新后安装完整性。' },
            tools: [] }
        ]
      }
    }
  }
};

// ---- Background Particle Canvas ----
function initBackgroundCanvas() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let w, h, particles;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }

  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x = Math.random() * w;
      this.y = Math.random() * h;
      this.size = Math.random() * 1.5 + 0.5;
      this.speedX = (Math.random() - 0.5) * 0.3;
      this.speedY = (Math.random() - 0.5) * 0.3;
      this.opacity = Math.random() * 0.4 + 0.1;
    }
    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      if (this.x < 0 || this.x > w || this.y < 0 || this.y > h) this.reset();
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(79,142,247,${this.opacity})`;
      ctx.fill();
    }
  }

  function init() {
    resize();
    particles = Array.from({ length: Math.floor((w * h) / 15000) }, () => new Particle());
  }

  function animate() {
    ctx.clearRect(0, 0, w, h);
    particles.forEach(p => { p.update(); p.draw(); });
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', () => { resize(); particles.forEach(p => p.reset()); });
  init();
  animate();
}

// ---- Navigation Scroll Effect ----
function initNav() {
  const nav = document.querySelector('.nav');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
  }, { passive: true });
}

// ---- Scroll Hint ----
function initScrollHint() {
  const hint = document.getElementById('scroll-hint');
  if (!hint) return;
  window.addEventListener('scroll', () => {
    hint.style.opacity = window.scrollY > 100 ? '0' : '1';
  }, { passive: true });
}

// ---- Intersection Observer Animation ----
function initScrollAnimations() {
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const delay = parseInt(el.dataset.delay || '0');
        setTimeout(() => el.classList.add('visible'), delay);
        io.unobserve(el);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

  document.querySelectorAll('.cmd-card, .mode-card, .step-item, .ut-row, .boundary-core, .boundary-ext, .boundary-arrow').forEach((el, i) => {
    el.dataset.delay = (i % 4) * 80;
    io.observe(el);
  });
}

// ---- Render Commands Grid ----
function renderCommands() {
  const grid = document.getElementById('commands-grid');
  if (!grid) return;
  grid.innerHTML = '';

  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const delay = parseInt(el.dataset.delay || '0');
        setTimeout(() => el.classList.add('visible'), delay);
        io.unobserve(el);
      }
    });
  }, { threshold: 0.05, rootMargin: '0px 0px -40px 0px' });

  commands.forEach((cmd, i) => {
    const labels = commandLabels[cmd.key] || {};
    const label = labels[currentLang] || labels.en || {};
    const card = document.createElement('div');
    card.className = 'cmd-card';
    if (cmd.name === '/tool-feat' || cmd.name === '/tool-fix') {
      card.classList.add('featured');
    }
    card.dataset.delay = (i % 3) * 100;
    card.style.setProperty('--cmd-color', cmd.color);

    const modeLabels = label.modes || [];
    const def = cmd.defaultMode || '';
    const modeTagsHTML = modeLabels.map(m => {
      const isDef = m === def || m.includes(def.replace('--',''));
      return `<span class="cost-tag${isDef ? ' cost-tag-default' : ''}">${m}</span>`;
    }).join('');

    card.innerHTML = `
      <div class="cmd-card-header">
        <span class="cmd-name">${cmd.name}</span>
        <span class="cmd-tag">${cmd.tag}</span>
      </div>
      <p class="cmd-usefor">${label.usefor || ''}</p>
      <div class="cmd-cost">${modeTagsHTML}</div>
    `;

    card.addEventListener('click', () => openWorkflowModal(cmd));
    grid.appendChild(card);
    io.observe(card);
  });
}

// ---- Workflow Modal ----
let activeModalCmd = null;
let activeMode = null;

function openWorkflowModal(cmd) {
  activeModalCmd = cmd;
  if (!commandWorkflows[cmd.name]) return;

  const wf = commandWorkflows[cmd.name];
  const modal = document.getElementById('wf-modal');
  const body = document.getElementById('wf-modal-body');
  const cmdEl = document.getElementById('wf-modal-cmd');
  const tagEl = document.getElementById('wf-modal-tag');
  const subEl = document.getElementById('wf-modal-sub');
  const tabsEl = document.getElementById('wf-modal-tabs');
  const toolsEl = document.getElementById('wf-modal-tools');

  cmdEl.textContent = cmd.name;
  tagEl.textContent = wf.tag;
  tagEl.style.background = hexToRgba(cmd.color, 0.15);
  tagEl.style.color = cmd.color;
  subEl.textContent = (wf.sub && wf.sub[currentLang]) || '';

  if (toolsEl && wf.tools) {
    toolsEl.textContent = (wf.tools[currentLang] || wf.tools.en || '');
    toolsEl.style.display = '';
  } else if (toolsEl) {
    toolsEl.style.display = 'none';
  }

  // Build mode tabs
  const modeKeys = cmd.modes || [];
  const subKeys = cmd.subcommands || [];
  tabsEl.innerHTML = '';

  if (modeKeys.length > 0) {
    const defMode = cmd.defaultMode && modeKeys.includes(cmd.defaultMode) ? cmd.defaultMode : modeKeys[0];
    modeKeys.forEach(m => {
      const tab = document.createElement('span');
      tab.className = 'mode-tab';
      tab.textContent = m;
      tab.dataset.mode = m;
      tab.addEventListener('click', () => switchMode(m, wf, body, cmd.color));
      tabsEl.appendChild(tab);
    });
    activeMode = defMode;
    tabsEl.querySelector(`[data-mode="${defMode}"]`).classList.add('active');
    switchMode(defMode, wf, body, cmd.color);
  } else if (subKeys.length > 0) {
    const defSub = cmd.defaultMode && subKeys.includes(cmd.defaultMode) ? cmd.defaultMode : subKeys[0];
    subKeys.forEach(s => {
      const tab = document.createElement('span');
      tab.className = 'mode-tab';
      tab.textContent = s;
      tab.dataset.mode = s;
      tab.addEventListener('click', () => switchSubcommand(s, wf, body, cmd.color));
      tabsEl.appendChild(tab);
    });
    activeMode = defSub;
    tabsEl.querySelector(`[data-mode="${defSub}"]`).classList.add('active');
    switchSubcommand(defSub, wf, body, cmd.color);
  }

  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function switchMode(mode, wf, body, color) {
  activeMode = mode;
  const tabs = document.querySelectorAll('#wf-modal-tabs .mode-tab');
  tabs.forEach(t => t.classList.toggle('active', t.dataset.mode === mode));

  const modeData = wf.modes && wf.modes[mode];
  if (!modeData) return;
  renderSteps(modeData.steps, body, color);
}

function switchSubcommand(sub, wf, body, color) {
  activeMode = sub;
  const tabs = document.querySelectorAll('#wf-modal-tabs .mode-tab');
  tabs.forEach(t => t.classList.toggle('active', t.dataset.mode === sub));

  const subData = wf.subcommands && wf.subcommands[sub];
  if (!subData) return;
  renderSteps(subData.steps, body, color);
}

function renderSteps(steps, body, color) {
  body.innerHTML = steps.map((step, i) => `
    <div class="wf-step" style="opacity:0;transform:translateX(-16px)">
      <div class="wf-step-connector">
        <div class="wf-step-dot" style="background:${color};box-shadow:0 0 10px ${color}"></div>
        ${i < steps.length - 1 ? '<div class="wf-step-line"></div>' : ''}
      </div>
      <div class="wf-step-content">
        <div class="wf-step-header">
          <span class="wf-step-phase" style="color:${color}">${step.phase}</span>
          <span class="wf-step-label">${step.label[currentLang] || step.label.en || ''}</span>
        </div>
        <p class="wf-step-desc">${step.desc[currentLang] || step.desc.en || ''}</p>
        ${step.tools && step.tools.length > 0 ? `<div class="wf-step-tools">${step.tools.map(t => `<span class="wf-tool-chip">${t}</span>`).join('')}</div>` : ''}
      </div>
    </div>
  `).join('');

  body.querySelectorAll('.wf-step').forEach((el, i) => {
    setTimeout(() => {
      el.style.transition = 'all 0.35s cubic-bezier(0.16, 1, 0.3, 1)';
      el.style.opacity = '1';
      el.style.transform = 'translateX(0)';
    }, 60 + i * 70);
  });
}

function closeWorkflowModal() {
  const modal = document.getElementById('wf-modal');
  modal.classList.remove('open');
  document.body.style.overflow = '';
  activeModalCmd = null;
  activeMode = null;
}

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function initWorkflowModal() {
  const backdrop = document.getElementById('wf-modal-backdrop');
  const closeBtn = document.getElementById('wf-modal-close');
  if (backdrop) backdrop.addEventListener('click', closeWorkflowModal);
  if (closeBtn) closeBtn.addEventListener('click', closeWorkflowModal);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeWorkflowModal(); });
}

// ---- Step Execution Visualization ----
function initStepExecution() {
  const steps = document.querySelectorAll('.step-item');
  if (!steps.length) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const delay = parseInt(el.dataset.delay || '0');
        setTimeout(() => el.classList.add('visible'), delay);
        io.unobserve(el);
      }
    });
  }, { threshold: 0.3 });
  steps.forEach(step => io.observe(step));
}

function addStepPulseKeyframe() {
  if (document.getElementById('step-pulse-style')) return;
  const style = document.createElement('style');
  style.id = 'step-pulse-style';
  style.textContent = `
    @keyframes stepPulse {
      0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(79,142,247,0.5); }
      50% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(79,142,247,0); }
      100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(79,142,247,0); }
    }
  `;
  document.head.appendChild(style);
}

// ---- Copy Buttons ----
function initCopyButtons() {
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const text = btn.dataset.copy || btn.closest('.code-block')?.querySelector('code')?.textContent || '';
      navigator.clipboard.writeText(text).then(() => {
        btn.classList.add('copied');
        btn.textContent = i18n[currentLang]['copied'] || 'copied';
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.textContent = i18n[currentLang]['copy'] || 'Copy';
        }, 2000);
      });
    });
  });
}

// ---- Smooth Scroll for Nav Links ----
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });
}

// ---- Upstream Table Row Stagger ----
function initUpstreamTable() {
  const rows = document.querySelectorAll('.ut-row');
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const delay = parseInt(el.dataset.delay || '0');
        setTimeout(() => el.classList.add('visible'), delay);
        io.unobserve(el);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
  rows.forEach((row, i) => {
    row.dataset.delay = i * 80;
    io.observe(row);
  });
}

// ---- Capability Boundary Animation ----
function initBoundary() {
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        [document.querySelector('.boundary-core'), document.querySelector('.boundary-arrow'), document.querySelector('.boundary-ext')].forEach((el, i) => {
          if (el) setTimeout(() => el.classList.add('visible'), i * 150);
        });
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });
  const layout = document.querySelector('.boundary-layout');
  if (layout) io.observe(layout);
}

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
  addStepPulseKeyframe();
  initBackgroundCanvas();
  initNav();
  initScrollHint();
  initScrollAnimations();
  initLanguageToggle();
  initRoutePicker();
  renderCommands();
  initStepExecution();
  initCopyButtons();
  initSmoothScroll();
  initUpstreamTable();
  initBoundary();
  initWorkflowModal();
});
