import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { FileText, Download, CreditCard, CheckCircle, Clock, AlertTriangle, HelpCircle, ArrowRight, Info, MessageCircle, Shield } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';
import { formatCurrency, formatDate } from '../../lib/utils';

const STATUS_MAP = {
  open: { color: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]', icon: Clock, de: 'Offen', en: 'Open' },
  overdue: { color: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]', icon: AlertTriangle, de: 'Ueberfaellig', en: 'Overdue' },
  paid: { color: 'bg-[var(--color-success-bg)] text-[var(--color-success)]', icon: CheckCircle, de: 'Bezahlt', en: 'Paid' },
  cancelled: { color: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]', icon: FileText, de: 'Storniert', en: 'Cancelled' },
};

const PURPOSE_MAP = {
  de: {
    'Studienkolleg': 'Gebuehr fuer deine Studienkolleg-Platzreservierung und Kursanmeldung.',
    'Sprachkurs': 'Gebuehr fuer deinen Deutsch-Sprachkurs.',
    'Anmeldegebuehr': 'Einmalige Anmeldegebuehr fuer die Bearbeitung deiner Bewerbung.',
    '_default': 'Gebuehr im Rahmen deiner Bewerbung beim Studienkolleg Aachen.',
  },
  en: {
    'Studienkolleg': 'Fee for your Studienkolleg placement reservation and course enrollment.',
    'Sprachkurs': 'Fee for your German language course.',
    'Anmeldegebuehr': 'One-time registration fee for processing your application.',
    '_default': 'Fee as part of your application at Studienkolleg Aachen.',
  },
};

function getInvoicePurpose(description, lang) {
  const map = PURPOSE_MAP[lang] || PURPOSE_MAP.de;
  for (const [key, val] of Object.entries(map)) {
    if (key !== '_default' && description?.toLowerCase().includes(key.toLowerCase())) return val;
  }
  return map._default;
}

