/* ================================================
   ENGINEER SHOVEL — GITHUB PAGES JAVASCRIPT
   Animations · Step Execution · Workflow Modal · i18n
   ================================================ */

// ---- Language ----
const i18n = {
  en: {
    'hero.badge': 'v1.3.0 · MIT License',
    'hero.subtitle': 'Token-aware AI development workflow router for OpenCode / Claude Code',
    'hero.desc': '12 commands covering quick tasks, bug fixes, features, branch, planning, refactoring, review, brainstorming, blueprints, research, graph, and sync. Use the cheapest path that verifies the result.',
    'copy': 'Copy',
    'copied': 'copied'
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
    'hero.badge': 'v1.3.0 · MIT License',
    'hero.subtitle': '面向 OpenCode / Claude Code 的 token-aware AI 开发工作流路由器',
    'hero.desc': '12 个命令覆盖快速任务、Bug 修复、新功能、分支、规划、重构、审查、头脑风暴、蓝图、研究、图谱和同步。用最低成本完成工作，只在需要时升级。',
    'commands.title': '12 个命令',
    'commands.sub': '每个命令对应一个明确的开发场景。选对工具，用最少的 token 完成任务。',
    'modes.title': '成本模式',
    'modes.sub': '根据任务复杂度选择对应模式，默认选择能验证结果的最低成本路径。',
    'modes.fast.title': '低风险 · 明确目标',
    'modes.fast.1': 'Typo 修复',
    'modes.fast.2': '1-2 文件编辑',
    'modes.fast.3': '已知位置的配置修改',
    'modes.standard.title': '常规开发任务',
    'modes.standard.1': '新功能实现',
    'modes.standard.2': '中等规模重构',
    'modes.standard.3': '本地 diff 审查',
    'modes.deep.title': '高风险 · 跨系统 · 模糊',
    'modes.deep.1': '架构决策',
    'modes.deep.2': '跨模块调试',
    'modes.deep.3': '深度研究',
    'start.title': '快速开始',
    'start.sub': '下载 → 检查 → 运行，三步完成安装。',
    'start.step1.title': '下载安装脚本',
    'start.step1.desc': '先下载、检查内容，再执行。默认全量安装所有组件。',
    'start.step2.title': '选择安装模式',
    'start.step2.desc': '支持 OpenCode / Claude Code，minimal / recommended / full 多种模式。',
    'start.step3.title': '开始使用',
    'start.step3.desc': '在会话中加载技能或直接调用命令。',
    'upstream.title': '上游工具',
    'upstream.sub': 'Engineer Shovel 在 --full 模式下会安装并配置这些上游工具。',
    'upstream.col.tool': '工具',
    'upstream.col.ver': '版本',
    'upstream.col.role': '作用',
    'upstream.ecc': 'AI agent harness 性能系统：skills、rules、hooks、MCP、安全与 research-first 工作流',
    'upstream.gsd': 'Spec-driven 规划、阶段执行、验证和上下文工程',
    'upstream.sp': '强制技能工作流：brainstorming、TDD、planning、review、branch finishing',
    'upstream.crg': '本地代码知识图谱、MCP review context、影响面分析',
    'upstream.caveman': '输出 token 压缩、精简 review/commit、MCP shrink',
    'upstream.rtk': 'Shell/tool 输出压缩代理和命令 rewrite hooks',
    'boundary.title': '能力边界',
    'boundary.core.title': '原生安装（最小模式）',
    'boundary.core.desc': 'Engineer Shovel 原生安装的是轻量路由器和 12 个 /tool-* 命令。',
    'boundary.core.1': '轻量级 SKILL.md 路由层',
    'boundary.core.2': '12 个 /tool-* 命令',
    'boundary.core.3': 'install.sh 安装脚本',
    'boundary.ext.title': '可选外部工具（recommended / full 模式）',
    'boundary.ext.desc': '完整工作流里更深的能力来自 recommended / full 模式安装或配置的可选外部工具。',
    'footer.docs': '文档',
    'footer.install': '安装',
    'footer.cost': '成本模型',
    'copy': '复制',
    'copied': '已复制',
    'wf.close': '关闭'
  }
};

