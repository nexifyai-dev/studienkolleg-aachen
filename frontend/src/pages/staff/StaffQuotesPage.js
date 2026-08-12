import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import apiClient from '../../lib/apiClient';
import {
  FileSignature, Plus, X, XCircle, ChevronDown, RefreshCw,
  Clock, CheckCircle, Send, Ban, AlertTriangle, Hourglass,
  Download, Search, Edit3, Loader2, Trash2, Mail
} from 'lucide-react';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { TariffSelect } from '../../components/staff/TariffSelect';
import { API } from '../../lib/apiBase';

const STATUS_OPTIONS = ['draft', 'sent', 'accepted', 'rejected', 'expired'];
const STATUS_LABELS_DE = {
  draft: 'Entwurf', sent: 'Versendet', accepted: 'Angenommen',
  rejected: 'Abgelehnt', expired: 'Abgelaufen',
};
const STATUS_ICONS = { draft: Clock, sent: Send, accepted: CheckCircle, rejected: Ban, expired: Hourglass };
const STATUS_COLORS = {
  draft: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-primary)] border border-[var(--color-divider)]',
  sent: 'bg-[var(--color-info-bg)] text-[var(--color-info)] border border-[var(--color-info-border)]',
  accepted: 'bg-[var(--color-success-bg)] text-[var(--color-success)] border border-[var(--color-success-border)]',
  rejected: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border border-[var(--color-danger-border)]',
  expired: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning-border)]',
};

function StatusBadge({ status }) {
  const Icon = STATUS_ICONS[status] || Clock;
  return (
    <span className={`w2g-status text-[11px] font-semibold ${STATUS_COLORS[status] || STATUS_COLORS.draft}`}
          data-testid={`quote-status-${status}`}>
      <Icon size={11} />
      {STATUS_LABELS_DE[status] || status}
    </span>
  );
}

/* ═══════ Line Items Editor (mit Tarif-Dropdown) ═══════ */
function QuoteLineItemsEditor({ items, onChange, products }) {
  const addItem = () => {
    onChange([...items, { description: '', quantity: 1, unit_price: 0 }]);
  };

  const addProduct = (product) => {
    const emptyOnly = items.length === 1 && !items[0].description && !parseFloat(items[0].unit_price);
    const newItem = { description: product.name, quantity: 1, unit_price: product.price };
    onChange(emptyOnly ? [newItem] : [...items, newItem]);
  };

  const updateItem = (idx, field, value) => {
    onChange(items.map((item, i) => i === idx ? { ...item, [field]: value } : item));
  };

  const removeItem = (idx) => {
    if (items.length <= 1) return;
    onChange(items.filter((_, i) => i !== idx));
  };

  const total = items.reduce((sum, item) => sum + (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0), 0);
  const fmtEur = (val) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(val);

  return (
    <div className="space-y-3" data-testid="quote-line-items-editor">
      <div className="flex items-center justify-between">
        <label className="w2g-label mb-0">Positionen</label>
        <button type="button" onClick={addItem}
          className="text-[11px] bg-[var(--color-primary)] text-white px-2.5 py-1 rounded-sm hover:bg-[rgba(10,25,47,0.9)] font-medium flex items-center gap-1"
          data-testid="quote-add-line-item-btn">
          <Plus size={12} /> Freie Position
        </button>
      </div>

      {/* Tarif-Dropdown */}
      {products?.length > 0 && (
        <TariffSelect products={products} onSelect={addProduct} testId="quote-tariff-select" />
      )}

      <div className="grid grid-cols-[1fr_80px_100px_90px_32px] gap-2 text-[10px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider px-1">
        <span>Beschreibung</span>
        <span className="text-right">Menge</span>
        <span className="text-right">Einzelpreis</span>
        <span className="text-right">Gesamt</span>
        <span></span>
      </div>

      {items.map((item, idx) => {
        const lineTotal = (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0);
        return (
          <div key={idx} className="grid grid-cols-[1fr_80px_100px_90px_32px] gap-2 items-center" data-testid={`quote-line-item-${idx}`}>
            <input type="text" value={item.description}
              onChange={e => updateItem(idx, 'description', e.target.value)}
              placeholder="Leistungsbeschreibung..."
              className="w2g-input text-xs py-1.5"
              data-testid={`quote-line-item-desc-${idx}`} />
            <input type="number" min="1" step="1" value={item.quantity}
              onChange={e => updateItem(idx, 'quantity', e.target.value)}
              className="w2g-input text-xs py-1.5 text-right"
              data-testid={`quote-line-item-qty-${idx}`} />
            <input type="number" min="0" step="0.01" value={item.unit_price}
              onChange={e => updateItem(idx, 'unit_price', e.target.value)}
              className="w2g-input text-xs py-1.5 text-right"
              data-testid={`quote-line-item-price-${idx}`} />
            <span className="text-xs font-medium text-[var(--color-text-primary)] text-right tabular-nums">{fmtEur(lineTotal)}</span>
            <button type="button" onClick={() => removeItem(idx)}
              disabled={items.length <= 1}
              className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              data-testid={`quote-remove-line-item-${idx}`}>
              <Trash2 size={13} />
            </button>
          </div>
        );
      })}

      <div className="border-t border-[var(--color-divider)] pt-3 mt-2">
        <div className="flex justify-between items-center px-1">
          <span className="text-xs text-[var(--color-text-secondary)]">Zwischensumme</span>
          <span className="text-sm font-bold text-[var(--color-text-primary)] tabular-nums" data-testid="quote-subtotal">{fmtEur(total)}</span>
        </div>
        <p className="text-[10px] text-[var(--color-text-tertiary)] italic mt-1 text-right">
          Ggf. umsatzsteuerbefreit gem. &sect; 4 Nr. 21 UStG
        </p>
      </div>
    </div>
  );
}

