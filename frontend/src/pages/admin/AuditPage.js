import React, { useEffect, useState } from 'react';
import apiClient from '../../lib/apiClient';
import { formatDate } from '../../lib/utils';
import { RefreshCw } from 'lucide-react';


export default function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/audit-logs`, { withCredentials: true });
      setLogs(res.data);
    } catch {}
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-6 animate-fade-in" data-testid="audit-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold text-slate-900">Audit Logs</h1>
          <p className="text-slate-500 text-sm">{logs.length} Einträge</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 text-slate-500 border border-slate-200 px-3 py-2 rounded-sm text-sm hover:border-slate-400">
          <RefreshCw size={14} /> Aktualisieren
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr className="text-xs text-slate-500 font-medium">
                <th className="px-4 py-3 text-left">Aktion</th>
                <th className="px-4 py-3 text-left">Zielobjekt</th>
                <th className="px-4 py-3 text-left">Akteur</th>
                <th className="px-4 py-3 text-left">Zeit</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-slate-400">Laden…</td></tr>
              ) : logs.length === 0 ? (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-slate-400">Keine Logs vorhanden</td></tr>
              ) : logs.map(log => (
                <tr key={log.id} className="border-t border-slate-50 hover:bg-slate-50" data-testid={`audit-row-${log.id}`}>
                  <td className="px-4 py-3">
                    <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded-sm font-mono">{log.action}</span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">{log.target_type}/{log.target_id?.slice(-8)}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">{log.actor_id?.slice(-8) || 'system'}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">{formatDate(log.occurred_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
