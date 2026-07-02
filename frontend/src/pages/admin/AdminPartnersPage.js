import React from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { api } from '../../lib/api-hooks';
import { Loader2, Search, Globe, UserPlus, Pencil, KeyRound, Copy, Power, X, Users, Euro } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

function Modal({ title, onClose, children, testId }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" data-testid={testId} onClick={onClose}>
      <div className="bg-[var(--color-surface)] rounded-[var(--radius-md)] shadow-xl w-full max-w-md p-5" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">{title}</h3>
          <button onClick={onClose} className="p-1 rounded hover:bg-[var(--color-surface-sunken)]" data-testid="modal-close-btn"><X size={16} /></button>
        </div>
        {children}
      </div>
    </div>
  );
}

const inputCls = "w-full text-xs rounded-[var(--radius-sm)] px-3 py-2 border border-[var(--color-divider)] bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-primary)]";

function InvitePartnerModal({ onClose, onDone }) {
  const [form, setForm] = React.useState({ email: '', full_name: '' });
  const [result, setResult] = React.useState(null);
  const [busy, setBusy] = React.useState(false);

  const submit = async () => {
    if (!form.email) return toast.error('E-Mail erforderlich');
    setBusy(true);
    try {
      const r = await api.post('/auth/invite', { ...form, role: 'affiliate' });
      setResult(r.data);
      onDone();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Einladung fehlgeschlagen');
    } finally { setBusy(false); }
  };

  return (
    <Modal title="Partner einladen" onClose={onClose} testId="invite-partner-modal">
      {result ? (
        <div className="space-y-3" data-testid="invite-partner-result">
          <p className="text-xs text-[var(--color-text-secondary)]">Einladung an <b>{result.email}</b> versendet. Link (7 Tage gültig):</p>
          <div className="flex items-start gap-2">
            <code className="block flex-1 text-[11px] bg-[var(--color-surface-sunken)] p-2 rounded-md break-all">{result.invite_url}</code>
            <button onClick={() => { navigator.clipboard.writeText(result.invite_url); toast.success('Kopiert'); }}
              className="p-2 rounded-md border border-[var(--color-divider)] hover:bg-[var(--color-surface-sunken)]" data-testid="copy-invite-url"><Copy size={13} /></button>
          </div>
          <button onClick={onClose} className="w2g-btn-primary w-full" data-testid="invite-done-btn">Fertig</button>
        </div>
      ) : (
        <div className="space-y-3">
          <input className={inputCls} placeholder="E-Mail *" value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })} data-testid="invite-partner-email" />
          <input className={inputCls} placeholder="Name" value={form.full_name}
            onChange={e => setForm({ ...form, full_name: e.target.value })} data-testid="invite-partner-name" />
          <button onClick={submit} disabled={busy} className="w2g-btn-primary w-full" data-testid="invite-partner-submit">
            {busy ? <Loader2 size={14} className="animate-spin" /> : 'Einladung senden'}
          </button>
        </div>
      )}
    </Modal>
  );
}

function EditPartnerModal({ partner, onClose, onDone }) {
  const [form, setForm] = React.useState({ full_name: partner.full_name || '', phone: partner.phone || '', active: partner.active !== false });
  const [busy, setBusy] = React.useState(false);

  const submit = async () => {
    setBusy(true);
    try {
      await api.put(`/users/${partner.id}`, form);
      toast.success('Partner aktualisiert');
      onDone(); onClose();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Speichern fehlgeschlagen');
    } finally { setBusy(false); }
  };

  return (
    <Modal title={`Partner bearbeiten – ${partner.email}`} onClose={onClose} testId="edit-partner-modal">
      <div className="space-y-3">
        <div>
          <label className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">Name</label>
          <input className={inputCls} value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} data-testid="edit-partner-name" />
        </div>
        <div>
          <label className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">Telefon</label>
          <input className={inputCls} value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} data-testid="edit-partner-phone" />
        </div>
        <label className="flex items-center gap-2 text-xs text-[var(--color-text-primary)] cursor-pointer">
          <input type="checkbox" checked={form.active} onChange={e => setForm({ ...form, active: e.target.checked })}
            className="accent-[#113655]" data-testid="edit-partner-active" />
          Aktiv (Login erlaubt)
        </label>
        <button onClick={submit} disabled={busy} className="w2g-btn-primary w-full" data-testid="edit-partner-save">
          {busy ? <Loader2 size={14} className="animate-spin" /> : 'Speichern'}
        </button>
      </div>
    </Modal>
  );
}

