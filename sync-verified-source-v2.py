"""Apply exactly four independently reviewed source supplements to the owned pilot snapshot."""
import json,hashlib,pathlib
root=pathlib.Path(__file__).resolve().parent
source=pathlib.Path('/workspace/shared/aachen-customer-20261030/content/workflow-full/parts/core-07-12-integrated-variants-v1706.json')
expected='4060e456e19821bbbf3be7b35e7a1e2257a71deb86710912aa9c76736904003d'
raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
snapshot=root/'dist/coverage-data.js';text=snapshot.read_text();data=json.loads(text.split('const COVERAGE=',1)[1].rstrip().removesuffix(';'))
ids={'WF-W07-03-01':'X038','WF-W07-04-01':'X042','WF-W07-05-01':'X044','WF-W09-02-02':'X089'}
new={p['id']:p for p in json.loads(raw)['profiles']}
before={p['id']:hashlib.sha256(json.dumps(p,sort_keys=True,ensure_ascii=False).encode()).hexdigest() for p in data['profile_mapping']}
for p in data['profile_mapping']:
 if p['id'] not in ids:continue
 q=new[p['id']]
 for key in ['title','source_refs','source_status','roles','decisions','exceptions','open_points']:p[key]=q[key]
 p['required_interactions']=q['steps'];p['acceptance_tests']=q['tests']
 p['source_supplement']={k:q[k] for k in ['goal','trigger','preconditions','inputs','data','interfaces','privacy','result','coverage_notes']}
 p['source_revision']={'variant':ids[p['id']],'path':str(source),'sha256':expected,'review':'Independent four-profile readback PASS; source content only, not production acceptance'}
unchanged=[p['id'] for p in data['profile_mapping'] if p['id'] not in ids and hashlib.sha256(json.dumps(p,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==before[p['id']]]
assert len(unchanged)==287
coverage=pathlib.Path('/workspace/shared/aachen-customer-20261030/content/workflow-full/FULL-SOURCE-COVERAGE-integrated-v2.json')
data['verified_source_supplement']={'source':str(source),'sha256':expected,'coverage_source':str(coverage),'coverage_sha256':hashlib.sha256(coverage.read_bytes()).hexdigest(),'profile_ids':list(ids),'unchanged_other_profiles':287,'designed_tests_total':sum(len(p['acceptance_tests']) for p in data['profile_mapping']),'production_tests_executed':0}
snapshot.write_text('/* Source-derived requirements catalogue; baseline is not implementation evidence. Four verified source supplements applied. */\nconst COVERAGE='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
(root/'V2-SOURCE-REFRESH.json').write_text(json.dumps(data['verified_source_supplement'],ensure_ascii=False,indent=2))
# Refresh traceability without asserting any new production implementation.
t=root/'V2-TRACEABILITY.json';trace=json.loads(t.read_text());by={p['id']:p for p in data['profile_mapping']}
for row in trace['profiles']:
 p=by[row['profile_id']];row['source_refs']=p['source_refs'];row['test_definition_ids']=[x['id'] for x in p['acceptance_tests']]
 if p['id'] in ids:row['source_revision']=p['source_revision']
trace['verified_source_supplement']=data['verified_source_supplement'];trace['planning_variants_not_activated']=trace.pop('pending_source_variants',list(ids.values()));t.write_text(json.dumps(trace,ensure_ascii=False,indent=2))
print(json.dumps(data['verified_source_supplement'],ensure_ascii=False,indent=2))
