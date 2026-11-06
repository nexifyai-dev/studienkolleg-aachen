import json,pathlib,collections
r=pathlib.Path(__file__).parent;p=json.load(open(r/'V3-MIGRATION-REGISTER.json'));ed={x['source']:x for x in json.load(open(r/'V3-EDITION-PREPARED.json'))}
for x in p['records']:
 u=x['source_url'];target=x['target_route_suggestion'];status='requires-final-editorial-reconciliation'
 if u in ed:status='source-language-editorial-detail-and-contextual-journey';x['editorial_detail_route']='/informationen/'+ed[u]['id']
 elif x.get('status')!='read':status='source-unavailable-cannot-migrate-unread-content'
 elif 'uncategorized' in u or 'post_type=' in u:status='non-product-template-content-retained-not-promoted'
 elif target=='/apply/bestaetigung':status='local-confirmation-state-not-fake-live-success'
 elif 'stayinaachen.de/' in u:
  if any(s in u for s in ['single','double']):status='source-property-room-data-and-correct-gallery-migrated'
  elif 'datenschutz' in u:status='older-privacy-wording-preserved-not-promoted-as-current-policy'
  elif 'impressum' in u:status='company-contact-details-curated-conflicting-legal-version-preserved'
  elif 'contact-us' in u:status='housing-enquiry-form-and-published-contact-path'
  else:status='housing-discovery-search-and-amenities-curated'
 elif 'w2g-pruefungen.de/' in u:
  if '/termine/' in u:status='date-conflict-preserved-source-link-and-confirmation-journey'
  elif '/kontakt' in u:status='examination-contact-path-and-location-preserved'
  elif '/impressum' in u:status='company-contact-details-curated-conflicting-legal-version-preserved'
  else:status='five-exam-family-discovery-detail-and-provider-paths'
 elif 'deinstudienkolleg.de/' in u:
  tail=u.rstrip('/').split('/')[-1]
  status={'courses':'curated-course-discovery-and-source-facts','services':'services-comparison-recognition-mentoring-journeys','knowledge':'1770-source-entries-searchable-in15topics','contact':'published-contact-data-and-direct-links','preise':'individual-offer-policy-conflicting-prices-not-asserted','legal':'published-company-legal-contact-data','privacy':'full-published-source-wording-not-new-legal-approval','agb':'full-published-source-wording-not-new-legal-approval','widerruf':'full-published-source-wording-not-new-legal-approval','booking':'three-step-advisory-flow-and-real-external-target','deinstudienkolleg.de':'homepage-brand-leadership-campus-contact-and11video-references'}.get(tail,status)
 x['implementation_status']=status
p['counts']=dict(collections.Counter(x['implementation_status'] for x in p['records']));(r/'V3-MIGRATION-REGISTER.json').write_text(json.dumps(p,ensure_ascii=False,indent=2));print(json.dumps(p['counts'],indent=2))
