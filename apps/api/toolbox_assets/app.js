const TOOL_CONFIG = window.__AI_TOOLBOX_CONFIG__ || {};
const RUNTIME_ENDPOINT = '/api/ai-toolbox/runtime';
const RUN_ENDPOINT = '/api/ai-toolbox/run';
const PHASE_LABELS = { foundation: '基础阶段', practice: '练习阶段', project: '项目阶段', review: '复盘阶段' };
const QUESTION_TYPE_LABELS = { fundamental: '基础理解', coding: '编码题', debugging: '排障题', scenario: '场景题' };
const SECTION_LABELS = { skills: '技能', experience: '经历', projects: '项目' };
const RUNTIME_RECOMMENDATIONS = {
  mock: { provider: 'mock', base_url: '', model: 'mock', api_key: '' },
  ollama: { provider: 'ollama', base_url: 'http://127.0.0.1:11434', model: 'qwen2.5:3b-instruct', api_key: 'local' },
  openai: { provider: 'openai', base_url: 'https://api.openai.com/v1', model: 'gpt-4o-mini', api_key: '' }
};

const toolSelect = document.getElementById('tool-select');
const toolTitle = document.getElementById('tool-title');
const toolDescription = document.getElementById('tool-description');
const toolTip = document.getElementById('tool-tip');
const fieldsContainer = document.getElementById('fields-container');
const toolForm = document.getElementById('tool-form');
const renderedResult = document.getElementById('rendered-result');
const statusBadge = document.getElementById('status-badge');
const statusMessage = document.getElementById('status-message');
const errorMessage = document.getElementById('error-message');
const httpStatus = document.getElementById('http-status');
const resetButton = document.getElementById('reset-button');
const submitButton = document.getElementById('submit-button');
const runtimeButton = document.getElementById('runtime-button');
const runtimeSummary = document.getElementById('runtime-summary');
const runtimeOverlay = document.getElementById('runtime-overlay');
const runtimeClose = document.getElementById('runtime-close');
const runtimeForm = document.getElementById('runtime-form');
const runtimeProvider = document.getElementById('runtime-provider');
const runtimeBaseUrl = document.getElementById('runtime-base-url');
const runtimeModel = document.getElementById('runtime-model');
const runtimeApiKey = document.getElementById('runtime-api-key');
const runtimeRecommend = document.getElementById('runtime-recommend');
const runtimeCurrentStatus = document.getElementById('runtime-current-status');
const runtimeMessage = document.getElementById('runtime-message');

let runtimeState = null;
let lastPayload = null;
let lastResponse = null;
let studyExpanded = false;

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function setStatus(kind, badgeText, message, httpText = '未提交') {
  statusBadge.textContent = badgeText;
  statusBadge.className = `status ${kind}`;
  statusMessage.textContent = message;
  httpStatus.textContent = httpText;
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.remove('hidden');
}

function hideError() {
  errorMessage.textContent = '';
  errorMessage.classList.add('hidden');
}

function showRuntimeMessage(message, kind = 'info') {
  runtimeMessage.textContent = message;
  runtimeMessage.className = kind === 'error' ? 'runtime-message error' : 'runtime-message';
  runtimeMessage.classList.remove('hidden');
}

function hideRuntimeMessage() {
  runtimeMessage.textContent = '';
  runtimeMessage.className = 'runtime-message hidden';
}

function createField(field) {
  const wrapper = document.createElement('label');
  wrapper.className = 'field';
  const title = document.createElement('span');
  title.textContent = field.label;
  wrapper.appendChild(title);
  let input;
  if (field.type === 'textarea') {
    input = document.createElement('textarea');
    input.rows = field.rows || 4;
  } else if (field.type === 'select') {
    input = document.createElement('select');
    (field.options || []).forEach((option) => {
      const el = document.createElement('option');
      el.value = option.value ?? '';
      el.textContent = option.label ?? option.value ?? '';
      input.appendChild(el);
    });
  } else {
    input = document.createElement('input');
    input.type = field.type || 'text';
  }
  input.name = field.name;
  if (field.type === 'number') {
    if (field.min !== undefined) input.min = field.min;
    if (field.max !== undefined) input.max = field.max;
    if (field.step !== undefined) input.step = field.step;
  }
  input.value = field.value ?? '';
  wrapper.appendChild(input);
  return wrapper;
}

