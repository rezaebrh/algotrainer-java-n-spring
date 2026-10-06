'use strict';

/* Browser front-end for the book. Chapter rendering is pure HTML/JS (so RTL is
   native). The quiz delegates to quiz_engine.py running under Pyodide, so the
   adaptive selection and mastery scoring stay one implementation shared with
   the CLI. Progress lives in localStorage in the same JSON shape the CLI
   writes to progress.json. */

const PYODIDE_VERSION = '314.0.7';
const PYODIDE_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
const STATE_KEY = 'javabook.progress.v2';
const BANK = 'grade-01';
const SESSION_SIZE = 3;

const CHAPTERS = ['01-building-blocks.md', '02-operators-control-flow.md'];

const $ = (selector) => document.querySelector(selector);

/* ---------- marked (vendored UMD; global is either the module or {marked}) ---------- */

function parseMarkdown(source) {
  const M = globalThis.marked;
  const parse = M && (M.parse ? M.parse : M.marked && M.marked.parse);
  if (!parse) throw new Error('marked بارگذاری نشد');
  return parse(String(source ?? ''), { gfm: true });
}

/* Render inline markdown without the surrounding <p>. */
function inlineMarkdown(source) {
  const html = parseMarkdown(source);
  const match = html.match(/^<p>([\s\S]*)<\/p>\s*$/);
  return match ? match[1] : html;
}

function esc(value) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  return String(value).replace(/[&<>"']/g, (c) => map[c]);
}

function setStatus(text) {
  $('#status').textContent = text || '';
}

/* ---------- asset base ----------
   Served locally from the repo root the page is at /web/, so assets are one
   level up. Deployed to Pages the site root holds them directly. Probing keeps
   one copy of these files working in both places. */

let assetBase = null;

async function headOk(path) {
  try {
    const response = await fetch(path, { method: 'HEAD' });
    return response.ok;
  } catch {
    return false;
  }
}

async function resolveBase() {
  if (assetBase) return assetBase;
  for (const candidate of ['./', '../']) {
    if (await headOk(candidate + 'quiz_engine.py')) {
      assetBase = candidate;
      return candidate;
    }
  }
  throw new Error('ریشهٔ پروژه پیدا نشد — پوشهٔ مخزن را سرو کنید، نه پوشهٔ web را');
}

/* ---------- progress state ---------- */

let cachedState = null;

function loadState() {
  if (cachedState) return cachedState;
  try {
    cachedState = JSON.parse(localStorage.getItem(STATE_KEY) || '{}');
  } catch {
    cachedState = {};
  }
  return cachedState;
}

function saveState(state) {
  cachedState = state;
  try {
    localStorage.setItem(STATE_KEY, JSON.stringify(state));
  } catch {
    /* private mode: keep working in memory */
  }
}

/* ---------- Pyodide bridge ---------- */

let pyBridge = null;

async function getBridge() {
  if (pyBridge) return pyBridge;
  setStatus('بارگذاری Pyodide… بار اول چند مگابایت دانلود می‌شود.');
  const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
  const base = await resolveBase();

  const bridgePath = (await headOk(base + 'quiz_bridge.py'))
    ? base + 'quiz_bridge.py'
    : base + 'web/quiz_bridge.py';

  for (const [name, url] of [
    ['quiz_engine.py', base + 'quiz_engine.py'],
    ['quiz_bridge.py', bridgePath],
  ]) {
    pyodide.FS.writeFile('/home/pyodide/' + name, await (await fetch(url)).text());
  }

  pyodide.runPython('import quiz_bridge');
  pyBridge = {
    select: pyodide.runPython('quiz_bridge.select'),
    grade: pyodide.runPython('quiz_bridge.grade'),
    summary: pyodide.runPython('quiz_bridge.summary'),
  };
  setStatus('');
  return pyBridge;
}

/* ---------- chapters ---------- */

let chapters = [];

async function loadChapters() {
  const base = await resolveBase();
  chapters = await Promise.all(CHAPTERS.map(async (file) => {
    const text = await (await fetch(base + 'book/' + file)).text();
    const match = text.match(/^#\s+(.+)$/m);
    return { file, text, title: match ? match[1].trim() : file };
  }));

  $('#toc-list').innerHTML = chapters
    .map((c, i) => `<li><button type="button" data-index="${i}">${esc(c.title)}</button></li>`)
    .join('');

  $('#toc-list').querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => openChapter(Number(button.dataset.index)));
  });
}

