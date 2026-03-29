import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';
import { Plane, Home, Heart, FileCheck, GraduationCap, ShieldCheck, ArrowRight } from 'lucide-react';

const AACHEN_GRAPHIC = "https://www.studienkollegaachen.de/images/grafik_hi_aachen_deutschkurs_german_course_a1_c1-380.webp";

const SERVICE_ICONS = { visa: Plane, housing: Home, mentoring: Heart, documents: FileCheck, uni: GraduationCap, insurance: ShieldCheck };
const SERVICE_KEYS = ['visa', 'housing', 'mentoring', 'documents', 'uni', 'insurance'];
const SERVICE_LINKS = {
  visa: { href: 'https://digital.diplo.de/studium', labelKey: 'services.visa.link' },
  housing: { href: 'https://stayinaachen.de/', labelKey: 'services.housing.link' },
  insurance: { href: 'https://www.care-concept.de', labelKey: 'services.insurance.link' },
};
const SERVICE_LINK_LABELS_DE = { visa: 'Visa-Infoportal', housing: 'stayinaachen.de', insurance: 'Zu unserem Partner' };
const SERVICE_LINK_LABELS_EN = { visa: 'Visa Info Portal', housing: 'stayinaachen.de', insurance: 'To Our Partner' };

const PROCESS_STEPS = ['apply', 'check', 'confirm', 'start'];
const STEP_NUMBERS = ['01', '02', '03', '04'];

const LOCATION_DE = [
  { label: 'Unterricht & Beratung', val: 'Theaterstraße 30–32, 52062 Aachen' },
  { label: 'Bürozeiten', val: 'Mo–Fr: 9:00–17:00 Uhr' },
  { label: 'Kontakt', val: 'info@stk-aachen.de · +49 241 990 322 92' },
];
const LOCATION_EN = [
  { label: 'Teaching & Consulting', val: 'Theaterstraße 30–32, 52062 Aachen' },
  { label: 'Office Hours', val: 'Mon–Fri: 9:00 am–5:00 pm' },
  { label: 'Contact', val: 'info@stk-aachen.de · +49 241 990 322 92' },
];

