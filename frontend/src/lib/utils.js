// Utility: merge classnames
export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}

export function formatDate(dateStr, locale = 'de-DE') {
  if (!dateStr) return '\u2013';
  return new Date(dateStr).toLocaleDateString(locale, { year: 'numeric', month: 'short', day: 'numeric' });
}

export function formatCurrency(amount, currency = 'EUR') {
  if (amount == null) return '\u2013';
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(amount);
}

/* ── Stage Labels (DE default, EN variant) ── */
export const STAGE_LABELS = {
  lead_new: 'Neue Anfrage',
  contacted: 'Kontaktiert',
  in_review: 'In Bearbeitung',
  pending_docs: 'Unterlagen angefordert',
  documents_requested: 'Unterlagen angefordert',
  docs_requested: 'Dokumente angefragt',
  docs_received: 'Dokumente eingegangen',
  docs_review: 'In Pr\u00fcfung',
  interview_scheduled: 'Beratungsgespr\u00e4ch geplant',
  conditional_offer: 'Vorl\u00e4ufige Zusage',
  offer_sent: 'Angebot versandt',
  enrolled: 'Eingeschrieben',
  invoice_open: 'Rechnung offen',
  payment_received: 'Zahlung eingegangen',
  process_next: 'N\u00e4chster Schritt',
  on_hold: 'Warteschleife',
  declined: 'Abgelehnt',
  completed: 'Abgeschlossen',
  dormant: 'Inaktiv',
  archived: 'Archiviert',
};

const STAGE_LABELS_EN = {
  lead_new: 'New Inquiry',
  contacted: 'Contacted',
  in_review: 'In Review',
  pending_docs: 'Documents Requested',
  documents_requested: 'Documents Requested',
  docs_requested: 'Documents Requested',
  docs_received: 'Documents Received',
  docs_review: 'Under Review',
  interview_scheduled: 'Interview Scheduled',
  conditional_offer: 'Conditional Offer',
  offer_sent: 'Offer Sent',
  enrolled: 'Enrolled',
  invoice_open: 'Invoice Open',
  payment_received: 'Payment Received',
  process_next: 'Next Step',
  on_hold: 'On Hold',
  declined: 'Declined',
  completed: 'Completed',
  dormant: 'Dormant',
  archived: 'Archived',
};

export function getStageLabel(stage, lang) {
  if (lang === 'en') return STAGE_LABELS_EN[stage] || stage;
  return STAGE_LABELS[stage] || stage;
}

export const STAGE_COLORS = {
  lead_new: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-primary)]',
  contacted: 'bg-[var(--color-info-bg)] text-[var(--color-info)]',
  in_review: 'bg-[var(--color-info-bg)] text-[var(--color-info)]',
  pending_docs: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]',
  documents_requested: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]',
  docs_requested: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]',
  docs_received: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]',
  docs_review: 'bg-[var(--color-info-bg)] text-[var(--color-info)]',
  interview_scheduled: 'bg-[var(--color-info-bg)] text-[var(--color-info)]',
  conditional_offer: 'bg-[var(--color-info-bg)] text-[var(--color-info)]',
  offer_sent: 'bg-[rgba(10,25,47,0.1)] text-[var(--color-primary)]',
  enrolled: 'bg-[var(--color-success-bg)] text-[var(--color-success)]',
  invoice_open: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]',
  payment_received: 'bg-[var(--color-success-bg)] text-[var(--color-success)]',
  process_next: 'bg-[var(--color-info-bg)] text-[var(--color-info)]',
  on_hold: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]',
  declined: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]',
  completed: 'bg-[var(--color-success-bg)] text-[var(--color-success)]',
  dormant: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)]',
  archived: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)]',
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

const ROLE_LABELS_EN = {
  superadmin: 'Superadmin',
  admin: 'Admin',
  staff: 'Staff',
  teacher: 'Teacher',
  accounting_staff: 'Accounting',
  agency_admin: 'Agency Admin',
  agency_agent: 'Agency Agent',
  affiliate: 'Partner',
  applicant: 'Applicant',
};

export function getRoleLabel(role, lang) {
  if (lang === 'en') return ROLE_LABELS_EN[role] || role;
  return ROLE_LABELS[role] || role;
}

/* ── Status Labels (Tasks, Invoices, Documents) ── */
export const TASK_STATUS_LABELS = {
  de: { open: 'Offen', in_progress: 'In Bearbeitung', done: 'Erledigt' },
  en: { open: 'Open', in_progress: 'In Progress', done: 'Completed' },
};

export const TASK_PRIORITY_LABELS = {
  de: { high: 'Hoch', normal: 'Normal', low: 'Niedrig' },
  en: { high: 'High', normal: 'Normal', low: 'Low' },
};

export const INVOICE_STATUS_LABELS = {
  de: { draft: 'Entwurf', sent: 'Versendet', paid: 'Bezahlt', overdue: 'Ueberfaellig', cancelled: 'Storniert' },
  en: { draft: 'Draft', sent: 'Sent', paid: 'Paid', overdue: 'Overdue', cancelled: 'Cancelled' },
};

export const DOC_STATUS_LABELS = {
  de: { uploaded: 'Hochgeladen', approved: 'Akzeptiert', rejected: 'Abgelehnt', in_review: 'In Pruefung', needs_review: 'Pruefung noetig' },
  en: { uploaded: 'Uploaded', approved: 'Approved', rejected: 'Rejected', in_review: 'In Review', needs_review: 'Needs Review' },
};

export function getLang(i18n) {
  return i18n?.language === 'en' ? 'en' : 'de';
}
