import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import {
  Activity, RefreshCw, XCircle, CheckCircle, Clock,
  AlertTriangle, Search, Filter, RotateCcw, Zap, Cpu,
  TrendingUp, BarChart3, Timer, ArrowRight, ChevronDown,
} from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { getLang } from '../../lib/utils';
import { API } from '../../lib/apiBase';

const apiFetch = async (url, opts = {}) => {
  const resp = await fetch(`${API}${url}`, { credentials: 'include', headers: { 'Content-Type': 'application/json' }, ...opts });
  if (!resp.ok) throw new Error((await resp.json().catch(() => ({}))).detail || resp.statusText);
  return resp.json();
};

/* ── Status-Konfiguration ───────────────────────────────────────── */
const STATUS_CONFIG = {
  queued: { label: 'Wartend', color: 'bg-[var(--color-info-bg)] text-[var(--color-info)] border-[var(--color-info-border)]/60', icon: Clock, dotColor: 'bg-[var(--color-info)]' },
  running: { label: 'Wird verarbeitet', color: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border-[var(--color-warning-border)]/60', icon: Activity, dotColor: 'bg-[var(--color-warning)]' },
  succeeded: { label: 'Erfolgreich', color: 'bg-[var(--color-success-bg)] text-[var(--color-success)] border-[var(--color-success-border)]/60', icon: CheckCircle, dotColor: 'bg-[var(--color-success)]' },
  failed: { label: 'Fehlgeschlagen', color: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border-[var(--color-danger-border)]/60', icon: XCircle, dotColor: 'bg-[var(--color-danger)]' },
  retry_scheduled: { label: 'Erneuter Versuch', color: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border-[var(--color-warning-border)]', icon: RefreshCw, dotColor: 'bg-[var(--color-warning)]' },
  dead_letter: { label: 'Endgueltig fehlgeschlagen', color: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border-[var(--color-danger-border)]', icon: AlertTriangle, dotColor: 'bg-[var(--color-danger)]' },
  cancelled: { label: 'Abgebrochen', color: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)] border-[var(--color-divider)]/60', icon: XCircle, dotColor: 'bg-[var(--color-text-tertiary)]' },
};

const TYPE_CONFIG = {
  ai_screening: { label: 'KI-Screening', icon: Cpu },
  delta_rescreening: { label: 'Delta Re-Screening', icon: RefreshCw },
  email_send: { label: 'E-Mail', icon: ArrowRight },
  notification_create: { label: 'Notification', icon: Zap },
  document_validation: { label: 'Dokument-Validierung', icon: CheckCircle },
  queue_followup: { label: 'Queue Followup', icon: RotateCcw },
  inactivity_reminder: { label: 'Inaktivitaets-Erinnerung', icon: Clock },
  pdf_export: { label: 'PDF Export', icon: BarChart3 },
  cleanup: { label: 'Bereinigung', icon: XCircle },
};

const PRIORITY_CONFIG = {
  critical: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border-[var(--color-danger-border)]',
  high: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border-[var(--color-warning-border)]',
  normal: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)] border-[var(--color-divider)]',
  low: 'bg-[var(--color-surface-elevated)] text-[var(--color-text-tertiary)] border-[var(--color-divider-subtle)]',
};

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.queued;
  const Icon = cfg.icon;
  return (
    <span data-testid={`status-${status}`} className={`inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-1 border ${cfg.color}`}>
      <Icon size={11} />
      {cfg.label}
    </span>
  );
}

function TypeBadge({ jobType }) {
  const cfg = TYPE_CONFIG[jobType] || { label: jobType, icon: Activity };
  const Icon = cfg.icon;
  return (
    <span className="inline-flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-1 rounded-[var(--radius-md)] bg-[var(--color-surface-elevated)] text-[var(--color-text-secondary)] border border-[var(--color-divider)]/50">
      <Icon size={11} />
      {cfg.label}
    </span>
  );
}

function MetricCard({ label, value, icon: Icon, subtext }) {
  return (
    <Card>
      <CardContent className="p-4 flex items-start gap-3">
        <div className="w-10 h-10 rounded-[var(--radius-sm)] flex items-center justify-center bg-[var(--color-primary-muted)]">
          <Icon size={18} className="text-[var(--color-primary)]" />
        </div>
        <div>
          <p className="text-2xl font-bold" style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}>{value}</p>
          <p className="text-[11px] text-[var(--color-text-tertiary)] font-medium uppercase tracking-wider">{label}</p>
          {subtext && <p className="text-[10px] text-[var(--color-text-tertiary)] mt-0.5">{subtext}</p>}
        </div>
      </CardContent>
    </Card>
  );
}

