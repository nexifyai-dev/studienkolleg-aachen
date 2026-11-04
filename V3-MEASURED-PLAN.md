# V3 — Visitor-first redesign and migration plan

Status 2026-10-30 18:08 UTC: audited V2, implementation authorized but not yet accepted. No claim of a complete product. The 291 workflow views are specification readers, not 291 implemented business features.

## Fresh browser observations
Browser CUA, original tab28 and local pilot tab19, supported Sites preview. Published private URL led to sign-in; no authentication attempted. No global window/zoom changes (parallel manual auth handoff protected).

| Dimension | V2 fresh preview | Existing deinstudienkolleg.de |
|---|---:|---:|
| CSS viewport |1180 × 757|1267 × 835|
| Content width |835|full width1267|
| Assistant width |330|none|
| Header before main |154.64|80|
| H1 |48 /53.76px|56 /60.48px|
| Intro paragraph |14 /23.8px|17 /28.9px|
| H2 |32 /35.84px|44 /48.4px|
| Hero image |visually squeezed against rail|473.92 ×422.77px|
| Assistant rectangle |x835 y154.64 w330 h607; bottom761.64|n/a|

These are real independent browser measurements, not equal-width comparisons or mobile device approval. V2 screenshot confirms nested visible scrollbar, duplicate dark hero+sidebar seam, disproportionately tiny navigation/eyebrows, competing internal control UI. No overlap does not equal a good integrated design. V2 rail extends4.64px below this viewport. On mobile the old rail follows the entire long page, making assistance hard to find.

## Design system acceptance targets (not measured results)
- One80px desktop header, optional24px discreet preview disclosure; no ecosystem selector, role switch, public coverage/test links.
- Maximum1440px content frame. Desktop >1100: content min0/remaining +344px contextual companion; 32px outer/24px inner spacing. Companion shares main section baseline, not a floating overlay. Heading and helper not two competing giant titles.
- Hero H1 clamp36–56px; body17px/1.65; navigation14px; labels minimum12px. Buttons44px minimum; consistent8px spacing scale.
- Medium801–1100: compact companion296px only where readable; otherwise in-flow inline guidance card. <=800: one-column composition, compact inline assistance immediately after introduction, expandable conversation without overlay; never at end of5000px document.
- Composer always in viewport on desktop; available height measured from actual header, no hardcoded obsolete offset. One message-body scroll region only after conversation grows.
- Preserve navy/pale-blue identity, original logo, supplied font files, authentic campus/leadership/housing imagery. Do not manufacture housing photography.

## Public information architecture
Visitor navigation by intention: Studienkolleg; Deutsch & Prüfungen; Wohnen; Studieren & Ankommen; Über uns/Wissen. Persistent Beratung and Mein Bereich, with one Bewerbung CTA. Contextual subsections, not internal mode tabs. Separate public partner/employer pages and their access links; staff entry separate from applicant login. Internal evidence remains reachable by explicit review URL, not public marketing navigation.

## Migration gaps confirmed before build
1. Existing hero/leadership Laura Saboor, campus gallery, nine short videos, testimonials, full FAQ/contact/legal/footer missing or replaced by generic blocks.
2. Real T/M/W/T+M course text and legacy fee records absent. Pricing conflicts must remain pending verification, not silently chosen.
3. Real housing property/room records and photos were replaced by three invented examples. Restore source-derived property content, preserve clear non-live availability and enquiry simulation.
4. Multi-provider blocked account/insurance comparison omitted; only cards. Need filters, side-by-side comparison, distinctions between external application and no local checkout.
5. University search limited to three sample records and one filter. Need language/start/deadline/cost/FSP/TestAS filters, suitability/missing prereqs, per-record provenance/review state, individual application handoff.
6. Existing exam breadth onSET/dMAT/TestAS/TestDaF/ÖSD, actual dated records and conflicting dates absent. Dates must not be sold as live availability.
7. Original navigation languages8 vs newer requirements DE/EN: explicit migration decision required, never imply untranslated versions complete.
8. Real legacy sites www.studienkollegaachen.de and way2germany.designschaefer.com were not audited in V2. Their content inventory now being delivered by independent source audit.

## Delivery sequence
A. Rebuild visitor shell/navigation, unified content/assistant composition, original homepage content and contextual access; browser screenshots/geometry.
B. Source-bound course/housing/exam/legal/contact migration; all conflicts retained in internal ledger, customer-facing concise confirmation wording.
C. Actual comparison/search interactions (insurance/blocked account and university) with clear sample/provider status and enquiry handoff.
D. Cross-link complete role journeys, preserving V2 positive/negative gates, not conflating spec viewers with feature delivery.
E. Independent browser route/function/visual review; real CSS width evidence where supported; parent alone publishes.

No backend, live AI, booking, payment, upload or genuine account access is implemented. Production migration and legally current claims require separate verification.
