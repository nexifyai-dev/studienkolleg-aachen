const vm=require('vm'),fs=require('fs'),assert=require('assert');const elements={};const listeners={};function el(id){return elements[id]??={innerHTML:'',textContent:'',value:'',checked:false,dataset:{},classList:{add(){},remove(){},toggle(){},contains(){return false}},addEventListener(type,fn){(listeners[id]??={})[type]=fn},focus(){},scrollIntoView(){},querySelectorAll(){return []},querySelector(){return null},scrollTop:0,scrollHeight:0}}const sandbox={console,location:{hash:'#/'},document:{documentElement:{lang:'de'},body:el('body'),getElementById:el,querySelectorAll(){return []},querySelector(s){return s==='body>.skip'?el('skip'):null},addEventListener(){}},window:{addEventListener(){},scrollTo(){}},setTimeout(){},clearTimeout(){}};vm.createContext(sandbox);for(const f of ['app.js','coverage-data.js','v2.js','migration-data.js','v3.js','content-data.js','v3-content.js','edition-data.js','media-data.js','v3-migration.js','admissions.js','learning-journey.js','attendance-journey.js','case-journey.js','appointment-journey.js','rental-journey.js','library-journey.js','arrival-journey.js','knowledge-journey.js'])vm.runInContext(fs.readFileSync(__dirname+'/dist/'+f,'utf8'),sandbox,{filename:f});const run=s=>vm.runInContext(s,sandbox);const go=r=>{sandbox.location.hash='#'+r;run('render()');return el('app').innerHTML};const tested=[];function check(name,fn){fn();tested.push(name)}
assert(go("/portal/appointments").includes("meeting-journey"), "Missing connected appointment journey");
check('Unreleased slots are absent; place, time, verification and overlap gates enforced',()=>{
 assert(!go('/portal/appointments').includes('data-meeting-pick'));
 go('/staff/calendar');run("meetingAction('publish')");assert.equal(run('meetingSlot().published'),false);
 run("Object.assign(meetingSlot(),{place:'Fiktiver Raum A',checked:true,end:'09:30'});meetingAction('publish')");assert.equal(run('meetingSlot().published'),false);
 run("meetingSlot().end='10:30';meetingAction('publish')");assert.equal(run('meetingSlot().published'),true);
 run("MEETINGS.slotSelected='SLOT-02';Object.assign(meetingSlot(),{date:'2026-11-10',start:'10:15',end:'10:45',place:'Fiktiver Raum B',checked:true});meetingAction('publish')");assert.equal(run('meetingSlot().published'),false);
 run("meetingSlot().date='2026-11-11';meetingAction('publish')");assert.equal(run('meetingSlot().published'),true);
});
check('Video missing connection and wrong owner cannot release a slot',()=>{
 run("MEETINGS.slotSelected='SLOT-03';Object.assign(meetingSlot(),{place:'fake zoom',checked:true});meetingAction('publish')");assert.equal(run('meetingSlot().published'),false);
 run("CASES.owner='adminB';meetingAction('publish')");assert.equal(run('meetingSlot().published'),false);assert(go('/portal/appointments').includes('Kein Zoom-/BBB-Link')||el('app').innerHTML.includes('kein Zoom-/BBB-Link'));
 run("CASES.owner='adminA';MEETINGS.slotSelected='SLOT-01'");
});
check('Booking uses released snapshot; occupied slots and unreviewed change requests blocked',()=>{
 go('/portal/appointments');run("meetingAction('pick','SLOT-01')");assert.equal(run('meetingBooking().slot.place'),'Fiktiver Raum A');assert.equal(run('MEETINGS.bookings.length'),1);
 run("meetingAction('pick','SLOT-01');meetingAction('pick','SLOT-02');meetingAction('cancel')");assert.equal(run('meetingBooking().status'),'booked');assert.equal(run('meetingBooking().slot.id'),'SLOT-01');
 go('/staff/calendar');run("meetingAction('withdraw')");assert.equal(run('meetingSlot().published'),true);
 run("meetingAction('allow-changes')");assert.equal(run('meetingBooking().changesAllowed'),false);
 run("meetingBooking().changeReason='Fiktive Regeln im Einzelfall geprüft';meetingBooking().changeChecked=true;meetingAction('allow-changes')");assert.equal(run('meetingBooking().changesAllowed'),true);
});
check('Reschedule releases old slot, preserves one active record and resets change review',()=>{
 go('/portal/appointments');run("meetingAction('pick','SLOT-02')");assert.equal(run('MEETINGS.bookings.length'),1);assert.equal(run('meetingBooking().slot.id'),'SLOT-02');assert.equal(run('MEETINGS.slots[0].booking'),null);assert.equal(run('meetingBooking().changesAllowed'),false);
 go('/staff/calendar');run("meetingBooking().changeReason='Fiktive Stornierung geprüft';meetingBooking().changeChecked=true;meetingAction('allow-changes')");go('/portal/appointments');run("meetingAction('cancel')");assert.equal(run('meetingBooking().status'),'cancelled');assert.equal(run('MEETINGS.slots[1].booking'),null);
 run("meetingAction('pick','SLOT-01')");assert.equal(run('MEETINGS.bookings.length'),2);assert.equal(run('MEETINGS.bookings.filter(b=>b.status===\"booked\").length'),1);
});
check('Unreviewed or unheld conversation cannot become documentation; private notes stay private',()=>{
 go('/staff/calendar');run("Object.assign(meetingBooking(),{summary:'Draft QA',note:'PRIVATE-NOTE-QA',docChecked:true});meetingAction('document')");assert.equal(run('meetingBooking().docs.length'),0);
 run("meetingBooking().occurred=true;meetingAction('document')");assert.equal(run('meetingBooking().docs.length'),1);assert.equal(run('meetingBooking().status'),'completed');
 const learner=go('/portal/appointments');assert(!learner.includes('Draft QA'));assert(!learner.includes('PRIVATE-NOTE-QA'));
 go('/staff/calendar');run("meetingAction('release-summary')");assert.equal(run('meetingBooking().released.length'),0);
 run("meetingBooking().portalChecked=true;meetingBooking().summary='Changed since review';meetingAction('release-summary')");assert.equal(run('meetingBooking().released.length'),0);
});
check('Reviewed revisions and explicit portal release preserve earlier versions and escape input',()=>{
 run("Object.assign(meetingBooking(),{summary:'<img src=x onerror=alert(1)> reviewed sample',note:'PRIVATE-NOTE-QA',docChecked:true});meetingAction('document');meetingBooking().portalChecked=true;meetingAction('release-summary');meetingAction('release-summary')");assert.equal(run('meetingBooking().released.length'),1);
 const learner=go('/portal/appointments');assert(learner.includes('&lt;img'));assert(!learner.includes('<img src=x'));assert(!learner.includes('PRIVATE-NOTE-QA'));
 go('/staff/calendar');run("meetingBooking().summary='UNRELEASED-REVISION';meetingBooking().docChecked=true;meetingAction('document')");assert(!go('/portal/appointments').includes('UNRELEASED-REVISION'));
 go('/staff/calendar');run("meetingBooking().portalChecked=true;meetingAction('release-summary')");assert.equal(run('meetingBooking().released.length'),2);assert.equal(run('meetingBooking().released[0].version'),2);
});
check('Follow-up bridges once into existing cases/tasks with only released summary',()=>{
 run("meetingAction('followup')");assert.equal(run('CASES.records.length'),1);assert.equal(run('caseRecord().messages[0].text'),'UNRELEASED-REVISION');assert(!run('JSON.stringify(caseRecord())').includes('PRIVATE-NOTE-QA'));
 const id=run('meetingBooking().caseId');go('/staff/calendar');run("meetingAction('followup')");assert.equal(run('CASES.records.length'),1);assert.equal(run('CASES.selected'),id);
 go('/staff/cases');run("caseRecord().taskDraft={title:'Fiktive Beratungsfolge',owner:'adminA',priority:'normal',due:'2026-11-15',follow:'2026-11-13',verified:true};caseAction('task-create')");assert(go('/staff/calendar').includes('Fiktive Beratungsfolge'));assert(go('/staff/tasks').includes('Fiktive Beratungsfolge'));
});
check('Wrong role, missing IDs and learner actions cannot leak or mutate staff documentation',()=>{
 run("CASES.owner='adminB'");const html=go('/staff/calendar');assert(!html.includes('PRIVATE-NOTE-QA'));assert(!html.includes('UNRELEASED-REVISION'));
 const snap=run('JSON.stringify(MEETINGS.bookings)');run("meetingAction('document');meetingAction('release-summary');meetingAction('followup')");assert.equal(run('JSON.stringify(MEETINGS.bookings)'),snap);
 go('/portal/appointments');run("meetingAction('document');meetingAction('release-summary')");assert.equal(run('JSON.stringify(MEETINGS.bookings)'),snap);
 run("MEETINGS.bookingSelected='UNKNOWN';MEETINGS.slotSelected='UNKNOWN';meetingAction('cancel');meetingAction('pick','UNKNOWN')");assert.equal(run('JSON.stringify(MEETINGS.bookings)'),snap);
 run("state.lang='en'");for(const r of ['/portal/appointments','/portal/student/appointments','/portal/applicant/appointments'])assert(go(r).includes('Local appointment scenario'));
});
console.log(JSON.stringify({status:'PASS',checks:tested,scope:'Local appointment and documentation scenarios, no booking authority, CRM or calendar integration'},null,2));