function openChapter(index) {
  const chapter = chapters[index];
  if (!chapter) return;
  showView('reading');
  $('#content').innerHTML = parseMarkdown(chapter.text);
  $('#content').querySelectorAll('pre').forEach((el) => el.setAttribute('dir', 'ltr'));
  $('#toc-list').querySelectorAll('button').forEach((button) => {
    button.setAttribute('aria-current', String(Number(button.dataset.index) === index));
  });
  window.scrollTo({ top: 0, behavior: 'instant' });
}

/* ---------- quiz ---------- */

let session = null;

function tfResponse(question, wantsTrue) {
  // The banks are inconsistent: some store "True"/"False", others "درست"/"نادرست".
  // Answer in whichever vocabulary this question actually uses, or grading fails.
  const stored = String((question.answers || [''])[0] || '');
  const isPersian = /[؀-ۿ]/.test(stored);
  if (isPersian) return wantsTrue ? 'درست' : 'نادرست';
  return wantsTrue ? 'true' : 'false';
}

async function startQuiz(reviewOnly = false) {
  showView('quiz');
  const bridge = await getBridge();
  const base = await resolveBase();
  const bank = await (await fetch(`${base}book/quiz/${BANK}.json`)).json();
  const result = JSON.parse(
    bridge.select(JSON.stringify(bank.questions || []), JSON.stringify(loadState()), SESSION_SIZE, reviewOnly)
  );
  saveState(result.state);
  session = { questions: result.questions, index: 0 };
  renderQuestion();
  refreshProgress();
}

function buildQuestion(question) {
  const meta = `پرسش ${session.index + 1}/${session.questions.length} | ${question.id} | سطح ${question.difficulty ?? 1} | ${question.type}`;
  const parts = [
    `<div class="q-meta">${esc(meta)}</div>`,
    `<div class="q-prompt">${parseMarkdown(question.prompt)}</div>`,
  ];
  if (question.hint) parts.push(`<p class="muted">راهنما: ${inlineMarkdown(question.hint)}</p>`);

  if (question.type === 'mcq' || question.type === 'multi') {
    parts.push('<div class="options">');
    for (const [key, label] of Object.entries(question.options || {})) {
      parts.push(
        `<button class="option" type="button" data-key="${esc(key)}" aria-pressed="false">` +
        `<span class="key">${esc(key)}.</span><span>${inlineMarkdown(label)}</span></button>`
      );
    }
    parts.push('</div>');
  } else if (question.type === 'tf') {
    parts.push(
      '<div class="options">' +
      '<button class="option" type="button" data-tf="1" aria-pressed="false"><span class="key">✓</span><span>درست</span></button>' +
      '<button class="option" type="button" data-tf="0" aria-pressed="false"><span class="key">✗</span><span>نادرست</span></button>' +
      '</div>'
    );
  } else {
    parts.push('<div class="options"><input type="text" id="blank" placeholder="پاسخ…" autocomplete="off"></div>');
  }

  parts.push('<div class="actions"><button class="btn" id="submit" type="button">ثبت پاسخ</button></div>');
  return parts.join('\n');
}

function renderQuestion() {
  const host = $('#quiz-body');
  const question = session.questions[session.index];
  if (!question) {
    host.innerHTML = '<p class="muted">پرسشی برای نمایش نیست.</p>';
    return;
  }
  host.innerHTML = buildQuestion(question);
  wireQuestion(host, question);
}

function wireQuestion(host, question) {
  const optionButtons = host.querySelectorAll('.option[data-key]');
  const tfButtons = host.querySelectorAll('.option[data-tf]');

  optionButtons.forEach((button) => button.addEventListener('click', () => {
    if (question.type === 'multi') {
      const pressed = button.getAttribute('aria-pressed') === 'true';
      button.setAttribute('aria-pressed', String(!pressed));
    } else {
      optionButtons.forEach((other) => other.setAttribute('aria-pressed', 'false'));
      button.setAttribute('aria-pressed', 'true');
    }
  }));

  tfButtons.forEach((button) => button.addEventListener('click', () => {
    tfButtons.forEach((other) => other.setAttribute('aria-pressed', 'false'));
    button.setAttribute('aria-pressed', 'true');
  }));

  host.querySelector('#submit').addEventListener('click', () => submitAnswer(question));
}

