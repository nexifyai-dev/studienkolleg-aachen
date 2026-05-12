import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api-hooks';
import {
  Euro, FileText, Search, Loader2, ExternalLink, Download,
  CheckCircle, Clock, AlertTriangle, RefreshCw, TrendingUp,
} from 'lucide-react';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { Link } from 'react-router-dom';
import { formatDate } from '../../lib/utils';
import { toast } from 'sonner';

function useInvoices() {
  return useQuery({
    queryKey: ['admin', 'invoices'],
    queryFn: () => api.get('/invoices').then(r => r.data),
    staleTime: 30000,
  });
}

const STATUS_LABELS = {
  draft: 'Entwurf',
  sent: 'Versandt',
  paid: 'Bezahlt',
  overdue: 'Überfällig',
  cancelled: 'Storniert',
  pending: 'Ausstehend',
};

const STATUS_STYLES = {
  paid: 'bg-[var(--color-success-bg)] text-[var(--color-success)]',
  sent: 'bg-[var(--color-info-bg,#dbeafe)] text-[var(--color-info,#1e40af)]',
  draft: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]',
  overdue: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]',
  cancelled: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)]',
  pending: 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning,#92400e)]',
};

const fmtEur = v => `${(v || 0).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`;

function KpiCard({ icon: Icon, label, value, sub, accent, testId }) {
  return (
    <Card className="border-l-[3px]" style={{ borderLeftColor: accent || 'var(--color-primary)' }} data-testid={testId}>
      <CardContent className="px-4 py-4">
        <div className="flex items-center gap-1.5 mb-2">
          <Icon size={13} style={{ color: accent || 'var(--color-primary)' }} />
          <span className="text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] font-semibold">{label}</span>
        </div>
        <p className="text-2xl font-extrabold text-[var(--color-text-primary)] tabular-nums leading-none">{value}</p>
        {sub && <p className="text-[11px] text-[var(--color-text-secondary)] mt-1">{sub}</p>}
      </CardContent>
    </Card>
  );
}

