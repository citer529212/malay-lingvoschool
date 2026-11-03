"""Build the reading course from cached OCR; the supplied page scans remain the source of truth."""
import re,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OCR=Path(sys.argv[1]) if len(sys.argv)>1 else None
RAW=json.loads((ROOT/'sources/book-ocr.json').read_text()) if OCR is None else None
starts_intro=[14,18,23,26,33,38,45,54,60]
starts_basic=[68,78,87,96,105,115,126,136,144,154,165,175,185,196,206,217,226,237,248,258,267,277,285,294,304,313,323,332,341,350,359]
intro_titles=['Первые звуки и правила чтения','Гласные o, e и звонкие согласные','Звуки c, j, ny, ng','Простое предложение','Описание предметов','Число, связки и общий вопрос','Знакомство и местонахождение','Пространство и направления','Отрицание и вопросы']
intro_sub=['Звуки a, u, i, e; согласные p, t, m, n, k','Звуки o, e; согласные b, d, g','Чтение и произношение; первые слова','Корневые слова, простой глагол, вопрос apa','Атрибутивные сочетания и принадлежность','Дифтонги, категория числа, частица kah','Siapa, предлоги, ada, энклитики','Пространственные слова и сложные предлоги','Гармония гласных, tidak, bukan, adakah']
titles=['Семья обедает','В институте','Календарь. Времена года','Учебный день','Покупки. На рынке. В магазине','Поездка. Вокзал','Две столицы','Повторение · уроки 1–7','Праздники Малайзии','Режим дня','Средства коммуникации. Почта. Интернет','Бедствия. У врача. Болезни','Спорт','День рождения','Осмотр достопримечательностей','Повторение · уроки 9–15','Досуг. Кино','Правила корреспонденции','Образование Малайзии. Малайская свадьба','Повторение · уроки 17–19','Многоязычная Малайзия','Год туризма в Малайзии','Политическая нестабильность в мире','История Куала-Лумпура. Реклама','Малайские пантуны','Усман Аванг — национальный писатель','Китайский Новый год','Абдулла Мунши: жизнь и творчество','Язык и национальная культура','Новые малайцы. Жалованные титулы','Наводнения. Наследственные титулы']
sub=['Keluarga makan tengahari','Di institut','Kalendar. Musim','Hari belajar','Membeli-belah. Di pasar. Di kedai','Perjalanan. Stesyen keretapi','Dua ibu negara','Повторение пройденной грамматики и лексики','Hari-hari besar di Malaysia','Jadual waktu','Alat-alat komunikasi. Pos. Internet','Bencana. Jumpa doktor. Penyakit','Sukan','Pesta hari jadi','Melawat tempat-tempat menarik','Повторение пройденной грамматики и лексики','Masa lapang. Menonton wayang gambar','Cara menulis surat kiriman','Pembentukan Malaysia. Nikah kahwin cara Melayu','Повторение пройденной грамматики и лексики','Malaysia yang berbilang bahasa','Tahun Melawat Malaysia','Pergolakan politik di dunia','Sejarah ringkas Kuala Lumpur. Iklan','Pantun Melayu','Usman Awang Sasterawan Negara','Tahun Baru Cina','Riwayat hidup dan karya-karya Abdullah Munsyi','Bahasa Malaysia sebagai asas kebudayaan Malaysia','Melayu Baru. Gelaran Kurniaan','Banjir. Gelaran Warisan']
lessons=[{'id':'orientation-0','stage':'orientation','number':0,'title':'Введение. Алфавит и звуковой состав','subtitle':'Как устроен малайский язык и как пользоваться учебником','start':12}]
lessons +=[{'id':f'intro-{i+1}','stage':'intro','number':i+1,'title':t,'subtitle':intro_sub[i],'start':starts_intro[i]} for i,t in enumerate(intro_titles)]
lessons +=[{'id':f'basic-{i+1}','stage':'basic','number':i+1,'title':t,'subtitle':sub[i],'start':starts_basic[i]} for i,t in enumerate(titles)]
# Locate lesson starts within a page. Running headers can refer to the next lesson while the page still starts with the previous vocabulary list.
def marker(line,number):
 l=line.strip()
 if re.fullmatch(r'(?:УРОК|Урок)\s*(?:\(PELAJARAN\)\s*)?'+str(number)+r'(?:\s*\(ПОВТОРИТЕЛЬНЫЙ\))?',l,re.I):return True
 if re.fullmatch(r'(?:PELAJARAN|РЕГА\]АКАМ)\s*'+str(number),l,re.I):return True
 return False
