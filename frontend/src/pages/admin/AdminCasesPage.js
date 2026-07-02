import React from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { api } from '../../lib/api-hooks';
import { Users, Loader2, Search, ChevronRight, UserCheck, UserX, Download, Archive, Flag, ArrowRightCircle, X } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

const STAGES = [
  ['lead_new', 'Neue Anfrage'], ['in_review', 'In Bearbeitung'], ['pending_docs', 'Dokumente ausstehend'],
  ['interview_scheduled', 'Interview geplant'], ['conditional_offer', 'Bedingtes Angebot'],
  ['offer_sent', 'Angebot versendet'], ['enrolled', 'Eingeschrieben'], ['declined', 'Abgelehnt'],
  ['on_hold', 'Pausiert'], ['archived', 'Archiviert'],
];
const STAGE_LABELS = Object.fromEntries(STAGES);

const STAGE_COLORS = {
  lead_new: 'var(--color-accent)', in_review: 'var(--color-primary)', pending_docs: 'var(--color-warning)',
  interview_scheduled: 'var(--color-primary-light)', conditional_offer: 'var(--color-success)',
  offer_sent: 'var(--color-info)', enrolled: 'var(--color-success)', declined: 'var(--color-danger)',
  on_hold: 'var(--color-text-secondary)', archived: 'var(--color-text-tertiary)',
};

