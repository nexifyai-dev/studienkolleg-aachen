import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';
import { Loader2, User, Mail, Globe, CheckCircle, AlertCircle, Shield } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

function ProfileCompleteness({ user, lang }) {
  const fields = [
    { key: 'full_name', label: lang === 'de' ? 'Name' : 'Name', filled: !!user?.full_name },
    { key: 'email', label: 'E-Mail', filled: !!user?.email },
    { key: 'language_pref', label: lang === 'de' ? 'Sprache' : 'Language', filled: !!user?.language_pref },
  ];
  const filled = fields.filter(f => f.filled).length;
  const percent = Math.round((filled / fields.length) * 100);

  return (
    <div className="w2g-panel" data-testid="profile-completeness">
      <div className="flex items-center justify-between mb-3">
        <h3 className="w2g-section-title">
          <User size={14} className="text-primary" />
          {lang === 'de' ? 'Profilvollstaendigkeit' : 'Profile Completeness'}
        </h3>
        <span className={`text-xs font-bold ${percent === 100 ? 'text-[var(--color-success)]' : 'text-[var(--color-warning)]'}`}>
          {percent}%
        </span>
      </div>
      <div className="h-1.5 bg-[var(--color-surface-sunken)] rounded-full overflow-hidden mb-3">
        <div className={`h-full rounded-full transition-all duration-700 ${percent === 100 ? 'bg-[var(--color-success)]' : 'bg-primary'}`}
          style={{ width: `${percent}%` }} />
      </div>
      <div className="space-y-1.5">
        {fields.map(f => (
          <div key={f.key} className="flex items-center gap-2 text-xs">
            {f.filled ? (
              <CheckCircle size={12} className="text-[var(--color-success)]" />
            ) : (
              <AlertCircle size={12} className="text-[var(--color-warning)]" />
            )}
            <span className={f.filled ? 'text-[var(--color-text-secondary)]' : 'text-[var(--color-text-primary)] font-medium'}>{f.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const { i18n } = useTranslation();
  const { user, refreshUser } = useAuth();
  const [form, setForm] = useState({ full_name: '', language_pref: 'de' });
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const lang = i18n.language === 'en' ? 'en' : 'de';

  useEffect(() => {
    if (user) {
      setForm({ full_name: user.full_name || '', language_pref: user.language_pref || 'de' });
    }
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSaved(false);
    try {
      await apiClient.put('/api/auth/me', form, { withCredentials: true });
      if (refreshUser) await refreshUser();
      i18n.changeLanguage(form.language_pref);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  return (
    <PageScaffold
      title={lang === 'de' ? 'Einstellungen' : 'Settings'}
      subtitle={lang === 'de' ? 'Verwalte dein Profil und deine Praeferenzen' : 'Manage your profile and preferences'}
      testId="settings-page"
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Profile Form */}
        <div className="lg:col-span-2">
          <Card className="p-6" data-testid="settings-form-card">
            <h3 className="w2g-section-title mb-4">
              <User size={14} className="text-primary" />
              {lang === 'de' ? 'Persoenliche Daten' : 'Personal Information'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="w2g-label">{lang === 'de' ? 'Vollstaendiger Name' : 'Full Name'}</label>
                <input value={form.full_name} onChange={e => setForm(p => ({...p, full_name: e.target.value}))}
                  data-testid="settings-name-input" className="w2g-input" />
              </div>
              <div>
                <label className="w2g-label">
                  <Mail size={12} className="inline mr-1" />
                  {lang === 'de' ? 'E-Mail (nicht aenderbar)' : 'Email (read-only)'}
                </label>
                <input value={user?.email || ''} disabled className="w2g-input bg-[var(--color-surface-elevated)] text-[var(--color-text-secondary)]" />
              </div>
              <div>
                <label className="w2g-label">
                  <Globe size={12} className="inline mr-1" />
                  {lang === 'de' ? 'Sprache' : 'Language'}
                </label>
                <select value={form.language_pref} onChange={e => setForm(p => ({...p, language_pref: e.target.value}))}
                  data-testid="settings-lang-select" className="w2g-select">
                  <option value="de">Deutsch</option>
                  <option value="en">English</option>
                </select>
                <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1">
                  {lang === 'de'
                    ? 'Aendert die Sprache der gesamten Plattform fuer dich.'
                    : 'Changes the language of the entire platform for you.'}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button type="submit" disabled={loading} data-testid="settings-save-btn"
                  className="w2g-btn-primary">
                  {loading && <Loader2 size={16} className="animate-spin" />}
                  {lang === 'de' ? 'Speichern' : 'Save'}
                </button>
                {saved && (
                  <span className="text-xs text-[var(--color-success)] flex items-center gap-1">
                    <CheckCircle size={12} />
                    {lang === 'de' ? 'Gespeichert' : 'Saved'}
                  </span>
                )}
              </div>
            </form>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <ProfileCompleteness user={user} lang={lang} />

          {/* Data Info */}
          <Card className="p-4" data-testid="settings-data-info">
            <h3 className="w2g-section-title mb-2">
              <Shield size={14} className="text-primary" />
              {lang === 'de' ? 'Datenschutz' : 'Privacy'}
            </h3>
            <p className="text-xs text-[var(--color-text-secondary)]">
              {lang === 'de'
                ? 'Deine Daten werden ausschliesslich fuer die Bearbeitung deiner Bewerbung verwendet. Weitere Informationen findest du in unserer Datenschutzerklaerung.'
                : 'Your data is used exclusively for processing your application. For more information, see our privacy policy.'}
            </p>
          </Card>
        </div>
      </div>
    </PageScaffold>
  );
}
