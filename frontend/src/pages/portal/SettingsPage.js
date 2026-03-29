import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';
import { Loader2, CheckCircle } from 'lucide-react';
import { formatApiError } from '../../contexts/AuthContext';


export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const [form, setForm] = useState({ full_name: user?.full_name || '', language_pref: user?.language_pref || 'de' });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async e => {
    e.preventDefault();
    setLoading(true); setError(''); setSuccess(false);
    try {
      await apiClient.put(`/api/users/${user.id}`, form, { withCredentials: true });
      await refreshUser();
      setSuccess(true);
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="settings-page">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">Einstellungen</h1>
        <p className="text-slate-500 text-sm mt-1">Dein Profil und Präferenzen</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm p-6 max-w-lg">
        <h3 className="font-semibold text-slate-800 mb-4">Profildaten</h3>
        <form onSubmit={handleSave} className="space-y-4" data-testid="settings-form">
          {error && <p className="text-red-600 text-sm">{error}</p>}
          {success && (
            <div className="flex items-center gap-2 text-green-700 text-sm bg-green-50 p-3 rounded-sm" data-testid="settings-success">
              <CheckCircle size={16} /> Gespeichert
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Vollständiger Name</label>
            <input value={form.full_name} onChange={e => setForm(p => ({...p, full_name: e.target.value}))}
              data-testid="settings-name-input"
              className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">E-Mail (nicht änderbar)</label>
            <input value={user?.email} disabled
              className="w-full border border-slate-100 rounded-sm px-3 py-2 text-sm bg-slate-50 text-slate-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Bevorzugte Sprache</label>
            <select value={form.language_pref} onChange={e => setForm(p => ({...p, language_pref: e.target.value}))}
              data-testid="settings-lang-select"
              className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary">
              <option value="de">Deutsch</option>
              <option value="en">English</option>
            </select>
          </div>
          <button type="submit" disabled={loading} data-testid="settings-save-btn"
            className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover disabled:opacity-60 flex items-center gap-2">
            {loading && <Loader2 size={16} className="animate-spin" />}
            Speichern
          </button>
        </form>
      </div>
    </div>
  );
}