export default function FinancialsPage() {
  const { i18n } = useTranslation();
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const lang = i18n.language === 'en' ? 'en' : 'de';

  useEffect(() => {
    const load = async () => {
      try {
        const res = await apiClient.get('/api/invoices/my', { withCredentials: true });
        setInvoices(res.data || []);
      } catch (e) {
        setError(lang === 'de' ? 'Rechnungen konnten nicht geladen werden.' : 'Could not load invoices.');
      } finally { setLoading(false); }
    };
    load();
  }, [lang]);

  const handleDownloadPdf = async (invoiceNumber) => {
    try {
      const res = await apiClient.get(`/api/invoices/${invoiceNumber}/pdf`, {
        responseType: 'blob',
        withCredentials: true,
      });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${invoiceNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      const errorMsg = lang === 'de' ? 'PDF konnte nicht heruntergeladen werden.' : 'Could not download PDF.';
      alert(errorMsg);
    }
  };

  if (loading) return <div className="w2g-loading"><div className="w2g-spinner" /><p className="w2g-loading-text">Wird geladen...</p></div>;

  const openInvoices = invoices.filter(i => i.status === 'open' || i.status === 'overdue');
  const paidInvoices = invoices.filter(i => i.status === 'paid');

  return (
    <PageScaffold
      title={lang === 'de' ? 'Rechnungen & Zahlungen' : 'Invoices & Payments'}
      subtitle={lang === 'de'
        ? `${openInvoices.length} offen, ${paidInvoices.length} bezahlt`
        : `${openInvoices.length} open, ${paidInvoices.length} paid`}
      testId="financials-page"
    >

      {/* Orientierungsbox */}
      <div className="w2g-panel bg-[var(--color-surface-elevated)]/80" data-testid="financials-guidance">
        <div className="flex items-start gap-3">
          <Info size={16} className="text-[var(--color-primary)] mt-0.5 shrink-0" />
          <div className="text-xs text-[var(--color-text-secondary)] space-y-1">
            <p className="font-medium text-[var(--color-text-primary)]">
              {lang === 'de' ? 'Informationen zu deinen Rechnungen' : 'About your invoices'}
            </p>
            <p>
              {lang === 'de'
                ? 'Hier findest du alle Rechnungen, die im Rahmen deiner Bewerbung erstellt wurden. Jede Rechnung erklaert, wofuer sie ist und was nach der Zahlung passiert.'
                : 'Here you find all invoices created as part of your application. Each invoice explains its purpose and what happens after payment.'}
            </p>
            <div className="flex flex-wrap gap-4 mt-2 pt-2 border-t border-[var(--color-divider)]">
              <span className="flex items-center gap-1.5">
                <Download size={11} className="text-[var(--color-primary)]" />
                {lang === 'de' ? 'PDF herunterladen' : 'Download PDF'}
              </span>
              <span className="flex items-center gap-1.5">
                <Shield size={11} className="text-[var(--color-primary)]" />
                {lang === 'de' ? 'Rechtssichere Rechnung' : 'Legally compliant invoice'}
              </span>
              <span className="flex items-center gap-1.5">
                <MessageCircle size={11} className="text-[var(--color-primary)]" />
                {lang === 'de' ? 'Hilfe per Chat' : 'Help via chat'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      {openInvoices.length > 0 && (
        <div className="bg-[var(--color-warning-bg)] border border-[var(--color-warning-border)] rounded-[var(--radius-sm)] p-4 flex items-start gap-3" data-testid="financials-open-banner">
          <AlertTriangle size={16} className="text-[var(--color-warning)] mt-0.5 shrink-0" />
          <p className="text-xs text-[var(--color-warning)]">
            {lang === 'de'
              ? `Du hast ${openInvoices.length} offene Rechnung(en). Eine rechtzeitige Zahlung sichert deinen Platz und beschleunigt die Bearbeitung.`
              : `You have ${openInvoices.length} open invoice(s). Timely payment secures your spot and speeds up processing.`}
          </p>
        </div>
      )}

      {error && (
        <div className="w2g-empty" data-testid="financials-error">
          <AlertTriangle size={24} className="w2g-empty-icon text-[var(--color-danger)]" />
          <p className="text-sm text-[var(--color-danger)]">{error}</p>
        </div>
      )}

      {invoices.length === 0 && !error && (
        <div className="w2g-empty" data-testid="financials-empty">
          <CreditCard size={32} className="w2g-empty-icon" />
          <p className="w2g-empty-text">
            {lang === 'de' ? 'Keine Rechnungen vorhanden' : 'No invoices available'}
          </p>
          <p className="w2g-empty-hint">
            {lang === 'de'
              ? 'Rechnungen werden erstellt, sobald deine Bewerbung den entsprechenden Status erreicht.'
              : 'Invoices are created once your application reaches the appropriate stage.'}
          </p>
        </div>
      )}

      {/* Invoice Cards */}
      <div className="space-y-3" data-testid="financials-list">
        {invoices.map(inv => {
          const cfg = STATUS_MAP[inv.status] || STATUS_MAP.open;
          const StatusIcon = cfg.icon;
          const purpose = getInvoicePurpose(inv.description, lang);

          return (
            <Card key={inv.invoice_number || inv.id}
              className={`p-0 overflow-hidden ${inv.status === 'overdue' ? 'border-[var(--color-danger-border)]' : inv.status === 'open' ? 'border-[var(--color-warning-border)]' : ''}`}
              data-testid={`invoice-card-${inv.invoice_number}`}>
              <div className="p-5">
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-sm font-semibold text-[var(--color-text-primary)] font-mono">{inv.invoice_number}</h4>
                      <span className={`w2g-badge flex items-center gap-1 ${cfg.color}`}>
                        <StatusIcon size={10} />
                        {lang === 'de' ? cfg.de : cfg.en}
                      </span>
                    </div>
                    <p className="text-xs text-[var(--color-text-secondary)]">{inv.description || '\u2013'}</p>
                  </div>
                  <p className="text-lg font-bold text-[var(--color-text-primary)] shrink-0">
                    {formatCurrency(inv.amount)}
                  </p>
                </div>

                {/* Zweck */}
                <div className="bg-[var(--color-surface-elevated)] rounded-[var(--radius-sm)] p-3 mb-3">
                  <p className="text-xs text-[var(--color-text-secondary)]">
                    <span className="font-medium">{lang === 'de' ? 'Zweck' : 'Purpose'}:</span> {purpose}
                  </p>
                </div>

                {/* Meta */}
                <div className="flex items-center gap-4 text-xs text-[var(--color-text-tertiary)]">
                  {inv.due_date && (
                    <span className="flex items-center gap-1">
                      <Clock size={10} /> {lang === 'de' ? 'Faellig' : 'Due'}: {formatDate(inv.due_date)}
                    </span>
                  )}
                  {inv.created_at && (
                    <span>{lang === 'de' ? 'Erstellt' : 'Created'}: {formatDate(inv.created_at)}</span>
                  )}
                </div>

                {/* Next Steps */}
                {(inv.status === 'open' || inv.status === 'overdue') && (
                  <div className="mt-3 w2g-panel bg-[var(--color-primary)]/[0.03] border-[var(--color-primary)]/10">
                    <div className="flex items-start gap-2 text-xs text-[var(--color-text-secondary)]">
                      <ArrowRight size={12} className="text-[var(--color-primary)] mt-0.5 shrink-0" />
                      <div>
                        <p className="font-medium text-[var(--color-text-primary)] mb-0.5">
                          {lang === 'de' ? 'Naechste Schritte' : 'Next Steps'}
                        </p>
                        <p>
                          {lang === 'de'
                            ? 'Nach Zahlungseingang pruefen wir die naechsten Schritte fuer deine Anmeldung und informieren dich per Nachricht im Portal.'
                            : 'After payment is received, we will process the next steps for your enrollment and notify you via message in the portal.'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {inv.status === 'paid' && (
                  <div className="mt-3 flex items-start gap-2 text-xs text-[var(--color-success)]">
                    <CheckCircle size={12} className="mt-0.5 shrink-0" />
                    <span>
                      {lang === 'de'
                        ? 'Zahlung eingegangen. Keine weiteren Schritte erforderlich.'
                        : 'Payment received. No further action required.'}
                    </span>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="border-t border-[var(--color-divider-subtle)] px-5 py-3 bg-[var(--color-surface-elevated)] flex items-center justify-between">
                <button onClick={() => handleDownloadPdf(inv.invoice_number)}
                  className="w2g-btn-secondary text-xs flex items-center gap-1.5 px-3 py-1.5"
                  data-testid={`invoice-download-${inv.invoice_number}`}>
                  <Download size={12} /> {lang === 'de' ? 'PDF herunterladen' : 'Download PDF'}
                </button>
                <div className="flex items-center gap-3">
                  {(inv.status === 'open' || inv.status === 'overdue') && (
                    <a href="/portal/messages" className="text-xs text-[var(--color-primary)] font-medium hover:underline flex items-center gap-1">
                      <HelpCircle size={12} />
                      {lang === 'de' ? 'Hilfe bei Zahlung' : 'Payment Help'}
                    </a>
                  )}
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </PageScaffold>
  );
}
