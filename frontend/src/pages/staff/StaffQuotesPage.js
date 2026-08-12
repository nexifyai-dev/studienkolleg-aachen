import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import apiClient from '../../lib/apiClient';
import {
  Plus, X, Search, Send, Download, Trash2, Loader2, Clock,
  CheckCircle, Ban, FileCheck2, Eye, FileText, ChevronDown,
} from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import TariffSelect from '../../components/staff/TariffSelect';

const STATUS_OPTIONS = ['draft', 'sent', 'accepted', 'declined', 'invoiced'];
const STATUS_LABELS_DE = {
  draft: 'Entwurf', sent: 'Versendet', accepted: 'Angenommen',
  declined: 'Abgelehnt', invoiced: 'In Rechnung gestellt',
};
const STATUS_ICONS = {
  draft: Clock, sent: Send, accepted: CheckCircle,
  declined: Ban, invoiced: FileCheck2,
};
const STATUS_COLORS = {
  draft: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-primary)] border border-[var(--color-divider)]',
  sent: 'bg-[var(--color-info-bg)] text-[var(--color-info)] border border-[var(--color-info-border)]',
  accepted: 'bg-[var(--color-success-bg)] text-[var(--color-success)] border border-[var(--color-success-border)]',
  declined: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border border-[var(--color-danger-border)]',
  invoiced: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning-border)]',
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

function LineItemsEditor({ items, onChange }) {
  const addItem = () => onChange([...items, { description: '', quantity: 1, unit_price: 0 }]);
  const updateItem = (idx, field, value) =>
    onChange(items.map((item, i) => i === idx ? { ...item, [field]: value } : item));
  const removeItem = (idx) => { if (items.length > 1) onChange(items.filter((_, i) => i !== idx)); };
  const total = items.reduce((s, i) => s + (parseFloat(i.quantity) || 0) * (parseFloat(i.unit_price) || 0), 0);
  const fmtEur = (v) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(v);

  return (
    <div className="space-y-3" data-testid="quote-line-items-editor">
      <div className="flex items-center justify-between">
        <label className="w2g-label mb-0">Positionen</label>
        <button type="button" onClick={addItem}
          className="text-[11px] bg-[var(--color-primary)] text-white px-2.5 py-1 rounded-sm font-medium flex items-center gap-1"
          data-testid="quote-add-line-item-btn">
          <Plus size={12} /> Position
        </button>
      </div>
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
              placeholder="Leistungsbeschreibung..." className="w2g-input text-xs py-1.5" />
            <input type="number" min="1" step="1" value={item.quantity}
              onChange={e => updateItem(idx, 'quantity', e.target.value)}
              className="w2g-input text-xs py-1.5 text-right" />
            <input type="number" min="0" step="0.01" value={item.unit_price}
              onChange={e => updateItem(idx, 'unit_price', e.target.value)}
              className="w2g-input text-xs py-1.5 text-right" />
            <span className="text-xs font-medium text-[var(--color-text-primary)] text-right tabular-nums">{fmtEur(lineTotal)}</span>
            <button type="button" onClick={() => removeItem(idx)} disabled={items.length <= 1}
              className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)] disabled:opacity-30 transition-colors">
              <Trash2 size={13} />
            </button>
          </div>
        );
      })}
      <div className="border-t border-[var(--color-divider)] pt-3 mt-2">
        <div className="flex justify-between items-center px-1">
          <span className="text-xs text-[var(--color-text-secondary)]">Zwischensumme</span>
          <span className="text-sm font-bold text-[var(--color-text-primary)] tabular-nums">{fmtEur(total)}</span>
        </div>
        <p className="text-[10px] text-[var(--color-text-tertiary)] italic mt-1 text-right">
          Ggf. umsatzsteuerbefreit gem. &sect; 4 Nr. 21 UStG
        </p>
      </div>
    </div>
  );
}

