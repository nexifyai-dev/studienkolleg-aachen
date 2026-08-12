import React, { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Power, PowerOff, Search, X, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import apiClient from '../../lib/apiClient';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { TARIFF_CATEGORIES } from '../../components/staff/TariffSelect';

const EMPTY_FORM = {
  code: '', name: '', description: '', price: '', currency: 'EUR',
  category: 'kurs', is_active: true,
};

function TariffModal({ tariff, onClose, onSaved }) {
  const [form, setForm] = useState(tariff ? {
    code: tariff.code, name: tariff.name, description: tariff.description || '',
    price: tariff.price, currency: tariff.currency || 'EUR',
    category: tariff.category || 'kurs', is_active: tariff.is_active !== false,
  } : { ...EMPTY_FORM });
  const [saving, setSaving] = useState(false);

  const set = (k, v) => setForm(prev => ({ ...prev, [k]: v }));

  const handleSave = async () => {
    if (!form.code || !form.name) { toast.error('Code und Name sind erforderlich'); return; }
    setSaving(true);
    try {
      const payload = {
        name: form.name, description: form.description,
        price: parseFloat(form.price) || 0, currency: form.currency,
        category: form.category, is_active: !!form.is_active,
      };
      if (tariff) {
        await apiClient.patch(`/api/products/${tariff.code}`, payload, { withCredentials: true });
        toast.success('Tarif aktualisiert');
      } else {
        await apiClient.post('/api/products', { code: form.code, ...payload }, { withCredentials: true });
        toast.success('Tarif erstellt');
      }
      onSaved();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w2g-modal-overlay" data-testid="tariff-modal" onClick={onClose}>
      <div className="bg-[var(--color-surface)] rounded-[var(--radius-md)] shadow-xl w-full max-w-md p-5" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">
            {tariff ? 'Tarif bearbeiten' : 'Neuer Tarif'}
          </h3>
          <button onClick={onClose} className="p-1 rounded hover:bg-[var(--color-surface-sunken)]" data-testid="tariff-modal-close">
            <X size={16} />
          </button>
        </div>
        <div className="space-y-3">
          <div>
            <label className="w2g-label">Code</label>
            <input
              className="w2g-input text-xs py-2"
              value={form.code}
              disabled={!!tariff}
              onChange={e => set('code', e.target.value.toUpperCase())}
              placeholder="z.B. SK-TKURS"
              data-testid="tariff-code-input"
            />
          </div>
          <div>
            <label className="w2g-label">Name</label>
            <input
              className="w2g-input text-xs py-2"
              value={form.name}
              onChange={e => set('name', e.target.value)}
              placeholder="Tarifname"
              data-testid="tariff-name-input"
            />
          </div>
          <div>
            <label className="w2g-label">Beschreibung</label>
            <input
              className="w2g-input text-xs py-2"
              value={form.description}
              onChange={e => set('description', e.target.value)}
              placeholder="Kurzbeschreibung"
              data-testid="tariff-desc-input"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="w2g-label">Kategorie</label>
              <select
                className="w2g-select w-full text-xs py-2"
                value={form.category}
                onChange={e => set('category', e.target.value)}
                data-testid="tariff-category-select"
              >
                {Object.entries(TARIFF_CATEGORIES).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="w2g-label">Preis (EUR)</label>
              <input
                type="number" min="0" step="0.01"
                className="w2g-input text-xs py-2"
                value={form.price}
                onChange={e => set('price', e.target.value)}
                data-testid="tariff-price-input"
              />
            </div>
          </div>
          <label className="flex items-center gap-2 text-xs text-[var(--color-text-secondary)]">
            <input type="checkbox" checked={!!form.is_active} onChange={e => set('is_active', e.target.checked)} />
            Aktiv (Preis erscheint live auf der Website)
          </label>
          <button
            onClick={handleSave}
            disabled={saving}
            className="w2g-btn-primary w-full flex items-center justify-center gap-2"
            data-testid="tariff-save-btn"
          >
            {saving ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
            {tariff ? 'Speichern' : 'Erstellen'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function AdminTariffsPage() {
  const [tariffs, setTariffs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [catFilter, setCatFilter] = useState('all');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);

  const load = () => {
    setLoading(true);
    apiClient.get('/api/products', { withCredentials: true })
      .then(r => setTariffs(r.data || []))
      .catch(() => toast.error('Tarife konnten nicht geladen werden'))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  const filtered = tariffs.filter(t => {
    const q = search.toLowerCase();
    const matchSearch = !q || (t.code || '').toLowerCase().includes(q) || (t.name || '').toLowerCase().includes(q);
    const matchCat = catFilter === 'all' || (t.category || 'sonstig') === catFilter;
    return matchSearch && matchCat;
  });

  const toggle = async (t) => {
    try {
      await apiClient.patch(`/api/products/${t.code}`, { is_active: !t.is_active }, { withCredentials: true });
      toast.success(t.is_active ? 'Tarif deaktiviert' : 'Tarif aktiviert');
      load();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler');
    }
  };

  const remove = async (t) => {
    if (!window.confirm(`Tarif ${t.code} wirklich loeschen?`)) return;
    try {
      await apiClient.delete(`/api/products/${t.code}`, { withCredentials: true });
      toast.success('Tarif geloescht');
      load();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Loeschen');
    }
  };

  const fmtEur = (v) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(v || 0);

  return (
    <PageScaffold
      title={`${filtered.length} Tarife \u00b7 Preise erscheinen live auf der Website`}
      testId="admin-tariffs-page"
      toolbar={
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search size={13} className="absolute left-2.5 top-2.5 text-[var(--color-text-tertiary)]" />
            <input
              className="w2g-search pl-9 text-xs py-2"
              placeholder="Code oder Name suchen..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              data-testid="tariffs-search"
            />
          </div>
          <select
            className="w2g-select text-xs rounded py-2"
            value={catFilter}
            onChange={e => setCatFilter(e.target.value)}
            data-testid="tariffs-category-filter"
          >
            <option value="all">Alle Kategorien</option>
            {Object.entries(TARIFF_CATEGORIES).map(([val, label]) => (
              <option key={val} value={val}>{label}</option>
            ))}
          </select>
          <button
            onClick={() => { setEditing(null); setModalOpen(true); }}
            className="w2g-btn-primary flex items-center gap-1.5 text-xs"
            data-testid="tariff-create-btn"
          >
            <Plus size={13} /> Neuer Tarif
          </button>
        </div>
      }
    >
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full" data-testid="admin-tariffs-table">
              <thead>
                <tr className="border-b border-[var(--color-divider)] text-[10px] uppercase tracking-wider text-[var(--color-text-secondary)]">
                  <th className="px-4 py-2.5 text-left">Code</th>
                  <th className="px-4 py-2.5 text-left">Name</th>
                  <th className="px-4 py-2.5 text-left">Kategorie</th>
                  <th className="px-4 py-2.5 text-right">Preis</th>
                  <th className="px-4 py-2.5 text-center">Status</th>
                  <th className="px-4 py-2.5 text-right">Aktionen</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-[var(--color-text-tertiary)]">
                    <Loader2 size={18} className="animate-spin inline" /> Lade Tarife...
                  </td></tr>
                )}
                {!loading && filtered.length === 0 && (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-[var(--color-text-tertiary)]">Keine Tarife gefunden</td></tr>
                )}
                {filtered.map(t => (
                  <tr key={t.code} data-testid={`tariff-row-${t.code}`}
                    className={`border-b border-[var(--color-divider)] hover:bg-[var(--color-surface-sunken)] transition-colors ${t.is_active ? '' : 'opacity-50'}`}>
                    <td className="px-4 py-2.5 font-mono text-xs">{t.code}</td>
                    <td className="px-4 py-2.5 text-xs">{t.name}</td>
                    <td className="px-4 py-2.5 text-xs">{TARIFF_CATEGORIES[t.category] || t.category}</td>
                    <td className="px-4 py-2.5 text-right text-xs tabular-nums">{fmtEur(t.price)}</td>
                    <td className="px-4 py-2.5 text-center">
                      <span className={`w2g-status text-[10px] font-semibold ${t.is_active ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
                        {t.is_active ? 'Aktiv' : 'Inaktiv'}
                      </span>
                    </td>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => { setEditing(t); setModalOpen(true); }}
                          className="p-1.5 rounded hover:bg-[var(--color-surface-sunken)]" data-testid={`tariff-edit-btn-${t.code}`}>
                          <Pencil size={13} />
                        </button>
                        <button onClick={() => toggle(t)}
                          className="p-1.5 rounded hover:bg-[var(--color-surface-sunken)]" data-testid={`tariff-toggle-btn-${t.code}`}>
                          {t.is_active ? <PowerOff size={13} className="text-[var(--color-danger)]" /> : <Power size={13} className="text-[var(--color-success)]" />}
                        </button>
                        <button onClick={() => remove(t)}
                          className="p-1.5 rounded hover:bg-[var(--color-danger-bg)] text-[var(--color-danger)]" data-testid={`tariff-delete-btn-${t.code}`}>
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
      {modalOpen && (
        <TariffModal tariff={editing} onClose={() => setModalOpen(false)} onSaved={() => { setModalOpen(false); load(); }} />
      )}
    </PageScaffold>
  );
}
