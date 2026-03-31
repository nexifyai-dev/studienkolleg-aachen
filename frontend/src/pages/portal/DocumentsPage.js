import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { FileText, Upload, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import { QuickActions, EmptyState } from '../../components/shared/crmPatterns';
import { formatDate } from '../../lib/utils';


export default function DocumentsPage() {
  const { t } = useTranslation();
  const [apps, setApps] = useState([]);
  const [docs, setDocs] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadForm, setUploadForm] = useState({ doc_type: 'passport', filename: '' });
  const [showUpload, setShowUpload] = useState(false);
  const [loading, setLoading] = useState(true);

  const STATUS_CONFIG = {
    uploaded: { label: t('portal.doc_status_uploaded'), icon: Clock, color: 'text-primary bg-primary/8' },
    in_review: { label: t('portal.doc_status_in_review'), icon: Clock, color: 'text-slate-600 bg-slate-100' },
    approved: { label: t('portal.doc_status_approved'), icon: CheckCircle, color: 'text-primary bg-primary/12' },
    rejected: { label: t('portal.doc_status_rejected'), icon: XCircle, color: 'text-red-600 bg-red-50' },
    missing: { label: t('portal.doc_status_missing'), icon: AlertCircle, color: 'text-slate-500 bg-slate-50' },
  };

  useEffect(() => {
    const load = async () => {
      try {
        const appsRes = await apiClient.get(`/api/applications`, { withCredentials: true });
        setApps(appsRes.data);
        if (appsRes.data[0]) {
          const docsRes = await apiClient.get(`/api/applications/${appsRes.data[0].id}/documents`, { withCredentials: true });
          setDocs(docsRes.data);
        }
      } catch {}
      finally { setLoading(false); }
    };
    load();
  }, []);

  const handleUpload = async e => {
    e.preventDefault();
    if (!apps[0]) return;
    setUploading(true);
    try {
      await apiClient.post(`/api/applications/${apps[0].id}/documents/upload`,
        { document_type: uploadForm.doc_type, filename: uploadForm.filename || uploadForm.doc_type },
        { withCredentials: true }
      );
      const docsRes = await apiClient.get(`/api/applications/${apps[0].id}/documents`, { withCredentials: true });
      setDocs(docsRes.data);
      setShowUpload(false);
    } catch (e) { console.error(e); }
    finally { setUploading(false); }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="documents-page">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-heading font-bold text-primary">{t('portal.documents')}</h1>
          <p className="text-slate-500 text-sm mt-1">{t('portal.docs_management')}</p>
        </div>
        {apps[0] && (
          <button onClick={() => setShowUpload(!showUpload)} data-testid="docs-upload-toggle"
            className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover transition-colors">
            <Upload size={16} />
            {t('portal.upload_doc')}
          </button>
        )}
      </div>

      {/* Upload form */}
      {showUpload && (
        <div className="bg-white border border-slate-200 rounded-sm p-5" data-testid="docs-upload-form">
          <h3 className="font-semibold text-slate-800 mb-4">{t('portal.doc_upload_title')}</h3>
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('portal.doc_type_label')}</label>
              <select value={uploadForm.doc_type} onChange={e => setUploadForm(p => ({...p, doc_type: e.target.value}))}
                data-testid="docs-type-select"
                className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary">
                <option value="passport">{t('portal.doc_type_passport')}</option>
                <option value="school_certificate">{t('portal.doc_type_school')}</option>
                <option value="language_certificate">{t('portal.doc_type_language')}</option>
                <option value="photo">{t('portal.doc_type_photo')}</option>
                <option value="birth_certificate">{t('portal.doc_type_birth')}</option>
                <option value="other">{t('portal.doc_type_other')}</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('portal.doc_filename_label')}</label>
              <input value={uploadForm.filename} onChange={e => setUploadForm(p => ({...p, filename: e.target.value}))}
                placeholder={t('portal.doc_filename_placeholder')} data-testid="docs-filename-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
            </div>
            <div className="flex gap-3">
              <button type="submit" disabled={uploading} data-testid="docs-upload-submit"
                className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover disabled:opacity-60">
                {uploading ? t('portal.doc_uploading') : t('portal.doc_upload_btn')}
              </button>
              <button type="button" onClick={() => setShowUpload(false)}
                className="border border-slate-200 text-slate-600 px-4 py-2 rounded-sm text-sm hover:bg-slate-50">
                {t('portal.doc_cancel')}
              </button>
            </div>
          </form>
        </div>
      )}

      <QuickActions testId="docs-quick-actions">
        {apps[0] && (
          <button onClick={() => setShowUpload(!showUpload)} data-testid="docs-upload-quick" className="flex items-center gap-2 bg-white border border-slate-200 rounded-sm p-3 text-sm hover:border-primary/30">
            <Upload size={16} className="text-primary" /> {t('portal.upload_doc')}
          </button>
        )}
      </QuickActions>

      {/* Documents list */}
      {docs.length === 0 ? (
        <div>
          <EmptyState icon={FileText} title={t('portal.no_docs')} hint={apps[0] ? t('portal.doc_click_upload') : t('portal.doc_start_application')} testId="docs-empty" />
          {!apps[0] && (
            <div className="mt-3 text-center">
              <a href="/apply" className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover transition-colors inline-block" data-testid="docs-apply-link">{t('portal.doc_apply_link')}</a>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {docs.map(doc => {
            const statusCfg = STATUS_CONFIG[doc.status] || STATUS_CONFIG.uploaded;
            const Icon = statusCfg.icon;
            return (
              <div key={doc.id} className="bg-white border border-slate-200 rounded-sm p-4 flex items-center justify-between"
                data-testid={`doc-item-${doc.id}`}>
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 bg-slate-50 border border-slate-100 rounded-sm flex items-center justify-center">
                    <FileText size={18} className="text-slate-400" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-800 text-sm">{doc.filename || doc.document_type}</p>
                    <p className="text-xs text-slate-500">{doc.document_type} · {formatDate(doc.uploaded_at)}</p>
                    {doc.rejection_reason && (
                      <p className="text-xs text-red-600 mt-0.5">{t('portal.doc_rejection_reason')}: {doc.rejection_reason}</p>
                    )}
                  </div>
                </div>
                <span className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-sm ${statusCfg.color}`}>
                  <Icon size={12} />
                  {statusCfg.label}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
