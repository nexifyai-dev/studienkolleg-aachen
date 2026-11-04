const vm=require('vm'),fs=require('fs'),assert=require('assert');const elements={};const listeners={};function el(id){return elements[id]??={innerHTML:'',textContent:'',value:'',checked:false,dataset:{},classList:{add(){},remove(){},toggle(){},contains(){return false}},addEventListener(type,fn){(listeners[id]??={})[type]=fn},focus(){},scrollIntoView(){},querySelectorAll(){return []},querySelector(){return null},scrollTop:0,scrollHeight:0}}const sandbox={console,location:{hash:'#/'},document:{documentElement:{lang:'de'},body:el('body'),getElementById:el,querySelectorAll(){return []},querySelector(s){return s==='body>.skip'?el('skip'):null},addEventListener(){}},window:{addEventListener(){},scrollTo(){}},setTimeout(){},clearTimeout(){}};vm.createContext(sandbox);for(const f of ['app.js','coverage-data.js','v2.js','migration-data.js','v3.js','content-data.js','v3-content.js','edition-data.js','media-data.js','v3-migration.js','admissions.js','learning-journey.js','attendance-journey.js','case-journey.js','appointment-journey.js','rental-journey.js','library-journey.js','arrival-journey.js','knowledge-journey.js'])vm.runInContext(fs.readFileSync(__dirname+'/dist/'+f,'utf8'),sandbox,{filename:f});const run=s=>vm.runInContext(s,sandbox);const go=r=>{sandbox.location.hash='#'+r;run('render()');return el('app').innerHTML};const tested=[];function check(name,fn){fn();tested.push(name)}

check('Teacher can review participant correction reports, not just three-value attendance selectors',()=>{assert(go('/portal/teacher/attendance').includes('attendance-journey'));});
check('Participant report never changes attendance; blank and duplicate reports blocked',()=>{
 go('/portal/student/attendance');run("attendanceAction('report')");assert.equal(run('attendanceRecord().request'),null);
 run("attendanceRecord().reportDraft='Fiktiv: Online teilgenommen';attendanceAction('report');attendanceAction('report')");assert.equal(run('attendanceRecord().status'),'unexcused');assert.equal(run('attendanceRecord().history.length'),1);
 run("attendanceRecord().checked=true;attendanceRecord().reviewDraft='Unauthorized';attendanceRecord().proposed='presence';attendanceAction('correct')");assert.equal(run('attendanceRecord().status'),'unexcused');
});
check('Teacher correction requires reason and verification and retains before/after, actor and time',()=>{
 go('/portal/teacher/attendance');run("attendanceRecord().reviewDraft='';attendanceAction('correct')");assert.equal(run('attendanceRecord().status'),'unexcused');
 run("attendanceRecord().reviewDraft='Fiktiv: Unterricht geprüft';attendanceRecord().checked=false;attendanceAction('correct')");assert.equal(run('attendanceRecord().status'),'unexcused');
 run("attendanceRecord().checked=true;attendanceRecord().proposed='online';attendanceAction('correct')");assert.equal(run('attendanceRecord().status'),'online');assert.equal(run('attendanceRecord().history[1].from'),'unexcused');assert.equal(run('attendanceRecord().history[1].to'),'online');assert(run('attendanceRecord().history[1].at').includes('T'));
 assert(go('/portal/student/attendance').includes('Musterkorrektur dokumentiert'));assert(go('/portal/teacher/classbook').includes('Fiktiv: Unterricht geprüft'));
});
check('Excused still counts as absence; unchanged and clarification do not modify state',()=>{
 go('/portal/student/attendance');run("attendanceRecord().reportDraft='Weitere fiktive Klärung';attendanceAction('report')");go('/portal/teacher/attendance');run("attendanceRecord().reviewDraft='Gruppenzuordnung klären';attendanceAction('clarify')");assert.equal(run('attendanceRecord().status'),'online');assert.equal(run('attendanceRecord().request.status'),'clarify');
 run("attendanceRecord().checked=true;attendanceRecord().reviewDraft='Fiktive Prüfung beendet';attendanceAction('keep')");assert.equal(run('attendanceRecord().status'),'online');assert.equal(run('attendanceRecord().request.status'),'unchanged');
 go('/portal/student/attendance');run("attendanceRecord().reportDraft='Weiterer Musterfall';attendanceAction('report')");go('/portal/teacher/attendance');run("attendanceRecord().reviewDraft='Fiktive Kennzeichnung';attendanceRecord().checked=true;attendanceRecord().proposed='excused';attendanceAction('correct')");assert.equal(run('attendanceCounts().absent'),1);assert.equal(run('attendanceCounts().excused'),1);
});
check('Actual subject class, per-record drafts, language, escaping and no cross-role leakage',()=>{
 run("ATTENDANCE.selected='UNIT-02';state.lang='en'");assert(go('/portal/student/attendance').includes('D-B1-02'));assert(go('/portal/student/attendance').includes('Present online'));
 run("attendanceRecord().reportDraft='<img src=x onerror=alert(1)>';attendanceAction('report')");const h=go('/portal/teacher/attendance');assert(h.includes('&lt;img'));assert(!h.includes('<img src=x'));
 run("attendanceRecord().reviewDraft='UNRELEASED-QA'");assert(!go('/portal/student/attendance').includes('UNRELEASED-QA'));
 run("ATTENDANCE.selected='UNIT-01'");assert(!go('/portal/teacher/attendance').includes('UNRELEASED-QA'));for(const r of ['/portal/applicant','/portal/partner'])assert(!go(r).includes('Fiktive Kennzeichnung'));
});
check('Unknown identifiers cannot mutate a record; only allowed status values are accepted',()=>{
 const before=run('JSON.stringify(ATTENDANCE.records)');run("ATTENDANCE.selected='UNKNOWN'");go('/portal/teacher/attendance');run("attendanceAction('correct')");assert.equal(run('JSON.stringify(ATTENDANCE.records)'),before);
 run("ATTENDANCE.selected='UNIT-02';attendanceRecord().checked=true;attendanceRecord().proposed='INVALID';attendanceAction('correct')");assert.equal(run('attendanceRecord().status'),'online');
});
console.log(JSON.stringify({status:'PASS',checks:tested,scope:'Fictional local attendance correction, no real authorization or attendance'},null,2));
