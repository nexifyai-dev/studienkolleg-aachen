import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../lib/apiClient';
import { STAGE_LABELS, STAGE_COLORS } from '../../lib/utils';
import {
  RefreshCw, Brain, AlertTriangle, CheckCircle, FileX,
  Archive, Users, Filter, XCircle, ChevronDown
} from 'lucide-react';

// Kanban-Stages (aktive Pipeline)
const PIPELINE_STAGES = [
  'lead_new', 'in_review', 'pending_docs',
  'interview_scheduled', 'conditional_offer', 'offer_sent', 'enrolled',
];

// Abgeschlossene/Inaktive States – in separatem Archiv-Tab
const ARCHIVED_STAGES = ['declined', 'on_hold', 'archived', 'dormant'];

// Anabin-Badge Farben
const ANABIN_BADGE = {
  'H+': { cls: 'bg-primary/12 text-primary border-primary/25', label: 'H+' },
  'H':  { cls: 'bg-slate-100 text-slate-700 border-slate-200',  label: 'H'  },
  'D':  { cls: 'bg-red-50 text-red-700 border-red-200',     label: 'D'  },
  'prüfen': { cls: 'bg-slate-50 text-slate-500 border-slate-200', label: '?' },
  'unbekannt': { cls: 'bg-slate-50 text-slate-500 border-slate-200', label: '–' },
};

function AIBadge({ screening }) {
  if (!screening) return null;
  const anabin = ANABIN_BADGE[screening.anabin_category] || ANABIN_BADGE['unbekannt'];
  return (
    <div className="mt-2 flex items-center gap-1.5 flex-wrap" data-testid="kanban-ai-badge">
      {/* Vollständigkeit */}
      <span className={`inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-sm border ${
        screening.is_complete ? 'bg-primary/10 text-primary border-primary/25' : 'bg-slate-100 text-slate-600 border-slate-200'
      }`}>
        {screening.is_complete
          ? <CheckCircle size={10} />
          : <FileX size={10} />}
        {screening.is_complete ? 'Vollst.' : `${screening.missing_documents?.length || 0} fehlt`}
      </span>
      {/* Anabin */}
      <span className={`inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-sm border font-semibold ${anabin.cls}`}>
        <Brain size={10} /> {anabin.label}
      </span>
      {/* Sprachniveau */}
      {screening.language_level_ok === false && (
        <span className="inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-sm border bg-red-50 text-red-600 border-red-200">
          <AlertTriangle size={10} /> Sprache
        </span>
      )}
    </div>
  );
}

function KanbanCard({ app, latestScreening, onMove, nextStage }) {
  return (
    <div className="bg-white border border-slate-200 rounded-sm p-3 hover:border-primary/30 hover:shadow-card transition-all"
      data-testid={`kanban-card-${app.id}`}>

      {/* Name + Link */}
      <Link to={`/staff/applications/${app.id}`}
        className="font-medium text-slate-800 text-xs hover:text-primary transition-colors block truncate mb-1"
        data-testid={`kanban-card-link-${app.id}`}>
        {app.applicant?.full_name || app.applicant?.email || `#${app.id.slice(-6)}`}
      </Link>

      {/* Kurs + Semester */}
      {(app.course_type || app.desired_start) && (
        <p className="text-slate-400 text-xs truncate mb-1">
          {[app.course_type, app.desired_start].filter(Boolean).join(' · ')}
        </p>
      )}

      {/* Herkunftsland */}
      {app.degree_country && (
        <p className="text-slate-400 text-xs">{app.degree_country}</p>
      )}

      {/* AI Screening Badges */}
      <AIBadge screening={latestScreening} />

      {/* Advance-Button */}
      {nextStage && (
        <button
          onClick={() => onMove(app.id, nextStage)}
          className="mt-2 w-full text-xs text-primary border border-primary/20 rounded-sm py-1 hover:bg-primary/5 transition-colors"
          data-testid={`kanban-advance-${app.id}`}>
          → {STAGE_LABELS[nextStage] || nextStage}
        </button>
      )}
    </div>
  );
}

