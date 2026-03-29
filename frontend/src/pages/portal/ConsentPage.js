import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';
import { Shield, CheckCircle, XCircle, Clock, AlertCircle, Info } from 'lucide-react';

const CONSENT_INFO = {
  de: {
    teacher_data_access: {
      title: 'Datenweitergabe an Lehr-/Betreuungspersonal',
      purpose: 'Weitergabe relevanter Bewerbungs- und Lerndaten an zugewiesenes Lehr- und Betreuungspersonal zum Zweck der pädagogischen Betreuung und Kursorganisation.',
      scope: ['Vollständiger Name', 'E-Mail', 'Telefon', 'Kurstyp', 'Sprachniveau', 'Land des Abschlusses', 'Dokumentenstatus', 'Bewerbungsstatus'],
      excludes: ['Finanzdaten', 'Passdaten', 'Interne Notizen', 'AI-Screening-Berichte'],
      legal_note: 'Diese Einwilligung ist freiwillig und jederzeit widerrufbar. Die Datenweitergabe erfolgt zweckgebunden und datenminimal gemäß DSGVO Art. 6 Abs. 1 lit. a.',
    },
  },
  en: {
    teacher_data_access: {
      title: 'Data Sharing with Teaching/Supervisory Staff',
      purpose: 'Sharing of relevant application and learning data with assigned teaching and supervisory staff for the purpose of educational support and course administration.',
      scope: ['Full Name', 'Email', 'Phone', 'Course Type', 'Language Level', 'Degree Country', 'Document Status', 'Application Stage'],
      excludes: ['Financial Data', 'Passport Details', 'Internal Notes', 'AI Screening Reports'],
      legal_note: 'This consent is voluntary and revocable at any time. Data sharing is purpose-bound and data-minimal in accordance with GDPR Art. 6(1)(a).',
    },
  },
};

