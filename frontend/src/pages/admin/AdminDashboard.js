import React, { useEffect, useState } from 'react';
import apiClient from '../../lib/apiClient';
import { Users, Activity, Database, Link as LinkIcon, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';


export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get(`/api/dashboard/stats`, { withCredentials: true })
      .then(r => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;

  return (
    <div className="space-y-5 animate-fade-in" data-testid="admin-dashboard">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-heading font-bold text-primary">Admin Dashboard</h1>
          <p className="text-slate-500 text-sm">System, Rollen, Audit und Qualitätslage</p>
        </div>
        <div className="inline-flex items-center gap-1.5 text-xs px-3 py-2 rounded-sm border border-primary/20 bg-primary/5 text-primary">
          <ShieldCheck size={14} /> Governance aktiv
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { label: 'Gesamt Leads', value: stats?.total_leads ?? '–', icon: Users },
          { label: 'Aktive Leads', value: stats?.open_leads ?? '–', icon: Activity },
          { label: 'Offene Aufgaben', value: stats?.open_tasks ?? '–', icon: Database },
          { label: 'Dokumente offen', value: stats?.pending_documents ?? '–', icon: LinkIcon },
        ].map(item => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="bg-white border border-slate-200 rounded-sm p-4 hover:border-primary/30 transition-colors" data-testid={`admin-stat-${item.label}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="w-9 h-9 rounded-sm bg-primary/10 flex items-center justify-center">
                  <Icon size={17} className="text-primary" />
                </div>
              </div>
              <p className="text-2xl font-heading font-bold text-slate-800">{item.value}</p>
              <p className="text-slate-500 text-xs mt-0.5">{item.label}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-sm p-4" data-testid="admin-focus-panel">
          <h3 className="font-semibold text-slate-800 text-sm mb-3 flex items-center gap-2">
            <AlertCircle size={14} className="text-primary" /> Prioritäten heute
          </h3>
          <div className="space-y-2">
            <Link to="/staff/kanban?stage=pending_docs" className="flex items-center justify-between text-sm border border-slate-200 rounded-sm px-3 py-2 hover:border-primary/30 hover:bg-primary/5 transition-colors">
              <span className="text-slate-700">Unvollständige Bewerbungen prüfen</span>
              <ArrowRight size={14} className="text-primary" />
            </Link>
            <Link to="/admin/users" className="flex items-center justify-between text-sm border border-slate-200 rounded-sm px-3 py-2 hover:border-primary/30 hover:bg-primary/5 transition-colors">
              <span className="text-slate-700">Rollen/Accounts validieren</span>
              <ArrowRight size={14} className="text-primary" />
            </Link>
            <Link to="/admin/audit" className="flex items-center justify-between text-sm border border-slate-200 rounded-sm px-3 py-2 hover:border-primary/30 hover:bg-primary/5 transition-colors">
              <span className="text-slate-700">Audit-Events und Stage-Wechsel kontrollieren</span>
              <ArrowRight size={14} className="text-primary" />
            </Link>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-sm p-4" data-testid="admin-quick-actions">
          <h3 className="font-semibold text-slate-800 text-sm mb-3">Quick Actions</h3>
          <div className="space-y-1.5 text-sm">
            <Link to="/admin/users" className="block px-3 py-2 rounded-sm text-slate-700 hover:bg-slate-50 hover:text-primary transition-colors">Nutzer verwalten</Link>
            <Link to="/staff/kanban" className="block px-3 py-2 rounded-sm text-slate-700 hover:bg-slate-50 hover:text-primary transition-colors">Kanban öffnen</Link>
            <Link to="/staff/tasks" className="block px-3 py-2 rounded-sm text-slate-700 hover:bg-slate-50 hover:text-primary transition-colors">Aufgaben prüfen</Link>
            <Link to="/admin/audit" className="block px-3 py-2 rounded-sm text-slate-700 hover:bg-slate-50 hover:text-primary transition-colors">Audit Logs</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