let currentLang = 'en';

// Store original text before any translation overwrites it
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
    if (i18n[lang].hasOwnProperty(key)) {
      el.textContent = i18n[lang][key];
    } else if (lang === 'en') {
      // Fall back to original HTML text for English
      el.textContent = el.dataset.i18nOriginal || el.textContent;
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

// ---- Command Data ----
const commands = [
  { name: '/tool-quick', color: '#3dd590', key: 'cmd.quick', tag: 'Low' },
  { name: '/tool-fix', color: '#f56f6f', key: 'cmd.fix', tag: 'Low→High' },
  { name: '/tool-feat', color: '#4f8ef7', key: 'cmd.feat', tag: 'Medium' },
  { name: '/tool-branch', color: '#9b6dff', key: 'cmd.branch', tag: 'Low' },
  { name: '/tool-plan', color: '#f5a84f', key: 'cmd.plan', tag: 'Medium' },
  { name: '/tool-refactor', color: '#3dd6f5', key: 'cmd.refactor', tag: 'Medium' },
  { name: '/tool-review', color: '#4f8ef7', key: 'cmd.review', tag: 'Low→High' },
  { name: '/tool-brainstorm', color: '#f5a84f', key: 'cmd.brainstorm', tag: 'Low→Medium' },
  { name: '/tool-blueprint', color: '#9b6dff', key: 'cmd.blueprint', tag: 'High' },
  { name: '/tool-research', color: '#3dd6f5', key: 'cmd.research', tag: 'Low→High' },
  { name: '/tool-graph', color: '#3dd590', key: 'cmd.graph', tag: 'Low' },
  { name: '/tool-update', color: '#4f8ef7', key: 'cmd.update', tag: 'Low' }
];

const commandLabels = {
  'cmd.quick': {
    en: { usefor: 'Typos, config edits, 1-2 file changes', costs: ['--fast', '/caveman lite', 'direct edit'] },
    zh: { usefor: 'Typo 修复、配置修改、1-2 文件编辑', costs: ['--fast', '/caveman lite', '直接编辑'] }
  },
  'cmd.fix': {
    en: { usefor: 'Bug reports, failing tests, regressions', costs: ['--fast', '--standard', '--deep'] },
    zh: { usefor: 'Bug 报告、失败测试、回归', costs: ['--fast', '--standard', '--deep'] }
  },
  'cmd.feat': {
    en: { usefor: 'New functionality', costs: ['--standard', '--deep', 'GSD phases'] },
    zh: { usefor: '新功能实现', costs: ['--standard', '--deep', 'GSD phases'] }
  },
  'cmd.branch': {
    en: { usefor: 'Branch: create, review, merge, abort', costs: ['create', 'review', 'merge', 'abort'] },
    zh: { usefor: '分支：创建、审查、合并、放弃', costs: ['create', 'review', 'merge', 'abort'] }
  },
  'cmd.plan': {
    en: { usefor: 'Requirements and implementation planning', costs: ['--fast inline', '--standard file', '--deep blueprint'] },
    zh: { usefor: '需求和实现规划', costs: ['--fast inline', '--standard file', '--deep blueprint'] }
  },
  'cmd.refactor': {
    en: { usefor: 'Behavior-preserving cleanup', costs: ['--standard', '--deep', '/review-work'] },
    zh: { usefor: '行为保持不变的重构', costs: ['--standard', '--deep', '/review-work'] }
  },
  'cmd.review': {
    en: { usefor: 'Local diff, PR, post-implementation review', costs: ['--fast', 'default', '--deep'] },
    zh: { usefor: '本地 diff、PR、实现后审查', costs: ['--fast', 'default', '--deep'] }
  },
  'cmd.brainstorm': {
    en: { usefor: 'Explore unclear ideas before building', costs: ['quick', 'feature', 'plan', 'research'] },
    zh: { usefor: '想法不清晰时先澄清', costs: ['quick', 'feature', 'plan', 'research'] }
  },
  'cmd.blueprint': {
    en: { usefor: 'Multi-step, multi-session projects', costs: ['--deep', 'GSD', 'multi-agent'] },
    zh: { usefor: '多步骤、多会话项目', costs: ['--deep', 'GSD', 'multi-agent'] }
  },
  'cmd.research': {
    en: { usefor: 'Current-state technical research', costs: ['--quick', '--web', '--deep'] },
    zh: { usefor: '当前状态技术研究', costs: ['--quick', '--web', '--deep'] }
  },
  'cmd.graph': {
    en: { usefor: 'code-review-graph: status, build, update', costs: ['status', 'build', 'update', 'rebuild'] },
    zh: { usefor: 'code-review-graph：状态、构建、更新', costs: ['status', 'build', 'update', 'rebuild'] }
  },
  'cmd.update': {
    en: { usefor: 'Sync and update installation', costs: ['--fast', 'rtk gain', 'verify'] },
    zh: { usefor: '同步和更新安装', costs: ['--fast', 'rtk gain', '验证'] }
  }
};

// ---- Command Workflow Data ----
const commandWorkflows = {
  '/tool-quick': {
    tag: 'Low',
    sub: { en: 'Obvious, low-risk work: typos, config changes, simple renames', zh: '明显、低风险的工作：typo、配置修改、简单重命名' },
    steps: [
      { phase: '01', label: { en: 'Identify', zh: '定位' }, desc: { en: 'Locate target file(s). Clear scope, known location.', zh: '定位目标文件。范围清晰、位置已知。' } },
      { phase: '02', label: { en: 'Execute', zh: '执行' }, desc: { en: 'Apply surgical edit directly. No planning needed.', zh: '直接进行精确编辑。无需规划。' } },
      { phase: '03', label: { en: 'Verify', zh: '验证' }, desc: { en: 'Run targeted verification (build/lint/test).', zh: '运行定向验证（构建/lint/测试）。' } },
      { phase: '04', label: { en: 'Commit', zh: '提交' }, desc: { en: 'Commit only if user explicitly asks.', zh: '仅在用户明确要求时提交。' } }
    ]
  },
  '/tool-fix': {
    tag: 'Low→High',
    sub: { en: 'Broken behavior, failing tests, regressions', zh: '行为异常、测试失败、回归问题' },
    steps: [
      { phase: '01', label: { en: 'Reproduce', zh: '复现' }, desc: { en: '--fast: known cause → direct fix. --standard: reproduce + inspect. --deep: GSD debugging + Oracle.', zh: '--fast：已知原因 → 直接修复。--standard：复现 + 检查。--deep：GSD 调试 + Oracle。' } },
      { phase: '02', label: { en: 'Locate', zh: '定位' }, desc: { en: 'Find root cause across files if needed.', zh: '必要时跨文件定位根本原因。' } },
      { phase: '03', label: { en: 'Fix', zh: '修复' }, desc: { en: 'Apply minimal fix. Add regression test.', zh: '应用最小修复。添加回归测试。' } },
      { phase: '04', label: { en: 'Verify', zh: '验证' }, desc: { en: 'Re-run tests. Confirm fix holds.', zh: '重新运行测试。确认修复有效。' } }
    ]
  },
  '/tool-feat': {
    tag: 'Medium',
    sub: { en: 'New functionality', zh: '新功能' },
    steps: [
      { phase: '01', label: { en: 'Plan', zh: '规划' }, desc: { en: '--fast: known location. --standard: targeted exploration + plan. --deep: blueprint/GSD phases.', zh: '--fast：已知位置。--standard：定向探索 + 计划。--deep：蓝图/GSD 阶段。' } },
      { phase: '02', label: { en: 'Search', zh: '搜索' }, desc: { en: 'Find existing patterns before building.', zh: '构建前先搜索现有模式。' } },
      { phase: '03', label: { en: 'Implement', zh: '实现' }, desc: { en: 'Surgical change. Preserve project style.', zh: '精确改动。保持项目风格。' } },
      { phase: '04', label: { en: 'Verify', zh: '验证' }, desc: { en: 'Run tests/build. Verify coverage.', zh: '运行测试/构建。验证覆盖率。' } }
    ]
  },
  '/tool-branch': {
    tag: 'Low',
    sub: { en: 'Feature branch lifecycle: create, review, merge, abort', zh: '功能分支生命周期：创建、审查、合并、放弃' },
    steps: [
      { phase: '01', label: { en: 'Create', zh: '创建' }, desc: { en: '/tool-branch create [type] [desc] — auto-detect feat/fix/refactor/docs.', zh: '/tool-branch create [类型] [描述] — 自动检测 feat/fix/refactor/docs。' } },
      { phase: '02', label: { en: 'Work', zh: '工作' }, desc: { en: 'Make commits on feature branch.', zh: '在功能分支上提交。' } },
      { phase: '03', label: { en: 'Review', zh: '审查' }, desc: { en: '/tool-branch review — show diff vs source.', zh: '/tool-branch review — 显示与源的差异。' } },
      { phase: '04', label: { en: 'Merge/Abort', zh: '合并/放弃' }, desc: { en: 'Merge: squash → commit → delete. Abort: discard + return to source.', zh: '合并：压缩 → 提交 → 删除。放弃：丢弃并返回源分支。' } }
    ]
  },
  '/tool-plan': {
    tag: 'Medium',
    sub: { en: 'Requirements and implementation planning', zh: '需求和实现规划' },
    steps: [
      { phase: '01', label: { en: 'Clarify', zh: '澄清' }, desc: { en: '--fast: inline plan. --standard: file-backed with risks. --deep: blueprint or GSD.', zh: '--fast：内联计划。--standard：文件支持 + 风险。--deep：蓝图或 GSD。' } },
      { phase: '02', label: { en: 'Scope', zh: '范围' }, desc: { en: 'Identify files/modules affected. Define verification criteria.', zh: '识别受影响的文件/模块。定义验证标准。' } },
      { phase: '03', label: { en: 'Plan', zh: '规划' }, desc: { en: 'Break into phases. Order dependencies.', zh: '分解为阶段。排序依赖。' } },
      { phase: '04', label: { en: 'Review', zh: '审查' }, desc: { en: 'Momus review before execution.', zh: '执行前 Momus 审查。' } }
    ]
  },
  '/tool-refactor': {
    tag: 'Medium',
    sub: { en: 'Behavior-preserving cleanup', zh: '行为保持不变的重构' },
    steps: [
      { phase: '01', label: { en: 'Baseline', zh: '基线' }, desc: { en: 'Establish tests/build baseline.', zh: '建立测试/构建基线。' } },
      { phase: '02', label: { en: 'Refactor', zh: '重构' }, desc: { en: 'One logical change at a time.', zh: '每次一个逻辑变更。' } },
      { phase: '03', label: { en: 'Verify', zh: '验证' }, desc: { en: 'Re-run verification each step.', zh: '每步重新运行验证。' } },
      { phase: '04', label: { en: 'Review', zh: '审查' }, desc: { en: 'Cheapest mode that fits risk.', zh: '最适合风险的最便宜模式。' } }
    ]
  },
  '/tool-review': {
    tag: 'Low→High',
    sub: { en: 'Local diff, PR, or post-implementation review', zh: '本地 diff、PR 或实现后审查' },
    steps: [
      { phase: '01', label: { en: 'Diff', zh: '差异' }, desc: { en: '--fast: Caveman-compressed. default: local/PR review. --deep: high-risk security review.', zh: '--fast：Caveman 压缩版。default：本地/PR 审查。--deep：高风险安全审查。' } },
      { phase: '02', label: { en: 'Security', zh: '安全' }, desc: { en: 'Check: auth, input, DB, file ops, ext APIs, crypto, payments.', zh: '检查：认证、输入、数据库、文件操作、外部 API、加密、支付。' } },
      { phase: '03', label: { en: 'Quality', zh: '质量' }, desc: { en: 'Code quality checklist: size, nesting, errors, tests.', zh: '代码质量清单：大小、嵌套、错误、测试。' } },
      { phase: '04', label: { en: 'Report', zh: '报告' }, desc: { en: 'BLOCK: CRITICAL. WARN: HIGH. APPROVE: rest.', zh: '阻止：CRITICAL。警告：HIGH。批准：其余。' } }
    ]
  },
  '/tool-brainstorm': {
    tag: 'Low→Medium',
    sub: { en: 'Explore unclear ideas before building', zh: '想法不清晰时先澄清' },
    steps: [
      { phase: '01', label: { en: 'Capture', zh: '捕获' }, desc: { en: 'Clarify the idea. Identify gaps.', zh: '澄清想法。识别空白。' } },
      { phase: '02', label: { en: 'Route', zh: '路由' }, desc: { en: 'Route to: quick, feature, plan, research, or backlog.', zh: '路由到：quick、feature、plan、research 或 backlog。' } },
      { phase: '03', label: { en: 'Sketch', zh: '草图' }, desc: { en: 'Rough approach, open questions.', zh: '粗略方案，开放问题。' } },
      { phase: '04', label: { en: 'Decide', zh: '决定' }, desc: { en: 'Pick best path forward.', zh: '选择最佳路径。' } }
    ]
  },
  '/tool-blueprint': {
    tag: 'High',
    sub: { en: 'Multi-step, multi-session projects', zh: '多步骤、多会话项目' },
    steps: [
      { phase: '01', label: { en: 'Scope', zh: '范围' }, desc: { en: 'Define milestones, dependencies, PR boundaries.', zh: '定义里程碑、依赖、PR 边界。' } },
      { phase: '02', label: { en: 'Plan', zh: '规划' }, desc: { en: 'One independently verifiable step per PR.', zh: '每个 PR 一步独立可验证。' } },
      { phase: '03', label: { en: 'Execute', zh: '执行' }, desc: { en: 'GSD phases. Verify each step.', zh: 'GSD 阶段。每步验证。' } },
      { phase: '04', label: { en: 'Iterate', zh: '迭代' }, desc: { en: 'Refine across sessions.', zh: '跨会话精炼。' } }
    ]
  },
  '/tool-research': {
    tag: 'Low→High',
    sub: { en: 'Current-state technical research', zh: '当前状态技术研究' },
    steps: [
      { phase: '01', label: { en: 'Quick', zh: '快速' }, desc: { en: '--quick: local docs + known references.', zh: '--quick：本地文档 + 已知参考资料。' } },
      { phase: '02', label: { en: 'Web', zh: '网页' }, desc: { en: '--web: add docs/web search.', zh: '--web：添加文档/网络搜索。' } },
      { phase: '03', label: { en: 'Deep', zh: '深度' }, desc: { en: '--deep: multi-source, code examples, synthesis.', zh: '--deep：多源、代码示例、综合。' } },
      { phase: '04', label: { en: 'Synthesize', zh: '综合' }, desc: { en: 'Resolve conflicts. Write findings.', zh: '解决冲突。撰写结论。' } }
    ]
  },
  '/tool-graph': {
    tag: 'Low',
    sub: { en: 'code-review-graph: status, build, update, rebuild, watch', zh: 'code-review-graph：状态、构建、更新、重建、监听' },
    steps: [
      { phase: '01', label: { en: 'Status', zh: '状态' }, desc: { en: 'Show install + graph health.', zh: '显示安装状态 + 图健康状态。' } },
      { phase: '02', label: { en: 'Build/Update', zh: '构建/更新' }, desc: { en: 'build: full index. update: incremental refresh.', zh: 'build：完整索引。update：增量刷新。' } },
      { phase: '03', label: { en: 'Rebuild', zh: '重建' }, desc: { en: 'Full refresh for stale/damaged graphs.', zh: '对过时/损坏的图进行完整刷新。' } },
      { phase: '04', label: { en: 'Watch', zh: '监听' }, desc: { en: 'Start continuous graph updates (user approval required).', zh: '启动持续图更新（需用户批准）。' } }
    ]
  },
  '/tool-update': {
    tag: 'Low',
    sub: { en: 'Sync and update installation', zh: '同步和更新安装' },
    steps: [
      { phase: '01', label: { en: 'Check', zh: '检查' }, desc: { en: 'Verify current install state.', zh: '验证当前安装状态。' } },
      { phase: '02', label: { en: 'Fetch', zh: '获取' }, desc: { en: 'Pull latest versions from remote.', zh: '从远程拉取最新版本。' } },
      { phase: '03', label: { en: 'Apply', zh: '应用' }, desc: { en: 'Update changed components.', zh: '更新已更改的组件。' } },
      { phase: '04', label: { en: 'Verify', zh: '验证' }, desc: { en: 'Confirm healthy state post-update.', zh: '确认更新后健康状态。' } }
    ]
  }
};

// ---- Background Particle Canvas ----
function initBackgroundCanvas() {
  const canvas = document.getElementById('bg-canvas');
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
    const labels = commandLabels[cmd.key][currentLang];
    const card = document.createElement('div');
    card.className = 'cmd-card';
    card.dataset.delay = (i % 3) * 100;
    card.style.setProperty('--cmd-color', cmd.color);

    card.innerHTML = `
      <div class="cmd-card-header">
        <span class="cmd-name">${cmd.name}</span>
        <span class="cmd-tag">${cmd.tag}</span>
      </div>
      <p class="cmd-usefor">${labels.usefor}</p>
      <div class="cmd-cost">
        ${labels.costs.map(c => `<span class="cost-tag">${c}</span>`).join('')}
      </div>
    `;

    card.addEventListener('click', () => openWorkflowModal(cmd.name));
    grid.appendChild(card);
    io.observe(card);
  });
}

