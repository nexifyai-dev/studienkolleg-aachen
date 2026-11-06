const vm=require('vm'),fs=require('fs'),assert=require('assert');const elements={};const listeners={};function el(id){return elements[id]??={innerHTML:'',textContent:'',value:'',checked:false,dataset:{},classList:{add(){},remove(){},toggle(){},contains(){return false}},addEventListener(type,fn){(listeners[id]??={})[type]=fn},focus(){},scrollIntoView(){},querySelectorAll(){return []},querySelector(){return null},scrollTop:0,scrollHeight:0}}const sandbox={console,location:{hash:'#/'},document:{documentElement:{lang:'de'},body:el('body'),getElementById:el,querySelectorAll(){return []},querySelector(s){return s==='body>.skip'?el('skip'):null},addEventListener(){}},window:{addEventListener(){},scrollTo(){}},setTimeout(){},clearTimeout(){}};vm.createContext(sandbox);for(const f of ['app.js','coverage-data.js','v2.js','migration-data.js','v3.js','content-data.js','v3-content.js','edition-data.js','media-data.js','v3-migration.js','admissions.js','learning-journey.js','attendance-journey.js','case-journey.js','appointment-journey.js','rental-journey.js','library-journey.js','arrival-journey.js','knowledge-journey.js'])vm.runInContext(fs.readFileSync(__dirname+'/dist/'+f,'utf8'),sandbox,{filename:f});const run=s=>vm.runInContext(s,sandbox);const go=r=>{sandbox.location.hash='#'+r;run('render()');return el('app').innerHTML};const tested=[];function check(name,fn){fn();tested.push(name)}

check('Application choices retain stable values with translated labels',()=>{
 run("state.lang='en';state.step=0;state.submitted=false;state.application.language='Noch offen';state.application.start='Späterer Einstieg'");
 const h=go('/apply');
 assert(h.includes('value="Noch offen" selected>Not set</option>'));
 assert(h.includes('value="Späterer Einstieg" selected>Later intake</option>'));
 assert(h.includes('>Next available intake</option>'));
});
check('Review and applicant portal preserve all draft selections without granting admission',()=>{
 run("state.application.educationCountry='Fictional-Country-QA';state.application.passport=true;state.uploads={0:true,1:true,2:true};state.step=3");
 for(const route of ['/apply','/portal/applicant']){
  const h=go(route); assert(h.includes('Fictional-Country-QA'));assert(h.includes('Later intake'));assert(h.includes('Passport'));assert(h.includes('Sample added · review pending'));assert(h.includes('Not set'));
 }
 assert.equal(run('state.submitted'),false);
 run("action('complete')");assert(go('/apply').includes('Nothing was submitted'));
 assert(go('/portal/applicant').includes('no admission decision'));
 run("action('edit-application')");assert.equal(run('state.application.educationCountry'),'Fictional-Country-QA');assert.equal(run('state.application.passport'),true);
});
check('Unset and adversarial sample values remain honest and escaped',()=>{
 run("state.application.educationCountry='';state.application.passport=false;state.step=3");
 for(const r of ['/apply','/portal/applicant']){const h=go(r);assert(h.includes('No sample added'));assert(h.includes('Not set'));}
 run(`state.application.educationCountry='<img src=x onerror=alert(1)>';state.application.language='<b>sample</b>'`);
 for(const r of ['/apply','/portal/applicant']){const h=go(r);assert(!h.includes('<img src=x'));assert(h.includes('&lt;img'));assert(!h.includes('<b>sample</b>'));}
});
check('German summary and staff contexts stay separate',()=>{
 run("state.lang='de';state.application.language='Noch offen';state.application.educationCountry='Fictional-Country-QA';state.application.passport=true;state.step=3");
 for(const r of ['/apply','/portal/applicant']){const h=go(r);assert(h.includes('Späterer Einstieg'));assert(h.includes('Muster ergänzt · Prüfung offen'));assert(h.includes('Fictional-Country-QA'));}
 for(const r of ['/portal/teacher','/portal/admin'])assert(!go(r).includes('Fictional-Country-QA'));
});

check('Applicant tasks and messages agree with all document masks in DE/EN',()=>{
 for(const lang of ['de','en'])for(let mask=0;mask<8;mask++){
  run(`state.lang='${lang}';state.uploads=${JSON.stringify(Object.fromEntries([0,1,2].filter(i=>mask&(1<<i)).map(i=>[i,true])))}`);
  const tasks=go('/portal/applicant/tasks'),messages=go('/portal/applicant/messages');
  const names=JSON.parse(run('JSON.stringify(docNames())'));
  for(let i=0;i<3;i++)assert.equal(tasks.includes(`data-action="upload" data-value="${i}"`),!(mask&(1<<i)));
  assert(messages.includes(lang==='de'?'Aktueller Musterstatus':'Current sample status'));
  assert(!messages.includes('Please add the sample transcript.'));assert(!messages.includes('Bitte ergänze die Muster-Notenübersicht.'));
  for(let i=0;i<3;i++){run(`action('upload','${i}')`);run(`action('upload','${i}')`);}
  assert.equal(run('Object.keys(state.uploads).length'),3);
 }
});

check('Booking review and confirmation translate all stable topic values',()=>{
 const topics=[['Erstberatung','Initial guidance'],['Kursberatung','Course guidance'],['Prüfungsberatung','Exam guidance'],['Bewerbungsgespräch','Application conversation']];
 for(const [de,en] of topics)for(const lang of ['de','en'])for(const confirmed of [false,true]){
  run(`state.lang='${lang}';V3_BOOKING.type=${JSON.stringify(de)};V3_BOOKING.step=2;V3_BOOKING.confirmed=${confirmed};V3_BOOKING.name='Sample Person';V3_BOOKING.date='2026-11-03';V3_BOOKING.time='10:00'`);
  const h=go('/beratung');assert(h.includes(lang==='de'?de:en));assert.equal(run('V3_BOOKING.type'),de);assert.equal(run('V3_BOOKING.confirmed'),confirmed);
 }
});
console.log(JSON.stringify({status:'PASS',checks:tested,scope:'Local VM assertions; no backend/auth/real upload or production acceptance'},null,2));
