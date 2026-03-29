import React, { useEffect, useState } from 'react';
import apiClient from '../../lib/apiClient';
import { STAGE_LABELS, STAGE_COLORS } from '../../lib/utils';
import { Users, RefreshCw } from 'lucide-react';


const KANBAN_STAGES = [
  'lead_new', 'contacted', 'docs_requested', 'docs_received',
  'docs_review', 'invoice_open', 'payment_received', 'completed'
];

export default function KanbanPage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/applications`, { withCredentials: true });
      setApplications(res.data);
    } catch {}
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const moveApplication = async (appId, newStage) => {
    try {
      await apiClient.put(`/api/applications/${appId}`, { current_stage: newStage }, { withCredentials: true });
      setApplications(prev => prev.map(a => a.id === appId ? { ...a, current_stage: newStage } : a));
    } catch (e) { console.error(e); }
  };

  const appsByStage = KANBAN_STAGES.reduce((acc, stage) => {
    acc[stage] = applications.filter(a => a.current_stage === stage);
    return acc;
  }, {});

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  );

  return (
    <div className="space-y-4 animate-fade-in" data-testid="kanban-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold text-primary">Kanban Board</h1>
          <p className="text-slate-500 text-sm">{applications.length} Bewerbungen gesamt</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 text-slate-500 hover:text-primary text-sm border border-slate-200 px-3 py-2 rounded-sm hover:border-primary transition-colors"
          data-testid="kanban-refresh-btn">
          <RefreshCw size={14} />
          Aktualisieren
        </button>
      </div>

      <div className="overflow-x-auto pb-4">
        <div className="flex gap-3" style={{ minWidth: `${KANBAN_STAGES.length * 220}px` }}>
          {KANBAN_STAGES.map(stage => (
            <div key={stage} className="flex-1 min-w-[200px]" data-testid={`kanban-col-${stage}`}>
              <div className="flex items-center justify-between mb-3">
                <span className={`text-xs font-semibold px-2 py-1 rounded-sm ${STAGE_COLORS[stage] || 'bg-slate-100 text-slate-700'}`}>
                  {STAGE_LABELS[stage] || stage}
                </span>
                <span className="text-xs text-slate-400 font-medium">{appsByStage[stage].length}</span>
              </div>

              <div className="space-y-2 min-h-[120px]">
                {appsByStage[stage].map(app => (
                  <div key={app.id} className="bg-white border border-slate-200 rounded-sm p-3 hover:border-primary/30 hover:shadow-card transition-all cursor-default"
                    data-testid={`kanban-card-${app.id}`}>
                    <p className="font-medium text-slate-800 text-xs truncate">
                      {app.applicant?.full_name || app.applicant?.email || `#${app.id.slice(-6)}`}
                    </p>
                    <p className="text-slate-400 text-xs mt-1">{app.source || 'direct'}</p>

                    {/* Move to next stage */}
                    {KANBAN_STAGES.indexOf(stage) < KANBAN_STAGES.length - 1 && (
                      <button
                        onClick={() => moveApplication(app.id, KANBAN_STAGES[KANBAN_STAGES.indexOf(stage) + 1])}
                        className="mt-2 text-xs text-primary hover:underline"
                        data-testid={`kanban-advance-${app.id}`}>
                        → Weiter
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
