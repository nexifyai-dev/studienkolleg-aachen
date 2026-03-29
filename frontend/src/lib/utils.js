// Utility: merge classnames
export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}

export function formatDate(dateStr, locale = 'de-DE') {
  if (!dateStr) return '–';
  return new Date(dateStr).toLocaleDateString(locale, { year: 'numeric', month: 'short', day: 'numeric' });
}

export function formatCurrency(amount, currency = 'EUR') {
  if (amount == null) return '–';
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(amount);
}

export const STAGE_LABELS = {
  lead_new: 'Neue Anfrage',
  contacted: 'Kontaktiert',
  in_review: 'In Bearbeitung',
  pending_docs: 'Unterlagen angefordert',
  docs_requested: 'Dokumente angefragt',
  docs_received: 'Dokumente eingegangen',
  docs_review: 'In Prüfung',
  interview_scheduled: 'Beratungsgespräch geplant',
  conditional_offer: 'Vorläufige Zusage',
  offer_sent: 'Angebot versandt',
  enrolled: 'Eingeschrieben',
  invoice_open: 'Rechnung offen',
  payment_received: 'Zahlung eingegangen',
  process_next: 'Nächster Schritt',
  on_hold: 'Warteschleife',
  declined: 'Abgelehnt',
  completed: 'Abgeschlossen',
  dormant: 'Inaktiv',
  archived: 'Archiviert',
};

export const STAGE_COLORS = {
  lead_new: 'bg-slate-100 text-slate-700',
  contacted: 'bg-blue-100 text-blue-700',
  in_review: 'bg-purple-100 text-purple-700',
  pending_docs: 'bg-yellow-100 text-yellow-700',
  docs_requested: 'bg-yellow-100 text-yellow-700',
  docs_received: 'bg-orange-100 text-orange-700',
  docs_review: 'bg-purple-100 text-purple-700',
  interview_scheduled: 'bg-teal-100 text-teal-700',
  conditional_offer: 'bg-blue-100 text-blue-700',
  offer_sent: 'bg-indigo-100 text-indigo-700',
  enrolled: 'bg-green-100 text-green-700',
  invoice_open: 'bg-red-100 text-red-700',
  payment_received: 'bg-green-100 text-green-700',
  process_next: 'bg-teal-100 text-teal-700',
  on_hold: 'bg-amber-100 text-amber-700',
  declined: 'bg-red-100 text-red-700',
  completed: 'bg-emerald-100 text-emerald-700',
  dormant: 'bg-gray-100 text-gray-500',
  archived: 'bg-gray-100 text-gray-400',
};

export const ROLE_LABELS = {
  superadmin: 'Superadmin',
  admin: 'Admin',
  staff: 'Mitarbeiter',
  teacher: 'Lehrer',
  accounting_staff: 'Buchhaltung',
  agency_admin: 'Agentur Admin',
  agency_agent: 'Agentur Agent',
  affiliate: 'Partner',
  applicant: 'Bewerber',
};
