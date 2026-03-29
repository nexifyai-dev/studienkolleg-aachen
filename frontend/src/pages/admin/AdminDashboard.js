import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, Activity, Database, Link } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/api/dashboard/stats`, { withCredentials: true })
      .then(r => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="admin-dashboard">
      <div>
        <h1 className="text-2xl font-heading font-bold text-slate-900">Admin Dashboard</h1>
        <p className="text-slate-500 text-sm">W2G Platform System Overview</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Gesamt Leads', value: stats?.total_leads ?? '–', icon: Users },
          { label: 'Aktive Leads', value: stats?.open_leads ?? '–', icon: Activity },
          { label: 'Offene Aufgaben', value: stats?.open_tasks ?? '–', icon: Database },
          { label: 'Dokumente offen', value: stats?.pending_documents ?? '–', icon: Link },
        ].map(item => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="bg-white border border-slate-200 rounded-sm p-5" data-testid={`admin-stat-${item.label}`}>
              <Icon size={18} className="text-slate-400 mb-3" />
              <p className="text-2xl font-bold text-slate-900">{item.value}</p>
              <p className="text-slate-500 text-xs mt-1">{item.label}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { href: '/admin/users', label: 'Nutzer verwalten', desc: 'Accounts, Rollen, Einladungen' },
          { href: '/staff/kanban', label: 'Kanban Board', desc: 'Bewerbungsübersicht' },
          { href: '/admin/audit', label: 'Audit Logs', desc: 'Alle Systemaktionen' },
        ].map(item => (
          <a key={item.href} href={item.href}
            className="bg-white border border-slate-200 rounded-sm p-5 hover:border-slate-400 transition-colors block"
            data-testid={`admin-action-${item.label.toLowerCase().replace(/ /g, '-')}`}>
            <h3 className="font-semibold text-slate-800 text-sm mb-1">{item.label}</h3>
            <p className="text-slate-500 text-xs">{item.desc}</p>
          </a>
        ))}
      </div>
    </div>
  );
}