function ArchivedSection({ apps }) {
  const [open, setOpen] = useState(false);
  if (!apps.length) return null;
  return (
    <div className="mt-6" data-testid="kanban-archived-section">
      <button onClick={() => setOpen(!open)}
        className="flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-primary transition-colors mb-3">
        <Archive size={15} />
        Archiv / Abgelehnte Bewerbungen ({apps.length})
        <ChevronDown size={14} className={`transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="bg-slate-50 border border-slate-200 rounded-sm p-4">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-slate-500 font-medium border-b border-slate-200">
                  <th className="text-left pb-2 pr-4">Bewerber</th>
                  <th className="text-left pb-2 pr-4">Status</th>
                  <th className="text-left pb-2 pr-4">Kurs</th>
                  <th className="text-left pb-2 pr-4">Erstellt</th>
                  <th className="text-left pb-2">Aktion</th>
                </tr>
              </thead>
              <tbody>
                {apps.map(app => (
                  <tr key={app.id} className="border-b border-slate-100 hover:bg-white transition-colors"
                    data-testid={`archived-app-${app.id}`}>
                    <td className="py-2 pr-4">
                      <Link to={`/staff/applications/${app.id}`}
                        className="font-medium text-slate-700 hover:text-primary transition-colors text-xs">
                        {app.applicant?.full_name || app.applicant?.email || `#${app.id.slice(-6)}`}
                      </Link>
                    </td>
                    <td className="py-2 pr-4">
                      <span className={`text-xs px-2 py-0.5 rounded-sm ${STAGE_COLORS[app.current_stage] || 'bg-slate-100 text-slate-600'}`}>
                        {STAGE_LABELS[app.current_stage] || app.current_stage}
                      </span>
                    </td>
                    <td className="py-2 pr-4 text-xs text-slate-500">{app.course_type || '–'}</td>
                    <td className="py-2 pr-4 text-xs text-slate-400">
                      {app.created_at ? new Date(app.created_at).toLocaleDateString('de-DE') : '–'}
                    </td>
                    <td className="py-2">
                      <Link to={`/staff/applications/${app.id}`}
                        className="text-xs text-primary hover:underline"
                        data-testid={`archived-open-${app.id}`}>
                        Öffnen / Reaktivieren
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default function KanbanPage() {
  const [applications, setApplications] = useState([]);
  const [screenings, setScreenings] = useState({});  // appId → latest screening
  const [loading, setLoading] = useState(true);
  const [filterCourse, setFilterCourse] = useState('');
  const [showFilterMenu, setShowFilterMenu] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/applications', { withCredentials: true });
      const apps = res.data || [];
      setApplications(apps);

      // Latest screenings für alle Apps laden (batch)
      const screeningMap = {};
      await Promise.allSettled(
        apps.slice(0, 30).map(async app => {
          try {
            const sr = await apiClient.get(`/api/applications/${app.id}/ai-screenings`, { withCredentials: true });
            if (sr.data?.length) screeningMap[app.id] = sr.data[0];
          } catch {}
        })
      );
      setScreenings(screeningMap);
    } catch {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const moveApplication = async (appId, newStage) => {
    try {
      await apiClient.put(`/api/applications/${appId}`, { current_stage: newStage }, { withCredentials: true });
      setApplications(prev => prev.map(a => a.id === appId ? { ...a, current_stage: newStage } : a));
    } catch {}
  };

  const filtered = filterCourse
    ? applications.filter(a => a.course_type === filterCourse)
    : applications;

  const pipeline = filtered.filter(a => !ARCHIVED_STAGES.includes(a.current_stage));
  const archived = filtered.filter(a => ARCHIVED_STAGES.includes(a.current_stage));

  const appsByStage = PIPELINE_STAGES.reduce((acc, stage) => {
    acc[stage] = pipeline.filter(a => a.current_stage === stage);
    return acc;
  }, {});

  const COURSE_OPTIONS = ['T-Course', 'M-Course', 'W-Course', 'M/T-Course', 'Language Course'];

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  );

  return (
    <div className="space-y-4 animate-fade-in" data-testid="kanban-page">

      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-heading font-bold text-primary">Kanban Board</h1>
          <p className="text-slate-500 text-sm">
            {pipeline.length} aktiv · {archived.length} archiviert
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Filter */}
          <div className="relative">
            <button onClick={() => setShowFilterMenu(!showFilterMenu)}
              className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-primary border border-slate-200 px-3 py-2 rounded-sm hover:border-primary/50 transition-colors">
              <Filter size={14} />
              {filterCourse || 'Kurs filtern'}
              {filterCourse && (
                <XCircle size={13} className="text-slate-400 hover:text-red-500 ml-1"
                  onClick={e => { e.stopPropagation(); setFilterCourse(''); setShowFilterMenu(false); }} />
              )}
            </button>
            {showFilterMenu && (
              <div className="absolute right-0 top-full mt-1 bg-white border border-slate-200 rounded-sm shadow-card z-20 min-w-[160px]">
                {COURSE_OPTIONS.map(c => (
                  <button key={c} onClick={() => { setFilterCourse(c); setShowFilterMenu(false); }}
                    className={`w-full text-left px-3 py-2 text-sm hover:bg-primary/5 ${filterCourse === c ? 'text-primary font-medium' : 'text-slate-700'}`}>
                    {c}
                  </button>
                ))}
              </div>
            )}
          </div>

          <button onClick={load}
            className="flex items-center gap-2 text-slate-500 hover:text-primary text-sm border border-slate-200 px-3 py-2 rounded-sm hover:border-primary transition-colors"
            data-testid="kanban-refresh-btn">
            <RefreshCw size={14} /> Aktualisieren
          </button>
        </div>
      </div>

      {/* AI-Badge Legende */}
      <div className="flex items-center gap-4 text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-sm px-4 py-2">
        <span className="flex items-center gap-1"><Brain size={12} className="text-primary" /> Anabin-Kategorie:</span>
        {Object.entries(ANABIN_BADGE).slice(0, 4).map(([k, v]) => (
          <span key={k} className={`px-1.5 py-0.5 rounded-sm border text-xs ${v.cls}`}>{v.label} = {k}</span>
        ))}
        <span className="flex items-center gap-1 ml-2">
          <CheckCircle size={12} className="text-primary" /> = vollständig
          <FileX size={12} className="text-slate-400 ml-2" /> = Docs fehlen
        </span>
      </div>

      {/* Kanban Columns */}
      <div className="overflow-x-auto pb-4">
        <div className="flex gap-3" style={{ minWidth: `${PIPELINE_STAGES.length * 200}px` }}>
          {PIPELINE_STAGES.map((stage, stageIdx) => (
            <div key={stage} className="flex-1 min-w-[185px]" data-testid={`kanban-col-${stage}`}>
              <div className="flex items-center justify-between mb-3">
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-sm ${STAGE_COLORS[stage] || 'bg-slate-100 text-slate-700'}`}>
                  {STAGE_LABELS[stage] || stage}
                </span>
                <span className="text-xs text-slate-400 font-medium tabular-nums">
                  {appsByStage[stage].length}
                </span>
              </div>

              <div className="space-y-2 min-h-[100px]">
                {appsByStage[stage].map(app => (
                  <KanbanCard
                    key={app.id}
                    app={app}
                    latestScreening={screenings[app.id]}
                    onMove={moveApplication}
                    nextStage={stageIdx < PIPELINE_STAGES.length - 1 ? PIPELINE_STAGES[stageIdx + 1] : null}
                  />
                ))}
                {appsByStage[stage].length === 0 && (
                  <div className="border-2 border-dashed border-slate-100 rounded-sm py-6 text-center">
                    <Users size={16} className="text-slate-300 mx-auto mb-1" />
                    <p className="text-xs text-slate-300">Leer</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Archiv-Bereich */}
      <ArchivedSection apps={archived} />
    </div>
  );
}
