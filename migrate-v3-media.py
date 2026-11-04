import json,pathlib,subprocess,hashlib
r=pathlib.Path(__file__).parent;s=pathlib.Path('/workspace/shared/stk-source-audit-v3-20261030/public-site')
h=json.loads((s/'homepage.json').read_text());names=[('W-Kurs kennenlernen','Explore the W course'),('Studienkolleg erleben','Experience Studienkolleg'),('Pedro erzählt','Pedro’s story'),('Internationale Gemeinschaft','International community'),('M-Kurs kennenlernen','Explore the M course'),('Deutsch: Wortschatz','German vocabulary'),('Tipps zum Deutschlernen','German learning tips'),('Feststellungsprüfung erklärt','The assessment examination'),('Einblick ins Wohnen','A glimpse of housing'),('Studienkolleg Aachen','Studienkolleg Aachen'),('Unterstützung beim Ankommen','Support for your arrival')];videos=[]
for i,a in enumerate(x for x in h['assets'] if x.get('tag')=='VIDEO'):
 f=r/'dist/assets'/('video-poster-'+str(i)+'.jpg');res=subprocess.run(['curl','-L','--fail','--silent','--show-error',a['poster'],'-o',str(f)])
 videos.append({'id':'V'+str(i+1).zfill(2),'title':names[i],'src':a['src'],'poster':'assets/'+f.name if res.returncode==0 else None,'source':h['url'],'captured':'2026-10-30','poster_sha256':hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None})
(r/'dist/media-data.js').write_text('const MIGRATED_MEDIA='+json.dumps(videos,ensure_ascii=False)+';')
(r/'V3-MEDIA-PROVENANCE.json').write_text(json.dumps(videos,ensure_ascii=False,indent=2));print(len(videos),'video references preserved; video remote loads only on user opening player')