export default function AdminFinancePage() {
  const { data: invoices, isLoading, isError, refetch } = useInvoices();
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const list = useMemo(() => invoices || [], [invoices]);

  const stats = useMemo(() => {
    const s = { paid: 0, paidCount: 0, outstanding: 0, outstandingCount: 0, overdueCount: 0, total: list.length };
    list.forEach(inv => {
      const amt = Number(inv.amount || 0);
      const status = inv.status || 'draft';
      if (status === 'paid') { s.paid += amt; s.paidCount += 1; }
      else if (status === 'overdue') { s.outstanding += amt; s.outstandingCount += 1; s.overdueCount += 1; }
      else if (status === 'sent' || status === 'pending') { s.outstanding += amt; s.outstandingCount += 1; }
    });
    return s;
  }, [list]);

  const filtered = useMemo(() => {
    let base = filterStatus === 'all' ? list : list.filter(i => (i.status || 'draft') === filterStatus);
    if (search) {
      const q = search.toLowerCase();
      base = base.filter(i =>
        (i.invoice_number || '').toLowerCase().includes(q) ||
        (i.applicant_name || '').toLowerCase().includes(q) ||
        (i.applicant_email || '').toLowerCase().includes(q) ||
        (i.description || '').toLowerCase().includes(q)
      );
    }
    return base.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
  }, [list, filterStatus, search]);

  const statusCounts = useMemo(() => {
    const c = { all: list.length };
    list.forEach(i => {
      const s = i.status || 'draft';
      c[s] = (c[s] || 0) + 1;
    });
    return c;
  }, [list]);

  const exportCsv = () => {
    if (!filtered.length) return;
    const headers = ['Rechnungsnummer', 'Bewerber', 'E-Mail', 'Beschreibung', 'Betrag', 'Status', 'Erstellt', 'Fällig'];
    const lines = [headers.join(',')];
    filtered.forEach(i => {
      lines.push([
        i.invoice_number || '',
        `"${(i.applicant_name || '').replace(/"/g, '""')}"`,
        i.applicant_email || '',
        `"${(i.description || '').replace(/"/g, '""')}"`,
        i.amount || 0,
        i.status || 'draft',
        i.created_at || '',
        i.due_date || '',
      ].join(','));
    });
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rechnungen_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('CSV exportiert');
  };

  return (
    <PageScaffold
      title="Finanzen & Rechnungen"
      subtitle={`${stats.total} Rechnungen · ${fmtEur(stats.paid)} bezahlt`}
      testId="admin-finance-page"
      actions={
        <div className="flex items-center gap-2">
          <button onClick={() => refetch()} className="w2g-btn-secondary" data-testid="finance-refresh-btn">
            <RefreshCw size={14} /> Aktualisieren
          </button>
          <button onClick={exportCsv} disabled={!filtered.length} className="w2g-btn-primary" data-testid="finance-export-btn">
            <Download size={14} /> CSV
          </button>
        </div>
      }
      toolbar={
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72 shrink-0">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Rechnung / Bewerber suchen..." className="w2g-search pl-9" data-testid="finance-search" />
            </div>
          }
          filters={[
            { key: 'all', label: `Alle (${statusCounts.all || 0})` },
            ...Object.entries(STATUS_LABELS)
              .filter(([k]) => (statusCounts[k] || 0) > 0)
              .map(([k, label]) => ({ key: k, label: `${label} (${statusCounts[k]})` })),
          ].map(tab => (
            <button key={tab.key} onClick={() => setFilterStatus(tab.key)} data-testid={`finance-tab-${tab.key}`}
              className={filterStatus === tab.key ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}>
              {tab.label}
            </button>
          ))}
        />
      }
    >
      {isError && (
        <Card><CardContent className="px-4 py-6 text-center text-sm text-[var(--color-danger)]">
          Rechnungen konnten nicht geladen werden. <button onClick={() => refetch()} className="underline">Erneut versuchen</button>
        </CardContent></Card>
      )}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <KpiCard icon={CheckCircle} label="Bezahlt" value={fmtEur(stats.paid)}
          sub={`${stats.paidCount} Rechnungen`} accent="var(--color-success)" testId="finance-kpi-paid" />
        <KpiCard icon={Clock} label="Offen" value={fmtEur(stats.outstanding)}
          sub={`${stats.outstandingCount} Rechnungen offen`} accent="var(--color-warning)" testId="finance-kpi-outstanding" />
        <KpiCard icon={AlertTriangle} label="Überfällig" value={stats.overdueCount}
          sub={`Rechnungen über Fälligkeit`} accent="var(--color-danger)" testId="finance-kpi-overdue" />
        <KpiCard icon={TrendingUp} label="Ø Rechnung" value={fmtEur(stats.paidCount ? stats.paid / stats.paidCount : 0)}
          sub="Durchschnitt bezahlt" accent="var(--color-primary)" testId="finance-kpi-avg" />
      </div>

      <Card className="p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w2g-table">
            <thead>
              <tr>
                <th>Rechnung</th>
                <th>Bewerber</th>
                <th>Beschreibung</th>
                <th className="text-right">Betrag</th>
                <th>Status</th>
                <th>Erstellt</th>
                <th>Fällig</th>
                <th className="text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={8} className="text-center py-8 text-[var(--color-text-tertiary)] text-sm">
                  <Loader2 size={14} className="animate-spin inline mr-1" /> Laden...
                </td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-8 text-[var(--color-text-tertiary)] text-sm">
                  {search ? 'Keine Treffer' : 'Keine Rechnungen vorhanden'}
                </td></tr>
              ) : filtered.map(i => (
                <tr key={i.id || i._id} data-testid={`invoice-row-${i.id || i._id}`}>
                  <td className="font-medium text-[var(--color-text-primary)]">
                    <div className="flex items-center gap-2">
                      <FileText size={12} className="text-[var(--color-text-tertiary)]" />
                      <span>{i.invoice_number || '–'}</span>
                    </div>
                  </td>
                  <td className="text-xs">
                    <div className="font-medium text-[var(--color-text-primary)]">{i.applicant_name || '–'}</div>
                    <div className="text-[10px] text-[var(--color-text-secondary)]">{i.applicant_email || ''}</div>
                  </td>
                  <td className="text-xs text-[var(--color-text-secondary)] max-w-xs truncate">{i.description || '–'}</td>
                  <td className="text-right font-semibold tabular-nums text-[var(--color-text-primary)]">{fmtEur(i.amount)}</td>
                  <td>
                    <span className={`w2g-badge ${STATUS_STYLES[i.status] || STATUS_STYLES.draft}`}>
                      {STATUS_LABELS[i.status] || i.status}
                    </span>
                  </td>
                  <td className="text-xs text-[var(--color-text-secondary)]">{formatDate(i.created_at)}</td>
                  <td className="text-xs text-[var(--color-text-secondary)]">{i.due_date ? formatDate(i.due_date) : '–'}</td>
                  <td className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      {i.applicant_id && (
                        <Link to={`/staff/applicants/${i.applicant_id}?tab=invoices`}
                          className="w2g-btn-icon" title="Zur Bewerbung"
                          data-testid={`invoice-open-${i.id || i._id}`}>
                          <ExternalLink size={14} />
                        </Link>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </PageScaffold>
  );
}
