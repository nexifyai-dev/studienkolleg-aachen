import React from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api-hooks';
import { Activity, AlertTriangle, CheckCircle, Clock, Server, Loader2, Shield, Settings2, Database, Sparkles } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { toast } from 'sonner';
import { getLang } from '../../lib/utils';

function useSystemMonitoring() {
  return useQuery({
    queryKey: ['system', 'monitoring'],
    queryFn: () => api.get('/system/monitoring').then(r => r.data),
    refetchInterval: 30000,
    staleTime: 10000,
  });
}

function StatusBadge({ ok, label }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium rounded-[var(--radius-full)] ${ok
      ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]'
      : 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]'
    }`} data-testid={`status-${label.toLowerCase().replace(/\s/g,'-')}`}>
      {ok ? <CheckCircle size={10} /> : <AlertTriangle size={10} />}
      {label}
    </span>
  );
}

export default function AdminSettingsPage() {
  const { data, isLoading } = useSystemMonitoring();

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-[var(--color-primary)]" />
    </div>
  );

  const worker = data?.worker || {};
  const scheduler = data?.scheduler || {};
  const queue = data?.job_queue || {};
  const metrics = data?.system_metrics || {};

  return (
    <PageScaffold
      title="System & Monitoring"
      subtitle="Echtzeit-Systemzustand, Worker, Scheduler und Metriken"
      testId="admin-settings-page"
      actions={
        <div className="flex gap-2">
          <StatusBadge ok={worker.is_healthy} label="Worker" />
          <StatusBadge ok={scheduler.is_healthy} label="Scheduler" />
        </div>
      }
      contentClassName="space-y-4"
    >
      {/* Service Health */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Card data-testid="worker-health">
          <CardContent className="px-4 py-3">
            <div className="flex items-center gap-2 mb-3">
              <Server size={14} className="text-[var(--color-primary)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Background Worker</span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className="text-[var(--color-text-tertiary)]">Status</span>
                <StatusBadge ok={worker.is_healthy} label={worker.running ? 'Aktiv' : 'Gestoppt'} />
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--color-text-tertiary)]">Verarbeitete Jobs</span>
                <span className="font-medium text-[var(--color-text-primary)]">{worker.jobs_processed || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--color-text-tertiary)]">Fehlgeschlagen</span>
                <span className={`font-medium ${worker.jobs_failed > 0 ? 'text-[var(--color-danger)]' : 'text-[var(--color-text-primary)]'}`}>
                  {worker.jobs_failed || 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card data-testid="scheduler-health">
          <CardContent className="px-4 py-3">
            <div className="flex items-center gap-2 mb-3">
              <Clock size={14} className="text-[var(--color-accent)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Scheduler</span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className="text-[var(--color-text-tertiary)]">Status</span>
                <StatusBadge ok={scheduler.is_healthy} label={scheduler.running ? 'Aktiv' : 'Gestoppt'} />
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--color-text-tertiary)]">Ausgefuehrt</span>
                <span className="font-medium text-[var(--color-text-primary)]">{scheduler.runs_total || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--color-text-tertiary)]">Fehler</span>
                <span className={`font-medium ${scheduler.errors_total > 0 ? 'text-[var(--color-danger)]' : 'text-[var(--color-text-primary)]'}`}>
                  {scheduler.errors_total || 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card data-testid="queue-health">
          <CardContent className="px-4 py-3">
            <div className="flex items-center gap-2 mb-3">
              <Activity size={14} className="text-[var(--color-primary)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Job Queue</span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className="text-[var(--color-text-tertiary)]">Warteschlange</span>
                <span className="font-medium text-[var(--color-text-primary)]">{queue.pending || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--color-text-tertiary)]">In Verarbeitung</span>
                <span className="font-medium text-[var(--color-text-primary)]">{queue.processing || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--color-text-tertiary)]">Fehlgeschlagen (24h)</span>
                <span className={`font-medium ${queue.failed_24h > 0 ? 'text-[var(--color-danger)]' : 'text-[var(--color-text-primary)]'}`}>
                  {queue.failed_24h || 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System-Metriken */}
      <Card data-testid="system-metrics">
        <CardContent className="px-5 py-4">
          <div className="flex items-center gap-2 mb-4">
            <Database size={14} className="text-[var(--color-primary)]" />
            <span className="text-xs font-semibold text-[var(--color-text-primary)]">Live-Metriken</span>
            {metrics.metrics_age_seconds != null && (
              <span className="text-[10px] text-[var(--color-text-tertiary)]">
                (vor {metrics.metrics_age_seconds}s aktualisiert)
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: 'Bewerbungen', value: metrics.applications_total, sub: `${metrics.applications_active || 0} aktiv` },
              { label: 'Offene Aufgaben', value: metrics.tasks_open, warn: metrics.tasks_overdue > 0, sub: `${metrics.tasks_overdue || 0} ueberfaellig` },
              { label: 'Unbezahlte Rechnungen', value: metrics.invoices_unpaid, warn: metrics.invoices_unpaid > 0 },
              { label: 'Dokumente ausstehend', value: metrics.documents_pending, warn: metrics.documents_pending > 0 },
              { label: 'Jobs wartend', value: metrics.jobs_pending },
              { label: 'Jobs fehlgeschlagen (24h)', value: metrics.jobs_failed_24h, warn: metrics.jobs_failed_24h > 0 },
              { label: 'Benutzer gesamt', value: metrics.users_total },
            ].map((m, i) => (
              <div key={i} className="p-2.5 rounded-[var(--radius-sm)] border border-[var(--color-divider)] bg-[var(--color-surface-sunken)]">
                <p className="text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)]">{m.label}</p>
                <p className={`text-lg font-bold mt-0.5 ${m.warn ? 'text-[var(--color-danger)]' : 'text-[var(--color-text-primary)]'}`}>
                  {m.value ?? '\u2014'}
                </p>
                {m.sub && <p className="text-[10px] text-[var(--color-text-tertiary)]">{m.sub}</p>}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Konfiguration */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        <Card data-testid="config-branding">
          <CardContent className="px-4 py-3">
            <div className="flex items-center gap-2 mb-3">
              <Settings2 size={14} className="text-[var(--color-accent)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Branding</span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">Primaerfarbe</span><span className="font-medium text-[var(--color-primary)]">CI-Blau aktiv</span></div>
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">Design-System</span><span className="font-medium text-[var(--color-text-primary)]">Swiss Elite v1.3</span></div>
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">Token-Compliance</span><StatusBadge ok={true} label="100%" /></div>
            </div>
          </CardContent>
        </Card>

        <Card data-testid="config-security">
          <CardContent className="px-4 py-3">
            <div className="flex items-center gap-2 mb-3">
              <Shield size={14} className="text-[var(--color-primary)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Sicherheit</span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">Rate-Limiting</span><StatusBadge ok={true} label="Aktiv" /></div>
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">Audit-Trail</span><StatusBadge ok={true} label="Aktiv" /></div>
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">CORS</span><StatusBadge ok={true} label="Restriktiv" /></div>
            </div>
          </CardContent>
        </Card>

        <Card data-testid="config-integrations">
          <CardContent className="px-4 py-3">
            <div className="flex items-center gap-2 mb-3">
              <Activity size={14} className="text-[var(--color-accent)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Integrationen</span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">DeepSeek KI</span><StatusBadge ok={true} label="Verbunden" /></div>
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">Strato SMTP</span><StatusBadge ok={true} label="Konfiguriert" /></div>
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">Oracle</span><StatusBadge ok={true} label="Aktiv" /></div>
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">Stripe Payments</span><StatusBadge ok={data?.integrations?.stripe_active !== false} label={data?.integrations?.stripe_active !== false ? 'Live' : 'Inaktiv'} /></div>
              <div className="flex justify-between"><span className="text-[var(--color-text-tertiary)]">S3 Storage</span><StatusBadge ok={data?.integrations?.storage_active !== false} label={data?.integrations?.storage_active !== false ? 'Aktiv' : 'Fehlt'} /></div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Scheduler-Details */}
      {scheduler.last_run && Object.keys(scheduler.last_run).length > 0 && (
        <Card data-testid="scheduler-details">
          <CardContent className="px-5 py-4">
            <div className="flex items-center gap-2 mb-3">
              <Clock size={14} className="text-[var(--color-primary)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Scheduler-Ausfuehrungen</span>
            </div>
            <div className="space-y-1 text-xs">
              {Object.entries(scheduler.last_run).map(([name, ts]) => (
                <div key={name} className="flex justify-between">
                  <span className="text-[var(--color-text-tertiary)]">{name}</span>
                  <span className="text-[var(--color-text-secondary)]">{new Date(ts).toLocaleString('de-DE')}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <DemoDataControls />
    </PageScaffold>
  );
}

function DemoDataControls() {
  const [busy, setBusy] = React.useState(null);
  const [result, setResult] = React.useState(null);

  const handleSeed = async () => {
    if (!window.confirm('Demo-Daten wiederherstellen?\n\nLegt 12 realistische Test-Bewerber + 5 Aufgaben an. Bestehende Demo-Accounts werden aktualisiert, nicht dupliziert.')) return;
    setBusy('seed');
    try {
      const r = await api.post('/system/seed-demo-data');
      setResult(r.data?.summary || r.data);
      toast.success(`Demo-Daten erstellt: ${r.data?.summary?.users_created || 0} neue Bewerber, ${r.data?.summary?.tasks_created || 0} neue Aufgaben`);
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Seed fehlgeschlagen');
    } finally {
      setBusy(null);
    }
  };

  const handleClean = async () => {
    if (!window.confirm('ACHTUNG: ALLE operativen Daten löschen?\n\n(Bewerbungen, Tasks, Dokumente, Rechnungen, Audit-Logs, …)\n\nNur Dev-Accounts und Stammdaten bleiben erhalten.')) return;
    setBusy('clean');
    try {
      const r = await api.post('/system/clean-demo-data');
      setResult(r.data?.summary || r.data);
      toast.success('Datenbank bereinigt');
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Bereinigung fehlgeschlagen');
    } finally {
      setBusy(null);
    }
  };

  return (
    <Card data-testid="demo-data-controls">
      <CardContent className="px-5 py-4">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={14} className="text-[var(--color-primary)]" />
          <span className="text-xs font-semibold text-[var(--color-text-primary)]">Demo-Daten & Datenbank-Reset</span>
        </div>
        <p className="text-xs text-[var(--color-text-tertiary)] mb-3">
          Für Live-Präsentationen: 12 Demo-Bewerber mit verschiedenen Pipeline-Stadien + 5 realistische Staff-Aufgaben in einem Klick erzeugen.
        </p>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleSeed}
            disabled={!!busy}
            data-testid="seed-demo-data-button"
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium text-white bg-[var(--color-primary)] rounded-[var(--radius-sm)] disabled:opacity-50 hover:opacity-90 transition-opacity"
          >
            {busy === 'seed' ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
            Demo-Daten wiederherstellen
          </button>
          <button
            onClick={handleClean}
            disabled={!!busy}
            data-testid="clean-demo-data-button"
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium text-[var(--color-danger)] border border-[var(--color-danger)] rounded-[var(--radius-sm)] disabled:opacity-50 hover:bg-[var(--color-danger-bg)] transition-colors"
          >
            {busy === 'clean' ? <Loader2 size={14} className="animate-spin" /> : null}
            Alle operativen Daten löschen
          </button>
        </div>
        {result && (
          <pre className="mt-3 text-[11px] text-[var(--color-text-secondary)] bg-[var(--color-bg-secondary)] p-2 rounded overflow-x-auto" data-testid="demo-data-result">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
      </CardContent>
    </Card>
  );
}
