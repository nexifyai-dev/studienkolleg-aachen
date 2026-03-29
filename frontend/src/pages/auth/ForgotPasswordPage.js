import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { formatApiError } from '../../contexts/AuthContext';
import { Loader2, AlertCircle, CheckCircle, GraduationCap } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      await axios.post(`${API}/api/auth/forgot-password`, { email }, { withCredentials: true });
      setSuccess(true);
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail));
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
          <h1 className="text-2xl font-heading font-bold text-primary">Passwort vergessen</h1>
        </div>
        <div className="bg-white border border-slate-200 rounded-sm shadow-card p-6">
          {success ? (
            <div className="text-center" data-testid="forgot-success">
              <CheckCircle size={36} className="text-green-500 mx-auto mb-3" />
              <p className="text-green-700 text-sm">Wenn diese E-Mail existiert, wurde ein Reset-Link gesendet.</p>
              <Link to="/auth/login" className="mt-4 inline-block text-primary font-medium hover:underline text-sm">← Zurück zur Anmeldung</Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4" data-testid="forgot-form">
              {error && <div className="bg-red-50 border border-red-200 rounded-sm p-3 flex items-center gap-2 text-red-700 text-sm"><AlertCircle size={16}/> {error}</div>}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">E-Mail-Adresse</label>
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} required data-testid="forgot-email-input"
                  className="w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20" />
              </div>
              <button type="submit" disabled={loading} data-testid="forgot-submit-btn"
                className="w-full bg-primary text-white font-semibold py-3 rounded-sm hover:bg-primary-hover transition-colors disabled:opacity-60 flex items-center justify-center gap-2">
                {loading && <Loader2 size={18} className="animate-spin" />}
                Reset-Link senden
              </button>
              <p className="text-center"><Link to="/auth/login" className="text-sm text-primary hover:underline">← Zurück</Link></p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