function renderTool(toolName) {
  const config = TOOL_CONFIG[toolName];
  studyExpanded = false;
  toolTitle.textContent = config.label;
  toolDescription.textContent = config.description;
  toolTip.textContent = config.tip || '';
  fieldsContainer.innerHTML = '';
  config.fields.forEach((field) => fieldsContainer.appendChild(createField(field)));
  renderedResult.textContent = '生成完成后，这里会显示整理好的结果。';
  renderedResult.classList.add('empty');
  hideError();
  setStatus('idle', '准备就绪', '填写信息后点击“开始生成”。');
}

function collectPayload() {
  const config = TOOL_CONFIG[toolSelect.value];
  const payload = { tool_name: toolSelect.value, task: config.task, input: {} };
  config.fields.forEach((field) => {
    const input = fieldsContainer.querySelector(`[name="${field.name}"]`);
    if (!input) return;
    if (field.type === 'number') {
      payload.input[field.name] = input.value.includes('.') ? Number.parseFloat(input.value) : Number.parseInt(input.value, 10);
    } else {
      payload.input[field.name] = input.value;
    }
  });
  return payload;
}

function renderStudyPlan(result) {
  const schedule = result.schedule || [];
  const visible = studyExpanded ? schedule : schedule.slice(0, 7);
  const hidden = Math.max(schedule.length - visible.length, 0);
  const cards = visible.map((item) => `
    <article class="result-card">
      <div class="result-card-title">第 ${item.day} 天 · ${escapeHtml(PHASE_LABELS[item.phase] || item.phase)}</div>
      <div class="result-card-meta">预计 ${escapeHtml(item.estimated_hours)} 小时</div>
      <ul>${(item.tasks || []).map((task) => `<li>${escapeHtml(task)}</li>`).join('')}</ul>
    </article>
  `).join('');
  return `
    <section class="result-section">
      <h3>学习计划总览</h3>
      <div class="summary-grid">
        <div class="summary-item"><span>目标</span><strong>${escapeHtml(result.goal)}</strong></div>
        <div class="summary-item"><span>总天数</span><strong>${escapeHtml(result.duration_days)} 天</strong></div>
        <div class="summary-item"><span>每天时长</span><strong>${escapeHtml(result.hours_per_day)} 小时</strong></div>
        <div class="summary-item"><span>当前水平</span><strong>${escapeHtml(result.level)}</strong></div>
      </div>
    </section>
    <section class="result-section"><h3>计划说明</h3><p>${escapeHtml(result.summary || '')}</p></section>
    <section class="result-section"><h3>重点方向</h3><ul>${(result.focus_areas || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('') || '<li>暂无</li>'}</ul></section>
    <section class="result-section"><h3>每周检查点</h3><ul>${(result.weekly_checkpoints || []).map((item) => `<li>第 ${item.day} 天：${escapeHtml(item.goal_check)}</li>`).join('') || '<li>暂无</li>'}</ul></section>
    <section class="result-section"><h3>每日安排</h3><div class="result-card-grid">${cards}</div>${hidden > 0 ? `<button class="secondary inline-button" data-toggle="expand" type="button">继续查看后 ${hidden} 天</button>` : ''}${studyExpanded && schedule.length > 7 ? '<button class="secondary inline-button" data-toggle="collapse" type="button">只看前 7 天</button>' : ''}</section>
  `;
}

function renderDocQa(result) {
  return `
    <section class="result-section"><h3>回答</h3><p>${escapeHtml(result.answer || '')}</p><p class="result-card-meta">置信度：${escapeHtml(result.confidence || '未提供')}</p></section>
    <section class="result-section"><h3>摘要</h3><p>${escapeHtml(result.summary || '')}</p></section>
    <section class="result-section"><h3>证据</h3><div class="result-card-grid">${(result.evidence || []).map((item) => `<article class="result-card"><div class="result-card-title">片段 ${escapeHtml(item.chunk_id)}</div><div class="result-card-meta">相关度：${escapeHtml(item.relevance)}</div><p>${escapeHtml(item.snippet)}</p></article>`).join('') || '<p>暂无</p>'}</div></section>
  `;
}

function renderResume(result) {
  return `
    <section class="result-section"><h3>匹配结果</h3><div class="summary-grid"><div class="summary-item"><span>目标岗位</span><strong>${escapeHtml(result.target_job || '')}</strong></div><div class="summary-item"><span>匹配分数</span><strong>${escapeHtml(result.match_score)}</strong></div><div class="summary-item summary-item-wide"><span>高优先级缺口</span><strong>${escapeHtml((result.high_priority_gaps || []).join('、') || '暂无')}</strong></div></div></section>
    <section class="result-section"><h3>优化建议</h3><div class="result-card-grid">${(result.rewrite_suggestions || []).map((item) => `<article class="result-card"><div class="result-card-title">${escapeHtml(SECTION_LABELS[item.section] || item.section || '建议')}</div><p>${escapeHtml(item.suggestion || '')}</p><div class="result-card-meta">${escapeHtml(item.reason || '')}</div></article>`).join('')}</div></section>
    <section class="result-section"><h3>ATS 小提示</h3><ul>${(result.ats_tips || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul></section>
  `;
}

