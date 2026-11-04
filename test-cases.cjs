const vm=require('vm'),fs=require('fs'),assert=require('assert');const elements={};const listeners={};function el(id){return elements[id]??={innerHTML:'',textContent:'',value:'',checked:false,dataset:{},classList:{add(){},remove(){},toggle(){},contains(){return false}},addEventListener(type,fn){(listeners[id]??={})[type]=fn},focus(){},scrollIntoView(){},querySelectorAll(){return []},querySelector(){return null},scrollTop:0,scrollHeight:0}}const sandbox={console,location:{hash:'#/'},document:{documentElement:{lang:'de'},body:el('body'),getElementById:el,querySelectorAll(){return []},querySelector(s){return s==='body>.skip'?el('skip'):null},addEventListener(){}},window:{addEventListener(){},scrollTo(){}},setTimeout(){},clearTimeout(){}};vm.createContext(sandbox);for(const f of ['app.js','coverage-data.js','v2.js','migration-data.js','v3.js','content-data.js','v3-content.js','edition-data.js','media-data.js','v3-migration.js','admissions.js','learning-journey.js','attendance-journey.js','case-journey.js','appointment-journey.js','rental-journey.js','library-journey.js','arrival-journey.js','knowledge-journey.js'])vm.runInContext(fs.readFileSync(__dirname+'/dist/'+f,'utf8'),sandbox,{filename:f});const run=s=>vm.runInContext(s,sandbox);const go=r=>{sandbox.location.hash='#'+r;run('render()');return el('app').innerHTML};const tested=[];function check(name,fn){fn();tested.push(name)}
assert(go("/staff/cases").includes("case-journey"), "Missing connected case workspace");
check('Blank and duplicate enquiries rejected; unclear routing never guessed',()=>{
 go('/portal/support');run("caseAction('create')");assert.equal(run('CASES.records.length'),0);
 run("CASES.draft={subject:'Musteranliegen',body:'Fiktive Frage zum Ablauf',category:'unclear'};caseAction('create')");assert.equal(run('caseRecord().owner'),'triage');assert.equal(run('caseRecord().status'),'new');
 run("CASES.draft={subject:'Musteranliegen',body:'Fiktive Frage zum Ablauf',category:'unclear'};caseAction('create')");assert.equal(run('CASES.records.length'),1);
});
check('Unassigned case held for triage; staff views and mutations scoped to assigned owner',()=>{
 go('/staff/cases');assert(!el('app').innerHTML.includes('Fiktive Frage zum Ablauf'));run("caseAction('start')");assert.equal(run('caseRecord().status'),'new');
 run("CASES.owner='triage';caseRecord().staffReply='Must not release';caseAction('respond')");assert.equal(run('caseRecord().messages.length'),1);
 run("caseRecord().transfer='adminA';caseAction('transfer')");assert.equal(run('caseRecord().owner'),'triage');
 run("caseRecord().note='Fiktiv: administrative Zuordnung geprüft';caseAction('transfer')");assert.equal(run('caseRecord().owner'),'adminA');assert(!el('app').innerHTML.includes('Fiktive Frage zum Ablauf'));
 run("CASES.owner='adminA';caseRecord().staffReply='UNRELEASED STAFF DRAFT';caseRecord().note='INTERNAL REVIEW'");assert(!go('/portal/messages').includes('UNRELEASED STAFF DRAFT'));assert(!el('app').innerHTML.includes('INTERNAL REVIEW'));
});
check('Question and participant response share a case without mail or duplicate publication',()=>{
 go('/staff/cases');run("caseRecord().staffReply='Fiktive Rückfrage: Welcher Ablauf?';caseAction('question');caseAction('question')");assert.equal(run('caseRecord().status'),'question');assert.equal(run('caseRecord().messages.length'),2);
 assert(go('/portal/messages').includes('Fiktive Rückfrage'));run("caseRecord().reply='<img src=x onerror=alert(1)> Musterantwort';caseAction('reply')");assert.equal(run('caseRecord().status'),'working');assert.equal(run('caseRecord().messages.length'),3);
 const h=go('/staff/inbox');assert(h.includes('&lt;img'));assert(!h.includes('<img src=x'));assert(!go('/portal/teacher').includes('Fiktive Rückfrage'));
});
check('Verified task dates required; case cannot close with open tasks',()=>{
 go('/staff/cases');run("caseRecord().taskDraft={title:'INTERNAL TASK QA',owner:'adminA',priority:'normal',due:'2026-02-30',follow:'2026-11-03',verified:true};caseAction('task-create')");assert.equal(run('caseRecord().tasks.length'),0);
 run("caseRecord().taskDraft.due='2026-11-06';caseRecord().taskDraft.verified=false;caseAction('task-create')");assert.equal(run('caseRecord().tasks.length'),0);
 run("caseRecord().taskDraft.verified=true;caseAction('task-create')");assert.equal(run('caseRecord().tasks.length'),1);
 run("caseRecord().staffReply='Fiktiv abgeschlossen';caseAction('close')");assert.notEqual(run('caseRecord().status'),'closed');assert(!go('/portal/messages').includes('INTERNAL TASK QA'));
 const calendar=go('/staff/calendar');assert(calendar.includes('2026-11-06'));assert(calendar.includes('2026-11-03'));assert(calendar.includes('INTERNAL TASK QA'));
});
check('Task changes update same calendar values and preserve before/after history',()=>{
 go('/staff/tasks');run("Object.assign(caseTaskDraft(caseTask().task),{due:'2026-11-09',reason:'Fiktiv neu abgestimmt',verified:true});caseAction('task-save')");assert.equal(run('caseTask().task.history.length'),2);
 const calendar=go('/staff/calendar');assert(calendar.includes('2026-11-09'));assert(!calendar.includes('2026-11-06'));
 go('/staff/tasks');run("Object.assign(caseTaskDraft(caseTask().task),{owner:'adminB',reason:'Fiktive Übergabe',verified:true});caseAction('task-save')");assert.equal(run('caseTask().task.owner'),'adminB');assert(!el('app').innerHTML.includes('INTERNAL TASK QA'));
 const snap=run('JSON.stringify(caseTask().task)');run("caseAction('task-save')");assert.equal(run('JSON.stringify(caseTask().task)'),snap);assert(!go('/staff/calendar').includes('INTERNAL TASK QA'));
 run("CASES.owner='adminB'");assert(go('/staff/tasks').includes('INTERNAL TASK QA'));assert(!go('/staff/cases').includes('Fiktive Frage zum Ablauf'));
});
check('Completion returns to case owner; final learner response closes case without changing decisions',()=>{
 go('/staff/tasks');run("Object.assign(caseTaskDraft(caseTask().task),{status:'done',reason:'Musteraufgabe erledigt',verified:true});caseAction('task-save')");assert(!go('/staff/calendar').includes('INTERNAL TASK QA'));
 run("CASES.owner='adminA'");go('/staff/cases');run("caseRecord().staffReply='Fiktive Abschlussrückmeldung';caseAction('close')");assert.equal(run('caseRecord().status'),'closed');assert(go('/portal/messages').includes('Fiktive Abschlussrückmeldung'));
 const n=run('caseRecord().messages.length');run("caseRecord().reply='No reopen';caseAction('reply')");assert.equal(run('caseRecord().messages.length'),n);
});
check('Multiple cases isolate drafts; all six routes translate; unknown IDs cannot mutate',()=>{
 go('/portal/support');run("CASES.draft={subject:'Zweites Muster',body:'Fiktive Fachfrage',category:'teaching'};caseAction('create')");assert.equal(run('caseRecord().owner'),'teacher');assert(!go('/portal/messages').includes('Fiktive Abschlussrückmeldung'));
 run("caseRecord().reply='SECOND-DRAFT';CASES.selected='DEMO-CASE-001'");assert(!go('/portal/messages').includes('SECOND-DRAFT'));
 run("state.lang='en';CASES.owner='teacher'");for(const r of ['/portal/support','/portal/messages','/staff/inbox','/staff/cases','/staff/tasks','/staff/calendar'])assert(go(r).includes('Local simulation'));
 const before=run('JSON.stringify(CASES.records)');run("CASES.selected='UNKNOWN';CASES.taskSelected='UNKNOWN';caseAction('reply');caseAction('close');caseAction('task-save')");assert.equal(run('JSON.stringify(CASES.records)'),before);
});
console.log(JSON.stringify({status:'PASS',checks:tested,scope:'Six shared local frontend views, no production identity, channels, dates or permissions'},null,2));
