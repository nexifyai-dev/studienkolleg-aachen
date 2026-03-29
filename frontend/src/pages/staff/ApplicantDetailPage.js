import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../../lib/apiClient';
import { STAGE_LABELS, STAGE_COLORS, formatDate } from '../../lib/utils';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';


export default function ApplicantDetailPage() {
  const { id } = useParams();
  const [app, setApp] = useState(null);
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [appRes] = await Promise.all([
          apiClient.get(`/api/applications/${id}`, { withCredentials: true }),
        ]);
        setApp(appRes.data);
        const docsRes = await apiClient.get(`/api/applications/${id}/documents`, { withCredentials: true });
        setDocs(docsRes.data);
      } catch {}
      finally { setLoading(false); }
    };
    load();
  }, [id]);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;
  if (!app) return <div className="p-6 text-slate-500">Bewerbung nicht gefunden</div>;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="applicant-detail-page">
      <div className="flex items-center gap-3">
        <Link to="/staff/kanban" className="text-slate-400 hover:text-primary">
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-heading font-bold text-primary">
          {app.applicant?.full_name || 'Bewerber'}
        </h1>
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-sm ${STAGE_COLORS[app.current_stage] || 'bg-slate-100'}`}>
          {STAGE_LABELS[app.current_stage] || app.current_stage}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white border border-slate-200 rounded-sm p-5">
          <h3 className="font-semibold text-slate-700 mb-3 text-sm">Persönliche Daten</h3>
          <dl className="space-y-2 text-sm">
            {[
              ['Name', app.applicant?.full_name || '–'],
              ['E-Mail', app.applicant?.email || '–'],
              ['Telefon', app.applicant?.phone || '–'],
              ['Land', app.applicant?.country || '–'],
              ['Quelle', app.source || '–'],
              ['Erstellt', formatDate(app.created_at)],
            ].map(([label, value]) => (
              <div key={label} className="flex gap-2">
                <dt className="text-slate-500 w-24 shrink-0">{label}:</dt>
                <dd className="text-slate-800 font-medium">{value}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className="bg-white border border-slate-200 rounded-sm p-5">
          <h3 className="font-semibold text-slate-700 mb-3 text-sm">Dokumente ({docs.length})</h3>
          {docs.length === 0 ? (
            <p className="text-slate-400 text-sm">Noch keine Dokumente</p>
          ) : (
            <ul className="space-y-2">
              {docs.map(doc => (
                <li key={doc.id} className="flex items-center justify-between text-sm"
                  data-testid={`detail-doc-${doc.id}`}>
                  <span className="text-slate-700">{doc.filename || doc.document_type}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-sm ${
                    doc.status === 'approved' ? 'bg-green-100 text-green-700' :
                    doc.status === 'rejected' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                  }`}>{doc.status}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
