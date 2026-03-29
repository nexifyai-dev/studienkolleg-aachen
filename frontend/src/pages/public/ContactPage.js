import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import { Phone, Mail, MessageCircle, MapPin, Clock } from 'lucide-react';

export default function ContactPage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-white">
      <PublicNav />
      <main className="pt-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
          <div className="text-center mb-8 sm:mb-12">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-heading font-bold text-primary mb-3">
              {t('contact_page.title')}
            </h1>
            <p className="text-slate-600 max-w-xl mx-auto">
              {t('contact_page.sub')}
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">

            {/* Kontaktdaten */}
            <div className="lg:col-span-2 space-y-6">

              {/* Bewerberbereich / Way2Germany */}
              <div className="bg-primary text-white rounded-sm p-6">
                <p className="text-xs font-bold text-white/60 uppercase tracking-wide mb-4">
                  {t('contact_page.standort_label')}
                </p>
                <div className="space-y-3.5 text-sm">
                  <div className="flex items-start gap-3">
                    <MapPin size={15} className="mt-0.5 shrink-0 opacity-70" />
                    <div>
                      <p>Theaterstraße 30–32</p>
                      <p>52062 Aachen</p>
                      <p className="text-xs text-white/70 mt-0.5">{t('contact_page.office_note')}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Phone size={15} className="shrink-0 opacity-70" />
                    <a href="tel:+4924199032292" className="hover:text-white/80 transition-colors">
                      +49 241 990 322 92
                    </a>
                  </div>
                  <div className="flex items-center gap-3">
                    <Mail size={15} className="shrink-0 opacity-70" />
                    <a href="mailto:info@stk-aachen.de" className="hover:text-white/80 transition-colors">
                      info@stk-aachen.de
                    </a>
                  </div>
                  <div className="flex items-center gap-3">
                    <MessageCircle size={15} className="shrink-0 opacity-70" />
                    <a href="https://api.whatsapp.com/message/RVKVWFEKNCIRG1?autoload=1&app_absent=0"
                      target="_blank" rel="noopener noreferrer"
                      className="hover:text-white/80 transition-colors">
                      WhatsApp
                    </a>
                  </div>
                  <div className="flex items-center gap-3">
                    <Clock size={15} className="shrink-0 opacity-70" />
                    <span className="text-white/80">{t('contact_page.hours_value')}</span>
                  </div>
                </div>
              </div>

              {/* Gesellschaftssitz */}
              <div className="border border-slate-200 rounded-sm p-5 text-sm">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3">
                  {t('contact_page.registered_label')}
                </p>
                <div className="space-y-1.5 text-slate-600">
                  <p className="font-semibold text-slate-800">W2G Academy GmbH</p>
                  <p>Theaterstraße 24</p>
                  <p>52062 Aachen</p>
                  <p className="text-xs text-slate-400 pt-1">HRB 23610 · Amtsgericht Aachen</p>
                </div>
              </div>

              <p className="text-xs text-slate-400">
                {t('contact_page.privacy_notice')}
              </p>
            </div>

            {/* CTAs */}
            <div className="lg:col-span-3 space-y-5">
              {/* Bewerben CTA */}
              <div className="border border-primary/20 rounded-sm p-6 sm:p-8">
                <h2 className="text-xl font-heading font-bold text-primary mb-2">
                  {t('contact_page.cta_apply_title')}
                </h2>
                <p className="text-slate-600 text-sm mb-5 leading-relaxed">
                  {t('contact_page.cta_apply_desc')}
                </p>
                <Link to="/apply"
                  data-testid="contact-apply-btn"
                  className="inline-block bg-primary text-white font-semibold px-6 py-3 rounded-sm hover:bg-primary-hover transition-all text-sm">
                  {t('contact_page.cta_apply_btn')}
                </Link>
              </div>

              {/* WhatsApp CTA */}
              <div className="border border-slate-200 rounded-sm p-6 sm:p-8">
                <h2 className="text-xl font-heading font-bold text-primary mb-2">
                  {t('contact_page.whatsapp_title')}
                </h2>
                <p className="text-slate-600 text-sm mb-5 leading-relaxed">
                  {t('contact_page.whatsapp_desc')}
                </p>
                <a
                  href="https://api.whatsapp.com/message/RVKVWFEKNCIRG1?autoload=1&app_absent=0"
                  target="_blank"
                  rel="noopener noreferrer"
                  data-testid="contact-whatsapp-btn"
                  className="block w-full bg-slate-800 text-white text-center font-semibold py-2.5 rounded-sm hover:bg-slate-900 transition-colors text-sm">
                  {t('contact_page.whatsapp_btn')}
                </a>
              </div>

              {/* Rechtliche Angaben */}
              <div className="pt-4 border-t border-slate-100">
                <p className="text-xs text-slate-400">
                  {t('contact_page.legal_link_note')}{' '}
                  <Link to="/legal" className="text-primary hover:underline">
                    {t('contact_page.impressum_link')}
                  </Link>
                  {' · '}
                  <Link to="/privacy" className="text-primary hover:underline">
                    {t('contact_page.privacy_link')}
                  </Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
