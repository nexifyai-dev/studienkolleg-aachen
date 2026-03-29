import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';
import { Loader2, CheckCircle } from 'lucide-react';

export default function PartnerSettingsPage() {
  const { t } = useTranslation();
  const { user, refreshUser } = useAuth();
  const [form, setForm] = useState({ full_name: user?.full_name || '', language_pref: user?.language_pref || 'de' });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSave = async e => {
    e.preventDefault();
    setLoading(true); setSuccess(false);
    try {
      await apiClient.put(`/api/users/${user.id}`, form, { withCredentials: true });
      await refreshUser();
      setSuccess(true);
    } catch {} finally { setLoading(false); }
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="partner-settings-page">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">{t('partner.settings')}</h1>
        <p className="text-slate-500 text-sm mt-1">{t('partner.settings_desc')}</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm p-6 max-w-lg">
        <form onSubmit={handleSave} className="space-y-4" data-testid="partner-settings-form">
          {success && (
            <div className="flex items-center gap-2 text-primary text-sm bg-primary/8 p-3 rounded-sm">
              <CheckCircle size={16} /> {t('portal.settings_saved')}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">{t('partner.org_name')}</label>
            <input value={form.full_name} onChange={e => setForm(p => ({...p, full_name: e.target.value}))}
              data-testid="partner-name-input"
              className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">{t('portal.settings_email_readonly')}</label>
            <input value={user?.email} disabled
              className="w-full border border-slate-100 rounded-sm px-3 py-2 text-sm bg-slate-50 text-slate-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">{t('portal.settings_language')}</label>
            <select value={form.language_pref} onChange={e => setForm(p => ({...p, language_pref: e.target.value}))}
              data-testid="partner-lang-select"
              className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary">
              <option value="de">Deutsch</option>
              <option value="en">English</option>
            </select>
          </div>
          <button type="submit" disabled={loading} data-testid="partner-save-btn"
            className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover disabled:opacity-60 flex items-center gap-2">
            {loading && <Loader2 size={16} className="animate-spin" />}
            {t('portal.settings_save')}
          </button>
        </form>
      </div>
    </div>
  );
}
