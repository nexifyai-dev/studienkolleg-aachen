import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Users, FileText, CheckSquare, TrendingUp, ArrowRight,
  AlertTriangle, Search, XCircle, BarChart3, Activity, Zap,
  Euro, ChevronRight, MessageSquare,
  Columns, Eye, Loader2
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { useAuth } from '../../contexts/AuthContext';
import { STAGE_LABELS, formatCurrency } from '../../lib/utils';
import { useDashboardStats, useApplications, useTasks, useInvoices } from '../../lib/api-hooks';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api-hooks';

/* Layout */
import { PageScaffold } from '../../components/layout/PageScaffold';
import { InfoCard, StatusLine } from '../../components/layout/BackstageComponents';

/* shadcn-Komponenten */
import { Card, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Avatar, AvatarFallback } from '../../components/ui/avatar';

/* ──────────────────────────────────────────────────────────────
   DESIGN-TOKENS (abgeleitet aus CI)
   ────────────────────────────────────────────────────────────── */
const CHART_PALETTE = [
  '#113655', '#D4AF37', '#2196F3', '#4CAF50', '#FF9800', '#E91E63', '#9E9E9E'
];

/* ──────────────────────────────────────────────────────────────
   HILFSFUNKTIONEN
   ────────────────────────────────────────────────────────────── */
function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (diff < 60) return 'gerade eben';
  if (diff < 3600) return `vor ${Math.floor(diff / 60)} Min.`;
  if (diff < 86400) return `vor ${Math.floor(diff / 3600)} Std.`;
  const d = Math.floor(diff / 86400);
  return d === 1 ? 'gestern' : `vor ${d} Tagen`;
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-divider)] shadow-lg px-3 py-2 rounded-[var(--radius-sm)]">
      <p className="text-[10px] font-bold text-[var(--color-text-primary)]">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-[10px] text-[var(--color-text-secondary)]">{p.name}: <strong className="tabular-nums">{p.value}</strong></p>
      ))}
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────
   KPI-KARTE (shadcn Card + Badge)
   ────────────────────────────────────────────────────────────── */
