# 2026-04-03 – Visual-System-Rollout Premium-Class

## Kontext
Das Produkt benoetigt einen konsistenten, hochwertigen, marktfuehrertauglichen
visuellen Standard. Kein zusammengebauter MVP, sondern eine aus einem Guss
gedachte Premium-Operations-Plattform.

## Zentrale CSS-Aenderungen (index.css)

### Neue Tokens
- Status-Tokens: --status-new-*, --status-active-*, --status-warning-*, --status-danger-*, --status-neutral-*
- Spacing-Tokens: --spacing-xs bis --spacing-3xl
- Transition-Tokens: --transition-fast/base/slow/spring
- z-Index-Schichten: --z-base bis --z-tooltip
- Semantische Farben mit Borders: --color-*-border
- Surface-Token: --color-surface-sunken, --color-divider-subtle
- Radii: --radius-xs (6px), --radius-xl (20px), --radius-full
- Shadow: --shadow-e4, --shadow-focus

### Neue Komponenten-Klassen
- w2g-stat-card (mit hover top-bar)
- w2g-section-heading, w2g-section-action
- w2g-alert-info/success/warning/danger
- w2g-status-new/active/warning/danger/neutral/success
- w2g-action-card, w2g-action-icon
- w2g-chat-own, w2g-chat-other, w2g-chat-meta, w2g-chat-input-area
- w2g-doc-card, w2g-doc-icon, w2g-doc-title, w2g-doc-meta
- w2g-timeline, w2g-timeline-item, w2g-timeline-dot-*
- w2g-empty (mit w2g-empty-title, w2g-empty-text, w2g-empty-hint, w2g-empty-action)
- w2g-loading (mit w2g-loading-text), w2g-skeleton
- w2g-error (mit w2g-error-icon, w2g-error-title, w2g-error-text)
- w2g-drawer, w2g-drawer-overlay, w2g-drawer-header

### Animationen
- @keyframes shimmer (Skeleton-Effekt)
- @keyframes slideInRight (Drawer)
- @keyframes pulse-dot (Status-Punkte)

## Tailwind-Config-Aenderungen
- BoxShadow: e1-e4 Ebenen
- BorderRadius: xs (6px), md (12px), lg (16px), xl (20px)
- Colors: primary.muted, accent.light
- FontFamily: DM Sans in heading, mono family hinzugefuegt

## Seiten-Rollout
1. StaffDashboard: StatCards, Section Headers, Urgent Banner, Empty State
2. AdminDashboard: StatCards, Pipeline, Activity, QuickAccess
3. PartnerDashboard: StatCards, Action Cards
4. ApplicantDashboard: QuickStats, Action Cards
5. LoginPage: Alert Pattern fuer Fehler
6. MessagesPage: Chat Bubble Patterns
7. DocumentsPage: Info Banner
8. StaffInvoicesPage: Status Badges mit Borders
9. 10+ Loading States app-weit auf w2g-loading + Text
10. Batch-Fix bg-primary/* -> bg-primary-muted (20+ Dateien)

## Mobile (390px) verifiziert
- Homepage, Login, Staff/Admin/Partner/Applicant Dashboards

## Testing
- Iteration 42: 100% Frontend (12/12 Bereiche)