all_lines=[]
for page in range(12,369):
 raw=(RAW[str(page)] if RAW is not None else (OCR/f'ocr-{page:03}.txt').read_text()).splitlines()
 for i,line in enumerate(raw):
  if i<3 and re.search(r'^(?:ОСНОВНОЙ КУРС|ВВОДНО-ФОНЕТИЧЕСКИЙ КУРС)',line.strip()):continue
  if i>=len(raw)-4 and re.fullmatch(r'\s*\d{1,3}\s*',line):continue
  all_lines.append((page,line))
positions=[]
for l in lessons:
 if l['number']==0:pos=0
 else:
  candidates=[i for i,(p,line) in enumerate(all_lines) if p==l['start'] and marker(line,l['number'])]
  if not candidates:raise ValueError('Missing lesson marker '+l['id'])
  pos=candidates[0]
 positions.append(pos)
positions.append(len(all_lines))
# Correct only frequent, unambiguous OCR substitutions inside predominantly Latin passages.
latin_fix={'ара':'apa','рада':'pada','рааа':'pada','Керада':'kepada','Кати':'kamu','КИа':'kita','Киа':'kita','ВиКи':'Buku','Кор!':'kopi','пата':'nama','таКап':'makan','таг!':'mari','Бей':'beli','Бег':'beri','реп':'pen','Бипра':'bunga','тепра':'tengah','ци':'itu'}
def clean_text(s):
 s=re.sub(r'(?<=[а-яa-z])-\n(?=[а-яa-z])','',s)
 paras=[]
 for p in re.split(r'\n\s*\n',s.strip()):
  latin=len(re.findall('[a-z]',p,re.I));cyr=len(re.findall('[а-я]',p,re.I))
  if latin>2*cyr:
   for a,b in latin_fix.items():p=re.sub(r'(?<![\w])'+re.escape(a)+r'(?![\w])',b,p)
  # Keep dialogue speaker turns and numbered tasks on new lines; reflow ordinary print line wrapping.
  lines=p.splitlines();out=''
  for line in lines:
   sep='\n' if re.match(r'\s*(?:[-–—]|\d{1,2}[.)]|[A-Za-z]+\s*:)',line) else ' '
   out+=(sep if out else '')+line.strip()
  paras.append(out)
 return '\n\n'.join(paras)
