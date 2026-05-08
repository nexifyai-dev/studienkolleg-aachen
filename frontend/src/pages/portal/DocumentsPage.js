import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { toast } from 'sonner';
import {
  Upload, FileText, Shield, GraduationCap, Camera, Languages, File,
  CheckCircle, Clock, XCircle, AlertTriangle, Info, Eye, X, Loader2
} from 'lucide-react';
import { getDocumentKnowledge } from '../../lib/portalKnowledge';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';
import { API } from '../../lib/apiBase';

const STATUS_CONFIG = {
  uploaded: { color: 'bg-[var(--color-info-bg)] text-[var(--color-info)]', icon: Clock, label_de: 'Hochgeladen', label_en: 'Uploaded' },
  pending: { color: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]', icon: Clock, label_de: 'In Pruefung', label_en: 'Under Review' },
  in_review: { color: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]', icon: Clock, label_de: 'In Pruefung', label_en: 'Under Review' },
  approved: { color: 'bg-[var(--color-success-bg)] text-[var(--color-success)]', icon: CheckCircle, label_de: 'Akzeptiert', label_en: 'Accepted' },
  accepted: { color: 'bg-[var(--color-success-bg)] text-[var(--color-success)]', icon: CheckCircle, label_de: 'Akzeptiert', label_en: 'Accepted' },
  validated: { color: 'bg-[var(--color-success-bg)] text-[var(--color-success)]', icon: CheckCircle, label_de: 'Validiert', label_en: 'Validated' },
  needs_review: { color: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]', icon: AlertTriangle, label_de: 'Wird geprueft', label_en: 'Under Review' },
  rejected: { color: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]', icon: XCircle, label_de: 'Abgelehnt', label_en: 'Rejected' },
};

const DOC_ICONS = { Shield, GraduationCap, Camera, Languages, File, FileText };

const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
const MAX_SIZE = 10 * 1024 * 1024;

/* ── Dynamische Pflicht-/Optional-Dokumente je Bewerbungstyp ─── */
const COURSE_DOC_REQUIREMENTS = {
  // Studienkolleg (M/T/W-Kurse)
  'M-Course': { required: ['passport', 'highschool_diploma', 'language_certificate'], optional: ['transcript', 'motivation_letter', 'cv', 'photo'] },
  'T-Course': { required: ['passport', 'highschool_diploma', 'language_certificate'], optional: ['transcript', 'motivation_letter', 'cv', 'photo'] },
  'W-Course': { required: ['passport', 'highschool_diploma', 'language_certificate'], optional: ['transcript', 'motivation_letter', 'cv', 'photo'] },
  'M/T-Course': { required: ['passport', 'highschool_diploma', 'language_certificate'], optional: ['transcript', 'motivation_letter', 'cv', 'photo'] },
  'T-Kurs': { required: ['passport', 'highschool_diploma', 'language_certificate'], optional: ['transcript', 'motivation_letter', 'cv', 'photo'] },
  'M-Kurs': { required: ['passport', 'highschool_diploma', 'language_certificate'], optional: ['transcript', 'motivation_letter', 'cv', 'photo'] },
  'W-Kurs': { required: ['passport', 'highschool_diploma', 'language_certificate'], optional: ['transcript', 'motivation_letter', 'cv', 'photo'] },
  // Sprachkurs
  'Language Course': { required: ['passport', 'language_certificate'], optional: ['photo'] },
  'Sprachkurs': { required: ['passport', 'language_certificate'], optional: ['photo'] },
  // Pflegeausbildung
  'Pflegeausbildung': { required: ['passport', 'highschool_diploma', 'language_certificate', 'cv'], optional: ['transcript', 'motivation_letter', 'photo', 'other'] },
  'Pflege': { required: ['passport', 'highschool_diploma', 'language_certificate', 'cv'], optional: ['transcript', 'motivation_letter', 'photo', 'other'] },
  // Direktstudium
  'Direktstudium': { required: ['passport', 'highschool_diploma', 'language_certificate', 'transcript'], optional: ['motivation_letter', 'cv', 'photo'] },
  'Fachstudium': { required: ['passport', 'highschool_diploma', 'language_certificate', 'transcript'], optional: ['motivation_letter', 'cv', 'photo'] },
};

