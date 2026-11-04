const vm=require('vm'),fs=require('fs'),assert=require('assert');const elements={};const listeners={};function el(id){return elements[id]??={innerHTML:'',textContent:'',value:'',checked:false,dataset:{},classList:{add(){},remove(){},toggle(){},contains(){return false}},addEventListener(type,fn){(listeners[id]??={})[type]=fn},focus(){},scrollIntoView(){},querySelectorAll(){return []},querySelector(){return null},scrollTop:0,scrollHeight:0}}const sandbox={console,location:{hash:'#/'},document:{documentElement:{lang:'de'},body:el('body'),getElementById:el,querySelectorAll(){return []},querySelector(s){return s==='body>.skip'?el('skip'):null},addEventListener(){}},window:{addEventListener(){},scrollTo(){}},setTimeout(){},clearTimeout(){}};vm.createContext(sandbox);for(const f of ['app.js','coverage-data.js','v2.js','migration-data.js','v3.js','content-data.js','v3-content.js','edition-data.js','media-data.js','v3-migration.js','admissions.js','learning-journey.js','attendance-journey.js','case-journey.js','appointment-journey.js','rental-journey.js','library-journey.js','arrival-journey.js','knowledge-journey.js'])vm.runInContext(fs.readFileSync(__dirname+'/dist/'+f,'utf8'),sandbox,{filename:f});const run=s=>vm.runInContext(s,sandbox);const go=r=>{sandbox.location.hash='#'+r;run('render()');return el('app').innerHTML};const tested=[];function check(name,fn){fn();tested.push(name)}

check('Teacher homework is a usable task editor rather than a specification reader',()=>{assert(go('/portal/teacher/homework').includes('id="learning-title"'));});
check('Draft stays hidden, assignment validation and stable DE/EN defaults',()=>{
 assert(go('/portal/student/tasks').includes('Noch keine lokale Aufgabe'));
 go('/portal/teacher/homework');run("LEARNING.draft.title='';learningAction('assign')");assert.equal(run('LEARNING.task'),null);
 run("LEARNING.draft.title=null;LEARNING.draft.due='invalid';learningAction('assign')");assert.equal(run('LEARNING.task'),null);
 run("LEARNING.draft.due='2026-11-03T18:00';learningAction('assign')");assert.equal(run('LEARNING.task.id'),'DEMO-HW-01');
 run("state.lang='en'");assert(go('/portal/student/tasks').includes('Linear functions'));assert(go('/portal/learning/course/UNKNOWN').includes('Learning space not found'));
});
check('Empty response blocked; late response has no penalty; draft feedback hidden',()=>{
 go('/portal/student/tasks');run("learningAction('submit')");assert.equal(run('LEARNING.submission'),null);
 run("LEARNING.answer='<img src=x onerror=alert(1)> Test solution';LEARNING.timing='late';learningAction('submit')");
 assert.equal(run('LEARNING.submission.version'),1);assert(go('/portal/student/tasks').includes('no automatic grade penalty'));
 const teacher=go('/portal/teacher/homework');assert(teacher.includes('&lt;img'));assert(!teacher.includes('<img src=x'));assert(teacher.includes('No missing-submission reminder'));
 run("LEARNING.feedbackDraft='PRIVATE-DRAFT-QA'");assert(!go('/portal/student/tasks').includes('PRIVATE-DRAFT-QA'));
 run("learningAction('feedback')");assert.equal(run('LEARNING.feedback'),null);
 go('/portal/teacher/homework');run("LEARNING.feedbackDraft='';learningAction('feedback')");assert.equal(run('LEARNING.feedback'),null);
 run("LEARNING.feedbackDraft='Reviewed sample feedback';learningAction('feedback')");assert(go('/portal/student/tasks').includes('Reviewed sample feedback'));
});
check('Revision invalidates current feedback but preserves released history; duplicate actions safe',()=>{
 go('/portal/student/tasks');run("learningAction('submit')");assert.equal(run('LEARNING.submission.version'),1);
 run("LEARNING.answer='Revised solution';LEARNING.timing='on-time';learningAction('submit')");assert.equal(run('LEARNING.submission.version'),2);assert.equal(run('LEARNING.feedback'),null);assert.equal(run('LEARNING.feedbackDraft'),'');
 assert.equal(run('LEARNING.versions[0].feedback[0]'),'Reviewed sample feedback');assert(go('/portal/student/tasks').includes('awaiting teacher review'));
 go('/portal/teacher/homework');run("LEARNING.feedbackDraft='Second response';learningAction('feedback');learningAction('feedback')");assert.equal(run('LEARNING.versions[1].feedback.length'),1);
 run("state.lang='de'");assert(go('/portal/student/tasks').includes('Rückmeldung lokal freigegeben'));
 for(const r of ['/portal/applicant','/portal/partner'])assert(!go(r).includes('Revised solution'));
});
check('Role-route gates and draft continuity through language and navigation',()=>{
 go('/portal/student/tasks');run("LEARNING.answer='Unsubmitted revised draft'");go('/portal/teacher/homework');run("state.lang='en'");assert(!go('/portal/teacher/homework').includes('Unsubmitted revised draft'));assert(go('/portal/student/tasks').includes('Unsubmitted revised draft'));
 const count=run('LEARNING.versions.length');go('/portal/teacher/homework');run("learningAction('submit')");assert.equal(run('LEARNING.versions.length'),count);
});
console.log(JSON.stringify({status:'PASS',checks:tested,scope:'Local fictional task journey; no production LMS, permissions or grades'},null,2));