/* ═══════ HAUPT-KOMPONENTE ═══════════════════════════════════════ */
export default function AdminJobsPage() {
  const [tab, setTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const [s, h] = await Promise.all([
        apiFetch('/api/jobs/stats'),
        apiFetch('/api/jobs/health'),
      ]);
      setStats(s);
      setHealth(h);
    } catch (err) { toast.error(err.message); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  // Auto-Refresh alle 10s fuer Dashboard
  useEffect(() => {
    if (tab !== 'dashboard') return;
    const iv = setInterval(loadDashboard, 10000);
    return () => clearInterval(iv);
  }, [tab, loadDashboard]);

  const tabs = [
    { key: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { key: 'jobs', label: 'Alle Jobs', icon: Activity },
    { key: 'failed', label: 'Fehlgeschlagen', icon: AlertTriangle },
  ];

  return (
    <PageScaffold
      title="Background Jobs"
      subtitle="Asynchrone Verarbeitung und Monitoring"
      testId="admin-jobs-page"
      actions={
        <button onClick={loadDashboard} data-testid="refresh-jobs" className="w2g-btn-secondary">
          <RefreshCw size={13} /> Aktualisieren
        </button>
      }
    >

      {/* Tab Navigation */}
      <div className="flex gap-1 p-1 rounded-[var(--radius-md)] border border-[var(--color-divider)]/50" style={{ background: 'var(--color-surface-elevated)' }}>
        {tabs.map(t => {
          const Icon = t.icon;
          const isActive = tab === t.key;
          return (
            <button key={t.key} onClick={() => setTab(t.key)} data-testid={`tab-${t.key}`}
              className={`flex items-center gap-1.5 text-xs font-medium px-4 py-2.5 rounded-[var(--radius-md)] transition-all ${isActive ? 'bg-white shadow-sm text-[var(--color-primary)] border border-[var(--color-divider)]/50' : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-white/50'}`}>
              <Icon size={13} />
              {t.label}
              {t.key === 'failed' && stats && (stats.failed + stats.dead_letter) > 0 && (
                <span className="ml-1 text-[10px] font-bold px-1.5 py-0.5 bg-[var(--color-danger)] text-white rounded-[var(--radius-sm)]">{stats.failed + stats.dead_letter}</span>
              )}
            </button>
          );
        })}
      </div>

      {/* Content */}
      {tab === 'dashboard' && <DashboardTab stats={stats} health={health} loading={loading} />}
      {tab === 'jobs' && <JobListTab />}
      {tab === 'failed' && <JobListTab defaultStatus="failed" />}
    </PageScaffold>
  );
}

/* ═══════ DASHBOARD TAB ═══════════════════════════════════════════ */
function DashboardTab({ stats, health, loading }) {
  if (loading || !stats || !health) {
    return (
      <div className="w2g-card p-12 text-center">
        <div className="w-8 h-8 border-2 border-[var(--color-divider)] border-t-[var(--color-primary)] rounded-full animate-spin mx-auto mb-3" />
        <p className="text-sm text-[var(--color-text-tertiary)]">Dashboard wird geladen...</p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Worker Status */}
      <div data-testid="worker-health" className={`p-4 rounded-[var(--radius-md)] border flex items-center gap-3 ${health.is_healthy ? 'bg-[var(--color-success-bg)]/50 border-[var(--color-success-border)]/50' : 'bg-[var(--color-danger-bg)]/50 border-[var(--color-danger-border)]/50'}`}>
        <div className={`w-3 h-3 rounded-full animate-pulse ${health.is_healthy ? 'bg-[var(--color-success)]' : 'bg-[var(--color-danger)]'}`} />
        <div className="flex-1">
          <p className="text-sm font-semibold" style={{ color: 'var(--color-primary)' }}>
            Worker: {health.is_healthy ? 'Aktiv und gesund' : 'Fehlerhaft'}
          </p>
          <p className="text-[10px] text-[var(--color-text-tertiary)]">
            Gestartet: {health.started_at ? new Date(health.started_at).toLocaleString('de') : '–'} ·
            Verarbeitet: {health.jobs_processed} · Fehler: {health.jobs_failed}
            {health.current_job && <span className="ml-2 text-[var(--color-info)]">Aktuell: {health.current_job.job_type}</span>}
          </p>
        </div>
      </div>

      {/* Metriken */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard label="In Queue" value={stats.queued} icon={Clock} subtext="Wartende Jobs" />
        <MetricCard label="Laufend" value={stats.running} icon={Activity} subtext="In Verarbeitung" />
        <MetricCard label="Erfolgreich" value={stats.succeeded} icon={CheckCircle} subtext="Abgeschlossen" />
        <MetricCard label="Fehlgeschlagen" value={stats.failed + stats.dead_letter} icon={AlertTriangle}
          subtext={stats.dead_letter > 0 ? `${stats.dead_letter} endgueltig` : 'Inkl. Dead Letter'}
          accent={stats.failed + stats.dead_letter > 0 ? 'bg-[var(--color-danger)]' : undefined} />
      </div>

      {/* Performance-Metriken */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <MetricCard label="Fehlerrate (1h)" value={`${stats.error_rate_1h}%`} icon={TrendingUp}
          accent={stats.error_rate_1h > 10 ? 'bg-[var(--color-danger)]' : undefined} />
        <MetricCard label="Durchschn. Dauer" value={stats.avg_duration_ms > 0 ? `${(stats.avg_duration_ms / 1000).toFixed(1)}s` : '–'} icon={Timer} />
        <MetricCard label="Max. Dauer" value={stats.max_duration_ms > 0 ? `${(stats.max_duration_ms / 1000).toFixed(1)}s` : '–'} icon={Timer} />
      </div>

      {/* Job-Typ-Verteilung (24h) */}
      {Object.keys(stats.by_type_24h || {}).length > 0 && (
        <div className="w2g-card">
          <h3 className="text-sm font-bold mb-3" style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}>
            Job-Typen (letzte 24h)
          </h3>
          <div className="space-y-2">
            {Object.entries(stats.by_type_24h).map(([type, count]) => {
              const cfg = TYPE_CONFIG[type] || { label: type, icon: Activity };
              const Icon = cfg.icon;
              const maxCount = Math.max(...Object.values(stats.by_type_24h));
              const pct = Math.round((count / maxCount) * 100);
              return (
                <div key={type} className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5 w-40 flex-shrink-0">
                    <Icon size={12} className="text-[var(--color-text-tertiary)]" />
                    <span className="text-xs text-[var(--color-text-secondary)] truncate">{cfg.label}</span>
                  </div>
                  <div className="flex-1 h-5 bg-[var(--color-surface-sunken)] rounded-full overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${pct}%`, background: 'var(--color-primary)', opacity: 0.7 }} />
                  </div>
                  <span className="text-xs font-bold text-[var(--color-text-secondary)] w-8 text-right">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Letzte Fehler */}
      {stats.recent_errors && stats.recent_errors.length > 0 && (
        <div className="w2g-card border-[var(--color-danger-border)]/50">
          <h3 className="text-sm font-bold mb-3 text-[var(--color-danger)]" style={{ fontFamily: 'var(--font-heading)' }}>
            Letzte Fehler
          </h3>
          <div className="space-y-2">
            {stats.recent_errors.map((err, i) => (
              <div key={i} className="flex items-start gap-3 p-2.5 rounded-[var(--radius-md)] bg-[var(--color-danger-bg)]/50 border border-[var(--color-danger-border)]">
                <AlertTriangle size={14} className="text-[var(--color-danger)] mt-0.5 flex-shrink-0" />
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-xs font-semibold text-[var(--color-danger)]">{err.job_type}</span>
                    <span className="text-[10px] text-[var(--color-danger)]">[{err.job_id}]</span>
                    {err.retry_count > 0 && <span className="text-[10px] text-[var(--color-warning)] font-medium">{err.retry_count}x versucht</span>}
                  </div>
                  <p className="text-[11px] text-[var(--color-danger)] break-all">{err.error_summary || '–'}</p>
                  <p className="text-[10px] text-[var(--color-danger)] mt-0.5">{err.failed_at ? new Date(err.failed_at).toLocaleString('de') : '–'}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ═══════ JOB LIST TAB ═══════════════════════════════════════════ */
function JobListTab({ defaultStatus = '' }) {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState(defaultStatus);
  const [filterType, setFilterType] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedJob, setExpandedJob] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterStatus) params.set('status', filterStatus);
      if (filterType) params.set('job_type', filterType);
      if (searchQuery) params.set('q', searchQuery);
      const data = await apiFetch(`/api/jobs?${params.toString()}`);
      setJobs(data.jobs || []);
      setTotal(data.total || 0);
    } catch (err) { toast.error(err.message); }
    finally { setLoading(false); }
  }, [filterStatus, filterType, searchQuery]);

  useEffect(() => { load(); }, [load]);

  const handleRetry = async (jobId) => {
    try {
      await apiFetch(`/api/jobs/${jobId}/retry`, { method: 'POST' });
      toast.success('Job erneut in Queue gestellt');
      load();
    } catch (err) { toast.error(err.message); }
  };

  const handleCancel = async (jobId) => {
    try {
      await apiFetch(`/api/jobs/${jobId}/cancel`, { method: 'POST' });
      toast.success('Job abgebrochen');
      load();
    } catch (err) { toast.error(err.message); }
  };

  return (
    <div data-testid="job-list-tab" className="space-y-4">
      {/* Filter-Bar */}
      <div className="flex flex-wrap items-center gap-2 p-3 rounded-[var(--radius-md)] border border-[var(--color-divider)]/50" style={{ background: 'var(--color-surface-elevated)', boxShadow: 'var(--shadow-e1)' }}>
        <div className="flex items-center gap-1.5 flex-1 min-w-[200px] bg-white rounded-[var(--radius-md)] border border-[var(--color-divider)] px-3">
          <Search size={13} className="text-[var(--color-text-tertiary)]" />
          <input data-testid="job-search" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
            placeholder="Job-ID, Entity-ID oder Fehler suchen..." className="flex-1 text-xs py-2 bg-transparent outline-none" />
        </div>
        <select data-testid="filter-status" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
          className="text-xs px-3 py-2 rounded-[var(--radius-md)] border border-[var(--color-divider)] bg-white">
          <option value="">Alle Status</option>
          {Object.entries(STATUS_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <select data-testid="filter-type" value={filterType} onChange={e => setFilterType(e.target.value)}
          className="text-xs px-3 py-2 rounded-[var(--radius-md)] border border-[var(--color-divider)] bg-white">
          <option value="">Alle Typen</option>
          {Object.entries(TYPE_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <span className="text-xs text-[var(--color-text-tertiary)]"><Filter size={11} className="inline" /> {total} Jobs</span>
      </div>

      {/* Job-Liste */}
      {loading ? (
        <div className="w2g-card p-12 text-center">
          <div className="w-8 h-8 border-2 border-[var(--color-divider)] border-t-[var(--color-primary)] rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-[var(--color-text-tertiary)]">Jobs werden geladen...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="w2g-card p-12 text-center">
          <CheckCircle size={32} className="text-[var(--color-success)] mx-auto mb-3" />
          <p className="text-sm font-semibold text-[var(--color-text-secondary)] mb-1">Keine Jobs gefunden</p>
          <p className="text-xs text-[var(--color-text-tertiary)]">Filter anpassen oder alle anzeigen.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {jobs.map(job => {
            const isExpanded = expandedJob === job.job_id;
            return (
              <div key={job.job_id} data-testid={`job-${job.job_id}`} className="w2g-card overflow-hidden">
                {/* Kompakte Zeile */}
                <div className="flex items-center gap-3 cursor-pointer" onClick={() => setExpandedJob(isExpanded ? null : job.job_id)}>
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 ${(STATUS_CONFIG[job.status] || STATUS_CONFIG.queued).dotColor}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-mono font-bold text-[var(--color-text-primary)]">{job.job_id}</span>
                      <TypeBadge jobType={job.job_type} />
                      <StatusBadge status={job.status} />
                      {job.priority && job.priority !== 'normal' && (
                        <span className={`text-[10px] font-bold px-2 py-0.5 border ${PRIORITY_CONFIG[job.priority] || PRIORITY_CONFIG.normal}`}>
                          {job.priority.toUpperCase()}
                        </span>
                      )}
                      {job.retry_count > 0 && (
                        <span className="text-[10px] text-[var(--color-warning)] font-medium">{job.retry_count}/{job.max_retries} Versuche</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-0.5 text-[10px] text-[var(--color-text-tertiary)]">
                      <span>{job.created_at ? new Date(job.created_at).toLocaleString('de') : '–'}</span>
                      {job.duration_ms && <span>· {(job.duration_ms / 1000).toFixed(1)}s</span>}
                      {job.related_entity_type && <span>· {job.related_entity_type}: {job.related_entity_id}</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {(job.status === 'failed' || job.status === 'dead_letter') && (
                      <button onClick={e => { e.stopPropagation(); handleRetry(job.job_id); }} data-testid={`retry-${job.job_id}`}
                        className="text-xs font-medium text-[var(--color-warning)] bg-[var(--color-warning-bg)] hover:bg-[var(--color-warning-bg)] px-3 py-1.5 rounded-[var(--radius-md)] border border-[var(--color-warning-border)] transition-colors">
                        <RotateCcw size={11} className="inline mr-1" />Retry
                      </button>
                    )}
                    {(job.status === 'queued' || job.status === 'retry_scheduled') && (
                      <button onClick={e => { e.stopPropagation(); handleCancel(job.job_id); }} data-testid={`cancel-${job.job_id}`}
                        className="text-xs font-medium text-[var(--color-danger)] bg-[var(--color-danger-bg)] hover:bg-[var(--color-danger-bg)] px-3 py-1.5 rounded-[var(--radius-md)] border border-[var(--color-danger-border)]/60 transition-colors">
                        <XCircle size={11} className="inline mr-1" />Cancel
                      </button>
                    )}
                    <ChevronDown size={14} className={`text-[var(--color-text-tertiary)] transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                  </div>
                </div>

                {/* Expandierter Bereich */}
                {isExpanded && (
                  <div className="mt-3 pt-3 border-t border-[var(--color-divider-subtle)] space-y-2">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
                      <div><span className="text-[var(--color-text-tertiary)]">Erstellt:</span><br/><span className="font-medium">{job.created_at ? new Date(job.created_at).toLocaleString('de') : '–'}</span></div>
                      <div><span className="text-[var(--color-text-tertiary)]">Gestartet:</span><br/><span className="font-medium">{job.started_at ? new Date(job.started_at).toLocaleString('de') : '–'}</span></div>
                      <div><span className="text-[var(--color-text-tertiary)]">Abgeschlossen:</span><br/><span className="font-medium">{job.finished_at ? new Date(job.finished_at).toLocaleString('de') : '–'}</span></div>
                      <div><span className="text-[var(--color-text-tertiary)]">Dauer:</span><br/><span className="font-medium">{job.duration_ms ? `${(job.duration_ms / 1000).toFixed(2)}s` : '–'}</span></div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
                      <div><span className="text-[var(--color-text-tertiary)]">Akteur:</span><br/><span className="font-medium">{job.actor_id || '–'}</span></div>
                      <div><span className="text-[var(--color-text-tertiary)]">Correlation:</span><br/><span className="font-mono font-medium">{job.correlation_id || '–'}</span></div>
                      <div><span className="text-[var(--color-text-tertiary)]">Dedupe-Key:</span><br/><span className="font-mono font-medium text-[var(--color-text-secondary)]">{job.dedupe_key || '–'}</span></div>
                      <div><span className="text-[var(--color-text-tertiary)]">Prioritaet:</span><br/><span className="font-medium">{job.priority || 'normal'}</span></div>
                    </div>
                    {job.error_summary && (
                      <div className="p-2.5 rounded-[var(--radius-md)] bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)]">
                        <p className="text-[11px] font-semibold text-[var(--color-danger)] mb-0.5">Fehler</p>
                        <p className="text-[11px] text-[var(--color-danger)] break-all">{job.error_summary}</p>
                      </div>
                    )}
                    {job.payload && Object.keys(job.payload).length > 0 && (
                      <div className="p-2.5 rounded-[var(--radius-md)] bg-[var(--color-surface-elevated)] border border-[var(--color-divider-subtle)]">
                        <p className="text-[11px] font-semibold text-[var(--color-text-secondary)] mb-0.5">Payload</p>
                        <pre className="text-[10px] text-[var(--color-text-secondary)] overflow-x-auto whitespace-pre-wrap">{JSON.stringify(job.payload, null, 2)}</pre>
                      </div>
                    )}
                    {job.result && (
                      <div className="p-2.5 rounded-[var(--radius-md)] bg-[var(--color-success-bg)] border border-[var(--color-success-border)]">
                        <p className="text-[11px] font-semibold text-[var(--color-success)] mb-0.5">Ergebnis</p>
                        <pre className="text-[10px] text-[var(--color-success)] overflow-x-auto whitespace-pre-wrap">{JSON.stringify(job.result, null, 2)}</pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
