import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { STAGE_LABELS, STAGE_COLORS } from '../../lib/utils';
import { CheckCircle, Circle, Clock } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const ALL_STAGES = [
  'lead_new','contacted','docs_requested','docs_received',
  'docs_review','invoice_open','payment_received','process_next','completed'
];

export default function JourneyPage() {
  const { t } = useTranslation();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/api/applications`, { withCredentials: true })
      .then(r => setApplications(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="journey-page">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">{t('portal.journey')}</h1>
        <p className="text-slate-500 text-sm mt-1">Dein aktueller Bewerbungsfortschritt</p>
      </div>

      {applications.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-sm p-8 text-center" data-testid="journey-empty">
          <Circle size={32} className="text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">Noch keine aktive Bewerbung.</p>
        </div>
      ) : (
        applications.map(app => (
          <div key={app.id} className="bg-white border border-slate-200 rounded-sm p-6" data-testid="journey-application">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="font-semibold text-slate-800">{app.workspace_name || 'Studienkolleg'}</h3>
                <p className="text-xs text-slate-500">ID: #{app.id?.slice(-6).toUpperCase()}</p>
              </div>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-sm ${STAGE_COLORS[app.current_stage] || 'bg-slate-100 text-slate-600'}`}>
                {STAGE_LABELS[app.current_stage] || app.current_stage}
              </span>
            </div>

            {/* Timeline */}
            <div className="space-y-0">
              {ALL_STAGES.map((stage, idx) => {
                const currentIdx = ALL_STAGES.indexOf(app.current_stage);
                const isComplete = idx < currentIdx;
                const isCurrent = idx === currentIdx;
                const isPending = idx > currentIdx;

                return (
                  <div key={stage} className="flex gap-3" data-testid={`journey-stage-${stage}`}>
                    <div className="flex flex-col items-center">
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center border-2 shrink-0 ${
                        isComplete ? 'bg-primary border-primary' :
                        isCurrent ? 'bg-white border-primary' :
                        'bg-white border-slate-200'
                      }`}>
                        {isComplete ? <CheckCircle size={14} className="text-white" /> :
                         isCurrent ? <Clock size={12} className="text-primary" /> :
                         <Circle size={12} className="text-slate-300" />}
                      </div>
                      {idx < ALL_STAGES.length - 1 && (
                        <div className={`w-0.5 h-8 mt-1 ${isComplete ? 'bg-primary' : 'bg-slate-200'}`} />
                      )}
                    </div>
                    <div className="pb-4">
                      <p className={`text-sm font-medium ${isComplete ? 'text-slate-700' : isCurrent ? 'text-primary font-semibold' : 'text-slate-400'}`}>
                        {STAGE_LABELS[stage] || stage}
                      </p>
                      {isCurrent && <p className="text-xs text-primary mt-0.5">Aktueller Status</p>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
