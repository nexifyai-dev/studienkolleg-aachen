import json,pathlib,re,hashlib
root=pathlib.Path(__file__).parent;src=pathlib.Path('/workspace/shared/stk-source-audit-v3-20261030/public-site')
kb=[]
for i,p in enumerate(json.loads((src/'knowledge-all.json').read_text())):
 body=p['text'].split('1.770 von 1.770 Beiträgen\n',1)[-1].split(f'Seite {i+1} von 89')[0]
 chunks=body.strip().split('\n\n')
 for j in range(0,len(chunks)-1,2):
  heading=chunks[j].strip().split('\n');answer=chunks[j+1].strip()
  if len(heading)!=2:raise Exception((i,j,heading))
  kb.append({'id':f'K{len(kb)+1:04}','topic':heading[0],'title':heading[1],'text':answer,'source':p['url'],'page':i+1,'locale':'de','observed':'2026-10-30','verification':'source-captured-not-substantively-revalidated'})
assert len(kb)==1770,len(kb)
legal={}
for p in json.loads((src/'legal-sections.json').read_text()):legal[p['url']]=p['text']
legal_records=[]
for url,text in legal.items():
 body=text.split('INHALTSVERZEICHNIS\n\n',1)[-1].split('Fragen zu unseren Rechtsdokumenten?')[0]
 legal_records.append({'id':url.split('/')[-1],'text':body,'source':url,'observed':'2026-10-30','verification':'published-wording-not-legal-approval'})
(root/'dist/content-data.js').write_text('const MIGRATED_KNOWLEDGE='+json.dumps(kb,ensure_ascii=False)+';\nconst MIGRATED_LEGAL='+json.dumps(legal_records,ensure_ascii=False)+';\n')
matrix=json.loads((src/'migration-content-matrix.json').read_text())
(root/'V3-MIGRATION-REGISTER.json').write_text(json.dumps({'scope':'source inventory, NOT implemented product coverage','records':matrix},ensure_ascii=False,indent=2))
(root/'V3-CONTENT-PROVENANCE.json').write_text(json.dumps({'knowledge':len(kb),'legal':len(legal_records),'source_files':[{ 'file':str(src/f),'sha256':hashlib.sha256((src/f).read_bytes()).hexdigest()} for f in ['knowledge-all.json','legal-sections.json','migration-content-matrix.json']]},indent=2))
print(len(kb),'knowledge entries;',len(legal_records),'legal source documents')
