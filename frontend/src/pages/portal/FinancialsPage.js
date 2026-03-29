import React from 'react';
import { CreditCard, AlertCircle } from 'lucide-react';

export default function FinancialsPage() {
  return (
    <div className="space-y-6 animate-fade-in" data-testid="financials-page">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">Rechnungen & Zahlungen</h1>
        <p className="text-slate-500 text-sm mt-1">Übersicht deiner Zahlungen</p>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-sm p-4 flex items-start gap-3" data-testid="financials-gate-notice">
        <AlertCircle size={16} className="text-amber-600 mt-0.5 shrink-0" />
        <div className="text-sm text-amber-700">
          <p className="font-medium mb-1">[OFFEN] Zahlungsmodul noch nicht aktiv</p>
          <p>Das Zahlungsmodul wird erst nach Klärung der Steuer-/Refund-Logik aktiviert (Gate 1 gemäß Projektdokumentation). Für Zahlungsfragen wende dich direkt an info@stk-aachen.de.</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm p-8 text-center">
        <CreditCard size={32} className="text-slate-300 mx-auto mb-3" />
        <p className="text-slate-500 text-sm">Keine Rechnungen vorhanden</p>
        <p className="text-xs text-slate-400 mt-1">Rechnungen erscheinen hier, sobald sie ausgestellt wurden.</p>
      </div>
    </div>
  );
}