function ResetModal({ partner, onClose }) {
  const [result, setResult] = React.useState(null);
  const [busy, setBusy] = React.useState(false);

  const trigger = async () => {
    setBusy(true);
    try {
      const r = await api.post(`/admin/staff/${partner.id}/reset-password`, {});
      setResult(r.data);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Reset fehlgeschlagen');
    } finally { setBusy(false); }
  };

  return (
    <Modal title={`Passwort-Reset – ${partner.email}`} onClose={onClose} testId="partner-reset-modal">
      {result ? (
        <div className="space-y-3" data-testid="partner-reset-result">
          <p className="text-xs text-[var(--color-text-secondary)]">Reset-Link (24h gültig) – an Partner weiterleiten:</p>
          <div className="flex items-start gap-2">
            <code className="block flex-1 text-[11px] bg-[var(--color-surface-sunken)] p-2 rounded-md break-all">{result.reset_url}</code>
            <button onClick={() => { navigator.clipboard.writeText(result.reset_url); toast.success('Kopiert'); }}
              className="p-2 rounded-md border border-[var(--color-divider)] hover:bg-[var(--color-surface-sunken)]" data-testid="copy-partner-reset-url"><Copy size={13} /></button>
          </div>
          <button onClick={onClose} className="w2g-btn-primary w-full">Fertig</button>
        </div>
      ) : (
        <button onClick={trigger} disabled={busy} className="w2g-btn-primary w-full" data-testid="partner-reset-trigger">
          {busy ? <Loader2 size={14} className="animate-spin" /> : 'Reset-Link generieren'}
        </button>
      )}
    </Modal>
  );
}

