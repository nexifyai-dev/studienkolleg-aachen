import React, { useEffect, useState } from 'react';
import apiClient from '../../lib/apiClient';
import {
  Users, FileText, CheckSquare, TrendingUp, Clock,
  ArrowRight, AlertCircle, ChevronRight, RefreshCw,
  MessageSquare, Columns, CalendarClock, DownloadCloud
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { STAGE_LABELS, STAGE_COLORS } from '../../lib/utils';

function StatCard({ label, value, icon: Icon, color, link, testId }) {
  const inner = (
    <div className="bg-white border border-slate-200 rounded-sm p-4 hover:border-primary/30 transition-colors group" data-testid={testId}>
      <div className="flex items-center justify-between mb-2">
        <div className={`w-9 h-9 rounded-sm flex items-center justify-center ${color}`}>
          <Icon size={18} />
        </div>
        {link && <ChevronRight size={14} className="text-slate-300 group-hover:text-primary transition-colors" />}
      </div>
      <p className="text-2xl font-heading font-bold text-slate-800">{value}</p>
      <p className="text-slate-500 text-xs mt-0.5">{label}</p>
    </div>
  );
  return link ? <Link to={link} data-testid={`${testId}-link`}>{inner}</Link> : inner;
}

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const now = new Date();
  const d = new Date(dateStr);
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return 'gerade eben';
  if (diff < 3600) return `vor ${Math.floor(diff / 60)} Min.`;
  if (diff < 86400) return `vor ${Math.floor(diff / 3600)} Std.`;
  const days = Math.floor(diff / 86400);
  if (days === 1) return 'gestern';
  return `vor ${days} Tagen`;
}

