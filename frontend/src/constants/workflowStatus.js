export const WORKFLOW_STATUSES = [
  'information_request',
  'documents_requested',
  'school_degree_assessed',
  'language_course_recommended',
  'language_course_booked',
  'studienkolleg_seat_reserved',
  'studienkolleg_enrollment_completed',
  'alternative_path_advisory',
  'vocational_training_recommended',
];

export const LEGACY_STATUS_ALIASES = {
  lead_new: 'information_request',
  contacted: 'information_request',
  pending_docs: 'documents_requested',
  docs_requested: 'documents_requested',
  docs_received: 'documents_requested',
  docs_review: 'school_degree_assessed',
  in_review: 'school_degree_assessed',
  interview_scheduled: 'language_course_recommended',
  conditional_offer: 'studienkolleg_seat_reserved',
  offer_sent: 'studienkolleg_seat_reserved',
  enrolled: 'studienkolleg_enrollment_completed',
};

export function normalizeWorkflowStatus(status) {
  if (!status) return null;
  if (WORKFLOW_STATUSES.includes(status)) return status;
  return LEGACY_STATUS_ALIASES[status] || null;
}
