import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ChevronRight, Menu, X } from 'lucide-react';

const LANGUAGES = [
  { code: 'de', label: 'DE' },
  { code: 'en', label: 'EN' },
];

export default function PublicNav() {
  const { t, i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const links = [
    { href: '/', label: t('nav.home') },
    { href: '/courses', label: t('nav.courses') },
    { href: '/services', label: t('nav.services') },
    { href: '/knowledge', label: t('nav.knowledge') },
    { href: '/booking', label: t('nav.booking') },
    { href: '/contact', label: t('nav.contact') },
  ];

  const isHome = location.pathname === '/';
  const navBg = scrolled
    ? 'bg-white/95 backdrop-blur-md border-b border-[var(--color-primary)]/8'
    : isHome ? 'bg-transparent' : 'bg-white border-b border-[var(--color-primary)]/8';
  const textColor = scrolled || !isHome ? 'text-[var(--color-primary-dark)]' : 'text-white';
  const textMuted = scrolled || !isHome ? 'text-[var(--color-text-secondary)]' : 'text-white/60';

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${navBg}`} data-testid="public-topbar">
      <div className="max-w-[1280px] mx-auto px-6 lg:px-12 h-16 md:h-[72px] lg:h-20 flex items-center justify-between">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 shrink-0" data-testid="nav-logo">
          <img src="/images/logos/studienkolleg-logo.png" alt="Studienkolleg Aachen"
            className="h-9 sm:h-10 w-auto object-contain"
            style={{ filter: scrolled || !isHome ? 'none' : 'brightness(0) invert(1)' }} />
        </Link>

        {/* Desktop Nav */}
        <div className="hidden lg:flex items-center gap-1 flex-1 justify-center" data-testid="public-desktop-nav">
          {links.map((link) => {
            const isActive = location.pathname === link.href;
            return (
              <Link key={link.href} to={link.href}
                className={`px-3.5 py-2 text-[13px] font-medium rounded-[3px] transition-colors ${
                  isActive
                    ? `${textColor} font-semibold`
                    : `${textMuted} hover:${textColor}`
                }`}
                data-testid={`nav-link-${link.href.replace(/\//g, '') || 'home'}`}>
                {link.label}
                {isActive && <div className="h-[2px] mt-0.5 rounded-full" style={{ background: 'var(--color-accent)' }} />}
              </Link>
            );
          })}
        </div>

        {/* Right Actions */}
        <div className="hidden md:flex items-center gap-3 shrink-0">
          {/* Language Switch */}
          <div className="flex items-center gap-0.5 p-0.5 rounded-[3px]" style={{ border: scrolled || !isHome ? '1px solid rgba(17,54,85,0.1)' : '1px solid rgba(255,255,255,0.15)' }} data-testid="public-language-switch">
            {LANGUAGES.map((lang) => (
              <button key={lang.code} type="button" onClick={() => i18n.changeLanguage(lang.code)}
                className={`px-2.5 py-1 text-[11px] font-semibold rounded-[2px] transition-all ${
                  i18n.language === lang.code
                    ? 'bg-[var(--color-primary)] text-white'
                    : `${textMuted} hover:${textColor}`
                }`}
                data-testid={`lang-${lang.code}`}>
                {lang.label}
              </button>
            ))}
          </div>

          <div className="w-[1px] h-5" style={{ background: scrolled || !isHome ? 'rgba(17,54,85,0.1)' : 'rgba(255,255,255,0.15)' }} />

          <Link to="/auth/login" data-testid="nav-login-btn"
            className={`text-[13px] font-semibold px-4 py-2 rounded-[3px] transition-colors ${textMuted} hover:${textColor}`}>
            {t('nav.login')}
          </Link>

          <Link to="/apply" data-testid="nav-apply-btn"
            className="inline-flex items-center h-10 px-5 text-[13px] font-bold text-[var(--color-primary-dark)] rounded-[3px] transition-all duration-300 hover:scale-[1.02]"
            style={{ background: 'var(--color-accent)', boxShadow: '0 2px 12px rgba(212,175,55,0.2)' }}>
            {t('nav.apply')}
          </Link>
        </div>

        {/* Mobile Toggle */}
        <div className="flex md:hidden items-center gap-2">
          <button type="button" onClick={() => i18n.changeLanguage(i18n.language === 'de' ? 'en' : 'de')}
            className={`text-[11px] font-bold px-2.5 py-1.5 rounded-[3px] border ${
              scrolled || !isHome ? 'border-[var(--color-primary)]/10 text-[var(--color-primary-dark)]' : 'border-white/15 text-white'
            }`}
            data-testid="public-mobile-language-toggle">
            {i18n.language === 'de' ? 'EN' : 'DE'}
          </button>
          <button onClick={() => setOpen(!open)}
            className={`w-9 h-9 flex items-center justify-center rounded-[3px] border ${
              scrolled || !isHome ? 'border-[var(--color-primary)]/10' : 'border-white/15'
            }`}
            data-testid="nav-mobile-toggle">
            {open ? <X size={18} className={textColor} /> : <Menu size={18} className={textColor} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {open && (
        <div className="bg-white border-t border-[var(--color-primary)]/8 px-6 py-4 md:hidden" data-testid="public-mobile-nav">
          <div className="space-y-1">
            {links.map((link) => (
              <Link key={link.href} to={link.href} onClick={() => setOpen(false)}
                className={`flex items-center justify-between px-4 py-3 text-[14px] font-medium rounded-[3px] transition-colors ${
                  location.pathname === link.href
                    ? 'bg-[var(--color-primary)] text-white'
                    : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-sunken)]'
                }`}
                data-testid={`mobile-nav-link-${link.href.replace(/\//g, '') || 'home'}`}>
                <span>{link.label}</span>
                <ChevronRight size={14} />
              </Link>
            ))}
            <Link to="/auth/login" onClick={() => setOpen(false)}
              className="flex items-center justify-between px-4 py-3 text-[14px] font-medium text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-sunken)] rounded-[3px]"
              data-testid="mobile-nav-login">
              <span>{t('nav.login')}</span>
              <ChevronRight size={14} />
            </Link>
            <Link to="/apply" onClick={() => setOpen(false)}
              className="mt-3 flex w-full items-center justify-center h-12 text-[14px] font-bold text-[var(--color-primary-dark)] rounded-[3px]"
              style={{ background: 'var(--color-accent)' }}
              data-testid="mobile-nav-apply">
              {t('nav.apply')}
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
