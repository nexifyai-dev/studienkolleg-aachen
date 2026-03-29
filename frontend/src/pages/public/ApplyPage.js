import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import { formatApiError } from '../../contexts/AuthContext';
import { CheckCircle, Loader2, AlertCircle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const AREAS = [
  { value: 'studienkolleg', label: 'Studienkolleg (T/M/W-Kurs)' },
  { value: 'language_courses', label: 'Sprachkurse (A1-B2)' },
  { value: 'nursing', label: 'Pflegefachschule' },
  { value: 'work_training', label: 'Arbeit & Ausbildung' },
];

const LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'Noch keins'];

export default function ApplyPage() {
  const { t } = useTranslation();
  const [form, setForm] = useState({
    full_name: '', email: '', phone: '', country: '',
    area_interest: 'studienkolleg', desired_start: '', language_level: '', notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleChange = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await axios.post(`${API}/api/leads/ingest`, { ...form, source: 'website_form' });
      setSuccess(true);
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail) || 'Fehler beim Absenden.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <PublicNav />
      <main className="pt-16">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-16">
          <div className="text-center mb-10">
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-primary mb-3">{t('apply.title')}</h1>
            <p className="text-slate-600">{t('apply.sub')}</p>
          </div>

          {success ? (
            <div className="bg-green-50 border border-green-200 rounded-sm p-8 text-center" data-testid="apply-success">
              <CheckCircle size={40} className="text-green-500 mx-auto mb-4" />
              <h3 className="font-semibold text-green-800 text-lg mb-2">Bewerbung eingegangen!</h3>
              <p className="text-green-700 text-sm">{t('apply.success')}</p>
              <Link to="/" className="mt-6 inline-block text-primary font-medium hover:underline text-sm">
                Zurück zur Startseite
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-sm shadow-card p-6 sm:p-8 space-y-5"
              data-testid="apply-form">
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-sm p-3 flex items-center gap-2 text-red-700 text-sm" data-testid="apply-error">
                  <AlertCircle size={16} /> {error}
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">{t('apply.name')} *</label>
                  <input name="full_name" value={form.full_name} onChange={handleChange} required
                    data-testid="apply-input-name"
                    className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">{t('apply.email')} *</label>
                  <input name="email" type="email" value={form.email} onChange={handleChange} required
                    data-testid="apply-input-email"
                    className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">{t('apply.phone')}</label>
                  <input name="phone" value={form.phone} onChange={handleChange}
                    data-testid="apply-input-phone"
                    className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">{t('apply.country')}</label>
                  <input name="country" value={form.country} onChange={handleChange}
                    data-testid="apply-input-country"
                    className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">{t('apply.area')} *</label>
                <select name="area_interest" value={form.area_interest} onChange={handleChange} required
                  data-testid="apply-select-area"
                  className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary">
                  {AREAS.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">{t('apply.start')}</label>
                  <input name="desired_start" value={form.desired_start} onChange={handleChange} placeholder="z.B. Sommersemester 2026"
                    data-testid="apply-input-start"
                    className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">{t('apply.level')}</label>
                  <select name="language_level" value={form.language_level} onChange={handleChange}
                    data-testid="apply-select-level"
                    className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary">
                    <option value="">-- Bitte wählen --</option>
                    {LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Anmerkungen</label>
                <textarea name="notes" value={form.notes} onChange={handleChange} rows={3}
                  data-testid="apply-textarea-notes"
                  className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 resize-none" />
              </div>

              <p className="text-xs text-slate-500">{t('apply.privacy')} – <Link to="/privacy" className="underline">Datenschutzerklärung</Link></p>

              <button type="submit" disabled={loading} data-testid="apply-submit-btn"
                className="w-full bg-primary text-white font-semibold py-3.5 rounded-sm hover:bg-primary-hover transition-all disabled:opacity-60 flex items-center justify-center gap-2">
                {loading ? <Loader2 size={18} className="animate-spin" /> : null}
                {t('apply.submit')}
              </button>
            </form>
          )}
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
