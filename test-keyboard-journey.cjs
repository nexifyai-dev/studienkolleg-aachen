const vm=require('vm'),fs=require('fs'),assert=require('assert');const elements={};const listeners={};function el(id){return elements[id]??={innerHTML:'',textContent:'',value:'',checked:false,dataset:{},classList:{add(){},remove(){},toggle(){},contains(){return false}},addEventListener(type,fn){(listeners[id]??={})[type]=fn},focus(){},scrollIntoView(){},querySelectorAll(){return []},querySelector(){return null},scrollTop:0,scrollHeight:0}}const sandbox={console,location:{hash:'#/'},document:{documentElement:{lang:'de'},body:el('body'),getElementById:el,querySelectorAll(){return []},querySelector(s){return s==='body>.skip'?el('skip'):null},addEventListener(){}},window:{addEventListener(){},scrollTo(){}},setTimeout(){},clearTimeout(){}};vm.createContext(sandbox);for(const f of ['app.js','coverage-data.js','v2.js','migration-data.js','v3.js','content-data.js','v3-content.js','edition-data.js','media-data.js','v3-migration.js','admissions.js','learning-journey.js','attendance-journey.js','case-journey.js','appointment-journey.js','rental-journey.js','library-journey.js','arrival-journey.js','knowledge-journey.js'])vm.runInContext(fs.readFileSync(__dirname+'/dist/'+f,'utf8'),sandbox,{filename:f});const run=s=>vm.runInContext(s,sandbox);const go=r=>{sandbox.location.hash='#'+r;run('render()');return el('app').innerHTML};const tested=[];function check(name,fn){fn();tested.push(name)}


check('Skiplink preserves route and draft while focusing current main',()=>{
 go('/apply');run("state.step=2;state.brief='Fictional QA';V2.notes['visitor:journey'].brief='Fictional QA';render()");
 let prevented=0,focused=0,scrolled=0;el('main').focus=()=>focused++;el('main').scrollIntoView=()=>scrolled++;
 assert.equal(typeof listeners.skip?.click,'function');
 listeners.skip.click({preventDefault(){prevented++}});
 assert.equal(sandbox.location.hash,'#/apply');assert.equal(prevented,1);assert.equal(focused,1);assert.equal(scrolled,1);assert.equal(run('state.step'),2);assert.equal(run('state.brief'),'Fictional QA');
 assert(el('app').innerHTML.includes('id="main" tabindex="-1"'));
});

check('Explicit application transitions move focus; edits and other routes do not',()=>{
 let focused=0;el('main').focus=()=>focused++;
 go('/apply');run("state.submitted=false;state.step=0");
 for(const [a,v] of [['next',''],['back',''],['step','3'],['complete',''],['edit-application','']])run(`action(${JSON.stringify(a)},${JSON.stringify(v)})`);
 assert.equal(focused,5);
 run("action('upload','0');action('topic','Kurswahl')");assert.equal(focused,5);
 go('/portal/applicant');run("action('step','1')");assert.equal(focused,5);
});
console.log(JSON.stringify({status:'PASS',checks:tested,scope:'Local event/DOM stub; browser keyboard proof separate'},null,2));
