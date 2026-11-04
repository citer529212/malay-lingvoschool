"""Build a separate Indonesian edition while awaiting the user's source materials."""
from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets/indonesian'
DEST.mkdir(parents=True, exist_ok=True)

# These short original examples are explicitly separate from the Malay textbook.
samples = [
    ('Знакомство', 'Местоимения и представление',
     'Nama saya Anna. Saya dari Rusia. Saya belajar bahasa Indonesia. Ini teman saya. Namanya Budi. Dia dari Indonesia.',
     'Меня зовут Анна. Я из России. Я изучаю индонезийский язык. Это мой друг. Его зовут Буди. Он из Индонезии.',
     'Anna: Selamat pagi! Siapa nama Anda?\nBudi: Selamat pagi! Nama saya Budi.\nAnna: Anda dari mana?\nBudi: Saya dari Indonesia. Anda?\nAnna: Saya dari Rusia. Senang berkenalan dengan Anda.',
     'saya — я; Anda — Вы; dia — он, она. В настоящем времени связка перед существительным часто отсутствует: Saya mahasiswa — Я студент. Принадлежность: teman saya — мой друг. Вопрос Siapa nama Anda? — Как Вас зовут?',
     '1. Представьтесь по образцу: Nama saya … Saya dari …\n2. Переведите: «Это мой друг. Он из России».\n3. Ответьте: Siapa nama teman Anna? Dari mana Budi?',
     '1. Индивидуальный ответ.\n2. Ini teman saya. Dia dari Rusia.\n3. Nama teman Anna Budi. Budi dari Indonesia.'),
    ('Учёба и повседневные дела', 'Глаголы, вопросы и отрицание',
     'Saya belajar di universitas. Setiap pagi saya membaca buku. Teman saya menulis di kelas. Kami berbicara bahasa Indonesia. Hari ini saya tidak bekerja. Saya belajar di rumah.',
     'Я учусь в университете. Каждое утро я читаю книгу. Мой друг пишет в классе. Мы говорим по-индонезийски. Сегодня я не работаю. Я занимаюсь дома.',
     'Anna: Apa yang Anda lakukan hari ini?\nBudi: Saya membaca buku. Anda?\nAnna: Saya belajar bahasa Indonesia.\nBudi: Apakah Anda belajar di universitas?\nAnna: Ya, saya belajar di universitas.',
     'Неизменяемость глагола: saya belajar — я учусь, dia belajar — он/она учится. Tidak отрицает действие или признак: saya tidak bekerja. Bukan отрицает именную характеристику: saya bukan guru. Di как предлог места пишется отдельно: di rumah. Kami означает «мы» без собеседника, kita включает собеседника.',
     '1. Поставьте отрицание: Saya bekerja. Dia guru.\n2. Переведите: «Я читаю книгу дома».\n3. Ответьте по тексту: Apa yang Anna lakukan setiap pagi?',
     '1. Saya tidak bekerja. Dia bukan guru.\n2. Saya membaca buku di rumah.\n3. Anna membaca buku setiap pagi.'),
    ('В городе', 'Местоположение и вежливые просьбы',
     'Saya tinggal di Jakarta. Rumah saya dekat stasiun. Di depan stasiun ada toko. Saya pergi ke toko dengan teman saya. Kami membeli air dan roti. Setelah itu kami pulang.',
     'Я живу в Джакарте. Мой дом рядом со станцией. Перед станцией есть магазин. Я иду в магазин с моим другом. Мы покупаем воду и хлеб. После этого мы возвращаемся домой.',
     'Anna: Permisi, di mana stasiun?\nBudi: Stasiun ada di sebelah kiri.\nAnna: Apakah jauh dari sini?\nBudi: Tidak, dekat. Silakan jalan lurus.\nAnna: Terima kasih.\nBudi: Sama-sama.',
     'Di mana? — Где? Ke mana? — Куда? Dari mana? — Откуда? Предлоги di, ke, dari пишутся отдельно от названия места. Di depan — перед, di sebelah kiri — слева. Permisi — извините (чтобы обратиться или пройти); silakan — пожалуйста (приглашение к действию); terima kasih — спасибо.',
     '1. Вставьте di, ke или dari: Saya tinggal … Jakarta. Saya pergi … toko. Saya … Rusia.\n2. Спросите, где станция.\n3. Переведите: «Магазин рядом с домом».',
     '1. di; ke; dari.\n2. Di mana stasiun?\n3. Toko dekat rumah.')
]
lessons=[]
for n,(title,subtitle,text,translation,dialog,theory,exercise,answer) in enumerate(samples,1):
    ident=f'intro-{n}'
    blocks=[{'id':f'{ident}-{kind}','kind':kind,'title':label,'text':content,'pages':[],
             **({'translation':translation} if kind=='read' else {}),
             **({'answer':answer} if kind=='exercise' else {})}
            for kind,label,content in [('read','Текст',text),('dialog','Диалог',dialog),('theory','Разбор',theory),('exercise','Практика',exercise)]]
    lessons.append({'id':ident,'number':n,'stage':'intro','title':title,'subtitle':subtitle,
                    'pages':[],'blocks':blocks})

