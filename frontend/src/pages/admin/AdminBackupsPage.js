import React from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Loader2, Database, RefreshCcw, Trash2, HardDrive, AlertTriangle, CheckCircle, PlayCircle, RotateCcw } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';
import { API } from '../../lib/apiBase';
import { csrfRequestInterceptor } from '../../lib/csrf';

const api = axios.create({ baseURL: `${API}/api`, withCredentials: true });
api.interceptors.request.use(csrfRequestInterceptor);

function formatBytes(mb) {
  if (mb == null) return '–';
  if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`;
  if (mb < 1024) return `${mb.toFixed(1)} MB`;
  return `${(mb / 1024).toFixed(2)} GB`;
}

function formatDate(iso) {
  if (!iso) return '–';
  try {
    const d = new Date(iso);
    return d.toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' });
  } catch { return iso; }
}

export default function AdminBackupsPage() {
  const qc = useQueryClient();
  const [busy, setBusy] = React.useState('');
  const [confirmRestore, setConfirmRestore] = React.useState(null);

  const status = useQuery({
    queryKey: ['backups', 'status'],
    queryFn: () => api.get('/backups/status').then(r => r.data),
    refetchInterval: 30000,
  });

  const list = useQuery({
    queryKey: ['backups', 'list'],
    queryFn: () => api.get('/backups').then(r => r.data?.backups || []),
  });

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ['backups'] });
  };

  const runBackup = async () => {
    setBusy('run');
    try {
      const r = await api.post('/backups/run');
      if (r.data?.status === 'ok') toast.success('Backup erfolgreich erstellt');
      else if (r.data?.status === 'skipped') toast.warning(`Backup übersprungen: ${r.data.message}`);
      else toast.error(r.data?.message || 'Backup fehlgeschlagen');
      refresh();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Backup fehlgeschlagen');
    } finally { setBusy(''); }
  };

  const deleteBackup = async (name) => {
    if (!window.confirm(`Backup "${name}" wirklich löschen?`)) return;
    setBusy(`del-${name}`);
    try {
      await api.delete(`/backups/${name}`);
      toast.success('Backup gelöscht');
      refresh();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Löschen fehlgeschlagen');
    } finally { setBusy(''); }
  };

  const restoreBackup = async (name) => {
    setBusy(`restore-${name}`);
    try {
      await api.post(`/backups/${name}/restore`);
      toast.success(`Backup ${name} wurde wiederhergestellt`);
      setConfirmRestore(null);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Restore fehlgeschlagen');
    } finally { setBusy(''); }
  };

  const s = status.data || {};
  const items = list.data || [];

  return (
    <PageScaffold
      title="Backups & Wiederherstellung"
      subtitle="MongoDB-Sicherungen · nightlich automatisch · Retention 7 Tage"
      testId="admin-backups-page"
      actions={
        <div className="flex items-center gap-2">
          <button onClick={refresh} className="w2g-btn-secondary text-xs flex items-center gap-1.5" data-testid="backups-refresh">
            <RefreshCcw size={12} /> Aktualisieren
          </button>
          <button
            onClick={runBackup}
            disabled={busy === 'run' || !s.mongodump_available}
            className="w2g-btn-primary text-xs flex items-center gap-1.5 disabled:opacity-50"
            data-testid="backups-run-btn"
          >
            {busy === 'run' ? <Loader2 size={12} className="animate-spin" /> : <PlayCircle size={12} />}
            Jetzt sichern
          </button>
        </div>
      }
    >
      {/* Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        <Card className="p-4">
          <div className="flex items-center gap-2 text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]"><HardDrive size={11} /> Pfad</div>
          <div className="text-xs font-mono text-[var(--color-text-primary)] mt-1 truncate" title={s.backup_dir}>{s.backup_dir || '–'}</div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-2 text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]"><Database size={11} /> Backups</div>
          <div className="text-lg font-bold text-[var(--color-text-primary)] mt-1">{s.count ?? 0}</div>
        </Card>
        <Card className="p-4">
          <div className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">Retention</div>
          <div className="text-lg font-bold text-[var(--color-text-primary)] mt-1">{s.retention_days ?? 7} Tage</div>
        </Card>
        <Card className="p-4">
          <div className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">Tools</div>
          <div className="flex flex-col gap-1 mt-1">
            <span className={`inline-flex items-center gap-1 text-[11px] ${s.mongodump_available ? 'text-[var(--color-success)]' : 'text-[var(--color-danger)]'}`}>
              {s.mongodump_available ? <CheckCircle size={10} /> : <AlertTriangle size={10} />} mongodump
            </span>
            <span className={`inline-flex items-center gap-1 text-[11px] ${s.mongorestore_available ? 'text-[var(--color-success)]' : 'text-[var(--color-danger)]'}`}>
              {s.mongorestore_available ? <CheckCircle size={10} /> : <AlertTriangle size={10} />} mongorestore
            </span>
          </div>
        </Card>
      </div>

      {!s.mongodump_available && (
        <Card className="p-4 border-[var(--color-warning)] bg-[var(--color-warning-bg)]/40">
          <div className="flex items-center gap-2 text-xs text-[var(--color-text-primary)]">
            <AlertTriangle size={14} className="text-[var(--color-warning)]" />
            <span><strong>mongodump</strong> nicht verfügbar auf diesem System. Backups können nicht erstellt werden.</span>
          </div>
        </Card>
      )}

      {/* Backup-Liste */}
      <Card className="overflow-hidden p-0">
        <table className="w-full" data-testid="backups-table">
          <thead>
            <tr className="border-b border-[var(--color-divider)]">
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Name</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Zeitstempel</th>
              <th className="text-right text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Größe</th>
              <th className="text-right text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {list.isLoading ? (
              <tr><td colSpan={4} className="text-center py-8"><Loader2 size={16} className="inline animate-spin text-[var(--color-primary)]" /></td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={4} className="text-center py-8 text-xs text-[var(--color-text-tertiary)]">Noch keine Backups vorhanden</td></tr>
            ) : items.map(b => (
              <tr key={b.name} className="border-b border-[var(--color-divider-subtle)] hover:bg-[var(--color-surface-sunken)] transition-colors" data-testid={`backup-row-${b.name}`}>
                <td className="px-4 py-2.5">
                  <span className="text-xs font-mono text-[var(--color-text-primary)]">{b.name}</span>
                </td>
                <td className="px-4 py-2.5 text-xs text-[var(--color-text-secondary)]">{formatDate(b.timestamp)}</td>
                <td className="px-4 py-2.5 text-right text-xs font-medium text-[var(--color-text-primary)]">{formatBytes(b.size_mb)}</td>
                <td className="px-4 py-2.5">
                  <div className="flex items-center justify-end gap-1">
                    <button
                      onClick={() => setConfirmRestore(b.name)}
                      disabled={!s.mongorestore_available || busy === `restore-${b.name}`}
                      title="Wiederherstellen"
                      className="p-1.5 rounded-md text-[var(--color-warning)] hover:bg-[var(--color-surface-sunken)] transition-colors disabled:opacity-40"
                      data-testid={`backup-restore-btn-${b.name}`}
                    >
                      {busy === `restore-${b.name}` ? <Loader2 size={13} className="animate-spin" /> : <RotateCcw size={13} />}
                    </button>
                    <button
                      onClick={() => deleteBackup(b.name)}
                      disabled={busy === `del-${b.name}`}
                      title="Löschen"
                      className="p-1.5 rounded-md text-[var(--color-danger)] hover:bg-[var(--color-surface-sunken)] transition-colors disabled:opacity-40"
                      data-testid={`backup-delete-btn-${b.name}`}
                    >
                      {busy === `del-${b.name}` ? <Loader2 size={13} className="animate-spin" /> : <Trash2 size={13} />}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      {confirmRestore && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" data-testid="restore-confirm-modal" onClick={() => setConfirmRestore(null)}>
          <div className="bg-[var(--color-surface)] rounded-[var(--radius-md)] shadow-xl w-full max-w-md p-5" onClick={e => e.stopPropagation()}>
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={18} className="text-[var(--color-danger)]" />
              <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">Wiederherstellung bestätigen</h3>
            </div>
            <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
              Die aktuelle Datenbank wird durch das Backup <span className="font-mono">{confirmRestore}</span> <strong>ersetzt</strong>.
              Alle Änderungen seit dieser Sicherung gehen verloren. Diese Aktion kann nicht rückgängig gemacht werden.
            </p>
            <div className="mt-4 flex justify-end gap-2">
              <button
                onClick={() => setConfirmRestore(null)}
                className="text-xs px-3 py-2 rounded-[var(--radius-sm)] border border-[var(--color-divider)] hover:bg-[var(--color-surface-sunken)]"
                data-testid="restore-cancel-btn"
              >
                Abbrechen
              </button>
              <button
                onClick={() => restoreBackup(confirmRestore)}
                disabled={busy?.startsWith('restore')}
                className="text-xs px-3 py-2 rounded-[var(--radius-sm)] bg-[var(--color-danger)] text-white hover:opacity-90 disabled:opacity-50"
                data-testid="restore-confirm-btn"
              >
                {busy?.startsWith('restore') ? <Loader2 size={12} className="animate-spin inline mr-1" /> : null}
                Ja, wiederherstellen
              </button>
            </div>
          </div>
        </div>
      )}
    </PageScaffold>
  );
}
