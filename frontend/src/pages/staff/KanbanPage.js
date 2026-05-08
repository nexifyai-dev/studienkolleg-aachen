import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import apiClient from '../../lib/apiClient';
import { getStageLabel, STAGE_COLORS, getLang } from '../../lib/utils';
import { toast } from 'sonner';
import {
  RefreshCw, Brain, AlertTriangle, CheckCircle, FileX,
  Archive, Users, XCircle, ChevronDown, Search,
  GripVertical, Mail, Globe, FileText,
  Clock, Receipt, CalendarClock, ChevronRight,
  BookOpen
} from 'lucide-react';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';

const PIPELINE_STAGES = [
  'lead_new', 'in_review', 'pending_docs',
  'interview_scheduled', 'conditional_offer', 'offer_sent', 'enrolled',
];
const ARCHIVED_STAGES = ['declined', 'on_hold', 'archived', 'dormant'];
const COURSE_OPTIONS = ['T-Course', 'M-Course', 'W-Course', 'M/T-Course', 'Language Course'];

const ANABIN_BADGE = {
  'H+': { cls: 'bg-primary/12 text-primary border-primary/25', label: 'H+' },
  'H':  { cls: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-primary)] border-[var(--color-divider)]', label: 'H' },
  'D':  { cls: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border-[var(--color-danger-border)]', label: 'D' },
};

