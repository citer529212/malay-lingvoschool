'use strict';

window.MalayLevels = (() => {
  const routes = [['a1-a2', 'A1–A2'], ['b1-b2', 'B1–B2'], ['c1-c2', 'C1–C2']];
  const stageInfo = [
    { id: 'a1-a2', level: 'A1–A2', title: 'Малайский на каждый день', description: 'Знакомство, кафе, покупки и поездки. Игровые задания с подсказками и коротким аудированием.', action: 'Начать играть', tone: 'a' },
    { id: 'b1-b2', level: 'B1–B2', title: 'Грамматика и перевод', description: 'Разбирайте структуру фразы, понимайте новости и переводите тексты в обе стороны.', action: 'Открыть ступень', tone: 'b' },
    { id: 'c1-c2', level: 'C1–C2', title: 'Практика переводчика', description: 'Письменный, последовательный, двусторонний, синхронный перевод и перевод с листа.', action: 'Открыть практику', tone: 'c' }
  ];
  const B2_PASS = 12;
  const STORAGE = 'malay-textbook-v1';
  let attempt = null;
  let selectedB = 'b-mail';
  let selectedC = 'c-sync';
  let levelFilter = 'all';
  let modeFilter = 'all';
  let cleanup = () => {};
  const data = () => window.MalayLevelData;

  function progress(user) {
    if (!user.levels || typeof user.levels !== 'object' || Array.isArray(user.levels)) user.levels = {};
    const state = user.levels;
    for (const key of ['results', 'drafts', 'done']) {
      if (!state[key] || typeof state[key] !== 'object' || Array.isArray(state[key])) state[key] = {};
    }
    return state;
  }

  function hasB2(user) {
    try {
      const state = user ?? JSON.parse(localStorage.getItem(STORAGE) || '{}');
      const result = state.levels?.results?.B2;
      return result?.total === 15 && Number.isInteger(result.best) && result.best >= B2_PASS && result.best <= 15;
    } catch {
      return false;
    }
  }

  function visit(route, user, save) {
    if (!routes.some(([id]) => id === route)) return;
    const state = progress(user);
    if (state.stage !== route) {
      state.stage = route;
      save();
    }
  }

  function canTranslate(user) {
    return user.levels?.stage === 'b1-b2'
      || (user.levels?.stage === 'c1-c2' && hasB2(user));
  }

  function shuffle(items) {
    const result = [...items];
    for (let i = result.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
  }

  function startQuiz(level) {
    const game = level === 'A1' || level === 'A2';
    const rows = game ? data().games[level] : data()[level.toLowerCase()];
    const questions = rows.map(row => {
      const [topic, ...parts] = game ? row : ['', ...row];
      const [prompt, correct, wrong1, wrong2, explain, audio] = parts;
      return { topic, prompt, correct, choices: shuffle([correct, wrong1, wrong2]), explain, audio };
    });
    // Keep B2 comprehension and listening questions together after grammar.
    attempt = { level, game, questions: level === 'B2' ? questions : shuffle(questions), answers: [], checked: false, finished: false, score: 0 };
  }

  function routeButton(label, target, primary = false) {
    return `<button type="button" class="btn ${primary ? 'primary' : ''}" data-route-link="${target}">${label}</button>`;
  }

  function levelNav(route, user) {
    return `<nav class="level-nav" aria-label="Ступени курса">${stageInfo.map(stage => `
      <button type="button" class="level-nav-btn level-${stage.tone}" data-route-link="${stage.id}" ${stage.id === route ? 'aria-current="page"' : ''}>
        <strong>${stage.level}</strong><span>${stage.id === 'c1-c2' && !hasB2(user) ? 'После теста B2' : stage.title}</span>
      </button>`).join('')}</nav>`;
  }

  function home(user) {
    return `<section class="level-home">
      <span class="eyebrow">BAHASA MELAYU</span>
      <h1>Малайский язык от A1 до C2</h1>
      <p>Выберите ступень по своей цели. Начните с разговорных ситуаций, разберите грамматику или перейдите к практике перевода.</p>
    </section><div class="level-grid">${stageInfo.map(stage => {
      const locked = stage.tone === 'c' && !hasB2(user);
      return `<article class="level-card level-${stage.tone}">
        <span class="level-range">${stage.level}</span><h2>${stage.title}</h2><p>${stage.description}</p>
        ${routeButton(locked ? 'Условия доступа' : stage.action, stage.id, stage.tone === 'a')}
        ${locked ? '<small>Откроется после сдачи теста B2</small>' : ''}
      </article>`;
    }).join('')}</div>
    <div class="controls level-home-links">${routeButton('Учебник', 'course')}${routeButton('Аудирование', 'listening')}${routeButton('Мой прогресс', 'progress')}</div>`;
  }

  function locked(user, esc) {
    const result = progress(user).results.B2;
    const current = result ? ` Лучший результат: ${Number(result.best) || 0} из 15.` : '';
    return `<section class="panel level-lock">
      <h2>Сначала сдайте B2</h2><p>Ответьте правильно минимум на 12 из 15 вопросов внутреннего теста.${esc(current)}</p>
      <p>После сдачи откроются все форматы и темы продвинутой практики.</p>
      <button type="button" class="btn primary" data-route-link="b1-b2" data-b2-jump>Перейти к тесту B2</button>
    </section>`;
  }

  function audioPlayer(id, label, rate = false) {
    return `<div class="level-audio">
      <audio controls preload="metadata" src="assets/level-audio/${id}.mp3" aria-label="${label}"></audio>
      ${rate ? '<label>Темп <select class="input" data-level-speed><option value="0.8">0,8×</option><option value="1" selected>1×</option><option value="1.2">1,2×</option></select></label>' : ''}
    </div>`;
  }

  function quizPanel(esc, tokens) {
    const q = attempt;
    if (q.finished) {
      const passed = q.level !== 'B2' || q.score >= B2_PASS;
      return `<section class="panel level-quiz" tabindex="-1" data-quiz-focus>
        <h2>${q.level} · ${q.score} из ${q.questions.length}</h2>
        <p>${q.level === 'B2' ? (passed ? 'Тест сдан. Практика C1–C2 открыта.' : 'Для доступа к C1–C2 нужно минимум 12 правильных ответов.') : 'Раунд завершён. Разберите ответы и попробуйте ещё раз.'}</p>
        <div class="controls">
          <button class="btn" type="button" data-start-level="${q.level}">Пройти ещё раз</button>
          ${q.level === 'B2' && passed ? routeButton('Перейти на C1–C2', 'c1-c2', true) : ''}
        </div>
        <details class="level-review"><summary>Разбор ответов</summary><ol>${q.questions.map((question, i) => `
          <li><strong>${tokens(question.prompt, true)}</strong><p>Ваш ответ: ${tokens(q.answers[i], true)}<br>Верный ответ: ${tokens(question.correct, true)}</p><p>${tokens(question.explain, true)}</p>${question.audio ? `<p lang="ms">${tokens(data().audio[question.audio], true)}</p>` : ''}</li>`).join('')}</ol></details>
      </section>`;
    }
    const index = q.answers.length - (q.checked ? 1 : 0);
    const current = q.questions[index];
    return `<section class="panel level-quiz" tabindex="-1" data-quiz-focus aria-label="Проверка ${q.level}">
      <div class="level-quiz-meta"><span>${q.level} · ${index + 1} из ${q.questions.length}</span>
        ${q.game ? `<span>Очки: ${q.score} / ${q.questions.length}</span>` : ''}
      </div>
      <progress value="${q.answers.length}" max="${q.questions.length}" aria-label="Выполнено заданий"></progress>
      ${current.topic ? `<p class="eyebrow">${esc(current.topic)}</p>` : ''}
      ${q.level === 'B2' && index >= 10 && index <= 12 ? `<blockquote lang="ms">${tokens(data().b2Text, true)}</blockquote>` : ''}
      <h2>${tokens(current.prompt, true)}</h2>
      ${current.audio ? audioPlayer(current.audio, 'Озвученный учебный фрагмент') : ''}
      <p class="mini muted">Нажмите на малайское слово, чтобы увидеть перевод.</p>
      <div class="level-choices">${current.choices.map((choice, i) => {
        const answerClass = q.checked ? (choice === current.correct ? ' level-correct' : choice === q.answers[index] ? ' level-wrong' : '') : '';
        const choose = `data-choose-level="${i}" ${q.checked ? 'disabled' : ''}`;
        if (!/^[\p{Script=Latin}][\p{Script=Latin}\s\p{P}\p{N}]*$/u.test(choice)) {
          return `<button type="button" class="btn${answerClass}" ${choose}>${esc(choice)}</button>`;
        }
        return `<div class="level-choice-row${answerClass}">
          <span lang="ms">${tokens(choice, true)}</span>
          <button type="button" class="btn small" aria-label="Выбрать: ${esc(choice)}" ${choose}>Выбрать</button>
        </div>`;
      }).join('')}</div>
      ${q.checked ? `${current.audio ? `<p lang="ms">${tokens(data().audio[current.audio], true)}</p>` : ''}<p role="status">${q.answers[index] === current.correct ? 'Верно. ' : 'Правильный ответ выделен. '}${tokens(current.explain, true)}</p>
        <button class="btn primary" type="button" data-next-level>${q.answers.length === q.questions.length ? 'Результат' : 'Следующее задание'}</button>` : ''}
    </section>`;
  }

  function beginner(user, esc, tokens) {
    const state = progress(user);
    return `<div class="level-grid level-grid-two">${['A1', 'A2'].map((level, i) => `
      <article class="panel level-launch">
        <h2>${level} · ${i ? 'Поездки и повседневные дела' : 'Первые разговоры'}</h2>
        <p>${i ? 'Понимать объявления, сравнивать цены, договариваться о встрече.' : 'Представиться, заказать еду, спросить цену и найти дорогу.'}</p>
        ${state.results[level] ? `<p class="mini muted">Лучший результат: ${Number(state.results[level].best) || 0} из 6</p>` : ''}
        <button class="btn primary" type="button" data-start-level="${level}">Играть · ${level}</button>
      </article>`).join('')}</div>
      ${attempt?.game ? quizPanel(esc, tokens) : ''}
      <section class="panel"><h2>Разговоры из учебника</h2><div class="controls">
        <button class="btn" type="button" data-lesson="intro-7">Знакомство</button>
        <button class="btn" type="button" data-lesson="basic-5">На рынке</button>
        <button class="btn" type="button" data-lesson="basic-6">На вокзале</button>
        ${routeButton('Аудирование', 'listening')}
      </div></section>`;
  }

  function intermediate(user, esc, tokens) {
    const state = progress(user);
    const tasks = data().translation.filter(task => task.level.startsWith('B'));
    const task = tasks.find(item => item.id === selectedB) || tasks[0];
    return `<section class="level-section">
      <h2>Грамматика на примерах</h2><div class="level-grid level-grid-two">
        ${data().theory.map(([level, title, text, example, lesson]) => `
          <article class="panel level-theory">
            <span class="level-range">${level}</span><h3>${esc(title)}</h3><p>${tokens(text, true)}</p>
            <p class="level-example">${tokens(example, true)}</p>
            <button class="btn small" type="button" data-lesson="${lesson}" data-open-part="theory">Раздел учебника</button>
          </article>`).join('')}
      </div>
    </section>
    <section class="level-section"><h2>Практика письменного перевода</h2>
      <label class="level-field">Задание <select class="input" data-translation-task="b">${taskOptions(tasks, task, esc)}</select></label>
      ${translationTask(task, state, esc, tokens)}
    </section>
    <section class="level-section" id="level-assessment">
      <h2>Проверка B1 и B2</h2>
      <p>B1 проверяет основные конструкции. Для доступа к C1–C2 наберите 12 из 15 в тесте B2. В нём есть грамматика, чтение и аудирование.</p>
      <div class="controls">
        <button class="btn" type="button" data-start-level="B1">Проверка B1</button>
        <button class="btn primary" type="button" data-start-level="B2">Начать тест B2</button>
        ${hasB2(user) ? routeButton('C1–C2 открыты', 'c1-c2') : ''}
      </div>
      <p class="mini muted">${state.results.B2 ? `Лучший результат B2: ${Number(state.results.B2.best) || 0} из 15. ` : ''}Это внутренний тест школы.</p>
      ${attempt && !attempt.game ? quizPanel(esc, tokens) : ''}
    </section>`;
  }

  function taskOptions(tasks, selected, esc) {
    return tasks.map(task => `<option value="${task.id}" ${task === selected ? 'selected' : ''}>${esc(task.level + ' · ' + task.topic + (task.mode === 'Синхронный' ? (task.lang === 'ru' ? ' · RU → MS' : ' · MS → RU') : ''))}</option>`).join('');
  }

  function advanced(user, esc, tokens) {
    if (!hasB2(user)) return locked(user, esc);
    const state = progress(user);
    const all = data().translation.filter(task => task.level.startsWith('C'));
    const modes = [...new Set(all.map(task => task.mode))];
    const tasks = all.filter(task => (levelFilter === 'all' || task.level === levelFilter) && (modeFilter === 'all' || task.mode === modeFilter));
    const selected = tasks.find(task => task.id === selectedC) || tasks[0];
    return `<section class="level-section">
      <h2>Тренажёр перевода</h2>
      <p>Выберите уровень, формат и тему. В устных заданиях можно записать себя и сверить перевод с образцом.</p>
      <div class="level-filters">
        <label class="level-field">Уровень <select class="input" data-c-filter="level">
          ${[['all','C1 и C2'], ['C1','C1'], ['C2','C2']].map(([key,label]) => `<option value="${key}" ${key === levelFilter ? 'selected' : ''}>${label}</option>`).join('')}
        </select></label>
        <label class="level-field">Вид перевода <select class="input" data-c-filter="mode">
          ${['all', ...modes].map(mode => `<option value="${esc(mode)}" ${mode === modeFilter ? 'selected' : ''}>${mode === 'all' ? 'Все виды' : esc(mode)}</option>`).join('')}
        </select></label>
        <label class="level-field">Тема и задание <select class="input" data-translation-task="c" ${selected ? '' : 'disabled'}>
          ${selected ? taskOptions(tasks, selected, esc) : '<option>Нет заданий</option>'}
        </select></label>
      </div>
      ${selected ? translationTask(selected, state, esc, tokens) : '<p class="panel">Для этого сочетания заданий пока нет. Выберите «Все виды» или «C1 и C2».</p>'}
    </section>
    <section class="panel"><h2>Подготовка к проверке C1 и C2</h2>
      <p>Отработайте все пять форматов на каждой ступени. При самопроверке отмечайте полноту смысла, точность терминов и цифр, регистр и темп речи.</p>
      <ul>${['C1', 'C2'].map(level => {
        const exercises = all.filter(task => task.level === level);
        return `<li>${level} · отработано ${exercises.filter(task => state.done[task.id]).length} из ${exercises.length}</li>`;
      }).join('')}</ul>
    </section>
    <section class="panel"><h2>Военный перевод и ГИА</h2>
      <p>Тематический словарь, диалоги, письменные задания и экзаменационный таймер.</p>
      ${routeButton('Открыть тренажёр ГИА', 'military')}
    </section>`;
  }

  function translationTask(task, state, esc, tokens) {
    const audio = task.mode === 'Последовательный' || task.mode === 'Синхронный';
    const oral = task.mode !== 'Письменный';
    const direction = task.mode === 'Двусторонний' ? 'MS ↔ RU' : task.lang === 'ms' ? 'MS → RU' : 'RU → MS';
    const instruction = {
      'Письменный': 'Переведите текст письменно. Затем откройте образец и проверьте свой вариант.',
      'С листа': 'Прочитайте текст за 30 секунд. Затем переведите его устно, сверяясь с оригиналом.',
      'Последовательный': 'Прослушайте речь. Запишите ключевые слова и переводите после окончания.',
      'Двусторонний': 'Переводите реплики по очереди на язык собеседника.',
      'Синхронный': 'Наденьте наушники, включите речь и начните переводить через несколько секунд. Не ставьте речь на паузу во время попытки.'
    }[task.mode];
    const source = `<div class="read-text" ${task.mode === 'Двусторонний' ? '' : `lang="${task.lang}"`}>${tokens(task.text, true)}</div>`;
    return `<article class="panel level-translation" data-task-id="${task.id}">
      <p class="eyebrow">${task.level} · ${direction}</p>
      <h3>${esc(task.mode)} · ${esc(task.topic)}</h3><p>${instruction}</p>
      ${audio ? `<p class="mini muted">Учебная речь с синтезированной озвучкой.</p>${audioPlayer(task.id, 'Исходная речь для перевода', true)}
        <details class="source-scan"><summary>Открыть расшифровку</summary>${source}</details>` : source}
      ${task.mode === 'С листа' ? '<div class="controls"><button type="button" class="btn small" data-prep-timer>30 секунд на подготовку</button><span role="status" data-prep-status></span></div>' : ''}
      ${oral ? `<div class="level-record controls">
        <button type="button" class="btn" data-record-start>Записать перевод</button>
        <button type="button" class="btn" data-record-stop disabled>Остановить запись</button>
        <span class="mini muted">Запись доступна до выхода из задания. Её можно скачать.</span>
      </div><p class="mini muted" data-record-status role="status"></p><div data-record-result></div>` : ''}
      <label class="level-field">${oral ? 'Заметки или текст перевода' : 'Ваш перевод'}
        <textarea class="answer" data-level-draft="${task.id}" rows="5">${esc(state.drafts[task.id] || '')}</textarea>
      </label>
      <details class="source-scan"><summary>Образец и критерии самопроверки</summary>
        <p class="read-text">${tokens(task.reference, true)}</p><p>${tokens(task.check, true)}</p>
      </details>
      <label class="check"><input type="checkbox" data-level-done="${task.id}" ${state.done[task.id] ? 'checked' : ''}> Задание отработано</label>
    </article>`;
  }

  function beforeRender(route) {
    cleanup();
    cleanup = () => {};
    const stage = stageInfo.find(item => item.id === route);
    document.documentElement.dataset.malayStage = stage?.tone || (route === 'military' ? 'c' : '');
  }

  function view(route, user, esc, tokens) {
    if (route === 'home') return home(user);
    if (route === 'military' && !hasB2(user)) {
      return levelNav('c1-c2', user) + locked(user, esc);
    }
    const stage = stageInfo.find(item => item.id === route);
    if (!stage) return null;
    const content = stage.tone === 'a' ? beginner(user, esc, tokens)
      : stage.tone === 'b' ? intermediate(user, esc, tokens)
        : advanced(user, esc, tokens);
    return `${levelNav(route, user)}<header class="level-stage-title level-${stage.tone}">
      <span class="level-range">${stage.level}</span><h1>${stage.title}</h1><p>${stage.description}</p>
    </header>${content}`;
  }

  function bind(app, user, save, render, toast) {
    const state = progress(user);
    const jump = app.querySelector('[data-b2-jump]');
    if (jump) jump.addEventListener('click', () => {
      const target = app.querySelector('[data-start-level="B2"]');
      target?.focus();
      target?.scrollIntoView({ block: 'center' });
    });
    const redrawQuiz = () => {
      render();
      const panel = app.querySelector('[data-quiz-focus]');
      panel?.focus({ preventScroll: true });
      panel?.scrollIntoView({ block: 'start' });
    };
    function finish() {
      attempt.finished = true;
      const previous = state.results[attempt.level]?.best || 0;
      state.results[attempt.level] = {
        best: Math.max(Number(previous) || 0, attempt.score),
        last: attempt.score,
        total: attempt.questions.length
      };
      save();
    }
    app.querySelectorAll('[data-start-level]').forEach(button => {
      button.onclick = () => { startQuiz(button.dataset.startLevel); redrawQuiz(); };
    });
    app.querySelectorAll('[data-choose-level]').forEach(button => {
      button.onclick = () => {
        if (!attempt || attempt.finished || attempt.checked) return;
        const question = attempt.questions[attempt.answers.length];
        const answer = question.choices[Number(button.dataset.chooseLevel)];
        attempt.answers.push(answer);
        if (answer === question.correct) attempt.score++;
        if (attempt.game) attempt.checked = true;
        else if (attempt.answers.length === attempt.questions.length) finish();
        redrawQuiz();
      };
    });
    const next = app.querySelector('[data-next-level]');
    if (next) next.onclick = () => {
      if (attempt.answers.length === attempt.questions.length) finish();
      else attempt.checked = false;
      redrawQuiz();
    };
    app.querySelectorAll('[data-translation-task]').forEach(select => {
      select.onchange = () => {
        if (select.dataset.translationTask === 'b') selectedB = select.value;
        else selectedC = select.value;
        render();
        app.querySelector(`[data-translation-task="${select.dataset.translationTask}"]`)?.focus();
      };
    });
    app.querySelectorAll('[data-c-filter]').forEach(select => {
      select.onchange = () => {
        if (select.dataset.cFilter === 'level') levelFilter = select.value;
        else modeFilter = select.value;
        render();
        app.querySelector(`[data-c-filter="${select.dataset.cFilter}"]`)?.focus();
      };
    });
    const task = app.querySelector('[data-task-id]');
    if (!task) return;
    const id = task.dataset.taskId;
    task.querySelector('[data-level-draft]').oninput = event => { state.drafts[id] = event.target.value; save(); };
    task.querySelector('[data-level-done]').onchange = event => { state.done[id] = event.target.checked; save(); };
    const speed = task.querySelector('[data-level-speed]');
    if (speed) speed.onchange = () => { task.querySelector('audio').playbackRate = Number(speed.value); };
    const disposers = [];
    const timer = task.querySelector('[data-prep-timer]');
    if (timer) {
      let interval;
      timer.onclick = () => {
        clearInterval(interval);
        const label = task.querySelector('[data-prep-status]');
        const end = Date.now() + 30000;
        label.textContent = 'Подготовка: 30 с';
        interval = setInterval(() => {
          const remaining = Math.max(0, Math.ceil((end - Date.now()) / 1000));
          label.textContent = remaining ? `Подготовка: ${remaining} с` : 'Начните переводить.';
          if (!remaining) clearInterval(interval);
        }, 250);
      };
      disposers.push(() => clearInterval(interval));
    }
    const record = task.querySelector('[data-record-start]');
    if (record) disposers.push(bindRecorder(task, toast));
    cleanup = () => disposers.forEach(dispose => dispose());
  }

  function bindRecorder(task, toast) {
    const start = task.querySelector('[data-record-start]');
    const stop = task.querySelector('[data-record-stop]');
    const status = task.querySelector('[data-record-status]');
    const output = task.querySelector('[data-record-result]');
    let stream, recorder, url, left = false;
    const release = () => stream?.getTracks().forEach(track => track.stop());
    start.onclick = async () => {
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        status.textContent = 'Запись недоступна в этом браузере. Можно перевести устно и записать заметки.';
        return;
      }
      start.disabled = true;
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (left) { release(); return; }
        recorder = new MediaRecorder(stream);
        const chunks = [];
        recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
        recorder.onstop = () => {
          release();
          if (left) return;
          start.disabled = false;
          stop.disabled = true;
          if (!chunks.length) { status.textContent = 'Запись пуста. Попробуйте ещё раз.'; return; }
          if (url) URL.revokeObjectURL(url);
          const type = recorder.mimeType || chunks[0].type;
          url = URL.createObjectURL(new Blob(chunks, { type }));
          const player = document.createElement('audio');
          player.controls = true;
          player.src = url;
          player.setAttribute('aria-label', 'Ваша запись');
          const download = document.createElement('a');
          download.className = 'btn small';
          download.href = url;
          download.download = type.includes('mp4') ? 'перевод.m4a' : type.includes('ogg') ? 'перевод.ogg' : 'перевод.webm';
          download.textContent = 'Скачать запись';
          output.replaceChildren(player, download);
          status.textContent = 'Запись готова.';
        };
        recorder.onerror = () => { release(); toast('Не удалось записать перевод.'); };
        recorder.start();
        stop.disabled = false;
        status.textContent = 'Идёт запись.';
      } catch {
        release();
        start.disabled = false;
        status.textContent = 'Микрофон недоступен. Проверьте разрешение браузера.';
      }
    };
    stop.onclick = () => { if (recorder?.state === 'recording') recorder.stop(); };
    return () => {
      left = true;
      if (recorder?.state === 'recording') recorder.stop();
      release();
      if (url) URL.revokeObjectURL(url);
    };
  }

  return { routes, hasB2, visit, canTranslate, beforeRender, view, bind };
})();
