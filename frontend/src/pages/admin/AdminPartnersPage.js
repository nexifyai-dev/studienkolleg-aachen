import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api-hooks';
import { Loader2, Search, Link2, Globe } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

function usePartners() {
  return useQuery({
    queryKey: ['admin', 'partners'],
    queryFn: () => api.get('/users?role=affiliate').then(r => r.data).catch(() => []),
    staleTime: 30000,
  });
}

export default function AdminPartnersPage() {
  const { data: partners, isLoading } = usePartners();
  const [search, setSearch] = React.useState('');

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-[var(--color-primary)]" />
    </div>
  );

  const list = (partners || []).filter(p => {
    const term = search.toLowerCase();
    return !term || (p.full_name || '').toLowerCase().includes(term) || (p.email || '').toLowerCase().includes(term);
  });

  return (
    <PageScaffold
      title="Partner-Verwaltung"
      subtitle={`${list.length} registrierte Partner / Affiliates`}
      testId="admin-partners-page"
      toolbar={
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
          <input
            type="text" value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Partner suchen..."
            className="w2g-search pl-9" data-testid="admin-partners-search"
          />
        </div>
      }
    >
      <Card className="overflow-hidden p-0">
        <table className="w-full" data-testid="admin-partners-table">
          <thead>
            <tr className="border-b border-[var(--color-divider)]">
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Partner</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5 hidden sm:table-cell">E-Mail</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Status</th>
            </tr>
          </thead>
          <tbody>
            {list.map(p => (
              <tr key={p.id || p.email} className="border-b border-[var(--color-divider-subtle)] hover:bg-[var(--color-surface-sunken)] transition-colors">
                <td className="px-4 py-2.5">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-[var(--radius-sm)] flex items-center justify-center bg-[var(--color-primary-muted)]">
                      <Globe size={12} className="text-[var(--color-accent)]" />
                    </div>
                    <span className="text-xs font-medium text-[var(--color-text-primary)]">{p.full_name || '\u2014'}</span>
                  </div>
                </td>
                <td className="px-4 py-2.5 text-xs text-[var(--color-text-secondary)] hidden sm:table-cell">{p.email}</td>
                <td className="px-4 py-2.5">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-medium rounded-[var(--radius-full)]
                    ${p.is_active !== false ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]' : 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]'}`}>
                    <Link2 size={9} /> {p.is_active !== false ? 'Aktiv' : 'Inaktiv'}
                  </span>
                </td>
              </tr>
            ))}
            {list.length === 0 && (
              <tr><td colSpan={3} className="text-center py-8 text-xs text-[var(--color-text-tertiary)]">Keine Partner gefunden</td></tr>
            )}
          </tbody>
        </table>
      </Card>
    </PageScaffold>
  );
}