verbs=r'(?:Слуш|Прослуш|Прочит|Перевед|Встав|Ответ|Состав|Раскр|Спиш|Заполн|Объяс|Придум|Выберите|Употреб|Дополн|Замен|Повтор|Дайте|Лексич|Инсцен|Опиш|Использ|Расскаж|Постав|Преобраз|Выуч|Укажите|Перепиш|Законч|Произнес|Сравните|Подготов|T[eu]rjem|Jawab|Baca|Bincang|Tulis|Isi|Lengkap|Buat|Cari|Berikan|Tukar|Hafal|Perhati|Sebut|Dengar|Ulang|Cerit|Susun|Pelajar|Huraikan|Terang|Tentukan|Pilih|Bincang|Lihat|Bentuk|Ungkap|Jelaskan|Kenal|Текет|Тенет)'
exercise_re=re.compile(r'^\s*(\d{1,2})[.,)]\s*'+verbs,re.I)
for idx,l in enumerate(lessons):
 lines=all_lines[positions[idx]:positions[idx+1]]
 l['pages']=sorted(set(p for p,_ in lines));l['startPrint']=min(l['pages'])-1;l['endPrint']=max(l['pages'])-1
 blocks=[];current={'kind':'theory','title':'План урока' if l['number'] else 'Вводные замечания','lines':[],'pages':[]}
 def flush():
  text=clean_text('\n'.join(current['lines']))
  if text and len(text)>4:
   b={'id':l['id']+'-b'+str(len(blocks)+1),'kind':current['kind'],'title':current['title'],'text':text,'pages':sorted(set(current['pages']))}
   if current.get('number'):b['number']=current['number']
   blocks.append(b)
 def switch(kind,title,page,number=None):
  global current
  flush();current={'kind':kind,'title':title,'lines':[],'pages':[page],**({'number':number} if number else {})}
 for j,(page,line) in enumerate(lines):
  st=line.strip();up=st.upper()
  if marker(st,l['number']):continue
  if st in ['(ПОВТОРИТЕЛЬНЫЙ)','ВВОДНЫЙ УРОК']:continue
  if re.search(r'^ИСПОЛЬЗУЕМЫЕ СОКРАЩЕНИЯ',st):break
  if re.match(r'^(?:Слова (?:к |и выражения к |урока)|(?:Kosa|Коза)\s+kata)',st,re.I) and len(st)<60:
   switch('vocab','Слова и выражения урока',page);continue
  if l['id']=='intro-8' and page==57 and st.startswith('Ahmad -'):
   switch('dialog','Диалог · в кафе',page)
  if re.match(r'^(?:Dialog|Perbualan|[Дд]?иалог)(?:\b|:)',st,re.I) and len(st)<120:
   switch('dialog',st,page);continue
  if re.match(r'^(?:TEKS|ТЕКСТ|ТЕХТ)(?:\s*\d+)?$',st,re.I):
   switch('read','Текст урока',page);continue
  if ('УПРАЖНЕНИЯ' in up or re.match(r'^LATIHAN(?:\s|$)',up)) and len(st)<85:
   switch('exercise','Упражнения',page);continue
  if re.fullmatch(r'[®*›«»©$ \-]*(?:ГРАММАТИКА|ФОНЕТИКА|КОММЕНТАРИЙ|КОММЕНТАРИИ|TATA BAHASA|TATABAHASA)[®*›«»©$ :\-]*',up):
   switch('theory',st.strip('®*›«»©$ :'),page);continue
  if re.fullmatch(r'[®*›«»©$ ]*ЗАПОМНИТЕ[®*›«»©$ ]*',up):
   switch('vocab','Запомните · выражения',page);continue
  ex=exercise_re.match(st)
  if ex:
   switch('exercise','Упражнение '+ex.group(1),page,int(ex.group(1)));current['lines'].append(line);continue
  if re.match(r'^(?:Ответьте на вопросы|Jawab soalan)',st,re.I):
   switch('exercise','Вопросы к тексту',page);current['lines'].append(line);continue
  # Malay reading titles are typeset in capitals before the actual passage.
  lat=len(re.findall('[A-Z]',st));cyr=len(re.findall('[А-Я]',st))
  if l['stage']=='basic' and len(st)>4 and len(st)<110 and st==up and lat>3 and lat>2*cyr and not re.search(r'(ГРАММАТИКА|ЛЕКСИЧЕСКАЯ|УРОК|KOSA|LATIHAN|PELAJARAN)',up):
   # Avoid turning abbreviated labels and table rows in grammar into new reading passages.
   if current['kind'] in ['read','dialog'] or (current['title']=='План урока'):
    switch('read',st,page);continue
  if l['stage']=='basic' and current['title']=='План урока':
   la=len(re.findall('[a-z]',st,re.I));cy=len(re.findall('[а-я]',st,re.I))
   if la>25 and cy<la*.15 and not re.search(r'(ГРАММАТИКА|ЛЕКСИЧЕСК|kata penghubung)',st,re.I):
    switch('read',l['subtitle'],page)
  current['lines'].append(line);current['pages'].append(page)
 flush();l['blocks']=blocks;l.pop('start',None)

 l['counts']={k:sum(b['kind']==k for b in blocks) for k in ['read','dialog','theory','exercise','vocab']}
output={'title':'Учебник малайского (малайзийского) языка','authors':['Т. В. Дорофеева','Е. С. Кукушкина'],'year':2006,'pageCount':385,'ocr':True,'lessons':lessons}
(ROOT/'assets/course.json').write_text(json.dumps(output,ensure_ascii=False,separators=(',',':')))
print('LESSONS',len(lessons),'BLOCKS',sum(len(l['blocks']) for l in lessons))
for l in lessons:print(l['id'],l['startPrint'],l['endPrint'],l['counts'])