vocab='''saya|я
Anda|Вы
dia|он, она
kami|мы (без собеседника)
kita|мы (с собеседником)
mereka|они
ini|это; этот
itu|то; тот
nama|имя
namanya|его/её зовут; его/её имя
dari|из; от
Rusia|Россия
Indonesia|Индонезия
bahasa|язык
belajar|учиться; изучать
teman|друг
selamat|благополучный; часть формул приветствия
pagi|утро
selamat pagi|доброе утро
siapa|кто
mana|который; где (в вопросительных сочетаниях)
senang|рад; довольный
berkenalan|знакомиться
dengan|с
mahasiswa|студент
guru|учитель
di|в; на (местоположение)
ke|в; к (направление)
universitas|университет
setiap|каждый
membaca|читать
baca|читать (основа)
buku|книга
menulis|писать
tulis|писать (основа)
kelas|класс; занятие
berbicara|говорить
hari|день
hari ini|сегодня
tidak|не (при глаголах и признаках)
bukan|не (при именах)
bekerja|работать
kerja|работа
rumah|дом
apa|что
yang|который; показатель определительной конструкции
lakukan|делать; выполнять
apakah|вопросительная частица
ya|да
tinggal|жить; оставаться
Jakarta|Джакарта
dekat|близкий; рядом
stasiun|станция; вокзал
depan|передняя сторона
di depan|перед
ada|есть; находиться
toko|магазин
pergi|идти; ехать; уходить
membeli|покупать
beli|покупать (основа)
air|вода
dan|и
roti|хлеб
setelah|после
setelah itu|после этого
pulang|возвращаться домой
permisi|извините; разрешите
di mana|где
sebelah|сторона; рядом с
kiri|левый; слева
kanan|правый; справа
jauh|далёкий; далеко
sini|здесь
dari sini|отсюда
silakan|пожалуйста (приглашение к действию)
jalan|дорога; идти пешком
lurus|прямой; прямо
terima kasih|спасибо
sama-sama|пожалуйста (ответ на благодарность)
berita|новость; новости
negara|страна; государство
pemerintah|правительство
masyarakat|общество; население
ekonomi|экономика
internasional|международный
kerja sama|сотрудничество
keamanan|безопасность
perdamaian|мир (отсутствие войны)
bantuan|помощь
kemanusiaan|гуманность; гуманитарная сфера
bantuan kemanusiaan|гуманитарная помощь
bencana|бедствие
penduduk|жители; население
perundingan|переговоры
perjanjian|соглашение
perbatasan|граница
pertahanan|оборона
angkatan bersenjata|вооружённые силы
angkatan darat|сухопутные войска
angkatan laut|военно-морские силы
angkatan udara|военно-воздушные силы
latihan|учение; упражнение
pasukan|войска; подразделение
komunikasi|связь; коммуникация
laporan|доклад; отчёт
petugas|сотрудник; дежурный
evakuasi|эвакуация
pelabuhan|порт
kapal|корабль
pesawat|самолёт
udara|воздух
laut|море
darat|суша
keselamatan|безопасность; сохранность
operasi|операция
tim|команда; группа
medis|медицинский
obat|лекарство
korban|пострадавший; жертва
informasi|информация
resmi|официальный
sumber|источник
terbaru|новейший
politik|политика; политический
hubungan|отношения; связь
tujuan|цель
dialog|диалог
damai|мирный
menjaga|охранять; поддерживать
melindungi|защищать
membantu|помогать
mengirim|отправлять
menyampaikan|передавать; сообщать
melaporkan|докладывать; сообщать
memeriksa|проверять
memastikan|обеспечивать; удостоверяться
harus|должен
perlu|необходимо
dapat|мочь; получать
akan|показатель будущего
sudah|уже
belum|ещё не
sedang|показатель текущего действия
untuk|для; чтобы
karena|потому что
tetapi|но
jika|если
sebelum|до; прежде чем
selama|во время; на протяжении
semua|все
baru|новый
penting|важный
baik|хороший
aman|безопасный
cepat|быстрый
besar|большой
kecil|маленький
satu|один
dua|два
tiga|три
empat|четыре
lima|пять
enam|шесть
tujuh|семь
delapan|восемь
sembilan|девять
sepuluh|десять'''
entries=[]
for line in vocab.splitlines():
    word,translation=line.split('|',1)
    entries.append({'word':word,'translation':translation,'lang':'id'})
    for gloss in translation.split(';'):
        entries.append({'word':gloss.strip(),'translation':word,'lang':'ru'})
