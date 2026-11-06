const vm=require('vm'),fs=require('fs'),assert=require('assert');const elements={};const listeners={};function el(id){return elements[id]??={innerHTML:'',textContent:'',value:'',checked:false,dataset:{},classList:{add(){},remove(){},toggle(){},contains(){return false}},addEventListener(type,fn){(listeners[id]??={})[type]=fn},focus(){},scrollIntoView(){},querySelectorAll(){return []},querySelector(){return null},scrollTop:0,scrollHeight:0}}const sandbox={console,location:{hash:'#/'},document:{documentElement:{lang:'de'},body:el('body'),getElementById:el,querySelectorAll(){return []},querySelector(s){return s==='body>.skip'?el('skip'):null},addEventListener(){}},window:{addEventListener(){},scrollTo(){}},setTimeout(){},clearTimeout(){}};vm.createContext(sandbox);for(const f of ['app.js','coverage-data.js','v2.js','migration-data.js','v3.js','content-data.js','v3-content.js','edition-data.js','media-data.js','v3-migration.js','admissions.js','learning-journey.js','attendance-journey.js','case-journey.js','appointment-journey.js','rental-journey.js','library-journey.js','arrival-journey.js','knowledge-journey.js'])vm.runInContext(fs.readFileSync(__dirname+'/dist/'+f,'utf8'),sandbox,{filename:f});const run=s=>vm.runInContext(s,sandbox);const go=r=>{sandbox.location.hash='#'+r;run('render()');return el('app').innerHTML};const tested=[];function check(name,fn){fn();tested.push(name)}

check('Missing samples: review, required reason, escaped request and same-case response',()=>{
 assert(go('/staff/admissions').includes('Keine Akte'));
 run("reviewAction('start');reviewAction('review');reviewAction('request')");assert.equal(run('ADMISSIONS.request'),null);
 run("ADMISSIONS.reason='<img src=x onerror=alert(1)>';reviewAction('request')");
 assert.equal(run('ADMISSIONS.request.items.length'),3);assert(go('/portal/applicant').includes('&lt;img'));assert(!go('/portal/applicant').includes('<img src=x'));
 run("reviewAction('document-0');reviewAction('respond');reviewAction('review')");assert.equal(run('ADMISSIONS.reviewed'),false);
 run("ADMISSIONS.quality[0]='accepted';reviewAction('review')");assert.equal(run('ADMISSIONS.request.items.join()'),'1,2');assert(!run('reviewState()').includes('erneute Prüfung offen'));
});
check('Unreadable and unclear samples remain gaps; no admission after complete review',()=>{
 run("reviewAction('document-1');reviewAction('document-2');ADMISSIONS.quality[1]='unreadable';ADMISSIONS.quality[2]='unclear';reviewAction('review')");
 assert.equal(run('reviewIssues().join()'),'1,2');
 run("ADMISSIONS.reason='Fiktiver Scan-Hinweis';reviewAction('request')");
 assert(go('/portal/applicant').includes('Unlesbar / abgeschnitten'));assert(!go('/portal/applicant').includes('Dein Entwurf ist für den nächsten Prüfschritt vorbereitet'));
 run("reviewAction('document-1');reviewAction('document-2');reviewAction('respond');ADMISSIONS.quality[1]='accepted';ADMISSIONS.quality[2]='accepted';reviewAction('review')");
 assert.equal(run('ADMISSIONS.request'),null);assert(go('/portal/applicant').includes('Fachprüfung offen'));assert(go('/staff/admissions/DEMO-001').includes('Kein Kontakt wurde durchgeführt'));
});
check('DE/EN state continuity, unknown records, role separation and draft invalidation',()=>{
 run("state.lang='en'");assert(go('/portal/applicant').includes('eligibility review pending'));assert(go('/staff/admissions/unknown').includes('Sample record not found'));
 for(const r of ['/portal/partner','/portal/teacher','/portal/student'])assert(!go(r).includes('Fiktiver Scan-Hinweis'));
 run("action('upload','1')");assert.equal(run('ADMISSIONS.reviewed'),false);assert.equal(run('ADMISSIONS.quality[1]'),'pending');
 run("state.lang='de'");assert(!run('reviewLog()').includes('School certificate'));
});
console.log(JSON.stringify({status:'PASS',checks:tested,scope:'Local simulation only; production source tests not executed'},null,2));
