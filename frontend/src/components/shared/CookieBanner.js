import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Shield, X, ChevronDown, ChevronUp } from 'lucide-react';

const STORAGE_KEY = 'w2g_cookie_consent';

const COOKIE_CATEGORIES = {
  necessary: {
    id: 'necessary',
    required: true,
    cookies: ['access_token', 'refresh_token', 'i18nextLng'],
  },
  functional: {
    id: 'functional',
    required: false,
    cookies: ['w2g_cookie_consent', 'onboarding_completed'],
  },
};

const TEXTS = {
  de: {
    title: 'Cookie-Einstellungen',
    description: 'Diese Website verwendet Cookies, um den sicheren Betrieb des Portals zu gewährleisten. Technisch notwendige Cookies sind für die Grundfunktionen erforderlich und können nicht deaktiviert werden.',
    necessary_title: 'Technisch notwendig',
    necessary_desc: 'Authentifizierung (Login-Session), Spracheinstellung. Diese Cookies sind für den Betrieb der Plattform zwingend erforderlich.',
    functional_title: 'Funktional',
    functional_desc: 'Speicherung Ihrer Cookie-Präferenzen und Onboarding-Status. Diese verbessern die Nutzererfahrung.',
    accept_all: 'Alle akzeptieren',
    accept_selected: 'Auswahl bestätigen',
    accept_necessary: 'Nur notwendige',
    details: 'Details anzeigen',
    hide_details: 'Details ausblenden',
    always_active: 'Immer aktiv',
    privacy_link: 'Datenschutzerklärung',
    legal_note: 'W2G Academy GmbH · Amtsgericht Aachen HRB 23610',
  },
  en: {
    title: 'Cookie Settings',
    description: 'This website uses cookies to ensure the secure operation of the portal. Technically necessary cookies are required for basic functions and cannot be disabled.',
    necessary_title: 'Technically Necessary',
    necessary_desc: 'Authentication (login session), language setting. These cookies are essential for the operation of the platform.',
    functional_title: 'Functional',
    functional_desc: 'Storage of your cookie preferences and onboarding status. These improve the user experience.',
    accept_all: 'Accept All',
    accept_selected: 'Confirm Selection',
    accept_necessary: 'Necessary Only',
    details: 'Show Details',
    hide_details: 'Hide Details',
    always_active: 'Always Active',
    privacy_link: 'Privacy Policy',
    legal_note: 'W2G Academy GmbH · Amtsgericht Aachen HRB 23610',
  },
};

function getConsent() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function saveConsent(categories) {
  const consent = {
    categories,
    timestamp: new Date().toISOString(),
    version: '1.0',
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(consent));
  return consent;
}

export function hasConsent(categoryId) {
  const consent = getConsent();
  if (!consent) return categoryId === 'necessary';
  return consent.categories?.[categoryId] === true;
}

export default function CookieBanner() {
  const { i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'de';
  const t = TEXTS[lang];

  const [visible, setVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [selections, setSelections] = useState({
    necessary: true,
    functional: false,
  });

  useEffect(() => {
    const existing = getConsent();
    if (!existing) {
      setVisible(true);
    }
  }, []);

  if (!visible) return null;

  const handleAcceptAll = () => {
    const all = {};
    Object.keys(COOKIE_CATEGORIES).forEach(k => { all[k] = true; });
    saveConsent(all);
    setVisible(false);
  };

  const handleAcceptNecessary = () => {
    saveConsent({ necessary: true, functional: false });
    setVisible(false);
  };

  const handleAcceptSelected = () => {
    saveConsent({ ...selections, necessary: true });
    setVisible(false);
  };

  const toggleCategory = (id) => {
    if (COOKIE_CATEGORIES[id]?.required) return;
    setSelections(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="fixed inset-0 z-[99999] flex items-end sm:items-center justify-center" data-testid="cookie-banner">
      <div className="absolute inset-0 bg-black/40" />
      <div className="relative bg-white w-full sm:max-w-lg sm:rounded-lg shadow-2xl border border-slate-200 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="px-5 pt-5 pb-3 flex items-start justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-primary/10 rounded flex items-center justify-center">
              <Shield size={16} className="text-primary" />
            </div>
            <h2 className="text-base font-semibold text-slate-800">{t.title}</h2>
          </div>
        </div>

        {/* Description */}
        <div className="px-5 pb-4">
          <p className="text-sm text-slate-600 leading-relaxed">{t.description}</p>
        </div>

        {/* Details toggle */}
        <div className="px-5 pb-3">
          <button
            onClick={() => setShowDetails(!showDetails)}
            data-testid="cookie-details-toggle"
            className="text-xs text-primary font-medium flex items-center gap-1 hover:underline"
          >
            {showDetails ? t.hide_details : t.details}
            {showDetails ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>
        </div>

        {/* Category details */}
        {showDetails && (
          <div className="px-5 pb-4 space-y-3" data-testid="cookie-details-panel">
            {Object.entries(COOKIE_CATEGORIES).map(([key, cat]) => (
              <div key={key} className="border border-slate-100 rounded p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-800">
                      {key === 'necessary' ? t.necessary_title : t.functional_title}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {key === 'necessary' ? t.necessary_desc : t.functional_desc}
                    </p>
                  </div>
                  {cat.required ? (
                    <span className="text-[10px] font-medium text-primary bg-primary/8 px-2 py-0.5 rounded whitespace-nowrap">
                      {t.always_active}
                    </span>
                  ) : (
                    <button
                      onClick={() => toggleCategory(key)}
                      data-testid={`cookie-toggle-${key}`}
                      className={`relative w-10 h-5 rounded-full transition-colors ${
                        selections[key] ? 'bg-primary' : 'bg-slate-300'
                      }`}
                    >
                      <span className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                        selections[key] ? 'translate-x-5' : 'translate-x-0.5'
                      }`} />
                    </button>
                  )}
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {cat.cookies.map(c => (
                    <span key={c} className="text-[10px] bg-slate-50 text-slate-500 px-1.5 py-0.5 rounded">
                      {c}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="px-5 pb-4 flex flex-col gap-2">
          <button
            onClick={handleAcceptAll}
            data-testid="cookie-accept-all"
            className="w-full bg-primary text-white text-sm font-semibold py-2.5 rounded hover:bg-primary/90 transition-colors"
          >
            {t.accept_all}
          </button>
          <div className="flex gap-2">
            {showDetails && (
              <button
                onClick={handleAcceptSelected}
                data-testid="cookie-accept-selected"
                className="flex-1 border border-primary text-primary text-sm font-medium py-2 rounded hover:bg-primary/5 transition-colors"
              >
                {t.accept_selected}
              </button>
            )}
            <button
              onClick={handleAcceptNecessary}
              data-testid="cookie-accept-necessary"
              className="flex-1 border border-slate-300 text-slate-600 text-sm font-medium py-2 rounded hover:bg-slate-50 transition-colors"
            >
              {t.accept_necessary}
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 pb-4 flex items-center justify-between border-t border-slate-100 pt-3">
          <a href="/privacy" className="text-xs text-primary hover:underline">{t.privacy_link}</a>
          <p className="text-[10px] text-slate-400">{t.legal_note}</p>
        </div>
      </div>
    </div>
  );
}
