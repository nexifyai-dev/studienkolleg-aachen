import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';
import {
  CheckCircle, Star, ChevronDown, ChevronUp, MapPin,
  ArrowRight, Shield, Users, Award, Play
} from 'lucide-react';

const HERO_IMAGE = "https://www.studienkollegaachen.de/images/foto_1_startseite_studienkolleg_aachen_studium_germany_study_deutschland-1052.webp";
const AACHEN_GRAPHIC = "https://www.studienkollegaachen.de/images/grafik_hi_aachen_deutschkurs_german_course_a1_c1-380.webp";
const LOGO_W2G = "https://www.studienkollegaachen.de/images/logo_gross_studienkolleg_aachen_way_2_germany_studie_german_courses-684.webp";

const VIDEO_MAIN = "https://www.youtube.com/embed/oD9UIiTOT8E";
const VIDEO_SERVICES = "https://www.youtube.com/embed/kZ-sxLHH5-g";

function FAQItem({ q, a }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border-b border-slate-100">
      <button onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between py-4 text-left gap-4"
        data-testid="faq-item-toggle">
        <span className="font-medium text-slate-800 text-sm sm:text-base">{q}</span>
        {open ? <ChevronUp size={18} className="text-primary shrink-0" /> : <ChevronDown size={18} className="text-slate-400 shrink-0" />}
      </button>
      {open && <p className="pb-4 text-sm text-slate-600 leading-relaxed">{a}</p>}
    </div>
  );
}

function YouTubeEmbed({ src, title }) {
  const [loaded, setLoaded] = useState(false);
  return (
    <div className="relative bg-slate-900 rounded-sm overflow-hidden aspect-video shadow-card-hover">
      {!loaded && (
        <div className="absolute inset-0 flex items-center justify-center cursor-pointer" onClick={() => setLoaded(true)}>
          <img
            src={`https://img.youtube.com/vi/${src.split('/embed/')[1]}/hqdefault.jpg`}
            alt={title}
            className="w-full h-full object-cover"
            onError={e => { e.target.style.display = 'none'; }}
          />
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
            <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform">
              <Play size={24} fill="white" className="text-white ml-1" />
            </div>
          </div>
          <p className="absolute bottom-3 left-3 text-white text-sm font-medium drop-shadow">{title}</p>
        </div>
      )}
      {loaded && (
        <iframe
          className="w-full h-full absolute inset-0"
          src={`${src}?autoplay=1&rel=0`}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      )}
    </div>
  );
}

const COURSES = [
  { key: 't_course', badge: 'T-Kurs', accentColor: 'border-l-blue-500' },
  { key: 'm_course', badge: 'M-Kurs', accentColor: 'border-l-primary' },
  { key: 'w_course', badge: 'W-Kurs', accentColor: 'border-l-slate-500' },
  { key: 'mt_course', badge: 'M/T-Kurs', accentColor: 'border-l-slate-700' },
];