function KpiCard({ label, value, icon: Icon, link, sub, testId }) {
  return (
    <Link to={link} className="group" data-testid={`${testId}-link`}>
      <Card className="relative hover:shadow-[var(--shadow-e2)] transition-shadow duration-200 border-l-[3px] border-l-[var(--color-primary)]" data-testid={testId}>
        <CardContent className="px-4 py-4">
          <div className="flex items-start justify-between mb-3">
            <div className="w-9 h-9 rounded-[var(--radius-sm)] flex items-center justify-center bg-[var(--color-primary-muted)]">
              <Icon size={16} className="text-[var(--color-primary)]" />
            </div>
            <ChevronRight size={14} className="text-[var(--color-text-tertiary)] opacity-0 group-hover:opacity-100 transition-opacity mt-1" />
          </div>
          <p className="text-2xl font-extrabold text-[var(--color-text-primary)] tabular-nums leading-none mb-1" style={{ fontFamily: 'var(--font-heading)' }}>
            {value}
          </p>
          <p className="text-[11px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">{label}</p>
          {sub && <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1">{sub}</p>}
        </CardContent>
      </Card>
    </Link>
  );
}

/* ──────────────────────────────────────────────────────────────
   HAUPT-DASHBOARD
   ────────────────────────────────────────────────────────────── */
export default function StaffDashboard() {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');

  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: apps = [], isLoading: appsLoading } = useApplications();
  const { data: tasks = [], isLoading: tasksLoading } = useTasks();
  const { data: invoices = [], isLoading: invoicesLoading } = useInvoices();
  useQuery({
    queryKey: ['followups', 'due'],
    queryFn: () => api.get('/followups/due').then(r => r.data).catch(() => []),
  });

  const loading = statsLoading || appsLoading || tasksLoading || invoicesLoading;

  /* ── Berechnete KPIs ───────────────────────────────────── */
  const kpis = useMemo(() => {
    const pendingDocs = apps.filter(a => a.current_stage === 'pending_docs' || a.current_stage === 'documents_requested');
    const newLeads = apps.filter(a => a.current_stage === 'lead_new');
    const inReview = apps.filter(a => a.current_stage === 'in_review');
    const enrolled = apps.filter(a => a.current_stage === 'enrolled');
    const openTasks = tasks.filter(t => t.status === 'open' || t.status === 'in_progress');
    const myTasks = openTasks.filter(t => t.assigned_to === user?.id);
    const highPrio = openTasks.filter(t => t.priority === 'high');
    const overdueInv = invoices.filter(i => i.status === 'overdue');
    const unpaidInv = invoices.filter(i => i.status === 'sent');
    const paidInv = invoices.filter(i => i.status === 'paid');
    const totalRev = paidInv.reduce((s, i) => s + (i.total_amount || i.amount || 0), 0);
    const openRev = [...unpaidInv, ...overdueInv].reduce((s, i) => s + (i.total_amount || i.amount || 0), 0);
    const convRate = apps.length > 0 ? Math.round((enrolled.length / apps.length) * 100) : 0;
    return { pendingDocs, newLeads, inReview, enrolled, openTasks, myTasks, highPrio, overdueInv, unpaidInv, paidInv, totalRev, openRev, convRate };
  }, [apps, tasks, invoices, user]);

  /* ── Pipeline-Daten ────────────────────────────────────── */
  const pipelineData = useMemo(() => {
    const pipeline = stats?.pipeline || {};
    const stages = ['lead_new', 'in_review', 'pending_docs', 'interview_scheduled', 'conditional_offer', 'offer_sent', 'enrolled'];
    return stages.map(s => ({
      name: (STAGE_LABELS[s] || s).substring(0, 14),
      count: pipeline[s] || apps.filter(a => a.current_stage === s).length,
    }));
  }, [stats, apps]);

  /* ── Kurs-Verteilung ───────────────────────────────────── */
  const courseData = useMemo(() => {
    const m = {};
    apps.forEach(a => { const c = a.course_type || 'Sonstige'; m[c] = (m[c] || 0) + 1; });
    return Object.entries(m).map(([name, value]) => ({ name, value }));
  }, [apps]);

  /* ── Rechnungs-Status ──────────────────────────────────── */
  const invoiceData = useMemo(() => {
    const m = {};
    m[t('staff.invoices.paid', 'Bezahlt')] = 0;
    m[t('staff.invoices.sent', 'Offen')] = 0;
    m[t('staff.invoices.overdue', 'Ueberfaellig')] = 0;
    m[t('staff.invoices.draft', 'Entwurf')] = 0;
    invoices.forEach(i => {
      if (i.status === 'paid') m[t('staff.invoices.paid', 'Bezahlt')]++;
      else if (i.status === 'overdue') m[t('staff.invoices.overdue', 'Ueberfaellig')]++;
      else if (i.status === 'draft') m[t('staff.invoices.draft', 'Entwurf')]++;
      else m[t('staff.invoices.sent', 'Offen')]++;
    });
    return Object.entries(m).filter(([, v]) => v > 0).map(([name, value]) => ({ name, value }));
  }, [invoices, t]);

  /* ── Letzte Faelle ─────────────────────────────────────── */
  const recentApps = useMemo(() => {
    const sorted = [...apps].sort((a, b) => new Date(b.last_activity_at || b.created_at) - new Date(a.last_activity_at || a.created_at));
    if (!searchQuery) return sorted.slice(0, 8);
    const q = searchQuery.toLowerCase();
    return sorted.filter(a =>
      (a.applicant?.full_name || '').toLowerCase().includes(q) ||
      (a.applicant?.email || '').toLowerCase().includes(q) ||
      (a.applicant?.country || a.degree_country || '').toLowerCase().includes(q)
    ).slice(0, 8);
  }, [apps, searchQuery]);

  const pipelineTotal = pipelineData.reduce((s, d) => s + d.count, 0);

  /* ── LOADING STATE ─────────────────────────────────────── */
  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]" data-testid="staff-dashboard-loading">
      <div className="text-center space-y-3">
        <Loader2 size={32} className="animate-spin text-[var(--color-primary)] mx-auto" />
        <p className="text-sm font-medium text-[var(--color-text-secondary)]">{t('common.loading', 'Dashboard wird geladen...')}</p>
      </div>
    </div>
  );

  /* ── RENDER ────────────────────────────────────────────── */
  return (
    <PageScaffold
      title={t('staff.dashboard.title', 'Dashboard')}
      subtitle={`${user?.full_name || user?.email} | ${new Date().toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long' })}`}
      testId="staff-dashboard"
      actions={
        (kpis.highPrio.length > 0 || kpis.overdueInv.length > 0) ? (
          <div className="flex items-center gap-3" data-testid="urgent-banner">
            <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center shrink-0">
              <AlertTriangle size={14} className="text-[var(--color-primary)]" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-[var(--color-danger)] leading-tight" style={{ fontFamily: 'var(--font-heading)' }}>{t('staff.dashboard.action_needed', 'Sofortiger Handlungsbedarf')}</p>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {kpis.highPrio.length > 0 && (
                  <Link to="/staff/tasks" data-testid="urgent-tasks-link">
                    <Badge variant="danger" size="xs"><Zap size={9} />{kpis.highPrio.length} {t('staff.tasks.urgent', 'dringend')}</Badge>
                  </Link>
                )}
                {kpis.overdueInv.length > 0 && (
                  <Link to="/staff/invoices" data-testid="urgent-invoices-link">
                    <Badge variant="danger" size="xs"><Euro size={10} />{kpis.overdueInv.length} {t('staff.invoices.overdue', 'ueberfaellig')}</Badge>
                  </Link>
                )}
              </div>
            </div>
          </div>
        ) : null
      }
    >

      {/* ═══ KPI-ZONE: 6 Karten ═══════════════════════════ */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4" data-testid="kpi-zone">
        <KpiCard label={t('staff.dashboard.new_applications', 'Neue Anfragen')} value={kpis.newLeads.length} icon={TrendingUp} link="/staff/kanban?stage=lead_new" testId="stat-new-leads" />
        <KpiCard label={t('staff.dashboard.overview', 'In Bearbeitung')} value={kpis.inReview.length} icon={Activity} link="/staff/kanban?stage=in_review" testId="stat-in-review" />
        <KpiCard label={t('staff.dashboard.pending_docs', 'Docs ausstehend')} value={kpis.pendingDocs.length} icon={FileText} link="/staff/documents" testId="stat-pending-docs" sub={kpis.pendingDocs.length > 0 ? t('staff.documents.needs_review', 'Pruefung noetig') : null} />
        <KpiCard label={t('staff.dashboard.open_tasks', 'Meine Aufgaben')} value={kpis.myTasks.length} icon={CheckSquare} link="/staff/tasks" testId="stat-my-tasks" sub={kpis.highPrio.length > 0 ? `${kpis.highPrio.length} ${t('staff.tasks.urgent', 'dringend')}` : null} />
        <KpiCard label={t('staff.dashboard.total_applicants', 'Eingeschrieben')} value={kpis.enrolled.length} icon={Users} link="/staff/kanban?stage=enrolled" testId="stat-enrolled" />
        <KpiCard label={t('staff.dashboard.revenue', 'Umsatz')} value={formatCurrency(kpis.totalRev)} icon={Euro} link="/staff/invoices" testId="stat-revenue" sub={kpis.openRev > 0 ? `${formatCurrency(kpis.openRev)} ${t('staff.dashboard.outstanding', 'offen')}` : null} />
      </div>

      {/* ═══ CONVERSION + PIPELINE PROGRESS ════════════════ */}
      <Card data-testid="conversion-bar">
        <CardContent className="px-5 py-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--color-text-tertiary)]">{t('staff.dashboard.overview', 'Pipeline-Fortschritt')}</p>
              <p className="text-lg font-extrabold text-[var(--color-text-primary)] tabular-nums mt-0.5" style={{ fontFamily: 'var(--font-heading)' }}>{pipelineTotal} {t('staff.dashboard.total_applicants', 'Bewerber')}</p>
            </div>
            <Badge variant="gold" size="sm">{kpis.convRate}% Conversion</Badge>
          </div>
          <div className="flex items-center gap-1 h-3">
            {pipelineData.map((d, i) => (
              <div key={i} className="h-full transition-all duration-500 hover:brightness-110"
                style={{
                  width: `${pipelineTotal > 0 ? (d.count / pipelineTotal) * 100 : 14}%`,
                  minWidth: d.count > 0 ? '12px' : '4px',
                  backgroundColor: CHART_PALETTE[i % CHART_PALETTE.length],
                  borderRadius: i === 0 ? 'var(--radius-full) 0 0 var(--radius-full)' : i === pipelineData.length - 1 ? '0 var(--radius-full) var(--radius-full) 0' : '0',
                  opacity: d.count > 0 ? 1 : 0.2,
                }}
                title={`${STAGE_LABELS[['lead_new', 'in_review', 'pending_docs', 'interview_scheduled', 'conditional_offer', 'offer_sent', 'enrolled'][i]] || ''}: ${d.count}`}
              />
            ))}
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3">
            {pipelineData.map((d, i) => (
              <div key={i} className="flex items-center gap-1.5 text-[10px]">
                <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: CHART_PALETTE[i % CHART_PALETTE.length] }} />
                <span className="text-[var(--color-text-tertiary)]">{d.name}</span>
                <span className="font-bold text-[var(--color-text-primary)] tabular-nums">{d.count}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ═══ HAUPTZONE: 3-Spalten ═════════════════════════ */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-5">

        {/* Spalte 1 (5): Letzte Faelle */}
        <div className="md:col-span-5">
          <InfoCard
            title={t('staff.dashboard.recent_activity', 'Letzte Faelle')}
            icon={Activity}
            headerAction={<Link to="/staff/cases" className="w2g-btn-table-action" data-testid="staff-all-apps-link">{t('staff.dashboard.view_all', 'Alle')} <ArrowRight size={10} /></Link>}
            deepLinkText={t('staff.dashboard.view_all', 'Alle Faelle anzeigen')}
            deepLinkHref="/staff/cases"
            noPadding
            className="h-full"
            testId="recent-cases-panel"
          >
            <div className="px-5 pt-3 pb-0">
              <div className="relative mb-3">
                <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
                <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder="Name, E-Mail, Land..." data-testid="dashboard-app-search"
                  className="w-full h-8 pl-8 pr-8 text-[11px] bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] rounded-[var(--radius-sm)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-tertiary)] focus:outline-none focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)]/20 transition-all" />
                {searchQuery && (
                  <button onClick={() => setSearchQuery('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]" data-testid="dashboard-search-clear"><XCircle size={12} /></button>
                )}
              </div>
            </div>
            <div className="divide-y divide-[var(--color-divider-subtle)]">
              {recentApps.length === 0 ? (
                <div className="py-12 text-center px-5">
                  <Search size={20} className="mx-auto mb-2 text-[var(--color-text-tertiary)]" />
                  <p className="text-xs font-medium text-[var(--color-text-secondary)]">{searchQuery ? t('common.no_data', 'Keine Treffer') : t('staff.cases.no_cases', 'Keine Bewerbungen')}</p>
                </div>
              ) : recentApps.map(app => (
                <Link key={app.id} to={`/staff/applications/${app.id}`} className="flex items-center gap-3 px-5 py-2.5 hover:bg-[var(--color-surface-elevated)] transition-colors group" data-testid={`dash-app-${app.id}`}>
                  <Avatar className="w-8 h-8">
                    <AvatarFallback>{(app.applicant?.full_name || '?')[0].toUpperCase()}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-[var(--color-text-primary)] truncate group-hover:text-[var(--color-primary)] transition-colors">{app.applicant?.full_name || 'Unbekannt'}</p>
                    <p className="text-[10px] text-[var(--color-text-tertiary)] truncate">{app.applicant?.email}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Badge variant={app.current_stage === 'enrolled' ? 'success' : app.current_stage === 'lead_new' ? 'gold' : 'info'} size="xs">
                      {STAGE_LABELS[app.current_stage] || app.current_stage}
                    </Badge>
                    <span className="text-[9px] text-[var(--color-text-tertiary)] tabular-nums hidden lg:block">{timeAgo(app.last_activity_at || app.created_at)}</span>
                  </div>
                </Link>
              ))}
            </div>
          </InfoCard>
        </div>

        {/* Spalte 2 (4): Charts */}
        <div className="md:col-span-4 space-y-5">
          {/* Pipeline Bar Chart */}
          <InfoCard
            title="Pipeline"
            icon={BarChart3}
            headerAction={<Link to="/staff/kanban" className="w2g-btn-table-secondary" data-testid="pipeline-kanban-link">Kanban <ArrowRight size={10} /></Link>}
            testId="pipeline-chart-panel"
          >
            <div style={{ height: '210px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={pipelineData} barSize={18}>
                  <XAxis dataKey="name" tick={{ fontSize: 9, fill: 'var(--color-text-tertiary)' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 9, fill: 'var(--color-text-tertiary)' }} axisLine={false} tickLine={false} width={22} allowDecimals={false} />
                  <Tooltip content={<ChartTooltip />} />
                  <Bar dataKey="count" name={t('staff.dashboard.total_applicants', 'Bewerber')} radius={[3, 3, 0, 0]}>
                    {pipelineData.map((_, i) => <Cell key={i} fill={CHART_PALETTE[i % CHART_PALETTE.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </InfoCard>

          {/* Donut-Charts: Kurse + Rechnungen */}
          <div className="grid grid-cols-2 gap-4">
            {courseData.length > 0 && (
              <Card data-testid="course-distribution-panel">
                <CardContent className="px-4 pt-4 pb-3">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--color-text-tertiary)] mb-2">Kurse</p>
                  <div style={{ height: '100px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={courseData} cx="50%" cy="50%" innerRadius={22} outerRadius={40} dataKey="value" stroke="none">
                          {courseData.map((_, i) => <Cell key={i} fill={CHART_PALETTE[i % CHART_PALETTE.length]} />)}
                        </Pie>
                        <Tooltip content={<ChartTooltip />} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="space-y-0.5 mt-2">
                    {courseData.slice(0, 4).map((d, i) => (
                      <div key={d.name} className="flex items-center gap-1.5 text-[9px]">
                        <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: CHART_PALETTE[i % CHART_PALETTE.length] }} />
                        <span className="text-[var(--color-text-tertiary)] truncate flex-1">{d.name}</span>
                        <span className="font-bold text-[var(--color-text-primary)] tabular-nums">{d.value}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
            {invoiceData.length > 0 && (
              <Card data-testid="invoice-distribution-panel">
                <CardContent className="px-4 pt-4 pb-3">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--color-text-tertiary)] mb-2">Rechnungen</p>
                  <div style={{ height: '100px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={invoiceData} cx="50%" cy="50%" innerRadius={22} outerRadius={40} dataKey="value" stroke="none">
                          {invoiceData.map((_, i) => {
                            const c = ['#4CAF50', '#FF9800', '#E91E63', '#9E9E9E'];
                            return <Cell key={i} fill={c[i % c.length]} />;
                          })}
                        </Pie>
                        <Tooltip content={<ChartTooltip />} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="space-y-0.5 mt-2">
                    {invoiceData.map((d, i) => {
                      const c = ['#4CAF50', '#FF9800', '#E91E63', '#9E9E9E'];
                      return (
                        <div key={d.name} className="flex items-center gap-1.5 text-[9px]">
                          <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: c[i % c.length] }} />
                          <span className="text-[var(--color-text-tertiary)] truncate flex-1">{d.name}</span>
                          <span className="font-bold text-[var(--color-text-primary)] tabular-nums">{d.value}</span>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Spalte 3 (3): Schnellzugriff + Aufgaben + Finanzen */}
        <div className="md:col-span-3 space-y-4">

          {/* Schnellzugriff */}
          <InfoCard title="Schnellzugriff" noPadding testId="quick-access-panel">
            <div className="px-4 pb-3 pt-1">
              <div className="space-y-0.5">
                {[
                  { to: '/staff/kanban', label: 'Kanban Board', icon: Columns },
                  { to: '/staff/cases', label: 'Fallliste', icon: Users },
                  { to: '/staff/tasks', label: 'Aufgaben', icon: CheckSquare, n: kpis.myTasks.length },
                  { to: '/staff/documents', label: 'Dokumente', icon: Eye },
                  { to: '/staff/invoices', label: 'Rechnungen', icon: FileText, n: kpis.overdueInv.length },
                  { to: '/staff/messaging', label: 'Nachrichten', icon: MessageSquare, n: stats?.unread_messages },
                  { to: '/staff/reporting', label: 'Reporting', icon: BarChart3 },
                ].map(item => (
                  <Link key={item.to} to={item.to} data-testid={`quick-${item.to.split('/').pop()}`}
                    className="flex items-center gap-2.5 px-2.5 py-2 text-xs text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-elevated)] hover:text-[var(--color-primary)] rounded-[var(--radius-xs)] transition-all">
                    <item.icon size={14} />
                    <span className="flex-1 font-medium">{item.label}</span>
                    {item.n > 0 && (
                      <Badge variant="gold" size="xs">{item.n}</Badge>
                    )}
                  </Link>
                ))}
              </div>
            </div>
          </InfoCard>

          {/* Offene Aufgaben */}
          {kpis.openTasks.length > 0 && (
            <InfoCard
              title="Aufgaben"
              headerAction={<Badge variant="outline" size="xs">{kpis.openTasks.length} offen</Badge>}
              deepLinkText="Alle anzeigen"
              deepLinkHref="/staff/tasks"
              noPadding
              testId="open-tasks-panel"
            >
              <div className="px-4 pb-3 pt-1 space-y-1">
                  {kpis.openTasks.slice(0, 5).map(t => (
                    <Link key={t.id} to="/staff/tasks" data-testid={`open-task-${t.id}`}
                      className="flex items-center justify-between px-2 py-1.5 text-[11px] hover:bg-[var(--color-surface-elevated)] rounded-[var(--radius-xs)] transition-colors">
                      <span className="text-[var(--color-text-primary)] truncate font-medium flex-1 mr-2">{t.title}</span>
                      <Badge variant={t.priority === 'high' ? 'danger' : 'muted'} size="xs">{t.priority === 'high' ? 'Hoch' : t.priority}</Badge>
                    </Link>
                  ))}
              </div>
            </InfoCard>
          )}

          {/* Finanzen */}
          <InfoCard title="Finanzen" icon={Euro} testId="finance-panel">
              <div className="space-y-2">
                {kpis.overdueInv.length > 0 && (
                  <Link to="/staff/invoices" className="flex items-center justify-between px-3 py-2.5 bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)] rounded-[var(--radius-sm)] hover:brightness-95 transition-all">
                    <span className="text-[10px] font-semibold text-[var(--color-danger)]">Ueberfaellig</span>
                    <span className="text-xs font-extrabold text-[var(--color-danger)] tabular-nums">{kpis.overdueInv.length}</span>
                  </Link>
                )}
                {kpis.unpaidInv.length > 0 && (
                  <Link to="/staff/invoices" className="flex items-center justify-between px-3 py-2.5 bg-[var(--color-warning-bg)] border border-[var(--color-warning-border)] rounded-[var(--radius-sm)] hover:brightness-95 transition-all">
                    <span className="text-[10px] font-semibold text-[var(--color-warning)]">Offen</span>
                    <span className="text-xs font-extrabold text-[var(--color-warning)] tabular-nums">{kpis.unpaidInv.length}</span>
                  </Link>
                )}
                {kpis.totalRev > 0 && (
                  <div className="flex items-center justify-between px-3 py-2.5 bg-[var(--color-success-bg)] border border-[var(--color-success-border)] rounded-[var(--radius-sm)]">
                    <span className="text-[10px] font-semibold text-[var(--color-success)]">Bezahlt</span>
                    <span className="text-xs font-extrabold text-[var(--color-success)] tabular-nums">{formatCurrency(kpis.totalRev)}</span>
                  </div>
                )}
              </div>
          </InfoCard>
        </div>
      </div>

      {/* Backstage StatusLine */}
      <StatusLine
        items={[
          { icon: Users, label: 'Bewerber', value: apps.length, color: 'var(--color-primary)' },
          { icon: CheckSquare, label: 'Offene Tasks', value: kpis.openTasks.length, color: kpis.highPrio.length > 0 ? 'var(--color-danger)' : undefined },
          { icon: Euro, label: 'Umsatz', value: formatCurrency(kpis.totalRev), color: 'var(--color-success)' },
          { icon: TrendingUp, label: 'Conversion', value: `${kpis.convRate}%`, color: 'var(--color-accent)' },
        ]}
        testId="dashboard-status-line"
      />
    </PageScaffold>
  );
}
