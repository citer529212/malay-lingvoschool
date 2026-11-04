// Indonesian source materials will be added independently of the Malay edition.
routes[1][1]='Уроки';
stageName=function(){return 'Вводный курс'};
parts[parts.findIndex(p=>p[0]==='source')][1]='О материалах';
const materialNote='Вы пришлёте индонезийский учебник, словарь и аудио позже. Сейчас доступны три авторских вводных примера. Материалы малайского учебника относятся только к малайской версии.';
const originalHome=homeView;
homeView=function(){return originalHome()
 .replace(/Курс по учебнику<br><strong>.*?<\/strong>/,'Самостоятельные вводные примеры<br><strong>Ваш учебник подключим после получения</strong>')
 .replace('147 аудиозаписей к урокам','Синтез речи · голос id-ID')
 .replace('<strong>40</strong>','<strong>'+course.lessons.length+'</strong>')
 .replace('<strong>147</strong>','<strong>TTS</strong>')
 .replace('записей<br>для аудирования','озвучивание<br>текстов браузером')
 .replace('<strong>50 319</strong>','<strong>'+course.dictionaryEntries+'</strong>')
 .replace('9 фонетических и 31 основной урок: тексты, диалоги, грамматика и упражнения.','Вводные примеры: тексты, диалоги, грамматика и упражнения. Ваш учебник подключим позже.')
 .replace('Оригинальные записи к учебнику. Слушайте в своём темпе, повторяйте, записывайте услышанное.','Озвучивание вводных текстов индонезийским голосом браузера. Аудиозаписи учебника подключим после получения.')
 .replace('BACA · DENGAR · CAKAP','BACA · DENGAR · BICARA')
 .replace('Откройте учебник','Откройте уроки')
 .replace('Сегодня — ещё один шаг.','Сегодня — ещё один шаг.')
 .replace('<section class="welcome-numbers"','<aside class="hint material-status">'+esc(materialNote)+'</aside><section class="welcome-numbers"')};
courseView=function(){const lessons=course.lessons.filter(l=>!courseSearch||norm(lessonTitle(l)+' '+l.subtitle).includes(norm(courseSearch)));return heading('Индонезийский · ваш маршрут',materialNote)+`<section class="panel"><h2>Вводные примеры</h2><p>Три небольших урока помогут попробовать чтение, диалоги, упражнения, перевод и сохранение слов. Они не заменяют ваш будущий учебник.</p><label for="courseSearch">Найти урок</label><input class="input" id="courseSearch" type="search" value="${esc(courseSearch)}" placeholder="Найти тему…"></section><div id="lessonGrid" class="lesson-grid">${lessonCards(lessons)}</div>`};
lessonCards=function(ls){return ls.length?ls.map(l=>`<button class="lesson-card" data-lesson="${l.id}"><span class="eyebrow">Вводный пример</span><span class="lesson-number">${l.number}</span><h3>${esc(l.title)}</h3><p>${esc(l.subtitle)}</p><footer><span>Текст · диалог · упражнения</span><span>${user.lessonDone[l.id]?'✓ Пройдено':'Открыть →'}</span></footer></button>`).join(''):'<div class="panel empty">По вашему запросу уроков не найдено.</div>'};
const originalBlockCard=blockCard;
const originalLessonView=lessonView;
lessonView=function(){return originalLessonView().replace('Аудио · 0','Озвучивание')};
blockCard=function(b,l,translation=false){let out=originalBlockCard(b,l,translation)
 .replace(/<span class="page-ref">.*?<\/span>/,'<span class="page-ref">Авторский вводный пример</span>')
 .replace(/<details class="source-scan"><summary>Сверить со страницей учебника<\/summary>.*?<\/details>/s,'');
 if(b.translation||b.answer){const detail=`<details class="source-scan"><summary>${b.answer?'Посмотреть пример ответа':'Посмотреть перевод примера'}</summary><p class="read-text">${esc(b.answer||b.translation)}</p></details>`;out=out.replace(/<\/article>$/,detail+'</article>')}return out};