const DEFAULT_REQUIRED = ['passport', 'highschool_diploma', 'language_certificate'];
const DEFAULT_OPTIONAL = ['transcript', 'motivation_letter', 'cv', 'photo'];

function getRequiredDocTypes(courseType) {
  if (!courseType) return DEFAULT_REQUIRED;
  const config = COURSE_DOC_REQUIREMENTS[courseType];
  return config ? config.required : DEFAULT_REQUIRED;
}

function getOptionalDocTypes(courseType) {
  if (!courseType) return DEFAULT_OPTIONAL;
  const config = COURSE_DOC_REQUIREMENTS[courseType];
  return config ? config.optional : DEFAULT_OPTIONAL;
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/* In-Browser Vorschau Modal */
function PreviewModal({ doc, onClose }) {
  const isPdf = doc.content_type === 'application/pdf' || doc.filename?.endsWith('.pdf');
  const isImage = doc.content_type?.startsWith('image/');
  const downloadUrl = `${API}/api/documents/${doc.id}/download`;

  return (
    <div className="w2g-modal-overlay" onClick={onClose} data-testid="doc-preview-modal">
      <div className="w2g-modal" style={{ maxWidth: '900px', height: '85vh' }} onClick={e => e.stopPropagation()}>
        <div className="w2g-modal-header">
          <div className="min-w-0 flex-1">
            <h3 className="font-heading text-base font-bold text-[var(--color-primary)] truncate">{doc.filename}</h3>
            <p className="text-[11px] text-[var(--color-text-tertiary)]">{doc.document_type}</p>
          </div>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="preview-close"><X size={16} /></button>
        </div>
        <div className="flex-1 overflow-hidden" style={{ height: 'calc(85vh - 130px)' }}>
          {isPdf ? (
            <iframe src={`${downloadUrl}#toolbar=1`} className="w-full h-full border-0" title={doc.filename} />
          ) : isImage ? (
            <div className="w-full h-full flex items-center justify-center bg-[var(--color-surface-sunken)] p-4">
              <img src={downloadUrl} alt={doc.filename} className="max-w-full max-h-full object-contain" style={{ borderRadius: 'var(--radius-md)' }} />
            </div>
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center gap-4">
              <FileText size={48} className="text-[var(--color-text-tertiary)]" />
              <p className="text-sm text-[var(--color-text-secondary)]">Vorschau nicht verfuegbar</p>
              <a href={downloadUrl} target="_blank" rel="noopener noreferrer" className="w2g-btn-primary text-sm" data-testid="preview-download">Herunterladen</a>
            </div>
          )}
        </div>
        <div className="w2g-modal-footer">
          <a href={downloadUrl} target="_blank" rel="noopener noreferrer" className="w2g-btn-secondary text-sm" data-testid="preview-download-btn">Herunterladen</a>
          <button onClick={onClose} className="w2g-btn-primary text-sm">Schliessen</button>
        </div>
      </div>
    </div>
  );
}

/* Drag & Drop Upload Zone */
function UploadZone({ appId, docType, lang, onUploaded }) {
  const fileRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const processFile = useCallback(async (file) => {
    if (!file) return;
    if (!ALLOWED_TYPES.includes(file.type)) {
      toast.error(lang === 'de' ? 'Dateityp nicht erlaubt (PDF, JPG, PNG, DOCX)' : 'File type not allowed (PDF, JPG, PNG, DOCX)');
      return;
    }
    if (file.size > MAX_SIZE) {
      toast.error(lang === 'de' ? 'Datei zu gross (max. 10 MB)' : 'File too large (max. 10 MB)');
      return;
    }

    setUploading(true);
    setProgress(20);
    try {
      const base64 = await fileToBase64(file);
      setProgress(60);
      await apiClient.post(`/api/applications/${appId}/documents/upload`, {
        document_type: docType,
        filename: file.name,
        content_type: file.type,
        file_data: base64,
      }, { withCredentials: true });
      setProgress(100);
      toast.success(lang === 'de' ? 'Dokument hochgeladen' : 'Document uploaded');
      onUploaded();
    } catch (e) {
      const detail = e.response?.data?.detail;
      toast.error(detail || (lang === 'de' ? 'Upload fehlgeschlagen' : 'Upload failed'));
    } finally {
      setUploading(false);
      setProgress(0);
    }
  }, [appId, docType, lang, onUploaded]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer?.files?.[0];
    if (file) processFile(file);
  }, [processFile]);

  return (
    <div
      className={`relative border-2 border-dashed transition-all p-6 text-center cursor-pointer ${
        dragActive
          ? 'border-[var(--color-accent)] bg-[var(--color-accent-muted)]'
          : 'border-[var(--color-divider)] hover:border-[var(--color-primary)] bg-[var(--color-surface-elevated)]'
      }`}
      style={{ borderRadius: 'var(--radius-md)' }}
      onDragOver={e => { e.preventDefault(); setDragActive(true); }}
      onDragLeave={() => setDragActive(false)}
      onDrop={handleDrop}
      onClick={() => !uploading && fileRef.current?.click()}
      data-testid={`upload-zone-${docType}`}
    >
      <input ref={fileRef} type="file" className="hidden"
        accept=".pdf,.jpg,.jpeg,.png,.webp,.doc,.docx"
        onChange={e => { const f = e.target.files?.[0]; if (f) processFile(f); e.target.value = ''; }}
        data-testid={`file-input-${docType}`} />

      {uploading ? (
        <div className="space-y-2">
          <Loader2 size={24} className="mx-auto animate-spin text-[var(--color-accent)]" />
          <p className="text-xs text-[var(--color-text-secondary)]">{lang === 'de' ? 'Wird hochgeladen...' : 'Uploading...'}</p>
          <div className="w-48 mx-auto h-1.5 bg-[var(--color-divider)]" style={{ borderRadius: 'var(--radius-full)' }}>
            <div className="h-full bg-[var(--color-accent)] transition-all" style={{ width: `${progress}%`, borderRadius: 'var(--radius-full)' }} />
          </div>
        </div>
      ) : (
        <>
          <Upload size={24} className={`mx-auto mb-2 ${dragActive ? 'text-[var(--color-accent)]' : 'text-[var(--color-text-tertiary)]'}`} />
          <p className="text-xs font-medium text-[var(--color-text-primary)]">
            {lang === 'de' ? 'Datei hierher ziehen oder klicken' : 'Drag file here or click to upload'}
          </p>
          <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1">PDF, JPG, PNG, DOCX (max. 10 MB)</p>
        </>
      )}
    </div>
  );
}

