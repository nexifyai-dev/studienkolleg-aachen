import json,pathlib,subprocess,hashlib
root=pathlib.Path(__file__).parent
src=pathlib.Path('/workspace/shared/stk-source-audit-v3-20261030/public-site')
pages=json.loads((src/'legacy-pages.json').read_text())
records=[]; assets=[]
keys=[('kapellenstrasse-single-draft','kapellen-single','Kapellenstraße','single',550),('kappellenstrasse-double','kapellen-double','Kapellenstraße','double',430),('vaalserstrasse-1-single','vaalser-single','Vaalser Straße 1','single',580),('vaalserstrasse-1-double','vaalser-double','Vaalser Straße 1','double',460),('vaalseerstrasse-2-double','vaalser2-double','Vaalser Straße 2','double',430),('romer-strasse-double','roemer-single','Römerstraße','single',650)]
def download(url,name):
 p=root/'dist/assets'/name
 if not p.exists():subprocess.run(['curl','-L','--fail','--retry','2','--silent','--show-error',url,'-o',str(p)],check=False)
 if not p.exists():return None
 assets.append({'url':url,'file':'assets/'+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 return 'assets/'+name
for key,id,name,kind,price in keys:
 page=next((p for p in pages if key+'/' in p['url']),None)
 if not page:continue
 pa=page.get('assets',[]);cut=next((i for i,a in enumerate(pa) if a.get('tag')=='iframe'),len(pa))
 imgs=list(dict.fromkeys(a['src'] for a in pa[:cut] if a.get('tag')=='img' and '/uploads/' in a.get('src','')))
 mapurl=next((a['src'] for a in pa if a.get('tag')=='iframe' and 'maps.google' in a.get('src','')),None)
 local=[v for i,u in enumerate(imgs) if (v:=download(u,id+'-'+hashlib.sha256(u.encode()).hexdigest()[:8]+'.jpg'))]
 roomdata=next((x['rooms'] for x in json.loads((src/'housing-normalized.json').read_text()) if x['source_url']==page['url']),[])
 records.append({'map':mapurl,'rooms':roomdata,'id':id,'name':name,'type':kind,'publishedRent':price,'deposit':650,'images':local,'source':page['url'],'observedAt':page['observed_at'],'sourceHash':page['sha256'],'status':'published-source-not-live-availability'})
for path,name in [('images/team/laura-saboor.jpg','laura-saboor.jpg'),('images/campus/life/klassenzimmer-szene.jpg','campus-classroom.jpg'),('images/campus/life/motivationsschreiben-unterricht.jpg','campus-workshop.jpg')]:
 download('https://deinstudienkolleg.de/'+path,name)
(root/'dist/migration-data.js').write_text('const MIGRATED_HOUSING='+json.dumps(records,ensure_ascii=False)+';\n')
(root/'V3-ASSET-PROVENANCE.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
print('Migrated',len(records),'housing records;',len(assets),'assets')