export default function StaffDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [apps, setApps] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [followups, setFollowups] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [statsRes, appsRes, tasksRes, followupsRes] = await Promise.all([
          apiClient.get('/api/dashboard/stats'),
          apiClient.get('/api/applications'),
          apiClient.get('/api/tasks'),
          apiClient.get('/api/followups/due').catch(() => ({ data: [] })),
        ]);
        setStats(statsRes.data);
        setApps(appsRes.data || []);
        setTasks(tasksRes.data || []);
        setFollowups(followupsRes.data || []);
      } catch {}
      finally { setLoading(false); }
    };
    load();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
  );

  const pendingDocs = apps.filter(a => a.current_stage === 'pending_docs');
  const newLeads = apps.filter(a => a.current_stage === 'lead_new');
  const inReview = apps.filter(a => a.current_stage === 'in_review');
  const openTasks = tasks.filter(t => t.status === 'open' || t.status === 'in_progress');
  const recentApps = [...apps].sort((a, b) =>
    new Date(b.last_activity_at || b.created_at) - new Date(a.last_activity_at || a.created_at)
  ).slice(0, 8);

  return (
    <div className="space-y-5 animate-fade-in" data-testid="staff-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-heading font-bold text-primary">Dashboard</h1>
          <p className="text-slate-500 text-sm">Willkommen, {user?.full_name || user?.email}</p>
        </div>
        <a href={`${process.env.REACT_APP_BACKEND_URL}/api/export/applications`}
          data-testid="export-btn"
          className="flex items-center gap-1.5 text-xs font-medium border border-slate-200 text-slate-600 px-3 py-2 rounded-sm hover:bg-slate-50 hover:border-primary/30 transition-colors">
          <DownloadCloud size={14} /> CSV-Export
        </a>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard label="Neue Anfragen" value={newLeads.length} icon={TrendingUp}
          color="text-primary bg-primary/8" link="/staff/kanban?stage=lead_new"
          testId="stat-new-leads" />
        <StatCard label="In Bearbeitung" value={inReview.length} icon={RefreshCw}
          color="text-primary bg-primary/10" link="/staff/kanban?stage=in_review"
          testId="stat-in-review" />
        <StatCard label="Docs ausstehend" value={pendingDocs.length} icon={FileText}
          color="text-primary bg-primary/10" link="/staff/kanban?stage=pending_docs"
          testId="stat-pending-docs" />
        <StatCard label="Gesamt Bewerber" value={apps.length} icon={Users}
          color="text-slate-600 bg-slate-100" link="/staff/kanban"
          testId="stat-total" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Recent Applications */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-sm overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-semibold text-slate-800 text-sm">Zuletzt bearbeitet</h3>
            <Link to="/staff/kanban" className="text-xs text-primary hover:underline flex items-center gap-1">
              Alle ansehen <ArrowRight size={12} />
            </Link>
          </div>
          {recentApps.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">Keine Bewerbungen</div>
          ) : (
            <div className="divide-y divide-slate-50">
              {recentApps.map(app => (
                <Link key={app.id} to={`/staff/applications/${app.id}`}
                  data-testid={`dash-app-${app.id}`}
                  className="flex items-center justify-between px-4 py-3 hover:bg-slate-50 transition-colors group">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 bg-primary/8 rounded-sm flex items-center justify-center shrink-0">
                      <span className="text-xs font-bold text-primary">
                        {(app.applicant?.full_name || '?')[0].toUpperCase()}
                      </span>
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-800 truncate">
                        {app.applicant?.full_name || app.applicant?.email || 'Unbekannt'}
                      </p>
                      <p className="text-xs text-slate-400 truncate">
                        {app.applicant?.email || ''} {app.applicant?.country ? `· ${app.applicant.country}` : ''}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className={`text-[11px] font-medium px-2 py-0.5 rounded-sm whitespace-nowrap ${STAGE_COLORS[app.current_stage] || 'bg-slate-100 text-slate-600'}`}>
                      {STAGE_LABELS[app.current_stage] || app.current_stage}
                    </span>
                    <span className="text-[10px] text-slate-300 hidden sm:block whitespace-nowrap">
                      {timeAgo(app.last_activity_at || app.created_at)}
                    </span>
                    <ChevronRight size={14} className="text-slate-300 group-hover:text-primary" />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Right Sidebar */}
        <div className="space-y-3">
          {/* Handlungsbedarf */}
          {(pendingDocs.length > 0 || newLeads.length > 0) && (
            <div className="bg-white border border-slate-200 rounded-sm p-4" data-testid="action-needed-panel">
              <h3 className="font-semibold text-slate-800 text-sm mb-3 flex items-center gap-2">
                <AlertCircle size={14} className="text-primary" /> Handlungsbedarf
              </h3>
              <div className="space-y-2">
                {newLeads.length > 0 && (
                  <Link to="/staff/kanban?stage=lead_new" data-testid="action-new-leads"
                    className="flex items-center justify-between px-3 py-2 bg-primary/5 border border-primary/15 rounded-sm text-sm hover:bg-primary/10 transition-colors">
                    <span className="text-slate-700">{newLeads.length} neue Anfrage{newLeads.length !== 1 ? 'n' : ''}</span>
                    <ArrowRight size={14} className="text-primary" />
                  </Link>
                )}
                {pendingDocs.length > 0 && (
                  <Link to="/staff/kanban?stage=pending_docs" data-testid="action-pending-docs"
                    className="flex items-center justify-between px-3 py-2 bg-primary/5 border border-primary/15 rounded-sm text-sm hover:bg-primary/10 transition-colors">
                    <span className="text-slate-700">{pendingDocs.length} Docs ausstehend</span>
                    <ArrowRight size={14} className="text-primary" />
                  </Link>
                )}
              </div>
            </div>
          )}

          {/* Schnellzugriff */}
          <div className="bg-white border border-slate-200 rounded-sm p-4" data-testid="quick-access-panel">
            <h3 className="font-semibold text-slate-800 text-sm mb-3">Schnellzugriff</h3>
            <div className="space-y-1.5">
              {[
                { to: '/staff/kanban', label: 'Kanban Board', icon: Columns },
                { to: '/staff/tasks', label: 'Aufgaben', icon: CheckSquare },
                { to: '/staff/messaging', label: 'Nachrichten', icon: MessageSquare },
              ].map(item => (
                <Link key={item.to} to={item.to}
                  data-testid={`quick-${item.to.split('/').pop()}`}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-sm text-sm text-slate-600 hover:bg-slate-50 hover:text-primary transition-colors">
                  <item.icon size={14} />
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Offene Aufgaben */}
          {openTasks.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-sm p-4" data-testid="open-tasks-panel">
              <h3 className="font-semibold text-slate-800 text-sm mb-3 flex items-center gap-2">
                <CheckSquare size={14} className="text-primary" /> Offene Aufgaben ({openTasks.length})
              </h3>
              <div className="space-y-1.5">
                {openTasks.slice(0, 5).map(t => (
                  <Link key={t.id} to="/staff/tasks" data-testid={`open-task-${t.id}`}
                    className="flex items-center justify-between px-2 py-1.5 rounded-sm text-xs hover:bg-slate-50 transition-colors">
                    <span className="text-slate-700 truncate">{t.title}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${
                      t.priority === 'high' ? 'border-red-200 text-red-600 bg-red-50' : 'border-slate-200 text-slate-500'
                    }`}>{t.priority === 'high' ? 'Hoch' : t.priority}</span>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Systemstatus */}
          <div className="bg-white border border-slate-200 rounded-sm p-4" data-testid="system-status-panel">
            <h3 className="font-semibold text-slate-800 text-sm mb-3 flex items-center gap-2">
              <Clock size={14} className="text-slate-400" /> Systemstatus
            </h3>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-slate-500">Offene Aufgaben</dt>
                <dd className="font-medium text-slate-800">{stats?.open_tasks ?? openTasks.length}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Offene Docs</dt>
                <dd className="font-medium text-slate-800">{stats?.pending_documents ?? pendingDocs.length}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Gesamt Leads</dt>
                <dd className="font-medium text-slate-800">{stats?.total_leads ?? apps.length}</dd>
              </div>
            </dl>
          </div>

          {/* Wiedervorlagen */}
          {followups.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-sm p-4" data-testid="followups-panel">
              <h3 className="font-semibold text-slate-800 text-sm mb-3 flex items-center gap-2">
                <CalendarClock size={14} className="text-primary" /> Wiedervorlagen ({followups.length})
              </h3>
              <div className="space-y-2">
                {followups.slice(0, 5).map(f => (
                  <Link key={f.id} to={`/staff/applications/${f.application_id}`}
                    data-testid={`followup-${f.id}`}
                    className="flex items-center justify-between px-2 py-2 rounded-sm text-xs hover:bg-primary/5 transition-colors border border-slate-100">
                    <div className="min-w-0">
                      <p className="font-medium text-slate-700 truncate">{f.applicant_name || 'Bewerber'}</p>
                      <p className="text-slate-500 truncate">{f.reason}</p>
                    </div>
                    <span className="text-[10px] text-primary whitespace-nowrap ml-2">{f.due_date}</span>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
