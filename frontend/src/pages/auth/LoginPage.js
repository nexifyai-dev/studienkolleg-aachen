import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, formatApiError } from '../../contexts/AuthContext';
import { Loader2, AlertCircle, GraduationCap, ArrowRight, Shield, BookOpen, CheckCircle } from 'lucide-react';

export default function LoginPage() {
  const { t, i18n } = useTranslation();
  const isEN = i18n.language === 'en';
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
      const adminRoles = ['superadmin', 'admin'];
      const staffRoles = ['staff', 'accounting_staff', 'teacher'];
      if (adminRoles.includes(user.role)) navigate('/admin');
      else if (staffRoles.includes(user.role)) navigate('/staff');
      else if (user.role === 'affiliate') navigate('/partner');
      else navigate('/portal');
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail) || (isEN ? 'Login failed.' : 'Anmeldung fehlgeschlagen.'));
    } finally {
      setLoading(false);
    }
  };

  const features = [
    { text: isEN ? 'Track your application status in real-time' : 'Bewerbungsstatus in Echtzeit verfolgen' },
    { text: isEN ? 'Upload & manage documents securely' : 'Dokumente sicher hochladen & verwalten' },
    { text: isEN ? 'Direct communication with our team' : 'Direkte Kommunikation mit unserem Team' },
    { text: isEN ? 'View invoices & payment history' : 'Rechnungen & Zahlungsverlauf einsehen' },
  ];

  return (
    <div className="min-h-screen flex" data-testid="login-page">

      {/* Left: Brand Panel */}
      <div className="hidden lg:flex lg:w-[480px] xl:w-[520px] shrink-0 flex-col justify-between p-10 xl:p-12 w2g-auth-panel">
        <div className="relative z-10">
          <Link to="/" className="inline-flex items-center gap-3 group mb-16" data-testid="login-logo-link">
            <div className="w-10 h-10 rounded-[var(--radius-sm)] flex items-center justify-center bg-[rgba(212,175,55,0.15)]">
              <GraduationCap size={20} className="text-[var(--color-accent)]" />
            </div>
            <span className="text-[16px] font-bold text-white font-heading">
              Studienkolleg Aachen
            </span>
          </Link>

          <h2 className="text-[28px] xl:text-[32px] font-extrabold text-white leading-[1.15] tracking-[-0.025em] mb-4 font-heading">
            {isEN ? 'Your Portal to Study in Germany' : 'Dein Portal zum Studium in Deutschland'}
          </h2>
          <p className="text-[15px] text-white/40 leading-[1.7] mb-10 max-w-[360px]">
            {isEN
              ? 'Access your personal dashboard, track your application progress, and manage your documents.'
              : 'Zugriff auf dein persoenliches Dashboard, Bewerbungsfortschritt und Dokumentenverwaltung.'}
          </p>

          <div className="space-y-4">
            {features.map((f, i) => (
              <div key={i} className="flex items-center gap-3">
                <CheckCircle size={16} className="text-[var(--color-accent)]" />
                <span className="text-[14px] text-white/60">{f.text}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 pt-8 border-t border-white/10">
          <p className="text-[11px] text-white/25">
            &copy; {new Date().getFullYear()} W2G Academy GmbH &middot; Studienkolleg Aachen
          </p>
        </div>
      </div>

      {/* Right: Login Form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 lg:px-12 bg-[var(--color-surface)]">
        <div className="w-full max-w-[400px]">

          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <Link to="/" className="inline-flex items-center gap-2.5 mb-4 group">
              <div className="w-9 h-9 rounded-[var(--radius-sm)] flex items-center justify-center bg-[rgba(212,175,55,0.15)]">
                <GraduationCap size={18} className="text-[var(--color-accent)]" />
              </div>
              <span className="text-[15px] font-bold text-[var(--color-primary-dark)] font-heading">
                Studienkolleg Aachen
              </span>
            </Link>
          </div>

          <div className="mb-8">
            <h1 className="text-[24px] sm:text-[28px] font-extrabold text-[var(--color-primary-dark)] tracking-[-0.025em] mb-2 font-heading">
              {t('auth.login_title')}
            </h1>
            <p className="text-[14px] text-[var(--color-text-secondary)]">
              {t('auth.login_subtitle') || (isEN ? 'Sign in to your portal' : 'Melde dich in deinem Portal an')}
            </p>
          </div>

          {error && (
            <div className="w2g-auth-error" data-testid="login-error">
              <AlertCircle size={16} className="shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5" data-testid="login-form">
            <div>
              <label className="w2g-auth-label">{t('auth.email')}</label>
              <input type="email" value={form.email} onChange={e => setForm(p => ({...p, email: e.target.value}))}
                required placeholder={isEN ? 'your@email.com' : 'deine@email.de'} data-testid="login-email-input"
                className="w2g-auth-input" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="w2g-auth-label" style={{ marginBottom: 0 }}>{t('auth.password')}</label>
                <Link to="/auth/forgot-password" className="text-[11px] font-medium text-[var(--color-accent)] hover:underline">
                  {t('auth.forgot_pw')}
                </Link>
              </div>
              <input type="password" value={form.password} onChange={e => setForm(p => ({...p, password: e.target.value}))}
                required placeholder="••••••••" data-testid="login-password-input"
                className="w2g-auth-input" />
            </div>
            <button type="submit" disabled={loading} data-testid="login-submit-btn"
              className="w2g-auth-btn">
              {loading && <Loader2 size={18} className="animate-spin" />}
              {t('auth.login_btn')} {!loading && <ArrowRight size={14} />}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-[var(--color-divider)]">
            <p className="text-center text-[13px] text-[var(--color-text-secondary)]">
              {t('auth.no_account')}{' '}
              <Link to="/apply" className="font-semibold text-[var(--color-primary)] hover:underline">
                {t('auth.register_link') || (isEN ? 'Apply Now' : 'Jetzt bewerben')}
              </Link>
            </p>
          </div>

          <div className="mt-8 flex items-center justify-center gap-5 text-[11px] text-[var(--color-text-tertiary)]">
            <span className="flex items-center gap-1"><Shield size={11} /> SSL</span>
            <span className="flex items-center gap-1"><BookOpen size={11} /> DSGVO</span>
          </div>

          <p className="mt-4 text-center text-[11px] text-[var(--color-text-tertiary)]">
            <Link to="/" className="hover:text-[var(--color-primary-dark)] transition-colors">{t('auth.back_to_site')}</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
