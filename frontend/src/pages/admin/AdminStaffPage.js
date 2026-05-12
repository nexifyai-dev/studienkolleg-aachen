import React, { useState, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../../lib/api-hooks';
import apiClient from '../../lib/apiClient';
import { ROLE_LABELS, formatDate } from '../../lib/utils';
import {
  UserPlus, RefreshCw, UserCheck, UserX, Search, Pencil, X, Save,
  KeyRound, Copy, Loader2, ClipboardCheck, ListTodo, FileText, Calendar,
} from 'lucide-react';
import { toast } from 'sonner';
import { formatApiError } from '../../contexts/AuthContext';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';

const STAFF_ROLES = ['superadmin', 'admin', 'staff', 'accounting_staff', 'teacher'];
const EDITABLE_ROLES = ['admin', 'staff', 'accounting_staff', 'teacher'];
const INVITABLE_ROLES = ['staff', 'accounting_staff', 'teacher'];

function useStaffList() {
  return useQuery({
    queryKey: ['admin', 'staff'],
    queryFn: () => api.get('/admin/staff').then(r => r.data),
    staleTime: 30000,
  });
}

function EditStaffModal({ user: u, onClose, onSaved }) {
  const [form, setForm] = useState({
    full_name: u.full_name || '',
    role: u.role,
    phone: u.phone || '',
    active: u.active !== false,
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.put(`/api/users/${u.id}`, form, { withCredentials: true });
      toast.success('Mitarbeiter aktualisiert');
      onSaved();
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail) || 'Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w2g-modal-overlay" data-testid="edit-staff-modal" onClick={onClose}>
      <div className="w2g-modal max-w-md" onClick={e => e.stopPropagation()}>
        <div className="w2g-modal-header">
          <h2 className="text-lg font-bold text-[var(--color-primary)]">Mitarbeiter bearbeiten</h2>
          <button onClick={onClose} className="w2g-btn-icon"><X size={18} /></button>
        </div>
        <form onSubmit={handleSave} className="w2g-modal-body space-y-4">
          <div>
            <label className="w2g-label">E-Mail (nicht änderbar)</label>
            <input value={u.email} disabled className="w2g-input bg-[var(--color-surface-elevated)] text-[var(--color-text-secondary)] cursor-not-allowed" />
          </div>
          <div>
            <label className="w2g-label">Vollständiger Name</label>
            <input value={form.full_name} onChange={e => setForm(f => ({...f, full_name: e.target.value}))}
              className="w2g-input" data-testid="edit-staff-name" />
          </div>
          <div>
            <label className="w2g-label">Telefon</label>
            <input value={form.phone} onChange={e => setForm(f => ({...f, phone: e.target.value}))}
              className="w2g-input" placeholder="+49 ..." data-testid="edit-staff-phone" />
          </div>
          <div>
            <label className="w2g-label">Rolle</label>
            <select value={form.role} onChange={e => setForm(f => ({...f, role: e.target.value}))}
              className="w2g-select" data-testid="edit-staff-role" disabled={u.role === 'superadmin'}>
              {(u.role === 'superadmin' ? ['superadmin', ...EDITABLE_ROLES] : EDITABLE_ROLES).map(r =>
                <option key={r} value={r}>{ROLE_LABELS[r] || r}</option>
              )}
            </select>
            {u.role === 'superadmin' && <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1">Superadmin-Rolle ist geschützt.</p>}
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.active} onChange={e => setForm(f => ({...f, active: e.target.checked}))}
              className="rounded text-[var(--color-primary)]" disabled={u.role === 'superadmin'} />
            <span className="text-sm text-[var(--color-text-primary)]">Account aktiv</span>
          </label>
        </form>
        <div className="w2g-modal-footer">
          <button onClick={onClose} className="w2g-btn-secondary" type="button">Abbrechen</button>
          <button onClick={handleSave} disabled={saving} className="w2g-btn-primary" data-testid="save-staff-btn" type="button">
            <Save size={14} /> {saving ? 'Speichern...' : 'Speichern'}
          </button>
        </div>
      </div>
    </div>
  );
}

function ResetPasswordModal({ user: u, onClose }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const trigger = async () => {
    setLoading(true); setError('');
    try {
      const r = await apiClient.post(`/api/admin/staff/${u.id}/reset-password`, {}, { withCredentials: true });
      setResult(r.data);
      toast.success('Reset-Link erstellt – an Mitarbeiter weitergeben');
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail) || 'Fehler beim Erstellen des Links');
    } finally {
      setLoading(false);
    }
  };

  const copy = (text) => {
    navigator.clipboard.writeText(text).then(() => toast.success('In Zwischenablage kopiert'));
  };

  return (
    <div className="w2g-modal-overlay" data-testid="reset-password-modal" onClick={onClose}>
      <div className="w2g-modal max-w-md" onClick={e => e.stopPropagation()}>
        <div className="w2g-modal-header">
          <h2 className="text-lg font-bold text-[var(--color-primary)]">Passwort zurücksetzen</h2>
          <button onClick={onClose} className="w2g-btn-icon"><X size={18} /></button>
        </div>
        <div className="w2g-modal-body space-y-4">
          <div className="bg-[var(--color-surface-elevated)] rounded-md p-3">
            <p className="text-sm text-[var(--color-text-primary)] font-medium">{u.full_name}</p>
            <p className="text-xs text-[var(--color-text-secondary)]">{u.email}</p>
          </div>

          {!result ? (
            <>
              <p className="text-sm text-[var(--color-text-secondary)]">
                Es wird ein neuer Reset-Link generiert (24h gültig). Du kannst ihn dem Mitarbeiter direkt weiterleiten.
                Das alte Passwort bleibt bis zum erfolgreichen Reset gültig.
              </p>
              {error && <p className="text-sm text-[var(--color-danger)]">{error}</p>}
              <button onClick={trigger} disabled={loading} className="w2g-btn-primary" data-testid="trigger-reset-btn">
                {loading ? <Loader2 size={14} className="animate-spin" /> : <KeyRound size={14} />}
                Reset-Link generieren
              </button>
            </>
          ) : (
            <div className="space-y-2" data-testid="reset-result">
              <p className="text-xs font-medium text-[var(--color-success)]">Reset-Link erstellt (gültig 24h):</p>
              <div className="flex items-center gap-1">
                <code className="block flex-1 text-[11px] bg-[var(--color-surface-sunken)] p-2 rounded-md break-all">{result.reset_url}</code>
                <button onClick={() => copy(result.reset_url)} className="w2g-btn-icon" title="Kopieren" data-testid="copy-reset-url">
                  <Copy size={14} />
                </button>
              </div>
              <p className="text-[10px] text-[var(--color-text-tertiary)]">Token läuft ab: {new Date(result.expires_at).toLocaleString('de-DE')}</p>
            </div>
          )}
        </div>
        <div className="w2g-modal-footer">
          <button onClick={onClose} className="w2g-btn-secondary" type="button">{result ? 'Fertig' : 'Abbrechen'}</button>
        </div>
      </div>
    </div>
  );
}