scanSection=function(){return heading('Материалы урока')+`<section class="panel"><p>${esc(materialNote)}</p><p>Эти вводные примеры созданы для знакомства с интерфейсом. У них нет страниц из печатного учебника.</p><a class="btn" href="https://bipa.kemendikdasmen.go.id/belajar.php" target="_blank" rel="noopener">Официальные материалы BIPA ↗</a><a class="btn" href="https://ejaan.kemendikdasmen.go.id/eyd/" target="_blank" rel="noopener">Правила орфографии EYD V ↗</a></section>`};
sourceView=scanSection;
allPagesView=scanSection;
frameView=function(news=false){const title=news?'Новости и перевод':'Военный перевод',section=news?'news':'home';return heading(title,news?'Индонезийские новости ANTARA и мастерская ID ↔ RU.':'Учебные сценарии перевода. Материалы вашего курса подключим после получения.')+`<div class="frame-toolbar"><p class="muted">Черновики и результаты сохраняются отдельно от малайской версии.</p><a class="btn small" href="indonesian-military.html?section=${section}" target="_blank" rel="noopener">Развернуть ↗</a></div><div class="frame-wrap"><iframe class="trainer-frame" src="indonesian-military.html?section=${section}" title="${title}" loading="lazy"></iframe></div>`};
const originalDictionaryView=dictionaryView;
dictionaryView=function(){return originalDictionaryView()
 .replace(/<a class="btn" href="assets\/dictionary-full.html".*?<\/a>/,'<p class="mini muted">Учебный мини-словарь вводных примеров: '+course.dictionaryEntries+' статей в двух направлениях. Полный словарь подключим после получения.</p>')};
function speechCards(l){return l.blocks.filter(b=>['read','dialog'].includes(b.kind)).map(b=>`<article class="panel"><h2>${esc(b.title)} · ${esc(l.title)}</h2><p class="mini muted">Синтез речи браузера · индонезийский голос. Это не запись диктора.</p><div class="controls"><button class="btn primary" data-speak="${b.id}">▶ Слушать</button><button class="btn" data-stop-speech>■ Остановить</button><label>Темп <select class="input" data-speech-rate="${b.id}"><option value="0.75">0,75×</option><option value="1" selected>1×</option><option value="1.25">1,25×</option></select></label></div><p data-speech-status="${b.id}" role="status"></p><details><summary>Показать текст для сверки</summary><div class="read-text">${tokens(b.text)}</div></details></article>`).join('')}
audioSection=function(tracks,l){return `<div class="hint">Аудиозаписи вашего учебника появятся после получения. Сейчас можно слушать вводные примеры, если на устройстве установлен индонезийский голос.</div>`+speechCards(l)+`<section class="panel"><label for="listeningNote">Запишите услышанное</label><textarea id="listeningNote" class="answer" data-draft="listen:${l.id}">${esc(user.drafts['listen:'+l.id]||'')}</textarea></section>`};
listeningView=function(){return heading('Аудирование','Озвучивание вводных примеров. Оригинальные записи подключим после получения.')+course.lessons.map(l=>`<section><h2>Урок ${l.number} · ${esc(l.title)}</h2>${speechCards(l)}</section>`).join('')};
const originalBind=bind;
bind=function(){originalBind();$$('[data-speak]').forEach(button=>button.onclick=()=>{
 const id=button.dataset.speak,b=course.lessons.flatMap(l=>l.blocks).find(b=>b.id===id),status=$$('[data-speech-status]').find(el=>el.dataset.speechStatus===id);
 if(!('speechSynthesis' in window)){status.textContent='Этот браузер не поддерживает озвучивание. Текст доступен для чтения.';return}
 const voice=speechSynthesis.getVoices().find(v=>/^id(?:[-_]|$)/i.test(v.lang));
 if(!voice){status.textContent='Индонезийский голос не найден. Добавьте голос Bahasa Indonesia в настройках речи устройства. После установки обновите страницу.';return}
 speechSynthesis.cancel();const utterance=new SpeechSynthesisUtterance(b.text.replace(/^(Anna|Budi):\s*/gm,''));utterance.voice=voice;utterance.lang='id-ID';utterance.rate=+$$('[data-speech-rate]').find(el=>el.dataset.speechRate===id).value;
 utterance.onstart=()=>status.textContent='Воспроизведение…';utterance.onend=()=>{status.textContent='Прослушано';user.listened['tts:'+id]=true;save()};utterance.onerror=()=>status.textContent='Озвучивание остановлено или недоступно.';speechSynthesis.speak(utterance);
 });$$('[data-stop-speech]').forEach(button=>button.onclick=()=>{window.speechSynthesis?.cancel();$$('[data-speech-status]').forEach(el=>el.textContent='Остановлено')})};
const originalSetRoute=setRoute;
setRoute=function(next){window.speechSynthesis?.cancel();originalSetRoute(next)};
window.addEventListener('pagehide',()=>window.speechSynthesis?.cancel());
// Request voices once; some browsers populate this list asynchronously.
window.speechSynthesis?.getVoices();
