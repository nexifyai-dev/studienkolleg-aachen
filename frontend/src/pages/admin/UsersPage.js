import React, { useEffect, useState } from 'react';
import apiClient from '../../lib/apiClient';
import { ROLE_LABELS, formatDate } from '../../lib/utils';
import { UserPlus, RefreshCw } from 'lucide-react';
import { formatApiError } from '../../contexts/AuthContext';


export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInvite, setShowInvite] = useState(false);
  const [invite, setInvite] = useState({ email: '', full_name: '', role: 'staff' });
  const [inviteResult, setInviteResult] = useState(null);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/users`, { withCredentials: true });
      setUsers(res.data);
    } catch {}
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleInvite = async e => {
    e.preventDefault(); setError(''); setInviteResult(null);
    try {
      const res = await apiClient.post(`/api/auth/invite`, invite, { withCredentials: true });
      setInviteResult(res.data);
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail));
    }
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="admin-users-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold text-slate-900">Nutzer</h1>
          <p className="text-slate-500 text-sm">{users.length} Nutzer registriert</p>
        </div>
        <div className="flex gap-2">
          <button onClick={load} className="flex items-center gap-2 text-slate-500 border border-slate-200 px-3 py-2 rounded-sm text-sm hover:border-slate-400">
            <RefreshCw size={14} /> Aktualisieren
          </button>
          <button onClick={() => setShowInvite(!showInvite)} data-testid="invite-user-btn"
            className="flex items-center gap-2 bg-primary text-white px-3 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover">
            <UserPlus size={14} /> Einladen
          </button>
        </div>
      </div>

      {showInvite && (
        <div className="bg-white border border-slate-200 rounded-sm p-5 max-w-md" data-testid="invite-form">
          <h3 className="font-semibold text-slate-800 mb-4">Nutzer einladen</h3>
          {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
          {inviteResult ? (
            <div className="bg-green-50 border border-green-200 rounded-sm p-3 text-sm" data-testid="invite-result">
              <p className="font-medium text-green-800">Einladungslink erstellt:</p>
              <p className="text-green-700 break-all mt-1 text-xs">{inviteResult.invite_url}</p>
            </div>
          ) : (
            <form onSubmit={handleInvite} className="space-y-3">
              <input placeholder="E-Mail" type="email" value={invite.email} required
                onChange={e => setInvite(p => ({...p, email: e.target.value}))} data-testid="invite-email-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
              <input placeholder="Vollständiger Name" value={invite.full_name}
                onChange={e => setInvite(p => ({...p, full_name: e.target.value}))} data-testid="invite-name-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
              <select value={invite.role} onChange={e => setInvite(p => ({...p, role: e.target.value}))}
                data-testid="invite-role-select"
                className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary">
                {['staff','accounting_staff','agency_admin','agency_agent','affiliate','applicant'].map(r => (
                  <option key={r} value={r}>{ROLE_LABELS[r] || r}</option>
                ))}
              </select>
              <button type="submit" className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover">
                Einladungslink generieren
              </button>
            </form>
          )}
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr className="text-xs text-slate-500 font-medium">
                <th className="px-4 py-3 text-left">Name</th>
                <th className="px-4 py-3 text-left">E-Mail</th>
                <th className="px-4 py-3 text-left">Rolle</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Erstellt</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-400">Laden…</td></tr>
              ) : users.map(u => (
                <tr key={u.id} className="border-t border-slate-50 hover:bg-slate-50" data-testid={`user-row-${u.id}`}>
                  <td className="px-4 py-3 text-sm font-medium text-slate-800">{u.full_name || '–'}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{u.email}</td>
                  <td className="px-4 py-3">
                    <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-sm">
                      {ROLE_LABELS[u.role] || u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-sm ${u.active ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'}`}>
                      {u.active ? 'Aktiv' : 'Deaktiviert'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">{formatDate(u.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