function renderInterview(result) {
  return `
    <section class="result-section"><h3>面试题列表</h3><div class="summary-grid"><div class="summary-item"><span>岗位</span><strong>${escapeHtml(result.role || '')}</strong></div><div class="summary-item"><span>级别</span><strong>${escapeHtml(result.level || '')}</strong></div><div class="summary-item"><span>题目数量</span><strong>${escapeHtml(result.question_count)}</strong></div></div><div class="result-card-grid">${(result.questions || []).map((item) => `<article class="result-card"><div class="result-card-title">第 ${escapeHtml(item.id)} 题 · ${escapeHtml(QUESTION_TYPE_LABELS[item.type] || item.type)}</div><div class="result-card-meta">技能：${escapeHtml(item.skill || '')} / 难度：${escapeHtml(item.difficulty || '')}</div><p>${escapeHtml(item.question || '')}</p></article>`).join('')}</div></section>
  `;
}

function renderCode(result, payload) {
  return `
    <section class="result-section"><h3>解释结果</h3><p>${escapeHtml(result.summary || '')}</p><p class="result-card-meta">模式：${escapeHtml(result.mode || '未知')} / 提供方：${escapeHtml(result.provider || '未知')}</p><details class="code-toggle"><summary>查看代码</summary><pre class="code-preview">${escapeHtml(payload?.input?.code || '')}</pre></details></section>
    <section class="result-section"><h3>分段说明</h3><div class="result-card-grid">${(result.line_by_line || []).map((item) => `<article class="result-card"><div class="result-card-title">${escapeHtml(item.line_range || '')}</div><p>${escapeHtml(item.explanation || '')}</p></article>`).join('')}</div></section>
    <section class="result-section"><h3>风险提示</h3><ul>${(result.risks || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul></section>
    <section class="result-section"><h3>优化建议</h3><ul>${(result.improvements || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul></section>
  `;
}

function renderResponse(payload, body) {
  if (!body || body.status !== 'success' || !body.result) {
    renderedResult.textContent = '生成失败，请检查输入后重试。';
    renderedResult.classList.add('empty');
    return;
  }
  const result = body.result;
  let html = `<pre class="code-preview">${escapeHtml(JSON.stringify(result, null, 2))}</pre>`;
  if (payload.tool_name === 'study_planner') html = renderStudyPlan(result);
  if (payload.tool_name === 'doc_qa') html = renderDocQa(result);
  if (payload.tool_name === 'resume_optimizer') html = renderResume(result);
  if (payload.tool_name === 'interview_generator') html = renderInterview(result);
  if (payload.tool_name === 'code_explainer') html = renderCode(result, payload);
  renderedResult.innerHTML = html;
  renderedResult.classList.remove('empty');
}

function updateRuntimeSummary(state) {
  const provider = state?.provider || 'mock';
  const label = provider === 'mock' ? 'mock（演示）' : (provider === 'ollama' ? 'ollama（本地）' : 'openai（远程）');
  runtimeSummary.textContent = `当前模式：${label} | 模型：${state?.model || '未设置'}`;
  runtimeCurrentStatus.textContent = `已应用：${label} | 模型：${state?.model || '未设置'} | 地址：${state?.base_url || '无'} | API Key：${state?.api_key_present ? '已设置' : '未设置'}`;
}

function setRuntimeForm(state) {
  const provider = state?.provider || 'mock';
  const recommended = RUNTIME_RECOMMENDATIONS[provider] || RUNTIME_RECOMMENDATIONS.mock;
  runtimeProvider.value = provider;
  runtimeBaseUrl.value = state?.base_url ?? recommended.base_url;
  runtimeModel.value = state?.model ?? recommended.model;
  runtimeApiKey.value = '';
  updateRuntimeFormState();
}

function updateRuntimeFormState() {
  const provider = runtimeProvider.value || 'mock';
  const isMock = provider === 'mock';
  runtimeBaseUrl.disabled = isMock;
  runtimeModel.disabled = isMock;
  runtimeApiKey.disabled = isMock;
}

