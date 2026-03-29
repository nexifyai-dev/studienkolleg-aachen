import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useAuth, formatApiError } from '../../contexts/AuthContext';
import { Loader2, AlertCircle, GraduationCap } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function RegisterPage() {
  const { t } = useTranslation();
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get('token');

  const [form, setForm] = useState({ email: '', password: '', full_name: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    if (form.password.length < 8) { setError('Passwort muss mindestens 8 Zeichen haben.'); return; }
    setLoading(true); setError('');
    try {
      const payload = { ...form, invite_token: inviteToken || undefined };
      const { data } = await axios.post(`${API}/api/auth/register`, payload, { withCredentials: true });
      setUser(data);
      const staffRoles = ['superadmin', 'admin', 'staff', 'accounting_staff'];
      navigate(staffRoles.includes(data.role) ? '/staff' : '/portal');
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail) || 'Registrierung fehlgeschlagen.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brand-bg flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 bg-primary rounded-sm flex items-center justify-center">
              <GraduationCap size={20} className="text-white" />
            </div>
            <span className="font-heading font-bold text-primary text-lg">Studienkolleg Aachen</span>
          </Link>
          <h1 className="text-2xl font-heading font-bold text-primary">{t('auth.register_title')}</h1>
          {inviteToken && <p className="text-xs text-green-600 mt-1 bg-green-50 px-2 py-1 rounded-sm">Einladungstoken aktiv</p>}
        </div>

        <div className="bg-white border border-slate-200 rounded-sm shadow-card p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-sm p-3 flex items-center gap-2 text-red-700 text-sm mb-4" data-testid="register-error">
              <AlertCircle size={16} /> {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4" data-testid="register-form">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('auth.name')}</label>
              <input type="text" value={form.full_name} onChange={e => setForm(p => ({...p, full_name: e.target.value}))}
                required placeholder="Dein vollständiger Name" data-testid="register-name-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('auth.email')}</label>
              <input type="email" value={form.email} onChange={e => setForm(p => ({...p, email: e.target.value}))}
                required placeholder="deine@email.de" data-testid="register-email-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('auth.password')}</label>
              <input type="password" value={form.password} onChange={e => setForm(p => ({...p, password: e.target.value}))}
                required placeholder="Min. 8 Zeichen" data-testid="register-password-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
            </div>
            <button type="submit" disabled={loading} data-testid="register-submit-btn"
              className="w-full bg-primary text-white font-semibold py-3 rounded-sm hover:bg-primary-hover transition-colors disabled:opacity-60 flex items-center justify-center gap-2">
              {loading && <Loader2 size={18} className="animate-spin" />}
              {t('auth.register_btn')}
            </button>
          </form>
          <p className="mt-4 text-center text-sm text-slate-500">
            {t('auth.have_account')}{' '}
            <Link to="/auth/login" className="text-primary font-medium hover:underline">{t('auth.login_link')}</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
