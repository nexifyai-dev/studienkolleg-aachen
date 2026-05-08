import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { GraduationCap, MapPin, Phone, Mail, MessageCircle, Shield, ArrowRight } from 'lucide-react';
import { openCookieSettings } from '../shared/CookieBanner';

const InstagramIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/>
  </svg>
);
const FacebookIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>
  </svg>
);
const YoutubeIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19.13C5.12 19.56 12 19.56 12 19.56s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.43z"/><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/>
  </svg>
);

export default function PublicFooter() {
  const { t } = useTranslation();

  return (
    <footer className="w2g-footer" data-testid="public-footer">
      {/* Oberer Bereich: 5-Spalten Grid */}
      <div className="max-w-[1280px] mx-auto px-6 lg:px-12 pt-16 pb-12">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-x-8 gap-y-10">

          {/* Spalte 1: Brand + Beschreibung */}
          <div className="col-span-2 sm:col-span-3 lg:col-span-2">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="w-9 h-9 rounded-[4px] flex items-center justify-center"
                style={{ background: 'rgba(212,175,55,0.15)' }}>
                <GraduationCap size={18} style={{ color: 'var(--color-accent)' }} />
              </div>
              <span className="text-[16px] font-bold text-white" style={{ fontFamily: 'var(--font-heading)' }}>
                Studienkolleg Aachen
              </span>
            </div>
            <p className="text-[14px] text-white/40 leading-[1.7] max-w-[360px] mb-6">
              {t('footer.copyright')}
            </p>
            {/* Social Icons */}
            <div className="flex items-center gap-3">
              <a href="https://www.instagram.com/carpediem_studienkolleg/" target="_blank" rel="noopener noreferrer"
                className="w-9 h-9 rounded-[4px] flex items-center justify-center text-white/40 hover:text-white transition-colors"
                style={{ background: 'rgba(255,255,255,0.06)' }} data-testid="footer-social-instagram">
                <InstagramIcon size={16} />
              </a>
              <a href="https://www.facebook.com/studienkollegaachen" target="_blank" rel="noopener noreferrer"
                className="w-9 h-9 rounded-[4px] flex items-center justify-center text-white/40 hover:text-white transition-colors"
                style={{ background: 'rgba(255,255,255,0.06)' }} data-testid="footer-social-facebook">
                <FacebookIcon size={16} />
              </a>
              <a href="https://www.youtube.com/@StudienkollegAachen" target="_blank" rel="noopener noreferrer"
                className="w-9 h-9 rounded-[4px] flex items-center justify-center text-white/40 hover:text-white transition-colors"
                style={{ background: 'rgba(255,255,255,0.06)' }} data-testid="footer-social-youtube">
                <YoutubeIcon size={16} />
              </a>
              <a href="https://api.whatsapp.com/message/RVKVWFEKNCIRG1?autoload=1&app_absent=0" target="_blank" rel="noopener noreferrer"
                className="w-9 h-9 rounded-[4px] flex items-center justify-center text-white/40 hover:text-white transition-colors"
                style={{ background: 'rgba(255,255,255,0.06)' }} data-testid="footer-social-whatsapp">
                <MessageCircle size={16} />
              </a>
            </div>
          </div>

          {/* Spalte 2: Programm */}
          <div>
            <h3 className="w2g-footer-heading">
              {t('footer.col_programs', 'Programm')}
            </h3>
            <ul className="space-y-3">
              <li><Link to="/courses#course-t" className="text-[13px] text-white/50 hover:text-white transition-colors">T-Kurs</Link></li>
              <li><Link to="/courses#course-m" className="text-[13px] text-white/50 hover:text-white transition-colors">M-Kurs</Link></li>
              <li><Link to="/courses#course-w" className="text-[13px] text-white/50 hover:text-white transition-colors">W-Kurs</Link></li>
              <li><Link to="/courses#course-deutsch" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.link_german', 'Deutsch-Intensiv')}</Link></li>
              <li><Link to="/courses" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.link_semesters', 'Semestertermine')}</Link></li>
            </ul>
          </div>

          {/* Spalte 3: Services & Infos */}
          <div>
            <h3 className="w2g-footer-heading">
              {t('footer.col_services', 'Services')}
            </h3>
            <ul className="space-y-3">
              <li><Link to="/services#service-visa" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.link_visa', 'Visa & Einreise')}</Link></li>
              <li><Link to="/services#service-housing" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.link_housing', 'Unterkunft')}</Link></li>
              <li><Link to="/services#service-insurance" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.link_insurance', 'Versicherung')}</Link></li>
              <li><Link to="/knowledge" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.link_knowledge', 'Wissensdatenbank')}</Link></li>
              <li><Link to="/booking" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.link_booking', 'Beratungstermin')}</Link></li>
              <li><Link to="/contact" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.link_contact', 'Kontakt')}</Link></li>
            </ul>
          </div>

          {/* Spalte 4: Kontakt + Rechtliches */}
          <div>
            <h3 className="w2g-footer-heading">
              {t('footer.location')}
            </h3>
            <div className="space-y-3 text-[13px] text-white/50 mb-6">
              <div className="flex items-start gap-2.5">
                <MapPin size={13} className="mt-0.5 shrink-0 opacity-60" />
                <div>
                  <p>Theaterstr. 30–32</p>
                  <p>52062 Aachen</p>
                </div>
              </div>
              <div className="flex items-center gap-2.5">
                <Phone size={13} className="shrink-0 opacity-60" />
                <a href="tel:+4924199032292" className="hover:text-white transition-colors">+49 241 990 322 92</a>
              </div>
              <div className="flex items-center gap-2.5">
                <Mail size={13} className="shrink-0 opacity-60" />
                <a href="mailto:info@stk-aachen.de" className="hover:text-white transition-colors">info@stk-aachen.de</a>
              </div>
            </div>

            {/* Rechtliches */}
            <h3 className="w2g-footer-heading" style={{ marginBottom: '16px' }}>
              {t('footer.legal_nav')}
            </h3>
            <ul className="space-y-2.5">
              <li><Link to="/legal" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.legal')}</Link></li>
              <li><Link to="/privacy" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.privacy')}</Link></li>
              <li><Link to="/agb" className="text-[13px] text-white/50 hover:text-white transition-colors">{t('footer.agb')}</Link></li>
              <li>
                <button onClick={openCookieSettings} data-testid="footer-cookie-settings"
                  className="text-[13px] text-white/50 hover:text-white transition-colors flex items-center gap-1.5">
                  <Shield size={11} className="opacity-60" /> {t('footer.cookie_settings')}
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* CTA-Banner */}
      <div className="border-t border-white/8">
        <div className="max-w-[1280px] mx-auto px-6 lg:px-12 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-[14px] text-white/50">{t('home.cta_desc', 'Bewirb dich jetzt und erhalte innerhalb von 24 Stunden eine Rückmeldung.')}</p>
          <Link to="/apply" className="inline-flex items-center gap-2 h-[44px] px-7 text-[13px] font-bold rounded-full shrink-0 transition-all hover:scale-[1.02] group bg-[var(--color-accent)] text-[var(--color-primary-dark)]" data-testid="footer-cta-apply">
            {t('hero.cta_primary', 'Jetzt bewerben')} <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>
      </div>

      {/* Copyright */}
      <div className="border-t border-white/6">
        <div className="max-w-[1280px] mx-auto px-6 lg:px-12 py-5 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-white/30">
          <span>&copy; {new Date().getFullYear()} W2G Academy GmbH / Studienkolleg Aachen. {t('footer.rights')}</span>
          <div className="flex items-center gap-4">
            <span className="text-[11px] text-white/20">{t('footer.address_legal_label', 'Gesellschaftssitz')}: Theaterstr. 24, 52062 Aachen</span>
            <span className="text-white/15">HRB 23610</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
