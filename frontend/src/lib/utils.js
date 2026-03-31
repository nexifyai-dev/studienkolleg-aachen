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
  information_request: 'Informationsanfrage',
  documents_requested: 'Dokumente angefordert',
  school_degree_assessed: 'Schulabschluss bewertet',
  language_course_recommended: 'Sprachkurs empfohlen',
  language_course_booked: 'Sprachkurs gebucht',
  studienkolleg_seat_reserved: 'Studienkolleg-Platz reserviert',
  studienkolleg_enrollment_completed: 'Studienkolleg-Einschreibung abgeschlossen',
  alternative_path_advisory: 'Alternativpfad-Beratung',
  vocational_training_recommended: 'Berufsausbildung empfohlen',
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
  information_request: 'bg-primary/10 text-primary',
  documents_requested: 'bg-amber-100 text-amber-700',
  school_degree_assessed: 'bg-primary/10 text-primary',
  language_course_recommended: 'bg-primary/10 text-primary',
  language_course_booked: 'bg-primary/10 text-primary',
  studienkolleg_seat_reserved: 'bg-primary/10 text-primary',
  studienkolleg_enrollment_completed: 'bg-emerald-100 text-emerald-700',
  alternative_path_advisory: 'bg-slate-100 text-slate-600',
  vocational_training_recommended: 'bg-slate-100 text-slate-600',
  lead_new: 'bg-primary/10 text-primary',
  contacted: 'bg-primary/10 text-primary',
  in_review: 'bg-primary/10 text-primary',
  pending_docs: 'bg-amber-100 text-amber-700',
  docs_requested: 'bg-amber-100 text-amber-700',
  docs_received: 'bg-primary/5 text-primary',
  docs_review: 'bg-primary/10 text-primary',
  interview_scheduled: 'bg-primary/10 text-primary',
  conditional_offer: 'bg-primary/10 text-primary',
  offer_sent: 'bg-primary/10 text-primary',
  enrolled: 'bg-emerald-100 text-emerald-700',
  invoice_open: 'bg-red-100 text-red-700',
  payment_received: 'bg-emerald-100 text-emerald-700',
  process_next: 'bg-primary/10 text-primary',
  on_hold: 'bg-amber-100 text-amber-700',
  declined: 'bg-red-100 text-red-700',
  completed: 'bg-emerald-100 text-emerald-700',
  dormant: 'bg-slate-100 text-slate-500',
  archived: 'bg-slate-100 text-slate-500',
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
