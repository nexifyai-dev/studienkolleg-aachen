import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  CheckCircle2, Download, ExternalLink, FileText, RotateCcw, Search,
  XCircle, Eye, X, MessageSquare, Shield, AlertTriangle, Loader2, Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import apiClient from '../../lib/apiClient';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { DOC_STATUS_LABELS, getLang } from '../../lib/utils';
import { API } from '../../lib/apiBase';

const STATUS_BADGE = {
  uploaded: 'bg-[var(--color-info-bg)] text-[var(--color-info)] border border-[var(--color-info-border)]',
  approved: 'bg-[var(--color-success-bg)] text-[var(--color-success)] border border-[var(--color-success-border)]',
  rejected: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border border-[var(--color-danger-border)]',
  in_review: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning-border)]',
  needs_review: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning-border)]',
};

const STATUS_LABEL = {
  uploaded: 'Hochgeladen',
  approved: 'Akzeptiert',
  rejected: 'Abgelehnt',
  in_review: 'In Pruefung',
  needs_review: 'Pruefung noetig',
};

function getDocStatusLabel(status, lang) {
  return DOC_STATUS_LABELS[lang]?.[status] || STATUS_LABEL[status] || status;
}

const DOC_TYPE_LABELS = {
  de: { passport: 'Reisepass / Ausweis', highschool_diploma: 'Schulabschlusszeugnis', transcript: 'Notenuebersicht', language_certificate: 'Sprachzertifikat', photo: 'Passfoto', receipt: 'Zahlungsbeleg', other: 'Sonstiges' },
  en: { passport: 'Passport / ID', highschool_diploma: 'High School Diploma', transcript: 'Transcript', language_certificate: 'Language Certificate', photo: 'Passport Photo', receipt: 'Payment Receipt', other: 'Other' },
};

