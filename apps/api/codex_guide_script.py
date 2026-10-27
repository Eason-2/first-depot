"""Progressively enhance the static lesson; no account or key data is collected."""

GUIDE_SCRIPT = """
<script>
document.addEventListener('DOMContentLoaded', () => {
  const guide = document.getElementById('codex-start');
  const steps = [...guide.querySelectorAll('[data-step]')];
  const osChoices = [...guide.querySelectorAll('[name="guide-os"]')];
  const authSelect = guide.querySelector('#guide-auth');
  const stepSelect = guide.querySelector('#guide-step-select');
  const readAll = guide.querySelector('#guide-read-all');
  const status = guide.querySelector('#guide-reading-status');
  const previous = guide.querySelector('[data-previous]');
  const next = guide.querySelector('[data-next]');
  let current = 0;
  let fullText = false;

  function setPlatform(value) {
    osChoices.forEach(input => { input.checked = input.value === value; });
    guide.querySelectorAll('[data-guide-os]').forEach(part => {
      part.hidden = part.dataset.guideOs !== value;
    });
    guide.querySelector('#guide-os-status').textContent = value === 'mac'
      ? '已切换到 macOS，命令使用 zsh。' : '已切换到 Windows，命令使用 PowerShell。';
  }
  function setAuth(value) {
    authSelect.value = value;
    guide.querySelectorAll('[data-auth]').forEach(part => { part.hidden = part.dataset.auth !== value; });
    guide.querySelectorAll('[data-route-choice]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.routeChoice === value));
    });
  }
  function showStep(index) {
    current = index;
    steps.forEach((step, i) => { step.hidden = !fullText && i !== current; });
    guide.querySelectorAll('[data-step-link]').forEach((link, i) => {
      if (i === current) link.setAttribute('aria-current', 'step');
      else link.removeAttribute('aria-current');
    });
    stepSelect.value = steps[current].id;
    status.textContent = fullText ? '全文 · 6 个步骤' : `第 ${current + 1} 步 / 共 ${steps.length} 步`;
    previous.hidden = current === 0;
    previous.href = '#' + steps[Math.max(0, current - 1)].id;
    next.href = current < steps.length - 1 ? '#' + steps[current + 1].id : '#first-task';
    next.textContent = current < steps.length - 1 ? '下一步：' + steps[current + 1].dataset.shortTitle : '选做：做一个网页';
    guide.querySelector('.lesson-controls').hidden = fullText;
  }
  function revealHash(scroll = true) {
    const target = document.getElementById(location.hash.slice(1));
    if (!target) return;
    const step = target.closest('[data-step]');
    const route = target.closest('[data-auth]');
    if (route) setAuth(route.dataset.auth);
    if (step) showStep(steps.indexOf(step));
    let node = target;
    while (node && node !== document.body) {
      if (node.tagName === 'DETAILS') node.open = true;
      node = node.parentElement;
    }
    if (scroll) requestAnimationFrame(() => {
      const scrollTarget = step === target && !fullText ? guide.querySelector('.lesson-paper') : target;
      scrollTarget.scrollIntoView({block: 'start'});
      if (step) step.focus({preventScroll: true});
    });
  }
  osChoices.forEach(input => input.addEventListener('change', () => setPlatform(input.value)));
  authSelect.addEventListener('change', () => {
    setAuth(authSelect.value);
    // Keep a Key-specific fragment from describing the account route after a switch.
    const target = document.getElementById(location.hash.slice(1));
    if (target?.closest('[data-auth]')) history.replaceState(null, '', '#' + steps[current].id);
  });
  guide.querySelectorAll('[data-route-choice]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => setAuth(button.dataset.routeChoice));
  });
  stepSelect.addEventListener('change', () => {
    if (location.hash === '#' + stepSelect.value) revealHash();
    else location.hash = stepSelect.value;
  });
  readAll.addEventListener('click', () => {
    fullText = !fullText;
    readAll.setAttribute('aria-pressed', String(fullText));
    readAll.textContent = fullText ? '返回分步阅读' : '阅读全文';
    showStep(current);
    if (!fullText) guide.querySelector('.lesson-paper').scrollIntoView({block: 'start'});
  });
  window.addEventListener('hashchange', () => revealHash());
  document.querySelector('.tutorials-page').addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (link && link.hash === location.hash) revealHash();
  });
  guide.querySelectorAll('[data-enhance]').forEach(element => { element.hidden = false; });
  // New visits always start on Windows; a specific Key link may select the API route.
  setPlatform('windows');
  setAuth('account');
  showStep(0);
  revealHash(Boolean(location.hash));

  guide.querySelectorAll('.guide-copy').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const code = button.closest('.guide-code').querySelector('code');
      const feedback = guide.querySelector('.guide-copy-status');
      try {
        await navigator.clipboard.writeText(code.textContent);
        button.textContent = '已复制';
        feedback.textContent = '已复制，请粘贴到代码框上方标注的位置。';
      } catch {
        const range = document.createRange();
        range.selectNodeContents(code);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = '请手动复制';
        feedback.textContent = '已选中文字，请使用系统复制快捷键。';
      }
      setTimeout(() => { button.textContent = '复制'; }, 2500);
    });
  });
});
</script>
"""
