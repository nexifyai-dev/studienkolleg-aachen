import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { UserCog, Save, Lock } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { InfoCard, ContentHeader } from '../../components/layout/BackstageComponents';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'sonner';
import { getLang } from '../../lib/utils';

export default function PartnerSettingsPage() {
  const { user } = useAuth();
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [form, setForm] = useState({ full_name: '', email: '', phone: '', company: '', language_pref: 'de' });
  const [pwForm, setPwForm] = useState({ current: '', newPw: '', confirm: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setForm({
        full_name: user.full_name || '', email: user.email || '',
        phone: user.phone || '', company: user.company || '',
        language_pref: user.language_pref || 'de',
      });
    }
  }, [user]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await apiClient.put(`/api/users/${user?.id}`, form);
      toast.success(lang === 'de' ? 'Profil aktualisiert' : 'Profile updated');
    } catch {
      toast.error(lang === 'de' ? 'Fehler beim Speichern' : 'Error saving');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async () => {
    if (pwForm.newPw !== pwForm.confirm) { toast.error(lang === 'de' ? 'Passwoerter stimmen nicht ueberein' : 'Passwords do not match'); return; }
    if (pwForm.newPw.length < 8) { toast.error(lang === 'de' ? 'Mindestens 8 Zeichen' : 'At least 8 characters'); return; }
    try {
      await apiClient.post('/api/auth/change-password', { current_password: pwForm.current, new_password: pwForm.newPw });
      toast.success(lang === 'de' ? 'Passwort geaendert' : 'Password changed');
      setPwForm({ current: '', newPw: '', confirm: '' });
    } catch {
      toast.error(lang === 'de' ? 'Passwort-Aenderung fehlgeschlagen' : 'Password change failed');
    }
  };

  const L = {
    settings: lang === 'de' ? 'Einstellungen' : 'Settings',
    profileSecurity: lang === 'de' ? 'Profil und Sicherheit' : 'Profile & Security',
    profile: lang === 'de' ? 'Profil' : 'Profile',
    name: lang === 'de' ? 'Name' : 'Name',
    email: 'E-Mail',
    phone: lang === 'de' ? 'Telefon' : 'Phone',
    company: lang === 'de' ? 'Firma' : 'Company',
    language: lang === 'de' ? 'Sprache' : 'Language',
    saveProfile: lang === 'de' ? 'Profil speichern' : 'Save Profile',
    saving: lang === 'de' ? 'Speichern...' : 'Saving...',
    changePw: lang === 'de' ? 'Passwort aendern' : 'Change Password',
    currentPw: lang === 'de' ? 'Aktuelles Passwort' : 'Current Password',
    newPw: lang === 'de' ? 'Neues Passwort' : 'New Password',
    confirmPw: lang === 'de' ? 'Bestaetigen' : 'Confirm',
  };

  return (
    <div className="space-y-6">
      <ContentHeader title={L.settings} subtitle={L.profileSecurity} />

      <InfoCard title={L.profile} icon={UserCog}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
          <div>
            <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{L.name}</label>
            <input data-testid="settings-name" type="text" value={form.full_name}
              onChange={e => setForm(p => ({ ...p, full_name: e.target.value }))}
              className="w-full text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2" />
          </div>
          <div>
            <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{L.email}</label>
            <input type="email" value={form.email} disabled
              className="w-full text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2 bg-gray-50 text-[var(--color-text-secondary)]" />
          </div>
          <div>
            <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{L.phone}</label>
            <input type="tel" value={form.phone}
              onChange={e => setForm(p => ({ ...p, phone: e.target.value }))}
              className="w-full text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2" />
          </div>
          <div>
            <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{L.company}</label>
            <input type="text" value={form.company}
              onChange={e => setForm(p => ({ ...p, company: e.target.value }))}
              className="w-full text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2" />
          </div>
          <div>
            <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{L.language}</label>
            <select value={form.language_pref}
              onChange={e => setForm(p => ({ ...p, language_pref: e.target.value }))}
              className="w-full text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2">
              <option value="de">Deutsch</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>
        <button data-testid="save-profile-btn" onClick={handleSave} disabled={saving}
          className="mt-4 flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-[var(--color-primary)] rounded-[var(--radius-sm)] hover:opacity-90 disabled:opacity-50">
          <Save size={14} /> {saving ? L.saving : L.saveProfile}
        </button>
      </InfoCard>

      <InfoCard title={L.changePw} icon={Lock}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
          <div>
            <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{L.currentPw}</label>
            <input type="password" value={pwForm.current}
              onChange={e => setPwForm(p => ({ ...p, current: e.target.value }))}
              className="w-full text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2" />
          </div>
          <div>
            <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{L.newPw}</label>
            <input type="password" value={pwForm.newPw}
              onChange={e => setPwForm(p => ({ ...p, newPw: e.target.value }))}
              className="w-full text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2" />
          </div>
          <div>
            <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{L.confirmPw}</label>
            <input type="password" value={pwForm.confirm}
              onChange={e => setPwForm(p => ({ ...p, confirm: e.target.value }))}
              className="w-full text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2" />
          </div>
        </div>
        <button onClick={handlePasswordChange}
          className="mt-4 flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-[var(--color-primary)] rounded-[var(--radius-sm)] hover:opacity-90">
          <Lock size={14} /> {L.changePw}
        </button>
      </InfoCard>
    </div>
  );
}
