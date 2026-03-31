import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../lib/apiClient';
import { formatDate } from '../../lib/utils';
import { AlertTriangle, ExternalLink, RefreshCw, Search } from 'lucide-react';

const DEFAULT_FILTERS = {
  q: '',
  action: 'all',
  target_type: 'all',
  role: '',
  period: 'all',
  sort: 'newest',
};

const CRITICAL_ACTION_PATTERNS = [
  /role/i,
  /deactiv/i,
  /stage_takeover/i,
  /stage_changed/i,
];

const TARGET_LINKS = {
  application: (id) => `/staff/applications/${id}`,
  task: () => '/staff/tasks',
  user: () => '/admin/users',
};

const PERIOD_TO_DAYS = {
  '24h': 1,
  '7d': 7,
  '30d': 30,
  '90d': 90,
};

function getCriticality(log) {
  const action = log.action || '';
  if (CRITICAL_ACTION_PATTERNS.some((pattern) => pattern.test(action))) {
    return { label: 'Kritisch', className: 'bg-red-50 text-red-700 border-red-200' };
  }
  const fields = Array.isArray(log?.details?.fields) ? log.details.fields : [];
  if (fields.includes('role') || fields.includes('active')) {
    return { label: 'Kritisch', className: 'bg-red-50 text-red-700 border-red-200' };
  }
  return { label: 'Normal', className: 'bg-primary/10 text-primary border-primary/20' };
}

function getTargetLink(log) {
  const resolver = TARGET_LINKS[log.target_type];
  if (!resolver || !log.target_id) return null;
  return resolver(log.target_id);
}

export default function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState(DEFAULT_FILTERS);

  const load = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.q.trim()) params.set('q', filters.q.trim());
      if (filters.action !== 'all') params.set('action', filters.action);
      if (filters.target_type !== 'all') params.set('target_type', filters.target_type);
      if (filters.role.trim()) params.set('role', filters.role.trim());
      params.set('sort', filters.sort);

      if (filters.period !== 'all') {
        const days = PERIOD_TO_DAYS[filters.period];
        if (days) {
          const dateFrom = new Date();
          dateFrom.setUTCDate(dateFrom.getUTCDate() - days);
          params.set('date_from', dateFrom.toISOString());
        }
      }

      const query = params.toString();
      const res = await apiClient.get(`/api/audit-logs${query ? `?${query}` : ''}`, { withCredentials: true });
      setLogs(res.data || []);
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const actionOptions = useMemo(
    () => [...new Set(logs.map((log) => log.action).filter(Boolean))].sort(),
    [logs]
  );
  const targetTypeOptions = useMemo(
    () => [...new Set(logs.map((log) => log.target_type).filter(Boolean))].sort(),
    [logs]
  );

  return (
    <div className="space-y-6 animate-fade-in" data-testid="audit-page">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-heading font-bold text-primary">Audit Logs</h1>
          <p className="text-slate-500 text-sm">{logs.length} Einträge</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 text-slate-500 border border-slate-200 px-3 py-2 rounded-sm text-sm hover:border-slate-400 transition-colors">
          <RefreshCw size={14} /> Aktualisieren
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm p-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-3" data-testid="audit-filters">
        <div className="xl:col-span-2 relative">
          <Search size={14} className="absolute left-2.5 top-2.5 text-slate-400" />
          <input
            value={filters.q}
            onChange={(e) => setFilters((prev) => ({ ...prev, q: e.target.value }))}
            placeholder="Suche: Akteur, Aktion, Zielobjekt-ID"
            className="w-full border border-slate-200 rounded-sm pl-8 pr-2.5 py-2 text-xs focus:outline-none focus:border-primary"
            data-testid="audit-search"
          />
        </div>

        <select
          value={filters.action}
          onChange={(e) => setFilters((prev) => ({ ...prev, action: e.target.value }))}
          className="border border-slate-200 rounded-sm px-3 py-2 text-xs focus:outline-none focus:border-primary"
          data-testid="audit-filter-action"
        >
          <option value="all">Aktionstyp: Alle</option>
          {actionOptions.map((action) => (
            <option key={action} value={action}>{action}</option>
          ))}
        </select>

        <select
          value={filters.target_type}
          onChange={(e) => setFilters((prev) => ({ ...prev, target_type: e.target.value }))}
          className="border border-slate-200 rounded-sm px-3 py-2 text-xs focus:outline-none focus:border-primary"
          data-testid="audit-filter-target"
        >
          <option value="all">Zieltyp: Alle</option>
          {targetTypeOptions.map((target) => (
            <option key={target} value={target}>{target}</option>
          ))}
        </select>

        <select
          value={filters.period}
          onChange={(e) => setFilters((prev) => ({ ...prev, period: e.target.value }))}
          className="border border-slate-200 rounded-sm px-3 py-2 text-xs focus:outline-none focus:border-primary"
          data-testid="audit-filter-period"
        >
          <option value="all">Zeitraum: Alle</option>
          <option value="24h">Letzte 24h</option>
          <option value="7d">Letzte 7 Tage</option>
          <option value="30d">Letzte 30 Tage</option>
          <option value="90d">Letzte 90 Tage</option>
        </select>

        <input
          value={filters.role}
          onChange={(e) => setFilters((prev) => ({ ...prev, role: e.target.value }))}
          placeholder="Rolle (optional)"
          className="border border-slate-200 rounded-sm px-3 py-2 text-xs focus:outline-none focus:border-primary"
          data-testid="audit-filter-role"
        />

        <select
          value={filters.sort}
          onChange={(e) => setFilters((prev) => ({ ...prev, sort: e.target.value }))}
          className="border border-slate-200 rounded-sm px-3 py-2 text-xs focus:outline-none focus:border-primary"
          data-testid="audit-filter-sort"
        >
          <option value="newest">Sortierung: Neueste zuerst</option>
          <option value="oldest">Sortierung: Älteste zuerst</option>
        </select>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr className="text-xs text-slate-500 font-medium">
                <th className="px-4 py-3 text-left">Aktion</th>
                <th className="px-4 py-3 text-left">Kritikalität</th>
                <th className="px-4 py-3 text-left">Zielobjekt</th>
                <th className="px-4 py-3 text-left">Akteur</th>
                <th className="px-4 py-3 text-left">Zeit</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-400">Laden…</td></tr>
              ) : logs.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-400">Keine Logs vorhanden</td></tr>
              ) : logs.map((log) => {
                const criticality = getCriticality(log);
                const targetLink = getTargetLink(log);
                return (
                  <tr key={log.id} className="border-t border-slate-50 hover:bg-slate-50" data-testid={`audit-row-${log.id}`}>
                    <td className="px-4 py-3">
                      <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded-sm font-mono">{log.action}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 text-[11px] border px-2 py-0.5 rounded-sm ${criticality.className}`}>
                        {criticality.label === 'Kritisch' && <AlertTriangle size={12} />}
                        {criticality.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {targetLink ? (
                        <Link to={targetLink} className="inline-flex items-center gap-1 text-primary hover:underline" data-testid={`audit-target-link-${log.id}`}>
                          {log.target_type}/{log.target_id?.slice(-8)} <ExternalLink size={11} />
                        </Link>
                      ) : (
                        <span>{log.target_type}/{log.target_id?.slice(-8)}</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">{log.actor_id?.slice(-8) || 'system'}</td>
                    <td className="px-4 py-3 text-xs text-slate-500">{formatDate(log.occurred_at)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
