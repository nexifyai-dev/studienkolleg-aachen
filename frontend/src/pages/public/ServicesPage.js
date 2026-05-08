import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';
import { Plane, Home, Heart, FileCheck, GraduationCap, ShieldCheck, ArrowRight, MapPin, Clock, Phone, Mail, ExternalLink } from 'lucide-react';

/* ── Daten ── */
const SERVICE_ICONS = { visa: Plane, housing: Home, mentoring: Heart, documents: FileCheck, uni: GraduationCap, insurance: ShieldCheck };
const SERVICE_KEYS = ['visa', 'housing', 'mentoring', 'documents', 'uni', 'insurance'];
const SERVICE_LINKS = {
  visa: 'https://digital.diplo.de/studium',
  housing: 'https://stayinaachen.de/',
  insurance: 'https://www.care-concept.de',
};

/* ── Animate ── */
function useInView(threshold = 0.1) {
  const ref = useRef(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVis(true); obs.unobserve(el); } }, { threshold });
    obs.observe(el); return () => obs.disconnect();
  }, [threshold]);
  return [ref, vis];
}
const stagger = (vis) => `transition-all duration-700 ${vis ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}`;
const staggerDelay = (idx) => ({ transitionDelay: `${idx * 80}ms` });

export default function ServicesPage() {
  const { t, i18n } = useTranslation();
  const isEN = i18n.language === 'en';
  const [heroRef, heroVis] = useInView(0.1);
  const [gridRef, gridVis] = useInView(0.1);
  const [locRef, locVis] = useInView(0.1);
  const [procRef, procVis] = useInView(0.1);
  const [ctaRef, ctaVis] = useInView(0.1);

  const PROCESS_STEPS = [
    { num: '01', titleKey: 'services_page.steps.apply.title', descKey: 'services_page.steps.apply.desc' },
    { num: '02', titleKey: 'services_page.steps.check.title', descKey: 'services_page.steps.check.desc' },
    { num: '03', titleKey: 'services_page.steps.confirm.title', descKey: 'services_page.steps.confirm.desc' },
    { num: '04', titleKey: 'services_page.steps.start.title', descKey: 'services_page.steps.start.desc' },
  ];

  return (
    <div className="min-h-screen bg-white">
      <SEOHead titleKey="seo.services_title" descKey="seo.services_desc" path="/services" />
      <PublicNav />
      <main className="pt-16">

        {/* ═══ HERO ═══ */}
        <section ref={heroRef} className="relative overflow-hidden py-[72px] lg:py-[96px]"
          style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' }}>
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12 relative z-10">
            <div className={`max-w-[640px] ${stagger(heroVis)}`}>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-6 h-[2px]" style={{ background: 'var(--color-accent)' }} />
                <span className="text-[11px] font-semibold tracking-[0.2em] uppercase" style={{ color: 'var(--color-accent)' }}>
                  {isEN ? 'Our Services' : 'Unsere Leistungen'}
                </span>
              </div>
              <h1 className="text-[36px] sm:text-[48px] lg:text-[56px] font-extrabold text-white leading-[1.08] tracking-[-0.03em] mb-6"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('services_page.hero_title')}
              </h1>
              <p className="text-[15px] lg:text-[17px] text-white/40 leading-[1.7] max-w-[520px]">
                {t('services_page.hero_sub')}
              </p>
            </div>
          </div>
        </section>

        {/* ═══ SERVICES-GRID ═══ */}
        <section ref={gridRef} className="py-[56px] lg:py-[80px]">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {SERVICE_KEYS.map((key, idx) => {
                const Icon = SERVICE_ICONS[key];
                const link = SERVICE_LINKS[key];
                return (
                  <div key={key} className={`p-6 lg:p-8 rounded-[8px] border border-[var(--color-primary)]/8 transition-all duration-300 hover:border-[var(--color-primary)]/15 group ${stagger(gridVis)}`}
                    style={{ ...staggerDelay(idx), boxShadow: '0 2px 12px rgba(17,54,85,0.04)' }}
                    id={`service-${key}`}
                    data-testid={`service-card-${key}`}>
                    <div className="w2g-icon-wrap mb-5">
                      <Icon size={20} />
                    </div>
                    <h3 className="text-[17px] font-bold text-[var(--color-primary-dark)] mb-2" style={{ fontFamily: 'var(--font-heading)' }}>
                      {t(`services.${key}.name`)}
                    </h3>
                    <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7] mb-4">
                      {t(`services.${key}.desc`)}
                    </p>
                    {link && (
                      <a href={link} target="_blank" rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-[13px] font-semibold transition-all hover:gap-2.5"
                        style={{ color: 'var(--color-primary)' }}>
                        {isEN ? 'Learn more' : 'Mehr erfahren'} <ExternalLink size={12} />
                      </a>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* ═══ STANDORT ═══ */}
        <section ref={locRef} className="py-[56px] lg:py-[80px] bg-[var(--color-surface-sunken)]">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16 items-center">
              <div className={`lg:col-span-5 ${stagger(locVis)}`}>
                <div className="rounded-[4px] overflow-hidden h-[300px] lg:h-[380px]"
                  style={{ boxShadow: '0 16px 48px rgba(17,54,85,0.1)' }}>
                  <img src="/images/location/aachen-dom.jpg" alt="Aachen Dom"
                    className="w-full h-full object-cover"
                    onError={e => { e.target.style.display = 'none'; }} />
                </div>
              </div>
              <div className={`lg:col-span-7 ${stagger(locVis)}`} style={staggerDelay(1)}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-6 h-[2px]" style={{ background: 'var(--color-accent)' }} />
                  <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">
                    {isEN ? 'Location' : 'Standort'}
                  </span>
                </div>
                <h2 className="text-[32px] sm:text-[40px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-5"
                  style={{ fontFamily: 'var(--font-heading)' }}>
                  {t('services_page.location_title')}
                </h2>
                <p className="text-[15px] text-[var(--color-text-secondary)] leading-[1.7] mb-8">
                  {t('services_page.location_desc')}
                </p>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w2g-icon-wrap-sm shrink-0"><MapPin size={16} /></div>
                    <div>
                      <p className="text-[14px] font-semibold text-[var(--color-primary-dark)]">Theaterstraße 30–32, 52062 Aachen</p>
                      <p className="text-[12px] text-[var(--color-text-secondary)]">{isEN ? 'Teaching & Consulting' : 'Unterricht & Beratung'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w2g-icon-wrap-sm shrink-0"><Clock size={16} /></div>
                    <div>
                      <p className="text-[14px] font-semibold text-[var(--color-primary-dark)]">{isEN ? 'Mon–Fri: 9:00 AM – 5:00 PM' : 'Mo–Fr: 9:00–17:00 Uhr'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w2g-icon-wrap-sm shrink-0"><Phone size={16} /></div>
                    <a href="tel:+4924199032292" className="text-[14px] font-semibold text-[var(--color-primary-dark)] hover:underline">+49 241 990 322 92</a>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w2g-icon-wrap-sm shrink-0"><Mail size={16} /></div>
                    <a href="mailto:info@stk-aachen.de" className="text-[14px] font-semibold text-[var(--color-primary-dark)] hover:underline">info@stk-aachen.de</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ═══ PROZESS ═══ */}
        <section ref={procRef} className="py-[56px] lg:py-[80px]">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className={`text-center mb-12 ${stagger(procVis)}`}>
              <h2 className="text-[32px] sm:text-[40px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-4"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('services_page.process_title')}
              </h2>
              <p className="text-[15px] text-[var(--color-text-secondary)] leading-[1.7] max-w-[480px] mx-auto">
                {t('services_page.process_desc')}
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {PROCESS_STEPS.map((step, idx) => (
                <div key={step.num} className={`p-6 rounded-[8px] border border-[var(--color-primary)]/6 ${stagger(procVis)}`}
                  style={staggerDelay(idx)} data-testid={`process-step-${step.num}`}>
                  <span className="text-[28px] font-extrabold mb-4 block"
                    style={{ color: 'var(--color-accent)', fontFamily: 'var(--font-heading)' }}>
                    {step.num}
                  </span>
                  <h3 className="text-[15px] font-bold text-[var(--color-primary-dark)] mb-2" style={{ fontFamily: 'var(--font-heading)' }}>
                    {t(step.titleKey)}
                  </h3>
                  <p className="text-[13px] text-[var(--color-text-secondary)] leading-[1.7]">{t(step.descKey)}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ═══ CTA ═══ */}
        <section ref={ctaRef} className="relative py-[72px] lg:py-[96px] overflow-hidden"
          style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' }}>
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />
          <div className="max-w-[640px] mx-auto px-6 lg:px-12 text-center relative z-10">
            <div className={stagger(ctaVis)}>
              <h2 className="text-[32px] sm:text-[40px] font-extrabold text-white leading-[1.1] tracking-[-0.025em] mb-4"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('services_page.cta_title')}
              </h2>
              <p className="text-[15px] text-white/40 leading-[1.7] mb-8">{t('services_page.cta_desc')}</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/apply" data-testid="services-cta-apply"
                  className="inline-flex items-center justify-center gap-2.5 h-[52px] px-10 text-[14px] font-bold rounded-full transition-all hover:scale-[1.02] group"
                  style={{ background: 'var(--color-accent)', color: 'var(--color-primary-dark)' }}>
                  {t('services_page.cta_apply')} <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
                </Link>
                <Link to="/contact" data-testid="services-cta-contact"
                  className="inline-flex items-center justify-center h-[52px] px-8 text-[14px] font-semibold text-white/70 border-2 border-white/15 rounded-full transition-all hover:border-white/30 hover:text-white">
                  {t('services_page.cta_contact')}
                </Link>
              </div>
            </div>
          </div>
        </section>

      </main>
      <PublicFooter />
    </div>
  );
}
