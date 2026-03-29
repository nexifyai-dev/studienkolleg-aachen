import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Menu, X, GraduationCap, Globe } from 'lucide-react';

const LANGUAGES = [
  { code: 'de', label: 'Deutsch' },
  { code: 'en', label: 'English' },
];

export default function PublicNav() {
  const { t, i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  const location = useLocation();

  const links = [
    { href: '/courses', label: t('nav.courses') },
    { href: '/services', label: t('nav.services') },
    { href: '/contact', label: t('nav.contact') },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-white/90 border-b border-slate-200/60 shadow-sm">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14 sm:h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group shrink-0" data-testid="nav-logo">
            <div className="w-7 h-7 sm:w-8 sm:h-8 bg-primary rounded-sm flex items-center justify-center group-hover:bg-primary-hover transition-colors">
              <GraduationCap size={16} className="text-white" />
            </div>
            <span className="font-heading font-bold text-primary text-sm sm:text-lg hidden min-[420px]:block truncate max-w-[160px] sm:max-w-none">
              Studienkolleg Aachen
            </span>
          </Link>

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-6">
            {links.map(l => (
              <Link key={l.href} to={l.href}
                className={`text-sm font-medium transition-colors hover:text-primary ${location.pathname === l.href ? 'text-primary' : 'text-slate-600'}`}
                data-testid={`nav-link-${l.href.replace('/', '')}`}
              >
                {l.label}
              </Link>
            ))}
          </div>

          {/* Right actions – Desktop */}
          <div className="hidden md:flex items-center gap-3">
            <div className="flex items-center gap-1 border border-slate-200 rounded-sm px-2 py-1">
              <Globe size={14} className="text-slate-400" />
              {LANGUAGES.map(lang => (
                <button key={lang.code}
                  onClick={() => i18n.changeLanguage(lang.code)}
                  className={`text-xs px-1 font-medium transition-colors ${i18n.language === lang.code ? 'text-primary' : 'text-slate-500 hover:text-primary'}`}
                  data-testid={`lang-${lang.code}`}
                >
                  {lang.code.toUpperCase()}
                </button>
              ))}
            </div>
            <Link to="/auth/login" data-testid="nav-login"
              className="text-sm font-medium text-slate-600 hover:text-primary transition-colors">
              {t('nav.login')}
            </Link>
            <Link to="/apply" data-testid="nav-apply-btn"
              className="bg-primary text-white text-sm font-medium px-4 py-2 rounded-sm hover:bg-primary-hover transition-colors">
              {t('nav.apply')}
            </Link>
          </div>

          {/* Right actions – Mobile: Language + Burger */}
          <div className="flex md:hidden items-center gap-1.5">
            <div className="flex items-center border border-slate-200 rounded-sm px-1.5 py-1">
              {LANGUAGES.map(lang => (
                <button key={lang.code}
                  onClick={() => i18n.changeLanguage(lang.code)}
                  className={`text-[11px] px-1.5 py-0.5 font-medium transition-colors rounded-sm ${
                    i18n.language === lang.code
                      ? 'text-white bg-primary'
                      : 'text-slate-500 hover:text-primary'
                  }`}
                  data-testid={`mobile-lang-${lang.code}`}
                >
                  {lang.code.toUpperCase()}
                </button>
              ))}
            </div>
            <button onClick={() => setOpen(!open)} className="p-2 text-slate-600 min-w-[40px] min-h-[40px] flex items-center justify-center" data-testid="nav-mobile-toggle">
              {open ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden bg-white border-t border-slate-100 px-4 py-4 space-y-1 animate-fade-in shadow-lg">
          {links.map(l => (
            <Link key={l.href} to={l.href} onClick={() => setOpen(false)}
              className={`block text-sm font-medium py-2.5 px-2 rounded-sm transition-colors ${
                location.pathname === l.href
                  ? 'text-primary bg-primary/5'
                  : 'text-slate-700 hover:text-primary hover:bg-slate-50'
              }`}>
              {l.label}
            </Link>
          ))}
          <div className="border-t border-slate-100 pt-3 mt-2 flex items-center gap-3">
            <Link to="/auth/login" onClick={() => setOpen(false)}
              className="text-sm font-medium text-slate-600 hover:text-primary py-2 px-2">
              {t('nav.login')}
            </Link>
            <Link to="/apply" onClick={() => setOpen(false)}
              className="bg-primary text-white text-sm font-medium px-5 py-2.5 rounded-sm hover:bg-primary-hover flex-1 text-center">
              {t('nav.apply')}
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
