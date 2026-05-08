import React from 'react';
import { Card, CardContent } from '../ui/card';
import { ArrowRight } from 'lucide-react';

/* ═══════════════════════════════════════════════════════════════════
   BACKSTAGE-INSPIRIERTE LAYOUT-KOMPONENTEN
   Modulares System fuer komplexe Dashboards und Detail-Ansichten.
   Alle Komponenten nutzen das strikte CSS-Variablen-System aus index.css.
   ═══════════════════════════════════════════════════════════════════ */

/* ─── InfoCard ────────────────────────────────────────────────────
   Backstage-Muster: Karte mit strukturiertem Header (Titel, Subtitle,
   Action-Bereich) und optionalem DeepLink-Footer.
   Ersetzt das manuelle Card > CardHeader > CardTitle > CardContent Pattern.
   ─────────────────────────────────────────────────────────────────── */
export function InfoCard({
  title,
  subtitle,
  headerAction,
  deepLink,
  deepLinkText,
  deepLinkHref,
  icon: Icon,
  noPadding = false,
  variant = 'default',
  className = '',
  children,
  testId,
}) {
  const variantStyles = {
    default: '',
    elevated: 'shadow-[var(--shadow-e2)]',
    outlined: 'shadow-none',
  };

  return (
    <Card
      className={`${variantStyles[variant] || ''} ${className}`}
      data-testid={testId}
    >
      {(title || subtitle || headerAction || Icon) && (
        <div className="flex items-start justify-between gap-3 px-5 pt-4 pb-0">
          <div className="flex items-start gap-3 min-w-0">
            {Icon && (
              <div className="w-8 h-8 flex items-center justify-center shrink-0 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] text-[var(--color-primary)]">
                <Icon size={15} />
              </div>
            )}
            <div className="min-w-0">
              {title && (
                <h3
                  className="text-sm font-bold text-[var(--color-text-primary)] leading-tight tracking-tight"
                  style={{ fontFamily: 'var(--font-heading)' }}
                >
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="text-[11px] text-[var(--color-text-secondary)] mt-0.5 leading-relaxed">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          {headerAction && <div className="shrink-0">{headerAction}</div>}
        </div>
      )}
      <div className={noPadding ? '' : 'px-5 pb-4 pt-3'}>{children}</div>
      {(deepLink || deepLinkText) && (
        <div className="border-t border-[var(--color-divider-subtle)]">
          {deepLink || (
            <a
              href={deepLinkHref || '#'}
              className="flex items-center justify-end gap-1.5 px-5 py-2.5 text-[11px] font-semibold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors"
            >
              {deepLinkText} <ArrowRight size={12} />
            </a>
          )}
        </div>
      )}
    </Card>
  );
}

/* ─── TabbedCard ──────────────────────────────────────────────────
   Backstage-Muster: Karte mit eingebauter Tab-Navigation.
   Fuer Bereiche die mehrere Ansichten in einer Karte benoetigen.
   ─────────────────────────────────────────────────────────────────── */
export function TabbedCard({
  title,
  tabs = [],
  activeTab,
  onTabChange,
  headerAction,
  noPadding = false,
  className = '',
  children,
  testId,
}) {
  return (
    <Card className={className} data-testid={testId}>
      <div className="px-5 pt-4 pb-0">
        {(title || headerAction) && (
          <div className="flex items-center justify-between mb-3">
            {title && (
              <h3
                className="text-sm font-bold tracking-tight"
                style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}
              >
                {title}
              </h3>
            )}
            {headerAction && <div className="shrink-0">{headerAction}</div>}
          </div>
        )}
        <div className="w2g-tabs" data-testid={testId ? `${testId}-tabs` : undefined}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabChange(tab.id)}
              className={activeTab === tab.id ? 'w2g-tab-active' : 'w2g-tab'}
              data-testid={testId ? `${testId}-tab-${tab.id}` : undefined}
            >
              {tab.icon && <tab.icon size={13} className="inline mr-1.5 -mt-px" />}
              {tab.label}
              {tab.count !== undefined && (
                <span
                  className="ml-1.5 text-[10px] font-bold tabular-nums px-1.5 py-0.5 rounded-[var(--radius-full)]"
                  style={{
                    background:
                      activeTab === tab.id ? 'rgba(17,54,85,0.1)' : 'var(--color-surface-sunken)',
                    color: activeTab === tab.id ? 'var(--color-primary)' : 'var(--color-text-tertiary)',
                  }}
                >
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
      <div className={noPadding ? '' : 'px-5 py-4'}>{children}</div>
    </Card>
  );
}

/* ─── StatusLine ──────────────────────────────────────────────────
   Backstage-Muster: Kompakte Statusleiste am unteren Seitenrand.
   Zeigt Metadaten/KPIs inline an.
   ─────────────────────────────────────────────────────────────────── */
export function StatusLine({ items = [], className = '', testId }) {
  if (!items.length) return null;
  return (
    <Card className={className} data-testid={testId}>
      <CardContent className="py-2 px-5">
        <div className="flex items-center gap-5 flex-wrap">
          {items.map((item, i) => (
            <div key={i} className="flex items-center gap-1.5 text-[11px]">
              {item.icon && (
                <item.icon
                  size={12}
                  style={{ color: item.color || 'var(--color-text-tertiary)' }}
                />
              )}
              <span className="font-medium text-[var(--color-text-tertiary)]">{item.label}</span>
              <span
                className="font-bold tabular-nums"
                style={{ color: item.color || 'var(--color-text-primary)' }}
              >
                {item.value}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/* ─── ContentHeader ───────────────────────────────────────────────
   Erweitert PageScaffold um Metadata-Badges und strukturierte
   Header-Informationen. Kann als Ersatz fuer den manuellen
   Card-Header-Block in Seiten verwendet werden.
   ─────────────────────────────────────────────────────────────────── */
export function ContentHeader({
  title,
  subtitle,
  actions,
  metadata = [],
  breadcrumb,
  testId,
}) {
  return (
    <Card style={{ borderLeft: '4px solid var(--color-primary)' }} data-testid={testId || 'content-header'}>
      <CardContent className="py-3.5 px-5">
        {breadcrumb && (
          <div className="text-[10px] text-[var(--color-text-tertiary)] mb-1.5">{breadcrumb}</div>
        )}
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="min-w-0">
            <h1
              className="text-lg font-bold tracking-tight"
              style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}
            >
              {title}
            </h1>
            {subtitle && (
              <p className="text-[11px] text-[var(--color-text-secondary)] mt-0.5 leading-relaxed">
                {subtitle}
              </p>
            )}
          </div>
          <div className="flex items-center gap-3 shrink-0 flex-wrap">
            {metadata.length > 0 && (
              <div className="flex items-center gap-4 text-[10px] font-semibold text-[var(--color-text-tertiary)]">
                {metadata.map((m, i) => (
                  <span key={i} className="flex items-center gap-1">
                    {m.icon && <m.icon size={11} />}
                    {m.label}
                  </span>
                ))}
              </div>
            )}
            {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/* ─── FullHeightLayout ────────────────────────────────────────────
   Berechnet die verbleibende Viewport-Hoehe und fuellt sie aus.
   Verhindert doppelte Scrollbalken bei Chat- oder Kanban-Ansichten.
   ─────────────────────────────────────────────────────────────────── */
export function FullHeightLayout({
  headerOffset = 0,
  children,
  className = '',
  testId,
}) {
  return (
    <div
      className={`flex flex-col ${className}`}
      style={{
        height: `calc(100vh - var(--topbar-height) - ${88 + headerOffset}px)`,
        minHeight: '400px',
      }}
      data-testid={testId}
    >
      {children}
    </div>
  );
}

/* ─── SplitLayout ─────────────────────────────────────────────────
   Zweispalten-Layout mit einklappbarer Sidebar.
   Backstage-Muster fuer Master-Detail Ansichten.
   ─────────────────────────────────────────────────────────────────── */
export function SplitLayout({
  sidebar,
  sidebarWidth = 280,
  sidebarOpen = true,
  onToggleSidebar,
  toggleIcon,
  children,
  className = '',
  testId,
}) {
  return (
    <Card className={`overflow-hidden p-0 flex flex-1 ${className}`} data-testid={testId}>
      {/* Sidebar */}
      <div
        className="border-r border-[var(--color-divider)] flex flex-col bg-[var(--color-surface)] transition-all overflow-hidden shrink-0"
        style={{ width: sidebarOpen ? `${sidebarWidth}px` : '0px' }}
        data-testid={testId ? `${testId}-sidebar` : undefined}
      >
        {sidebar}
      </div>

      {/* Toggle */}
      {onToggleSidebar && (
        <button
          type="button"
          onClick={onToggleSidebar}
          className="flex items-center justify-center w-5 bg-[var(--color-surface-sunken)] border-r border-[var(--color-divider)] hover:bg-[var(--color-divider-subtle)] transition-colors shrink-0"
          data-testid={testId ? `${testId}-toggle` : undefined}
        >
          {toggleIcon || (
            <span className="text-[var(--color-text-tertiary)] text-xs">|</span>
          )}
        </button>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 bg-[var(--color-surface)]">{children}</div>
    </Card>
  );
}
