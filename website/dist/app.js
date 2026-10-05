(() => {
  'use strict';
  const root = document.documentElement;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionButton = document.getElementById('motion-toggle');
  let paused = reducedMotion.matches;
  let manualMotionChoice = false;
  const setMotion = (value) => {
    value = value || reducedMotion.matches;
    paused = value;
    root.classList.toggle('motion-paused', value);
    root.classList.toggle('js-motion', !value);
    motionButton.setAttribute('aria-pressed', String(value));
    motionButton.disabled = reducedMotion.matches;
    document.getElementById('motion-label').textContent = reducedMotion.matches ? 'Reduced motion' : value ? 'Enable motion' : 'Pause motion';
  };
  setMotion(paused);
  motionButton.addEventListener('click', () => {
    manualMotionChoice = true;
    setMotion(!paused);
  });
  reducedMotion.addEventListener('change', (event) => {
    setMotion(manualMotionChoice ? paused : event.matches);
  });
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
  const ambient = document.querySelectorAll('.asterisk, .tiny-orbit, .ticker-track, .radar-sweep, .radar-point, .footer-star');
  const visibleAmbient = new Set();
  const updateAmbient = () => ambient.forEach((element) => {
    element.style.animationPlayState = !document.hidden && visibleAmbient.has(element) ? 'running' : 'paused';
  });
  const ambientObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => entry.isIntersecting ? visibleAmbient.add(entry.target) : visibleAmbient.delete(entry.target));
    updateAmbient();
  });
  ambient.forEach((element) => ambientObserver.observe(element));
  document.addEventListener('visibilitychange', updateAmbient);

  const progress = document.querySelector('.reading-progress');
  let framePending = false;
  const updateScroll = () => {
    const range = root.scrollHeight - window.innerHeight;
    progress.style.transform = `scaleX(${range > 0 ? window.scrollY / range : 0})`;
    framePending = false;
  };
  window.addEventListener('scroll', () => {
    if (!framePending) { framePending = true; window.requestAnimationFrame(updateScroll); }
  }, { passive: true });
  window.addEventListener('resize', updateScroll);
  updateScroll();

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
    document.getElementById('demo-total').classList.toggle('long-price', key === 'jakarta');
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
