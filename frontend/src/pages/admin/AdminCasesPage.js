import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api-hooks';
import { Users, Loader2, Search, ChevronRight, UserCheck, UserX } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

function useAllApplications() {
  return useQuery({
    queryKey: ['admin', 'cases'],
    queryFn: () => api.get('/applications').then(r => r.data),
    staleTime: 30000,
  });
}

const STAGE_COLORS = {
  lead_new: 'var(--color-accent)',
  in_review: 'var(--color-primary)',
  pending_docs: 'var(--color-warning)',
  interview_scheduled: 'var(--color-primary-light)',
  conditional_offer: 'var(--color-success)',
  enrolled: 'var(--color-success)',
  declined: 'var(--color-danger)',
  archived: 'var(--color-text-tertiary)',
};

export default function AdminCasesPage() {
  const { data: apps, isLoading } = useAllApplications();
  const [search, setSearch] = React.useState('');

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-[var(--color-primary)]" />
    </div>
  );

  const filtered = (apps || []).filter(a => {
    const term = search.toLowerCase();
    return !term || (a.applicant_name || '').toLowerCase().includes(term) ||
      (a.applicant_email || '').toLowerCase().includes(term) ||
      (a.current_stage || '').toLowerCase().includes(term);
  });

  return (
    <PageScaffold
      title="Alle Faelle"
      subtitle={`${filtered.length} von ${(apps || []).length} Bewerbungen`}
      testId="admin-cases-page"
      toolbar={
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
          <input
            type="text" value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Name, E-Mail oder Status suchen..."
            className="w2g-search pl-9" data-testid="admin-cases-search"
          />
        </div>
      }
    >
      <Card className="overflow-hidden p-0">
        <table className="w-full" data-testid="admin-cases-table">
          <thead>
            <tr className="border-b border-[var(--color-divider)]">
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Name</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5 hidden sm:table-cell">E-Mail</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Status</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5 hidden md:table-cell">Erstellt</th>
              <th className="px-4 py-2.5 w-8"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(a => (
              <tr key={a.id} className="border-b border-[var(--color-divider-subtle)] hover:bg-[var(--color-surface-sunken)] transition-colors">
                <td className="px-4 py-2.5">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-[var(--radius-sm)] flex items-center justify-center bg-[var(--color-primary-muted)]">
                      {a.current_stage === 'enrolled' ? <UserCheck size={12} className="text-[var(--color-success)]" /> :
                       a.current_stage === 'declined' ? <UserX size={12} className="text-[var(--color-danger)]" /> :
                       <Users size={12} className="text-[var(--color-primary)]" />}
                    </div>
                    <span className="text-xs font-medium text-[var(--color-text-primary)]">{a.applicant_name || '—'}</span>
                  </div>
                </td>
                <td className="px-4 py-2.5 text-xs text-[var(--color-text-secondary)] hidden sm:table-cell">{a.applicant_email || '—'}</td>
                <td className="px-4 py-2.5">
                  <span className="inline-flex px-2 py-0.5 text-[10px] font-medium rounded-[var(--radius-full)]"
                    style={{ background: `color-mix(in srgb, ${STAGE_COLORS[a.current_stage] || 'var(--color-text-tertiary)'} 12%, transparent)`, color: STAGE_COLORS[a.current_stage] || 'var(--color-text-tertiary)' }}>
                    {(a.current_stage || 'unknown').replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="px-4 py-2.5 text-xs text-[var(--color-text-tertiary)] hidden md:table-cell">
                  {a.created_at ? new Date(a.created_at).toLocaleDateString('de-DE') : '—'}
                </td>
                <td className="px-4 py-2.5">
                  <ChevronRight size={12} className="text-[var(--color-text-tertiary)]" />
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={5} className="text-center py-8 text-xs text-[var(--color-text-tertiary)]">Keine Ergebnisse</td></tr>
            )}
          </tbody>
        </table>
      </Card>
    </PageScaffold>
  );
}