/* ═══════ Create Quote Modal ═══════ */
function CreateQuoteModal({ onClose, onCreated, applicants, products }) {
  const defaultValid = () => {
    const d = new Date(); d.setDate(d.getDate() + 30);
    return d.toISOString().split('T')[0];
  };
  const [form, setForm] = useState({
    applicant_id: '', description: '', valid_until: defaultValid(),
    items: [{ description: '', quantity: 1, unit_price: 0 }],
  });
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);

  const filtered = applicants.filter(a => {
    const q = search.toLowerCase();
    return (a.full_name || '').toLowerCase().includes(q) || (a.email || '').toLowerCase().includes(q);
  });

  const selectedApplicant = applicants.find(a => a.id === form.applicant_id);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.applicant_id || !form.valid_until || form.items.every(i => !i.description)) return;
    setSaving(true);
    try {
      const desc = form.items.map(i => i.description).filter(Boolean).join(', ') || form.description;
      const res = await apiClient.post('/api/quotes', {
        applicant_id: form.applicant_id,
        description: desc,
        valid_until: form.valid_until,
        items: form.items.filter(i => i.description).map(i => ({
          description: i.description,
          quantity: parseFloat(i.quantity) || 1,
          unit_price: parseFloat(i.unit_price) || 0,
        })),
      });
      toast.success('Angebot erstellt');
      onCreated(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler');
    } finally { setSaving(false); }
  };

  return (
    <div className="w2g-modal-overlay" data-testid="create-quote-modal">
      <div className="w2g-modal max-w-2xl">
        <div className="w2g-modal-header">
          <h2 className="text-lg font-bold text-primary">Neues Angebot</h2>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="close-create-quote"><X size={18} /></button>
        </div>
        <form onSubmit={handleSubmit} className="w2g-modal-body space-y-5">
          {/* Applicant Search */}
          <div className="relative">
            <label className="w2g-label">Bewerber</label>
            {selectedApplicant ? (
              <div className="w2g-input flex items-center justify-between" data-testid="quote-applicant-selected">
                <span className="text-sm text-[var(--color-text-primary)]">{selectedApplicant.full_name || selectedApplicant.email}</span>
                <button type="button" onClick={() => { setForm(f => ({...f, applicant_id: ''})); setSearch(''); }}
                  className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]"><X size={14} /></button>
              </div>
            ) : (
              <>
                <div className="relative">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
                  <input type="text" value={search}
                    onChange={e => { setSearch(e.target.value); setShowDropdown(true); }}
                    onFocus={() => setShowDropdown(true)}
                    className="w2g-input pl-9" placeholder="Name oder E-Mail suchen..."
                    data-testid="quote-applicant-search" />
                </div>
                {showDropdown && (
                  <div className="absolute z-50 mt-1 w-full bg-white border border-[var(--color-divider)] rounded-md shadow-lg max-h-48 overflow-y-auto"
                    data-testid="quote-applicant-dropdown">
                    {filtered.length === 0 ? (
                      <p className="px-3 py-2 text-xs text-[var(--color-text-tertiary)]">Keine Ergebnisse</p>
                    ) : (
                      filtered.slice(0, 50).map(a => (
                        <button key={a.id} type="button"
                          onClick={() => { setForm(f => ({...f, applicant_id: a.id})); setShowDropdown(false); setSearch(a.full_name || a.email); }}
                          className="w-full text-left px-3 py-2 hover:bg-[var(--color-surface-elevated)] border-b border-[var(--color-divider-subtle)] last:border-0"
                          data-testid={`quote-applicant-option-${a.id}`}>
                          <p className="text-sm text-[var(--color-text-primary)] font-medium">{a.full_name || 'Unbekannt'}</p>
                          <p className="text-xs text-[var(--color-text-tertiary)]">{a.email}</p>
                        </button>
                      ))
                    )}
                  </div>
                )}
              </>
            )}
          </div>

          {/* Valid until */}
          <div>
            <label className="w2g-label">Gültig bis</label>
            <input type="date" value={form.valid_until} onChange={e => setForm(f => ({...f, valid_until: e.target.value}))}
              className="w2g-input" data-testid="quote-valid-until-input" required />
          </div>

          {/* Line Items mit Tarif-Dropdown */}
          <QuoteLineItemsEditor items={form.items} products={products}
            onChange={items => setForm(f => ({...f, items}))} />
        </form>
        <div className="w2g-modal-footer">
          <button type="button" onClick={onClose} className="w2g-btn-secondary">Abbrechen</button>
          <button type="submit" disabled={saving || !form.applicant_id || !form.valid_until} onClick={handleSubmit}
            className="w2g-btn-primary" data-testid="quote-submit-btn">
            {saving ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
            Angebot erstellen
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════ Edit Quote Modal ═══════ */
function EditQuoteModal({ quote, onClose, onSaved, products }) {
  const initialItems = quote?.items?.length
    ? quote.items.map(i => ({
        description: i.description || '',
        quantity: i.quantity || 1,
        unit_price: i.unit_price || 0,
      }))
    : [{ description: quote?.description || '', quantity: 1, unit_price: quote?.amount || 0 }];

  const [form, setForm] = useState({
    valid_until: quote?.valid_until?.split('T')[0] || '',
    notes: quote?.notes || '',
    items: initialItems,
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const desc = form.items.map(i => i.description).filter(Boolean).join(', ');
      await apiClient.patch(`/api/quotes/${quote.quote_number}`, {
        description: desc,
        valid_until: form.valid_until,
        notes: form.notes,
        items: form.items.map(i => ({
          description: i.description,
          quantity: parseFloat(i.quantity) || 1,
          unit_price: parseFloat(i.unit_price) || 0,
        })),
      });
      toast.success('Angebot aktualisiert');
      onSaved();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler');
    } finally { setSaving(false); }
  };

  return (
    <div className="w2g-modal-overlay" data-testid="edit-quote-modal">
      <div className="w2g-modal max-w-2xl">
        <div className="w2g-modal-header">
          <h2 className="text-lg font-bold text-primary">Angebot bearbeiten</h2>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="close-edit-quote"><X size={18} /></button>
        </div>
        <div className="w2g-modal-body space-y-5">
          <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] rounded-md p-3 flex items-center justify-between">
            <div>
              <span className="font-mono text-sm font-bold text-primary">{quote.quote_number}</span>
              <span className="text-xs text-[var(--color-text-tertiary)] ml-3">{quote.applicant_name}</span>
            </div>
            <StatusBadge status={quote.status} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="w2g-label">Gültig bis</label>
              <input type="date" value={form.valid_until}
                onChange={e => setForm(f => ({...f, valid_until: e.target.value}))}
                className="w2g-input" data-testid="edit-quote-valid-until" />
            </div>
            <div>
              <label className="w2g-label">Interne Notizen</label>
              <input type="text" value={form.notes}
                onChange={e => setForm(f => ({...f, notes: e.target.value}))}
                className="w2g-input" data-testid="edit-quote-notes" placeholder="Anmerkungen..." />
            </div>
          </div>

          <QuoteLineItemsEditor items={form.items} products={products}
            onChange={items => setForm(f => ({...f, items}))} />
        </div>
        <div className="w2g-modal-footer">
          <button onClick={onClose} className="w2g-btn-secondary">Abbrechen</button>
          <button onClick={handleSave} disabled={saving} className="w2g-btn-primary" data-testid="save-edit-quote-btn">
            {saving ? <Loader2 size={14} className="animate-spin" /> : null} Speichern
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════ Main Quotes Page ═══════ */
export default function StaffQuotesPage() {
  const [quotes, setQuotes] = useState([]);
  const [stats, setStats] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [editQuote, setEditQuote] = useState(null);
  const [filter, setFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusDropdown, setStatusDropdown] = useState(null);
  const [sendingQuote, setSendingQuote] = useState(null);
  const [deletingQuote, setDeletingQuote] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = filter ? `?status=${filter}` : '';
      const [qRes, statsRes] = await Promise.all([
        apiClient.get(`/api/quotes${params}`),
        apiClient.get('/api/quotes/stats'),
      ]);
      setQuotes(qRes.data);
      setStats(statsRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Fehler beim Laden');
    } finally { setLoading(false); }
  }, [filter]);

  useEffect(() => { fetchData(); }, [fetchData]);
  useEffect(() => {
    apiClient.get('/api/invoices/applicants').then(r => setApplicants(r.data || [])).catch(() => {});
    apiClient.get('/api/products').then(r => setProducts(r.data || [])).catch(() => {});
  }, []);

  const handleStatusChange = async (quoteNumber, newStatus) => {
    try {
      await apiClient.patch(`/api/quotes/${quoteNumber}`, { status: newStatus });
      toast.success(`Status: ${STATUS_LABELS_DE[newStatus]}`);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler');
    }
    setStatusDropdown(null);
  };

  const handleSendQuote = async (quoteNumber) => {
    setSendingQuote(quoteNumber);
    try {
      await apiClient.post(`/api/quotes/${quoteNumber}/send`, {}, { withCredentials: true });
      toast.success('Angebot per E-Mail versendet');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Versand fehlgeschlagen');
    } finally { setSendingQuote(null); }
  };

  const handleDeleteQuote = async (quoteNumber) => {
    if (!window.confirm(`Angebot ${quoteNumber} wirklich löschen?`)) return;
    setDeletingQuote(quoteNumber);
    try {
      await apiClient.delete(`/api/quotes/${quoteNumber}`);
      toast.success('Angebot gelöscht');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Löschen fehlgeschlagen');
    } finally { setDeletingQuote(null); }
  };

  const fmtCurrency = (amount, currency = 'EUR') =>
    new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(amount);

  const fmtDate = (iso) => {
    if (!iso) return '-';
    try { return new Date(iso).toLocaleDateString('de-DE'); } catch { return iso; }
  };

  const q = searchTerm.toLowerCase();
  const filteredQuotes = q
    ? quotes.filter(i =>
        (i.quote_number || '').toLowerCase().includes(q) ||
        (i.applicant_name || '').toLowerCase().includes(q) ||
        (i.applicant_email || '').toLowerCase().includes(q) ||
        (i.applicant_number || '').toLowerCase().includes(q) ||
        (i.description || '').toLowerCase().includes(q)
      )
    : quotes;

  return (
    <PageScaffold
      title="Angebote"
      subtitle="Angebote erstellen, versenden und nachverfolgen"
      testId="staff-quotes-page"
      actions={
        <div className="flex items-center gap-2">
          <button onClick={fetchData} className="w2g-btn-icon" data-testid="refresh-quotes" title="Aktualisieren">
            <RefreshCw size={16} />
          </button>
          <button onClick={() => setShowCreate(true)} className="w2g-btn-primary" data-testid="create-quote-btn">
            <Plus size={16} /> Neues Angebot
          </button>
        </div>
      }
      toolbar={
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
                placeholder="Nr., Bewerber, Beschreibung..."
                className="w2g-search pl-9" data-testid="quote-search" />
              {searchTerm && (
                <button onClick={() => setSearchTerm('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]">
                  <XCircle size={14} />
                </button>
              )}
            </div>
          }
          filters={['', 'draft', 'sent', 'accepted', 'rejected', 'expired'].map(s => (
            <button key={s} onClick={() => setFilter(s)}
              className={filter === s ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}
              data-testid={`quote-filter-${s || 'all'}`}>
              {s ? STATUS_LABELS_DE[s] : 'Alle'}
            </button>
          ))}
        />
      }
    >
      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3" data-testid="quote-stats">
          <Card className="border-l-[3px] border-l-[var(--color-primary)]">
            <CardContent className="px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--color-text-tertiary)]">Gesamt</p>
              <p className="text-xl font-extrabold text-[var(--color-primary)] mt-1 tabular-nums" style={{ fontFamily: 'var(--font-heading)' }}>{fmtCurrency(stats.total_amount)}</p>
              <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1">{stats.total_count} Angebote</p>
            </CardContent>
          </Card>
          {['draft', 'sent', 'accepted', 'rejected'].map(s => {
            const data = stats.by_status?.[s];
            if (!data) return null;
            return (
              <Card key={s} className="cursor-pointer hover:shadow-[var(--shadow-e2)] transition-shadow" onClick={() => setFilter(filter === s ? '' : s)}>
                <CardContent className="px-4 py-3">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--color-text-tertiary)]">{STATUS_LABELS_DE[s]}</p>
                  <p className="text-xl font-bold text-[var(--color-text-primary)] mt-1 tabular-nums">{fmtCurrency(data.total)}</p>
                  <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1">{data.count} Angebot{data.count !== 1 ? 'e' : ''}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="w2g-loading" data-testid="quotes-loading"><div className="w2g-spinner"></div></div>
      ) : error ? (
        <div className="text-center py-12 text-[var(--color-danger)]" data-testid="quotes-error">
          <AlertTriangle size={24} className="mx-auto mb-2" />
          <p className="text-sm">{error}</p>
        </div>
      ) : filteredQuotes.length === 0 ? (
        <div className="w2g-empty" data-testid="quotes-empty">
          <FileSignature size={32} className="w2g-empty-icon" />
          <p className="w2g-empty-text">{searchTerm ? 'Keine Treffer' : 'Keine Angebote vorhanden'}</p>
          <p className="w2g-empty-hint">{!searchTerm && 'Erstellen Sie ein neues Angebot oben rechts.'}</p>
        </div>
      ) : (
        <Card className="p-0 overflow-hidden" data-testid="quotes-table">
          <table className="w2g-table">
            <thead>
              <tr>
                <th>Angebotsnr.</th>
                <th>Bewerber</th>
                <th>Beschreibung</th>
                <th>Pos.</th>
                <th className="text-right">Betrag</th>
                <th>Status</th>
                <th>Gültig bis</th>
                <th className="text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {filteredQuotes.map(qt => (
                <tr key={qt.quote_number || qt.id} data-testid={`quote-row-${qt.quote_number}`}>
                  <td className="font-mono text-xs text-primary font-medium">{qt.quote_number}</td>
                  <td>
                    <p className="font-medium text-[var(--color-text-primary)] text-sm">{qt.applicant_name}</p>
                    <div className="flex items-center gap-2">
                      {qt.applicant_number && <span className="text-[10px] font-mono text-primary font-bold">{qt.applicant_number}</span>}
                      <p className="text-[10px] text-[var(--color-text-tertiary)]">{qt.applicant_email}</p>
                    </div>
                  </td>
                  <td className="text-[var(--color-text-secondary)] max-w-[180px] truncate text-xs">{qt.description}</td>
                  <td className="text-xs text-[var(--color-text-secondary)] tabular-nums">{qt.items?.length || 1}</td>
                  <td className="text-right font-medium text-[var(--color-text-primary)]">{fmtCurrency(qt.amount, qt.currency)}</td>
                  <td><StatusBadge status={qt.status} /></td>
                  <td className="text-xs text-[var(--color-text-secondary)]">{fmtDate(qt.valid_until)}</td>
                  <td className="text-right">
                    <div className="flex items-center justify-end gap-1 relative">
                      <button onClick={() => setEditQuote(qt)}
                        className="w2g-btn-icon" title="Bearbeiten"
                        data-testid={`edit-quote-${qt.quote_number}`}>
                        <Edit3 size={14} />
                      </button>
                      <a href={`${API}/api/quotes/${qt.quote_number}/pdf`}
                        target="_blank" rel="noreferrer" className="w2g-btn-icon" title="PDF Download"
                        data-testid={`download-quote-pdf-${qt.quote_number}`}>
                        <Download size={14} />
                      </a>
                      {qt.applicant_email && qt.status !== 'rejected' && qt.status !== 'expired' && (
                        <button onClick={() => handleSendQuote(qt.quote_number)}
                          disabled={sendingQuote === qt.quote_number}
                          className="w2g-btn-icon" title="Per E-Mail senden"
                          data-testid={`send-quote-${qt.quote_number}`}>
                          {sendingQuote === qt.quote_number
                            ? <Loader2 size={14} className="animate-spin" />
                            : <Mail size={14} />
                          }
                        </button>
                      )}
                      {qt.status === 'draft' && (
                        <button onClick={() => handleDeleteQuote(qt.quote_number)}
                          disabled={deletingQuote === qt.quote_number}
                          className="w2g-btn-icon" title="Löschen"
                          data-testid={`delete-quote-${qt.quote_number}`}>
                          {deletingQuote === qt.quote_number
                            ? <Loader2 size={14} className="animate-spin" />
                            : <Trash2 size={14} className="text-[var(--color-danger)]" />
                          }
                        </button>
                      )}
                      <button onClick={() => setStatusDropdown(statusDropdown === qt.quote_number ? null : qt.quote_number)}
                        className="w2g-btn-icon" title="Status ändern"
                        data-testid={`quote-status-change-btn-${qt.quote_number}`}>
                        <ChevronDown size={14} />
                      </button>
                      {statusDropdown === qt.quote_number && (
                        <>
                          <div className="fixed inset-0 z-40" onClick={() => setStatusDropdown(null)} />
                          <div className="absolute right-0 top-full mt-1 bg-white border border-[var(--color-divider)] rounded-md shadow-lg z-50 min-w-[150px]"
                               data-testid={`quote-status-dropdown-${qt.quote_number}`}>
                            {STATUS_OPTIONS.filter(s => s !== qt.status).map(s => (
                              <button key={s} onClick={() => handleStatusChange(qt.quote_number, s)}
                                className="w-full text-left px-3 py-2 text-xs hover:bg-[var(--color-surface-elevated)] flex items-center gap-2"
                                data-testid={`quote-set-status-${s}`}>
                                <StatusBadge status={s} />
                              </button>
                            ))}
                          </div>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {/* Modals */}
      {showCreate && (
        <CreateQuoteModal applicants={applicants} products={products}
          onClose={() => setShowCreate(false)}
          onCreated={() => { setShowCreate(false); fetchData(); }} />
      )}
      {editQuote && (
        <EditQuoteModal quote={editQuote} products={products}
          onClose={() => setEditQuote(null)}
          onSaved={() => { setEditQuote(null); fetchData(); }} />
      )}
    </PageScaffold>
  );
}
