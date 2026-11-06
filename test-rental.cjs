const vm=require('vm'),fs=require('fs'),assert=require('assert');const elements={};const listeners={};function el(id){return elements[id]??={innerHTML:'',textContent:'',value:'',checked:false,dataset:{},classList:{add(){},remove(){},toggle(){},contains(){return false}},addEventListener(type,fn){(listeners[id]??={})[type]=fn},focus(){},scrollIntoView(){},querySelectorAll(){return []},querySelector(){return null},scrollTop:0,scrollHeight:0}}const sandbox={console,location:{hash:'#/'},document:{documentElement:{lang:'de'},body:el('body'),getElementById:el,querySelectorAll(){return []},querySelector(s){return s==='body>.skip'?el('skip'):null},addEventListener(){}},window:{addEventListener(){},scrollTo(){}},setTimeout(){},clearTimeout(){}};vm.createContext(sandbox);for(const f of ['app.js','coverage-data.js','v2.js','migration-data.js','v3.js','content-data.js','v3-content.js','edition-data.js','media-data.js','v3-migration.js','admissions.js','learning-journey.js','attendance-journey.js','case-journey.js','appointment-journey.js','rental-journey.js','library-journey.js','arrival-journey.js','knowledge-journey.js'])vm.runInContext(fs.readFileSync(__dirname+'/dist/'+f,'utf8'),sandbox,{filename:f});const run=s=>vm.runInContext(s,sandbox);const go=r=>{sandbox.location.hash='#'+r;run('render()');return el('app').innerHTML};const tested=[];function check(name,fn){fn();tested.push(name)}
assert(go("/portal/tenant/issues").includes("rental-journey"), "Missing connected tenancy issue journey");
check('Protocol requires complete data and verification; exact tenant confirmation and version retention',()=>{
 go('/staff/housing');run("rentalAction('save-in')");assert.equal(run('RENTAL.incoming.length'),0);
 run("Object.assign(RENTAL.inDraft,{room:'Fiktiver Tischkratzer',common:'Fiktive Lampe ohne Mangel',inventory:'Tisch und Lampe',cleanliness:'Fiktiv sauber',roomDefect:true,roomKeys:'2',houseKeys:'1',photo:true,checked:true});rentalAction('save-in')");assert.equal(run('RENTAL.incoming.length'),1);assert.equal(run('rentalBaseline()'),null);
 go('/portal/tenant/handover');run("rentalAction('confirm-in');rentalAction('confirm-in')");assert.equal(run('rentalBaseline().version'),1);assert.equal(run('rentalLatest().history.length'),2);
 go('/staff/housing');run("RENTAL.inDraft.room='Fiktiver Tischkratzer genauer';RENTAL.inDraft.checked=true;rentalAction('save-in')");assert.equal(run('rentalBaseline()'),null);assert.equal(run('RENTAL.incoming[0].tenantConfirmed'),true);
 go('/portal/tenant/handover');run("rentalAction('confirm-in')");assert.equal(run('rentalBaseline().version'),2);
});
check('Common-area report has no perpetrator or forced tenancy; no owner means no fake forwarding',()=>{
 go('/portal/tenant/issues');run("rentalAction('create-issue')");assert.equal(run('RENTAL.issues.length'),0);
 run("Object.assign(RENTAL.issueDraft,{item:'common',description:'Fiktiv: Lampe flackert',suggested:'urgent',missingOwner:true});rentalAction('create-issue')");assert.equal(run('rentalIssue().room'),null);assert.equal(run('rentalIssue().tenancy'),null);assert.equal(run('rentalIssue().owner'),null);assert.equal(run('rentalIssue().decision'),null);
 go('/staff/housing/maintenance');run("rentalIssue().response='Must not complete';rentalIssue().measures='No';rentalAction('finish')");assert.equal(run('rentalIssue().status'),'received');run("rentalAction('claim')");assert.equal(run('rentalIssue().owner'),'housing');
});
check('Existing-damage claim needs confirmed item evidence; priority reviewed instead of copied',()=>{
 run("Object.assign(rentalIssue(),{priority:'urgent',classification:'existing',review:'Fiktiv geprüft',checked:true});rentalAction('review-issue')");assert.equal(run('rentalIssue().decision'),null);
 run("rentalIssue().classification='changed';rentalAction('review-issue')");assert.equal(run('rentalIssue().decision.priority'),'urgent');assert.equal(run('rentalIssue().status'),'working');
 run("rentalIssue().response='Fiktive Rückfrage zur Lampe';rentalAction('question')");assert.equal(run('rentalIssue().reviewed'),false);
 go('/portal/tenant/issues');assert(el('app').innerHTML.includes('Fiktive Rückfrage zur Lampe'));run("rentalIssue().reply='<img src=x onerror=alert(1)> Fiktive Antwort';rentalAction('reply')");assert.equal(run('rentalIssue().reviewed'),false);
 go('/staff/housing/maintenance');assert(el('app').innerHTML.includes('&lt;img'));assert(!el('app').innerHTML.includes('<img src=x'));
});
check('Completion requires reviewed facts, measures and public reply; internal costs stay private',()=>{
 run("Object.assign(rentalIssue(),{measures:'INTERNAL ACTION QA',costnote:'INTERNAL COST QA',response:'Fiktiv erledigt'});rentalAction('finish')");assert.notEqual(run('rentalIssue().status'),'done');
 run("rentalIssue().review='Fiktiv erneut geprüft';rentalIssue().checked=true;rentalAction('review-issue');rentalAction('finish')");assert.equal(run('rentalIssue().status'),'done');
 const h=go('/portal/tenant/issues');assert(h.includes('Fiktiv erledigt'));assert(!h.includes('INTERNAL ACTION QA'));assert(!h.includes('INTERNAL COST QA'));
});
check('Room issue preserves its move-in snapshot; urgency sorting does not invent priority',()=>{
 go('/portal/tenant/issues');run("Object.assign(RENTAL.issueDraft,{item:'room',description:'Fiktiver vorhandener Tischkratzer',suggested:'normal'});rentalAction('create-issue')");assert.equal(run('rentalIssue().baseline.version'),2);
 go('/staff/housing/maintenance');run("Object.assign(rentalIssue(),{priority:'normal',classification:'existing',review:'Fiktiver Vorschadensbezug geprüft',checked:true});rentalAction('review-issue')");assert.equal(run('rentalIssue().decision.classification'),'existing');
 go('/staff/housing');run("RENTAL.inDraft.room='Fiktive spätere Änderung';RENTAL.inDraft.checked=true;rentalAction('save-in')");assert.equal(run('rentalIssue().baseline.version'),2);assert.equal(run('rentalIssue().baseline.data.items.room.text'),'Fiktiver Tischkratzer genauer');
});
check('Move-out without current confirmation stays unresolved; keys compared by type and objections retained',()=>{
 go('/staff/housing');run("RENTAL.panel='out';Object.assign(RENTAL.outDraft,{room:'Fiktiv unverändert',common:'Fiktiv Lampe repariert',inventory:'Tisch und Lampe',cleanliness:'Fiktiv sauber',roomKeys:'1',houseKeys:'1',checked:true});rentalAction('save-out')");assert.equal(run('RENTAL.outgoing[0].baseline'),null);
 go('/portal/tenant/handover');run("rentalAction('confirm-in')");go('/staff/housing');run("RENTAL.outDraft.checked=true;rentalAction('save-out')");assert.equal(run('RENTAL.outgoing[1].baseline.version'),3);assert.equal(run('RENTAL.outgoing[0].baseline'),null);run("RENTAL.outDraft.checked=true;rentalAction('save-out')");assert.equal(run('RENTAL.outgoing.length'),2);
 const h=go('/portal/tenant/moveout');assert(h.includes('Zimmer fehlt 1'));assert(h.includes('Vorschaden in Einzugsfassung dokumentiert'));
 run("RENTAL.objection='Fiktiv: Rückgabezahl wird bestritten';rentalAction('object')");assert.equal(run('RENTAL.outgoing[1].objections.length'),1);
 go('/staff/housing');run("RENTAL.outDraft.roomKeys='2';RENTAL.outDraft.checked=true;rentalAction('save-out')");assert.equal(run('RENTAL.outgoing[2].objections.length'),1);assert.equal(run('RENTAL.outgoing[1].data.keys.room'),1);assert(go('/portal/tenant/moveout').includes('Frühere Rückgabeaufnahmen'));
});
check('Unassigned role and unknown IDs cannot read or mutate records; draft isolation and DE/EN',()=>{
 run("RENTAL.role='other'");const h=go('/staff/housing/maintenance');assert(!h.includes('INTERNAL COST QA'));assert(!h.includes('Fiktiver vorhandener Tischkratzer'));
 const snap=run('JSON.stringify(RENTAL.issues)');run("rentalAction('finish');rentalAction('review-issue')");assert.equal(run('JSON.stringify(RENTAL.issues)'),snap);
 run("RENTAL.role='housing';RENTAL.selected='UNKNOWN';rentalAction('review-issue')");assert.equal(run('JSON.stringify(RENTAL.issues)'),snap);
 run("state.lang='en'");for(const r of ['/portal/tenant/handover','/portal/tenant/issues','/portal/tenant/moveout','/staff/housing','/staff/housing/maintenance'])assert(go(r).includes('Local housing simulation'));
});
console.log(JSON.stringify({status:'PASS',checks:tested,scope:'Local sample tenancy records only, no financial, housing-access or legal decisions'},null,2));
