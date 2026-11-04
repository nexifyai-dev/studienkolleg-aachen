# WF-PILOT-SIM-01 — source-bound workflow explorer

## 1. Document Control
Version 2.0 · concept implementation · owner: assigned pilot writer · sources: full coverage matrix dated 30 Oct 2026 · status: local-demo implemented, production not applicable.
## 2. Executive Summary
Goal: make every supplied profile traceable without pretending its process is operational. Outcome: browse source requirements, mark steps reviewed, explore yes/no decisions and exceptions. Non-goal: execute the underlying business action.
## 3. Source Requirements
REQ-SIM-01: retain every profile and source reference. REQ-SIM-02: source → route → interaction → test traceability. REQ-SIM-03: distinguish planned, demo and unverified production. REQ-SIM-04: visible source conflicts. REQ-SIM-05: no secrets/personal data/external writes.
## 4. Assumptions
ASSUMPTION-01: a source profile can be displayed as a specification without being accepted business scope. ASSUMPTION-02: local sample states have no contractual effect.
## 5. Open Questions / Missing Information
Corrected source profile hash verified for X038/X042/X044/X089: 4060e456e19821bbbf3be7b35e7a1e2257a71deb86710912aa9c76736904003d. Their business activation remains unapproved. Source matrix lists six further missing-material groups. Production role/delegation rules and provider contracts need separate confirmation.
## 6. Actors & Responsibilities
Visitor reviews public content. Demo role explores its sample workspace. Source reviewer inspects requirements and unresolved conflicts. No browser actor receives real permissions.
## 7. Systems & Integrations
Browser-only HTML/CSS/JS. Local, bundled source data. No provider calls. OpenOLAT/BBB/Drive/bank states are previews, not connected systems.
## 8. Data Model & Data Contracts
Input: profile ID in catalogue; required_interactions, decisions, exceptions, source_refs, acceptance_tests. Output: in-memory reviewed-step index, explored branches, local audit entries. Validation: unknown profile → explicit not-found page; invalid route → not-found, not generic fallback. Source-of-truth: supplied versioned catalogue, not local demo edits.
## 9. Trigger & Preconditions
Navigate to `/workflow/<known-id>`. Profile must exist in bundled catalogue. No login or payment precondition for a concept preview.
## 10. Workflow State Model
UNREAD → REVIEWING → REVIEWED. REVIEWING may explore YES/NO and EXCEPTION paths independently. Reset returns UNREAD. No state is named “business approved” or “production complete”.
## 11. End-to-End Workflow Logic
STEP-01 resolve profile. STEP-02 display exact source/roles/limits. STEP-03 display all numbered source steps. STEP-04 mark a step reviewed; clamp at step count. STEP-05 display both decision branches on demand. STEP-06 display exception handling and resume condition. STEP-07 show test definitions as not executed. STEP-08 retain local audit until reload.
## 12. Decision Matrix
DEC-01 known profile? yes render; no not-found. DEC-02 current step below total? yes increment; no remain terminal. DEC-03 selected branch yes/no? display corresponding source outcome; unknown branch is not exposed by controls. DEC-04 pending source variant? show warning; otherwise no variant warning.
## 13. Parallelism, Joins & Concurrency
One browser memory state. No backend, shared writer, external lock or concurrent transaction. Multi-tab copies are independent; not a production concurrency model.
## 14. Timers, Waiting & Scheduling
N/A: no scheduled side effects. Toast timeout affects visibility only. Source refresh requires an explicit verified code/data update.
## 15. Human-in-the-Loop / Approvals / Escalations
The UI displays source human tasks. Clicking a branch is exploration, never an approval. Pending source conflicts remain visible and cannot be resolved by a UI click.
## 16. Integration Specifications
N/A for network endpoints, authentication and rate limits: no external integration calls. Future adapters require independent specifications and approvals.
## 17. Transaction & Saga Boundaries
N/A for persistent transactions. Each local action mutates only its in-memory demonstration object.
## 18. Error Handling & Recovery Matrix
Unknown route/profile → explicit 404. Missing source business detail → open question. Capacity/evidence/consent absent in domain demos → blocked local transition with feedback. Refresh discards local states; this is not recoverable persistence.
## 19. Idempotency & Duplicate Prevention
Step index is clamped. The integration-retry demo sets one boolean sample state, so repeated clicks do not create extra sample events. No claim about real event delivery or backend idempotency.
## 20. Compensation / Rollback Logic
Reset clears review progress, not source data. No records are deleted. No external side effects require compensation.
## 21. Security, Privacy & Permissions
No real auth/ACL. No personal/health input requested. Public/staff notes use separate context keys. Source code is inspectable. Role menus are not a security boundary.
## 22. Observability
Local review audit contains profile ID and reviewed/explored labels, no personal information. No analytics or telemetry backend. Test logs are local files.
## 23. SLA/SLO & Operational Rules
N/A: concept preview, no production service-level commitment. Do not represent source process test definitions as executed results.
## 24. Edge Cases & Exception Paths
Unknown profile; empty filter; full capacity; absent external evidence; unconfirmed bank receipt; missing individual application consent; inactive career profile; room overlap; head-lease end; repeat retry; role/context note isolation; changed language; reset/reload.
## 25. Test Specification
Node VM tests cover all routes/profiles and representative positive/negative state gates. Parent browser QA covers actual layout, focus and interactions. Integration/retry/concurrency/recovery tests for production remain not run. Exact profile test IDs remain visible without passing labels.
## 26. Deployment, Versioning & Migration
Buildless files packaged by parent via official Sites workflow. Source data snapshot retained with hash. No production data migration or domain cut-over.
## 27. Acceptance Criteria
All source profile IDs resolve; no generic 404 fallback pretends completion; no external effects; branch/exception text matches source; visible scope/limitations; layout reserves assistant grid space; sources and test status remain auditable.
## 28. Traceability Matrix
REQ-SIM-01 → catalogue resolver → STEP-01/02 → 291-render test. REQ-SIM-02 → source/profile route → STEP-07 → V2-TRACEABILITY. REQ-SIM-03 → evidence status → STEP-07 → no production-pass claim. REQ-SIM-04 → variant/conflict warnings → DEC-04 → affected profile render. REQ-SIM-05 → memory-only controller → STEP-04/05 → static no-network review and context isolation test.
## 29. Completeness & Consistency Review
222 literal route patterns plus one all-routes conceptual requirement; 291 distinct profiles. Source implementation depth is explicitly differentiated from UI rendering. Four late source supplements are now hash-verified and incorporated; their operational activation remains pending.
## 30. Implementation Handoff
Parent owns browser acceptance, source registration and private publication. No credentials are needed for the simulator. Production integrations, security controls, policies and source corrections require separate verified implementation; none is silently supplied by this prototype.