/* ═══════ Create Quote Modal (mit Tarif-Dropdown) ═══════ */
function CreateQuoteModal({ onClose, onCreated, applicants }) {
  const [form, setForm] = useState({
    applicant_id: '', description: '', valid_until: '', notes: '',
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
  const total = form.items.reduce((s, i) => s + (parseFloat(i.quantity) || 0) * (parseFloat(i.unit_price) || 0), 0);

  const addTariff = (tariff) => {
    setForm(f => ({
      ...f,
      items: f.items.every(i => !i.description)
        ? [{ description: tariff.name, quantity: 1, unit_price: tariff.price, code: tariff.code }]
        : [...f.items, { description: tariff.name, quantity: 1, unit_price: tariff.price, code: tariff.code }],
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.applicant_id || !form.valid_until || form.items.every(i => !i.description)) {
      toast.error('Bewerber, Gueltig-bis-Datum und mindestens eine Position angeben');
      return;
    }
    setSaving(true);
    try {
      const desc = form.items.map(i => i.description).filter(Boolean).join(', ') || form.description;
      await apiClient.post('/api/quotes', {
        applicant_id: form.applicant_id,
        description: desc,
        amount: Math.round(total * 100) / 100,
        valid_until: form.valid_until,
        notes: form.notes,
        items: form.items.map(i => ({
          code: i.code,
          description: i.description,
          quantity: parseFloat(i.quantity) || 1,
          unit_price: parseFloat(i.unit_price) || 0,
        })),
      });
      toast.success('Angebot als Entwurf gespeichert');
      onCreated();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Erstellen des Angebots');
    } finally { setSaving(false); }
  };

  return (
    <div className="w2g-modal-overlay" data-testid="quote-create-modal" onClick={onClose}>
      <div className="w2g-modal max-w-2xl" onClick={e => e.stopPropagation()}>
        <div className="w2g-modal-header">
          <h2 className="text-lg font-bold text-primary">Neues Angebot</h2>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="quote-modal-close"><X size={18} /></button>
        </div>
        <form className="w2g-modal-body space-y-4" onSubmit={handleSubmit}>
          {/* Applicant */}
          <div className="relative">
            <label className="w2g-label">Bewerber</label>
            <input
              className="w2g-input"
              placeholder="Name oder E-Mail suchen..."
              value={selectedApplicant ? `${selectedApplicant.full_name} (${selectedApplicant.email})` : search}
              onFocus={() => setShowDropdown(true)}
              onChange={e => { setSearch(e.target.value); setForm(f => ({ ...f, applicant_id: '' })); }}
              data-testid="quote-applicant-search"
            />
            {showDropdown && (
              <div className="absolute z-20 mt-1 w-full bg-[var(--color-surface)] border border-[var(--color-divider)] rounded-md shadow-lg max-h-48 overflow-y-auto">
                {filtered.length === 0 && <div className="p-3 text-xs text-[var(--color-text-tertiary)]">Keine Bewerber gefunden</div>}
                {filtered.map(a => (
                  <button type="button" key={a.id}
                    onClick={() => { setForm(f => ({ ...f, applicant_id: a.id })); setSearch(`${a.full_name} (${a.email})`); setShowDropdown(false); }}
                    className="w-full text-left px-3 py-2 text-xs hover:bg-[var(--color-surface-sunken)]"
                    data-testid={`quote-applicant-option-${a.id}`}>
                    {a.full_name} <span className="text-[var(--color-text-tertiary)]">{a.email}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Valid until + Notes */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="w2g-label">Gueltig bis</label>
              <input type="date" value={form.valid_until}
                onChange={e => setForm(f => ({ ...f, valid_until: e.target.value }))}
                className="w2g-input" data-testid="quote-valid-until-input" required />
            </div>
            <div>
              <label className="w2g-label">Interne Notizen</label>
              <input type="text" value={form.notes}
                onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                className="w2g-input" data-testid="quote-notes-input" placeholder="Anmerkungen..." />
            </div>
          </div>

          {/* Tarif-Dropdown */}
          <TariffSelect onAdd={addTariff} label="Tarif hinzufuegen" />

          {/* Line Items */}
          <LineItemsEditor items={form.items} onChange={items => setForm(f => ({ ...f, items }))} />
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

/* ═══════ Main Quotes Page ═══════ */
export default function StaffQuotesPage() {
  const [quotes, setQuotes] = useState([]);
  const [stats, setStats] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [filter, setFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusDropdown, setStatusDropdown] = useState(null);
  const [sending, setSending] = useState(null);
  const [detail, setDetail] = useState(null);

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
    apiClient.get('/api/quotes/applicants').then(r => setApplicants(r.data || [])).catch(() => {});
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

  const handleSend = async (quoteNumber) => {
    setSending(quoteNumber);
    try {
      await apiClient.post(`/api/quotes/${quoteNumber}/send`, {}, { withCredentials: true });
      toast.success('Angebot per E-Mail versendet');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Versand fehlgeschlagen');
    } finally { setSending(null); }
  };

  const handleDelete = async (quote) => {
    if (!window.confirm(`Angebot ${quote.quote_number} wirklich loeschen?`)) return;
    try {
      await apiClient.delete(`/api/quotes/${quote.quote_number}`, { withCredentials: true });
      toast.success('Angebot geloescht');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Loeschen');
    }
  };

  const fmtCurrency = (amount, currency = 'EUR') =>
    new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(amount || 0);
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
      subtitle="Verwaltung, Positionen, Versand"
      testId="staff-quotes-page"
      actions={
        <div className="flex items-center gap-2">
          <button onClick={() => setShowCreate(true)} className="w2g-btn-primary flex items-center gap-1.5" data-testid="quote-create-btn">
            <Plus size={15} /> Neues Angebot
          </button>
        </div>
      }
    >
      {/* Stats + Filter */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-baseline gap-2 min-w-[200px]">
              <span className="text-[10px] uppercase tracking-wider text-[var(--color-text-secondary)]">Gesamt</span>
              <span className="text-xl font-bold text-primary tabular-nums">{fmtCurrency(stats?.total_amount)}</span>
              <span className="text-xs text-[var(--color-text-tertiary)]">{stats?.total_count || 0} Angebote</span>
            </div>
            <div className="flex flex-wrap items-center gap-1.5 ml-auto">
              {['', ...STATUS_OPTIONS].map(s => (
                <button key={s || 'all'} onClick={() => setFilter(s)}
                  className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors ${filter === s
                    ? 'bg-[var(--color-primary)] text-white'
                    : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'}`}
                  data-testid={`quote-filter-${s || 'all'}`}>
                  {s ? STATUS_LABELS_DE[s] : 'Alle'}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Search */}
      <div className="relative">
        <Search size={13} className="absolute left-3 top-2.5 text-[var(--color-text-tertiary)]" />
        <input
          className="w2g-search pl-9"
          placeholder="Nr., Bewerber, Beschreibung..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          data-testid="quotes-search"
        />
      </div>

      {/* List */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full" data-testid="quotes-table">
              <thead>
                <tr className="border-b border-[var(--color-divider)] text-[10px] uppercase tracking-wider text-[var(--color-text-secondary)]">
                  <th className="px-4 py-2.5 text-left">Nr.</th>
                  <th className="px-4 py-2.5 text-left">Bewerber</th>
                  <th className="px-4 py-2.5 text-left">Beschreibung</th>
                  <th className="px-4 py-2.5 text-right">Betrag</th>
                  <th className="px-4 py-2.5 text-left">Gueltig bis</th>
                  <th className="px-4 py-2.5 text-center">Status</th>
                  <th className="px-4 py-2.5 text-right">Aktionen</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr><td colSpan={7} className="px-4 py-8 text-center text-[var(--color-text-tertiary)]">
                    <Loader2 size={18} className="animate-spin inline" /> Lade Angebote...
                  </td></tr>
                )}
                {!loading && error && (
                  <tr><td colSpan={7} className="px-4 py-8 text-center text-[var(--color-danger)]">{error}</td></tr>
                )}
                {!loading && !error && filteredQuotes.length === 0 && (
                  <tr><td colSpan={7} className="px-4 py-8 text-center text-[var(--color-text-tertiary)]">
                    Keine Angebote vorhanden. Erstellen Sie ein neues Angebot oben rechts.
                  </td></tr>
                )}
                {filteredQuotes.map(quote => (
                  <tr key={quote.id || quote.quote_number}
                    className="border-b border-[var(--color-divider)] hover:bg-[var(--color-surface-sunken)] transition-colors"
                    data-testid={`quote-row-${quote.quote_number}`}>
                    <td className="px-4 py-2.5">
                      <button onClick={() => setDetail(quote)} className="font-mono text-xs font-semibold text-primary hover:underline"
                        data-testid={`quote-detail-${quote.quote_number}`}>
                        {quote.quote_number}
                      </button>
                    </td>
                    <td className="px-4 py-2.5 text-xs">
                      <div className="font-medium">{quote.applicant_name || '-'}</div>
                      <div className="text-[10px] text-[var(--color-text-tertiary)]">{quote.applicant_number || ''}</div>
                    </td>
                    <td className="px-4 py-2.5 text-xs text-[var(--color-text-secondary)] max-w-[220px] truncate">{quote.description || '-'}</td>
                    <td className="px-4 py-2.5 text-right text-xs font-semibold tabular-nums">{fmtCurrency(quote.amount)}</td>
                    <td className="px-4 py-2.5 text-xs">{fmtDate(quote.valid_until)}</td>
                    <td className="px-4 py-2.5 text-center"><StatusBadge status={quote.status} /></td>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center justify-end gap-1">
                        <button title="PDF" onClick={() => window.open(`/api/quotes/${quote.quote_number}/pdf`, '_blank')}
                          className="p-1.5 rounded hover:bg-[var(--color-surface-sunken)]" data-testid={`quote-pdf-${quote.quote_number}`}>
                          <Download size={13} />
                        </button>
                        <button title="Per E-Mail versenden" onClick={() => handleSend(quote.quote_number)} disabled={sending === quote.quote_number}
                          className="p-1.5 rounded hover:bg-[var(--color-surface-sunken)] disabled:opacity-40" data-testid={`quote-send-${quote.quote_number}`}>
                          {sending === quote.quote_number ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
                        </button>
                        <div className="relative">
                          <button onClick={() => setStatusDropdown(statusDropdown === quote.quote_number ? null : quote.quote_number)}
                            className="p-1.5 rounded hover:bg-[var(--color-surface-sunken)]" data-testid={`quote-status-btn-${quote.quote_number}`}>
                            <ChevronDown size={13} />
                          </button>
                          {statusDropdown === quote.quote_number && (
                            <div className="absolute right-0 z-20 mt-1 w-44 bg-[var(--color-surface)] border border-[var(--color-divider)] rounded-md shadow-lg py-1">
                              {STATUS_OPTIONS.filter(s => s !== quote.status).map(s => (
                                <button key={s} onClick={() => handleStatusChange(quote.quote_number, s)}
                                  className="w-full text-left px-3 py-1.5 text-xs hover:bg-[var(--color-surface-sunken)]"
                                  data-testid={`quote-status-option-${s}`}>
                                  {STATUS_LABELS_DE[s]}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                        {quote.status === 'draft' && (
                          <button title="Loeschen" onClick={() => handleDelete(quote)}
                            className="p-1.5 rounded hover:bg-[var(--color-danger-bg)] text-[var(--color-danger)]"
                            data-testid={`quote-delete-${quote.quote_number}`}>
                            <Trash2 size={13} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Detail Modal */}
      {detail && (
        <div className="w2g-modal-overlay" data-testid="quote-detail-modal" onClick={() => setDetail(null)}>
          <div className="w2g-modal max-w-2xl" onClick={e => e.stopPropagation()}>
            <div className="w2g-modal-header">
              <h2 className="text-lg font-bold text-primary">{detail.quote_number}</h2>
              <button onClick={() => setDetail(null)} className="w2g-btn-icon"><X size={18} /></button>
            </div>
            <div className="w2g-modal-body space-y-4">
              <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] rounded-md p-3 flex items-center justify-between">
                <div>
                  <span className="text-sm font-semibold">{detail.applicant_name}</span>
                  <span className="text-xs text-[var(--color-text-tertiary)] ml-2">{detail.applicant_email}</span>
                </div>
                <StatusBadge status={detail.status} />
              </div>
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div><span className="text-[var(--color-text-tertiary)]">Erstellt: </span>{fmtDate(detail.created_at)}</div>
                <div><span className="text-[var(--color-text-tertiary)]">Gueltig bis: </span>{fmtDate(detail.valid_until)}</div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-[var(--color-divider)] text-[10px] uppercase tracking-wider text-[var(--color-text-secondary)]">
                      <th className="py-2 text-left">Beschreibung</th>
                      <th className="py-2 text-right">Menge</th>
                      <th className="py-2 text-right">Einzelpreis</th>
                      <th className="py-2 text-right">Gesamt</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(detail.items || []).map((item, i) => (
                      <tr key={i} className="border-b border-[var(--color-divider)]">
                        <td className="py-2">{item.description}</td>
                        <td className="py-2 text-right">{item.quantity}</td>
                        <td className="py-2 text-right tabular-nums">{fmtCurrency(item.unit_price)}</td>
                        <td className="py-2 text-right font-semibold tabular-nums">{fmtCurrency((item.quantity || 1) * (item.unit_price || 0))}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="flex justify-end items-baseline gap-2">
                <span className="text-xs text-[var(--color-text-secondary)]">Gesamtbetrag</span>
                <span className="text-lg font-bold text-primary tabular-nums">{fmtCurrency(detail.amount)}</span>
              </div>
              {detail.notes && (
                <p className="text-xs text-[var(--color-text-tertiary)] border-t border-[var(--color-divider)] pt-3">
                  <span className="font-semibold">Hinweise:</span> {detail.notes}
                </p>
              )}
            </div>
            <div className="w2g-modal-footer">
              <button onClick={() => setDetail(null)} className="w2g-btn-secondary">Schliessen</button>
              <button onClick={() => window.open(`/api/quotes/${detail.quote_number}/pdf`, '_blank')}
                className="w2g-btn-primary flex items-center gap-1.5">
                <Download size={14} /> PDF
              </button>
            </div>
          </div>
        </div>
      )}

      {showCreate && (
        <CreateQuoteModal
          applicants={applicants}
          onClose={() => setShowCreate(false)}
          onCreated={() => { setShowCreate(false); fetchData(); }}
        />
      )}
    </PageScaffold>
  );
}
