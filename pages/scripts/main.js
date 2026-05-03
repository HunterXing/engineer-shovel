/* ================================================
   ENGINEER SHOVEL — GITHUB PAGES JAVASCRIPT
   Animations · Step Execution · Interactive UI
   ================================================ */

// ---- Command Data ----
const commands = [
  {
    name: '/tool-quick',
    color: '#3dd590',
    tag: 'Low',
    usefor: 'Typos, config edits, 1-2 file changes',
    costs: ['--fast', '/caveman lite', 'direct edit']
  },
  {
    name: '/tool-fix',
    color: '#f56f6f',
    tag: 'Low→High',
    usefor: 'Bug reports, failing tests, regressions',
    costs: ['--fast', '--standard', '--deep']
  },
  {
    name: '/tool-feat',
    color: '#4f8ef7',
    tag: 'Medium',
    usefor: 'New functionality',
    costs: ['--standard', '--deep', 'GSD phases']
  },
  {
    name: '/tool-branch',
    color: '#9b6dff',
    tag: 'Low',
    usefor: 'Branch: create, review, merge, abort',
    costs: ['create', 'review', 'merge', 'abort']
  },
  {
    name: '/tool-plan',
    color: '#f5a84f',
    tag: 'Medium',
    usefor: 'Requirements and implementation planning',
    costs: ['--fast inline', '--standard file', '--deep blueprint']
  },
  {
    name: '/tool-refactor',
    color: '#3dd6f5',
    tag: 'Medium',
    usefor: 'Behavior-preserving cleanup',
    costs: ['--standard', '--deep', '/review-work']
  },
  {
    name: '/tool-review',
    color: '#4f8ef7',
    tag: 'Low→High',
    usefor: 'Local diff, PR, post-implementation review',
    costs: ['--fast', 'default', '--deep']
  },
  {
    name: '/tool-brainstorm',
    color: '#f5a84f',
    tag: 'Low→Medium',
    usefor: 'Explore unclear ideas before building',
    costs: ['quick', 'feature', 'plan', 'research']
  },
  {
    name: '/tool-blueprint',
    color: '#9b6dff',
    tag: 'High',
    usefor: 'Multi-step, multi-session projects',
    costs: ['--deep', 'GSD', 'multi-agent']
  },
  {
    name: '/tool-research',
    color: '#3dd6f5',
    tag: 'Low→High',
    usefor: 'Current-state technical research',
    costs: ['--quick', '--web', '--deep']
  },
  {
    name: '/tool-graph',
    color: '#3dd590',
    tag: 'Low',
    usefor: 'code-review-graph status, build, update',
    costs: ['status', 'build', 'update', 'rebuild']
  },
  {
    name: '/tool-update',
    color: '#4f8ef7',
    tag: 'Low',
    usefor: 'Sync and update installation',
    costs: ['--fast', 'rtk gain', 'verify']
  }
];

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
    constructor() {
      this.reset();
    }
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
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
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

  commands.forEach((cmd, i) => {
    const card = document.createElement('div');
    card.className = 'cmd-card';
    card.dataset.delay = (i % 3) * 100;
    card.style.setProperty('--cmd-color', cmd.color);

    card.innerHTML = `
      <div class="cmd-card-header">
        <span class="cmd-name">${cmd.name}</span>
        <span class="cmd-tag">${cmd.tag}</span>
      </div>
      <p class="cmd-usefor">${cmd.usefor}</p>
      <div class="cmd-details">
        <div class="cmd-cost">
          ${cmd.costs.map(c => `<span class="cost-tag">${c}</span>`).join('')}
        </div>
      </div>
    `;

    card.addEventListener('click', () => {
      const wasExpanded = card.classList.contains('expanded');
      document.querySelectorAll('.cmd-card.expanded').forEach(c => c.classList.remove('expanded'));
      if (!wasExpanded) card.classList.add('expanded');
    });

    grid.appendChild(card);
  });

  // observe for scroll animation
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const delay = parseInt(el.dataset.delay || '0');
        setTimeout(() => el.classList.add('visible'), delay);
        io.unobserve(el);
      }
    });
  }, { threshold: 0.05, rootMargin: '0px 0px -40px 0px' });

  grid.querySelectorAll('.cmd-card').forEach(card => io.observe(card));
}

// ---- Step Execution Visualization ----
function initStepExecution() {
  const steps = document.querySelectorAll('.step-item');
  if (!steps.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const stepNum = el.dataset.step;
        animateStep(el, stepNum);
        io.unobserve(el);
      }
    });
  }, { threshold: 0.3 });

  steps.forEach(step => io.observe(step));
}

function animateStep(el, num) {
  const delay = parseInt(el.dataset.delay || 0);
  setTimeout(() => {
    el.classList.add('visible');
    // Pulse the step number
    const numEl = el.querySelector('.step-num');
    if (numEl) {
      numEl.style.animation = 'stepPulse 0.5s ease-out';
      setTimeout(() => { numEl.style.animation = ''; }, 500);
    }
  }, delay);
}

// ---- Add step pulse keyframe dynamically ----
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
        btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> 已复制`;
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> 复制`;
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
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

// ---- Upstream Table Row Stagger ----
function initUpstreamTable() {
  const rows = document.querySelectorAll('.ut-row');
  const io = new IntersectionObserver((entries) => {
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
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const core = document.querySelector('.boundary-core');
        const arrow = document.querySelector('.boundary-arrow');
        const ext = document.querySelector('.boundary-ext');

        [core, arrow, ext].forEach((el, i) => {
          if (!el) return;
          setTimeout(() => el.classList.add('visible'), i * 150);
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
  renderCommands();
  initStepExecution();
  initCopyButtons();
  initSmoothScroll();
  initUpstreamTable();
  initBoundary();
});
