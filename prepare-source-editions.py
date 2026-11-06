"""Preserve legacy language-specific editorial content without duplicated navigation.
Creates typed content records; does not execute downloaded HTML or change customer sources.
"""
import json,pathlib,re,hashlib,html
from html.parser import HTMLParser
r=pathlib.Path(__file__).parent;s=pathlib.Path('/workspace/shared/stk-source-audit-v3-20261030/public-site')
legacy=json.loads((s/'legacy-pages.json').read_text());matrix=json.loads((s/'migration-content-matrix.json').read_text());byurl={p['url']:p for p in legacy}
class Blocks(HTMLParser):
 def __init__(self):super().__init__();self.depth=0;self.kind=None;self.parts=[];self.blocks=[]
 def handle_starttag(self,tag,attrs):
  if tag in ['p','h1','h2','h3','li'] and self.kind is None:self.kind=tag;self.depth=1;self.parts=[]
  elif self.kind is not None and tag not in ['br','img','input','meta','hr','source','link']:self.depth+=1
  if tag=='br' and self.kind:self.parts.append(' ')
 def handle_endtag(self,tag):
  if self.kind is not None:
   self.depth-=1
   if self.depth<=0:
    text=' '.join(''.join(self.parts).split())
    if text:self.blocks.append({'type':self.kind,'text':text})
    self.kind=None
 def handle_data(self,data):
  if self.kind:self.parts.append(data)
records=[]
for m in matrix:
 url=m['source_url'];p=byurl.get(url)
 if not p or 'studienkollegaachen.de' not in url or m['target_route_suggestion']=='/apply/bestaetigung':continue
 if p.get('status')!=200 or not p.get('text'):continue
 body=p['text']
 if '\nMenu\n' in body:body=body.rsplit('\nMenu\n',1)[1]
 for marker in ['\nContact\nAGB\nlegal notice','\nThis website uses cookies.']:
  body=body.split(marker,1)[0]
 normal=' '.join(body.split())
 parser=Blocks()
 if p.get('file') and (s/p['file']).exists():parser.feed((s/p['file']).read_text())
 selected=[]
 for b in parser.blocks:
  if len(b['text'])>4 and b['text'] in normal and b['text'] not in [x['text'] for x in selected]:selected.append(b)
 # Keep source editorial paragraphs; skip isolated navigation CTA labels.
 ignored={'TIMELINE','SERVICES','HIER BEWERBEN','APPLY NOW','Menu','language','Contact','Kontakt','AGB','legal notice','privacy policy'}
 selected=[x for x in selected if x['text'] not in ignored]
 if not selected:selected=[{'type':'p','text':line.strip()}for line in body.split('\n') if len(line.strip())>15]
 family=m['target_route_suggestion'].strip('/').replace('/','-') or 'studienkolleg'
 id=family+'-'+m.get('source_locale','en')+'-'+hashlib.sha256(url.encode()).hexdigest()[:6]
 records.append({'id':id,'family':family,'target':m['target_route_suggestion'],'locale':m.get('source_locale','en'),'title':m['title'],'blocks':selected,'source':url,'observed':m.get('observed_at'),'source_sha256':m.get('source_sha256'),'status':'original-published-editorial-text-not-newly-verified'})
(r/'V3-EDITION-PREPARED.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(len(records),'language-edition pages;',sum(len(x['blocks']) for x in records),'editorial blocks')