export default function AdminPartnersPage() {
  const qc = useQueryClient();
  const { data: partners, isLoading } = useQuery({
    queryKey: ['admin', 'partners-overview'],
    queryFn: () => api.get('/admin/partners/overview').then(r => r.data),
    staleTime: 30000,
  });
  const [search, setSearch] = React.useState('');
  const [showInvite, setShowInvite] = React.useState(false);
  const [editP, setEditP] = React.useState(null);
  const [resetP, setResetP] = React.useState(null);

  const refresh = () => qc.invalidateQueries({ queryKey: ['admin', 'partners-overview'] });

  const toggleActive = async (p) => {
    try {
      await api.put(`/users/${p.id}`, { active: !(p.active !== false) });
      toast.success(p.active !== false ? 'Partner deaktiviert' : 'Partner aktiviert');
      refresh();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Fehler');
    }
  };

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-[var(--color-primary)]" />
    </div>
  );

  const list = (partners || []).filter(p => {
    const term = search.toLowerCase();
    return !term || (p.full_name || '').toLowerCase().includes(term) || (p.email || '').toLowerCase().includes(term);
  });

  const totals = list.reduce((acc, p) => ({
    referrals: acc.referrals + (p.referral_count || 0),
    enrolled: acc.enrolled + (p.enrolled_count || 0),
    commission: acc.commission + (p.commission_confirmed || 0),
  }), { referrals: 0, enrolled: 0, commission: 0 });

  return (
    <PageScaffold
      title="Partner-Verwaltung"
      subtitle={`${list.length} Partner · ${totals.referrals} Referrals · ${totals.enrolled} eingeschrieben`}
      testId="admin-partners-page"
      toolbar={
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
            <input
              type="text" value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Partner suchen..."
              className="w2g-search pl-9" data-testid="admin-partners-search"
            />
          </div>
          <button onClick={() => setShowInvite(true)}
            className="w2g-btn-primary flex items-center gap-1.5 text-xs" data-testid="invite-partner-btn">
            <UserPlus size={13} /> Partner einladen
          </button>
        </div>
      }
    >
      <div className="grid grid-cols-3 gap-3 mb-4">
        {[
          { label: 'Referrals gesamt', value: totals.referrals, icon: Users },
          { label: 'Eingeschrieben', value: totals.enrolled, icon: Globe },
          { label: 'Provision (bestätigt)', value: `${totals.commission.toFixed(0)} €`, icon: Euro },
        ].map(({ label, value, icon: Icon }) => (
          <Card key={label} className="p-3.5 flex items-center gap-3">
            <div className="w-8 h-8 rounded-[var(--radius-sm)] flex items-center justify-center bg-[var(--color-primary-muted)]">
              <Icon size={14} className="text-[var(--color-primary)]" />
            </div>
            <div>
              <div className="text-sm font-semibold text-[var(--color-text-primary)]">{value}</div>
              <div className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)]">{label}</div>
            </div>
          </Card>
        ))}
      </div>

      <Card className="overflow-hidden p-0">
        <table className="w-full" data-testid="admin-partners-table">
          <thead>
            <tr className="border-b border-[var(--color-divider)]">
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Partner</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5 hidden sm:table-cell">E-Mail</th>
              <th className="text-center text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-2 py-2.5">Referrals</th>
              <th className="text-center text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-2 py-2.5 hidden md:table-cell">Eingeschr.</th>
              <th className="text-right text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-2 py-2.5 hidden md:table-cell">Provision</th>
              <th className="text-left text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Status</th>
              <th className="text-right text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] px-4 py-2.5">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {list.map(p => (
              <tr key={p.id} className="border-b border-[var(--color-divider-subtle)] hover:bg-[var(--color-surface-sunken)] transition-colors"
                data-testid={`partner-row-${p.id}`}>
                <td className="px-4 py-2.5">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-[var(--radius-sm)] flex items-center justify-center bg-[var(--color-primary-muted)]">
                      <Globe size={12} className="text-[var(--color-accent)]" />
                    </div>
                    <span className="text-xs font-medium text-[var(--color-text-primary)]">{p.full_name || '—'}</span>
                  </div>
                </td>
                <td className="px-4 py-2.5 text-xs text-[var(--color-text-secondary)] hidden sm:table-cell">{p.email}</td>
                <td className="px-2 py-2.5 text-center text-xs font-semibold text-[var(--color-text-primary)]">{p.referral_count}</td>
                <td className="px-2 py-2.5 text-center text-xs text-[var(--color-success)] hidden md:table-cell">{p.enrolled_count}</td>
                <td className="px-2 py-2.5 text-right text-xs text-[var(--color-text-secondary)] hidden md:table-cell">
                  {(p.commission_confirmed || 0).toFixed(0)} €
                  {p.commission_pending > 0 && <span className="text-[var(--color-text-tertiary)]"> (+{p.commission_pending.toFixed(0)} offen)</span>}
                </td>
                <td className="px-4 py-2.5">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-medium rounded-[var(--radius-full)]
                    ${p.active !== false ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]' : 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]'}`}>
                    {p.active !== false ? 'Aktiv' : 'Inaktiv'}
                  </span>
                </td>
                <td className="px-4 py-2.5">
                  <div className="flex items-center justify-end gap-1">
                    <button onClick={() => setEditP(p)} title="Bearbeiten"
                      className="p-1.5 rounded-md text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-sunken)] transition-colors"
                      data-testid={`partner-edit-btn-${p.id}`}><Pencil size={13} /></button>
                    <button onClick={() => setResetP(p)} title="Passwort-Reset"
                      className="p-1.5 rounded-md text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-sunken)] transition-colors"
                      data-testid={`partner-reset-btn-${p.id}`}><KeyRound size={13} /></button>
                    <button onClick={() => toggleActive(p)} title={p.active !== false ? 'Deaktivieren' : 'Aktivieren'}
                      className={`p-1.5 rounded-md hover:bg-[var(--color-surface-sunken)] transition-colors ${p.active !== false ? 'text-[var(--color-danger)]' : 'text-[var(--color-success)]'}`}
                      data-testid={`partner-toggle-btn-${p.id}`}><Power size={13} /></button>
                  </div>
                </td>
              </tr>
            ))}
            {list.length === 0 && (
              <tr><td colSpan={7} className="text-center py-8 text-xs text-[var(--color-text-tertiary)]">Keine Partner gefunden</td></tr>
            )}
          </tbody>
        </table>
      </Card>

      {showInvite && <InvitePartnerModal onClose={() => setShowInvite(false)} onDone={refresh} />}
      {editP && <EditPartnerModal partner={editP} onClose={() => setEditP(null)} onDone={refresh} />}
      {resetP && <ResetModal partner={resetP} onClose={() => setResetP(null)} />}
    </PageScaffold>
  );
}