async function submitAnswer(question) {
  const host = $('#quiz-body');
  let response;

  if (question.type === 'mcq' || question.type === 'multi') {
    const chosen = [...host.querySelectorAll('.option[data-key][aria-pressed="true"]')].map((b) => b.dataset.key);
    if (!chosen.length) return setStatus('یک گزینه انتخاب کنید.');
    response = question.type === 'multi' ? chosen : chosen[0];
  } else if (question.type === 'tf') {
    const button = host.querySelector('.option[data-tf][aria-pressed="true"]');
    if (!button) return setStatus('درست یا نادرست را انتخاب کنید.');
    response = tfResponse(question, button.dataset.tf === '1');
  } else {
    const value = host.querySelector('#blank').value.trim();
    if (!value) return setStatus('پاسخ را بنویسید.');
    response = value;
  }

  setStatus('');
  const bridge = await getBridge();
  const result = JSON.parse(
    bridge.grade(JSON.stringify(question), JSON.stringify(response), JSON.stringify(loadState()))
  );
  saveState(result.state);
  renderVerdict(question, result.correct);
  refreshProgress();
}

function renderVerdict(question, correct) {
  const host = $('#quiz-body');
  const answerText = (question.answers || []).join('، ');
  host.innerHTML =
    `<div class="verdict ${correct ? 'ok' : 'bad'}">` +
    `<strong>${correct ? '✓ درست است' : `✗ نادرست است — پاسخ درست: ${esc(answerText)}`}</strong>` +
    `${parseMarkdown(question.explanation || '')}</div>` +
    '<div class="actions"><button class="btn" id="next" type="button">پرسش بعدی</button></div>';

  host.querySelector('#next').addEventListener('click', () => {
    session.index += 1;
    if (session.index >= session.questions.length) {
      host.innerHTML = '<p class="muted">پایان جلسه. آفرین!</p>';
      return;
    }
    renderQuestion();
  });
}

async function refreshProgress() {
  const host = $('#progress');
  try {
    const bridge = await getBridge();
    const summary = JSON.parse(bridge.summary(JSON.stringify(loadState())));
    const rows = (summary.mastery || []).slice(0, 8).map(([concept, score, hit, seen]) => {
      const filled = Math.round(score * 12);
      const bar = '█'.repeat(filled) + '░'.repeat(Math.max(0, 12 - filled));
      return `<div class="muted"><span class="bar">${bar}</span> ${esc(concept)} — ${Math.round(score * 100)}٪ (${hit}/${seen})</div>`;
    }).join('');
    host.innerHTML =
      `<div class="q-meta">سطح تخمینی: ${Number(summary.level).toFixed(1)}/5</div>` +
      (rows || '<div class="muted">هنوز پاسخی ثبت نشده است.</div>');
  } catch {
    host.innerHTML = '';
  }
}

/* ---------- progress export / import ----------
   Same JSON shape as the CLI's progress.json, so progress can be moved between
   the terminal reader and the browser in either direction. */

function exportProgress() {
  const blob = new Blob([JSON.stringify(loadState(), null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'javabook-progress.json';
  link.click();
  URL.revokeObjectURL(url);
}

function importProgress(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      saveState(JSON.parse(String(reader.result)));
      refreshProgress();
      setStatus('پیشرفت بارگذاری شد.');
    } catch {
      setStatus('پروندهٔ پیشرفت نامعتبر است.');
    }
  };
  reader.readAsText(file);
}

/* ---------- view switching ---------- */

function showView(name) {
  const reading = name === 'reading';
  $('#reading').hidden = !reading;
  $('#quiz').classList.toggle('active', !reading);
  $('#btn-reading').setAttribute('aria-pressed', String(reading));
  $('#btn-quiz').setAttribute('aria-pressed', String(!reading));
  setStatus('');
}

/* ---------- boot ---------- */

async function boot() {
  $('#btn-reading').addEventListener('click', () => showView('reading'));
  $('#btn-quiz').addEventListener('click', () => {
    if (session) showView('quiz');
    else startQuiz(false).catch((error) => setStatus(`خطا: ${error.message}`));
  });
  $('#btn-review').addEventListener('click', () => {
    startQuiz(true).catch((error) => setStatus(`خطا: ${error.message}`));
  });
  $('#btn-export').addEventListener('click', exportProgress);
  $('#btn-import').addEventListener('click', () => $('#import-file').click());
  $('#import-file').addEventListener('change', (event) => {
    const file = event.target.files && event.target.files[0];
    if (file) importProgress(file);
    event.target.value = '';
  });

  try {
    await loadChapters();
    if (chapters.length) openChapter(0);
  } catch (error) {
    setStatus(`خطا: ${error.message}`);
  }
}

document.addEventListener('DOMContentLoaded', boot);
