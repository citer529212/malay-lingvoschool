"""Check isolation, language codes and publication files for both editions."""
from pathlib import Path
import json,re,subprocess
from urllib.parse import urlparse
root=Path(__file__).resolve().parents[1]
course=json.loads((root/'assets/indonesian/course.json').read_text())
assert course['status']=='awaiting-user-materials'
assert len(course['lessons'])==3
ids=[]
for lesson in course['lessons']:
    assert {'read','dialog','theory','exercise','vocab'} <= {b['kind'] for b in lesson['blocks']}
    assert not lesson['pages']
    for block in lesson['blocks']:
        assert block['text'].strip()
        ids.append(block['id'])
assert len(ids)==len(set(ids))
rows=json.loads((root/'assets/indonesian/dictionary.json').read_text())
assert len(rows)==course['dictionaryEntries']
assert {r['lang'] for r in rows}=={'id','ru'}
assert any(r['word']=='air' and r['translation']=='вода' for r in rows)
source=(root/'indonesian-school.js').read_text()
assert "KEY='indonesian-textbook-v1'" in source
assert "'ms'" not in source and 'dictIndex.ms' not in source
assert "fetch('assets/indonesian/dictionary.json')" in source
assert "'indonesian-school'" in source
trainer=(root/'indonesian-military.html').read_text()
data=json.loads(re.search(r'id="embedded-data">(.*?)</script>',trainer,re.S).group(1))
assert {t['section'] for t in data['texts']}=={1,2,3,4}
assert len({x['id'] for x in data['terms']})>=10
assert all(t['lang'] in ['id','ru'] for t in data['texts'])
assert "KEY='indonesian-gia-2026-v2'" in trainer
assert "localStorage.getItem('malay" not in trainer
assert "'langpair',dir+'|'+(dir==='id'?'ru':'id')" in trainer
for cat in ['latest','international','politics','business']:
    feed=json.loads((root/'indonesian-news.json').read_text())['feeds'][cat]
    assert feed['items'] and all((urlparse(i['url']).hostname or '').endswith('.antaranews.com') for i in feed['items'])
for page in ['index.html','indonesian.html']:
    html=(root/page).read_text()
    assert 'data-language-link="ms"' in html and 'data-language-link="id"' in html
    for asset in re.findall(r'(?:src|href)="([^"?#]+)',html):
        if not asset.startswith(('http', '#')):assert (root/asset).is_file(),asset
# Parse each inline trainer script, including the renamed id/ru object fields.
for script in re.findall(r'<script>(.*?)</script>',trainer,re.S):
    subprocess.run(['node','--check'],input=script,text=True,check=True)
print('OK: Indonesian samples, bidirectional dictionary, independent progress, translator language codes, RSS and publication files.')
