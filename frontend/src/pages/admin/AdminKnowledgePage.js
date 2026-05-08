import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, Plus, Edit3, AlertTriangle, CheckCircle, Clock, X, Save, RotateCcw, Layers, ShieldCheck, ShieldAlert, HelpCircle, BarChart3, ArrowUpDown } from 'lucide-react';
import { toast } from 'sonner';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { getLang } from '../../lib/utils';
import { API } from '../../lib/apiBase';

/* ─── Konstanten ──────────────────────────────────────────────── */
const CATEGORY_CONFIG = {
  'H+':       { label: 'H+ (Hohe Anerkennung)', color: 'text-[var(--color-success)]', bg: 'bg-[var(--color-success-bg)]', border: 'border-[var(--color-success-border)]/60' },
  'H':        { label: 'H (Bedingt anerkennbar)', color: 'text-[var(--color-info)]', bg: 'bg-[var(--color-info-bg)]', border: 'border-[var(--color-info-border)]/60' },
  'H+-':      { label: 'H+- (Eingeschraenkt)', color: 'text-[var(--color-warning)]', bg: 'bg-[var(--color-warning-bg)]', border: 'border-[var(--color-warning-border)]/60' },
  'D':        { label: 'D (Eingeschraenkt)', color: 'text-[var(--color-danger)]', bg: 'bg-[var(--color-danger-bg)]', border: 'border-[var(--color-danger-border)]/60' },
  'pruefen':  { label: 'Pruefen', color: 'text-[var(--color-warning)]', bg: 'bg-[var(--color-warning-bg)]', border: 'border-[var(--color-warning-border)]' },
  'unbekannt':{ label: 'Unbekannt', color: 'text-[var(--color-text-secondary)]', bg: 'bg-[var(--color-surface-sunken)]', border: 'border-[var(--color-divider)]/60' },
};
const STATUS_CONFIG = {
  verified:  { label: 'Verifiziert', color: 'text-[var(--color-success)]', bg: 'bg-[var(--color-success-bg)]', icon: CheckCircle },
  in_review: { label: 'In Pruefung', color: 'text-[var(--color-warning)]', bg: 'bg-[var(--color-warning-bg)]', icon: Clock },
  draft:     { label: 'Entwurf', color: 'text-[var(--color-text-secondary)]', bg: 'bg-[var(--color-surface-sunken)]', icon: Edit3 },
  outdated:  { label: 'Veraltet', color: 'text-[var(--color-warning)]', bg: 'bg-[var(--color-warning-bg)]', icon: AlertTriangle },
  locked:    { label: 'Gesperrt', color: 'text-[var(--color-danger)]', bg: 'bg-[var(--color-danger-bg)]', icon: ShieldAlert },
};
const CONFIDENCE_CONFIG = {
  high:    { label: 'Hoch', color: 'text-[var(--color-success)]', bg: 'bg-[var(--color-success-bg)]' },
  medium:  { label: 'Mittel', color: 'text-[var(--color-warning)]', bg: 'bg-[var(--color-warning-bg)]' },
  low:     { label: 'Niedrig', color: 'text-[var(--color-danger)]', bg: 'bg-[var(--color-danger-bg)]' },
  unknown: { label: 'Unbekannt', color: 'text-[var(--color-text-secondary)]', bg: 'bg-[var(--color-surface-sunken)]' },
};
const QUEUE_STATUS = {
  open:        { label: 'Offen', color: 'text-[var(--color-warning)]', bg: 'bg-[var(--color-warning-bg)]' },
  in_progress: { label: 'In Bearbeitung', color: 'text-[var(--color-info)]', bg: 'bg-[var(--color-info-bg)]' },
  resolved:    { label: 'Geloest', color: 'text-[var(--color-success)]', bg: 'bg-[var(--color-success-bg)]' },
  escalated:   { label: 'Eskaliert', color: 'text-[var(--color-danger)]', bg: 'bg-[var(--color-danger-bg)]' },
};

/* ─── API-Helfer ──────────────────────────────────────────────── */
async function apiFetch(path, opts = {}) {
  const res = await fetch(`${API}${path}`, { credentials: 'include', ...opts, headers: { 'Content-Type': 'application/json', ...opts.headers } });
  if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || `HTTP ${res.status}`); }
  return res.json();
}

/* ─── Badge-Komponente ────────────────────────────────────────── */
function Badge({ config }) {
  return <span className={`w2g-status text-[11px] font-semibold ${config.bg} ${config.color} ${config.border || ''}`}>{config.label}</span>;
}

