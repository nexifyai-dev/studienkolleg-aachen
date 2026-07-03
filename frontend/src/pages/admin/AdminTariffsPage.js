import React from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { api } from '../../lib/api-hooks';
import { Loader2, Search, Tag, Plus, Pencil, Archive, RotateCcw, X } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

const CATEGORIES = ['kurs', 'sprache', 'pruefung', 'gebuehr', 'service', 'unterkunft', 'kombi', 'sonstig'];
const CAT_LABELS = { kurs: 'Kurs', sprache: 'Sprache', pruefung: 'Prüfung', gebuehr: 'Gebühr', service: 'Service', unterkunft: 'Unterkunft', kombi: 'Kombi-Paket', sonstig: 'Sonstiges' };
const inputCls = "w-full text-xs rounded-[var(--radius-sm)] px-3 py-2 border border-[var(--color-divider)] bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-primary)]";

function TariffModal({ tariff, onClose, onDone }) {
  const isEdit = !!tariff;
  const [form, setForm] = React.useState({
    code: tariff?.code || '', name: tariff?.name || '', description: tariff?.description || '',
    price: tariff?.price ?? '', currency: tariff?.currency || 'EUR', category: tariff?.category || 'kurs',
  });
  const [busy, setBusy] = React.useState(false);
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const submit = async () => {
    if (!form.code || !form.name) return toast.error('Code und Name sind erforderlich');
    setBusy(true);
    try {
      if (isEdit) await api.put(`/products/${tariff.id}`, { ...form, price: parseFloat(form.price || 0) });
      else await api.post('/products', { ...form, price: parseFloat(form.price || 0) });
      toast.success(isEdit ? 'Tarif aktualisiert' : 'Tarif erstellt');
      onDone(); onClose();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Speichern fehlgeschlagen');
    } finally { setBusy(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" data-testid="tariff-modal" onClick={onClose}>
      <div className="bg-[var(--color-surface)] rounded-[var(--radius-md)] shadow-xl w-full max-w-md p-5" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">{isEdit ? `Tarif bearbeiten – ${tariff.code}` : 'Neuer Tarif'}</h3>
          <button onClick={onClose} className="p-1 rounded hover:bg-[var(--color-surface-sunken)]" data-testid="tariff-modal-close"><X size={16} /></button>
        </div>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">Code *</label>
              <input className={inputCls} value={form.code} onChange={e => set('code', e.target.value.toUpperCase())} data-testid="tariff-code-input" />
            </div>
            <div>
              <label className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">Kategorie</label>
              <select className={inputCls} value={form.category} onChange={e => set('category', e.target.value)} data-testid="tariff-category-select">
                {CATEGORIES.map(c => <option key={c} value={c}>{CAT_LABELS[c]}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">Name *</label>
            <input className={inputCls} value={form.name} onChange={e => set('name', e.target.value)} data-testid="tariff-name-input" />
          </div>
          <div>
            <label className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">Beschreibung</label>
            <textarea className={inputCls} rows={2} value={form.description} onChange={e => set('description', e.target.value)} data-testid="tariff-desc-input" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">Preis</label>
              <input className={inputCls} type="number" min="0" step="0.01" value={form.price} onChange={e => set('price', e.target.value)} data-testid="tariff-price-input" />
            </div>
            <div>
              <label className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">Währung</label>
              <input className={inputCls} value={form.currency} onChange={e => set('currency', e.target.value)} data-testid="tariff-currency-input" />
            </div>
          </div>
          <button onClick={submit} disabled={busy} className="w2g-btn-primary w-full" data-testid="tariff-save-btn">
            {busy ? <Loader2 size={14} className="animate-spin" /> : (isEdit ? 'Speichern' : 'Erstellen')}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function AdminTariffsPage() {
  const qc = useQueryClient();
  const { data: tariffs, isLoading } = useQuery({
    queryKey: ['admin', 'tariffs'],
    queryFn: () => api.get('/products', { params: { include_inactive: true } }).then(r => r.data),
    staleTime: 15000,
  });
  const [search, setSearch] = React.useState('');
  const [catFilter, setCatFilter] = React.useState('all');
  const [showCreate, setShowCreate] = React.useState(false);
  const [editT, setEditT] = React.useState(null);

  const refresh = () => qc.invalidateQueries({ queryKey: ['admin', 'tariffs'] });

  const toggleActive = async (t) => {
    try {
      if (t.is_active) {
        await api.delete(`/products/${t.id}`);
        toast.success(`"${t.name}" archiviert`);
      } else {
        await api.put(`/products/${t.id}`, { is_active: true });
        toast.success(`"${t.name}" reaktiviert`);
      }
      refresh();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Fehler');
    }
  };

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-[var(--color-primary)]" />
    </div>
  );

  const list = (tariffs || []).filter(t => {
    if (catFilter !== 'all' && t.category !== catFilter) return false;
    const term = search.toLowerCase();
    return !term || (t.name || '').toLowerCase().includes(term) || (t.code || '').toLowerCase().includes(term);
  });

  return (
    <PageScaffold
      title="Tarife & Produkte"
      subtitle={`${list.length} Tarife · Preise erscheinen live auf der Website`}
      testId="admin-tariffs-page"
      toolbar={
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
            <input type="text" value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Code oder Name suchen..." className="w2g-search pl-9" data-testid="tariffs-search" />
          </div>
          <select value={catFilter} onChange={e => setCatFilter(e.target.value)}
            className="text-xs rounded-[var(--radius-sm)] px-2.5 py-2 border border-[var(--color-divider)] bg-[var(--color-surface)] text-[var(--color-text-primary)]"
            data-testid="tariffs-category-filter">
            <option value="all">Alle Kategorien</option>
            {CATEGORIES.map(c => <option key={c} value={c}>{CAT_LABELS[c]}</option>)}
          </select>
          <button onClick={() => setShowCreate(true)} className="w2g-btn-primary flex items-center gap-1.5 text-xs" data-testid="tariff-create-btn">
            <Plus size={13} /> Neuer Tarif
          </button>
        </div>
      }
    >
      <Card className="overflow-hidden p-0">
        <table className="w-full" data-testid="admin-tariffs-table">
          <thead>
            <tr className="border-b border-[var(--color-divider)]">
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Code</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Name</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5 hidden md:table-cell">Kategorie</th>
              <th className="text-right text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Preis</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Status</th>
              <th className="text-right text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {list.map(t => (
              <tr key={t.id} className={`border-b border-[var(--color-divider-subtle)] hover:bg-[var(--color-surface-sunken)] transition-colors ${!t.is_active ? 'opacity-50' : ''}`}
                data-testid={`tariff-row-${t.code}`}>
                <td className="px-4 py-2.5">
                  <span className="inline-flex items-center gap-1.5 text-[11px] font-mono font-semibold text-[var(--color-primary)]">
                    <Tag size={11} /> {t.code}
                  </span>
                </td>
                <td className="px-4 py-2.5">
                  <div className="text-xs font-medium text-[var(--color-text-primary)]">{t.name}</div>
                  <div className="text-[10px] text-[var(--color-text-tertiary)] truncate max-w-[280px]">{t.description}</div>
                </td>
                <td className="px-4 py-2.5 hidden md:table-cell">
                  <span className="inline-flex px-2 py-0.5 text-[10px] rounded-[var(--radius-full)] bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]">
                    {CAT_LABELS[t.category] || t.category}
                  </span>
                </td>
                <td className="px-4 py-2.5 text-right text-xs font-semibold text-[var(--color-text-primary)]">
                  {Number(t.price).toLocaleString('de-DE')} {t.currency === 'EUR' ? '€' : t.currency}
                </td>
                <td className="px-4 py-2.5">
                  <span className={`inline-flex px-2 py-0.5 text-[10px] font-medium rounded-[var(--radius-full)]
                    ${t.is_active ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)]'}`}>
                    {t.is_active ? 'Aktiv' : 'Archiviert'}
                  </span>
                </td>
                <td className="px-4 py-2.5">
                  <div className="flex items-center justify-end gap-1">
                    <button onClick={() => setEditT(t)} title="Bearbeiten"
                      className="p-1.5 rounded-md text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-sunken)] transition-colors"
                      data-testid={`tariff-edit-btn-${t.code}`}><Pencil size={13} /></button>
                    <button onClick={() => toggleActive(t)} title={t.is_active ? 'Archivieren' : 'Reaktivieren'}
                      className={`p-1.5 rounded-md hover:bg-[var(--color-surface-sunken)] transition-colors ${t.is_active ? 'text-[var(--color-danger)]' : 'text-[var(--color-success)]'}`}
                      data-testid={`tariff-toggle-btn-${t.code}`}>
                      {t.is_active ? <Archive size={13} /> : <RotateCcw size={13} />}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {list.length === 0 && (
              <tr><td colSpan={6} className="text-center py-8 text-xs text-[var(--color-text-tertiary)]">Keine Tarife gefunden</td></tr>
            )}
          </tbody>
        </table>
      </Card>
      {showCreate && <TariffModal onClose={() => setShowCreate(false)} onDone={refresh} />}
      {editT && <TariffModal tariff={editT} onClose={() => setEditT(null)} onDone={refresh} />}
    </PageScaffold>
  );
}
