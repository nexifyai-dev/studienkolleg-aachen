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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group" data-testid="nav-logo">
            <div className="w-8 h-8 bg-primary rounded-sm flex items-center justify-center group-hover:bg-primary-hover transition-colors">
              <GraduationCap size={18} className="text-white" />
            </div>
            <span className="font-heading font-bold text-primary text-lg hidden sm:block">
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

          {/* Right actions */}
          <div className="hidden md:flex items-center gap-3">
            {/* Language switcher */}
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

          {/* Mobile menu toggle */}
          <button onClick={() => setOpen(!open)} className="md:hidden p-2 text-slate-600" data-testid="nav-mobile-toggle">
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden bg-white border-t border-slate-100 px-4 py-4 space-y-3 animate-fade-in">
          {links.map(l => (
            <Link key={l.href} to={l.href} onClick={() => setOpen(false)}
              className="block text-sm font-medium text-slate-700 hover:text-primary py-1">
              {l.label}
            </Link>
          ))}
          {/* Mobile Language Switcher */}
          <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
            <Globe size={14} className="text-slate-400" />
            {LANGUAGES.map(lang => (
              <button key={lang.code}
                onClick={() => { i18n.changeLanguage(lang.code); setOpen(false); }}
                className={`text-xs px-2 py-1 rounded-sm font-medium transition-colors ${i18n.language === lang.code ? 'bg-primary text-white' : 'text-slate-500 hover:text-primary'}`}
                data-testid={`mobile-lang-${lang.code}`}
              >
                {lang.code.toUpperCase()}
              </button>
            ))}
          </div>
          <div className="flex gap-3">
            <Link to="/auth/login" onClick={() => setOpen(false)}
              className="text-sm font-medium text-slate-600 hover:text-primary">
              {t('nav.login')}
            </Link>
            <Link to="/apply" onClick={() => setOpen(false)}
              className="bg-primary text-white text-sm font-medium px-4 py-2 rounded-sm hover:bg-primary-hover">
              {t('nav.apply')}
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
