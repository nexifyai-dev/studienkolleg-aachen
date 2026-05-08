import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { Link } from 'react-router-dom';
import { getStageLabel, formatDate, getLang } from '../../lib/utils';
import {
  Users, Activity, CheckSquare, FileText, MessageSquare,
  BarChart3, Shield, UserPlus, ChevronRight,
  Clock, AlertCircle, RefreshCw, Loader2, Zap
} from 'lucide-react';

/* shadcn-Komponenten */
import { Card, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { InfoCard, StatusLine } from '../../components/layout/BackstageComponents';

/* ──────────────────────────────────────────────────────────────
   KPI-KARTE (shadcn Card + farbiger Seitenrand)
   ────────────────────────────────────────────────────────────── */
function KpiCard({ label, value, icon: Icon, link, testId }) {
  const content = (
    <Card className="relative hover:shadow-[var(--shadow-e2)] transition-shadow duration-200 border-l-[3px] border-l-[var(--color-primary)]" data-testid={testId}>
      <CardContent className="px-4 py-4">
        <div className="flex items-start justify-between mb-3">
          <div className="w-9 h-9 rounded-[var(--radius-sm)] flex items-center justify-center bg-[var(--color-primary-muted)]">
            <Icon size={16} className="text-[var(--color-primary)]" />
          </div>
          {link && <ChevronRight size={14} className="text-[var(--color-text-tertiary)] opacity-0 group-hover:opacity-100 transition-opacity mt-1" />}
        </div>
        <p className="text-2xl font-extrabold text-[var(--color-text-primary)] tabular-nums leading-none mb-1" style={{ fontFamily: 'var(--font-heading)' }}>
          {value ?? '\u2013'}
        </p>
        <p className="text-[11px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">{label}</p>
      </CardContent>
    </Card>
  );
  return link ? <Link to={link} className="group" data-testid={`${testId}-link`}>{content}</Link> : content;
}

/* ──────────────────────────────────────────────────────────────
   PIPELINE-UEBERSICHT (shadcn Card + Progress)
   ────────────────────────────────────────────────────────────── */
function PipelineBar({ pipeline }) {
  if (!pipeline) return null;
  const stages = [
    'lead_new', 'in_review', 'pending_docs', 'interview_scheduled',
    'conditional_offer', 'offer_sent', 'enrolled',
  ];
  const total = stages.reduce((s, k) => s + (pipeline[k] || 0), 0);
  if (total === 0) return null;

  return (
    <InfoCard
      title="Pipeline-Uebersicht"
      icon={BarChart3}
      headerAction={<Badge variant="gold" size="sm">{total} Bewerber</Badge>}
      testId="admin-pipeline"
    >
        <div className="space-y-2.5">
          {stages.map(stage => {
            const count = pipeline[stage] || 0;
            return (
              <Link key={stage} to={`/staff/kanban?stage=${stage}`}
                data-testid={`admin-pipeline-${stage}`}
                className="flex items-center gap-3 group hover:bg-[var(--color-surface-elevated)] rounded-[var(--radius-xs)] px-2 py-1.5 -mx-2 transition-colors">
                <span className="text-[11px] font-medium w-32 truncate text-[var(--color-text-secondary)]">
                  {getStageLabel(stage, 'de')}
                </span>
                <div className="flex-1">
                  <Progress value={count} max={total > 0 ? total : 1} variant="default" />
                </div>
                <span className="text-xs font-semibold text-[var(--color-text-primary)] w-8 text-right tabular-nums">{count}</span>
                <ChevronRight size={12} className="text-[var(--color-text-tertiary)] group-hover:text-[var(--color-primary)]" />
              </Link>
            );
          })}
        </div>
        <div className="flex items-center justify-between pt-3 border-t border-[var(--color-divider-subtle)] mt-3">
          <span className="text-xs text-[var(--color-text-secondary)]">Aktive Pipeline</span>
          <span className="text-sm font-bold text-[var(--color-primary)]" style={{ fontFamily: 'var(--font-heading)' }}>{total}</span>
        </div>
        {(pipeline['declined'] > 0 || pipeline['on_hold'] > 0) && (
          <div className="flex gap-4 text-[10px] text-[var(--color-text-tertiary)] pt-1">
            {pipeline['declined'] > 0 && <span>Abgelehnt: <strong>{pipeline['declined']}</strong></span>}
            {pipeline['on_hold'] > 0 && <span>Warteschleife: <strong>{pipeline['on_hold']}</strong></span>}
          </div>
        )}
    </InfoCard>
  );
}

/* ──────────────────────────────────────────────────────────────
   LETZTE AKTIVITAETEN (shadcn Card)
   ────────────────────────────────────────────────────────────── */
function RecentActivity({ activities }) {
  if (!activities || activities.length === 0) return null;
  const actionLabels = {
    user_created: 'Nutzer erstellt',
    user_updated: 'Nutzer aktualisiert',
    application_stage_changed: 'Status geaendert',
    document_uploaded: 'Dokument hochgeladen',
    document_reviewed: 'Dokument geprueft',
    invoice_created: 'Rechnung erstellt',
    task_created: 'Aufgabe erstellt',
    email_sent: 'E-Mail gesendet',
    login: 'Anmeldung',
  };

  return (
    <InfoCard
      title="Letzte Aktivitaeten"
      icon={Activity}
      headerAction={<Link to="/admin/audit" className="w2g-btn-table-secondary" data-testid="admin-audit-link">Alle anzeigen</Link>}
      deepLinkText="Alle Aktivitaeten"
      deepLinkHref="/admin/audit"
      noPadding
      testId="admin-recent-activity"
    >
      <div className="divide-y divide-[var(--color-divider-subtle)]">
        {activities.slice(0, 8).map((a, i) => (
          <div key={a.id || i} className="flex items-center gap-3 px-5 py-2.5" data-testid={`activity-${i}`}>
            <div className="w-7 h-7 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center shrink-0">
              <Clock size={11} className="text-[var(--color-primary)]" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs text-[var(--color-text-primary)] font-medium truncate">
                {actionLabels[a.action] || a.action}
              </p>
              <p className="text-[10px] text-[var(--color-text-tertiary)] truncate">
                {a.target_type && `${a.target_type}`}
                {a.actor_id && ` \u00B7 ${a.actor_id.slice(-6)}`}
              </p>
            </div>
            <span className="text-[10px] text-[var(--color-text-tertiary)] shrink-0 tabular-nums">{formatDate(a.occurred_at)}</span>
          </div>
        ))}
      </div>
    </InfoCard>
  );
}

/* ══════════════════════════════════════════════════════════════
   ADMIN DASHBOARD – HAUPTKOMPONENTE
   ══════════════════════════════════════════════════════════════ */
export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const reload = () => {
    setLoading(true);
    apiClient.get('/api/dashboard/stats', { withCredentials: true })
      .then(r => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { reload(); }, []);

  /* ── LOADING STATE ─────────────────────────────────────── */
  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]" data-testid="admin-dashboard-loading">
      <div className="text-center space-y-3">
        <Loader2 size={32} className="animate-spin text-[var(--color-primary)] mx-auto" />
        <p className="text-sm font-medium text-[var(--color-text-secondary)]">Admin Cockpit wird geladen...</p>
      </div>
    </div>
  );

  /* ── RENDER ────────────────────────────────────────────── */
  return (
    <PageScaffold
      title="Admin Cockpit"
      subtitle={`Systemweite Uebersicht und Steuerung | ${new Date().toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long' })}`}
      testId="admin-dashboard"
      actions={
        <button onClick={reload} className="w2g-btn-secondary" data-testid="admin-refresh-btn">
          <RefreshCw size={14} /> Aktualisieren
        </button>
      }
    >

      {/* ═══ KPI-ZONE: 5 Karten ═══════════════════════════ */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4" data-testid="admin-kpi-zone">
        <KpiCard label="Gesamt Bewerber" value={stats?.total_leads} icon={Users} link="/staff/kanban" testId="admin-stat-leads" />
        <KpiCard label="Aktive Bewerber" value={stats?.open_leads} icon={Activity} link="/staff/kanban" testId="admin-stat-active" />
        <KpiCard label="Offene Aufgaben" value={stats?.open_tasks} icon={CheckSquare} link="/staff/tasks" testId="admin-stat-tasks" />
        <KpiCard label="Docs ausstehend" value={stats?.pending_documents} icon={FileText} testId="admin-stat-docs" />
        <KpiCard label="Nachrichten" value={stats?.unread_messages ?? 0} icon={MessageSquare} link="/staff/messaging" testId="admin-stat-messages" />
      </div>

      {/* ═══ NUTZER-UEBERSICHT ═════════════════════════════ */}
      <Card data-testid="admin-users-summary">
        <CardContent className="px-5 py-4 flex items-center gap-4 flex-wrap">
          <div className="w-9 h-9 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center shrink-0">
            <Users size={16} className="text-[var(--color-primary)]" />
          </div>
          <div className="flex gap-5 text-xs flex-wrap">
            <span className="text-[var(--color-text-secondary)]"><strong className="text-[var(--color-text-primary)] tabular-nums">{stats?.total_users ?? 0}</strong> Nutzer</span>
            <span className="text-[var(--color-text-secondary)]"><strong className="text-[var(--color-text-primary)] tabular-nums">{stats?.total_staff ?? 0}</strong> Mitarbeiter</span>
            <span className="text-[var(--color-text-secondary)]"><strong className="text-[var(--color-text-primary)] tabular-nums">{stats?.total_applicants ?? 0}</strong> Bewerber</span>
          </div>
          <Link to="/admin/users" className="w2g-btn-table-action ml-auto" data-testid="admin-manage-users-link">
            Verwalten <ChevronRight size={10} />
          </Link>
        </CardContent>
      </Card>

      {/* ═══ HAUPTZONE: 3-Spalten ═════════════════════════ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* ── SPALTE 1+2: Pipeline + Activity ────────────── */}
        <div className="lg:col-span-2 space-y-5">
          <PipelineBar pipeline={stats?.pipeline} />
          <RecentActivity activities={stats?.recent_activity} />
        </div>

        {/* ── SPALTE 3: Schnellzugriff + Hinweise ────────── */}
        <div className="space-y-4">

          {/* Schnellzugriff */}
          <InfoCard title="Schnellzugriff" noPadding testId="admin-quick-actions">
            <div className="px-4 pb-3 pt-1">
              <div className="space-y-0.5">
                {[
                  { to: '/admin/users', label: 'Nutzer verwalten', desc: 'Accounts, Rollen, Einladungen', icon: UserPlus },
                  { to: '/staff/kanban', label: 'Kanban Board', desc: 'Bewerbungsuebersicht', icon: BarChart3 },
                  { to: '/staff/tasks', label: 'Aufgaben', desc: 'Team-Tasks verwalten', icon: CheckSquare },
                  { to: '/staff/messaging', label: 'Nachrichten', desc: 'In-App Kommunikation', icon: MessageSquare },
                  { to: '/staff/invoices', label: 'Rechnungen', desc: 'Rechnungserstellung', icon: FileText },
                  { to: '/admin/audit', label: 'Audit Logs', desc: 'Systemaktionen', icon: Shield },
                ].map(item => (
                  <Link key={item.to} to={item.to}
                    data-testid={`admin-action-${item.to.split('/').pop()}`}
                    className="flex items-center gap-2.5 px-2.5 py-2.5 text-xs text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-elevated)] hover:text-[var(--color-primary)] rounded-[var(--radius-xs)] transition-all group">
                    <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center shrink-0 transition-colors">
                      <item.icon size={14} className="text-[var(--color-primary)]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-[var(--color-text-primary)]">{item.label}</p>
                      <p className="text-[10px] text-[var(--color-text-tertiary)]">{item.desc}</p>
                    </div>
                    <ChevronRight size={14} className="text-[var(--color-text-tertiary)] group-hover:text-[var(--color-primary)]" />
                  </Link>
                ))}
              </div>
            </div>
          </InfoCard>

          {/* Hinweise/Alerts */}
          {(stats?.open_tasks > 5 || stats?.pending_documents > 3) && (
            <InfoCard title="Hinweise" icon={AlertCircle} testId="admin-alerts">
                <div className="space-y-1.5">
                  {stats?.open_tasks > 5 && (
                    <div className="flex items-center gap-2">
                      <Badge variant="warning" size="xs"><Zap size={9} />{stats.open_tasks} offene Aufgaben</Badge>
                    </div>
                  )}
                  {stats?.pending_documents > 3 && (
                    <div className="flex items-center gap-2">
                      <Badge variant="danger" size="xs"><FileText size={9} />{stats.pending_documents} Dokumente ausstehend</Badge>
                    </div>
                  )}
                </div>
            </InfoCard>
          )}
        </div>
      </div>

      {/* Backstage StatusLine */}
      <StatusLine
        items={[
          { icon: Users, label: 'Gesamt', value: stats?.total_leads || 0, color: 'var(--color-primary)' },
          { icon: Activity, label: 'Aktiv', value: stats?.open_leads || 0 },
          { icon: CheckSquare, label: 'Tasks', value: stats?.open_tasks || 0, color: (stats?.open_tasks || 0) > 5 ? 'var(--color-warning)' : undefined },
          { icon: Shield, label: 'Nutzer', value: stats?.total_users || 0 },
        ]}
        testId="admin-status-line"
      />
    </PageScaffold>
  );
}
