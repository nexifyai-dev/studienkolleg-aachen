# Studienkolleg Aachen — reusable website and portal pilot

## Scope and ownership
A buildless, static, fully client-side concept shell. Public marketing content sits left; a contrasting, contextual study companion sits right. The established STK navy/pale-blue palette, original logo, original hero image and self-hosted brand fonts are retained. The NeXify pattern is structural, not a rebranding into NeXify colours.

Website registration, deployment, source synchronization and hosting metadata are owned by the parent task, not this implementation subtask. No customer document sources were changed.

## Component library
- `dist/tokens.css`: colour, type, spacing and radius foundations; local brand font faces.
- `dist/style.css`: responsive shell, hero, cards, course finder, forms, timeline, portal navigation, status indicators, modal, chat and workflow panel.
- `dist/app.js`: reusable `link`, `button`, `badge`, `panel`, `notice`, `heading`, `courseCard`, `documentRows`, `taskRows`, `stat`, `modal`, and contextual `assistant` functions.
- Data: `courses`, `courseGuidance`, role labels, persona-isolated in-memory brief/chat state.
- Routes: hash navigation, no server routing requirements or framework dependencies.
- Interactions: deterministic local state and modal flows. No fetch, API keys, real auth, payments, external forms, uploads or write integrations.

## Route inventory
Public: `#/`, `#/courses`, `#/course/{T,M,W,G,TM,Deutsch,TestAS}`, `#/admission`, `#/apply`, `#/help`, `#/services`, `#/services/housing`, `#/about`.

Portals: `#/portal/{applicant,student,teacher,admin,partner}` with role-specific overview/navigation; tasks, documents, messages, finances and appointments where applicable. Teacher attendance and assessment views. Admissions case board, human review modal and local workflow builder. Agency visibility demonstrates assigned candidate statuses and commissions only, never applicant documents or staff notes through its menu. **This is not security enforcement:** hashes and client source remain inspectable; production RBAC is not implemented.

## Requirement → component → test traceability
| Requirement | Component / route | Check / acceptance evidence |
|---|---|---|
| REQ-BRAND-01: retain STK brand | tokens, Header, Hero; `/` | BRAND-01: original assets, navy gradient, pale-blue CTA, local typefaces |
| REQ-SHELL-01: information left, companion right | Layout, Assistant | SHELL-01: desktop rail; mobile toggled drawer |
| REQ-COURSE-01: meaningful course discovery | CourseCard, CourseDetail; `/courses`, `/course/*` | COURSE-01: all/language/preparation filter; course-specific narrative and advisory question |
| REQ-APPLY-01: guided preparation | Stepper, documentRows; `/apply` | APPLY-01: four steps; sample file add; brief; completion without submission |
| REQ-ASSIST-01: contextual bounded guidance | Assistant, rolePrompts, chat | CHAT-01: deterministic prompts/free-text routing; explicit demo; source dates; editable brief |
| REQ-ROLE-01: role context separation | syncPersona, personaMemory | ROLE-01: applicant/student journey shared; teacher/admin/agency brief/chat isolated |
| REQ-LEARN-01: participant learning view | student overview, LMS modal | LEARN-01: timetable and OpenOLAT preview; no live connection or access promise |
| REQ-TEACH-01: assigned-class workflow | teacher attendance/grades/classbook | TEACH-01: local attendance choice; draft vs published result explanation |
| REQ-ADM-01: admission human decision | admin cases, case review modal | CASE-01: reason required before simulated request/review; no real approval |
| REQ-WORKFLOW-01: reusable process stages | WorkflowPanel / admin | FLOW-01: configurable sample request stage, planned document/admission agents, mandatory human gate; no execution |
| REQ-PARTNER-01: constrained agency view | partner overview/financials | PARTNER-01: assigned sample candidates, no applicant files or internal notes in menu |
| REQ-SERVICES-01: separated service requests | services, housing/exam/arrival modals | SERVICE-01: no reservation, visa guarantee or exam checkout |
| REQ-I18N-01: DE/EN | t(), language toggle | LANG-01: meaningful public and portal content switches; brand/sample identifiers retained |
| REQ-A11Y-01: usable controls | native controls, skip link, dialog focus | A11Y-01: labels, keyboard focus, Escape, modal focus trap, mobile actions |
| REQ-DEMO-01: no actual private data | in-memory state, pilot banner, about/privacy | PRIV-01: no localStorage, fetch, auth or real file input; reload discards entries |

## Reusable architecture beyond pilot
These modules form a pattern library, not a claim that production systems exist. A future implementation should extract the view/component functions into framework modules, separate route/data definitions, add server-enforced identity and role boundaries, approved content management, audited workflows, document security, permissions, retention rules and dedicated provider adapters. Planned specialist agents should only prepare suggestions from approved sources, with traces to requirements, workflow stage, source version and human review. Public website copy should remain student-facing; governance belongs in staff interfaces and implementation documentation.

## Verification and limitations
`node --check dist/app.js` passes. Additional static runtime smoke checks exercise public routes, role routes and persona state isolation (see `smoke-test.cjs`). Parent task owns browser interaction QA and publication. All functional status changes are local demonstrations; no production acceptance implied. DE/EN is meaningful but a few sample dropdown values/class identifiers intentionally remain German. Agency restrictions are presentation only, not security. Hero imagery is reused solely as a customer concept reference; asset rights should be confirmed before general public production deployment.