/* ═══════ Rich Kanban Card ═══════ */
function KanbanCard({ app, screening, tasks, invoices, followups, provided, isDragging }) {
  const anabin = screening ? (ANABIN_BADGE[screening.anabin_category] || null) : null;
  const missingDocs = screening?.missing_documents?.length || 0;
  const openTasks = (tasks || []).filter(t => t.status !== 'done').length;
  const overdueInvoices = (invoices || []).filter(i => i.status === 'overdue').length;
  const draftInvoices = (invoices || []).filter(i => i.status === 'draft').length;
  const activeFollowups = (followups || []).filter(f => f.status !== 'done').length;
  const hasRisk = screening?.language_level_ok === false || missingDocs > 2 || overdueInvoices > 0;

  return (
    <div
      ref={provided.innerRef}
      {...provided.draggableProps}
      className={`bg-white border rounded-[var(--radius-md)] transition-all duration-200 ${
        isDragging
          ? 'border-primary shadow-lg ring-2 ring-primary/25 rotate-[0.5deg] scale-[1.03]'
          : hasRisk
            ? 'border-[var(--color-warning-border)]/80 hover:border-[var(--color-warning-border)]'
            : 'border-[var(--color-divider)]/80 hover:border-primary/40 hover:shadow-md'
      }`}
      style={{
        ...provided.draggableProps.style,
        boxShadow: isDragging ? 'var(--shadow-elevated)' : undefined,
      }}
      data-testid={`kanban-card-${app.id}`}
    >
      {/* Risk indicator bar */}
      {hasRisk && (
        <div className="h-[3px] bg-gradient-to-r from-amber-400 to-red-400 rounded-t-lg" />
      )}

      <div className="p-3">
        {/* Header: Drag Handle + Name + Quick Link */}
        <div className="flex items-start gap-2">
          <div
            {...provided.dragHandleProps}
            className="mt-0.5 p-1 rounded bg-primary-muted text-primary hover:bg-primary/15 cursor-grab active:cursor-grabbing transition-colors shrink-0"
            data-testid={`kanban-drag-${app.id}`}
            title="Ziehen zum Verschieben"
            aria-label="Drag-Handle"
          >
            <GripVertical size={14} />
          </div>
          <div className="flex-1 min-w-0">
            <Link to={`/staff/applications/${app.id}`}
              className="font-semibold text-[var(--color-text-primary)] text-[13px] hover:text-primary transition-colors block truncate leading-tight"
              data-testid={`kanban-card-link-${app.id}`}>
              {app.applicant?.full_name || app.applicant?.email || `#${app.id.slice(-6)}`}
            </Link>
            {app.applicant_number && (
              <span className="text-[9px] font-mono text-primary/70 font-bold">{app.applicant_number}</span>
            )}
            {app.duplicate_flag && (
              <span className="inline-flex text-[7px] px-1 py-0.5 rounded bg-[var(--color-danger-bg)] text-[var(--color-danger)] font-bold border border-[var(--color-danger-border)] mt-0.5" data-testid={`kanban-dup-${app.id}`}>
                DUBLETTE
              </span>
            )}
            {app.applicant?.email && (
              <p className="text-[10px] text-[var(--color-text-tertiary)] truncate mt-0.5 flex items-center gap-1">
                <Mail size={9} className="shrink-0" />{app.applicant.email}
              </p>
            )}
          </div>
          <Link to={`/staff/applications/${app.id}`}
            className="text-[var(--color-text-tertiary)] hover:text-primary transition-colors shrink-0 mt-0.5"
            title="Fallakte oeffnen">
            <ChevronRight size={14} />
          </Link>
        </div>

        {/* Context Row: Land, Kurs, Semester */}
        <div className="mt-2 flex flex-wrap gap-x-3 gap-y-0.5 text-[10px] text-[var(--color-text-secondary)] ml-[30px]">
          {app.degree_country && (
            <span className="flex items-center gap-1"><Globe size={9} className="text-[var(--color-text-tertiary)]" />{app.degree_country}</span>
          )}
          {app.course_type && (
            <span className="flex items-center gap-1"><BookOpen size={9} className="text-[var(--color-text-tertiary)]" />{app.course_type}</span>
          )}
          {app.desired_start && (
            <span className="text-[var(--color-text-tertiary)]">{app.desired_start}</span>
          )}
        </div>

        {/* Signal Badges Row */}
        <div className="mt-2 flex flex-wrap gap-1 ml-[30px]">
          {/* Completeness */}
          {screening && (
            <span className={`inline-flex items-center gap-0.5 text-[9px] px-1.5 py-0.5 rounded border font-medium ${
              screening.is_complete
                ? 'bg-primary-muted text-primary border-primary/20'
                : 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border-[var(--color-warning-border)]'
            }`}>
              {screening.is_complete ? <CheckCircle size={8} /> : <FileX size={8} />}
              {screening.is_complete ? 'Vollst.' : `${missingDocs} fehlt`}
            </span>
          )}
          {/* Anabin */}
          {anabin && (
            <span className={`inline-flex items-center gap-0.5 text-[9px] px-1.5 py-0.5 rounded border font-bold ${anabin.cls}`}>
              <Brain size={8} /> {anabin.label}
            </span>
          )}
          {/* Language Risk */}
          {screening?.language_level_ok === false && (
            <span className="inline-flex items-center gap-0.5 text-[9px] px-1.5 py-0.5 rounded border bg-[var(--color-danger-bg)] text-[var(--color-danger)] border-[var(--color-danger-border)] font-medium">
              <AlertTriangle size={8} /> Sprache
            </span>
          )}
          {/* Language level */}
          {app.language_level && !screening?.language_level_ok === false && (
            <span className="text-[9px] px-1.5 py-0.5 rounded border border-[var(--color-divider)] bg-[var(--color-surface-elevated)] text-[var(--color-text-secondary)]">
              {app.language_level}
            </span>
          )}
        </div>

        {/* Operations Signals Row */}
        {(openTasks > 0 || overdueInvoices > 0 || draftInvoices > 0 || activeFollowups > 0) && (
          <div className="mt-1.5 flex flex-wrap gap-1.5 ml-[30px] text-[9px]">
            {openTasks > 0 && (
              <span className="flex items-center gap-0.5 text-[var(--color-text-secondary)]">
                <Clock size={8} /> {openTasks} Aufg.
              </span>
            )}
            {overdueInvoices > 0 && (
              <span className="flex items-center gap-0.5 text-[var(--color-danger)] font-medium">
                <Receipt size={8} /> {overdueInvoices} ueberfaellig
              </span>
            )}
            {draftInvoices > 0 && (
              <span className="flex items-center gap-0.5 text-[var(--color-text-tertiary)]">
                <FileText size={8} /> {draftInvoices} Entwurf
              </span>
            )}
            {activeFollowups > 0 && (
              <span className="flex items-center gap-0.5 text-primary font-medium">
                <CalendarClock size={8} /> {activeFollowups} WV
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ═══════ Archived Section ═══════ */
function ArchivedSection({ apps, lang }) {
  const [open, setOpen] = useState(false);
  if (!apps.length) return null;
  return (
    <div className="mt-6" data-testid="kanban-archived-section">
      <button onClick={() => setOpen(!open)}
        className="flex items-center gap-2 text-sm font-medium text-[var(--color-text-secondary)] hover:text-primary transition-colors mb-3">
        <Archive size={15} />
        {lang === 'de' ? 'Archiv / Abgelehnt' : 'Archive / Declined'} ({apps.length})
        <ChevronDown size={14} className={`transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="w2g-card p-0 overflow-hidden">
          <table className="w2g-table">
            <thead><tr><th>{lang === 'de' ? 'Bewerber' : 'Applicant'}</th><th>Status</th><th>{lang === 'de' ? 'Kurs' : 'Course'}</th><th>{lang === 'de' ? 'Erstellt' : 'Created'}</th><th>{lang === 'de' ? 'Aktion' : 'Action'}</th></tr></thead>
            <tbody>
              {apps.map(app => (
                <tr key={app.id} data-testid={`archived-app-${app.id}`}>
                  <td><Link to={`/staff/applications/${app.id}`} className="font-medium text-[var(--color-text-primary)] hover:text-primary text-xs">{app.applicant?.full_name || app.applicant?.email}</Link></td>
                  <td><span className={`w2g-badge ${STAGE_COLORS[app.current_stage] || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>{getStageLabel(app.current_stage, lang)}</span></td>
                  <td className="text-xs text-[var(--color-text-secondary)]">{app.course_type || '\u2013'}</td>
                  <td className="text-xs text-[var(--color-text-tertiary)]">{app.created_at ? new Date(app.created_at).toLocaleDateString(lang === 'de' ? 'de-DE' : 'en-US') : '\u2013'}</td>
                  <td><Link to={`/staff/applications/${app.id}`} className="w2g-btn-secondary w2g-btn-sm inline-flex">{lang === 'de' ? 'Oeffnen' : 'Open'}</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ═══════ Main Kanban Page ═══════ */
export default function KanbanPage() {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [searchParams, setSearchParams] = useSearchParams();
  const [applications, setApplications] = useState([]);
  const [screenings, setScreenings] = useState({});
  const [allTasks, setAllTasks] = useState([]);
  const [allInvoices, setAllInvoices] = useState([]);
  const [allFollowups, setAllFollowups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterCourse, setFilterCourse] = useState('');
  const [filterStage, setFilterStage] = useState(searchParams.get('stage') || '');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const stage = searchParams.get('stage');
    if (stage) setFilterStage(stage);
  }, [searchParams]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [appsRes, tasksRes, invoicesRes, followupsRes] = await Promise.all([
        apiClient.get('/api/applications', { withCredentials: true }),
        apiClient.get('/api/tasks', { withCredentials: true }).catch(() => ({ data: [] })),
        apiClient.get('/api/invoices', { withCredentials: true }).catch(() => ({ data: [] })),
        apiClient.get('/api/followups', { withCredentials: true }).catch(() => ({ data: [] })),
      ]);
      const apps = appsRes.data || [];
      setApplications(apps);
      setAllTasks(tasksRes.data || []);
      setAllInvoices(invoicesRes.data || []);
      setAllFollowups(followupsRes.data || []);

      // Load screenings for first 50 apps
      const screeningMap = {};
      await Promise.allSettled(
        apps.slice(0, 50).map(async app => {
          try {
            const sr = await apiClient.get(`/api/applications/${app.id}/ai-screenings`, { withCredentials: true });
            if (sr.data?.length) screeningMap[app.id] = sr.data[0];
          } catch {}
        })
      );
      setScreenings(screeningMap);
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  // Memoized task/invoice/followup maps by application
  const tasksByApp = useMemo(() => {
    const map = {};
    allTasks.forEach(t => {
      if (t.application_id) {
        if (!map[t.application_id]) map[t.application_id] = [];
        map[t.application_id].push(t);
      }
    });
    return map;
  }, [allTasks]);

  const invoicesByApp = useMemo(() => {
    const map = {};
    allInvoices.forEach(i => {
      if (i.applicant_id) {
        if (!map[i.applicant_id]) map[i.applicant_id] = [];
        map[i.applicant_id].push(i);
      }
    });
    return map;
  }, [allInvoices]);

  const followupsByApp = useMemo(() => {
    const map = {};
    allFollowups.forEach(f => {
      if (f.application_id) {
        if (!map[f.application_id]) map[f.application_id] = [];
        map[f.application_id].push(f);
      }
    });
    return map;
  }, [allFollowups]);

  const moveApplication = async (appId, newStage) => {
    try {
      await apiClient.put(`/api/applications/${appId}`, { current_stage: newStage }, { withCredentials: true });
      setApplications(prev => prev.map(a => a.id === appId ? { ...a, current_stage: newStage } : a));
      toast.success(`${lang === 'de' ? 'Verschoben' : 'Moved'}: ${getStageLabel(newStage, lang)}`);
    } catch {
      toast.error(lang === 'de' ? 'Verschiebung fehlgeschlagen' : 'Move failed');
    }
  };

  const onDragEnd = (result) => {
    const { draggableId, destination, source } = result;
    if (!destination || destination.droppableId === source.droppableId) return;
    moveApplication(draggableId, destination.droppableId);
  };

  const clearStageFilter = () => { setFilterStage(''); setSearchParams({}); };

  const filtered = useMemo(() => {
    return applications.filter(a => {
      if (filterCourse && a.course_type !== filterCourse) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const name = (a.applicant?.full_name || '').toLowerCase();
        const email = (a.applicant?.email || '').toLowerCase();
        const country = (a.degree_country || '').toLowerCase();
        const course = (a.course_type || '').toLowerCase();
        const phone = (a.applicant?.phone || '').toLowerCase();
        const appNum = (a.applicant_number || '').toLowerCase();
        if (!name.includes(q) && !email.includes(q) && !country.includes(q) && !course.includes(q) && !phone.includes(q) && !appNum.includes(q)) return false;
      }
      return true;
    });
  }, [applications, filterCourse, searchQuery]);

  const pipeline = filterStage
    ? filtered.filter(a => a.current_stage === filterStage)
    : filtered.filter(a => !ARCHIVED_STAGES.includes(a.current_stage));
  const archived = filterStage ? [] : filtered.filter(a => ARCHIVED_STAGES.includes(a.current_stage));
  const activePipelineStages = filterStage ? [filterStage] : PIPELINE_STAGES;
  const appsByStage = activePipelineStages.reduce((acc, stage) => {
    acc[stage] = pipeline.filter(a => a.current_stage === stage);
    return acc;
  }, {});

  if (loading) return <div className="w2g-loading"><div className="w2g-spinner" /><p className="w2g-loading-text">Wird geladen...</p></div>;

  return (
    <PageScaffold
      title={lang === 'de' ? 'Kanban Board' : 'Kanban Board'}
      subtitle={`${pipeline.length} ${lang === 'de' ? 'aktiv' : 'active'} von ${applications.length} ${lang === 'de' ? 'gesamt' : 'total'}${archived.length > 0 ? ` · ${archived.length} ${lang === 'de' ? 'archiviert' : 'archived'}` : ''}`}
      testId="kanban-page"
      actions={
        <button onClick={load} className="w2g-btn-secondary text-xs" data-testid="kanban-refresh-btn">
          <RefreshCw size={14} /> Aktualisieren
        </button>
      }
      toolbar={
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72 shrink-0">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                placeholder="Name, E-Mail, Land, Kurs..."
                className="w2g-search pl-9 py-2 text-xs" data-testid="kanban-search" />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]"
                  data-testid="kanban-search-clear">
                  <XCircle size={14} />
                </button>
              )}
            </div>
          }
          filters={[
            <button key="all" onClick={() => setFilterCourse('')}
              className={!filterCourse ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}
              data-testid="kanban-filter-all">Alle</button>,
            ...COURSE_OPTIONS.map(c => (
              <button key={c} onClick={() => setFilterCourse(filterCourse === c ? '' : c)}
                className={filterCourse === c ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}
                data-testid={`kanban-filter-${c.toLowerCase().replace(/[\s/]/g, '-')}`}>
                {c}
              </button>
            )),
          ]}
        />
      }
    >

      {filterStage && (
        <div className="flex items-center justify-between bg-primary-muted border border-primary/20 rounded-md px-4 py-2.5" data-testid="kanban-stage-filter-banner">
          <span className="text-sm text-primary font-medium">{lang === 'de' ? 'Fokus' : 'Focus'}: {getStageLabel(filterStage, lang)} ({pipeline.length})</span>
          <button onClick={clearStageFilter} className="w2g-btn-secondary w2g-btn-sm flex items-center gap-1"><XCircle size={13} /> {lang === 'de' ? 'Alle Stufen' : 'All Stages'}</button>
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center gap-4 text-[10px] text-[var(--color-text-secondary)] px-4 py-2 bg-[var(--color-surface-elevated)]/80 rounded-md border border-[var(--color-divider-subtle)]" data-testid="kanban-legend">
        <span className="flex items-center gap-1.5 font-medium text-[var(--color-text-secondary)]">
          <span className="inline-flex p-0.5 rounded bg-primary-muted text-primary"><GripVertical size={10} /></span>
          {lang === 'de' ? 'Ziehen & Ablegen' : 'Drag & Drop'}
        </span>
        <span className="text-[var(--color-accent)]">|</span>
        <span className="flex items-center gap-1"><Brain size={10} className="text-primary" /> Anabin-Einstufung</span>
        <span className="flex items-center gap-1"><CheckCircle size={10} className="text-primary" /> Docs vollst.</span>
        <span className="flex items-center gap-1"><AlertTriangle size={10} className="text-[var(--color-warning)]" /> Risiko</span>
        <span className="flex items-center gap-1"><Receipt size={10} className="text-[var(--color-text-tertiary)]" /> Rechnung</span>
        <span className="flex items-center gap-1"><CalendarClock size={10} className="text-primary" /> Wiedervorlage</span>
      </div>

      {/* Kanban Board with DnD – optimiert fuer Bildschirmhoehe */}
      <DragDropContext onDragEnd={onDragEnd}>
        <div className="pb-2" data-testid="kanban-board" style={{ height: 'calc(100vh - 280px)', minHeight: '400px' }}>
          <div className="flex gap-2.5 h-full" style={{ minWidth: `${activePipelineStages.length * 200}px` }}>
            {activePipelineStages.map(stage => (
              <div key={stage} className="flex-1 min-w-[185px] max-w-[280px] flex flex-col h-full" data-testid={`kanban-col-${stage}`}>
                {/* Column Header */}
                <div className="flex items-center justify-between mb-2 px-1">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-[var(--radius-xs)] ${STAGE_COLORS[stage] || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-primary)]'}`}>
                    {getStageLabel(stage, lang)}
                  </span>
                  <span className="text-[10px] text-[var(--color-text-tertiary)] font-bold tabular-nums bg-[var(--color-surface-sunken)] w-5 h-5 flex items-center justify-center rounded-full">
                    {appsByStage[stage]?.length || 0}
                  </span>
                </div>

                {/* Droppable Column – scrollbar bei Ueberlauf */}
                <Droppable droppableId={stage}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`space-y-1.5 flex-1 overflow-y-auto p-1.5 rounded-[var(--radius-md)] transition-all duration-200 ${
                        snapshot.isDraggingOver
                          ? 'bg-primary/6 border-2 border-dashed border-primary/40 shadow-inner'
                          : 'bg-[var(--color-surface-elevated)] border-2 border-dashed border-transparent'
                      }`}
                      style={{ scrollbarWidth: 'thin' }}
                      data-testid={`kanban-drop-${stage}`}
                    >
                      {appsByStage[stage]?.map((app, index) => (
                        <Draggable key={app.id} draggableId={app.id} index={index}>
                          {(provided, snapshot) => (
                            <KanbanCard
                              app={app}
                              screening={screenings[app.id]}
                              tasks={tasksByApp[app.id]}
                              invoices={invoicesByApp[app.applicant_id || app.id]}
                              followups={followupsByApp[app.id]}
                              provided={provided}
                              isDragging={snapshot.isDragging}
                            />
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                      {(!appsByStage[stage] || appsByStage[stage].length === 0) && !snapshot.isDraggingOver && (
                        <div className="py-8 text-center">
                          <Users size={16} className="text-[var(--color-accent)] mx-auto mb-1" />
                          <p className="text-[9px] text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Hierher ziehen' : 'Drag here'}</p>
                        </div>
                      )}
                    </div>
                  )}
                </Droppable>
              </div>
            ))}
          </div>
        </div>
      </DragDropContext>

      <ArchivedSection apps={archived} lang={lang} />
    </PageScaffold>
  );
}