function StatPill({ icon: Icon, label, value }) {
  return (
    <span className="inline-flex items-center gap-1 text-[10px] text-[var(--color-text-secondary)] bg-[var(--color-surface-sunken)] px-1.5 py-0.5 rounded-md tabular-nums">
      <Icon size={10} /> <span>{value}</span> <span className="text-[var(--color-text-tertiary)]">{label}</span>
    </span>
  );
}

export default function AdminStaffPage() {
  const qc = useQueryClient();
  const { data: list, isLoading, refetch } = useStaffList();
  const [showInvite, setShowInvite] = useState(false);
  const [invite, setInvite] = useState({ email: '', full_name: '', role: 'staff' });
  const [inviteResult, setInviteResult] = useState(null);
  const [inviteError, setInviteError] = useState('');
  const [search, setSearch] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [editUser, setEditUser] = useState(null);
  const [resetUser, setResetUser] = useState(null);
  const [updating, setUpdating] = useState(null);

  const filtered = useMemo(() => {
    const base = (list || []).filter(u => filterRole === 'all' ? true : u.role === filterRole);
    if (!search) return base;
    const q = search.toLowerCase();
    return base.filter(u =>
      (u.full_name || '').toLowerCase().includes(q) ||
      (u.email || '').toLowerCase().includes(q) ||
      (ROLE_LABELS[u.role] || u.role).toLowerCase().includes(q)
    );
  }, [list, filterRole, search]);

  const counts = useMemo(() => {
    const c = { all: (list || []).length };
    STAFF_ROLES.forEach(r => { c[r] = (list || []).filter(u => u.role === r).length; });
    return c;
  }, [list]);

  const toggleActive = async (u) => {
    setUpdating(u.id);
    try {
      await apiClient.put(`/api/users/${u.id}`, { active: !u.active }, { withCredentials: true });
      toast.success(!u.active ? 'Mitarbeiter aktiviert' : 'Mitarbeiter deaktiviert');
      qc.invalidateQueries({ queryKey: ['admin', 'staff'] });
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail) || 'Fehler');
    } finally {
      setUpdating(null);
    }
  };

  const handleInvite = async (e) => {
    e.preventDefault();
    setInviteError(''); setInviteResult(null);
    try {
      const res = await apiClient.post('/api/auth/invite', invite, { withCredentials: true });
      setInviteResult(res.data);
      toast.success('Einladung erstellt');
      qc.invalidateQueries({ queryKey: ['admin', 'staff'] });
    } catch (err) {
      setInviteError(formatApiError(err.response?.data?.detail) || 'Einladung fehlgeschlagen');
    }
  };

  return (
    <PageScaffold
      title="Mitarbeiter-Verwaltung"
      subtitle={`${counts.all || 0} Mitarbeiter · Rollen, Aktivität & Performance`}
      testId="admin-staff-page"
      actions={
        <div className="flex items-center gap-2">
          <button onClick={() => refetch()} className="w2g-btn-secondary" data-testid="staff-refresh-btn">
            <RefreshCw size={14} /> Aktualisieren
          </button>
          <button onClick={() => { setShowInvite(s => !s); setInviteResult(null); setInviteError(''); }}
            className="w2g-btn-primary" data-testid="invite-staff-btn">
            <UserPlus size={14} /> Mitarbeiter einladen
          </button>
        </div>
      }
      toolbar={
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72 shrink-0">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Mitarbeiter suchen..." className="w2g-search pl-9" data-testid="staff-search" />
            </div>
          }
          filters={[
            { key: 'all', label: `Alle (${counts.all || 0})` },
            ...STAFF_ROLES.filter(r => counts[r] > 0).map(r => ({ key: r, label: `${ROLE_LABELS[r] || r} (${counts[r]})` })),
          ].map(tab => (
            <button key={tab.key} onClick={() => setFilterRole(tab.key)} data-testid={`staff-tab-${tab.key}`}
              className={filterRole === tab.key ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}>
              {tab.label}
            </button>
          ))}
        />
      }
    >
      {showInvite && (
        <Card className="max-w-lg" data-testid="invite-staff-form">
          <CardContent className="p-5 space-y-3">
            <h3 className="font-semibold text-[var(--color-text-primary)]">Mitarbeiter einladen</h3>
            <p className="text-[var(--color-text-secondary)] text-xs">Es wird ein Einladungslink generiert. Der Mitarbeiter setzt sein eigenes Passwort.</p>
            {inviteError && <p className="text-[var(--color-danger)] text-sm">{inviteError}</p>}
            {inviteResult ? (
              <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] rounded-md p-3 text-sm" data-testid="invite-staff-result">
                <p className="font-medium text-[var(--color-text-primary)] mb-1">Einladungslink:</p>
                <code className="block text-[11px] bg-[var(--color-surface-sunken)] p-2 rounded-md break-all">{inviteResult.invite_url}</code>
                <button onClick={() => { setInviteResult(null); }} className="mt-2 text-xs text-[var(--color-primary)] hover:underline">Weiteren einladen</button>
              </div>
            ) : (
              <form onSubmit={handleInvite} className="space-y-3">
                <input placeholder="E-Mail" type="email" value={invite.email} required
                  onChange={e => setInvite(p => ({...p, email: e.target.value}))}
                  className="w2g-input" data-testid="invite-staff-email" />
                <input placeholder="Vollständiger Name" value={invite.full_name} required
                  onChange={e => setInvite(p => ({...p, full_name: e.target.value}))}
                  className="w2g-input" data-testid="invite-staff-name" />
                <select value={invite.role} onChange={e => setInvite(p => ({...p, role: e.target.value}))}
                  className="w2g-select" data-testid="invite-staff-role">
                  {INVITABLE_ROLES.map(r => <option key={r} value={r}>{ROLE_LABELS[r] || r}</option>)}
                </select>
                <button type="submit" className="w2g-btn-primary" data-testid="invite-staff-submit">Einladungslink generieren</button>
              </form>
            )}
          </CardContent>
        </Card>
      )}

      <Card className="p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w2g-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Rolle</th>
                <th>Kontakt</th>
                <th>Performance</th>
                <th>Letzter Login</th>
                <th>Status</th>
                <th className="text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={7} className="text-center py-8 text-[var(--color-text-tertiary)] text-sm">Laden...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-8 text-[var(--color-text-tertiary)] text-sm">{search ? 'Keine Treffer' : 'Keine Mitarbeiter gefunden'}</td></tr>
              ) : filtered.map(u => (
                <tr key={u.id} data-testid={`staff-row-${u.id}`}>
                  <td className="font-medium text-[var(--color-text-primary)]">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-[var(--color-primary-muted)] flex items-center justify-center text-[10px] font-bold text-[var(--color-primary)]">
                        {(u.full_name || u.email || '?').slice(0, 2).toUpperCase()}
                      </div>
                      <span>{u.full_name || '–'}</span>
                    </div>
                  </td>
                  <td>
                    <span className="w2g-badge bg-[#113655]/8 text-[var(--color-primary)]">{ROLE_LABELS[u.role] || u.role}</span>
                  </td>
                  <td className="text-xs text-[var(--color-text-secondary)]">
                    <div>{u.email}</div>
                    {u.phone && <div className="text-[10px]">{u.phone}</div>}
                  </td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      <StatPill icon={ListTodo} label="offen" value={u.stats?.tasks_open ?? 0} />
                      <StatPill icon={ClipboardCheck} label="erledigt" value={u.stats?.tasks_done ?? 0} />
                      <StatPill icon={FileText} label="Rechn." value={u.stats?.invoices_created ?? 0} />
                    </div>
                  </td>
                  <td className="text-xs text-[var(--color-text-secondary)]">
                    {u.last_login ? (
                      <span className="inline-flex items-center gap-1"><Calendar size={10} /> {formatDate(u.last_login)}</span>
                    ) : (
                      <span className="text-[var(--color-text-tertiary)]">Nie</span>
                    )}
                  </td>
                  <td>
                    <span className={`w2g-badge ${u.active !== false ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]' : 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]'}`}>
                      {u.active !== false ? 'Aktiv' : 'Deaktiviert'}
                    </span>
                  </td>
                  <td className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button onClick={() => setEditUser(u)} className="w2g-btn-icon" data-testid={`edit-staff-${u.id}`} title="Bearbeiten">
                        <Pencil size={14} />
                      </button>
                      <button onClick={() => setResetUser(u)} className="w2g-btn-icon" data-testid={`reset-staff-${u.id}`} title="Passwort zurücksetzen">
                        <KeyRound size={14} />
                      </button>
                      {u.role !== 'superadmin' && (
                        <button onClick={() => toggleActive(u)} disabled={updating === u.id}
                          data-testid={`toggle-staff-${u.id}`}
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

      {editUser && <EditStaffModal user={editUser} onClose={() => setEditUser(null)}
        onSaved={() => { setEditUser(null); qc.invalidateQueries({ queryKey: ['admin', 'staff'] }); }} />}
      {resetUser && <ResetPasswordModal user={resetUser} onClose={() => setResetUser(null)} />}
    </PageScaffold>
  );
}