export default function DocumentsPage() {
  const { i18n } = useTranslation();
  const [documents, setDocuments] = useState([]);
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedType, setExpandedType] = useState(null);
  const [preview, setPreview] = useState(null);
  const lang = i18n.language === 'en' ? 'en' : 'de';

  const loadData = useCallback(async () => {
    try {
      const [docsRes, appsRes] = await Promise.all([
        apiClient.get('/api/documents/my', { withCredentials: true }),
        apiClient.get('/api/applications', { withCredentials: true }),
      ]);
      setDocuments(docsRes.data || []);
      setApps(appsRes.data || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <div className="w2g-loading"><div className="w2g-spinner" /><p className="w2g-loading-text">Wird geladen...</p></div>;

  const requiredTypes = getRequiredDocTypes(apps[0]?.course_type);
  const optionalTypes = getOptionalDocTypes(apps[0]?.course_type);
  const uploadedByType = {};
  documents.forEach(d => {
    if (!uploadedByType[d.document_type]) uploadedByType[d.document_type] = [];
    uploadedByType[d.document_type].push(d);
  });
  const allTypes = [...new Set([...requiredTypes, ...optionalTypes, ...Object.keys(uploadedByType)])];

  // Status-Zusammenfassung
  const statusSummary = {
    total: documents.length,
    accepted: documents.filter(d => ['approved', 'accepted', 'validated'].includes(d.status)).length,
    pending: documents.filter(d => ['uploaded', 'in_review', 'needs_review', 'pending'].includes(d.status)).length,
    rejected: documents.filter(d => d.status === 'rejected').length,
  };

  return (
    <PageScaffold
      title={lang === 'de' ? 'Dokumentencenter' : 'Document Center'}
      subtitle={lang === 'de' ? 'Verwalte deine Dokumente und pruefe den Status' : 'Manage your documents and check their status'}
      testId="documents-page"
    >
      <div className="w2g-callout-info" data-testid="docs-help-banner">
        <Info size={16} className="shrink-0 mt-0.5 text-[var(--color-info)]" />
        <p className="text-xs text-[var(--color-text-secondary)]">
          {lang === 'de'
            ? 'Klicke auf eine Dokumentkarte, um ein Dokument hochzuladen oder das bestehende anzusehen. Abgelehnte Dokumente koennen erneut hochgeladen werden.'
            : 'Click on a document card to upload or view an existing document. Rejected documents can be re-uploaded.'}
        </p>
      </div>

      {!apps[0] && (
        <div className="w2g-empty" data-testid="docs-empty">
          <FileText size={32} className="w2g-empty-icon" />
          <p className="w2g-empty-text">{lang === 'de' ? 'Starte zuerst eine Bewerbung' : 'Start an application first'}</p>
          <a href="/apply" className="w2g-btn-primary mt-3 inline-block" data-testid="docs-apply-link">{lang === 'de' ? 'Jetzt bewerben' : 'Apply Now'}</a>
        </div>
      )}

      {apps[0] && (
        <div className="space-y-3" data-testid="docs-list">
          {/* Status-Uebersicht */}
          {statusSummary.total > 0 && (
            <div className="grid grid-cols-3 gap-2 mb-2" data-testid="docs-status-summary">
              <div className="p-3 bg-[var(--color-success-bg)] border border-[var(--color-success-border)]" style={{ borderRadius: 'var(--radius-md)' }}>
                <p className="text-lg font-bold text-[var(--color-success)]">{statusSummary.accepted}</p>
                <p className="text-[10px] text-[var(--color-success)]">{lang === 'de' ? 'Akzeptiert' : 'Accepted'}</p>
              </div>
              <div className="p-3 bg-[var(--color-warning-bg)] border border-[var(--color-warning-border)]" style={{ borderRadius: 'var(--radius-md)' }}>
                <p className="text-lg font-bold text-[var(--color-warning)]">{statusSummary.pending}</p>
                <p className="text-[10px] text-[var(--color-warning)]">{lang === 'de' ? 'In Pruefung' : 'Pending'}</p>
              </div>
              <div className="p-3 bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)]" style={{ borderRadius: 'var(--radius-md)' }}>
                <p className="text-lg font-bold text-[var(--color-danger)]">{statusSummary.rejected}</p>
                <p className="text-[10px] text-[var(--color-danger)]">{lang === 'de' ? 'Abgelehnt' : 'Rejected'}</p>
              </div>
            </div>
          )}
          {allTypes.map(type => {
            const docInfo = getDocumentKnowledge(type, lang);
            const uploaded = uploadedByType[type] || [];
            const isRequired = requiredTypes.includes(type);
            const isMissing = uploaded.length === 0;
            const hasRejected = uploaded.some(d => d.status === 'rejected');
            const latestDoc = uploaded[uploaded.length - 1];
            const latestStatus = latestDoc?.status;
            const statusCfg = STATUS_CONFIG[latestStatus] || {};
            const IconComponent = DOC_ICONS[docInfo?.icon] || FileText;
            const StatusIcon = statusCfg.icon || Clock;
            const isExpanded = expandedType === type;

            return (
              <Card key={type}
                className={`p-0 overflow-hidden transition-all ${hasRejected ? 'border-[var(--color-danger-border)]' : isMissing && isRequired ? 'border-[var(--color-warning-border)]' : ''}`}
                data-testid={`doc-card-${type}`}>

                {/* Card Header - Klickbar */}
                <div className="p-4 cursor-pointer hover:bg-[var(--color-surface-elevated)] transition-colors"
                  onClick={() => setExpandedType(isExpanded ? null : type)}
                  data-testid={`doc-card-toggle-${type}`}>
                  <div className="flex items-start gap-3">
                    <div className={`w-10 h-10 flex items-center justify-center shrink-0 ${
                      hasRejected ? 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]' :
                      isMissing ? 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]' :
                      latestStatus === 'approved' || latestStatus === 'accepted' ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]' :
                      'bg-primary-muted text-primary'
                    }`} style={{ borderRadius: 'var(--radius-sm)' }}>
                      <IconComponent size={20} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="text-sm font-semibold text-[var(--color-text-primary)] truncate">{docInfo?.label || type}</h4>
                        {isRequired && (
                          <span className="text-[9px] font-bold text-primary bg-primary-muted px-1.5 py-0.5 shrink-0" style={{ borderRadius: 'var(--radius-xs)' }}>
                            {lang === 'de' ? 'PFLICHT' : 'REQUIRED'}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[var(--color-text-secondary)]">{docInfo?.purpose}</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {latestDoc?.has_binary && (
                        <button onClick={e => { e.stopPropagation(); setPreview(latestDoc); }}
                          className="w2g-btn-icon" style={{ width: '28px', height: '28px' }}
                          title={lang === 'de' ? 'Vorschau' : 'Preview'} data-testid={`doc-preview-btn-${type}`}>
                          <Eye size={14} />
                        </button>
                      )}
                      {latestStatus ? (
                        <span className={`w2g-badge shrink-0 flex items-center gap-1 ${statusCfg.color || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
                          <StatusIcon size={10} />
                          {lang === 'de' ? statusCfg.label_de : statusCfg.label_en}
                        </span>
                      ) : (
                        <span className="w2g-badge bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)] shrink-0">
                          {lang === 'de' ? 'Fehlt' : 'Missing'}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Rejection / Validation Feedback */}
                  {hasRejected && (
                    <div className="mt-3 bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)] p-3 flex items-start gap-2" style={{ borderRadius: 'var(--radius-sm)' }}>
                      <AlertTriangle size={14} className="text-[var(--color-danger)] mt-0.5 shrink-0" />
                      <div>
                        <p className="text-xs font-medium text-[var(--color-danger)]">{lang === 'de' ? 'Dokument abgelehnt' : 'Document rejected'}</p>
                        {latestDoc?.rejection_reason && <p className="text-xs text-[var(--color-danger)] mt-0.5">{latestDoc.rejection_reason}</p>}
                        <p className="text-[10px] text-[var(--color-danger)] mt-1">{lang === 'de' ? 'Bitte lade eine neue Version hoch.' : 'Please upload a new version.'}</p>
                      </div>
                    </div>
                  )}

                  {latestDoc?.validation_status === 'needs_review' && !hasRejected && (
                    <div className="mt-3 bg-[var(--color-warning-bg)] border border-[var(--color-warning-border)] p-3 flex items-start gap-2" style={{ borderRadius: 'var(--radius-sm)' }}>
                      <Clock size={14} className="text-[var(--color-warning)] mt-0.5 shrink-0" />
                      <p className="text-xs text-[var(--color-warning)]">{lang === 'de' ? 'Wird von unserem Team geprueft.' : 'Being reviewed by our team.'}</p>
                    </div>
                  )}

                  {isMissing && isRequired && (
                    <div className="mt-3 bg-[var(--color-warning-bg)] border border-[var(--color-warning-border)] p-3 flex items-start gap-2" style={{ borderRadius: 'var(--radius-sm)' }}>
                      <AlertTriangle size={14} className="text-[var(--color-warning)] mt-0.5 shrink-0" />
                      <p className="text-xs text-[var(--color-warning)]">{lang === 'de' ? 'Dieses Dokument wird benoetigt.' : 'This document is required.'}</p>
                    </div>
                  )}
                </div>

                {/* Expanded: Upload Zone + History */}
                {isExpanded && (
                  <div className="border-t border-[var(--color-divider)] p-4 bg-[var(--color-surface-elevated)] space-y-4 animate-fade-in" data-testid={`doc-expanded-${type}`}>
                    <UploadZone appId={apps[0].id} docType={type} lang={lang} onUploaded={loadData} />

                    {/* Upload-Historie fuer diesen Typ */}
                    {uploaded.length > 0 && (
                      <div>
                        <p className="text-[11px] font-semibold text-[var(--color-text-secondary)] mb-2 uppercase tracking-wide">{lang === 'de' ? 'Hochgeladene Versionen' : 'Uploaded versions'}</p>
                        <div className="space-y-1.5">
                          {uploaded.map(doc => {
                            const sc = STATUS_CONFIG[doc.status] || {};
                            const SI = sc.icon || Clock;
                            return (
                              <div key={doc.id} className="flex items-center justify-between bg-[var(--color-surface)] border border-[var(--color-divider-subtle)] px-3 py-2" style={{ borderRadius: 'var(--radius-sm)' }} data-testid={`doc-version-${doc.id}`}>
                                <div className="flex items-center gap-2 min-w-0 flex-1">
                                  <FileText size={14} className="text-[var(--color-text-tertiary)] shrink-0" />
                                  <div className="min-w-0">
                                    <p className="text-xs font-medium text-[var(--color-text-primary)] truncate">{doc.filename}</p>
                                    <p className="text-[10px] text-[var(--color-text-tertiary)]">{doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString('de-DE') : ''}{doc.file_size ? ` · ${(doc.file_size / 1024).toFixed(0)} KB` : ''}</p>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2 shrink-0">
                                  {doc.has_binary && (
                                    <button onClick={() => setPreview(doc)} className="text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors"
                                      data-testid={`doc-view-${doc.id}`} title={lang === 'de' ? 'Vorschau' : 'Preview'}>
                                      <Eye size={14} />
                                    </button>
                                  )}
                                  <button onClick={async (e) => {
                                    e.stopPropagation();
                                    if (!window.confirm(lang === 'de' ? 'Dokument wirklich loeschen?' : 'Really delete this document?')) return;
                                    try {
                                      await apiClient.delete(`/api/documents/${doc.id}`, { withCredentials: true });
                                      toast.success(lang === 'de' ? 'Dokument geloescht' : 'Document deleted');
                                      loadData();
                                    } catch (err) {
                                      toast.error(err.response?.data?.detail || (lang === 'de' ? 'Loeschen fehlgeschlagen' : 'Delete failed'));
                                    }
                                  }} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)] transition-colors"
                                    data-testid={`doc-delete-${doc.id}`} title={lang === 'de' ? 'Loeschen' : 'Delete'}>
                                    <X size={14} />
                                  </button>
                                  <span className={`w2g-badge flex items-center gap-1 ${sc.color || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
                                    <SI size={10} />{lang === 'de' ? sc.label_de : sc.label_en}
                                  </span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Footer mit Format-Info */}
                <div className="border-t border-[var(--color-divider-subtle)] px-4 py-2 bg-[var(--color-surface-elevated)] flex items-center justify-between">
                  <div className="flex items-center gap-4 text-[10px] text-[var(--color-text-tertiary)]">
                    <span>{lang === 'de' ? 'Formate' : 'Formats'}: {docInfo?.formats}</span>
                  </div>
                  <button onClick={() => setExpandedType(isExpanded ? null : type)}
                    className="text-[11px] font-medium text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors"
                    data-testid={`doc-toggle-btn-${type}`}>
                    {isExpanded
                      ? (lang === 'de' ? 'Schliessen' : 'Close')
                      : (isMissing ? (lang === 'de' ? 'Hochladen' : 'Upload') : (lang === 'de' ? 'Details' : 'Details'))}
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* In-Browser Preview Modal */}
      {preview && <PreviewModal doc={preview} onClose={() => setPreview(null)} />}
    </PageScaffold>
  );
}