/* ═══════ DASHBOARD TAB ═══════════════════════════════════════════ */
function DashboardTab({ stats, onNavigate }) {
  const cards = [
    { label: 'Aktive Mappings', value: stats.total, icon: Layers },
    { label: 'Verifiziert', value: stats.verified, icon: ShieldCheck },
    { label: 'In Pruefung', value: stats.in_review, icon: Clock },
    { label: 'Sonderfaelle', value: stats.special_cases, icon: AlertTriangle },
    { label: 'Wissensluecken', value: stats.unknown, icon: HelpCircle, action: () => onNavigate('gaps') },
    { label: 'Review Queue', value: stats.queue_open, icon: BarChart3, action: () => onNavigate('queue') },
  ];

  return (
    <div data-testid="anabin-dashboard" className="space-y-6">
      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {cards.map((c, i) => (
          <button key={i} onClick={c.action} data-testid={`stat-card-${i}`}>
            <Card className="text-left group cursor-pointer hover:shadow-[var(--shadow-e2)] transition-shadow border-l-[3px] border-l-[var(--color-primary)]">
              <CardContent className="px-4 py-3">
                <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center mb-3">
                  <c.icon size={15} className="text-[var(--color-primary)]" />
                </div>
                <p className="w2g-stat-value tabular-nums">{c.value}</p>
                <p className="w2g-stat-label">{c.label}</p>
              </CardContent>
            </Card>
          </button>
        ))}
      </div>

      {/* Category Distribution + Recent Changes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="w2g-card">
          <h3 className="w2g-section-heading mb-4">Kategorieverteilung</h3>
          <div className="space-y-3">
            {Object.entries(stats.categories || {}).map(([cat, count]) => {
              const config = CATEGORY_CONFIG[cat] || CATEGORY_CONFIG.unbekannt;
              const pct = stats.total ? Math.round((count / stats.total) * 100) : 0;
              return (
                <div key={cat} className="flex items-center gap-3">
                  <span className={`text-xs font-semibold w-20 ${config.color}`}>{cat}</span>
                  <div className="flex-1 bg-[var(--color-surface-sunken)] rounded-full h-2.5 overflow-hidden">
                    <div className={`h-full rounded-full`}
                      style={{ width: `${pct}%`, backgroundColor: cat === 'H+' ? 'var(--color-success)' : cat === 'H' ? 'var(--color-info)' : cat === 'D' ? 'var(--color-danger)' : 'var(--color-text-tertiary)' }} />
                  </div>
                  <span className="text-xs text-[var(--color-text-secondary)] w-16 text-right">{count} ({pct}%)</span>
                </div>
              );
            })}
          </div>
        </div>
        <div className="w2g-card">
          <h3 className="w2g-section-heading mb-4">Zuletzt geaendert</h3>
          <div className="space-y-2">
            {(stats.recent_changes || []).map((r, i) => (
              <div key={i} className="flex items-center justify-between p-2.5 rounded-[var(--radius-md)] bg-[var(--color-surface-elevated)]/60 border border-[var(--color-divider-subtle)]">
                <div>
                  <span className="text-sm font-medium text-[var(--color-text-primary)]">{r.country}</span>
                  {r.degree_type && r.degree_type !== 'Allgemein' && <span className="text-xs text-[var(--color-text-tertiary)] ml-2">{r.degree_type}</span>}
                </div>
                <Badge config={CATEGORY_CONFIG[r.category] || CATEGORY_CONFIG.unbekannt} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-3">
        <button onClick={() => onNavigate('entries')} data-testid="quick-action-all-entries" className="w2g-btn-secondary text-sm rounded-[var(--radius-md)] px-4 py-2.5"><Layers size={14} /> Alle Eintraege</button>
        <button onClick={() => onNavigate('queue')} data-testid="quick-action-review-queue" className="w2g-btn-secondary text-sm rounded-[var(--radius-md)] px-4 py-2.5"><Clock size={14} /> Review Queue ({stats.queue_open})</button>
        <button onClick={() => onNavigate('gaps')} data-testid="quick-action-knowledge-gaps" className="w2g-btn-secondary text-sm rounded-[var(--radius-md)] px-4 py-2.5"><AlertTriangle size={14} /> Wissensluecken ({stats.unknown})</button>
        <button onClick={() => onNavigate('create')} data-testid="quick-action-new-entry" className="w2g-btn-primary text-sm rounded-[var(--radius-md)] px-4 py-2.5"><Plus size={14} /> Neuer Eintrag</button>
      </div>
    </div>
  );
}

/* ═══════ ENTRIES TABLE TAB ═══════════════════════════════════════ */
function EntriesTab({ onEdit, onNavigate }) {
  const [entries, setEntries] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterCat, setFilterCat] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterConf, setFilterConf] = useState('');
  const [filterSpecial] = useState('');
  const [sortBy, setSortBy] = useState('country');
  const [sortDir, setSortDir] = useState(1);
  const [selected, setSelected] = useState(new Set());
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 25;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set('q', search);
      if (filterCat) params.set('category', filterCat);
      if (filterStatus) params.set('status', filterStatus);
      if (filterConf) params.set('confidence', filterConf);
      if (filterSpecial) params.set('special_case', filterSpecial);
      params.set('sort_by', sortBy);
      params.set('sort_dir', sortDir);
      params.set('skip', page * PAGE_SIZE);
      params.set('limit', PAGE_SIZE);
      const data = await apiFetch(`/api/anabin/entries?${params}`);
      setEntries(data.entries || []);
      setTotal(data.total || 0);
    } catch (err) { toast.error(err.message); }
    finally { setLoading(false); }
  }, [search, filterCat, filterStatus, filterConf, filterSpecial, sortBy, sortDir, page]);

  useEffect(() => { load(); }, [load]);

  const toggleSort = (field) => {
    if (sortBy === field) setSortDir(d => d * -1);
    else { setSortBy(field); setSortDir(1); }
  };

  const toggleAll = () => {
    if (selected.size === entries.length) setSelected(new Set());
    else setSelected(new Set(entries.map(e => e.id)));
  };

  const handleBulkAction = async (action) => {
    if (selected.size === 0) return;
    try {
      await apiFetch('/api/anabin/bulk-update', {
        method: 'POST',
        body: JSON.stringify({ ids: [...selected], update: action }),
      });
      toast.success(`${selected.size} Eintraege aktualisiert`);
      setSelected(new Set());
      load();
    } catch (err) { toast.error(err.message); }
  };

  const SortHeader = ({ field, children }) => (
    <button onClick={() => toggleSort(field)} className="flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)] transition-colors">
      {children} <ArrowUpDown size={10} className={sortBy === field ? 'text-[var(--color-primary)]' : 'text-[var(--color-text-tertiary)]'} />
    </button>
  );

  return (
    <div data-testid="anabin-entries-tab" className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-col md:flex-row gap-3 items-start md:items-center justify-between p-4 rounded-[var(--radius-md)] border border-[var(--color-divider)] shadow-[var(--shadow-e4)]" style={{ background: 'var(--color-surface-elevated)', boxShadow: 'var(--shadow-e1)' }}>
        <div className="flex items-center gap-2 flex-1 w-full md:w-auto">
          <div className="relative flex-1 max-w-md">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
            <input data-testid="search-input" value={search} onChange={e => { setSearch(e.target.value); setPage(0); }}
              placeholder="Land, Abschluss oder Stichwort suchen..."
              className="w-full pl-9 pr-3 py-2.5 text-sm rounded-[var(--radius-md)] border border-[var(--color-divider)] bg-white focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 focus:border-[var(--color-primary)]/40" />
          </div>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <select data-testid="filter-category" value={filterCat} onChange={e => { setFilterCat(e.target.value); setPage(0); }}
            className="text-xs px-3 py-2 rounded-[var(--radius-md)] border border-[var(--color-divider)] bg-white">
            <option value="">Alle Kategorien</option>
            {Object.entries(CATEGORY_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
          <select data-testid="filter-status" value={filterStatus} onChange={e => { setFilterStatus(e.target.value); setPage(0); }}
            className="text-xs px-3 py-2 rounded-[var(--radius-md)] border border-[var(--color-divider)] bg-white">
            <option value="">Alle Status</option>
            {Object.entries(STATUS_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
          <select data-testid="filter-confidence" value={filterConf} onChange={e => { setFilterConf(e.target.value); setPage(0); }}
            className="text-xs px-3 py-2 rounded-[var(--radius-md)] border border-[var(--color-divider)] bg-white">
            <option value="">Alle Konfidenz</option>
            {Object.entries(CONFIDENCE_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
          <button onClick={() => onNavigate('create')} data-testid="new-entry-btn" className="w2g-btn-primary text-xs rounded-[var(--radius-md)] px-4 py-2.5">
            <Plus size={13} /> Neu
          </button>
        </div>
      </div>

      {/* Bulk Actions */}
      {selected.size > 0 && (
        <div className="flex items-center gap-3 p-3 rounded-[var(--radius-md)] bg-[var(--color-info-bg)] border border-[var(--color-info-border)]/40">
          <span className="text-xs font-semibold text-[var(--color-info)]">{selected.size} ausgewaehlt</span>
          <button onClick={() => handleBulkAction({ status: 'verified' })} className="text-xs text-[var(--color-success)] font-medium px-2.5 py-1 rounded-[var(--radius-md)] bg-[var(--color-success-bg)] hover:bg-[var(--color-success-bg)]">Verifizieren</button>
          <button onClick={() => handleBulkAction({ status: 'in_review' })} className="text-xs text-[var(--color-warning)] font-medium px-2.5 py-1 rounded-[var(--radius-md)] bg-[var(--color-warning-bg)] hover:bg-[var(--color-warning-bg)]">Zur Pruefung</button>
          <button onClick={() => setSelected(new Set())} className="text-xs text-[var(--color-text-secondary)] ml-auto"><X size={14} /></button>
        </div>
      )}

      {/* Table */}
      <div className="w2g-card p-0 overflow-hidden" style={{ boxShadow: 'var(--shadow-e2)' }}>
        {loading ? (
          <div className="p-12 text-center">
            <div className="w-8 h-8 border-2 border-[var(--color-divider)] border-t-[var(--color-primary)] rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-[var(--color-text-tertiary)]">Wissensbasis wird geladen...</p>
          </div>
        ) : entries.length === 0 ? (
          <div className="p-12 text-center">
            <Search size={32} className="text-[var(--color-accent)] mx-auto mb-3" />
            <p className="text-sm font-semibold text-[var(--color-text-secondary)] mb-1">Keine Eintraege gefunden</p>
            <p className="text-xs text-[var(--color-text-tertiary)]">Passe deine Suche oder Filter an, oder erstelle einen neuen Eintrag.</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full" data-testid="entries-table">
                <thead>
                  <tr className="border-b border-[var(--color-divider-subtle)] bg-[var(--color-surface-elevated)]/80">
                    <th className="w-10 px-4 py-3"><input type="checkbox" checked={selected.size === entries.length && entries.length > 0} onChange={toggleAll} className="rounded" /></th>
                    <th className="px-4 py-3 text-left"><SortHeader field="country">Land</SortHeader></th>
                    <th className="px-4 py-3 text-left"><span className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">Abschluss</span></th>
                    <th className="px-4 py-3 text-left"><SortHeader field="category">Kategorie</SortHeader></th>
                    <th className="px-4 py-3 text-left"><SortHeader field="status">Status</SortHeader></th>
                    <th className="px-4 py-3 text-left"><SortHeader field="confidence">Konfidenz</SortHeader></th>
                    <th className="px-4 py-3 text-left"><span className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">Flags</span></th>
                    <th className="px-4 py-3 w-20" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--color-divider-subtle)]">
                  {entries.map(entry => {
                    const catCfg = CATEGORY_CONFIG[entry.category] || CATEGORY_CONFIG.unbekannt;
                    const stCfg = STATUS_CONFIG[entry.status] || STATUS_CONFIG.draft;
                    const confCfg = CONFIDENCE_CONFIG[entry.confidence] || CONFIDENCE_CONFIG.unknown;
                    const StIcon = stCfg.icon;
                    return (
                      <tr key={entry.id} data-testid={`entry-row-${entry.id}`} className="hover:bg-[var(--color-surface-elevated)] transition-colors group">
                        <td className="px-4 py-3"><input type="checkbox" checked={selected.has(entry.id)} onChange={() => { const s = new Set(selected); s.has(entry.id) ? s.delete(entry.id) : s.add(entry.id); setSelected(s); }} className="rounded" /></td>
                        <td className="px-4 py-3"><span className="text-sm font-semibold text-[var(--color-text-primary)]">{entry.country}</span></td>
                        <td className="px-4 py-3"><span className="text-sm text-[var(--color-text-secondary)]">{entry.degree_type || 'Allgemein'}</span></td>
                        <td className="px-4 py-3"><Badge config={catCfg} /></td>
                        <td className="px-4 py-3"><span className={`inline-flex items-center gap-1 text-[11px] font-medium ${stCfg.color}`}><StIcon size={12} />{stCfg.label}</span></td>
                        <td className="px-4 py-3"><Badge config={confCfg} /></td>
                        <td className="px-4 py-3">
                          {entry.is_special_case && <span className="text-[10px] font-bold text-[var(--color-warning)] bg-[var(--color-warning-bg)] px-2 py-0.5 border border-[var(--color-warning-border)]">SONDERFALL</span>}
                          {entry.requires_staff_decision && <span className="text-[10px] font-bold text-[var(--color-info)] bg-[var(--color-info-bg)] px-2 py-0.5 border border-[var(--color-info-border)] ml-1">STAFF</span>}
                        </td>
                        <td className="px-4 py-3">
                          <button onClick={() => onEdit(entry)} data-testid={`edit-${entry.id}`} className="opacity-0 group-hover:opacity-100 transition-opacity text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)] p-1.5 rounded-[var(--radius-md)] hover:bg-[var(--color-surface-sunken)]">
                            <Edit3 size={14} />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {/* Pagination */}
            <div className="flex items-center justify-between px-4 py-3 border-t border-[var(--color-divider-subtle)] bg-[var(--color-surface-elevated)]">
              <span className="text-xs text-[var(--color-text-tertiary)]">{total} Eintraege gesamt</span>
              <div className="flex items-center gap-2">
                <button disabled={page === 0} onClick={() => setPage(p => p - 1)} className="text-xs px-3 py-1.5 rounded-[var(--radius-md)] border border-[var(--color-divider)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-sunken)] disabled:opacity-40">Zurueck</button>
                <span className="text-xs text-[var(--color-text-secondary)]">Seite {page + 1} von {Math.ceil(total / PAGE_SIZE) || 1}</span>
                <button disabled={(page + 1) * PAGE_SIZE >= total} onClick={() => setPage(p => p + 1)} className="text-xs px-3 py-1.5 rounded-[var(--radius-md)] border border-[var(--color-divider)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-sunken)] disabled:opacity-40">Weiter</button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* ═══════ ENTRY EDITOR (Create/Edit) ═══════════════════════════════ */
function EntryEditor({ entry, onSave, onCancel }) {
  const isNew = !entry?.id;
  const [form, setForm] = useState({
    country: entry?.country || '',
    degree_type: entry?.degree_type || 'Allgemein',
    degree_variants: (entry?.degree_variants || []).join(', '),
    category: entry?.category || 'pruefen',
    confidence: entry?.confidence || 'unknown',
    status: entry?.status || 'draft',
    is_special_case: entry?.is_special_case || false,
    requires_staff_decision: entry?.requires_staff_decision || false,
    notes: entry?.notes || '',
    staff_note: entry?.staff_note || '',
    source: entry?.source || 'staff_manual',
    source_url: entry?.source_url || '',
    operational_classification: entry?.operational_classification || '',
    standard_response: entry?.standard_response || '',
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!form.country.trim()) { toast.error('Land ist erforderlich'); return; }
    setSaving(true);
    try {
      const payload = { ...form, degree_variants: form.degree_variants.split(',').map(s => s.trim()).filter(Boolean) };
      if (isNew) {
        await apiFetch('/api/anabin/entries', { method: 'POST', body: JSON.stringify(payload) });
        toast.success('Eintrag erstellt');
      } else {
        await apiFetch(`/api/anabin/entries/${entry.id}`, { method: 'PUT', body: JSON.stringify(payload) });
        toast.success('Eintrag aktualisiert');
      }
      onSave();
    } catch (err) { toast.error(err.message); }
    finally { setSaving(false); }
  };

  const Field = ({ label, children, span = 1 }) => (
    <div className={span === 2 ? 'md:col-span-2' : ''}>
      <label className="block text-[11px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">{label}</label>
      {children}
    </div>
  );
  const inputCls = "w-full px-3.5 py-2.5 text-sm rounded-[var(--radius-md)] border border-[var(--color-divider)] bg-white focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 focus:border-[var(--color-primary)]/40 transition-colors";
  const selectCls = inputCls;

  return (
    <div data-testid="entry-editor" className="w2g-card" style={{ boxShadow: 'var(--shadow-e2)' }}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold" style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}>
            {isNew ? 'Neuer Wissenseintrag' : `Bearbeiten: ${entry.country}`}
          </h3>
          <p className="text-xs text-[var(--color-text-tertiary)] mt-0.5">{isNew ? 'Neues Mapping in die Wissensbasis aufnehmen' : `Version ${entry.version || 1} · Zuletzt geaendert: ${entry.updated_at ? new Date(entry.updated_at).toLocaleDateString('de-DE') : '–'}`}</p>
        </div>
        <button onClick={onCancel} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)] p-2 rounded-[var(--radius-md)] hover:bg-[var(--color-surface-sunken)] transition-colors"><X size={18} /></button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <Field label="Land"><input data-testid="field-country" value={form.country} onChange={e => setForm(f => ({ ...f, country: e.target.value }))} className={inputCls} placeholder="z.B. Iran" /></Field>
        <Field label="Abschlusstyp"><input data-testid="field-degree-type" value={form.degree_type} onChange={e => setForm(f => ({ ...f, degree_type: e.target.value }))} className={inputCls} placeholder="z.B. Bachelor, Diplom" /></Field>
        <Field label="Varianten / Synonyme" span={2}><input data-testid="field-variants" value={form.degree_variants} onChange={e => setForm(f => ({ ...f, degree_variants: e.target.value }))} className={inputCls} placeholder="Karshenasi, Licence (kommagetrennt)" /></Field>
        <Field label="Kategorie">
          <select data-testid="field-category" value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))} className={selectCls}>
            {Object.entries(CATEGORY_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
        </Field>
        <Field label="Konfidenz">
          <select data-testid="field-confidence" value={form.confidence} onChange={e => setForm(f => ({ ...f, confidence: e.target.value }))} className={selectCls}>
            {Object.entries(CONFIDENCE_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
        </Field>
        <Field label="Status">
          <select data-testid="field-status" value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))} className={selectCls}>
            {Object.entries(STATUS_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
        </Field>
        <Field label="Quelle">
          <select data-testid="field-source" value={form.source} onChange={e => setForm(f => ({ ...f, source: e.target.value }))} className={selectCls}>
            <option value="staff_manual">Staff (manuell)</option>
            <option value="anabin_seed">Anabin Seed</option>
            <option value="ai_research">KI-Recherche</option>
            <option value="auto_flagged">Auto-geflaggt</option>
          </select>
        </Field>
        <Field label="Quell-URL / Referenz" span={2}><input data-testid="field-source-url" value={form.source_url} onChange={e => setForm(f => ({ ...f, source_url: e.target.value }))} className={inputCls} placeholder="https://anabin.kmk.org/..." /></Field>
        <Field label="Operative Einstufung" span={2}><input data-testid="field-classification" value={form.operational_classification} onChange={e => setForm(f => ({ ...f, operational_classification: e.target.value }))} className={inputCls} placeholder="z.B. bedingt_anerkennbar, vollstaendig, abgelehnt" /></Field>
        <Field label="Notizen" span={2}><textarea data-testid="field-notes" value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} rows={2} className={inputCls} placeholder="Allgemeine Hinweise zum Eintrag" /></Field>
        <Field label="Staff-Hinweis" span={2}><textarea data-testid="field-staff-note" value={form.staff_note} onChange={e => setForm(f => ({ ...f, staff_note: e.target.value }))} rows={2} className={inputCls} placeholder="Interner Hinweis fuer Staff-Bearbeitung" /></Field>
        <Field label="Standard-Antworttext" span={2}><textarea data-testid="field-standard-response" value={form.standard_response} onChange={e => setForm(f => ({ ...f, standard_response: e.target.value }))} rows={2} className={inputCls} placeholder="Vordefinierte Antwort fuer Sonderfaelle" /></Field>
      </div>

      {/* Flags */}
      <div className="flex flex-wrap gap-4 mb-6 p-4 rounded-[var(--radius-md)] bg-[var(--color-surface-elevated)]/80 border border-[var(--color-divider-subtle)]">
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input data-testid="flag-special-case" type="checkbox" checked={form.is_special_case} onChange={e => setForm(f => ({ ...f, is_special_case: e.target.checked }))} className="rounded border-[var(--color-divider)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]" />
          <span className="text-[var(--color-text-primary)]">Sonderfall</span>
        </label>
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input data-testid="flag-staff-decision" type="checkbox" checked={form.requires_staff_decision} onChange={e => setForm(f => ({ ...f, requires_staff_decision: e.target.checked }))} className="rounded border-[var(--color-divider)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]" />
          <span className="text-[var(--color-text-primary)]">Staff-Entscheid zwingend</span>
        </label>
      </div>

      {/* History (edit only) */}
      {!isNew && entry.change_history && entry.change_history.length > 0 && (
        <div className="mb-6 p-4 rounded-[var(--radius-md)] bg-[var(--color-surface-elevated)]/60 border border-[var(--color-divider-subtle)]">
          <h4 className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-2">Aenderungsverlauf</h4>
          <div className="space-y-1.5 max-h-32 overflow-y-auto">
            {entry.change_history.slice(-5).reverse().map((h, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-[var(--color-text-secondary)]">
                <span className="text-[var(--color-text-tertiary)]">{new Date(h.at).toLocaleDateString('de-DE')}</span>
                <span className="font-medium text-[var(--color-text-secondary)]">{h.action}</span>
                <span>durch {h.by}</span>
                {h.fields && <span className="text-[var(--color-text-tertiary)]">({h.fields.join(', ')})</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3 pt-4 border-t border-[var(--color-divider-subtle)]">
        <button onClick={handleSave} disabled={saving} data-testid="save-entry-btn" className="w2g-btn-primary text-sm rounded-[var(--radius-md)] px-6 py-2.5">
          {saving ? <><RotateCcw size={14} className="animate-spin" /> Speichert...</> : <><Save size={14} /> {isNew ? 'Erstellen' : 'Speichern'}</>}
        </button>
        <button onClick={onCancel} className="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] px-4 py-2.5">Abbrechen</button>
      </div>
    </div>
  );
}

/* ═══════ REVIEW QUEUE TAB ═══════════════════════════════════════ */
function ReviewQueueTab({ onNavigate }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');
  const [resolveModal, setResolveModal] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = filterStatus ? `?status=${filterStatus}` : '';
      const data = await apiFetch(`/api/anabin/review-queue${params}`);
      setItems(data.items || []);
      setTotal(data.total || 0);
    } catch (err) { toast.error(err.message); }
    finally { setLoading(false); }
  }, [filterStatus]);

  useEffect(() => { load(); }, [load]);

  return (
    <div data-testid="review-queue-tab" className="space-y-4">
      <div className="flex items-center justify-between p-4 rounded-[var(--radius-md)] border border-[var(--color-divider)] shadow-[var(--shadow-e4)]" style={{ background: 'var(--color-surface-elevated)', boxShadow: 'var(--shadow-e1)' }}>
        <div className="flex items-center gap-2">
          <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} data-testid="queue-filter-status"
            className="text-xs px-3 py-2 rounded-[var(--radius-md)] border border-[var(--color-divider)] bg-white">
            <option value="">Offene Faelle</option>
            {Object.entries(QUEUE_STATUS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
          <span className="text-xs text-[var(--color-text-tertiary)]">{total} Eintraege</span>
        </div>
        <button onClick={() => onNavigate('create-review')} data-testid="new-review-btn" className="w2g-btn-primary text-xs rounded-[var(--radius-md)] px-4 py-2.5"><Plus size={13} /> Fall melden</button>
      </div>

      {loading ? (
        <div className="w2g-card p-12 text-center">
          <div className="w-8 h-8 border-2 border-[var(--color-divider)] border-t-[var(--color-primary)] rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-[var(--color-text-tertiary)]">Review Queue wird geladen...</p>
        </div>
      ) : items.length === 0 ? (
        <div className="w2g-card p-12 text-center">
          <CheckCircle size={32} className="text-[var(--color-success)] mx-auto mb-3" />
          <p className="text-sm font-semibold text-[var(--color-text-secondary)] mb-1">Keine offenen Review-Faelle</p>
          <p className="text-xs text-[var(--color-text-tertiary)]">Alle Wissensluecken sind derzeit bearbeitet.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map(item => {
            const qst = QUEUE_STATUS[item.status] || QUEUE_STATUS.open;
            return (
              <div key={item.id} data-testid={`queue-item-${item.id}`} className="w2g-card flex flex-col md:flex-row gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-bold text-[var(--color-text-primary)]" style={{ fontFamily: 'var(--font-heading)' }}>{item.country || '?'}</span>
                    {item.degree_type && <span className="text-xs text-[var(--color-text-secondary)]">{item.degree_type}</span>}
                    <Badge config={qst} />
                    {item.priority && <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${item.priority === 'critical' ? 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border border-[var(--color-danger-border)]/60' : item.priority === 'high' ? 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning-border)]' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>{item.priority.toUpperCase()}</span>}
                  </div>
                  <p className="text-xs text-[var(--color-text-secondary)] mb-1">{item.reason_label || item.reason}</p>
                  {item.applicant_name && <p className="text-xs text-[var(--color-text-tertiary)]">Bewerber: {item.applicant_name}</p>}
                  {item.next_action && <p className="text-xs text-[var(--color-info)] mt-1 font-medium">{item.next_action}</p>}
                  {item.last_screening_output && item.last_screening_output.suggested_stage && (
                    <p className="text-xs text-[var(--color-text-tertiary)] mt-1">Letzter KI-Vorschlag: <span className="font-medium">{item.last_screening_output.suggested_stage}</span> (Konfidenz: {item.last_screening_output.confidence || '?'})</p>
                  )}
                  {item.resolution && <p className="text-xs text-[var(--color-success)] mt-1 font-medium">Loesung: {item.resolution}</p>}
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {item.status !== 'resolved' && (
                    <>
                      <button onClick={() => setResolveModal(item)} data-testid={`resolve-${item.id}`}
                        className="text-xs font-medium text-[var(--color-success)] bg-[var(--color-success-bg)] hover:bg-[var(--color-success-bg)] px-3 py-2 rounded-[var(--radius-md)] border border-[var(--color-success-border)]/60 transition-colors">
                        <CheckCircle size={12} className="inline mr-1" />Loesen
                      </button>
                      <button onClick={() => apiFetch(`/api/anabin/review-queue/${item.id}`, { method: 'PUT', body: JSON.stringify({ status: 'escalated' }) }).then(() => { toast.success('Eskaliert'); load(); })}
                        className="text-xs font-medium text-[var(--color-danger)] bg-[var(--color-danger-bg)] hover:bg-[var(--color-danger-bg)] px-3 py-2 rounded-[var(--radius-md)] border border-[var(--color-danger-border)]/60 transition-colors">
                        Eskalieren
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Resolve-Dialog mit Feedback-Loop */}
      {resolveModal && (
        <ResolveWithFeedbackModal
          item={resolveModal}
          onClose={() => setResolveModal(null)}
          onResolved={() => { setResolveModal(null); load(); }}
        />
      )}
    </div>
  );
}

/* ═══════ RESOLVE WITH FEEDBACK MODAL ═══════════════════════════════ */
function ResolveWithFeedbackModal({ item, onClose, onResolved }) {
  const [resolving, setResolving] = useState(false);
  const [resolutionNote, setResolutionNote] = useState('Mapping geprueft und akzeptiert');
  const [updateKnowledge, setUpdateKnowledge] = useState(true);
  const [kbForm, setKbForm] = useState({
    category: 'H',
    confidence: 'medium',
    status: 'verified',
    is_special_case: false,
    requires_staff_decision: false,
    notes: `Geloest aus Review-Queue fuer ${item.country}`,
    staff_note: '',
    operational_classification: '',
    standard_response: '',
  });

  const handleResolve = async () => {
    setResolving(true);
    try {
      const payload = {
        resolution_note: resolutionNote,
      };
      if (updateKnowledge) {
        payload.update_knowledge = kbForm;
      }
      await apiFetch(`/api/anabin/review-queue/${item.id}/resolve`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      toast.success(updateKnowledge
        ? 'Queue geloest und Wissensbasis aktualisiert'
        : 'Queue geloest (ohne Wissensbasis-Update)');
      onResolved();
    } catch (err) { toast.error(err.message); }
    finally { setResolving(false); }
  };

  const inputCls = "w-full px-3.5 py-2.5 text-sm rounded-[var(--radius-md)] border border-[var(--color-divider)] bg-white focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 focus:border-[var(--color-primary)]/40";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="resolve-modal">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-[var(--radius-lg)] w-full max-w-xl max-h-[85vh] overflow-y-auto p-6 border border-[var(--color-divider)] shadow-[var(--shadow-e4)]">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-lg font-bold" style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}>
              Queue-Fall loesen
            </h3>
            <p className="text-xs text-[var(--color-text-tertiary)] mt-0.5">{item.country} · {item.degree_type || 'Allgemein'}</p>
          </div>
          <button onClick={onClose} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)] p-2 rounded-[var(--radius-md)] hover:bg-[var(--color-surface-sunken)]"><X size={18} /></button>
        </div>

        {/* Kontext */}
        <div className="p-3 rounded-[var(--radius-md)] bg-[var(--color-surface-elevated)] border border-[var(--color-divider-subtle)] mb-4">
          <p className="text-xs text-[var(--color-text-secondary)] mb-1"><span className="font-semibold">Grund:</span> {item.reason_label || item.reason}</p>
          {item.last_screening_output?.suggested_stage && (
            <p className="text-xs text-[var(--color-text-secondary)]"><span className="font-semibold">KI-Vorschlag:</span> {item.last_screening_output.suggested_stage} (Konfidenz: {item.last_screening_output.confidence || '?'})</p>
          )}
        </div>

        {/* Resolution Note */}
        <div className="mb-4">
          <label className="block text-[11px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Loesungshinweis</label>
          <textarea data-testid="resolution-note" value={resolutionNote} onChange={e => setResolutionNote(e.target.value)}
            rows={2} className={inputCls} placeholder="Beschreibung der Loesung..." />
        </div>

        {/* Feedback Toggle */}
        <div className="mb-4 p-3 rounded-[var(--radius-md)] bg-[var(--color-info-bg)]/50 border border-[var(--color-info-border)]/40">
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input data-testid="update-knowledge-toggle" type="checkbox" checked={updateKnowledge}
              onChange={e => setUpdateKnowledge(e.target.checked)}
              className="rounded border-[var(--color-divider)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]" />
            <span className="font-medium text-[var(--color-text-primary)]">Wissensbasis aktualisieren (Feedback-Loop)</span>
          </label>
          <p className="text-[10px] text-[var(--color-text-secondary)] mt-1 ml-6">Aktualisiert die Anabin-Wissensbasis fuer zukuenftige Screenings dieses Landes</p>
        </div>

        {/* Knowledge Base Form */}
        {updateKnowledge && (
          <div className="grid grid-cols-2 gap-3 mb-5 p-4 rounded-[var(--radius-md)] border border-[var(--color-info-border)]/40 bg-white">
            <div>
              <label className="block text-[10px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">Kategorie</label>
              <select data-testid="kb-category" value={kbForm.category} onChange={e => setKbForm(f => ({ ...f, category: e.target.value }))}
                className={inputCls}>
                {Object.entries(CATEGORY_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-[10px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">Konfidenz</label>
              <select data-testid="kb-confidence" value={kbForm.confidence} onChange={e => setKbForm(f => ({ ...f, confidence: e.target.value }))}
                className={inputCls}>
                {Object.entries(CONFIDENCE_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
              </select>
            </div>
            <div className="col-span-2">
              <label className="block text-[10px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">Operative Einstufung</label>
              <input data-testid="kb-classification" value={kbForm.operational_classification}
                onChange={e => setKbForm(f => ({ ...f, operational_classification: e.target.value }))}
                className={inputCls} placeholder="z.B. bedingt_anerkennbar, vollstaendig" />
            </div>
            <div className="col-span-2">
              <label className="block text-[10px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">Staff-Hinweis</label>
              <textarea data-testid="kb-staff-note" value={kbForm.staff_note}
                onChange={e => setKbForm(f => ({ ...f, staff_note: e.target.value }))}
                rows={2} className={inputCls} placeholder="Interner Hinweis fuer zukuenftige Screenings..." />
            </div>
            <div className="col-span-2">
              <label className="block text-[10px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">Notizen</label>
              <textarea data-testid="kb-notes" value={kbForm.notes}
                onChange={e => setKbForm(f => ({ ...f, notes: e.target.value }))}
                rows={2} className={inputCls} />
            </div>
            <label className="flex items-center gap-2 text-xs cursor-pointer">
              <input type="checkbox" checked={kbForm.is_special_case}
                onChange={e => setKbForm(f => ({ ...f, is_special_case: e.target.checked }))}
                className="rounded border-[var(--color-divider)] text-[var(--color-primary)]" />
              <span className="text-[var(--color-text-secondary)]">Sonderfall</span>
            </label>
            <label className="flex items-center gap-2 text-xs cursor-pointer">
              <input type="checkbox" checked={kbForm.requires_staff_decision}
                onChange={e => setKbForm(f => ({ ...f, requires_staff_decision: e.target.checked }))}
                className="rounded border-[var(--color-divider)] text-[var(--color-primary)]" />
              <span className="text-[var(--color-text-secondary)]">Staff-Entscheid noetig</span>
            </label>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-3 pt-4 border-t border-[var(--color-divider-subtle)]">
          <button onClick={handleResolve} disabled={resolving} data-testid="confirm-resolve-btn"
            className="w2g-btn-primary text-sm rounded-[var(--radius-md)] px-6 py-2.5">
            {resolving ? <><RotateCcw size={14} className="animate-spin" /> Wird geloest...</> : <><CheckCircle size={14} /> Fall loesen</>}
          </button>
          <button onClick={onClose} className="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] px-4 py-2.5">Abbrechen</button>
        </div>
      </div>
    </div>
  );
}

/* ═══════ KNOWLEDGE GAPS TAB ═══════════════════════════════════════ */
function KnowledgeGapsTab({ onEdit }) {
  const [gaps, setGaps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const data = await apiFetch('/api/anabin/knowledge-gaps');
        setGaps(data.gaps || []);
      } catch (err) { toast.error(err.message); }
      finally { setLoading(false); }
    })();
  }, []);

  return (
    <div data-testid="knowledge-gaps-tab" className="space-y-4">
      {loading ? (
        <div className="w2g-card p-12 text-center">
          <div className="w-8 h-8 border-2 border-[var(--color-divider)] border-t-[var(--color-primary)] rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-[var(--color-text-tertiary)]">Wissensluecken werden analysiert...</p>
        </div>
      ) : gaps.length === 0 ? (
        <div className="w2g-card p-12 text-center">
          <ShieldCheck size={32} className="text-[var(--color-success)] mx-auto mb-3" />
          <p className="text-sm font-semibold text-[var(--color-text-secondary)] mb-1">Keine Wissensluecken erkannt</p>
          <p className="text-xs text-[var(--color-text-tertiary)]">Alle Eintraege sind entweder verifiziert oder in Pruefung.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {gaps.map(gap => {
            const catCfg = CATEGORY_CONFIG[gap.category] || CATEGORY_CONFIG.unbekannt;
            return (
              <div key={gap.id} data-testid={`gap-${gap.id}`} className="w2g-card flex flex-col md:flex-row items-start gap-4">
                <div className="w-10 h-10 rounded-[var(--radius-md)] bg-[var(--color-primary-muted)] flex items-center justify-center flex-shrink-0">
                  <HelpCircle size={18} className="text-[var(--color-warning)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold text-[var(--color-text-primary)]">{gap.country}</span>
                    {gap.degree_type && gap.degree_type !== 'Allgemein' && <span className="text-xs text-[var(--color-text-secondary)]">{gap.degree_type}</span>}
                    <Badge config={catCfg} />
                    {gap.screening_frequency > 0 && (
                      <span className="text-[10px] font-semibold text-[var(--color-info)] bg-[var(--color-info-bg)] px-2 py-0.5">{gap.screening_frequency}x im Screening</span>
                    )}
                  </div>
                  <p className="text-xs text-[var(--color-text-secondary)]">{gap.notes || 'Kein belastbares Mapping gefunden'}</p>
                  {gap.staff_note && <p className="text-xs text-[var(--color-warning)] mt-1">{gap.staff_note}</p>}
                </div>
                <button onClick={() => onEdit(gap)} data-testid={`fix-gap-${gap.id}`}
                  className="text-xs font-medium px-3 py-2 rounded-[var(--radius-md)] border transition-colors flex-shrink-0" style={{ borderColor: 'var(--color-primary)', color: 'var(--color-primary)' }}>
                  <Edit3 size={12} className="inline mr-1" />Mapping erstellen
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ═══════ HAUPTKOMPONENTE ═══════════════════════════════════════════ */
export default function AdminKnowledgePage() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({ total: 0, verified: 0, in_review: 0, special_cases: 0, unknown: 0, queue_open: 0, categories: {}, recent_changes: [] });
  const [editEntry, setEditEntry] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);

  const loadStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const data = await apiFetch('/api/anabin/stats');
      setStats(data);
    } catch (err) { console.error(err); }
    finally { setStatsLoading(false); }
  }, []);

  useEffect(() => { loadStats(); }, [loadStats]);

  const navigate = (tab) => {
    setEditEntry(null);
    setActiveTab(tab);
    if (tab === 'dashboard') loadStats();
  };

  const handleEdit = (entry) => {
    setEditEntry(entry);
    setActiveTab('edit');
  };

  const handleSaved = () => {
    setEditEntry(null);
    setActiveTab('entries');
    loadStats();
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'entries', label: 'Wissensbasis', icon: Layers },
    { id: 'queue', label: 'Review Queue', icon: Clock, badge: stats.queue_open },
    { id: 'gaps', label: 'Wissensluecken', icon: AlertTriangle, badge: stats.unknown },
  ];

  return (
    <PageScaffold
      title="Anabin-Wissensbasis"
      subtitle="Laender-Mappings, operative Einstufungen und Pruefungsfaelle verwalten"
      testId="admin-knowledge-page"
      contentClassName="space-y-4"
    >
      {/* Tab Navigation */}
      {activeTab !== 'edit' && activeTab !== 'create' && activeTab !== 'create-review' && (
        <div className="w2g-tabs" data-testid="knowledge-tabs">
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button key={tab.id} onClick={() => navigate(tab.id)} data-testid={`tab-${tab.id}`}
                className={isActive ? 'w2g-tab-active' : 'w2g-tab'}>
                <span className="flex items-center gap-2">
                  <Icon size={14} /> {tab.label}
                  {tab.badge > 0 && <span className={`text-[10px] font-bold px-1.5 py-0.5 ${isActive ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`} style={{ borderRadius: 'var(--radius-full)' }}>{tab.badge}</span>}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Tab Content */}
      {statsLoading && activeTab === 'dashboard' ? (
        <div className="w2g-card p-16 text-center">
          <div className="w-10 h-10 border-2 border-[var(--color-divider)] border-t-[var(--color-primary)] rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-[var(--color-text-tertiary)]">Wissensbasis-Dashboard wird geladen...</p>
        </div>
      ) : (
        <>
          {activeTab === 'dashboard' && <DashboardTab stats={stats} onNavigate={navigate} />}
          {activeTab === 'entries' && <EntriesTab onEdit={handleEdit} onNavigate={navigate} />}
          {activeTab === 'queue' && <ReviewQueueTab onNavigate={navigate} />}
          {activeTab === 'gaps' && <KnowledgeGapsTab onEdit={handleEdit} />}
          {(activeTab === 'edit' || activeTab === 'create') && (
            <EntryEditor entry={activeTab === 'create' ? null : editEntry} onSave={handleSaved} onCancel={() => navigate('entries')} />
          )}
          {activeTab === 'create-review' && (
            <CreateReviewItem onSave={() => navigate('queue')} onCancel={() => navigate('queue')} />
          )}
        </>
      )}
    </PageScaffold>
  );
}

/* ═══════ CREATE REVIEW ITEM ═══════════════════════════════════════ */
function CreateReviewItem({ onSave, onCancel }) {
  const [form, setForm] = useState({ country: '', degree_type: '', reason_label: '', priority: 'medium', next_action: 'Mapping pruefen und operative Einstufung vornehmen' });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!form.country.trim()) { toast.error('Land ist erforderlich'); return; }
    setSaving(true);
    try {
      await apiFetch('/api/anabin/review-queue', { method: 'POST', body: JSON.stringify({ ...form, reason: 'manual_review' }) });
      toast.success('Review-Fall gemeldet');
      onSave();
    } catch (err) { toast.error(err.message); }
    finally { setSaving(false); }
  };

  const inputCls = "w-full px-3.5 py-2.5 text-sm rounded-[var(--radius-md)] border border-[var(--color-divider)] bg-white focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 focus:border-[var(--color-primary)]/40";
  return (
    <div data-testid="create-review-item" className="w2g-card" style={{ boxShadow: 'var(--shadow-e2)' }}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold" style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}>Neuer Review-Fall</h3>
          <p className="text-xs text-[var(--color-text-tertiary)] mt-0.5">Fall zur Wissenspruefung in die Queue melden</p>
        </div>
        <button onClick={onCancel} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)] p-2 rounded-[var(--radius-md)] hover:bg-[var(--color-surface-sunken)]"><X size={18} /></button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div><label className="block text-[11px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Land</label><input data-testid="review-country" value={form.country} onChange={e => setForm(f => ({ ...f, country: e.target.value }))} className={inputCls} placeholder="z.B. Nigeria" /></div>
        <div><label className="block text-[11px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Abschluss</label><input data-testid="review-degree" value={form.degree_type} onChange={e => setForm(f => ({ ...f, degree_type: e.target.value }))} className={inputCls} placeholder="z.B. HND, OND" /></div>
        <div className="md:col-span-2"><label className="block text-[11px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Grund der Unsicherheit</label><input data-testid="review-reason" value={form.reason_label} onChange={e => setForm(f => ({ ...f, reason_label: e.target.value }))} className={inputCls} placeholder="z.B. Abschluss nicht in Anabin gelistet" /></div>
        <div><label className="block text-[11px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Prioritaet</label>
          <select data-testid="review-priority" value={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.value }))} className={inputCls}>
            <option value="critical">Kritisch</option><option value="high">Hoch</option><option value="medium">Mittel</option><option value="low">Niedrig</option>
          </select>
        </div>
        <div><label className="block text-[11px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Naechste Aktion</label><input value={form.next_action} onChange={e => setForm(f => ({ ...f, next_action: e.target.value }))} className={inputCls} /></div>
      </div>
      <div className="flex items-center gap-3">
        <button onClick={handleSave} disabled={saving} data-testid="submit-review-btn" className="w2g-btn-primary text-sm rounded-[var(--radius-md)] px-6 py-2.5">{saving ? 'Wird gemeldet...' : 'Fall melden'}</button>
        <button onClick={onCancel} className="text-sm text-[var(--color-text-secondary)] px-4 py-2.5">Abbrechen</button>
      </div>
    </div>
  );
}