export default function HomePage() {
  const { t } = useTranslation();

  const trustItems = [
    { icon: Award, key: 'recognized' },
    { icon: Shield, key: 'allinone' },
    { icon: Users, key: 'community' },
    { icon: MapPin, key: 'central' },
  ];

  const processSteps = t('home.process_steps', { returnObjects: true });
  const videoBullets = t('home.video_bullets', { returnObjects: true });

  return (
    <div className="min-h-screen bg-white">
      <SEOHead titleKey="seo.home_title" descKey="seo.home_desc" path="/" />
      <PublicNav />
      <section className="pt-16 bg-white" data-testid="hero-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center py-16 lg:py-24">
            <div className="animate-slide-up">
              <div className="inline-flex items-center gap-2 bg-primary/8 text-primary px-3 py-1.5 rounded-sm text-xs font-semibold mb-6 border border-primary/20">
                <GraduationCap16 />
                {t('hero.badge')}
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-heading font-extrabold text-primary leading-tight tracking-tight text-balance mb-6">
                {t('hero.headline')}
              </h1>
              <p className="text-base sm:text-lg text-slate-600 leading-relaxed mb-8 max-w-lg">
                {t('hero.sub')}
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <Link to="/apply" data-testid="hero-cta-primary"
                  className="bg-primary text-white font-semibold px-6 py-3.5 rounded-sm hover:bg-primary-hover transition-all hover:-translate-y-0.5 hover:shadow-card-hover flex items-center justify-center gap-2">
                  {t('hero.cta_primary')}
                  <ArrowRight size={18} />
                </Link>
                <Link to="/contact" data-testid="hero-cta-secondary"
                  className="border-2 border-primary text-primary font-semibold px-6 py-3.5 rounded-sm hover:bg-slate-50 transition-all flex items-center justify-center gap-2">
                  {t('hero.cta_secondary')}
                </Link>
              </div>
              <p className="mt-6 text-xs text-slate-500 flex items-center gap-2">
                <CheckCircle size={14} className="text-primary" />
                {t('hero.trust')}
              </p>
            </div>

            <div className="relative hidden lg:block">
              <div className="absolute inset-0 bg-primary/5 rounded-sm transform rotate-3 scale-105"></div>
              <img
                src={HERO_IMAGE}
                alt="Studienkolleg Aachen"
                className="relative rounded-sm object-cover w-full h-[480px] shadow-card-hover"
                data-testid="hero-image"
                onError={e => { e.target.src = "https://images.pexels.com/photos/7683629/pexels-photo-7683629.jpeg"; }}
              />
              <div className="absolute bottom-6 left-6 bg-white rounded-sm shadow-card-hover p-4 flex items-center gap-3">
                <div className="flex">
                  {[...Array(5)].map((_, i) => <Star key={i} size={14} fill="#F59E0B" className="text-yellow-400" />)}
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-800">Google Bewertungen</p>
                  <p className="text-xs text-slate-500">Sehr gut bewertet</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust bar */}
      <section className="bg-primary py-8" data-testid="trust-bar">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {trustItems.map(item => {
              const Icon = item.icon;
              return (
                <div key={item.key} className="text-center text-white">
                  <div className="w-10 h-10 bg-white/10 rounded-sm flex items-center justify-center mx-auto mb-3">
                    <Icon size={20} className="text-white/80" />
                  </div>
                  <h3 className="font-semibold text-sm mb-1">{t(`trust.items.${item.key}.title`)}</h3>
                  <p className="text-white/70 text-xs leading-relaxed">{t(`trust.items.${item.key}.desc`)}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Kurse */}
      <section id="courses" className="py-16 sm:py-24 bg-slate-50" data-testid="courses-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-heading font-bold text-primary mb-4">
              {t('courses.title')}
            </h2>
            <p className="text-slate-600 max-w-xl mx-auto">{t('courses.sub')}</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {COURSES.map(course => (
              <div key={course.key}
                className={`bg-white border border-slate-200 border-l-4 ${course.accentColor} rounded-sm p-6 hover:-translate-y-1 hover:shadow-card-hover transition-all duration-300`}
                data-testid={`course-card-${course.key}`}>
                <span className="inline-block text-xs font-bold px-2.5 py-1 rounded-sm mb-4 bg-primary/8 text-primary border border-primary/20">
                  {course.badge}
                </span>
                <h3 className="font-heading font-bold text-primary text-lg mb-2">{t(`courses.${course.key}.name`)}</h3>
                <p className="text-slate-600 text-sm leading-relaxed">{t(`courses.${course.key}.desc`)}</p>
              </div>
            ))}
          </div>
          <div className="text-center mt-8">
            <Link to="/courses" className="text-primary font-semibold text-sm hover:underline flex items-center gap-1 justify-center">
              {t('courses.view_all')} <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* Video */}
      <section className="py-16 sm:py-24 bg-white" data-testid="video-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-4">
                {t('home.video_title')}
              </h2>
              <p className="text-slate-600 mb-6 leading-relaxed">
                {t('home.video_desc')}
              </p>
              <ul className="space-y-3 mb-8">
                {Array.isArray(videoBullets) && videoBullets.map((item, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-sm text-slate-700">
                    <CheckCircle size={16} className="text-primary mt-0.5 shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
              <Link to="/apply" data-testid="video-cta"
                className="inline-flex items-center gap-2 bg-primary text-white font-semibold px-6 py-3 rounded-sm hover:bg-primary-hover transition-all hover:-translate-y-0.5">
                {t('hero.cta_primary')} <ArrowRight size={16} />
              </Link>
            </div>
            <div>
              <YouTubeEmbed src={VIDEO_MAIN} title="Studienkolleg Aachen – Way2Germany" />
            </div>
          </div>
        </div>
      </section>

      {/* Services */}
      <section className="py-16 sm:py-24 bg-slate-50" data-testid="services-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-4">
              {t('services.title')}
            </h2>
            <p className="text-slate-600 max-w-xl mx-auto">
              {t('home.services_sub')}
            </p>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            <div>
              <YouTubeEmbed src={VIDEO_SERVICES} title={t('services.title')} />
            </div>
            <div className="space-y-4">
              <img
                src={AACHEN_GRAPHIC}
                alt="Deutschkurs Aachen A1-C1"
                className="w-full rounded-sm object-contain max-h-48"
                onError={e => { e.target.style.display = 'none'; }}
              />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {['visa', 'housing', 'mentoring', 'documents', 'uni', 'insurance'].map(key => (
                  <div key={key} className="bg-white border border-slate-100 rounded-sm p-4 hover:shadow-card transition-shadow">
                    <h4 className="font-semibold text-sm text-primary mb-1">{t(`services.${key}.name`)}</h4>
                    <p className="text-xs text-slate-600 leading-relaxed">{t(`services.${key}.desc`)}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Prozess */}
      <section className="py-16 sm:py-24 bg-white" data-testid="process-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-4">
                {t('home.process_title')}
              </h2>
              <p className="text-slate-600 mb-8">
                {t('home.process_desc')}
              </p>
              <div className="space-y-4">
                {Array.isArray(processSteps) && processSteps.map(item => (
                  <div key={item.step} className="flex gap-4 items-start" data-testid={`process-step-${item.step}`}>
                    <div className="w-8 h-8 bg-primary text-white rounded-sm flex items-center justify-center text-xs font-bold shrink-0">
                      {item.step}
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-800 text-sm">{item.title}</h4>
                      <p className="text-slate-600 text-sm mt-0.5">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
              <Link to="/apply" data-testid="process-cta"
                className="mt-8 inline-flex items-center gap-2 bg-primary text-white font-semibold px-6 py-3 rounded-sm hover:bg-primary-hover transition-all hover:-translate-y-0.5">
                {t('hero.cta_primary')} <ArrowRight size={16} />
              </Link>
            </div>
            <div className="hidden lg:flex flex-col items-center justify-center bg-primary rounded-sm p-12 border border-primary/20">
              <img
                src={LOGO_W2G}
                alt="Studienkolleg Aachen – Way2Germany"
                className="max-w-[200px] w-full object-contain brightness-0 invert"
                onError={e => { e.target.style.display = 'none'; }}
              />
              <div className="w-16 h-0.5 bg-white/20 my-6 rounded-full" />
              <p className="text-white/70 text-sm text-center max-w-xs leading-relaxed">
                {t('home.partner_text')}
              </p>
              <div className="mt-6 text-center">
                <p className="text-white/60 text-xs">W2G Academy GmbH</p>
                <p className="text-white/60 text-xs">Amtsgericht Aachen · HRB 23610</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-16 sm:py-24 bg-slate-50" data-testid="faq-section">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-4">
              {t('faq.title')}
            </h2>
          </div>
          <div className="bg-white rounded-sm border border-slate-100 shadow-card px-6">
            {t('faq.items', { returnObjects: true }).map((item, i) => (
              <FAQItem key={i} q={item.q} a={item.a} />
            ))}
          </div>
          <div className="mt-8 text-center">
            <p className="text-slate-600 text-sm mb-3">{t('home.faq_more')}</p>
            <Link to="/contact" data-testid="faq-contact-link"
              className="text-primary font-semibold hover:underline text-sm flex items-center gap-1 justify-center">
              {t('home.faq_contact')} <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="bg-primary py-16" data-testid="cta-banner">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl sm:text-3xl font-heading font-bold text-white mb-4">
            {t('home.cta_title')}
          </h2>
          <p className="text-white/70 mb-8 max-w-xl mx-auto">
            {t('home.cta_desc')}
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/apply" data-testid="bottom-cta-apply"
              className="bg-white text-primary font-semibold px-8 py-3.5 rounded-sm hover:bg-slate-50 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2">
              {t('hero.cta_primary')} <ArrowRight size={18} />
            </Link>
            <Link to="/contact" data-testid="bottom-cta-contact"
              className="border-2 border-white/40 text-white font-semibold px-8 py-3.5 rounded-sm hover:border-white/70 transition-all flex items-center justify-center">
              {t('home.cta_consultation')}
            </Link>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  );
}

function GraduationCap16() {
  return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m22 10-10-5-10 5 10 5 10-5z"/><path d="M6 12v6"/><path d="M18 12v6"/><path d="M12 17v4"/></svg>;
}