for l in lessons:
    selected=[e for e in entries if e['lang']=='id' and re.search(r'(?<!\w)'+re.escape(e['word'])+r'(?!\w)', ' '.join(b['text'] for b in l['blocks']), re.I)]
    l['blocks'].append({'id':l['id']+'-vocab','kind':'vocab','title':'Слова урока','text':'\n'.join(e['word']+' — '+e['translation'] for e in selected),'pages':[]})
course={'title':'Индонезийский язык · вводные примеры','authors':[], 'year':2026,'pageCount':0,'ocr':False,
        'status':'awaiting-user-materials','lessons':lessons,'dictionaryEntries':len(entries)}
(DEST/'course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2))
(DEST/'dictionary.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2))
(DEST/'audio.json').write_text('[]\n')

# Reuse behavior, but isolate every language-specific URL, label, and storage key.
def localize(s):
    pairs=[('Малайская','Индонезийская'),('МАЛАЙСКАЯ','ИНДОНЕЗИЙСКАЯ'),('малайская','индонезийская'),
           ('Малайский','Индонезийский'),('малайский','индонезийский'),('малайского','индонезийского'),
           ('малайском','индонезийском'),('малайско','индонезийско'),('малайские','индонезийские'),
           ('Bahasa Melayu','Bahasa Indonesia'),('Melayu','Indonesia'),('малайзийского','индонезийского'),
           ('MS','ID'),("'ms'","'id'"),('"ms"','"id"'),('ms:new','id:new'),('dictIndex.ms','dictIndex.id'),
           ('?sl=ms','?sl=id'),('malay-','indonesian-')]
    for a,b in pairs:s=s.replace(a,b)
    return s.replace('.ms', '.id')

html=(ROOT/'index.html').read_text()
# Strip an existing switch when rebuilding.
html=re.sub(r'<div class="header-actions">.*?</div>(?=</div><nav)', '<button type="button" id="theme" class="icon-btn" aria-label="Сменить цветовую тему">☼</button>', html)
def switch(lang):
    return '<div class="header-actions"><nav class="language-switch" aria-label="Язык обучения">'+''.join(
        f'<a href="{url}" data-language-link="{code}"'+(' aria-current="true"' if code==lang else '')+f'>{label}</a>'
        for code,url,label in [('ms','index.html','Малайский'),('id','indonesian.html','Индонезийский')])+'</nav><button type="button" id="theme" class="icon-btn" aria-label="Сменить цветовую тему">☼</button></div>'
theme='<button type="button" id="theme" class="icon-btn" aria-label="Сменить цветовую тему">☼</button>'
html=re.sub(r'school.css\?v=[^"\s]+','school.css?v=20261105-languages',html)
html=re.sub(r'school.js\?v=[^"\s]+','school.js?v=20261105-languages',html)
(ROOT/'index.html').write_text(html.replace(theme,switch('ms')))
ind=localize(html).replace('school.js?v=20261105-languages','indonesian-school.js?v=20261105-languages')
ind=ind.replace('учебник Дорофеевой и Кукушкиной, упражнения, аудирование и перевод слов по нажатию.', 'уроки, диалоги, практика перевода и слова по нажатию.')
(ROOT/'indonesian.html').write_text(ind.replace(theme,switch('id')))
js=localize((ROOT/'school.js').read_text())
js=js.replace("fetch('assets/", "fetch('assets/indonesian/")
js=js.replace('href="military.html?', 'href="indonesian-military.html?').replace('src="military.html?', 'src="indonesian-military.html?')
js=js.replace("start();\n", "")
js += '\n' + (ROOT/'scripts/indonesian-ui.js').read_text() + '\nstart();\n'
(ROOT/'indonesian-school.js').write_text(js)

# Four bilingual original practice scenarios; all trainer modes remain available.
scenarios=[
 ('Гуманитарная помощь','Bantuan kemanusiaan',
  'Tim medis mengirim obat dan air ke daerah bencana. Petugas membantu penduduk dan memeriksa kebutuhan mereka. Keselamatan semua orang menjadi tujuan utama operasi ini.',
  'Медицинская группа отправляет лекарства и воду в район бедствия. Сотрудники помогают жителям и проверяют их потребности. Безопасность всех людей является главной целью этой операции.',
  [('Ke mana tim medis mengirim bantuan?','Куда медицинская группа отправляет помощь?'),('Tim medis mengirim bantuan ke daerah bencana.','Медицинская группа отправляет помощь в район бедствия.'),('Apa tujuan utama operasi ini?','Какова главная цель этой операции?'),('Tujuan utamanya adalah keselamatan semua orang.','Главная цель — безопасность всех людей.')]),
 ('Международный диалог','Dialog internasional',
  'Perwakilan kedua negara membahas kerja sama dan keamanan. Mereka menyampaikan pandangan masing-masing melalui dialog. Kedua pihak ingin menjaga perdamaian dan menyelesaikan masalah secara damai.',
  'Представители двух стран обсуждают сотрудничество и безопасность. Они излагают свои позиции в ходе диалога. Обе стороны хотят поддерживать мир и решать проблемы мирным путём.',
  [('Apa yang dibahas oleh perwakilan kedua negara?','Что обсуждают представители двух стран?'),('Mereka membahas kerja sama dan keamanan.','Они обсуждают сотрудничество и безопасность.'),('Bagaimana kedua pihak ingin menyelesaikan masalah?','Как обе стороны хотят решать проблемы?'),('Mereka ingin menyelesaikan masalah secara damai.','Они хотят решать проблемы мирным путём.')]),
 ('Доклад и связь','Laporan dan komunikasi',
  'Petugas menyampaikan laporan resmi kepada pemimpin tim. Laporan itu berisi informasi tentang keadaan penduduk. Semua informasi harus diperiksa sebelum disampaikan kepada masyarakat.',
  'Сотрудник передаёт официальный доклад руководителю группы. Доклад содержит сведения о положении жителей. Всю информацию необходимо проверить перед передачей населению.',
  [('Kepada siapa laporan disampaikan?','Кому передают доклад?'),('Laporan disampaikan kepada pemimpin tim.','Доклад передают руководителю группы.'),('Kapan informasi harus diperiksa?','Когда нужно проверять информацию?'),('Informasi harus diperiksa sebelum disampaikan kepada masyarakat.','Информацию нужно проверять до передачи населению.')]),
 ('Безопасность на море','Keselamatan di laut',
  'Kapal itu berada di dekat pelabuhan. Petugas memeriksa alat komunikasi sebelum kapal berangkat. Tim harus memastikan bahwa semua orang memahami aturan keselamatan selama perjalanan.',
  'Корабль находится рядом с портом. Сотрудники проверяют средства связи перед его отправлением. Группа должна убедиться, что все понимают правила безопасности во время плавания.',
  [('Di mana kapal itu berada?','Где находится корабль?'),('Kapal itu berada di dekat pelabuhan.','Корабль находится рядом с портом.'),('Apa yang diperiksa sebelum kapal berangkat?','Что проверяют перед отправлением корабля?'),('Petugas memeriksa alat komunikasi.','Сотрудники проверяют средства связи.')])]
data={'texts':[],'dialogs':[],'topics':[],'terms':[]}
for n,(title,idtitle,text,ru,dialog) in enumerate(scenarios,1):
    for section,lang,body in [(1,'id',text),(2,'ru',ru),(3,'ru',ru),(4,'id',text)]:
        ident=len(data['texts'])+1
        kind={1:'Письменный · ID → RU',2:'Письменный · RU → ID',3:'Последовательный · RU → ID',4:'Зрительно-устный · ID → RU'}[section]
        data['texts'].append({'id':ident,'section':section,'kind':kind,'lang':lang,'body':body,'title':title,'words':len(body.split())})
    data['dialogs'].append({'id':n,'title':title,'pairs':[{'id':a,'ru':b} for a,b in dialog]})
    words=[e for e in entries if e['lang']=='id' and e['word'].lower() in text.lower() and len(e['word'])>5][:12]
    terms=[{'id':e['word'],'ru':e['translation'],'topic':n} for e in words]
    data['terms']+=terms
    data['topics'].append({'id':n,'title':idtitle,'text':text,'vocab':terms,'questions':[dialog[0][0],dialog[2][0]]})
# Card choices require unique terms.
data['terms']=list({x['id']:x for x in data['terms']}.values())
trainer=(ROOT/'military.html').read_text()
trainer=re.sub(r'(<script type="application/json" id="embedded-data">).*?(</script>)',lambda m:m[1]+json.dumps(data,ensure_ascii=False)+m[2],trainer,flags=re.S)
trainer=localize(trainer).replace('news.json','indonesian-news.json').replace('Astro AWANI','ANTARA').replace('https://www.astroawani.com/','https://www.antaranews.com/').replace('military-words.js','indonesian-military-words.js')
trainer=trainer.replace('Тексты из сборника;', 'Короткие авторские учебные примеры;')
# The Malay exam specification cannot be presented as official Indonesian requirements.
trainer=re.sub(r'<div class="pane notice"><strong>Формат письменной ГИА:.*?</details>', '<div class="pane notice">Учебный режим: два направления перевода и таймер 120 минут. Это тренировочный шаблон; требования к индонезийскому экзамену и материалы будут подключены после получения от вас.</div>', trainer,flags=re.S)
trainer=trainer.replace('34 текста','16 коротких заданий').replace('14 опорных текстов','4 учебных темы').replace('70 выражениям',str(len(data['terms']))+' выражениям')
(ROOT/'indonesian-military.html').write_text(trainer)
words=localize((ROOT/'military-words.js').read_text()).replace("'index.html?word='", "'indonesian.html?word='")
(ROOT/'indonesian-military-words.js').write_text(words)
print(f'Built Indonesian edition: {len(lessons)} sample lessons, {len(entries)} dictionary entries, {len(data["texts"])} practice tasks.')