async function loadRuntime() {
  try {
    const response = await fetch(RUNTIME_ENDPOINT);
    const body = await response.json();
    if (!response.ok || !body?.ok || !body.data) throw new Error(body?.error || '加载失败');
    runtimeState = body.data;
    updateRuntimeSummary(runtimeState);
    setRuntimeForm(runtimeState);
  } catch {
    runtimeSummary.textContent = '挡位状态加载失败';
    runtimeCurrentStatus.textContent = '暂时无法获取当前挡位。';
  }
}

async function applyRuntime(event) {
  event.preventDefault();
  hideRuntimeMessage();
  const payload = { provider: runtimeProvider.value, base_url: runtimeBaseUrl.value.trim(), model: runtimeModel.value.trim(), api_key: runtimeApiKey.value.trim() };
  if (payload.provider === 'openai' && !payload.api_key && !runtimeState?.api_key_present) {
    showRuntimeMessage('请先填写 OpenAI 挡位的 API Key。', 'error');
    return;
  }
  try {
    const response = await fetch(RUNTIME_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const body = await response.json();
    if (!response.ok || !body?.ok || !body.data) throw new Error(body?.error || '应用失败');
    runtimeState = body.data;
    updateRuntimeSummary(runtimeState);
    setRuntimeForm(runtimeState);
    setStatus('success', '已应用', '挡位设置已更新，可以继续使用。', httpStatus.textContent);
    runtimeOverlay.classList.add('hidden');
  } catch (error) {
    showRuntimeMessage(error?.message || '应用失败，请稍后再试。', 'error');
  }
}

async function submitPayload(event) {
  event.preventDefault();
  hideError();
  if (runtimeState?.provider === 'openai' && !runtimeState.api_key_present) {
    showError('当前是 OpenAI 挡位，请先在右上角“设置挡位”里填写 API Key。');
    runtimeOverlay.classList.remove('hidden');
    return;
  }
  const payload = collectPayload();
  studyExpanded = false;
  lastPayload = payload;
  setStatus('loading', '处理中', '正在生成结果，请稍候...', '请求中');
  renderedResult.textContent = '正在生成结果，请稍候...';
  renderedResult.classList.add('empty');
  submitButton.disabled = true;
  try {
    const response = await fetch(RUN_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const body = await response.json();
    lastResponse = body;
    if (response.ok && body.status === 'success') {
      setStatus('success', '已完成', '结果已生成，可以直接查看。', `HTTP ${response.status}`);
      renderResponse(payload, body);
    } else {
      setStatus('error', '失败', '这次没有成功生成结果。', `HTTP ${response.status}`);
      showError(body?.error?.message || '生成失败，请稍后再试。');
      renderResponse(payload, null);
    }
  } catch (error) {
    setStatus('error', '失败', '请求没有成功发到服务端。', '网络异常');
    showError('请检查服务是否正常运行：' + String(error));
    renderResponse(payload, null);
  } finally {
    submitButton.disabled = false;
  }
}

Object.entries(TOOL_CONFIG).forEach(([toolName, config]) => {
  const option = document.createElement('option');
  option.value = toolName;
  option.textContent = config.label;
  toolSelect.appendChild(option);
});

toolSelect.addEventListener('change', () => renderTool(toolSelect.value));
resetButton.addEventListener('click', () => renderTool(toolSelect.value));
toolForm.addEventListener('submit', submitPayload);
runtimeButton.addEventListener('click', () => { runtimeOverlay.classList.remove('hidden'); hideRuntimeMessage(); });
runtimeClose.addEventListener('click', () => runtimeOverlay.classList.add('hidden'));
runtimeOverlay.addEventListener('click', (event) => { if (event.target === runtimeOverlay) runtimeOverlay.classList.add('hidden'); });
runtimeProvider.addEventListener('change', updateRuntimeFormState);
runtimeRecommend.addEventListener('click', () => {
  const data = RUNTIME_RECOMMENDATIONS[runtimeProvider.value] || RUNTIME_RECOMMENDATIONS.mock;
  runtimeBaseUrl.value = data.base_url; runtimeModel.value = data.model; runtimeApiKey.value = data.api_key; updateRuntimeFormState();
});
runtimeForm.addEventListener('submit', applyRuntime);
renderedResult.addEventListener('click', (event) => {
  const trigger = event.target.closest('[data-toggle]');
  if (!trigger || !lastPayload || !lastResponse || lastPayload.tool_name !== 'study_planner') return;
  studyExpanded = trigger.dataset.toggle === 'expand';
  renderResponse(lastPayload, lastResponse);
});

renderTool('study_planner');
loadRuntime();
