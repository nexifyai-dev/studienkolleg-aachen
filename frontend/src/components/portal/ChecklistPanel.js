import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, AlertTriangle, Clock, CheckCircle, User, CreditCard, HelpCircle, GraduationCap } from 'lucide-react';

/* shadcn-Komponenten */
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';

const ICONS = { FileText, AlertTriangle, Clock, CheckCircle, User, CreditCard, HelpCircle, GraduationCap };
const STATUS_STYLES = {
  missing: 'border-[var(--color-danger-border)] bg-[var(--color-danger-bg)]/50',
  action_needed: 'border-[var(--color-warning-border)] bg-[var(--color-warning-bg)]/50',
  in_progress: 'border-[var(--color-divider)] bg-[var(--color-surface-elevated)]',
  done: 'border-[var(--color-success-border)] bg-[var(--color-success-bg)]/30',
};
const ICON_COLORS = {
  missing: 'text-[var(--color-danger)]',
  action_needed: 'text-[var(--color-warning)]',
  in_progress: 'text-[var(--color-text-tertiary)]',
  done: 'text-[var(--color-success)]',
};

export default function ChecklistPanel({ items, lang = 'de' }) {
  if (!items || items.length === 0) {
    return (
      <Card data-testid="checklist-empty">
        <CardContent className="py-8 text-center">
          <CheckCircle size={24} className="text-[var(--color-success)] mx-auto mb-2" />
          <p className="text-sm font-bold text-[var(--color-text-primary)]" style={{ fontFamily: 'var(--font-heading)' }}>
            {lang === 'de' ? 'Checkliste' : 'Checklist'}
          </p>
          <p className="text-xs text-[var(--color-text-secondary)] mt-1">
            {lang === 'de'
              ? 'Aktuell keine offenen Aufgaben. Alles erledigt!'
              : 'No open tasks right now. All done!'}
          </p>
        </CardContent>
      </Card>
    );
  }

  const openItems = items.filter(i => i.status !== 'done');
  const doneItems = items.filter(i => i.status === 'done');

  return (
    <Card data-testid="checklist-panel">
      <CardContent className="pt-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--color-text-tertiary)]">
            {lang === 'de' ? 'Deine Aufgaben' : 'Your Tasks'}
          </p>
          <Badge variant="outline" size="xs">{doneItems.length}/{items.length} {lang === 'de' ? 'erledigt' : 'done'}</Badge>
        </div>

        {/* Offene Aufgaben */}
        <div className="space-y-2">
          {openItems.map(item => {
            const Icon = ICONS[item.icon] || FileText;
            return (
              <Link key={item.key} to={item.path || '#'}
                className={`flex items-center gap-3 p-3 rounded-[var(--radius-sm)] border transition-colors hover:border-[var(--color-primary)]/30 ${STATUS_STYLES[item.status] || ''}`}
                data-testid={`checklist-${item.key}`}>
                <Icon size={16} className={ICON_COLORS[item.status] || 'text-[var(--color-text-tertiary)]'} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-[var(--color-text-primary)] truncate">{item.label}</p>
                  {item.description && <p className="text-[10px] text-[var(--color-text-secondary)] truncate">{item.description}</p>}
                </div>
                {item.priority === 'high' && (
                  <Badge variant="danger" size="xs">{lang === 'de' ? 'Wichtig' : 'Important'}</Badge>
                )}
              </Link>
            );
          })}
        </div>

        {/* Erledigte Aufgaben */}
        {doneItems.length > 0 && (
          <div className="mt-3 pt-3 border-t border-[var(--color-divider-subtle)]">
            <p className="text-[10px] text-[var(--color-text-tertiary)] mb-1.5">
              {lang === 'de' ? 'Erledigt' : 'Completed'} ({doneItems.length})
            </p>
            {doneItems.map(item => (
              <div key={item.key} className="flex items-center gap-2 py-1 text-xs text-[var(--color-text-tertiary)]">
                <CheckCircle size={12} />
                <span className="line-through">{item.label}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
