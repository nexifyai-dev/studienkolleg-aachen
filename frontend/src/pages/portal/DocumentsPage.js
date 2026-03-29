import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { FileText, Upload, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import { formatDate } from '../../lib/utils';


const STATUS_CONFIG = {
  uploaded: { label: 'Hochgeladen', icon: Clock, color: 'text-primary bg-primary/8' },
  in_review: { label: 'In Prüfung', icon: Clock, color: 'text-slate-600 bg-slate-100' },
  approved: { label: 'Akzeptiert', icon: CheckCircle, color: 'text-primary bg-primary/12' },
  rejected: { label: 'Abgelehnt', icon: XCircle, color: 'text-red-600 bg-red-50' },
  missing: { label: 'Fehlt', icon: AlertCircle, color: 'text-slate-500 bg-slate-50' },
};

export default function DocumentsPage() {
  const { t } = useTranslation();
  const [apps, setApps] = useState([]);
  const [docs, setDocs] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadForm, setUploadForm] = useState({ doc_type: 'passport', filename: '' });
  const [showUpload, setShowUpload] = useState(false);
  const [loading, setLoading] = useState(true);

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold text-primary">{t('portal.documents')}</h1>
          <p className="text-slate-500 text-sm mt-1">Sichere Dokumentenverwaltung</p>
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
          <h3 className="font-semibold text-slate-800 mb-4">Dokument hochladen</h3>
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Dokumenttyp</label>
              <select value={uploadForm.doc_type} onChange={e => setUploadForm(p => ({...p, doc_type: e.target.value}))}
                data-testid="docs-type-select"
                className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary">
                <option value="passport">Reisepass / Ausweis</option>
                <option value="school_certificate">Schulzeugnis / Abschluss</option>
                <option value="language_certificate">Sprachzertifikat</option>
                <option value="photo">Lichtbild</option>
                <option value="birth_certificate">Geburtsurkunde</option>
                <option value="other">Sonstiges</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Dateiname</label>
              <input value={uploadForm.filename} onChange={e => setUploadForm(p => ({...p, filename: e.target.value}))}
                placeholder="z.B. reisepass_max_mustermann.pdf" data-testid="docs-filename-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
            </div>
            <div className="flex gap-3">
              <button type="submit" disabled={uploading} data-testid="docs-upload-submit"
                className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover disabled:opacity-60">
                {uploading ? 'Wird hochgeladen…' : 'Hochladen'}
              </button>
              <button type="button" onClick={() => setShowUpload(false)}
                className="border border-slate-200 text-slate-600 px-4 py-2 rounded-sm text-sm hover:bg-slate-50">
                Abbrechen
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Documents list */}
      {docs.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-sm p-8 text-center" data-testid="docs-empty">
          <FileText size={32} className="text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">{t('portal.no_docs')}</p>
          {apps[0] ? (
            <p className="text-xs text-slate-400 mt-2">Klicke auf „Dokument hochladen" um zu beginnen.</p>
          ) : (
            <div className="mt-4">
              <p className="text-xs text-slate-500 mb-3">Um Dokumente hochzuladen, starte zunächst deine Bewerbung.</p>
              <a href="/apply" className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover transition-colors inline-block"
                data-testid="docs-apply-link">Jetzt bewerben →</a>
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
                      <p className="text-xs text-red-600 mt-0.5">Ablehnungsgrund: {doc.rejection_reason}</p>
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