/* Dokumenten-Review-Modal – Popup mit Vorschau + KI-Pruefbericht + Aktionen */
function ReviewModal({ doc, onClose, onAction }) {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [rejectionReason, setRejectionReason] = useState('');
  const [showRejectForm, setShowRejectForm] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);
  const [validation, setValidation] = useState(null);
  const [validationLoading, setValidationLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('report');
  const isPdf = doc.content_type === 'application/pdf' || doc.filename?.endsWith('.pdf');
  const isImage = doc.content_type?.startsWith('image/');
  const canPreview = doc.has_binary && doc.storage_key && (isPdf || isImage);
  const canDownload = doc.has_binary && doc.storage_key;
  const downloadUrl = `${API}/api/documents/${doc.id}/download`;

  // KI-Validierungsdaten laden
  useEffect(() => {
    apiClient.get(`/api/documents/${doc.id}/validation`, { withCredentials: true })
      .then(r => setValidation(r.data))
      .catch(() => {})
      .finally(() => setValidationLoading(false));
  }, [doc.id]);

  const handleAction = async (action, payload) => {
    setActionLoading(action);
    try {
      await onAction(action, payload);
      onClose();
    } catch {
      /* error handled in parent */
    }
    setActionLoading(null);
  };

  const L = {
    file: lang === 'de' ? 'Datei' : 'File',
    applicant: lang === 'de' ? 'Bewerber' : 'Applicant',
    classification: lang === 'de' ? 'KI-Klassifikation' : 'AI Classification',
    report: lang === 'de' ? 'KI-Pruefbericht' : 'AI Report',
    extraction: lang === 'de' ? 'Extrahierte Daten' : 'Extracted Data',
    knowledge: lang === 'de' ? 'Wissensabgleich' : 'Knowledge Match',
    consistency: lang === 'de' ? 'Konsistenz' : 'Consistency',
    actions: lang === 'de' ? 'Aktionen' : 'Actions',
    approve: lang === 'de' ? 'Akzeptieren' : 'Approve',
    reject: lang === 'de' ? 'Ablehnen' : 'Reject',
    revalidate: lang === 'de' ? 'Neu pruefen' : 'Revalidate',
    question: lang === 'de' ? 'Rueckfrage' : 'Question',
    cancel: lang === 'de' ? 'Abbrechen' : 'Cancel',
    rejReason: lang === 'de' ? 'Ablehnungsgrund' : 'Rejection Reason',
    rejPlaceholder: lang === 'de' ? 'Bitte Grund fuer die Ablehnung angeben...' : 'Please provide a reason for rejection...',
    preview: lang === 'de' ? 'Dokument-Vorschau' : 'Document Preview',
    noPreview: lang === 'de' ? 'Vorschau nicht verfuegbar' : 'Preview not available',
    noFile: lang === 'de' ? 'Keine Datei-Daten vorhanden. Nur Metadaten gespeichert.' : 'No file data available. Only metadata stored.',
    open: lang === 'de' ? 'Oeffnen' : 'Open',
    docReview: lang === 'de' ? 'Dokumentenpruefung' : 'Document Review',
    detected: lang === 'de' ? 'Erkannter Typ' : 'Detected Type',
    confidence: lang === 'de' ? 'Konfidenz' : 'Confidence',
    authentic: lang === 'de' ? 'Authentisch' : 'Authentic',
    country: lang === 'de' ? 'Ausstellungsland' : 'Issuing Country',
    staffRequired: lang === 'de' ? 'Staff-Entscheidung erforderlich' : 'Staff Decision Required',
    noReport: lang === 'de' ? 'Kein KI-Pruefbericht vorhanden. Klicken Sie auf "Neu pruefen" um die KI-Analyse zu starten.' : 'No AI report available. Click "Revalidate" to start AI analysis.',
    loading: lang === 'de' ? 'KI-Daten werden geladen...' : 'Loading AI data...',
    warnings: lang === 'de' ? 'Warnungen' : 'Warnings',
    risks: lang === 'de' ? 'Risikofaktoren' : 'Risk Factors',
    anabin: lang === 'de' ? 'Anabin-Abgleich' : 'Anabin Match',
    langMatch: lang === 'de' ? 'Sprachniveau' : 'Language Level',
  };

  return (
    <div className="w2g-modal-overlay" onClick={onClose} data-testid="doc-review-modal">
      <div className="w2g-modal" style={{ maxWidth: '1100px', maxHeight: '90vh' }} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="w2g-modal-header">
          <div className="min-w-0 flex-1">
            <h3 className="font-heading text-base font-bold text-[var(--color-primary)] truncate">
              Dokumentenpruefung: {doc.filename || 'Unbenannt'}
            </h3>
            <p className="text-[11px] text-[var(--color-text-tertiary)] mt-0.5">
              {doc.applicant_name} · {doc.document_type} · {doc.status ? STATUS_LABEL[doc.status] || doc.status : 'Hochgeladen'}
            </p>
          </div>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="review-modal-close"><X size={16} /></button>
        </div>

        {/* Body: 2-Column Layout */}
        <div className="flex-1 overflow-hidden flex" style={{ height: 'calc(90vh - 160px)' }}>
          {/* Linke Haelfte: Dokument-Vorschau */}
          <div className="flex-1 border-r border-[var(--color-divider)] flex flex-col">
            <div className="px-4 py-2 border-b border-[var(--color-divider-subtle)] bg-[var(--color-surface-elevated)] flex items-center justify-between">
              <span className="text-[11px] font-semibold uppercase tracking-wide text-[var(--color-text-tertiary)]">Dokument-Vorschau</span>
              {canDownload && (
                <div className="flex items-center gap-2">
                  <a href={downloadUrl} target="_blank" rel="noopener noreferrer"
                    className="w2g-btn-table-secondary" data-testid="review-open-external">
                    <ExternalLink size={11} /> Oeffnen
                  </a>
                  <a href={downloadUrl} download={doc.filename}
                    className="w2g-btn-table-secondary" data-testid="review-download">
                    <Download size={11} />
                  </a>
                </div>
              )}
            </div>
            <div className="flex-1 overflow-hidden bg-[var(--color-surface-sunken)]">
              {canPreview ? (
                isPdf ? (
                  <iframe src={`${downloadUrl}#toolbar=1`} className="w-full h-full border-0" title={doc.filename} />
                ) : (
                  <div className="w-full h-full flex items-center justify-center p-4">
                    <img src={downloadUrl} alt={doc.filename} className="max-w-full max-h-full object-contain" style={{ borderRadius: 'var(--radius-md)' }} />
                  </div>
                )
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center gap-4">
                  <FileText size={40} className="text-[var(--color-text-tertiary)]" />
                  {canDownload ? (
                    <>
                      <p className="text-sm text-[var(--color-text-secondary)]">Vorschau nicht verfuegbar</p>
                      <a href={downloadUrl} target="_blank" rel="noopener noreferrer" className="w2g-btn-primary w2g-btn-sm" data-testid="review-fallback-open">
                        <ExternalLink size={13} /> Dokument oeffnen
                      </a>
                    </>
                  ) : (
                    <div className="text-center px-6">
                      <div className="bg-[var(--color-warning-bg)] border border-[var(--color-warning-border)] px-4 py-3 inline-flex items-center gap-2" style={{ borderRadius: 'var(--radius-sm)' }}>
                        <AlertTriangle size={14} className="text-[var(--color-warning)] shrink-0" />
                        <span className="text-xs text-[var(--color-warning)]">Keine Datei-Daten vorhanden. Nur Metadaten gespeichert.</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Rechte Haelfte: KI-Pruefbericht + Aktionen */}
          <div className="w-[420px] shrink-0 flex flex-col overflow-y-auto">
            <div className="p-5 space-y-4 flex-1">
              {/* Datei-Info */}
              <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] p-3.5 space-y-2" style={{ borderRadius: 'var(--radius-md)' }}>
                <p className="text-[10px] uppercase tracking-[0.14em] font-semibold text-[var(--color-text-tertiary)]">{L.file}</p>
                <div className="flex items-center gap-2">
                  <FileText size={14} className="text-[var(--color-primary)] shrink-0" />
                  <span className="text-xs font-semibold text-[var(--color-text-primary)] truncate">{doc.filename}</span>
                </div>
                <div className="flex items-center gap-3 text-[10px] text-[var(--color-text-tertiary)]">
                  <span>{doc.document_type}</span>
                  {doc.file_size && <span>{(doc.file_size / 1024).toFixed(0)} KB</span>}
                  {doc.uploaded_at && <span>{new Date(doc.uploaded_at).toLocaleDateString(lang === 'de' ? 'de-DE' : 'en-US')}</span>}
                </div>
              </div>

              {/* KI-Klassifikation Zusammenfassung */}
              <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] p-3.5 space-y-2" style={{ borderRadius: 'var(--radius-md)' }}>
                <p className="text-[10px] uppercase tracking-[0.14em] font-semibold text-[var(--color-text-tertiary)]">{L.classification}</p>
                {validationLoading ? (
                  <p className="text-xs text-[var(--color-text-tertiary)] flex items-center gap-1"><Loader2 size={12} className="animate-spin" /> {L.loading}</p>
                ) : validation ? (
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <Shield size={14} className={validation.staff_decision_required ? 'text-[var(--color-warning)]' : 'text-[var(--color-success)]'} />
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded ${STATUS_BADGE[validation.validation_status] || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
                        {getDocStatusLabel(validation.validation_status, lang)}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[10px]">
                      <span className="text-[var(--color-text-tertiary)]">{L.detected}:</span>
                      <span className="font-medium text-[var(--color-text-primary)]">{DOC_TYPE_LABELS[lang]?.[validation.detected_type] || validation.detected_type || '–'}</span>
                      <span className="text-[var(--color-text-tertiary)]">{L.confidence}:</span>
                      <span className={`font-medium ${validation.validation_confidence === 'high' ? 'text-[var(--color-success)]' : validation.validation_confidence === 'medium' ? 'text-[var(--color-warning)]' : 'text-[var(--color-danger)]'}`}>{validation.validation_confidence || '–'}</span>
                      {validation.ai_classification?.issuing_country && (
                        <><span className="text-[var(--color-text-tertiary)]">{L.country}:</span><span className="font-medium text-[var(--color-text-primary)]">{validation.ai_classification.issuing_country}</span></>
                      )}
                      {validation.ai_classification?.is_authentic_document !== undefined && (
                        <><span className="text-[var(--color-text-tertiary)]">{L.authentic}:</span><span className={`font-medium ${validation.ai_classification.is_authentic_document ? 'text-[var(--color-success)]' : 'text-[var(--color-danger)]'}`}>{validation.ai_classification.is_authentic_document ? (lang === 'de' ? 'Ja' : 'Yes') : (lang === 'de' ? 'Nein' : 'No')}</span></>
                      )}
                    </div>
                    {validation.staff_decision_required && (
                      <p className="text-[10px] text-[var(--color-warning)] bg-[var(--color-warning-bg)] px-2 py-1 flex items-center gap-1 mt-1" style={{ borderRadius: 'var(--radius-xs)' }}>
                        <AlertTriangle size={10} /> {L.staffRequired}
                      </p>
                    )}
                    {validation.validation_warnings?.length > 0 && (
                      <div className="mt-1">
                        <p className="text-[9px] uppercase tracking-wider text-[var(--color-text-tertiary)] mb-0.5">{L.warnings}</p>
                        <div className="flex flex-wrap gap-1">
                          {validation.validation_warnings.map((w, i) => (
                            <span key={i} className="text-[9px] px-1.5 py-0.5 bg-[var(--color-warning-bg)] text-[var(--color-warning)] rounded">{w}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-xs text-[var(--color-text-secondary)]">{getDocStatusLabel(doc.validation_status || doc.status, lang)}</p>
                )}
              </div>

              {/* Tabs: Pruefbericht / Extrahierte Daten / Wissensabgleich */}
              {validation && (validation.ai_report || validation.ai_extraction || validation.knowledge_match) && (
                <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] overflow-hidden" style={{ borderRadius: 'var(--radius-md)' }}>
                  <div className="flex border-b border-[var(--color-divider)]">
                    {[
                      { key: 'report', label: L.report, show: !!validation.ai_report },
                      { key: 'extraction', label: L.extraction, show: !!validation.ai_extraction },
                      { key: 'knowledge', label: L.knowledge, show: !!validation.knowledge_match },
                    ].filter(t => t.show).map(tab => (
                      <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                        className={`flex-1 py-2 text-[10px] font-medium transition-colors ${activeTab === tab.key ? 'text-[var(--color-primary)] border-b-2 border-[var(--color-primary)] bg-white' : 'text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]'}`}
                        data-testid={`review-tab-${tab.key}`}>
                        {tab.label}
                      </button>
                    ))}
                  </div>
                  <div className="p-3.5 max-h-[250px] overflow-y-auto">
                    {activeTab === 'report' && validation.ai_report && (
                      <pre className="text-[11px] text-[var(--color-text-primary)] whitespace-pre-wrap leading-relaxed font-sans" data-testid="ai-report-content">
                        {validation.ai_report}
                      </pre>
                    )}
                    {activeTab === 'extraction' && validation.ai_extraction && (
                      <div className="space-y-1.5" data-testid="ai-extraction-content">
                        {Object.entries(validation.ai_extraction).filter(([k]) => !k.startsWith('_') && !k.startsWith('raw_text')).map(([key, val]) => (
                          <div key={key} className="flex gap-2 text-[11px]">
                            <span className="text-[var(--color-text-tertiary)] min-w-[120px] shrink-0">{key}:</span>
                            <span className="text-[var(--color-text-primary)] font-medium break-all">{typeof val === 'object' ? JSON.stringify(val) : String(val)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {activeTab === 'knowledge' && validation.knowledge_match && (
                      <div className="space-y-3" data-testid="ai-knowledge-content">
                        {validation.knowledge_match.anabin_match && (
                          <div>
                            <p className="text-[9px] uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">{L.anabin}</p>
                            <div className="grid grid-cols-2 gap-1 text-[11px]">
                              <span className="text-[var(--color-text-tertiary)]">{L.country}:</span>
                              <span className="font-medium">{validation.knowledge_match.anabin_match.country}</span>
                              <span className="text-[var(--color-text-tertiary)]">Kategorie:</span>
                              <span className={`font-bold ${validation.knowledge_match.anabin_match.category === 'H+' ? 'text-[var(--color-success)]' : validation.knowledge_match.anabin_match.category === 'D' ? 'text-[var(--color-danger)]' : 'text-[var(--color-warning)]'}`}>
                                {validation.knowledge_match.anabin_match.category || '–'}
                              </span>
                            </div>
                          </div>
                        )}
                        {validation.knowledge_match.language_match && (
                          <div>
                            <p className="text-[9px] uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">{L.langMatch}</p>
                            <div className="grid grid-cols-2 gap-1 text-[11px]">
                              <span className="text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Extrahiert' : 'Extracted'}:</span>
                              <span className="font-medium">{validation.knowledge_match.language_match.extracted_level || '–'}</span>
                              <span className="text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Erforderlich' : 'Required'}:</span>
                              <span className="font-medium">{validation.knowledge_match.language_match.required_level || '–'}</span>
                              <span className="text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Ausreichend' : 'Sufficient'}:</span>
                              <span className={`font-bold ${validation.knowledge_match.language_match.is_sufficient ? 'text-[var(--color-success)]' : 'text-[var(--color-danger)]'}`}>
                                {validation.knowledge_match.language_match.is_sufficient ? (lang === 'de' ? 'Ja' : 'Yes') : (lang === 'de' ? 'Nein' : 'No')}
                              </span>
                            </div>
                          </div>
                        )}
                        {validation.knowledge_match.risk_flags?.length > 0 && (
                          <div>
                            <p className="text-[9px] uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">{L.risks}</p>
                            <div className="space-y-1">
                              {validation.knowledge_match.risk_flags.map((flag, i) => (
                                <p key={i} className="text-[10px] text-[var(--color-danger)] bg-[var(--color-danger-bg)] px-2 py-1 rounded flex items-start gap-1">
                                  <AlertTriangle size={10} className="shrink-0 mt-0.5" /> {flag}
                                </p>
                              ))}
                            </div>
                          </div>
                        )}
                        {validation.knowledge_match.consistency_checks?.length > 0 && (
                          <div>
                            <p className="text-[9px] uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1">{L.consistency}</p>
                            <div className="space-y-1">
                              {validation.knowledge_match.consistency_checks.map((check, i) => (
                                <p key={i} className={`text-[10px] px-2 py-1 rounded ${check.status === 'match' ? 'text-[var(--color-success)] bg-[var(--color-success-bg)]' : 'text-[var(--color-danger)] bg-[var(--color-danger-bg)]'}`}>
                                  {check.field}: {check.detail}
                                </p>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Kein KI-Bericht vorhanden */}
              {!validationLoading && validation && !validation.ai_report && !validation.ai_extraction && (
                <div className="bg-[var(--color-surface-elevated)] border border-dashed border-[var(--color-divider)] p-4 text-center" style={{ borderRadius: 'var(--radius-md)' }}>
                  <Sparkles size={20} className="mx-auto mb-2 text-[var(--color-text-tertiary)]" />
                  <p className="text-xs text-[var(--color-text-secondary)]">{L.noReport}</p>
                </div>
              )}

              {/* Ablehnungsgrund-Formular */}
              {showRejectForm && (
                <div className="bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)] p-3.5 space-y-2 animate-fade-in" style={{ borderRadius: 'var(--radius-md)' }} data-testid="reject-form">
                  <p className="text-xs font-semibold text-[var(--color-danger)]">{L.rejReason}</p>
                  <textarea
                    value={rejectionReason}
                    onChange={e => setRejectionReason(e.target.value)}
                    placeholder={L.rejPlaceholder}
                    className="w2g-input text-xs"
                    rows={3}
                    data-testid="reject-reason-input"
                  />
                  <div className="flex gap-2">
                    <button onClick={() => handleAction('reject', { reason: rejectionReason })}
                      disabled={!rejectionReason.trim() || actionLoading === 'reject'}
                      className="w2g-btn-destructive w2g-btn-sm flex-1" data-testid="reject-confirm-btn">
                      {actionLoading === 'reject' ? <Loader2 size={12} className="animate-spin" /> : <XCircle size={12} />}
                      {L.reject}
                    </button>
                    <button onClick={() => setShowRejectForm(false)} className="w2g-btn-outline w2g-btn-sm">{L.cancel}</button>
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons – fixiert unten */}
            <div className="border-t border-[var(--color-divider)] p-4 bg-[var(--color-surface)] space-y-2" data-testid="review-actions">
              <div className="grid grid-cols-2 gap-2">
                <button onClick={() => handleAction('approve')}
                  disabled={actionLoading === 'approve'}
                  className="w2g-btn-primary w2g-btn-sm" data-testid="review-approve-btn">
                  {actionLoading === 'approve' ? <Loader2 size={13} className="animate-spin" /> : <CheckCircle2 size={13} />}
                  {L.approve}
                </button>
                <button onClick={() => setShowRejectForm(true)}
                  className="w2g-btn-outline w2g-btn-sm border-[var(--color-danger-border)] text-[var(--color-danger)] hover:bg-[var(--color-danger)] hover:text-white hover:border-[var(--color-danger)]"
                  data-testid="review-reject-btn">
                  <XCircle size={13} /> {L.reject}
                </button>
              </div>
              <button onClick={() => handleAction('question')}
                className="w2g-btn-secondary w2g-btn-sm w-full" data-testid="review-question-btn">
                <MessageSquare size={13} /> {L.question}
              </button>
              <button onClick={() => handleAction('revalidate')}
                disabled={actionLoading === 'revalidate'}
                className="w2g-btn-outline w2g-btn-sm w-full" data-testid="review-revalidate-btn">
                {actionLoading === 'revalidate' ? <Loader2 size={13} className="animate-spin" /> : <RotateCcw size={13} />}
                {L.revalidate}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function StaffDocumentsReviewPage() {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [rows, setRows] = useState([]);
  const [reviewDoc, setReviewDoc] = useState(null);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const appsRes = await apiClient.get('/api/applications', { withCredentials: true });
      const apps = appsRes.data || [];
      const docs = await Promise.all(apps.slice(0, 40).map(async (app) => {
        const res = await apiClient.get(`/api/applications/${app.id}/documents`, { withCredentials: true }).catch(() => ({ data: [] }));
        return (res.data || []).map(d => ({
          ...d,
          applicant_name: app.applicant?.full_name || app.applicant?.email || 'Unbekannt',
          application_id: app.id,
          course_type: app.course_type,
        }));
      }));
      setRows(docs.flat());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = useMemo(() => rows.filter(r => {
    const q = search.toLowerCase();
    const matchSearch = !q || r.filename?.toLowerCase().includes(q) || r.applicant_name?.toLowerCase().includes(q) || r.document_type?.toLowerCase().includes(q);
    const matchType = typeFilter === 'all' || r.document_type === typeFilter;
    const matchStatus = statusFilter === 'all' || r.status === statusFilter;
    return matchSearch && matchType && matchStatus;
  }), [rows, search, typeFilter, statusFilter]);

  const docTypes = useMemo(() => [...new Set(rows.map(r => r.document_type).filter(Boolean))], [rows]);

  const handleReviewAction = async (action, payload) => {
    if (!reviewDoc) return;
    try {
      if (action === 'approve') {
        await apiClient.put(`/api/documents/${reviewDoc.id}/review`, { status: 'approved' }, { withCredentials: true });
        toast.success('Dokument akzeptiert');
      } else if (action === 'reject') {
        await apiClient.put(`/api/documents/${reviewDoc.id}/review`, { status: 'rejected', rejection_reason: payload?.reason }, { withCredentials: true });
        toast.success('Dokument abgelehnt');
      } else if (action === 'revalidate') {
        await apiClient.post(`/api/documents/${reviewDoc.id}/revalidate`, {}, { withCredentials: true });
        toast.success('Neupruefung gestartet');
      } else if (action === 'question') {
        toast.info('Rueckfrage-Funktion wird erweitert');
      }
      await load();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Aktion fehlgeschlagen');
      throw e;
    }
  };

  return (
    <PageScaffold
      title={lang === 'de' ? 'Dokumentenpruefung' : 'Document Review'}
      subtitle={`${lang === 'de' ? 'Review Queue' : 'Review Queue'} – ${filtered.length} ${lang === 'de' ? (filtered.length !== 1 ? 'Dokumente' : 'Dokument') : (filtered.length !== 1 ? 'documents' : 'document')} ${lang === 'de' ? 'in der Warteschlange' : 'in queue'}`}
      testId="staff-documents-review-page"
      toolbar={
        <ToolbarRow
          search={
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input value={search} onChange={e => setSearch(e.target.value)}
                className="w2g-search pl-10" placeholder={lang === 'de' ? 'Dokumente durchsuchen...' : 'Search documents...'}
                data-testid="staff-documents-search" />
            </div>
          }
          filters={[
            <select key="type" value={typeFilter} onChange={e => setTypeFilter(e.target.value)}
              className="w2g-select" data-testid="staff-documents-type-filter">
              <option value="all">{lang === 'de' ? 'Alle Typen' : 'All Types'}</option>
              {docTypes.map(t => <option key={t} value={t}>{t}</option>)}
            </select>,
            <select key="status" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
              className="w2g-select" data-testid="staff-documents-status-filter">
              <option value="all">{lang === 'de' ? 'Alle Status' : 'All Statuses'}</option>
              <option value="uploaded">{DOC_STATUS_LABELS[lang]?.uploaded}</option>
              <option value="approved">{DOC_STATUS_LABELS[lang]?.approved}</option>
              <option value="rejected">{DOC_STATUS_LABELS[lang]?.rejected}</option>
              <option value="in_review">{DOC_STATUS_LABELS[lang]?.in_review}</option>
            </select>,
          ]}
        />
      }
    >
      {loading ? (
        <div className="w2g-loading"><div className="w2g-spinner" /></div>
      ) : (
        <div className="w2g-card p-0 overflow-hidden" data-testid="staff-documents-table-panel">
          <div className="overflow-x-auto">
            <table className="w2g-table" data-testid="staff-documents-table">
              <thead>
                <tr>
                  <th>{lang === 'de' ? 'Dokument' : 'Document'}</th>
                  <th>{lang === 'de' ? 'Bewerber' : 'Applicant'}</th>
                  <th>{lang === 'de' ? 'Typ' : 'Type'}</th>
                  <th>Status</th>
                  <th>Upload</th>
                  <th>{lang === 'de' ? 'KI-Evidenz' : 'AI Evidence'}</th>
                  <th className="text-right">{lang === 'de' ? 'Aktion' : 'Action'}</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="text-center py-12 text-[var(--color-text-tertiary)]">
                      <FileText size={24} className="mx-auto mb-2 text-[var(--color-text-tertiary)]" />
                      <p className="text-sm font-medium">{lang === 'de' ? 'Keine Dokumente in der Warteschlange' : 'No documents in queue'}</p>
                      <p className="text-xs mt-1">{lang === 'de' ? 'Dokumente werden hier angezeigt, sobald Bewerber ihre Unterlagen hochladen.' : 'Documents will appear here once applicants upload their files.'}</p>
                    </td>
                  </tr>
                ) : filtered.map(row => (
                  <tr key={row.id} data-testid={`staff-document-row-${row.id}`}>
                    <td>
                      <div className="flex items-center gap-2">
                        <FileText size={14} className="text-[var(--color-text-tertiary)] shrink-0" />
                        <span className="text-sm font-semibold text-[var(--color-text-primary)] truncate max-w-[180px]">{row.filename || 'Unbenannt'}</span>
                      </div>
                    </td>
                    <td className="text-sm text-[var(--color-text-secondary)]">{row.applicant_name}</td>
                    <td className="text-sm text-[var(--color-text-secondary)]">{row.document_type}</td>
                    <td>
                      <span className={`w2g-badge ${STATUS_BADGE[row.status] || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
                        {getDocStatusLabel(row.status, lang)}
                      </span>
                    </td>
                    <td className="text-sm text-[var(--color-text-secondary)]">
                      {row.uploaded_at ? new Date(row.uploaded_at).toLocaleDateString(lang === 'de' ? 'de-DE' : 'en-US') : (row.created_at ? new Date(row.created_at).toLocaleDateString(lang === 'de' ? 'de-DE' : 'en-US') : '\u2014')}
                    </td>
                    <td className="text-xs text-[var(--color-text-secondary)]">
                      {row.validation_status || (lang === 'de' ? 'KI-Pruefung vorhanden' : 'AI check available')}
                    </td>
                    <td className="text-right">
                      <div className="flex items-center gap-2 justify-end">
                        <button onClick={() => setReviewDoc(row)}
                          className="w2g-btn-table-action"
                          data-testid={`doc-review-btn-${row.id}`}>
                          <Eye size={11} /> {lang === 'de' ? 'Pruefen' : 'Review'}
                        </button>
                        {row.has_binary && row.storage_key && (
                          <a href={`${API}/api/documents/${row.id}/download`} target="_blank" rel="noopener noreferrer"
                            className="w2g-btn-table-secondary"
                            data-testid={`doc-table-download-${row.id}`} title={lang === 'de' ? 'Dokument oeffnen' : 'Open document'}>
                            <ExternalLink size={11} />
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Review Modal */}
      {reviewDoc && (
        <ReviewModal
          doc={reviewDoc}
          onClose={() => setReviewDoc(null)}
          onAction={handleReviewAction}
        />
      )}
    </PageScaffold>
  );
}
