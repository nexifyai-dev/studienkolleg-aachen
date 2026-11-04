# V2 — connected website, microsites, portals and source workbench

## Result and limits
The V2 shell exposes 34 source-derived area families and resolves all **222 concrete proposed route patterns**; the source's 223rd entry means “all public and portal routes” rather than a literal path. All 291 source profiles have their own `/workflow/:profileId` view with exact roles, steps, decisions, exceptions, open points and test definitions. **A profile renderer is not implementation of that business process.** Repeated/shared page types are intentional reusable workbenches, not independently implemented backend modules.

The product-facing depth includes:
- Stay in Aachen: location/type/amenity/period filter, empty state/reset, sample property, schematic floor plan, room/bed, separate external evidence gate, enquiry/manual review/waitlist; no reservation.
- Tenant lifecycle: contract, separate rent/deposit, move-in, issues, extension and move-out sample records.
- Housing operations: inventory by bed, overlap and head-lease gates, waitlist, source-bound owner/settlement workflows.
- Language school: A1/A2/B1/B2/C1 entry pages, packages, certificate/written assessment pathway, self-learning duration and non-renewal, separate B2 nursing preparation.
- Exams: ÖSD modules, sample slot, capacity+confirmed-payment gates, provider-owned TestDaF/TestAS pathway, result/certificate source processes.
- University service: fictional programme search, shortlist toggling, comparison, individual application approval, draft-only result.
- Nursing/careers/employers: planned rotation/logbook, voluntary profile activation, candidate-controlled sample match, anonymous talent pool and interview gate.
- Finance: confirmed receipt vs document, match suggestion, human review; separate ledger/refund/cash/closing source processes.
- Scheduling, learning, admissions, teaching, certificates, marketing, knowledge, management, tenant/role administration and integration workspaces.
- White-label/master views: sample tenant configuration and unconnected domain/app states, no provisioning.

## Files and reusable components
`app.js` retains V1 marketing/course/application components and safe demo primitives. `v2.js` composes the ecosystem navigation, true grid shell, domain-specific page types, source-bound workbenches and state machines. `v2.css` overrides legacy mobile overlay behaviour: below 800px the companion is an ordinary document-flow section after content, never a floating overlay. The desktop companion occupies its own CSS grid track. `coverage-data.js` preserves the complete source matrix snapshot without claiming its baseline status as current implementation proof.

Common functions: `vheading`, `subnav`, `sourceStrip`, `field`, `check`, `vbtn`, `panel`, `workflowBrief`, `genericTaskBoard`, `profileLinks`, `relatedPanel`. Domain renderers: `housing`, `tenant`, `languagePage`, `selfLearning`, `exams`, `university`, `nursing`, `careers`, `platform`, `servicesPage`, `publicContent`, `staffWorkspace`. Source workbench: `coveragePage`, `workflowPage`, `conflictsPage`.

## Content vs internal architecture
Public marketing pages contain audience-facing explanations and next steps, not the 291-profile implementation catalogue. The complete register lives in clearly labelled concept/workbench routes `/coverage`, `/workflow/*`, `/conflicts`, and `/admin/acceptance`. Small provenance links remain in the pilot footer. Source profile lists are restricted to staff/admin/concept views by renderer context; these are presentation boundaries, not security enforcement.

## State and scope
All state is in page memory, discarded on reload. No localStorage, network writes, authentication, uploaded files, payments, real reservations, electronic signatures, provisioning or live agents. User/area notes use separate keys for public and staff contexts. Candidate disclosure is not implemented: anonymous records stay anonymous even after sample acceptance. Health information is neither requested nor processed.

## Traceability and tests
- `V2-TRACEABILITY.json`: all 291 profile bindings, area routes, exact source references, the dedicated workflow route, demo interaction and test definition IDs.
- `test-v2.cjs`: 222 pattern renders, 291 profile renders and representative positive/negative local-state tests.
- `V2-TEST-RESULTS.json`: actual Node VM results, explicitly not browser/production evidence.
- Parent task owns browser QA and publishing. Production test definitions remain **not run**; no green completion badges imply otherwise.

## Verified source correction
Four independently reviewed source supplements were applied from `core-07-12-integrated-variants-v1706.json`, SHA256 `4060e456e19821bbbf3be7b35e7a1e2257a71deb86710912aa9c76736904003d`: X038 → WF-W07-03-01, X042 → WF-W07-04-01, X044 → WF-W07-05-01, X089 → WF-W09-02-02. The other 287 pilot catalogue profiles are byte-equivalent under canonical JSON comparison. All 291 profiles now contain **992 designed test definitions, zero executed production tests**. The variants remain planning/offer supplements, not active functions, accepted contractual extensions or verified legal/normative rules. The source changes are visible in the affected profile steps, branches, exceptions, test definitions and detailed supplement disclosure. Provenance and exact hashes are recorded in `V2-SOURCE-REFRESH.json`; original shared source files were not modified.

## Remaining production work
Server-enforced tenant/role isolation, provider adapters, approved public/legal/pricing content, real inventory/assets and permissions, approved tests and assessment thresholds, consent/retention policies, audited human approvals, concurrency, idempotency and recovery require separate implementation and acceptance. UI simulation cannot establish these controls.

## Bounded root browser evidence
`V2-BROWSER-QA.json` captures Cloud Chromium local-preview checks. At 1180 CSS px, main right and assistant left both measured 835px, overlap 0. A zoom-based narrow reflow at 393 CSS px / 252px height measured main bottom equal to assistant top (1072.698px), static assistant and no overlap or horizontal overflow. This is **not physical-device/mobile emulation acceptance**. Housing external evidence and ÖSD payment/capacity positive/negative flows passed. Other families require separate checks; source hash validation is documented independently.
