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
  const walkthroughs = [...guide.querySelectorAll('[data-walkthrough]')];
  const scenePositions = new Map();

  function visibleScenes(walk) {
    const os = guide.querySelector('[name="guide-os"]:checked').value;
    return [...walk.querySelectorAll('[data-scene]')].filter(scene =>
      (!scene.dataset.sceneOs || scene.dataset.sceneOs === os) &&
      (!scene.dataset.sceneAuth || scene.dataset.sceneAuth === authSelect.value));
  }
  function updateWalkthroughs() {
    walkthroughs.forEach(walk => {
      const eligible = visibleScenes(walk);
      const index = Math.min(scenePositions.get(walk) || 0, eligible.length - 1);
      scenePositions.set(walk, index);
      walk.querySelectorAll('[data-scene]').forEach(scene => {
        scene.hidden = !eligible.includes(scene) || (!fullText && scene !== eligible[index]);
      });
      walk.querySelector('[data-scene-count]').textContent = `本章第 ${index + 1} 步 / 共 ${eligible.length} 步`;
      walk.querySelector('.walk-reading').hidden = fullText;
      walk.querySelector('.walk-controls').hidden = fullText;
      walk.querySelector('[data-scene-prev]').disabled = index === 0;
      walk.querySelector('[data-scene-next]').hidden = index === eligible.length - 1;
      walk.querySelector('[data-scene-replay]').hidden = index !== eligible.length - 1;
      walk.querySelector('.walk-proof').hidden = !fullText && index !== eligible.length - 1;
    });
    const active = walkthroughs[current];
    guide.querySelector('.lesson-controls').hidden = fullText || scenePositions.get(active) < visibleScenes(active).length - 1;
  }
  function resetWalkthroughs() {
    scenePositions.clear();
    guide.querySelectorAll('[data-proof]').forEach(input => { input.checked = false; });
    updateWalkthroughs();
  }

  function setPlatform(value) {
    osChoices.forEach(input => { input.checked = input.value === value; });
    guide.querySelectorAll('[data-guide-os]').forEach(part => {
      part.hidden = part.dataset.guideOs !== value;
    });
    guide.querySelector('#guide-os-status').textContent = value === 'mac'
      ? '已切换到 macOS，命令使用 zsh。' : '已切换到 Windows，命令使用 PowerShell。';
    resetWalkthroughs();
  }
  function setAuth(value) {
    authSelect.value = value;
    guide.querySelectorAll('[data-auth]').forEach(part => { part.hidden = part.dataset.auth !== value; });
    guide.querySelectorAll('[data-route-choice]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.routeChoice === value));
    });
    resetWalkthroughs();
  }
  function showStep(index) {
    current = index;
    steps.forEach((step, i) => { step.hidden = !fullText && i !== current; });
    guide.querySelectorAll('[data-step-link]').forEach((link, i) => {
      if (i === current) link.setAttribute('aria-current', 'step');
      else link.removeAttribute('aria-current');
    });
    stepSelect.value = steps[current].id;
    status.textContent = fullText ? '全部操作 · 6 个章节' : `第 ${current + 1} 章 / 共 ${steps.length} 章`;
    previous.hidden = current === 0;
    previous.href = '#' + steps[Math.max(0, current - 1)].id;
    next.href = current < steps.length - 1 ? '#' + steps[current + 1].id : '#first-task';
    next.textContent = current < steps.length - 1 ? '下一章：' + steps[current + 1].dataset.shortTitle : '选做：做一个网页';
    updateWalkthroughs();
  }
  function revealHash(scroll = true) {
    const target = document.getElementById(location.hash.slice(1));
    if (!target) return;
    const step = target.closest('[data-step]');
    const route = target.closest('[data-auth]');
    const scene = target.closest('[data-scene]');
    if (route && route.dataset.auth !== authSelect.value) setAuth(route.dataset.auth);
    if (scene?.dataset.sceneAuth && scene.dataset.sceneAuth !== authSelect.value) setAuth(scene.dataset.sceneAuth);
    if (scene?.dataset.sceneOs && scene.dataset.sceneOs !== guide.querySelector('[name="guide-os"]:checked').value) setPlatform(scene.dataset.sceneOs);
    if (scene) {
      const walk = scene.closest('[data-walkthrough]');
      scenePositions.set(walk, visibleScenes(walk).indexOf(scene));
    }
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
  osChoices.forEach(input => input.addEventListener('change', () => {
    setPlatform(input.value);
    const target = document.getElementById(location.hash.slice(1));
    if (target?.closest('[data-scene]')) history.replaceState(null, '', '#' + steps[current].id);
  }));
  authSelect.addEventListener('change', () => {
    setAuth(authSelect.value);
    // Keep a Key-specific fragment from describing the account route after a switch.
    const target = document.getElementById(location.hash.slice(1));
    if (target?.closest('[data-auth]') || target?.closest('[data-scene]')) history.replaceState(null, '', '#' + steps[current].id);
  });
  guide.querySelectorAll('[data-route-choice]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => {
      setAuth(button.dataset.routeChoice);
      history.replaceState(null, '', '#' + steps[current].id);
    });
  });
  walkthroughs.forEach(walk => {
    walk.querySelector('[data-proof]').disabled = false;
    walk.querySelectorAll('[data-scene-prev],[data-scene-next],[data-scene-replay]').forEach(button => {
      button.addEventListener('click', () => {
        const index = scenePositions.get(walk) || 0;
        const target = button.hasAttribute('data-scene-replay') ? 0 : index + (button.hasAttribute('data-scene-prev') ? -1 : 1);
        scenePositions.set(walk, target);
        updateWalkthroughs();
        const scene = visibleScenes(walk)[target];
        history.replaceState(null, '', '#' + scene.id);
        const heading = scene.querySelector('h3');
        heading.tabIndex = -1;
        heading.focus({preventScroll:true});
        walk.scrollIntoView({block:'start'});
      });
    });
  });
  guide.querySelectorAll('[data-env-demo]').forEach(demo => {
    demo.querySelector('.walk-demo-actions').hidden = false;
    const save = demo.querySelector('[data-demo-save]');
    demo.querySelector('[data-demo-fill]').addEventListener('click', () => {
      demo.querySelector('[data-demo-value]').textContent = 'DEMO-KEY-NOT-VALID';
      demo.querySelector('.walk-demo-feedback').textContent = '演示值已填入。下一步练习点“确定”。';
      save.disabled = false;
    });
    save.addEventListener('click', () => {
      demo.querySelector('.walk-demo-feedback').textContent = '网页练习完成。现在到自己的 Windows 设置里填写真实 Key，再逐层点“确定”。';
      save.disabled = true;
    });
  });
  stepSelect.addEventListener('change', () => {
    if (location.hash === '#' + stepSelect.value) revealHash();
    else location.hash = stepSelect.value;
  });
  readAll.addEventListener('click', () => {
    fullText = !fullText;
    readAll.setAttribute('aria-pressed', String(fullText));
    readAll.textContent = fullText ? '返回分步跟练' : '展开全部操作';
    showStep(current);
    if (!fullText) guide.querySelector('.lesson-paper').scrollIntoView({block: 'start'});
  });
  window.addEventListener('hashchange', () => revealHash());
  document.querySelector('.tutorials-page').addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (link && link.hash === location.hash) revealHash();
  });
  guide.querySelectorAll('[data-enhance]').forEach(element => { element.hidden = false; });
  // Default visits use Windows/account; explicit screen fragments select their own route.
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
