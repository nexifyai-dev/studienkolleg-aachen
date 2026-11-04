# Sources and asset provenance
Reviewed 30 October 2026.

## Domain distinction
The user named `meinstudienkolleg.de`, which returned HTTP 503 during research. The supplied Master Canvas named `deinstudienkolleg.de`. The latter was accessible and is explicitly used as the brand reference, not silently equated to the requested domain.

## Public brand reference
- https://deinstudienkolleg.de/
- https://deinstudienkolleg.de/static/css/main.e4d09145.css
- Verified primary navy `#113655`, dark `#0c2a44`, supporting navy `#17466e`, pale accent `#b3cde1`, stronger accent `#5b87ad`.
- Font families: IBM Plex Sans (body), Plus Jakarta Sans (headings).
- https://deinstudienkolleg.de/images/logos/studienkolleg-logo.png → `dist/assets/studienkolleg-logo.png`
- https://deinstudienkolleg.de/images/hero/hero-woman.webp → `dist/assets/hero-woman.webp`
- https://deinstudienkolleg.de/images/location/aachen-dom.jpg → `dist/assets/aachen-dom.jpg` (retained reference asset; not currently used in layout)
- https://deinstudienkolleg.de/static/media/IBM-Plex-Sans-400-latin.b33a81b76947ac354369.woff2 → `dist/assets/ibm-plex-sans-latin.woff2`
- https://deinstudienkolleg.de/static/media/Plus-Jakarta-Sans-500-latin.d6578b4e85b986795c74.woff2 → `dist/assets/plus-jakarta-sans-latin.woff2`
- Font licences from upstream Google Fonts OFL: https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexsans/OFL.txt and https://raw.githubusercontent.com/google/fonts/main/ofl/plusjakartasans/OFL.txt; copies included with assets.

No public numeric testimonials, outcome guarantees, prices, capacities or specific start dates were adopted. Original logo and hero image are customer-design reference assets, not newly invented endorsements. Confirm reuse rights for production.

## User-supplied process sources (read-only)
- `/workspace/shared/aachen-customer-20261030/content/workflow-brochure.md`: workflow brochure, revision 3.0, 30 Oct 2026; educational journey, role boundaries, approval and service separation.
- `/workspace/shared/aachen-customer-20261030/content/workflow-full/`: detailed workflow material available to parent and research agent.
- Research sibling verified newer W2G 22 Oct 2026 workflow precedence: DE/EN, OpenOLAT, human-approved admissions and results, separate contract/payment/access, no invented prices, agency records scoped to assigned candidates, no private document access for agency.

## Layout reference
NeXify screenshot supplied in workspace: `/workspace/scratch/df228c9caeac/graphics-reference/Bildschirmfoto 2026-10-30 um 13.53.42.png`. Structural reference only: informative main area left, persistent contextual assistant right. Not reused as a STK visual asset.

## V2 verified source supplement (30 Oct 2026)
- Part: `/workspace/shared/aachen-customer-20261030/content/workflow-full/parts/core-07-12-integrated-variants-v1706.json`; SHA256 `4060e456e19821bbbf3be7b35e7a1e2257a71deb86710912aa9c76736904003d`. Independent four-profile readback PASS supplied by source owner.
- Coverage: `content/workflow-full/FULL-SOURCE-COVERAGE-integrated-v2.json`; SHA256 `7338138bcc4d97aad7aaaaf6689fb6e62123bf4e328d2b1c388f8a9cb7a3e117`.
- Pilot snapshot changes exactly WF-W07-03-01, WF-W07-04-01, WF-W07-05-01 and WF-W09-02-02. Other 287 unchanged. X038/X042/X044/X089 remain source-described planning/offer variants, not active integrations or expanded authority.
- 992 designed test definitions are presented as NOT EXECUTED production tests. PDF rendering and publication approval are separate processes, not inferred from source readback.
