import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import apiClient from '../../lib/apiClient';
import {
  FileText, Plus, X, XCircle, ChevronDown, RefreshCw,
  Clock, CheckCircle, Send, AlertTriangle, Ban, Settings,
  Download, Search, Edit3, Loader2, Trash2, Mail, CreditCard
} from 'lucide-react';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { TariffSelect } from '../../components/staff/TariffSelect';
import { INVOICE_STATUS_LABELS, getLang } from '../../lib/utils';
import { API } from '../../lib/apiBase';

const STATUS_OPTIONS = ['draft', 'sent', 'paid', 'overdue', 'cancelled'];
const STATUS_LABELS_DE = {
  draft: 'Entwurf', sent: 'Versendet', paid: 'Bezahlt',
  overdue: 'Ueberfaellig', cancelled: 'Storniert',
};
const STATUS_ICONS = { draft: Clock, sent: Send, paid: CheckCircle, overdue: AlertTriangle, cancelled: Ban };
const STATUS_COLORS = {
  draft: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-primary)] border border-[var(--color-divider)]',
  sent: 'bg-[var(--color-info-bg)] text-[var(--color-info)] border border-[var(--color-info-border)]',
  paid: 'bg-[var(--color-success-bg)] text-[var(--color-success)] border border-[var(--color-success-border)]',
  overdue: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning-border)]',
  cancelled: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border border-[var(--color-danger-border)]',
};

function StatusBadge({ status }) {
  const Icon = STATUS_ICONS[status] || Clock;
  return (
    <span className={`w2g-status text-[11px] font-semibold ${STATUS_COLORS[status] || STATUS_COLORS.draft}`}
          data-testid={`invoice-status-${status}`}>
      <Icon size={11} />
      {STATUS_LABELS_DE[status] || status}
    </span>
  );
}

