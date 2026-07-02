import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';
import { Phone, Mail, MessageCircle, MapPin, Clock, ArrowRight, Send } from 'lucide-react';

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

export default function ContactPage() {
  const { t, i18n } = useTranslation();
  const isEN = i18n.language === 'en';
  const [heroRef, heroVis] = useInView(0.1);
  const [mainRef, mainVis] = useInView(0.1);

  return (
    <div className="min-h-screen bg-white">
      <SEOHead titleKey="seo.contact_title" descKey="seo.contact_desc" path="/contact" />
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
                  {isEN ? 'Get in Touch' : 'Kontakt'}
                </span>
              </div>
              <h1 className="text-[36px] sm:text-[48px] lg:text-[56px] font-extrabold text-white leading-[1.08] tracking-[-0.03em] mb-6"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('contact_page.title')}
              </h1>
              <p className="text-[15px] lg:text-[17px] text-white/40 leading-[1.7] max-w-[520px]">
                {t('contact_page.sub')}
              </p>
            </div>
          </div>
        </section>

        {/* ═══ CONTENT ═══ */}
        <section ref={mainRef} className="py-[56px] lg:py-[80px]">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16">

              {/* LINKS: Kontaktdaten */}
              <div className={`lg:col-span-5 ${stagger(mainVis)}`}>
                {/* Standort-Karte */}
                <div className="p-6 lg:p-8 rounded-[4px] mb-6"
                  style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)', boxShadow: '0 16px 48px rgba(17,54,85,0.15)' }}>
                  <p className="text-[11px] font-semibold tracking-[0.15em] uppercase mb-5" style={{ color: 'var(--color-accent)' }}>
                    {t('contact_page.standort_label')}
                  </p>
                  <div className="space-y-4 text-[14px] text-white/70">
                    <div className="flex items-start gap-3">
                      <div className="w2g-icon-wrap-dark shrink-0"><MapPin size={16} /></div>
                      <div>
                        <p className="font-semibold text-white">Theaterstraße 30–32</p>
                        <p>52062 Aachen</p>
                        <p className="text-[12px] text-white/40 mt-1">{t('contact_page.office_note')}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w2g-icon-wrap-dark shrink-0"><Phone size={16} /></div>
                      <a href="tel:+4924199032292" className="hover:text-white transition-colors font-semibold text-white">
                        +49 241 990 322 92
                      </a>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w2g-icon-wrap-dark shrink-0"><Mail size={16} /></div>
                      <a href="mailto:info@stk-aachen.de" className="hover:text-white transition-colors font-semibold text-white">
                        info@stk-aachen.de
                      </a>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w2g-icon-wrap-dark shrink-0"><MessageCircle size={16} /></div>
                      <a href="https://wa.me/4915208496876" target="_blank" rel="noopener noreferrer"
                        className="hover:text-white transition-colors font-semibold text-white">WhatsApp</a>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w2g-icon-wrap-dark shrink-0"><Clock size={16} /></div>
                      <span className="text-white/60">{t('contact_page.hours_value')}</span>
                    </div>
                  </div>
                </div>

                {/* Gesellschaftssitz */}
                <div className="p-5 rounded-[8px] border border-[rgba(10,25,47,0.08)]" style={{ boxShadow: '0 2px 8px rgba(17,54,85,0.03)' }}>
                  <p className="text-[11px] font-semibold tracking-[0.15em] uppercase text-[rgba(10,25,47,0.6)] mb-3">
                    {t('contact_page.registered_label')}
                  </p>
                  <p className="text-[14px] font-bold text-[var(--color-primary-dark)] mb-1">W2G Academy GmbH</p>
                  <p className="text-[13px] text-[var(--color-text-secondary)]">Theaterstraße 24 · 52062 Aachen</p>
                  <p className="text-[11px] text-[rgba(71,85,105,0.6)] mt-1">HRB 23610 · Amtsgericht Aachen</p>
                </div>
              </div>

              {/* RECHTS: CTA-Karten */}
              <div className={`lg:col-span-7 space-y-5 ${stagger(mainVis)}`} style={staggerDelay(1)}>

                {/* Bewerbung CTA */}
                <div className="p-6 lg:p-8 rounded-[4px] border-2 transition-colors"
                  style={{ borderColor: 'rgba(212,175,55,0.25)', boxShadow: '0 4px 16px rgba(212,175,55,0.06)' }}>
                  <h2 className="text-[20px] font-bold text-[var(--color-primary-dark)] mb-2" style={{ fontFamily: 'var(--font-heading)' }}>
                    {t('contact_page.cta_apply_title')}
                  </h2>
                  <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7] mb-6">
                    {t('contact_page.cta_apply_desc')}
                  </p>
                  <Link to="/apply" data-testid="contact-apply-btn"
                    className="inline-flex items-center gap-2.5 h-[48px] px-8 text-[14px] font-bold rounded-full transition-all hover:scale-[1.02] group"
                    style={{ background: 'var(--color-accent)', color: 'var(--color-primary-dark)' }}>
                    {t('contact_page.cta_apply_btn')} <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </div>

                {/* WhatsApp CTA */}
                <div className="p-6 lg:p-8 rounded-[8px] border border-[rgba(10,25,47,0.08)]" style={{ boxShadow: '0 2px 12px rgba(17,54,85,0.04)' }}>
                  <h2 className="text-[20px] font-bold text-[var(--color-primary-dark)] mb-2" style={{ fontFamily: 'var(--font-heading)' }}>
                    {t('contact_page.whatsapp_title')}
                  </h2>
                  <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7] mb-6">
                    {t('contact_page.whatsapp_desc')}
                  </p>
                  <a href="https://wa.me/4915208496876" target="_blank" rel="noopener noreferrer"
                    data-testid="contact-whatsapp-btn"
                    className="inline-flex items-center gap-2.5 h-[48px] px-8 text-[14px] font-bold rounded-full text-white transition-all hover:scale-[1.02]"
                    style={{ background: 'var(--color-primary-dark)' }}>
                    <MessageCircle size={16} /> WhatsApp {isEN ? 'Chat' : 'schreiben'}
                  </a>
                </div>

                {/* Beratungstermin CTA */}
                <div className="p-6 lg:p-8 rounded-[8px] border border-[rgba(10,25,47,0.08)]" style={{ boxShadow: '0 2px 12px rgba(17,54,85,0.04)' }}>
                  <h2 className="text-[20px] font-bold text-[var(--color-primary-dark)] mb-2" style={{ fontFamily: 'var(--font-heading)' }}>
                    {isEN ? 'Book a Consultation' : 'Beratungstermin buchen'}
                  </h2>
                  <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7] mb-6">
                    {isEN
                      ? 'Schedule a free, personal consultation with our team. We will discuss your options and guide you through the next steps.'
                      : 'Vereinbare einen kostenlosen, persönlichen Beratungstermin mit unserem Team. Wir besprechen deine Möglichkeiten und begleiten dich durch die nächsten Schritte.'}
                  </p>
                  <Link to="/booking" data-testid="contact-booking-btn"
                    className="inline-flex items-center gap-2.5 h-[48px] px-8 text-[14px] font-semibold rounded-full border-2 border-[var(--color-primary)] text-[var(--color-primary)] transition-all hover:bg-[var(--color-primary-dark)] hover:text-white hover:border-[var(--color-primary-dark)]">
                    {isEN ? 'Book Now' : 'Termin vereinbaren'} <Send size={14} />
                  </Link>
                </div>

                {/* Rechtliche Links */}
                <div className="pt-4 border-t border-[rgba(10,25,47,0.06)]">
                  <p className="text-[12px] text-[var(--color-text-secondary)]">
                    {t('contact_page.legal_link_note')}{' '}
                    <Link to="/legal" className="font-semibold hover:underline" style={{ color: 'var(--color-primary)' }}>{t('contact_page.impressum_link')}</Link>
                    {' · '}
                    <Link to="/privacy" className="font-semibold hover:underline" style={{ color: 'var(--color-primary)' }}>{t('contact_page.privacy_link')}</Link>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>
      <PublicFooter />
    </div>
  );
}