export default function ConsentPage() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [consents, setConsents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState('');

  const lang = i18n.language === 'en' ? 'en' : 'de';
  const consentInfo = CONSENT_INFO[lang];

  useEffect(() => {
    loadConsents();
  }, []);

  const loadConsents = async () => {
    try {
      const res = await apiClient.get('/api/consents/my', { withCredentials: true });
      setConsents(res.data || []);
    } catch (e) {
      console.error('Failed to load consents', e);
    } finally {
      setLoading(false);
    }
  };

  const grantConsent = async (consentType) => {
    setActionLoading(consentType);
    try {
      await apiClient.post('/api/consents/grant', {
        consent_type: consentType,
        version: '1.0',
        granted: true,
      }, { withCredentials: true });
      await loadConsents();
    } catch (e) {
      console.error('Failed to grant consent', e);
    } finally {
      setActionLoading('');
    }
  };

  const revokeConsent = async (consentType) => {
    setActionLoading(consentType);
    try {
      await apiClient.post(`/api/consents/revoke/${consentType}`, {}, { withCredentials: true });
      await loadConsents();
    } catch (e) {
      console.error('Failed to revoke consent', e);
    } finally {
      setActionLoading('');
    }
  };

  const hasActiveConsent = (consentType) => {
    return consents.some(c => c.consent_type === consentType && c.granted && !c.revoked_at);
  };

  const getConsentHistory = (consentType) => {
    return consents.filter(c => c.consent_type === consentType);
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
  );

  const labels = {
    de: {
      title: 'Einwilligungen & Datenschutz',
      sub: 'Verwalte deine Einwilligungen zur Datenverarbeitung.',
      active: 'Aktiv',
      revoked: 'Widerrufen',
      not_granted: 'Nicht erteilt',
      grant_btn: 'Einwilligung erteilen',
      revoke_btn: 'Einwilligung widerrufen',
      scope_label: 'Umfang der Datenweitergabe:',
      excluded_label: 'Ausdrücklich ausgeschlossen:',
      history_label: 'Verlauf',
      granted_on: 'Erteilt am',
      revoked_on: 'Widerrufen am',
      no_history: 'Noch keine Einwilligungshistorie.',
      info_banner: 'Deine Einwilligungen steuern, welche Daten an Lehr- und Betreuungspersonal weitergegeben werden dürfen. Du kannst jede Einwilligung jederzeit widerrufen.',
    },
    en: {
      title: 'Consents & Privacy',
      sub: 'Manage your data processing consents.',
      active: 'Active',
      revoked: 'Revoked',
      not_granted: 'Not granted',
      grant_btn: 'Grant Consent',
      revoke_btn: 'Revoke Consent',
      scope_label: 'Data sharing scope:',
      excluded_label: 'Explicitly excluded:',
      history_label: 'History',
      granted_on: 'Granted on',
      revoked_on: 'Revoked on',
      no_history: 'No consent history yet.',
      info_banner: 'Your consents control which data may be shared with teaching and supervisory staff. You can revoke any consent at any time.',
    },
  };

  const l = labels[lang];

  return (
    <div className="space-y-6 animate-fade-in" data-testid="consent-page">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">{l.title}</h1>
        <p className="text-slate-500 text-sm">{l.sub}</p>
      </div>

      {/* Info Banner */}
      <div className="bg-primary/5 border border-primary/20 rounded-sm p-4 flex items-start gap-3" data-testid="consent-info-banner">
        <Info size={18} className="text-primary mt-0.5 shrink-0" />
        <p className="text-sm text-slate-600">{l.info_banner}</p>
      </div>

      {/* Consent Cards */}
      {Object.entries(consentInfo).map(([consentType, info]) => {
        const isActive = hasActiveConsent(consentType);
        const history = getConsentHistory(consentType);

        return (
          <div key={consentType} className="bg-white border border-slate-200 rounded-sm" data-testid={`consent-card-${consentType}`}>
            <div className="p-5 sm:p-6">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-sm flex items-center justify-center ${isActive ? 'bg-green-50' : 'bg-slate-100'}`}>
                    <Shield size={20} className={isActive ? 'text-green-600' : 'text-slate-400'} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800 text-sm">{info.title}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-sm border ${
                      isActive ? 'bg-green-50 text-green-700 border-green-200' : 'bg-slate-50 text-slate-500 border-slate-200'
                    }`}>
                      {isActive ? l.active : l.not_granted}
                    </span>
                  </div>
                </div>
              </div>

              <p className="text-sm text-slate-600 mb-4">{info.purpose}</p>

              {/* Scope */}
              <div className="mb-3">
                <p className="text-xs font-medium text-slate-700 mb-1">{l.scope_label}</p>
                <div className="flex flex-wrap gap-1.5">
                  {info.scope.map(item => (
                    <span key={item} className="text-xs bg-primary/5 text-primary px-2 py-0.5 rounded-sm border border-primary/10">
                      {item}
                    </span>
                  ))}
                </div>
              </div>

              {/* Excludes */}
              <div className="mb-4">
                <p className="text-xs font-medium text-slate-700 mb-1">{l.excluded_label}</p>
                <div className="flex flex-wrap gap-1.5">
                  {info.excludes.map(item => (
                    <span key={item} className="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-sm border border-red-100">
                      {item}
                    </span>
                  ))}
                </div>
              </div>

              {/* Legal Note */}
              <p className="text-xs text-slate-400 mb-4 italic">{info.legal_note}</p>

              {/* Action Button */}
              <div className="flex gap-3">
                {isActive ? (
                  <button
                    onClick={() => revokeConsent(consentType)}
                    disabled={actionLoading === consentType}
                    data-testid={`consent-revoke-${consentType}`}
                    className="bg-red-50 text-red-700 border border-red-200 px-4 py-2 rounded-sm text-sm font-medium hover:bg-red-100 transition-colors disabled:opacity-50 flex items-center gap-2"
                  >
                    {actionLoading === consentType ? (
                      <div className="w-4 h-4 border-2 border-red-400 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <XCircle size={16} />
                    )}
                    {l.revoke_btn}
                  </button>
                ) : (
                  <button
                    onClick={() => grantConsent(consentType)}
                    disabled={actionLoading === consentType}
                    data-testid={`consent-grant-${consentType}`}
                    className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover transition-colors disabled:opacity-50 flex items-center gap-2"
                  >
                    {actionLoading === consentType ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <CheckCircle size={16} />
                    )}
                    {l.grant_btn}
                  </button>
                )}
              </div>
            </div>

            {/* History */}
            {history.length > 0 && (
              <div className="border-t border-slate-100 p-4 bg-slate-50/50">
                <p className="text-xs font-medium text-slate-600 mb-2">{l.history_label}</p>
                <div className="space-y-1.5">
                  {history.slice(0, 5).map((entry, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-xs text-slate-500">
                      {entry.granted && !entry.revoked_at ? (
                        <CheckCircle size={12} className="text-green-500" />
                      ) : entry.revoked_at ? (
                        <XCircle size={12} className="text-red-400" />
                      ) : (
                        <Clock size={12} className="text-slate-400" />
                      )}
                      <span>
                        {entry.granted && !entry.revoked_at
                          ? `${l.granted_on} ${new Date(entry.granted_at).toLocaleDateString('de-DE')} (v${entry.version})`
                          : entry.revoked_at
                          ? `${l.revoked_on} ${new Date(entry.revoked_at).toLocaleDateString('de-DE')}`
                          : l.not_granted
                        }
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
