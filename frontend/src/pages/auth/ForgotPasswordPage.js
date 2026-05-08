import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { formatApiError } from '../../contexts/AuthContext';
import { Loader2, AlertCircle, CheckCircle, GraduationCap, ArrowLeft, ArrowRight, Shield } from 'lucide-react';

export default function ForgotPasswordPage() {
  const { t, i18n } = useTranslation();
  const isEN = i18n.language === 'en';
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      await apiClient.post(`/api/auth/forgot-password`, { email });
      setSuccess(true);
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex" data-testid="forgot-password-page">

      {/* Left: Brand Panel */}
      <div className="hidden lg:flex lg:w-[480px] xl:w-[520px] shrink-0 flex-col justify-between p-10 xl:p-12 w2g-auth-panel">
        <div className="relative z-10">
          <Link to="/" className="inline-flex items-center gap-3 group mb-16">
            <div className="w-10 h-10 rounded-[var(--radius-sm)] flex items-center justify-center bg-[rgba(212,175,55,0.15)]">
              <GraduationCap size={20} className="text-[var(--color-accent)]" />
            </div>
            <span className="text-[16px] font-bold text-white font-heading">
              Studienkolleg Aachen
            </span>
          </Link>
          <h2 className="text-[28px] xl:text-[32px] font-extrabold text-white leading-[1.15] tracking-[-0.025em] mb-4 font-heading">
            {isEN ? 'Secure Account Recovery' : 'Sicheres Konto wiederherstellen'}
          </h2>
          <p className="text-[15px] text-white/40 leading-[1.7] max-w-[360px]">
            {isEN
              ? 'Enter your email address and we will send you a link to reset your password.'
              : 'Gib deine E-Mail-Adresse ein und wir senden dir einen Link zum Zuruecksetzen deines Passworts.'}
          </p>
        </div>
        <div className="relative z-10 pt-8 border-t border-white/8">
          <p className="text-[11px] text-white/25">
            &copy; {new Date().getFullYear()} W2G Academy GmbH
          </p>
        </div>
      </div>

      {/* Right: Form */}
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

          {success ? (
            <div className="text-center" data-testid="forgot-success">
              <div className="w-16 h-16 mx-auto mb-6 rounded-full flex items-center justify-center bg-[var(--color-accent-muted)]">
                <CheckCircle size={32} className="text-[var(--color-accent)]" />
              </div>
              <h2 className="text-[22px] font-extrabold text-[var(--color-primary-dark)] mb-2 font-heading">
                {t('auth.forgot_success_title') || (isEN ? 'Email Sent' : 'E-Mail gesendet')}
              </h2>
              <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7] mb-8 max-w-[320px] mx-auto">
                {t('auth.forgot_success_msg') || (isEN
                  ? 'If this email address exists, a reset link has been sent. Please also check your spam folder.'
                  : 'Wenn diese E-Mail-Adresse existiert, wurde ein Reset-Link gesendet. Bitte pruefe auch deinen Spam-Ordner.')}
              </p>
              <Link to="/auth/login" className="w2g-auth-btn inline-flex w-auto px-6">
                <ArrowLeft size={14} /> {t('auth.back_to_login') || (isEN ? 'Back to Login' : 'Zurueck zur Anmeldung')}
              </Link>
            </div>
          ) : (
            <>
              <div className="mb-8">
                <h1 className="text-[24px] sm:text-[28px] font-extrabold text-[var(--color-primary-dark)] tracking-[-0.025em] mb-2 font-heading">
                  {t('auth.forgot_title') || (isEN ? 'Forgot Password' : 'Passwort vergessen')}
                </h1>
                <p className="text-[14px] text-[var(--color-text-secondary)]">
                  {t('auth.forgot_subtitle') || (isEN ? 'We will send you a reset link' : 'Wir senden dir einen Link zum Zuruecksetzen')}
                </p>
              </div>

              {error && (
                <div className="w2g-auth-error" data-testid="forgot-error">
                  <AlertCircle size={16} className="shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5" data-testid="forgot-form">
                <div>
                  <label className="w2g-auth-label">
                    {t('auth.email') || 'E-Mail-Adresse'}
                  </label>
                  <input type="email" value={email} onChange={e => setEmail(e.target.value)} required data-testid="forgot-email-input"
                    className="w2g-auth-input"
                    placeholder={isEN ? 'your@email.com' : 'deine@email.de'} />
                </div>
                <button type="submit" disabled={loading} data-testid="forgot-submit-btn"
                  className="w2g-auth-btn">
                  {loading && <Loader2 size={18} className="animate-spin" />}
                  {t('auth.forgot_submit') || (isEN ? 'Send Reset Link' : 'Reset-Link senden')}
                  {!loading && <ArrowRight size={14} />}
                </button>
              </form>

              <p className="mt-6 text-center">
                <Link to="/auth/login" className="text-[13px] font-medium text-[var(--color-primary)] hover:underline inline-flex items-center gap-1.5">
                  <ArrowLeft size={14} /> {t('auth.back_to_login') || (isEN ? 'Back to Login' : 'Zurueck zur Anmeldung')}
                </Link>
              </p>
            </>
          )}

          <div className="mt-8 flex items-center justify-center gap-5 text-[11px] text-[var(--color-text-tertiary)]">
            <span className="flex items-center gap-1"><Shield size={11} /> SSL + DSGVO</span>
          </div>
        </div>
      </div>
    </div>
  );
}
