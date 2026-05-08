import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { X, Search, Plus, Trash2, Send, FileText, Loader2, Receipt } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { toast } from 'sonner';

const CATEGORIES = {
  kurs: 'Kurse',
  sprache: 'Sprache',
  pruefung: 'Pruefungen',
  gebuehr: 'Gebuehren',
  service: 'Services',
  unterkunft: 'Unterkunft',
  kombi: 'Kombi-Pakete',
  sonstig: 'Sonstiges',
};

export default function InvoiceCreateModal({ applicant, onClose, onCreated }) {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [items, setItems] = useState([]);
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState(() => {
    const d = new Date(); d.setDate(d.getDate() + 14);
    return d.toISOString().split('T')[0];
  });
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      apiClient.get('/api/products', { withCredentials: true }).then(r => r.data).catch(() => []),
      apiClient.get(`/api/invoices?applicant_id=${applicant?.id || ''}`, { withCredentials: true }).then(r => r.data).catch(() => []),
    ]).then(([prods, invs]) => {
      setProducts(prods || []);
      setHistory(Array.isArray(invs) ? invs : invs?.invoices || []);
    }).finally(() => setLoading(false));
  }, [applicant?.id]);

  const filtered = useMemo(() => {
    if (!search.trim()) return products;
    const q = search.toLowerCase();
    return products.filter(p =>
      p.name?.toLowerCase().includes(q) ||
      p.code?.toLowerCase().includes(q) ||
      p.description?.toLowerCase().includes(q) ||
      CATEGORIES[p.category]?.toLowerCase().includes(q)
    );
  }, [products, search]);

  const grouped = useMemo(() => {
    const groups = {};
    filtered.forEach(p => {
      const cat = p.category || 'sonstig';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(p);
    });
    return groups;
  }, [filtered]);

  const addProduct = useCallback((product) => {
    if (product.code === 'CUSTOM') {
      setItems(prev => [...prev, { description: '', quantity: 1, unit_price: 0, custom: true }]);
    } else {
      setItems(prev => [...prev, {
        description: product.name,
        quantity: 1,
        unit_price: product.price,
        code: product.code,
      }]);
    }
    setSearch('');
  }, []);

  const updateItem = useCallback((idx, field, value) => {
    setItems(prev => prev.map((item, i) => i === idx ? { ...item, [field]: value } : item));
  }, []);

  const removeItem = useCallback((idx) => {
    setItems(prev => prev.filter((_, i) => i !== idx));
  }, []);

  const total = useMemo(() => items.reduce((sum, i) => sum + (i.quantity || 1) * (i.unit_price || 0), 0), [items]);

  const handleSubmit = async (sendNow = false) => {
    if (items.length === 0) { toast.error('Mindestens eine Position hinzufuegen'); return; }
    if (!dueDate) { toast.error('Faelligkeitsdatum angeben'); return; }
    setSubmitting(true);
    try {
      const payload = {
        applicant_id: applicant?.id,
        application_id: applicant?.application_id,
        description: description || items.map(i => i.description).join(', '),
        amount: total,
        due_date: dueDate,
        currency: 'EUR',
        items: items.map(i => ({
          description: i.description,
          quantity: i.quantity || 1,
          unit_price: i.unit_price || 0,
        })),
      };
      const res = await apiClient.post('/api/invoices', payload, { withCredentials: true });
      if (sendNow && res.data?.id) {
        await apiClient.patch(`/api/invoices/${res.data.id}`, { status: 'sent' }, { withCredentials: true }).catch(() => {});
        toast.success('Rechnung erstellt und versendet');
      } else {
        toast.success('Rechnung als Entwurf gespeichert');
      }
      onCreated?.();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Erstellen der Rechnung');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w2g-modal-overlay" data-testid="invoice-create-modal">
      <div className="w2g-modal" style={{ maxWidth: '900px' }}>
        <div className="w2g-modal-header">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-[var(--color-accent)] flex items-center justify-center" style={{ borderRadius: 'var(--radius-sm)' }}>
              <Receipt size={18} className="text-[var(--color-primary-dark)]" />
            </div>
            <div>
              <h2 className="text-base font-bold text-[var(--color-primary)]">Rechnung erstellen</h2>
              <p className="text-xs text-[var(--color-text-secondary)]">
                {applicant?.full_name || 'Unbekannt'}
                {applicant?.applicant_number ? ` (${applicant.applicant_number})` : ''}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="invoice-modal-close"><X size={18} /></button>
        </div>

        <div className="flex flex-col lg:flex-row" style={{ maxHeight: 'calc(90vh - 160px)' }}>
          {/* Linke Seite: Positionen */}
          <div className="flex-1 p-5 overflow-y-auto border-r border-[var(--color-divider-subtle)]">
            {/* Produkt-Suche */}
            <div className="mb-4">
              <label className="w2g-label">Paket / Leistung hinzufuegen</label>
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
                <input value={search} onChange={e => setSearch(e.target.value)}
                  placeholder="Suchen: Kurs, Paket, Service..."
                  className="w2g-input pl-9" data-testid="invoice-product-search" />
              </div>
              {search && (
                <div className="mt-1.5 max-h-[240px] overflow-y-auto border border-[var(--color-divider)] bg-white"
                  style={{ borderRadius: 'var(--radius-sm)', boxShadow: 'var(--shadow-e2)' }}>
                  {Object.entries(grouped).map(([cat, prods]) => (
                    <div key={cat}>
                      <div className="px-3 py-1.5 bg-[var(--color-surface-sunken)] text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">
                        {CATEGORIES[cat] || cat}
                      </div>
                      {prods.map(p => (
                        <button key={p.code} onClick={() => addProduct(p)}
                          data-testid={`invoice-product-${p.code}`}
                          className="w-full flex items-center justify-between px-3 py-2.5 text-left hover:bg-[var(--color-accent-subtle)] transition-colors text-sm">
                          <div className="min-w-0">
                            <p className="font-semibold text-[var(--color-text-primary)] truncate">{p.name}</p>
                            <p className="text-[11px] text-[var(--color-text-tertiary)]">{p.code}</p>
                          </div>
                          <span className="text-sm font-bold text-[var(--color-primary)] tabular-nums shrink-0 ml-3">
                            {p.price > 0 ? `${p.price.toLocaleString('de-DE')} EUR` : 'Individuell'}
                          </span>
                        </button>
                      ))}
                    </div>
                  ))}
                  {filtered.length === 0 && <p className="px-3 py-4 text-center text-sm text-[var(--color-text-tertiary)]">Keine Ergebnisse</p>}
                </div>
              )}
            </div>

            {/* Positionen */}
            <div className="space-y-2 mb-4">
              <div className="flex items-center justify-between">
                <label className="w2g-label mb-0">Rechnungspositionen</label>
                <button onClick={() => addProduct({ code: 'CUSTOM' })} className="w2g-btn-ghost text-xs" data-testid="invoice-add-custom">
                  <Plus size={12} /> Freie Position
                </button>
              </div>
              {items.length === 0 ? (
                <div className="py-8 text-center border border-dashed border-[var(--color-divider)] bg-[var(--color-surface-sunken)]" style={{ borderRadius: 'var(--radius-sm)' }}>
                  <FileText size={24} className="mx-auto mb-2 text-[var(--color-text-tertiary)]" />
                  <p className="text-sm text-[var(--color-text-tertiary)]">Produkt/Paket oben suchen und hinzufuegen</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {items.map((item, idx) => (
                    <div key={idx} className="flex items-start gap-2 p-3 bg-[var(--color-surface-elevated)] border border-[var(--color-divider-subtle)]"
                      style={{ borderRadius: 'var(--radius-sm)' }} data-testid={`invoice-item-${idx}`}>
                      <div className="flex-1 min-w-0 space-y-2">
                        {item.custom ? (
                          <input value={item.description} onChange={e => updateItem(idx, 'description', e.target.value)}
                            placeholder="Beschreibung..." className="w2g-input text-sm" />
                        ) : (
                          <p className="text-sm font-semibold text-[var(--color-text-primary)]">{item.description}</p>
                        )}
                        <div className="flex items-center gap-3">
                          <div className="w-20">
                            <label className="text-[10px] text-[var(--color-text-tertiary)]">Menge</label>
                            <input type="number" min="1" value={item.quantity}
                              onChange={e => updateItem(idx, 'quantity', parseInt(e.target.value) || 1)}
                              className="w2g-input text-sm text-center" />
                          </div>
                          <div className="w-28">
                            <label className="text-[10px] text-[var(--color-text-tertiary)]">Einzelpreis (EUR)</label>
                            <input type="number" min="0" step="0.01" value={item.unit_price}
                              onChange={e => updateItem(idx, 'unit_price', parseFloat(e.target.value) || 0)}
                              className="w2g-input text-sm text-right" />
                          </div>
                          <div className="w-24 text-right pt-4">
                            <span className="text-sm font-bold text-[var(--color-primary)] tabular-nums">
                              {((item.quantity || 1) * (item.unit_price || 0)).toLocaleString('de-DE')} EUR
                            </span>
                          </div>
                        </div>
                      </div>
                      <button onClick={() => removeItem(idx)} className="w2g-btn-icon mt-1" data-testid={`invoice-remove-${idx}`}>
                        <Trash2 size={14} className="text-[var(--color-danger)]" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Zusammenfassung */}
            {items.length > 0 && (
              <div className="p-4 bg-[var(--color-primary)] text-white" style={{ borderRadius: 'var(--radius-sm)' }}>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Gesamtbetrag</span>
                  <span className="text-xl font-bold tabular-nums" data-testid="invoice-total">{total.toLocaleString('de-DE')} EUR</span>
                </div>
              </div>
            )}

            {/* Meta */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
              <div>
                <label className="w2g-label">Beschreibung (optional)</label>
                <input value={description} onChange={e => setDescription(e.target.value)}
                  placeholder="z.B. T-Kurs WS 2026/27" className="w2g-input text-sm" data-testid="invoice-description" />
              </div>
              <div>
                <label className="w2g-label">Faellig am</label>
                <input type="date" value={dueDate} onChange={e => setDueDate(e.target.value)}
                  className="w2g-input text-sm" data-testid="invoice-due-date" />
              </div>
            </div>
          </div>

          {/* Rechte Seite: History */}
          <div className="w-full lg:w-[280px] p-4 overflow-y-auto bg-[var(--color-surface-sunken)] shrink-0">
            <h3 className="w2g-section-heading mb-3"><FileText size={13} /> Rechnungs-Historie</h3>
            {loading ? (
              <div className="py-6 text-center"><Loader2 size={18} className="animate-spin mx-auto text-[var(--color-accent)]" /></div>
            ) : history.length === 0 ? (
              <p className="text-xs text-[var(--color-text-tertiary)] text-center py-4">Noch keine Rechnungen</p>
            ) : (
              <div className="space-y-2">
                {history.slice(0, 10).map((inv, i) => (
                  <div key={inv.id || i} className="p-3 bg-white border border-[var(--color-divider-subtle)]"
                    style={{ borderRadius: 'var(--radius-xs)' }}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[11px] font-bold text-[var(--color-primary)]">{inv.invoice_number || `#${i + 1}`}</span>
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 ${
                        inv.status === 'paid' ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]' :
                        inv.status === 'sent' ? 'bg-[var(--color-info-bg)] text-[var(--color-info)]' :
                        inv.status === 'overdue' ? 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]' :
                        'bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)]'
                      }`} style={{ borderRadius: 'var(--radius-xs)' }}>
                        {inv.status === 'paid' ? 'Bezahlt' : inv.status === 'sent' ? 'Versendet' :
                         inv.status === 'overdue' ? 'Ueberfaellig' : inv.status === 'draft' ? 'Entwurf' : inv.status}
                      </span>
                    </div>
                    <p className="text-xs text-[var(--color-text-secondary)] truncate">{inv.description || '-'}</p>
                    <p className="text-sm font-bold text-[var(--color-primary)] tabular-nums mt-1">{(inv.amount || 0).toLocaleString('de-DE')} EUR</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="w2g-modal-footer">
          <button onClick={onClose} className="w2g-btn-outline" data-testid="invoice-cancel">Abbrechen</button>
          <button onClick={() => handleSubmit(false)} disabled={submitting || items.length === 0}
            className="w2g-btn-secondary" data-testid="invoice-save-draft">
            {submitting ? <Loader2 size={14} className="animate-spin" /> : <FileText size={14} />} Entwurf speichern
          </button>
          <button onClick={() => handleSubmit(true)} disabled={submitting || items.length === 0}
            className="w2g-btn-primary" data-testid="invoice-send">
            {submitting ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />} Erstellen & Senden
          </button>
        </div>
      </div>
    </div>
  );
}
