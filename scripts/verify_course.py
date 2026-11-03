"""Check content migration and all public asset references before publication."""
from pathlib import Path
import json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
course=json.loads((ROOT/'assets/course.json').read_text())
audios=json.loads((ROOT/'assets/audio.json').read_text())
dictionary=json.loads((ROOT/'assets/dictionary.json').read_text())
lessons=course['lessons'];assert len(lessons)==41
assert [l['number'] for l in lessons if l['stage']=='intro']==list(range(1,10))
assert [l['number'] for l in lessons if l['stage']=='basic']==list(range(1,32))
assert len(set(l['id'] for l in lessons))==41
ids=[]
for l in lessons:
 assert l['blocks'] and l['pages'],l['id']
 if l['stage']=='basic':assert any(b['kind']=='read' for b in l['blocks']),l['id']
 for b in l['blocks']:
  ids.append(b['id']);assert b['text'].strip() and b['pages'],b['id']
  assert all(p in l['pages'] for p in b['pages']),b['id']
  for p in b['pages']:assert (ROOT/f'assets/book/{p:03}.webp').is_file(),(b['id'],p)
assert len(ids)==len(set(ids))
assert len(list((ROOT/'assets/book').glob('*.webp')))==385
assert len(audios)==147 and len({a['id'] for a in audios})==147
for a in audios:
 assert (ROOT/a['src']).is_file() and (ROOT/a['src']).stat().st_size>10000,a['id']
 assert any(l['stage']==a['stage'] and l['number']==a['lesson'] for l in lessons),a['id']
assert len(dictionary)==50319
assert any(e['word']=='sekolah' and e['translation']=='школа' for e in dictionary)
legacy=(ROOT/'military.html').read_text()
get_data=lambda s:json.loads(re.search(r'<script type="application/json" id="embedded-data">(.*?)</script>',s,re.S).group(1))
D=get_data(legacy)
assert [len(D[k]) for k in ['texts','dialogs','topics','terms']]==[34,11,14,70]
assert "KEY='malay-gia-2026-v2'" in legacy
# Compare against the preserved pre-textbook release while that revision is available.
try:
 old=subprocess.check_output(['git','show','1415cec:index.html'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL)
 assert D==get_data(old),'Military training content changed during migration'
except subprocess.CalledProcessError:pass
print(f'OK: 41 lessons, {len(ids)} material blocks, 385 scans, 147 audio files, 50,319 dictionary articles; military materials preserved.')
