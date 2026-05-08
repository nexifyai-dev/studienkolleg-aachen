import React, { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { formatDate, getLang } from '../../lib/utils';
import { RefreshCw, Search, XCircle } from 'lucide-react';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

const ACTION_LABELS_DE = {
  user_created: 'Nutzer erstellt', user_updated: 'Nutzer aktualisiert',
  application_stage_changed: 'Status geaendert', document_uploaded: 'Dokument hochgeladen',
  document_reviewed: 'Dokument geprueft', invoice_created: 'Rechnung erstellt',
  task_created: 'Aufgabe erstellt', email_sent: 'E-Mail gesendet',
  login: 'Anmeldung', invite_created: 'Einladung erstellt',
};
const ACTION_LABELS_EN = {
  user_created: 'User created', user_updated: 'User updated',
  application_stage_changed: 'Status changed', document_uploaded: 'Document uploaded',
  document_reviewed: 'Document reviewed', invoice_created: 'Invoice created',
  task_created: 'Task created', email_sent: 'Email sent',
  login: 'Login', invite_created: 'Invite created',
};

export default function AuditPage() {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const ACTION_LABELS = lang === 'en' ? ACTION_LABELS_EN : ACTION_LABELS_DE;
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState('all');

  const load = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/audit-logs', { withCredentials: true });
      setLogs(res.data);
    } catch {}
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const actions = useMemo(() => {
    const set = new Set(logs.map(l => l.action));
    return ['all', ...Array.from(set).sort()];
  }, [logs]);

  const filteredLogs = useMemo(() => {
    let result = logs;
    if (actionFilter !== 'all') result = result.filter(l => l.action === actionFilter);
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      result = result.filter(l =>
        (l.action || '').toLowerCase().includes(q) ||
        (l.target_type || '').toLowerCase().includes(q) ||
        (l.target_id || '').toLowerCase().includes(q) ||
        (l.actor_id || '').toLowerCase().includes(q)
      );
    }
    return result;
  }, [logs, actionFilter, searchTerm]);

  return (
    <PageScaffold
      title="Audit Logs"
      subtitle={`${filteredLogs.length} von ${logs.length} Eintraegen`}
      testId="audit-page"
      actions={
        <button onClick={load} className="w2g-btn-secondary" data-testid="audit-refresh-btn">
          <RefreshCw size={14} /> Aktualisieren
        </button>
      }
      toolbar={
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72 shrink-0">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
                placeholder="Logs durchsuchen..."
                data-testid="audit-search"
                className="w2g-search pl-9" />
              {searchTerm && (
                <button onClick={() => setSearchTerm('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]">
                  <XCircle size={13} />
                </button>
              )}
            </div>
          }
          filters={[
            <select key="action" value={actionFilter} onChange={e => setActionFilter(e.target.value)}
              data-testid="audit-action-filter"
              className="w2g-select text-xs w-auto py-1.5">
              {actions.map(a => (
                <option key={a} value={a}>{a === 'all' ? 'Alle Aktionen' : ACTION_LABELS[a] || a}</option>
              ))}
            </select>,
          ]}
        />
      }
    >
      <Card className="p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w2g-table">
            <thead>
              <tr>
                <th>Aktion</th>
                <th>Zielobjekt</th>
                <th>Akteur</th>
                <th>Details</th>
                <th>Zeit</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-[var(--color-text-tertiary)]">Laden...</td></tr>
              ) : filteredLogs.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-[var(--color-text-tertiary)]">
                  {searchTerm || actionFilter !== 'all' ? 'Keine Treffer' : 'Keine Logs vorhanden'}
                </td></tr>
              ) : filteredLogs.slice(0, 200).map(log => (
                <tr key={log.id} className="hover:bg-[var(--color-surface-elevated)] transition-colors" data-testid={`audit-row-${log.id}`}>
                  <td>
                    <span className="w2g-badge bg-primary-muted text-primary font-medium">
                      {ACTION_LABELS[log.action] || log.action}
                    </span>
                  </td>
                  <td className="text-xs text-[var(--color-text-secondary)]">
                    {log.target_type && <span className="font-medium">{log.target_type}</span>}
                    {log.target_id && <span className="text-[var(--color-text-tertiary)] ml-1">#{log.target_id.slice(-8)}</span>}
                  </td>
                  <td className="text-xs text-[var(--color-text-secondary)]">
                    {log.actor_id ? `#${log.actor_id.slice(-8)}` : 'System'}
                  </td>
                  <td className="text-xs text-[var(--color-text-secondary)] max-w-[200px] truncate">
                    {log.details && typeof log.details === 'object' ? JSON.stringify(log.details).slice(0, 60) : ''}
                  </td>
                  <td className="text-xs text-[var(--color-text-tertiary)] whitespace-nowrap">{formatDate(log.occurred_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </PageScaffold>
  );
}
