import json, subprocess, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from html.parser import HTMLParser
class Plain(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self,data): self.parts.append(data)
def plain(text):
    p=Plain(); p.feed(text or ''); return ''.join(p.parts).strip()
root=Path(__file__).resolve().parents[1]
import sys
indonesian='--indonesian' in sys.argv
path=root/('indonesian-news.json' if indonesian else 'news.json')
data=json.loads(path.read_text()) if path.exists() else {'feeds':{}}
for cat in ['latest','international','politics','business']:
    try:
        feed=({'latest':'terkini','international':'dunia','politics':'politik','business':'ekonomi'}[cat] if indonesian else cat)
        url=('https://www.antaranews.com/rss/'+feed+'.xml') if indonesian else ('https://www.astroawani.com/rss/'+cat+'/public')
        xml=subprocess.check_output(['curl','--fail','--silent','--show-error','--location','--max-time','30',url]).strip()
        doc=ET.fromstring(xml)
        items=[{'title':plain(n.findtext('title')),'summary':plain(n.findtext('description'))[:700],'url':(n.findtext('link') or '').strip(),'date':n.findtext('pubDate') or ''} for n in doc.findall('./channel/item')[:12]]
        if not items: raise ValueError('Empty feed')
        data['feeds'][cat]={'updated':datetime.now(timezone.utc).isoformat(),'items':items}
        print(cat, len(items))
    except Exception as e:
        print(cat,'unavailable:',type(e).__name__)
if not data['feeds']: raise SystemExit('No news feeds available')
path.write_text(json.dumps(data,ensure_ascii=False,indent=2))