export default function ServicesPage() {
  const { t, i18n } = useTranslation();
  const isEN = i18n.language === 'en';
  const linkLabels = isEN ? SERVICE_LINK_LABELS_EN : SERVICE_LINK_LABELS_DE;
  const locationRows = isEN ? LOCATION_EN : LOCATION_DE;

  return (
    <div className="min-h-screen bg-white">
      <SEOHead titleKey="seo.services_title" descKey="seo.services_desc" path="/services" />
      <PublicNav />
      <main className="pt-16">

        {/* Hero */}
        <section className="bg-primary py-10 sm:py-16 lg:py-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
            <h1 className="text-2xl sm:text-4xl lg:text-5xl font-heading font-bold text-white mb-3 sm:mb-4">
              {t('services_page.hero_title')}
            </h1>
            <p className="text-white/70 text-sm sm:text-base lg:text-lg max-w-xl mx-auto leading-relaxed">
              {t('services_page.hero_sub')}
            </p>
          </div>
        </section>

        {/* Services-Grid */}
        <section className="py-10 sm:py-16 lg:py-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
              {SERVICE_KEYS.map(key => {
                const Icon = SERVICE_ICONS[key];
                const link = SERVICE_LINKS[key];
                return (
                  <div
                    key={key}
                    className={`bg-white border rounded-sm p-6 hover:-translate-y-1 hover:shadow-card-hover transition-all duration-300 ${
                      key === 'visa' ? 'border-primary/30' : 'border-slate-200'
                    }`}
                    data-testid={`service-card-${key}`}
                  >
                    <div className="w-10 h-10 bg-primary/8 border border-primary/15 rounded-sm flex items-center justify-center mb-5">
                      <Icon size={18} className="text-primary" />
                    </div>
                    <h3 className="font-heading font-bold text-primary text-lg mb-2">
                      {t(`services.${key}.name`)}
                    </h3>
                    <p className="text-slate-600 text-sm leading-relaxed mb-4">
                      {t(`services.${key}.desc`)}
                    </p>
                    {link && (
                      <a href={link.href} target="_blank" rel="noopener noreferrer"
                        className="text-primary text-sm font-medium hover:underline flex items-center gap-1">
                        {linkLabels[key]} <ArrowRight size={13} />
                      </a>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Aachen-Grafik + Standort-Info */}
        <section className="py-10 sm:py-16 lg:py-20 bg-slate-50 border-t border-b border-slate-100">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-10 items-center">
              <div>
                <img
                  src={AACHEN_GRAPHIC}
                  alt="Deutschkurs Aachen A1–C1"
                  className="w-full max-h-64 object-contain rounded-sm"
                  onError={e => { e.target.style.display = 'none'; }}
                />
              </div>
              <div>
                <h2 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-4">
                  {t('services_page.location_title')}
                </h2>
                <p className="text-slate-600 mb-5 leading-relaxed">
                  {t('services_page.location_desc')}
                </p>
                <div className="space-y-3">
                  {locationRows.map(item => (
                    <div key={item.label} className="flex gap-3 text-sm">
                      <span className="text-slate-400 w-36 shrink-0">{item.label}:</span>
                      <span className="text-slate-700 font-medium">{item.val}</span>
                    </div>
                  ))}
                </div>
                <Link to="/contact"
                  className="mt-6 inline-flex items-center gap-2 border-2 border-primary text-primary font-semibold px-5 py-2.5 rounded-sm hover:bg-primary hover:text-white transition-all text-sm"
                  data-testid="services-contact-btn">
                  {t('nav.contact')} <ArrowRight size={15} />
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Prozess-Überblick */}
        <section className="py-10 sm:py-16 lg:py-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-heading font-bold text-primary mb-3 text-center">
              {t('services_page.process_title')}
            </h2>
            <p className="text-slate-600 text-center mb-8 sm:mb-10 max-w-lg mx-auto">
              {t('services_page.process_desc')}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
              {PROCESS_STEPS.map((step, i) => (
                <div key={step}
                  className="bg-white border border-slate-200 rounded-sm p-5"
                  data-testid={`process-step-${STEP_NUMBERS[i]}`}>
                  <span className="inline-flex w-8 h-8 bg-primary text-white text-xs font-bold rounded-sm items-center justify-center mb-4">
                    {STEP_NUMBERS[i]}
                  </span>
                  <h3 className="font-semibold text-slate-800 text-sm mb-2">
                    {t(`services_page.steps.${step}.title`)}
                  </h3>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    {t(`services_page.steps.${step}.desc`)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="bg-primary py-10 sm:py-14 lg:py-16">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 text-center">
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-heading font-bold text-white mb-3 sm:mb-4">
              {t('services_page.cta_title')}
            </h2>
            <p className="text-white/70 mb-6 sm:mb-8 max-w-lg mx-auto">
              {t('services_page.cta_desc')}
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/apply"
                data-testid="services-cta-apply"
                className="bg-white text-primary font-semibold px-6 sm:px-8 py-3 sm:py-3.5 rounded-sm hover:bg-slate-50 transition-all inline-flex items-center justify-center gap-2 text-sm sm:text-base">
                {t('services_page.cta_apply')} <ArrowRight size={16} />
              </Link>
              <Link to="/contact"
                data-testid="services-cta-contact"
                className="border-2 border-white/40 text-white font-semibold px-6 sm:px-8 py-3 sm:py-3.5 rounded-sm hover:border-white/70 transition-all inline-flex items-center justify-center text-sm sm:text-base">
                {t('services_page.cta_contact')}
              </Link>
            </div>
          </div>
        </section>

      </main>
      <PublicFooter />
    </div>
  );
}
