import React from 'react';
import { FileCog, Layers3, Settings2 } from 'lucide-react';
import { PageScaffold, ToolbarRow } from '../layout/PageScaffold';

const ICONS = { FileCog, Layers3, Settings2 };

export function PortalPlaceholderPage({
  title,
  subtitle,
  testId,
  toolbar,
  sections = [],
  actions,
}) {
  return (
    <PageScaffold title={title} subtitle={subtitle} actions={actions} toolbar={toolbar} testId={testId}>
      <div className="grid gap-4 lg:grid-cols-12">
        {sections.map((section) => {
          const Icon = ICONS[section.icon] || Layers3;
          return (
            <div key={section.title} className={`w2g-card lg:col-span-${section.span || 6}`} data-testid={`${testId}-${section.testId}`}>
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-[var(--radius-lg)] bg-[var(--color-primary)]/8 text-[var(--color-primary)]">
                  <Icon size={18} />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-[var(--color-text-primary)]">{section.title}</h2>
                  <p className="text-sm text-[var(--color-text-secondary)]">{section.subtitle}</p>
                </div>
              </div>
              <div className="space-y-3">
                {(section.items || []).map((item) => (
                  <div key={item.label} className="rounded-[var(--radius-lg)] border border-[var(--color-divider)] bg-[var(--color-surface-elevated)] px-4 py-3" data-testid={`${testId}-${section.testId}-${item.label.toLowerCase().replace(/[^a-z0-9]+/gi, '-')}`}>
                    <p className="text-sm font-semibold text-[var(--color-text-primary)]">{item.label}</p>
                    <p className="text-xs text-[var(--color-text-secondary)]">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </PageScaffold>
  );
}

export { ToolbarRow };
