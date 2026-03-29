import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, FileText, CheckSquare, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { STAGE_LABELS } from '../../lib/utils';

const API = process.env.REACT_APP_BACKEND_URL;

export default function StaffDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentApps, setRecentApps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [statsRes, appsRes] = await Promise.all([
          axios.get(`${API}/api/dashboard/stats`, { withCredentials: true }),
          axios.get(`${API}/api/applications`, { withCredentials: true }),
        ]);
        setStats(statsRes.data);
        setRecentApps(appsRes.data.slice(0, 10));
      } catch {}
      finally { setLoading(false); }
    };
    load();
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="staff-dashboard">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">Staff Dashboard</h1>
        <p className="text-slate-500 text-sm">Willkommen zurück, {user?.full_name || user?.email}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Gesamt Leads', value: stats?.total_leads ?? '–', icon: Users, color: 'text-blue-600 bg-blue-50' },
          { label: 'Aktive Leads', value: stats?.open_leads ?? '–', icon: TrendingUp, color: 'text-primary bg-accent/20' },
          { label: 'Offene Aufgaben', value: stats?.open_tasks ?? '–', icon: CheckSquare, color: 'text-orange-600 bg-orange-50' },
          { label: 'Dokumente offen', value: stats?.pending_documents ?? '–', icon: FileText, color: 'text-purple-600 bg-purple-50' },
        ].map(item => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="bg-white border border-slate-200 rounded-sm p-5"
              data-testid={`staff-stat-${item.label.toLowerCase().replace(/ /g, '-')}`}>
              <div className={`w-10 h-10 rounded-sm flex items-center justify-center mb-3 ${item.color}`}>
                <Icon size={20} />
              </div>
              <p className="text-2xl font-heading font-bold text-slate-800">{item.value}</p>
              <p className="text-slate-500 text-xs mt-1">{item.label}</p>
            </div>
          );
        })}
      </div>

      {/* Recent applications */}
      <div className="bg-white border border-slate-200 rounded-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-semibold text-slate-800">Aktuelle Bewerbungen</h3>
          <Link to="/staff/kanban" className="text-sm text-primary hover:underline">Kanban ansehen →</Link>
        </div>
        {recentApps.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">Keine Bewerbungen vorhanden</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50 text-xs text-slate-500 font-medium">
                  <th className="px-4 py-3 text-left">Bewerber</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-left">Quelle</th>
                  <th className="px-4 py-3 text-left">Erstellt</th>
                </tr>
              </thead>
              <tbody>
                {recentApps.map(app => (
                  <tr key={app.id} className="border-t border-slate-50 hover:bg-slate-50 transition-colors"
                    data-testid={`staff-app-row-${app.id}`}>
                    <td className="px-4 py-3 text-sm font-medium text-slate-800">
                      {app.applicant?.full_name || app.applicant?.email || app.applicant_id?.slice(-8)}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-sm">
                        {STAGE_LABELS[app.current_stage] || app.current_stage}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">{app.source || '–'}</td>
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {app.created_at ? new Date(app.created_at).toLocaleDateString('de-DE') : '–'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
