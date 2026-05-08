import React, { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { ROLE_LABELS, formatDate, getRoleLabel, getLang } from '../../lib/utils';
import { UserPlus, RefreshCw, UserCheck, UserX, Search, Pencil, X, Save } from 'lucide-react';
import { toast } from 'sonner';
import { formatApiError } from '../../contexts/AuthContext';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

const STAFF_ROLES = ['superadmin', 'admin', 'staff', 'accounting_staff', 'agency_admin', 'agency_agent', 'affiliate'];
const INVITABLE_ROLES = ['staff', 'accounting_staff', 'agency_admin', 'agency_agent', 'affiliate'];
const ALL_ROLES = ['superadmin', 'admin', ...INVITABLE_ROLES, 'applicant', 'teacher'];

const ROLE_DESCRIPTIONS = {
  staff: 'Sachbearbeiter',
  accounting_staff: 'Buchhaltung',
  agency_admin: 'Agentur-Admin',
  agency_agent: 'Agentur-Agent',
  affiliate: 'Partner',
};

function EditUserModal({ user: u, onClose, onSaved }) {
  const [form, setForm] = useState({ full_name: u.full_name || '', role: u.role, active: u.active !== false });
  const [saving, setSaving] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.put(`/api/users/${u.id}`, form, { withCredentials: true });
      toast.success('Nutzer aktualisiert');
      onSaved();
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w2g-modal-overlay" data-testid="edit-user-modal">
      <div className="w2g-modal max-w-md">
        <div className="w2g-modal-header">
          <h2 className="text-lg font-bold text-[var(--color-primary)]">Nutzer bearbeiten</h2>
          <button onClick={onClose} className="w2g-btn-icon"><X size={18} /></button>
        </div>
        <form onSubmit={handleSave} className="w2g-modal-body space-y-4">
          <div>
            <label className="w2g-label">E-Mail</label>
            <input value={u.email} disabled className="w2g-input bg-[var(--color-surface-elevated)] text-[var(--color-text-secondary)] cursor-not-allowed" />
          </div>
          <div>
            <label className="w2g-label">Vollständiger Name</label>
            <input value={form.full_name} onChange={e => setForm(f => ({...f, full_name: e.target.value}))}
              className="w2g-input" data-testid="edit-user-name" />
          </div>
          <div>
            <label className="w2g-label">Rolle</label>
            <select value={form.role} onChange={e => setForm(f => ({...f, role: e.target.value}))}
              className="w2g-select" data-testid="edit-user-role" disabled={u.role === 'superadmin'}>
              {ALL_ROLES.map(r => <option key={r} value={r}>{ROLE_LABELS[r] || r}</option>)}
            </select>
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.active} onChange={e => setForm(f => ({...f, active: e.target.checked}))}
              className="rounded text-[var(--color-primary)]" disabled={u.role === 'superadmin'} />
            <span className="text-sm text-[var(--color-text-primary)]">Aktiv</span>
          </label>
        </form>
        <div className="w2g-modal-footer">
          <button onClick={onClose} className="w2g-btn-secondary">Abbrechen</button>
          <button onClick={handleSave} disabled={saving} className="w2g-btn-primary" data-testid="save-user-btn">
            <Save size={14} /> {saving ? 'Speichern...' : 'Speichern'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInvite, setShowInvite] = useState(false);
  const [invite, setInvite] = useState({ email: '', full_name: '', role: 'staff' });
  const [inviteResult, setInviteResult] = useState(null);
  const [error, setError] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [editUser, setEditUser] = useState(null);
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
      toast.success('Einladung erstellt');
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail));
    }
  };

  const toggleActive = async (userId, currentActive) => {
    setUpdating(userId);
    try {
      await apiClient.put(`/api/users/${userId}`, { active: !currentActive }, { withCredentials: true });
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, active: !currentActive } : u));
      toast.success(!currentActive ? 'Nutzer aktiviert' : 'Nutzer deaktiviert');
    } catch {}
    finally { setUpdating(null); }
  };

  const staffUsers = users.filter(u => STAFF_ROLES.includes(u.role));
  const applicantUsers = users.filter(u => u.role === 'applicant');

  const displayUsers = useMemo(() => {
    let base = filterRole === 'all' ? users : filterRole === 'staff_only' ? staffUsers : applicantUsers;
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      base = base.filter(u =>
        (u.full_name || '').toLowerCase().includes(q) ||
        (u.email || '').toLowerCase().includes(q) ||
        (ROLE_LABELS[u.role] || u.role).toLowerCase().includes(q)
      );
    }
    return base;
  }, [users, filterRole, searchTerm, staffUsers, applicantUsers]);

  return (
    <PageScaffold
      title="Nutzerverwaltung"
      subtitle={`${staffUsers.length} Mitarbeiter · ${applicantUsers.length} Bewerber`}
      testId="admin-users-page"
      actions={
        <div className="flex items-center gap-2">
          <button onClick={load} className="w2g-btn-secondary" data-testid="users-refresh-btn">
            <RefreshCw size={14} /> Aktualisieren
          </button>
          <button onClick={() => { setShowInvite(!showInvite); setInviteResult(null); setError(''); }}
            className="w2g-btn-primary" data-testid="invite-user-btn">
            <UserPlus size={14} /> Mitarbeiter einladen
          </button>
        </div>
      }
      toolbar={
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72 shrink-0">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
                placeholder="Nutzer suchen..." className="w2g-search pl-9" data-testid="users-search" />
            </div>
          }
          filters={[
            { key: 'all', label: `Alle (${users.length})` },
            { key: 'staff_only', label: `Mitarbeiter (${staffUsers.length})` },
            { key: 'applicants', label: `Bewerber (${applicantUsers.length})` },
          ].map(tab => (
            <button key={tab.key} onClick={() => setFilterRole(tab.key)} data-testid={`users-tab-${tab.key}`}
              className={filterRole === tab.key ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}>
              {tab.label}
            </button>
          ))}
        />
      }
    >
      {/* Invite Panel */}
      {showInvite && (
        <Card className="max-w-lg" data-testid="invite-form">
          <div className="p-5 space-y-3">
            <h3 className="font-semibold text-[var(--color-text-primary)] mb-1">Mitarbeiter einladen</h3>
            <p className="text-[var(--color-text-secondary)] text-xs mb-4">Generiere einen Einladungslink. Der neue Mitarbeiter setzt sein eigenes Passwort.</p>
            {error && <p className="text-[var(--color-danger)] text-sm mb-3">{error}</p>}
            {inviteResult ? (
              <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] rounded-[var(--radius-md)] p-4 text-sm" data-testid="invite-result">
                <p className="font-medium text-[var(--color-text-primary)] mb-1">Einladungslink erstellt:</p>
                <code className="block text-[var(--color-text-primary)] break-all text-xs bg-[var(--color-surface-sunken)] p-2 rounded-md">{inviteResult.invite_url}</code>
                <button onClick={() => setInviteResult(null)} className="mt-2 text-xs text-[var(--color-primary)] hover:underline">Weiteren einladen</button>
              </div>
            ) : (
              <form onSubmit={handleInvite} className="space-y-3">
                <input placeholder="E-Mail" type="email" value={invite.email} required
                  onChange={e => setInvite(p => ({ ...p, email: e.target.value }))}
                  data-testid="invite-email-input" className="w2g-input" />
                <input placeholder="Vollstaendiger Name" value={invite.full_name} required
                  onChange={e => setInvite(p => ({ ...p, full_name: e.target.value }))}
                  data-testid="invite-name-input" className="w2g-input" />
                <div>
                  <select value={invite.role} onChange={e => setInvite(p => ({ ...p, role: e.target.value }))}
                    data-testid="invite-role-select" className="w2g-select">
                    {INVITABLE_ROLES.map(r => <option key={r} value={r}>{ROLE_LABELS[r] || r}</option>)}
                  </select>
                  {ROLE_DESCRIPTIONS[invite.role] && <p className="text-[var(--color-text-secondary)] text-xs mt-1 px-1">{ROLE_DESCRIPTIONS[invite.role]}</p>}
                </div>
                <button type="submit" data-testid="invite-submit-btn" className="w2g-btn-primary">Einladungslink generieren</button>
              </form>
            )}
          </div>
        </Card>
      )}

      {/* Table */}
      <Card className="p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w2g-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>E-Mail</th>
                <th>Rolle</th>
                <th>Status</th>
                <th>Erstellt</th>
                <th className="text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="text-center py-8 text-[var(--color-text-tertiary)] text-sm">Laden...</td></tr>
              ) : displayUsers.length === 0 ? (
                <tr><td colSpan={6} className="text-center py-8 text-[var(--color-text-tertiary)] text-sm">{searchTerm ? 'Keine Treffer' : 'Keine Nutzer gefunden'}</td></tr>
              ) : displayUsers.map(u => (
                <tr key={u.id} data-testid={`user-row-${u.id}`}>
                  <td className="font-medium text-[var(--color-text-primary)]">{u.full_name || '\u2013'}</td>
                  <td className="text-[var(--color-text-secondary)]">{u.email}</td>
                  <td>
                    <span className={`w2g-badge ${STAFF_ROLES.includes(u.role) ? 'bg-[#113655]/8 text-[var(--color-primary)]' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
                      {ROLE_LABELS[u.role] || u.role}
                    </span>
                  </td>
                  <td>
                    <span className={`w2g-badge ${u.active !== false ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]' : 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]'}`}>
                      {u.active !== false ? 'Aktiv' : 'Deaktiviert'}
                    </span>
                  </td>
                  <td className="text-xs text-[var(--color-text-secondary)]">{formatDate(u.created_at)}</td>
                  <td className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button onClick={() => setEditUser(u)} className="w2g-btn-icon" data-testid={`edit-user-${u.id}`} title="Bearbeiten">
                        <Pencil size={14} />
                      </button>
                      {u.role !== 'superadmin' && (
                        <button onClick={() => toggleActive(u.id, u.active !== false)} disabled={updating === u.id}
                          data-testid={`toggle-user-${u.id}`}
                          className={`w2g-btn-icon ${u.active !== false ? 'hover:text-[var(--color-danger)]' : 'hover:text-[var(--color-success)]'}`}
                          title={u.active !== false ? 'Deaktivieren' : 'Aktivieren'}>
                          {u.active !== false ? <UserX size={14} /> : <UserCheck size={14} />}
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {editUser && <EditUserModal user={editUser} onClose={() => setEditUser(null)} onSaved={() => { setEditUser(null); load(); }} />}
    </PageScaffold>
  );
}