// ---- Workflow Modal ----
function openWorkflowModal(cmdName) {
  const wf = commandWorkflows[cmdName];
  if (!wf) return;

  const modal = document.getElementById('wf-modal');
  const body = document.getElementById('wf-modal-body');
  const cmdEl = document.getElementById('wf-modal-cmd');
  const tagEl = document.getElementById('wf-modal-tag');
  const subEl = document.getElementById('wf-modal-sub');

  cmdEl.textContent = cmdName;
  tagEl.textContent = wf.tag;
  subEl.textContent = wf.sub[currentLang];

  const cmdData = commands.find(c => c.name === cmdName);
  const color = cmdData ? cmdData.color : '#4f8ef7';
  tagEl.style.background = hexToRgba(color, 0.15);
  tagEl.style.color = color;

  body.innerHTML = wf.steps.map((step, i) => `
    <div class="wf-step" style="opacity:0;transform:translateX(-16px)">
      <div class="wf-step-connector">
        <div class="wf-step-dot" style="background:${color};box-shadow:0 0 8px ${color}"></div>
        ${i < wf.steps.length - 1 ? '<div class="wf-step-line"></div>' : ''}
      </div>
      <div class="wf-step-content">
        <div class="wf-step-header">
          <span class="wf-step-phase" style="color:${color}">${step.phase}</span>
          <span class="wf-step-label">${step.label[currentLang]}</span>
        </div>
        <p class="wf-step-desc">${step.desc[currentLang]}</p>
      </div>
    </div>
  `).join('');

  modal.classList.add('open');
  document.body.style.overflow = 'hidden';

  body.querySelectorAll('.wf-step').forEach((el, i) => {
    setTimeout(() => {
      el.style.transition = 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
      el.style.opacity = '1';
      el.style.transform = 'translateX(0)';
    }, 100 + i * 100);
  });
}

function closeWorkflowModal() {
  const modal = document.getElementById('wf-modal');
  modal.classList.remove('open');
  document.body.style.overflow = '';
}

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function initWorkflowModal() {
  const modal = document.getElementById('wf-modal');
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
        animateStep(el, el.dataset.step);
        io.unobserve(el);
      }
    });
  }, { threshold: 0.3 });

  steps.forEach(step => io.observe(step));
}

function animateStep(el) {
  const delay = parseInt(el.dataset.delay || 0);
  setTimeout(() => {
    el.classList.add('visible');
    const numEl = el.querySelector('.step-num');
    if (numEl) {
      numEl.style.animation = 'stepPulse 0.5s ease-out';
      setTimeout(() => { numEl.style.animation = ''; }, 500);
    }
  }, delay);
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
        const orig = btn.textContent.trim();
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
  renderCommands();
  initStepExecution();
  initCopyButtons();
  initSmoothScroll();
  initUpstreamTable();
  initBoundary();
  initWorkflowModal();
});