function BulkBar({ selected, onDone, onClear }) {
  const [stage, setStage] = React.useState('');
  const [busy, setBusy] = React.useState(false);

  const run = async (action, value) => {
    setBusy(true);
    try {
      const r = await api.post('/applications/bulk-update', { ids: selected, action, value });
      toast.success(`${r.data.updated} Fälle aktualisiert`);
      onDone();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Bulk-Aktion fehlgeschlagen');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex flex-wrap items-center gap-2 px-4 py-2.5 rounded-[var(--radius-md)] bg-[var(--color-primary)] text-white" data-testid="bulk-action-bar">
      <span className="text-xs font-semibold">{selected.length} ausgewählt</span>
      <div className="flex items-center gap-1.5">
        <select value={stage} onChange={e => setStage(e.target.value)} disabled={busy}
          className="text-xs rounded-md px-2 py-1.5 bg-white/10 border border-white/20 text-white [&>option]:text-black"
          data-testid="bulk-stage-select">
          <option value="">Status wählen…</option>
          {STAGES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
        <button onClick={() => stage && run('set_stage', stage)} disabled={busy || !stage}
          className="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-md bg-white/15 hover:bg-white/25 disabled:opacity-40 transition-colors"
          data-testid="bulk-apply-stage-btn">
          {busy ? <Loader2 size={12} className="animate-spin" /> : <ArrowRightCircle size={12} />} Status setzen
        </button>
      </div>
      <button onClick={() => run('set_priority', 'high')} disabled={busy}
        className="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-md bg-white/15 hover:bg-white/25 disabled:opacity-40 transition-colors"
        data-testid="bulk-priority-btn">
        <Flag size={12} /> Hohe Priorität
      </button>
      <button onClick={() => { if (window.confirm(`${selected.length} Fälle archivieren?`)) run('archive'); }} disabled={busy}
        className="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-md bg-white/15 hover:bg-white/25 disabled:opacity-40 transition-colors"
        data-testid="bulk-archive-btn">
        <Archive size={12} /> Archivieren
      </button>
      <button onClick={onClear} className="ml-auto p-1.5 rounded-md hover:bg-white/15 transition-colors" title="Auswahl aufheben" data-testid="bulk-clear-btn">
        <X size={14} />
      </button>
    </div>
  );
}

export default function AdminCasesPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { data: apps, isLoading } = useQuery({
    queryKey: ['admin', 'cases'],
    queryFn: () => api.get('/applications').then(r => r.data),
    staleTime: 30000,
  });
  const [search, setSearch] = React.useState('');
  const [stageFilter, setStageFilter] = React.useState('all');
  const [selected, setSelected] = React.useState([]);

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-[var(--color-primary)]" />
    </div>
  );

  const all = Array.isArray(apps) ? apps : [];
  const filtered = all.filter(a => {
    if (stageFilter !== 'all' && a.current_stage !== stageFilter) return false;
    const term = search.toLowerCase();
    return !term || (a.applicant_name || '').toLowerCase().includes(term) ||
      (a.applicant_email || '').toLowerCase().includes(term) ||
      (a.current_stage || '').toLowerCase().includes(term);
  });

  const toggleAll = () => setSelected(selected.length === filtered.length ? [] : filtered.map(a => a.id));
  const toggle = (id) => setSelected(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);

  const exportCsv = () => {
    const head = ['Name', 'E-Mail', 'Status', 'Kurs', 'Priorität', 'Erstellt'];
    const lines = filtered.map(a => [
      a.applicant_name || '', a.applicant_email || '', STAGE_LABELS[a.current_stage] || a.current_stage || '',
      a.course_type || '', a.priority || '', a.created_at ? new Date(a.created_at).toLocaleDateString('de-DE') : '',
    ].map(v => `"${String(v).replace(/"/g, '""')}"`).join(';'));
    const blob = new Blob(['\uFEFF' + [head.join(';'), ...lines].join('\n')], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const el = document.createElement('a');
    el.href = url; el.download = `faelle_${new Date().toISOString().slice(0, 10)}.csv`;
    el.click(); URL.revokeObjectURL(url);
  };

  return (
    <PageScaffold
      title="Alle Faelle"
      subtitle={`${filtered.length} von ${all.length} Bewerbungen`}
      testId="admin-cases-page"
      toolbar={
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
            <input
              type="text" value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Name, E-Mail oder Status suchen..."
              className="w2g-search pl-9" data-testid="admin-cases-search"
            />
          </div>
          <select value={stageFilter} onChange={e => setStageFilter(e.target.value)}
            className="text-xs rounded-[var(--radius-sm)] px-2.5 py-2 border border-[var(--color-divider)] bg-[var(--color-surface)] text-[var(--color-text-primary)]"
            data-testid="admin-cases-stage-filter">
            <option value="all">Alle Status</option>
            {STAGES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
          <button onClick={exportCsv}
            className="flex items-center gap-1.5 text-xs px-3 py-2 rounded-[var(--radius-sm)] border border-[var(--color-divider)] bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] hover:border-[var(--color-primary)] transition-colors"
            data-testid="admin-cases-export-btn">
            <Download size={13} /> CSV
          </button>
        </div>
      }
    >
      {selected.length > 0 && (
        <div className="mb-3">
          <BulkBar
            selected={selected}
            onClear={() => setSelected([])}
            onDone={() => { setSelected([]); qc.invalidateQueries({ queryKey: ['admin', 'cases'] }); }}
          />
        </div>
      )}
      <Card className="overflow-hidden p-0">
        <table className="w-full" data-testid="admin-cases-table">
          <thead>
            <tr className="border-b border-[var(--color-divider)]">
              <th className="px-4 py-2.5 w-8">
                <input type="checkbox" checked={filtered.length > 0 && selected.length === filtered.length}
                  onChange={toggleAll} className="cursor-pointer accent-[#113655]" data-testid="admin-cases-select-all" />
              </th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Name</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5 hidden sm:table-cell">E-Mail</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Status</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5 hidden md:table-cell">Kurs</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5 hidden md:table-cell">Erstellt</th>
              <th className="px-4 py-2.5 w-8"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(a => (
              <tr key={a.id}
                className="border-b border-[var(--color-divider-subtle)] hover:bg-[var(--color-surface-sunken)] transition-colors cursor-pointer"
                onClick={() => navigate(`/admin/cases/${a.id}`)}
                data-testid={`admin-case-row-${a.id}`}>
                <td className="px-4 py-2.5" onClick={e => e.stopPropagation()}>
                  <input type="checkbox" checked={selected.includes(a.id)} onChange={() => toggle(a.id)}
                    className="cursor-pointer accent-[#113655]" data-testid={`admin-case-check-${a.id}`} />
                </td>
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
                    {STAGE_LABELS[a.current_stage] || (a.current_stage || 'unbekannt').replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="px-4 py-2.5 text-xs text-[var(--color-text-secondary)] hidden md:table-cell">{a.course_type || '—'}</td>
                <td className="px-4 py-2.5 text-xs text-[var(--color-text-tertiary)] hidden md:table-cell">
                  {a.created_at ? new Date(a.created_at).toLocaleDateString('de-DE') : '—'}
                </td>
                <td className="px-4 py-2.5">
                  <ChevronRight size={12} className="text-[var(--color-text-tertiary)]" />
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={7} className="text-center py-8 text-xs text-[var(--color-text-tertiary)]">Keine Ergebnisse</td></tr>
            )}
          </tbody>
        </table>
      </Card>
    </PageScaffold>
  );
}
