import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '../../lib/api-hooks';
import { Loader2, Search, FileCheck2, FileWarning, FileClock, ChevronRight } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

export default function AdminDocumentsPage() {
  const navigate = useNavigate();
  const [search, setSearch] = React.useState('');
  const [filter, setFilter] = React.useState('all');

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'doc-compliance'],
    queryFn: () => api.get('/admin/documents/compliance').then(r => r.data),
    staleTime: 30000,
  });

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-[var(--color-primary)]" />
    </div>
  );

  const stats = data?.stats || {};
  const items = (data?.items || []).filter(r => {
    if (filter === 'complete' && !r.complete) return false;
    if (filter === 'incomplete' && r.complete) return false;
    if (filter === 'pending' && !r.pending_review) return false;
    const term = search.toLowerCase();
    return !term || (r.applicant_name || '').toLowerCase().includes(term) || (r.applicant_email || '').toLowerCase().includes(term);
  });

  return (
    <PageScaffold
      title="Dokumenten-Compliance"
      subtitle={`${stats.total ?? 0} aktive Bewerbungen`}
      testId="admin-documents-page"
      toolbar={
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
            <input type="text" value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Bewerber suchen..." className="w2g-search pl-9" data-testid="admin-documents-search" />
          </div>
          <select value={filter} onChange={e => setFilter(e.target.value)}
            className="text-xs rounded-[var(--radius-sm)] px-2.5 py-2 border border-[var(--color-divider)] bg-[var(--color-surface)] text-[var(--color-text-primary)]"
            data-testid="admin-documents-filter">
            <option value="all">Alle</option>
            <option value="incomplete">Unvollständig</option>
            <option value="complete">Vollständig</option>
            <option value="pending">Prüfung offen</option>
          </select>
        </div>
      }
    >
      <div className="grid grid-cols-3 gap-3 mb-4">
        {[
          { label: 'Vollständig', value: stats.complete ?? 0, icon: FileCheck2, color: 'var(--color-success)' },
          { label: 'Unvollständig', value: stats.incomplete ?? 0, icon: FileWarning, color: 'var(--color-warning)' },
          { label: 'Prüfungen offen', value: stats.pending_review ?? 0, icon: FileClock, color: 'var(--color-info)' },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label} className="p-3.5 flex items-center gap-3">
            <div className="w-8 h-8 rounded-[var(--radius-sm)] flex items-center justify-center" style={{ background: `color-mix(in srgb, ${color} 12%, transparent)` }}>
              <Icon size={14} style={{ color }} />
            </div>
            <div>
              <div className="text-sm font-semibold text-[var(--color-text-primary)]">{value}</div>
              <div className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">{label}</div>
            </div>
          </Card>
        ))}
      </div>

      <Card className="overflow-hidden p-0">
        <table className="w-full" data-testid="admin-documents-table">
          <thead>
            <tr className="border-b border-[var(--color-divider)]">
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Bewerber</th>
              <th className="text-center text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-2 py-2.5">Pflicht-Docs</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5 hidden md:table-cell">Fehlend</th>
              <th className="text-center text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-2 py-2.5 hidden sm:table-cell">Prüfung offen</th>
              <th className="px-4 py-2.5 w-8"></th>
            </tr>
          </thead>
          <tbody>
            {items.map(r => (
              <tr key={r.application_id}
                className="border-b border-[var(--color-divider-subtle)] hover:bg-[var(--color-surface-sunken)] transition-colors cursor-pointer"
                onClick={() => navigate(`/admin/cases/${r.application_id}`)}
                data-testid={`doc-compliance-row-${r.application_id}`}>
                <td className="px-4 py-2.5">
                  <div className="text-xs font-medium text-[var(--color-text-primary)]">{r.applicant_name}</div>
                  <div className="text-[10px] text-[var(--color-text-tertiary)]">{r.applicant_email}</div>
                </td>
                <td className="px-2 py-2.5 text-center">
                  <span className={`text-xs font-semibold ${r.complete ? 'text-[var(--color-success)]' : 'text-[var(--color-warning)]'}`}>
                    {r.total_present}/{r.total_required}
                  </span>
                </td>
                <td className="px-4 py-2.5 hidden md:table-cell">
                  <div className="flex flex-wrap gap-1">
                    {r.missing_labels.length === 0 ? (
                      <span className="text-[10px] text-[var(--color-success)]">Vollständig</span>
                    ) : r.missing_labels.map(l => (
                      <span key={l} className="inline-flex px-1.5 py-0.5 text-[9px] rounded-[var(--radius-full)] bg-[var(--color-warning-bg)] text-[var(--color-warning)]">{l}</span>
                    ))}
                  </div>
                </td>
                <td className="px-2 py-2.5 text-center hidden sm:table-cell">
                  {r.pending_review > 0 ? (
                    <span className="inline-flex px-2 py-0.5 text-[10px] font-medium rounded-[var(--radius-full)] bg-[var(--color-info-bg)] text-[var(--color-info)]">{r.pending_review}</span>
                  ) : <span className="text-[10px] text-[var(--color-text-tertiary)]">—</span>}
                </td>
                <td className="px-4 py-2.5"><ChevronRight size={12} className="text-[var(--color-text-tertiary)]" /></td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={5} className="text-center py-8 text-xs text-[var(--color-text-tertiary)]">Keine Ergebnisse</td></tr>
            )}
          </tbody>
        </table>
      </Card>
    </PageScaffold>
  );
}
