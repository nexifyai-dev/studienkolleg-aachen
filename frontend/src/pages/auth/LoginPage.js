import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, formatApiError } from '../../contexts/AuthContext';
import { Loader2, AlertCircle, GraduationCap } from 'lucide-react';

export default function LoginPage() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const user = await login(form.email, form.password);
      const staffRoles = ['superadmin', 'admin', 'staff', 'accounting_staff', 'teacher'];
      if (staffRoles.includes(user.role)) navigate('/staff');
      else if (user.role === 'affiliate') navigate('/partner');
      else navigate('/portal');
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail) || 'Anmeldung fehlgeschlagen.');
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
          <h1 className="text-2xl font-heading font-bold text-primary">{t('auth.login_title')}</h1>
        </div>

        <div className="bg-white border border-slate-200 rounded-sm shadow-card p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-sm p-3 flex items-center gap-2 text-red-700 text-sm mb-4" data-testid="login-error">
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4" data-testid="login-form">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('auth.email')}</label>
              <input type="email" value={form.email} onChange={e => setForm(p => ({...p, email: e.target.value}))}
                required placeholder="deine@email.de" data-testid="login-email-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-sm font-medium text-slate-700">{t('auth.password')}</label>
                <Link to="/auth/forgot-password" className="text-xs text-primary hover:underline">{t('auth.forgot_pw')}</Link>
              </div>
              <input type="password" value={form.password} onChange={e => setForm(p => ({...p, password: e.target.value}))}
                required placeholder="••••••••" data-testid="login-password-input"
                className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
            </div>
            <button type="submit" disabled={loading} data-testid="login-submit-btn"
              className="w-full bg-primary text-white font-semibold py-3 rounded-sm hover:bg-primary-hover transition-colors disabled:opacity-60 flex items-center justify-center gap-2">
              {loading && <Loader2 size={18} className="animate-spin" />}
              {t('auth.login_btn')}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-slate-500">
            {t('auth.no_account')}{' '}
            <Link to="/auth/register" className="text-primary font-medium hover:underline">{t('auth.register_link')}</Link>
          </p>
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">
          <Link to="/" className="hover:text-primary">{t('auth.back_to_site')}</Link>
        </p>
      </div>
    </div>
  );
}
