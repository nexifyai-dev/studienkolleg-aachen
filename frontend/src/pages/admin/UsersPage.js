import React, { useEffect, useState } from 'react';
import apiClient from '../../lib/apiClient';
import { ROLE_LABELS, formatDate } from '../../lib/utils';
import { UserPlus, RefreshCw, UserCheck, UserX, Search } from 'lucide-react';
import { formatApiError } from '../../contexts/AuthContext';

const STAFF_ROLES = ['superadmin', 'admin', 'staff', 'accounting_staff', 'agency_admin', 'agency_agent', 'affiliate'];
const INVITABLE_ROLES = ['staff', 'accounting_staff', 'agency_admin', 'agency_agent', 'affiliate'];

const ROLE_DESCRIPTIONS = {
  staff: 'Sachbearbeiter – Bewerbungen bearbeiten, Dokumente prüfen, KI-Screening starten',
  accounting_staff: 'Buchhaltung – Zahlungen, Rechnungen, Finanzübersicht',
  agency_admin: 'Agentur-Admin – eigene Agentur verwalten, Bewerbungen einreichen',
  agency_agent: 'Agentur-Agent – Bewerbungen einreichen, Kommunikation',
  affiliate: 'Partner – Leads einbringen, Provision-Tracking',
};

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInvite, setShowInvite] = useState(false);
  const [invite, setInvite] = useState({ email: '', full_name: '', role: 'staff' });
  const [inviteResult, setInviteResult] = useState(null);
  const [error, setError] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [query, setQuery] = useState('');
  const [updating, setUpdating] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/users', { withCredentials: true });
      setUsers(res.data || []);
    } catch {}
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleInvite = async e => {
    e.preventDefault(); setError(''); setInviteResult(null);
    try {
      const res = await apiClient.post('/api/auth/invite', invite, { withCredentials: true });
      setInviteResult(res.data);
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail));
    }
  };

  const toggleActive = async (userId, currentActive) => {
    setUpdating(userId);
    try {
      await apiClient.put(`/api/users/${userId}`, { active: !currentActive }, { withCredentials: true });
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, active: !currentActive } : u));
    } catch {}
    finally { setUpdating(null); }
  };

  const staffUsers = users.filter(u => STAFF_ROLES.includes(u.role));
  const applicantUsers = users.filter(u => u.role === 'applicant');

  const roleFilteredUsers = filterRole === 'all'
    ? users
    : filterRole === 'staff_only'
    ? staffUsers
    : applicantUsers;
  const displayUsers = roleFilteredUsers.filter(u => {
    if (!query.trim()) return true;
    const haystack = [u.full_name, u.email, u.role].filter(Boolean).join(' ').toLowerCase();
    return haystack.includes(query.trim().toLowerCase());
  });

  return (
    <div className="space-y-6 animate-fade-in" data-testid="admin-users-page">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-heading font-bold text-primary">Nutzerverwaltung</h1>
          <p className="text-slate-500 text-sm">
            {staffUsers.length} Mitarbeiter · {applicantUsers.length} Bewerber
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <button onClick={load}
            className="flex items-center gap-2 text-slate-500 border border-slate-200 px-3 py-2 rounded-sm text-sm hover:border-slate-400 transition-colors"
            data-testid="users-refresh-btn">
            <RefreshCw size={14} /> Aktualisieren
          </button>
          <button onClick={() => { setShowInvite(!showInvite); setInviteResult(null); setError(''); }}
            data-testid="invite-user-btn"
            className="flex items-center gap-2 bg-primary text-white px-3 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover transition-colors">
            <UserPlus size={14} /> Mitarbeiter einladen
          </button>
        </div>
      </div>

      {/* Einladungs-Panel */}
      {showInvite && (
        <div className="bg-white border border-slate-200 rounded-sm p-5 max-w-lg" data-testid="invite-form">
          <h3 className="font-semibold text-slate-800 mb-1">Mitarbeiter einladen</h3>
          <p className="text-slate-500 text-xs mb-4">
            Generiere einen Einladungslink. Der neue Mitarbeiter setzt sein eigenes Passwort.
          </p>
          {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
          {inviteResult ? (
            <div className="bg-slate-50 border border-slate-200 rounded-sm p-4 text-sm" data-testid="invite-result">
              <p className="font-medium text-slate-800 mb-1">Einladungslink erstellt:</p>
              <code className="block text-slate-700 break-all text-xs bg-slate-100 p-2 rounded-sm">{inviteResult.invite_url}</code>
              <p className="text-slate-600 text-xs mt-2">Bitte diesen Link sicher an den Mitarbeiter senden (nicht per unverschlüsselter E-Mail).</p>
              <button onClick={() => setInviteResult(null)} className="mt-2 text-xs text-primary hover:underline">
                Weiteren Mitarbeiter einladen
              </button>
            </div>
          ) : (
            <form onSubmit={handleInvite} className="space-y-3">
              <input placeholder="E-Mail" type="email" value={invite.email} required
                onChange={e => setInvite(p => ({ ...p, email: e.target.value }))}
                data-testid="invite-email-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
              <input placeholder="Vollständiger Name" value={invite.full_name} required
                onChange={e => setInvite(p => ({ ...p, full_name: e.target.value }))}
                data-testid="invite-name-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
              <div>
                <select value={invite.role}
                  onChange={e => setInvite(p => ({ ...p, role: e.target.value }))}
                  data-testid="invite-role-select"
                  className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary">
                  {INVITABLE_ROLES.map(r => (
                    <option key={r} value={r}>{ROLE_LABELS[r] || r}</option>
                  ))}
                </select>
                {ROLE_DESCRIPTIONS[invite.role] && (
                  <p className="text-slate-500 text-xs mt-1 px-1">{ROLE_DESCRIPTIONS[invite.role]}</p>
                )}
              </div>
              <button type="submit" data-testid="invite-submit-btn"
                className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover">
                Einladungslink generieren
              </button>
            </form>
          )}
        </div>
      )}

      {/* Filter-Tabs */}
      <div className="flex items-center justify-between flex-wrap gap-2" data-testid="users-filter-tabs">
        <div className="flex items-center gap-2">
        {[
          { key: 'all', label: `Alle (${users.length})` },
          { key: 'staff_only', label: `Mitarbeiter (${staffUsers.length})` },
          { key: 'applicants', label: `Bewerber (${applicantUsers.length})` },
        ].map(tab => (
          <button key={tab.key} onClick={() => setFilterRole(tab.key)}
            data-testid={`users-tab-${tab.key}`}
            className={`text-xs px-3 py-1.5 rounded-sm font-medium transition-all ${
              filterRole === tab.key
                ? 'bg-primary text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}>
            {tab.label}
          </button>
        ))}
        </div>
        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-2.5 text-slate-400" />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Name, E-Mail, Rolle…"
            className="border border-slate-200 rounded-sm pl-8 pr-2.5 py-2 text-xs focus:outline-none focus:border-primary w-56"
            data-testid="users-search"
          />
        </div>
      </div>

      {/* Tabelle */}
      <div className="bg-white border border-slate-200 rounded-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr className="text-xs text-slate-500 font-medium">
                <th className="px-4 py-3 text-left">Name</th>
                <th className="px-4 py-3 text-left">E-Mail</th>
                <th className="px-4 py-3 text-left">Rolle</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Erstellt</th>
                <th className="px-4 py-3 text-left">Aktion</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-400 text-sm">Laden…</td></tr>
              ) : displayUsers.length === 0 ? (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-400 text-sm">Keine Nutzer gefunden</td></tr>
              ) : displayUsers.map(u => (
                <tr key={u.id} className="border-t border-slate-50 hover:bg-slate-50 transition-colors" data-testid={`user-row-${u.id}`}>
                  <td className="px-4 py-3 text-sm font-medium text-slate-800">{u.full_name || '–'}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{u.email}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2.5 py-1 rounded-sm ${STAFF_ROLES.includes(u.role) ? 'bg-primary/10 text-primary' : 'bg-slate-100 text-slate-600'}`}>
                      {ROLE_LABELS[u.role] || u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-sm ${u.active !== false ? 'bg-primary/10 text-primary' : 'bg-red-50 text-red-600'}`}>
                      {u.active !== false ? 'Aktiv' : 'Deaktiviert'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">{formatDate(u.created_at)}</td>
                  <td className="px-4 py-3">
                    {u.role !== 'superadmin' && (
                      <button
                        onClick={() => toggleActive(u.id, u.active !== false)}
                        disabled={updating === u.id}
                        data-testid={`toggle-user-${u.id}`}
                        className={`flex items-center gap-1 text-xs px-2.5 py-1 rounded-sm border transition-colors disabled:opacity-50 ${
                          u.active !== false
                            ? 'border-red-200 text-red-600 hover:bg-red-50'
                            : 'border-primary/30 text-primary hover:bg-primary/5'
                        }`}>
                        {u.active !== false
                          ? <><UserX size={12} /> Deaktivieren</>
                          : <><UserCheck size={12} /> Aktivieren</>}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
