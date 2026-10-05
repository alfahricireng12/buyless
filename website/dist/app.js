(() => {
  'use strict';
  const root = document.documentElement;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const notesButton = document.getElementById('notes-toggle');
  const notesButtons = [notesButton, document.getElementById('notes-float')].filter(Boolean);
  const progress = document.querySelector('.reading-progress');
  const introPoster = document.querySelector('.intro-poster');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  const chapters = [...document.querySelectorAll('.chapter-nav a[href^="#"]')]
    .map((link) => ({ link, target: document.getElementById(link.hash.slice(1)) }))
    .filter(({ target }) => target);
  const exhibits = [...document.querySelectorAll('[data-choreo]')]
    .map((section) => ({ section, stage: section.querySelector('.exhibit-stage') }));
  let paused = reducedMotion.matches;
  let scrollFrame = 0;
  let tiltFrame = 0;
  let pointerPosition = null;
  let priceAnimation = null;
  let introTimer = 0;
  const finishIntro = () => {
    window.clearTimeout(introTimer);
    root.classList.remove('intro-playing', 'intro-docking');
    if (root.classList.contains('intro-sequence')) root.classList.add('page-entering');
  };
  const clamp = (value) => Math.min(1, Math.max(0, value));

  const updateScroll = () => {
    scrollFrame = 0;
    if (document.hidden) return;

    // Read geometry as one batch before writing the exhibition's visual state.
    const viewportHeight = window.innerHeight;
    const range = root.scrollHeight - viewportHeight;
    const pageProgress = clamp(range > 0 ? window.scrollY / range : 0);
    const geometry = exhibits.map(({ section, stage }) => {
      const bounds = section.getBoundingClientRect();
      const travel = Math.max(bounds.height - viewportHeight, viewportHeight * 0.5);
      return { section, stage, phase: paused ? 0.5 : clamp(-bounds.top / travel) };
    });
    const chapterGeometry = chapters.map(({ link, target }) => ({ link, bounds: target.getBoundingClientRect() }));
    const chapterLine = viewportHeight * 0.42;
    const currentChapter = (chapterGeometry.find(({ bounds }) => bounds.top <= chapterLine && bounds.bottom > chapterLine)
      || chapterGeometry.find(({ bounds }) => bounds.top < viewportHeight && bounds.bottom > 0))?.link;

    if (progress) progress.style.transform = `scaleX(${pageProgress})`;
    geometry.forEach(({ section, stage, phase }) => {
      const value = phase.toFixed(4);
      section.style.setProperty('--phase', value);
      if (stage) stage.style.setProperty('--phase', value);
    });
    chapters.forEach(({ link }) => {
      if (link === currentChapter) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  };
  const scheduleScroll = () => {
    if (!scrollFrame && !document.hidden) scrollFrame = window.requestAnimationFrame(updateScroll);
  };
  const resetPosterTilt = () => {
    if (tiltFrame) window.cancelAnimationFrame(tiltFrame);
    tiltFrame = 0;
    pointerPosition = null;
    if (introPoster) {
      introPoster.style.setProperty('--tilt-x', '0deg');
      introPoster.style.setProperty('--tilt-y', '0deg');
    }
  };
  const updatePosterTilt = () => {
    tiltFrame = 0;
    if (!introPoster || !pointerPosition || paused || document.hidden || !finePointer.matches) {
      resetPosterTilt();
      return;
    }
    const bounds = introPoster.getBoundingClientRect();
    const horizontal = clamp((pointerPosition.x - bounds.left) / Math.max(bounds.width, 1)) * 2 - 1;
    const vertical = clamp((pointerPosition.y - bounds.top) / Math.max(bounds.height, 1)) * 2 - 1;
    introPoster.style.setProperty('--tilt-x', `${(-vertical * 4).toFixed(2)}deg`);
    introPoster.style.setProperty('--tilt-y', `${(horizontal * 4).toFixed(2)}deg`);
  };
  introPoster?.addEventListener('pointermove', (event) => {
    if (paused || document.hidden || !finePointer.matches) return;
    pointerPosition = { x: event.clientX, y: event.clientY };
    if (!tiltFrame) tiltFrame = window.requestAnimationFrame(updatePosterTilt);
  }, { passive: true });
  introPoster?.addEventListener('pointerleave', resetPosterTilt, { passive: true });
  finePointer.addEventListener('change', resetPosterTilt);
  const setMotion = () => {
    paused = reducedMotion.matches;
    root.classList.toggle('motion-paused', paused);
    root.classList.toggle('js-motion', !paused);
    if (paused) {
      finishIntro();
      document.querySelectorAll('.reveal').forEach((element) => element.classList.add('is-visible'));
      resetPosterTilt();
      priceAnimation?.cancel();
      priceAnimation = null;
    }
    updateAmbient();
    scheduleScroll();
  };
  reducedMotion.addEventListener('change', setMotion);
  const toggleNotes = () => {
    const enabled = !root.classList.contains('notes-mode');
    root.classList.toggle('notes-mode', enabled);
    document.body.classList.toggle('notes-mode', enabled);
    notesButtons.forEach((button) => {
      button.setAttribute('aria-pressed', String(enabled));
      const label = button.querySelector('#notes-label, [data-notes-label]') || button;
      label.textContent = enabled ? 'Notes on' : 'Notes off';
    });
    scheduleScroll();
  };
  notesButtons.forEach((button) => button.addEventListener('click', toggleNotes));
  const reveals = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        reveals.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach((element) => reveals.observe(element));

  // Ambient animation is suspended outside the viewport and while the tab is hidden.
  const ambient = document.querySelectorAll('[data-ambient], .asterisk, .tiny-orbit, .ticker-track, .radar-sweep, .radar-point, .footer-star, .gallery-marquee-track');
  const visibleAmbient = new Set();
  const updateAmbient = () => ambient.forEach((element) => {
    element.style.animationPlayState = !paused && !document.hidden && visibleAmbient.has(element) ? 'running' : 'paused';
  });
  const ambientObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => entry.isIntersecting ? visibleAmbient.add(entry.target) : visibleAmbient.delete(entry.target));
    updateAmbient();
  });
  ambient.forEach((element) => ambientObserver.observe(element));
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && scrollFrame) {
      window.cancelAnimationFrame(scrollFrame);
      scrollFrame = 0;
    }
    if (document.hidden) {
      resetPosterTilt();
      priceAnimation?.cancel();
      priceAnimation = null;
    }
    updateAmbient();
    scheduleScroll();
  });
  window.addEventListener('scroll', scheduleScroll, { passive: true });
  window.addEventListener('resize', scheduleScroll, { passive: true });
  window.addEventListener('load', scheduleScroll, { once: true });
  document.fonts?.ready.then(scheduleScroll);
  setMotion();

  // A brief brand entrance on the home view; deep links stay immediately visible.
  if (!paused && (!window.location.hash || window.location.hash === '#top') && window.scrollY < 20
      && performance.getEntriesByType('navigation')[0]?.type !== 'back_forward') {
    root.classList.add('intro-sequence', 'intro-playing');
    const dockLogo = () => {
      const logo = document.querySelector('.opening-brand img');
      const masthead = document.querySelector('.masthead');
      if (!logo || !masthead || paused || !root.classList.contains('intro-playing')) {
        finishIntro();
        return;
      }
      const start = logo.getBoundingClientRect();
      const destination = masthead.getBoundingClientRect();
      if (!start.width || !destination.width) { finishIntro(); return; }
      logo.style.setProperty('--dock-transform', `translate(${destination.left - start.left}px, ${destination.top - start.top}px) scale(${destination.width / start.width})`);
      root.classList.add('intro-docking');
      introTimer = window.setTimeout(finishIntro, 1830);
    };
    introTimer = window.setTimeout(dockLogo, 1700);
    ['pointerdown', 'keydown', 'wheel', 'touchstart'].forEach((event) => {
      window.addEventListener(event, finishIntro, { once: true, passive: true });
    });
    window.addEventListener('resize', finishIntro, { once: true, passive: true });
  }

  const scenarios = {
    manchester: { prompt: '“Find me headphones in Manchester.”', product: 'Wireless headphones · new · one item', total: '£189', item: '£209', coupon: '−£20', shipping: '£0', other: '£219 total', risky: '£139 + unknown fees' },
    jakarta: { prompt: '“Find me a laptop in Jakarta.”', product: 'Same laptop variant · new · one item', total: 'Rp6.850.000', item: 'Rp7.100.000', coupon: '−Rp250.000', shipping: 'Rp0', other: 'Rp7.250.000 total', risky: 'Rp5.900.000 + unknown fees' },
    osaka: { prompt: '“Find me a camera in Osaka.”', product: 'Same camera body · new · one item', total: '¥89,800', item: '¥94,800', coupon: '−¥5,000', shipping: '¥0', other: '¥98,500 total', risky: '¥72,000 + unknown fees' }
  };
  let scenario = 'manchester';
  let runId = 0;
  const demo = document.querySelector('.demo');
  const play = document.getElementById('demo-play');
  const steps = [...document.querySelectorAll('.research-steps li')];
  const demoStatus = document.getElementById('demo-progress');
  const displayScenario = (key) => {
    const data = scenarios[key];
    Object.entries(data).forEach(([field, value]) => { document.getElementById(`demo-${field}`).textContent = value; });
    const total = document.getElementById('demo-total');
    total.classList.toggle('long-price', key === 'jakarta');
    priceAnimation?.cancel();
    priceAnimation = null;
    if (!paused && !document.hidden && typeof total.animate === 'function') {
      const animation = total.animate([
        { opacity: 0.3, transform: 'translateY(9px)' },
        { opacity: 1, transform: 'translateY(0)' }
      ], { duration: 450, easing: 'ease-out' });
      priceAnimation = animation;
      animation.onfinish = () => { if (priceAnimation === animation) priceAnimation = null; };
    }
  };
  const resetDemo = () => {
    runId += 1;
    demo.classList.remove('is-running');
    steps.forEach((step) => step.classList.remove('is-active'));
    play.disabled = false;
    play.innerHTML = 'Explore the search <span aria-hidden="true">↗</span>';
    demoStatus.textContent = 'Explore an illustrative comparison.';
  };
  document.querySelectorAll('[data-scenario]').forEach((button) => button.addEventListener('click', () => {
    resetDemo();
    scenario = button.dataset.scenario;
    document.querySelectorAll('[data-scenario]').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    displayScenario(scenario);
  }));
  play.addEventListener('click', async () => {
    resetDemo();
    const thisRun = runId;
    play.disabled = true;
    play.textContent = 'Exploring the example…';
    demo.classList.add('is-running');
    const messages = ['Discovering sources near the example destination.', 'Keeping matching models and variants together.', 'Separating coupons, shipping, and unknown fees.', 'Comparing seller and warranty evidence.'];
    for (let index = 0; index < steps.length; index += 1) {
      if (!paused) await new Promise((resolve) => window.setTimeout(resolve, 650));
      if (runId !== thisRun) return;
      steps[index].classList.add('is-active');
      demoStatus.textContent = messages[index];
    }
    if (runId !== thisRun) return;
    demoStatus.textContent = 'Example complete. Offer B has the lowest supported comparable total in this fictional shortlist.';
    play.disabled = false;
    play.innerHTML = 'Replay the example <span aria-hidden="true">↻</span>';
  });

  const installs = {
    codex: { instruction: 'Add the public repository as a marketplace, then install:', code: 'codex plugin marketplace add alfahricireng12/buyless\ncodex plugin add buyless@buyless-community', note: 'Open a new supported host session after installation. Plugin and web-tool availability depend on your host.' },
    claude: { instruction: 'Download and extract the release. Inside the buyless folder, run:', code: 'node bin/buyless.mjs init --ai claude --global', note: 'Requires Node.js 20+. Start a new Claude Code session, then ask naturally or use /buyless. Your host needs web tools.' },
    cursor: { instruction: 'Download and extract the release. Inside the buyless folder, run:', code: 'node bin/buyless.mjs init --ai cursor --global', note: 'Requires Node.js 20+. Open a new Cursor session after installation. Skill activation and web tools depend on your host settings.' }
  };
  const code = document.getElementById('install-code');
  const copyStatus = document.getElementById('copy-status');
  document.querySelectorAll('[data-host]').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('[data-host]').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    const data = installs[button.dataset.host];
    code.textContent = data.code;
    document.getElementById('install-instruction').textContent = data.instruction;
    document.getElementById('install-note').textContent = data.note;
    copyStatus.textContent = '';
  }));
  document.getElementById('copy-command').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(code.textContent);
      copyStatus.textContent = 'Copied. Paste into your terminal when ready.';
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(code);
      selection.removeAllRanges();
      selection.addRange(range);
      copyStatus.textContent = 'Copy access unavailable. Command selected: use Ctrl+C or ⌘C.';
    }
  });
})();