/* ═══════ Line Items Editor ═══════ */
function LineItemsEditor({ items, onChange, products }) {
  const addItem = () => {
    onChange([...items, { description: '', quantity: 1, unit_price: 0 }]);
  };

  const addProduct = (product) => {
    const emptyOnly = items.length === 1 && !items[0].description && !parseFloat(items[0].unit_price);
    const newItem = { description: product.name, quantity: 1, unit_price: product.price };
    onChange(emptyOnly ? [newItem] : [...items, newItem]);
  };

  const updateItem = (idx, field, value) => {
    const updated = items.map((item, i) => i === idx ? { ...item, [field]: value } : item);
    onChange(updated);
  };

  const removeItem = (idx) => {
    if (items.length <= 1) return;
    onChange(items.filter((_, i) => i !== idx));
  };

  const total = items.reduce((sum, item) => sum + (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0), 0);

  const fmtEur = (val) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(val);

  return (
    <div className="space-y-3" data-testid="line-items-editor">
      <div className="flex items-center justify-between">
        <label className="w2g-label mb-0">Positionen</label>
        <button type="button" onClick={addItem}
          className="text-[11px] bg-[var(--color-primary)] text-white px-2.5 py-1 rounded-sm hover:bg-[rgba(10,25,47,0.9)] font-medium flex items-center gap-1"
          data-testid="add-line-item-btn">
          <Plus size={12} /> Position
        </button>
      </div>

      {products?.length > 0 && (
        <TariffSelect products={products} onSelect={addProduct} testId="invoice-tariff-select" />
      )}

      {/* Table Header */}
      <div className="grid grid-cols-[1fr_80px_100px_90px_32px] gap-2 text-[10px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider px-1">
        <span>Beschreibung</span>
        <span className="text-right">Menge</span>
        <span className="text-right">Einzelpreis</span>
        <span className="text-right">Gesamt</span>
        <span></span>
      </div>

      {/* Items */}
      {items.map((item, idx) => {
        const lineTotal = (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0);
        return (
          <div key={idx} className="grid grid-cols-[1fr_80px_100px_90px_32px] gap-2 items-center" data-testid={`line-item-${idx}`}>
            <input type="text" value={item.description}
              onChange={e => updateItem(idx, 'description', e.target.value)}
              placeholder="Leistungsbeschreibung..."
              className="w2g-input text-xs py-1.5"
              data-testid={`line-item-desc-${idx}`} />
            <input type="number" min="1" step="1" value={item.quantity}
              onChange={e => updateItem(idx, 'quantity', e.target.value)}
              className="w2g-input text-xs py-1.5 text-right"
              data-testid={`line-item-qty-${idx}`} />
            <input type="number" min="0" step="0.01" value={item.unit_price}
              onChange={e => updateItem(idx, 'unit_price', e.target.value)}
              className="w2g-input text-xs py-1.5 text-right"
              data-testid={`line-item-price-${idx}`} />
            <span className="text-xs font-medium text-[var(--color-text-primary)] text-right tabular-nums">{fmtEur(lineTotal)}</span>
            <button type="button" onClick={() => removeItem(idx)}
              disabled={items.length <= 1}
              className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              data-testid={`remove-line-item-${idx}`}>
              <Trash2 size={13} />
            </button>
          </div>
        );
      })}

      {/* Summe */}
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

/* ═══════ Create Invoice Modal ═══════ */
function CreateInvoiceModal({ onClose, onCreated, applicants, products }) {
  const [form, setForm] = useState({
    applicant_id: '', description: '', due_date: '',
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.applicant_id || !form.due_date || form.items.every(i => !i.description)) return;
    setSaving(true);
    try {
      const desc = form.items.map(i => i.description).filter(Boolean).join(', ') || form.description;
      const res = await apiClient.post('/api/invoices', {
        applicant_id: form.applicant_id,
        description: desc,
        amount: Math.round(total * 100) / 100,
        due_date: form.due_date,
        items: form.items.map(i => ({
          description: i.description,
          quantity: parseFloat(i.quantity) || 1,
          unit_price: parseFloat(i.unit_price) || 0,
        })),
      });
      toast.success('Rechnung erstellt');
      onCreated(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler');
    } finally { setSaving(false); }
  };

  return (
    <div className="w2g-modal-overlay" data-testid="create-invoice-modal">
      <div className="w2g-modal max-w-2xl">
        <div className="w2g-modal-header">
          <h2 className="text-lg font-bold text-primary">Neue Rechnung</h2>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="close-create-invoice"><X size={18} /></button>
        </div>
        <form onSubmit={handleSubmit} className="w2g-modal-body space-y-5">
          {/* Applicant Search */}
          <div className="relative">
            <label className="w2g-label">Bewerber</label>
            {selectedApplicant ? (
              <div className="w2g-input flex items-center justify-between" data-testid="invoice-applicant-selected">
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
                    data-testid="invoice-applicant-search" />
                </div>
                {showDropdown && (
                  <div className="absolute z-50 mt-1 w-full bg-white border border-[var(--color-divider)] rounded-md shadow-lg max-h-48 overflow-y-auto"
                    data-testid="invoice-applicant-dropdown">
                    {filtered.length === 0 ? (
                      <p className="px-3 py-2 text-xs text-[var(--color-text-tertiary)]">Keine Ergebnisse</p>
                    ) : (
                      filtered.slice(0, 50).map(a => (
                        <button key={a.id} type="button"
                          onClick={() => { setForm(f => ({...f, applicant_id: a.id})); setShowDropdown(false); setSearch(a.full_name || a.email); }}
                          className="w-full text-left px-3 py-2 hover:bg-[var(--color-surface-elevated)] border-b border-[var(--color-divider-subtle)] last:border-0"
                          data-testid={`applicant-option-${a.id}`}>
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

          {/* Due Date */}
          <div>
            <label className="w2g-label">Faelligkeitsdatum</label>
            <input type="date" value={form.due_date} onChange={e => setForm(f => ({...f, due_date: e.target.value}))}
              className="w2g-input" data-testid="invoice-due-date-input" required />
          </div>

          {/* Line Items */}
          <LineItemsEditor items={form.items} products={products} onChange={items => setForm(f => ({...f, items}))} />
        </form>
        <div className="w2g-modal-footer">
          <button type="button" onClick={onClose} className="w2g-btn-secondary">Abbrechen</button>
          <button type="submit" disabled={saving || !form.applicant_id || !form.due_date} onClick={handleSubmit}
            className="w2g-btn-primary" data-testid="invoice-submit-btn">
            {saving ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
            Rechnung erstellen
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════ Invoice Settings Panel ═══════ */
function InvoiceSettingsPanel({ onClose }) {
  const [cfg, setCfg] = useState({ prefix: 'INV', start_number: 1, suffix: '', include_date: true, preview: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    apiClient.get('/api/invoices/settings').then(r => setCfg(r.data)).catch(() => {});
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const r = await apiClient.put('/api/invoices/settings', {
        prefix: cfg.prefix, start_number: cfg.start_number, suffix: cfg.suffix, include_date: cfg.include_date,
      });
      setCfg(r.data);
      toast.success('Einstellungen gespeichert');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler');
    } finally { setSaving(false); }
  };

  return (
    <div className="w2g-modal-overlay" data-testid="invoice-settings-modal">
      <div className="w2g-modal max-w-md">
        <div className="w2g-modal-header">
          <h2 className="text-lg font-bold text-primary">Rechnungsnummern</h2>
          <button onClick={onClose} className="w2g-btn-icon"><X size={18} /></button>
        </div>
        <div className="w2g-modal-body space-y-4">
          <div>
            <label className="w2g-label">Praefix</label>
            <input type="text" value={cfg.prefix} onChange={e => setCfg(c => ({...c, prefix: e.target.value.toUpperCase()}))}
              className="w2g-input" data-testid="invoice-prefix-input" maxLength={10} />
          </div>
          <div>
            <label className="w2g-label">Startnummer</label>
            <input type="number" min={1} value={cfg.start_number} onChange={e => setCfg(c => ({...c, start_number: parseInt(e.target.value) || 1}))}
              className="w2g-input" data-testid="invoice-start-input" />
          </div>
          <div>
            <label className="w2g-label">Suffix</label>
            <input type="text" value={cfg.suffix} onChange={e => setCfg(c => ({...c, suffix: e.target.value.toUpperCase()}))}
              className="w2g-input" data-testid="invoice-suffix-input" maxLength={10} placeholder="z.B. AC" />
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={cfg.include_date} onChange={e => setCfg(c => ({...c, include_date: e.target.checked}))}
              className="rounded text-primary" />
            <span className="text-sm text-[var(--color-text-primary)]">Datum einbeziehen (YYYYMM)</span>
          </label>
          <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] rounded-md p-3">
            <p className="text-xs text-[var(--color-text-secondary)] mb-1">Vorschau naechste Nummer:</p>
            <p className="text-sm font-mono font-bold text-primary" data-testid="invoice-number-preview">{cfg.preview || '...'}</p>
          </div>
        </div>
        <div className="w2g-modal-footer">
          <button onClick={onClose} className="w2g-btn-secondary">Abbrechen</button>
          <button onClick={handleSave} disabled={saving} className="w2g-btn-primary" data-testid="save-invoice-settings-btn">
            {saving ? <Loader2 size={14} className="animate-spin" /> : null} Speichern
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════ Edit Invoice Modal (Line Items) ═══════ */
function EditInvoiceModal({ invoice, onClose, onSaved, products }) {
  const initialItems = invoice?.items?.length
    ? invoice.items.map(i => ({
        description: i.description || '',
        quantity: i.quantity || 1,
        unit_price: i.unit_price || 0,
      }))
    : [{ description: invoice?.description || '', quantity: 1, unit_price: invoice?.amount || 0 }];

  const [form, setForm] = useState({
    description: invoice?.description || '',
    due_date: invoice?.due_date?.split('T')[0] || '',
    notes: invoice?.notes || '',
    items: initialItems,
  });
  const [saving, setSaving] = useState(false);

  const total = form.items.reduce((s, i) => s + (parseFloat(i.quantity) || 0) * (parseFloat(i.unit_price) || 0), 0);

  const handleSave = async () => {
    setSaving(true);
    try {
      const desc = form.items.map(i => i.description).filter(Boolean).join(', ') || form.description;
      await apiClient.patch(`/api/invoices/${invoice.invoice_number}`, {
        description: desc,
        amount: Math.round(total * 100) / 100,
        due_date: form.due_date,
        notes: form.notes,
        items: form.items.map(i => ({
          description: i.description,
          quantity: parseFloat(i.quantity) || 1,
          unit_price: parseFloat(i.unit_price) || 0,
        })),
      });
      toast.success('Rechnung aktualisiert');
      onSaved();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler');
    } finally { setSaving(false); }
  };

  return (
    <div className="w2g-modal-overlay" data-testid="edit-invoice-modal">
      <div className="w2g-modal max-w-2xl">
        <div className="w2g-modal-header">
          <h2 className="text-lg font-bold text-primary">Rechnung bearbeiten</h2>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="close-edit-invoice"><X size={18} /></button>
        </div>
        <div className="w2g-modal-body space-y-5">
          {/* Header info */}
          <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] rounded-md p-3 flex items-center justify-between">
            <div>
              <span className="font-mono text-sm font-bold text-primary">{invoice.invoice_number}</span>
              <span className="text-xs text-[var(--color-text-tertiary)] ml-3">{invoice.applicant_name}</span>
            </div>
            <StatusBadge status={invoice.status} />
          </div>

          {/* Due Date + Notes */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="w2g-label">Faelligkeitsdatum</label>
              <input type="date" value={form.due_date}
                onChange={e => setForm(f => ({...f, due_date: e.target.value}))}
                className="w2g-input" data-testid="edit-invoice-due-date" />
            </div>
            <div>
              <label className="w2g-label">Interne Notizen</label>
              <input type="text" value={form.notes}
                onChange={e => setForm(f => ({...f, notes: e.target.value}))}
                className="w2g-input" data-testid="edit-invoice-notes" placeholder="Anmerkungen..." />
            </div>
          </div>

          {/* Line Items */}
          <LineItemsEditor items={form.items} products={products} onChange={items => setForm(f => ({...f, items}))} />
        </div>
        <div className="w2g-modal-footer">
          <button onClick={onClose} className="w2g-btn-secondary">Abbrechen</button>
          <button onClick={handleSave} disabled={saving} className="w2g-btn-primary" data-testid="save-edit-invoice-btn">
            {saving ? <Loader2 size={14} className="animate-spin" /> : null} Speichern
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════ Main Invoices Page ═══════ */
export default function StaffInvoicesPage() {
  const [invoices, setInvoices] = useState([]);
  const [stats, setStats] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [editInvoice, setEditInvoice] = useState(null);
  const [filter, setFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusDropdown, setStatusDropdown] = useState(null);
  const [sendingInvoice, setSendingInvoice] = useState(null);
  const [checkoutLoading, setCheckoutLoading] = useState(null);

  // Stripe payment success detection
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const payment = params.get('payment');
    const sessionId = params.get('session_id');
    if (payment === 'success' && sessionId) {
      apiClient.get(`/api/payments/status/${sessionId}`)
        .then(r => {
          if (r.data.payment_status === 'paid') {
            toast.success(`Zahlung erfolgreich: ${r.data.invoice_number}`);
            fetchData();
          }
        })
        .catch(() => {});
      window.history.replaceState({}, '', window.location.pathname);
    } else if (payment === 'cancelled') {
      toast.info('Zahlung abgebrochen');
      window.history.replaceState({}, '', window.location.pathname);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = filter ? `?status=${filter}` : '';
      const [invRes, statsRes] = await Promise.all([
        apiClient.get(`/api/invoices${params}`),
        apiClient.get('/api/invoices/stats'),
      ]);
      setInvoices(invRes.data);
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

  const handleStatusChange = async (invoiceNumber, newStatus) => {
    try {
      await apiClient.patch(`/api/invoices/${invoiceNumber}`, { status: newStatus });
      toast.success(`Status: ${STATUS_LABELS_DE[newStatus]}`);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler');
    }
    setStatusDropdown(null);
  };

  const handleSendInvoice = async (invoiceNumber) => {
    setSendingInvoice(invoiceNumber);
    try {
      await apiClient.post(`/api/invoices/${invoiceNumber}/send`, {}, { withCredentials: true });
      toast.success('Rechnung per E-Mail versendet');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Versand fehlgeschlagen');
    } finally { setSendingInvoice(null); }
  };

  const fmtCurrency = (amount, currency = 'EUR') =>
    new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(amount);

  const handleStripeCheckout = async (invoiceNumber) => {
    setCheckoutLoading(invoiceNumber);
    try {
      const res = await apiClient.post('/api/payments/checkout', {
        invoice_number: invoiceNumber,
        origin_url: window.location.origin,
      });
      if (res.data.url) {
        window.open(res.data.url, '_blank');
        toast.success('Stripe-Checkout geoeffnet');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Checkout fehlgeschlagen');
    } finally { setCheckoutLoading(null); }
  };

  const fmtDate = (iso) => {
    if (!iso) return '-';
    try { return new Date(iso).toLocaleDateString('de-DE'); } catch { return iso; }
  };

  const q = searchTerm.toLowerCase();
  const filteredInvoices = q
    ? invoices.filter(i =>
        (i.invoice_number || '').toLowerCase().includes(q) ||
        (i.applicant_name || '').toLowerCase().includes(q) ||
        (i.applicant_email || '').toLowerCase().includes(q) ||
        (i.applicant_number || '').toLowerCase().includes(q) ||
        (i.description || '').toLowerCase().includes(q)
      )
    : invoices;

  return (
    <PageScaffold
      title="Rechnungen"
      subtitle="Verwaltung, Positionen, Versand"
      testId="staff-invoices-page"
      actions={
        <div className="flex items-center gap-2">
          <button onClick={() => setShowSettings(true)} className="w2g-btn-icon" data-testid="invoice-settings-btn" title="Einstellungen">
            <Settings size={16} />
          </button>
          <button onClick={fetchData} className="w2g-btn-icon" data-testid="refresh-invoices" title="Aktualisieren">
            <RefreshCw size={16} />
          </button>
          <button onClick={() => setShowCreate(true)} className="w2g-btn-primary" data-testid="create-invoice-btn">
            <Plus size={16} /> Neue Rechnung
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
                className="w2g-search pl-9" data-testid="invoice-search" />
              {searchTerm && (
                <button onClick={() => setSearchTerm('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]">
                  <XCircle size={14} />
                </button>
              )}
            </div>
          }
          filters={['', 'draft', 'sent', 'paid', 'overdue', 'cancelled'].map(s => (
            <button key={s} onClick={() => setFilter(s)}
              className={filter === s ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}
              data-testid={`filter-${s || 'all'}`}>
              {s ? STATUS_LABELS_DE[s] : 'Alle'}
            </button>
          ))}
        />
      }
    >
      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3" data-testid="invoice-stats">
          <Card className="border-l-[3px] border-l-[var(--color-primary)]">
            <CardContent className="px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--color-text-tertiary)]">Gesamt</p>
              <p className="text-xl font-extrabold text-[var(--color-primary)] mt-1 tabular-nums" style={{ fontFamily: 'var(--font-heading)' }}>{fmtCurrency(stats.total_amount)}</p>
              <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1">{stats.total_count} Rechnungen</p>
            </CardContent>
          </Card>
          {['draft', 'sent', 'paid', 'overdue'].map(s => {
            const data = stats.by_status?.[s];
            if (!data) return null;
            return (
              <Card key={s} className="cursor-pointer hover:shadow-[var(--shadow-e2)] transition-shadow" onClick={() => setFilter(filter === s ? '' : s)}>
                <CardContent className="px-4 py-3">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--color-text-tertiary)]">{STATUS_LABELS_DE[s]}</p>
                  <p className="text-xl font-bold text-[var(--color-text-primary)] mt-1 tabular-nums">{fmtCurrency(data.total)}</p>
                  <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1">{data.count} Rechnung{data.count !== 1 ? 'en' : ''}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="w2g-loading" data-testid="invoices-loading"><div className="w2g-spinner"></div></div>
      ) : error ? (
        <div className="text-center py-12 text-[var(--color-danger)]" data-testid="invoices-error">
          <AlertTriangle size={24} className="mx-auto mb-2" />
          <p className="text-sm">{error}</p>
        </div>
      ) : filteredInvoices.length === 0 ? (
        <div className="w2g-empty" data-testid="invoices-empty">
          <FileText size={32} className="w2g-empty-icon" />
          <p className="w2g-empty-text">{searchTerm ? 'Keine Treffer' : 'Keine Rechnungen vorhanden'}</p>
          <p className="w2g-empty-hint">{!searchTerm && 'Erstellen Sie eine neue Rechnung oben rechts.'}</p>
        </div>
      ) : (
        <Card className="p-0 overflow-hidden" data-testid="invoices-table">
          <table className="w2g-table">
            <thead>
              <tr>
                <th>Rechnungsnr.</th>
                <th>Bewerber</th>
                <th>Beschreibung</th>
                <th>Pos.</th>
                <th className="text-right">Betrag</th>
                <th>Status</th>
                <th>Faelligkeit</th>
                <th className="text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {filteredInvoices.map(inv => (
                <tr key={inv.invoice_number || inv.id} data-testid={`invoice-row-${inv.invoice_number}`}>
                  <td className="font-mono text-xs text-primary font-medium">{inv.invoice_number}</td>
                  <td>
                    <p className="font-medium text-[var(--color-text-primary)] text-sm">{inv.applicant_name}</p>
                    <div className="flex items-center gap-2">
                      {inv.applicant_number && <span className="text-[10px] font-mono text-primary font-bold">{inv.applicant_number}</span>}
                      <p className="text-[10px] text-[var(--color-text-tertiary)]">{inv.applicant_email}</p>
                    </div>
                  </td>
                  <td className="text-[var(--color-text-secondary)] max-w-[180px] truncate text-xs">{inv.description}</td>
                  <td className="text-xs text-[var(--color-text-secondary)] tabular-nums">{inv.items?.length || 1}</td>
                  <td className="text-right font-medium text-[var(--color-text-primary)]">{fmtCurrency(inv.amount, inv.currency)}</td>
                  <td><StatusBadge status={inv.status} /></td>
                  <td className="text-xs text-[var(--color-text-secondary)]">{fmtDate(inv.due_date)}</td>
                  <td className="text-right">
                    <div className="flex items-center justify-end gap-1 relative">
                      <button onClick={() => setEditInvoice(inv)}
                        className="w2g-btn-icon" title="Bearbeiten"
                        data-testid={`edit-invoice-${inv.invoice_number}`}>
                        <Edit3 size={14} />
                      </button>
                      <a href={`${API}/api/invoices/${inv.invoice_number}/pdf`}
                        target="_blank" rel="noreferrer" className="w2g-btn-icon" title="PDF Download"
                        data-testid={`download-pdf-${inv.invoice_number}`}>
                        <Download size={14} />
                      </a>
                      {inv.applicant_email && inv.status !== 'cancelled' && (
                        <button onClick={() => handleSendInvoice(inv.invoice_number)}
                          disabled={sendingInvoice === inv.invoice_number}
                          className="w2g-btn-icon" title="Per E-Mail senden"
                          data-testid={`send-invoice-${inv.invoice_number}`}>
                          {sendingInvoice === inv.invoice_number
                            ? <Loader2 size={14} className="animate-spin" />
                            : <Mail size={14} />
                          }
                        </button>
                      )}
                      {(inv.status === 'sent' || inv.status === 'overdue') && (
                        <button onClick={() => handleStripeCheckout(inv.invoice_number)}
                          disabled={checkoutLoading === inv.invoice_number}
                          className="w2g-btn-icon" title="Stripe-Zahlung"
                          data-testid={`stripe-pay-${inv.invoice_number}`}>
                          {checkoutLoading === inv.invoice_number
                            ? <Loader2 size={14} className="animate-spin" />
                            : <CreditCard size={14} />
                          }
                        </button>
                      )}
                      <button onClick={() => setStatusDropdown(statusDropdown === inv.invoice_number ? null : inv.invoice_number)}
                        className="w2g-btn-icon" title="Status aendern"
                        data-testid={`status-change-btn-${inv.invoice_number}`}>
                        <ChevronDown size={14} />
                      </button>
                      {statusDropdown === inv.invoice_number && (
                        <>
                          <div className="fixed inset-0 z-40" onClick={() => setStatusDropdown(null)} />
                          <div className="absolute right-0 top-full mt-1 bg-white border border-[var(--color-divider)] rounded-md shadow-lg z-50 min-w-[150px]"
                               data-testid={`status-dropdown-${inv.invoice_number}`}>
                            {STATUS_OPTIONS.filter(s => s !== inv.status).map(s => (
                              <button key={s} onClick={() => handleStatusChange(inv.invoice_number, s)}
                                className="w-full text-left px-3 py-2 text-xs hover:bg-[var(--color-surface-elevated)] flex items-center gap-2"
                                data-testid={`set-status-${s}`}>
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
        <CreateInvoiceModal applicants={applicants} products={products}
          onClose={() => setShowCreate(false)}
          onCreated={() => { setShowCreate(false); fetchData(); }} />
      )}
      {showSettings && <InvoiceSettingsPanel onClose={() => setShowSettings(false)} />}
      {editInvoice && (
        <EditInvoiceModal invoice={editInvoice} products={products}
          onClose={() => setEditInvoice(null)}
          onSaved={() => { setEditInvoice(null); fetchData(); }} />
      )}
    </PageScaffold>
  );
}
