import React from 'react';
import { Card, CardContent } from '../ui/card';

export function ToolbarRow({ search, filters = [], viewSwitcher, secondaryActions = [], primaryAction, extra, className = '' }) {
  return (
    <Card className={className} data-testid="page-toolbar">
      <CardContent className="py-2.5 px-4">
        <div className="flex items-center gap-3 flex-wrap">
          {search && <div className="min-w-0 flex-1">{search}</div>}
          {filters.length > 0 && <div className="flex flex-wrap items-center gap-2">{filters}</div>}
          {viewSwitcher && <div className="flex flex-wrap items-center gap-2">{viewSwitcher}</div>}
          {extra && <div className="flex items-center gap-2">{extra}</div>}
          {secondaryActions.length > 0 && <div className="flex flex-wrap items-center gap-2">{secondaryActions}</div>}
          {primaryAction && <div className="ml-auto flex items-center gap-2">{primaryAction}</div>}
        </div>
      </CardContent>
    </Card>
  );
}

export function PageScaffold({ title, subtitle, actions, toolbar, children, testId, contentClassName = 'space-y-4' }) {
  return (
    <section className="space-y-3 animate-fade-in" data-testid={testId}>
      <Card style={{ borderLeft: '4px solid var(--color-primary)' }} data-testid="page-header-card">
        <CardContent className="py-3.5 px-5">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="min-w-0">
              <h1 className="text-lg font-bold tracking-tight" style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}>{title}</h1>
              {subtitle && <p className="text-[11px] text-[var(--color-text-secondary)] mt-0.5 leading-relaxed">{subtitle}</p>}
            </div>
            {actions && (
              <div className="flex items-center gap-4 shrink-0">
                <div className="hidden sm:block w-px h-10 bg-[var(--color-divider)]" />
                <div className="flex flex-wrap items-center gap-2">{actions}</div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      {toolbar || null}
      <div className={contentClassName}>{children}</div>
    </section>
  );
}
