import React from 'react';
import { useTranslation } from 'react-i18next';
import { CreditCard, AlertCircle } from 'lucide-react';

export default function FinancialsPage() {
  const { t } = useTranslation();
  return (
    <div className="space-y-6 animate-fade-in" data-testid="financials-page">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">{t('portal.financials_title')}</h1>
        <p className="text-slate-500 text-sm mt-1">{t('portal.financials_sub')}</p>
      </div>

      <div className="bg-slate-50 border border-slate-200 rounded-sm p-4 flex items-start gap-3" data-testid="financials-gate-notice">
        <AlertCircle size={16} className="text-slate-500 mt-0.5 shrink-0" />
        <div className="text-sm text-slate-700">
          <p className="font-medium mb-1">{t('portal.financials_prep_title')}</p>
          <p>{t('portal.financials_prep_desc')}</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm p-8 text-center">
        <CreditCard size={32} className="text-slate-300 mx-auto mb-3" />
        <p className="text-slate-500 text-sm">{t('portal.financials_empty')}</p>
        <p className="text-xs text-slate-400 mt-1">{t('portal.financials_empty_hint')}</p>
      </div>
    </div>
  );
}
