import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import {
  CheckCircle, Star, ChevronDown, ChevronUp, MapPin,
  Phone, ArrowRight, Shield, Users, BookOpen, Award
} from 'lucide-react';

const HERO_IMAGE = "https://images.pexels.com/photos/7683629/pexels-photo-7683629.jpeg";
const LIBRARY_IMAGE = "https://images.pexels.com/photos/9158999/pexels-photo-9158999.jpeg";

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

const COURSES = [
  { key: 't_course', color: 'bg-blue-50 border-blue-200', badge: 'T-Kurs', badgeColor: 'bg-blue-100 text-blue-700' },
  { key: 'm_course', color: 'bg-green-50 border-green-200', badge: 'M-Kurs', badgeColor: 'bg-green-100 text-green-700' },
  { key: 'w_course', color: 'bg-purple-50 border-purple-200', badge: 'W-Kurs', badgeColor: 'bg-purple-100 text-purple-700' },
  { key: 'mt_course', color: 'bg-orange-50 border-orange-200', badge: 'M/T-Kurs', badgeColor: 'bg-orange-100 text-orange-700' },
];

export default function HomePage() {
  const { t } = useTranslation();

  const trustItems = [
    { icon: Award, key: 'recognized' },
    { icon: Shield, key: 'allinone' },
    { icon: Users, key: 'community' },
    { icon: MapPin, key: 'central' },
  ];

  return (
    <div className="min-h-screen bg-white">
      <PublicNav />

      {/* Hero */}
      <section className="pt-16 bg-white" data-testid="hero-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center py-16 lg:py-24">
            <div className="animate-slide-up">
              <div className="inline-flex items-center gap-2 bg-accent/30 text-primary px-3 py-1.5 rounded-sm text-xs font-semibold mb-6 border border-accent">
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
                <CheckCircle size={14} className="text-green-500" />
                {t('hero.trust')}
              </p>
            </div>

            {/* Hero image */}
            <div className="relative hidden lg:block">
              <div className="absolute inset-0 bg-primary/5 rounded-sm transform rotate-3 scale-105"></div>
              <img src={HERO_IMAGE} alt="International students in Aachen"
                className="relative rounded-sm object-cover w-full h-[480px] shadow-card-hover"
                data-testid="hero-image" />
              {/* Floating badge */}
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
                    <Icon size={20} className="text-accent" />
                  </div>
                  <h3 className="font-semibold text-sm mb-1">{t(`trust.items.${item.key}.title`)}</h3>
                  <p className="text-blue-200 text-xs leading-relaxed">{t(`trust.items.${item.key}.desc`)}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Courses */}
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
                className={`border rounded-sm p-6 ${course.color} hover:-translate-y-1 hover:shadow-card-hover transition-all duration-300`}
                data-testid={`course-card-${course.key}`}>
                <span className={`inline-block text-xs font-bold px-2 py-1 rounded-sm mb-4 ${course.badgeColor}`}>
                  {course.badge}
                </span>
                <h3 className="font-heading font-bold text-primary text-lg mb-2">{t(`courses.${course.key}.name`)}</h3>
                <p className="text-slate-600 text-sm leading-relaxed">{t(`courses.${course.key}.desc`)}</p>
              </div>
            ))}
          </div>
          <div className="text-center mt-8">
            <Link to="/courses" className="text-primary font-semibold text-sm hover:underline flex items-center gap-1 justify-center">
              Alle Kurse ansehen <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* Process */}
      <section className="py-16 sm:py-24 bg-white" data-testid="process-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-4">
                So funktioniert der Prozess
              </h2>
              <p className="text-slate-600 mb-8">
                Von der Anfrage bis zum Studienkolleg – digital, transparent, persönlich.
              </p>
              <div className="space-y-4">
                {[
                  { step: '01', title: 'Bewerbung einreichen', desc: 'Fülle das kurze Formular aus. Wir melden uns innerhalb von 24 Stunden.' },
                  { step: '02', title: 'Portalzugang erhalten', desc: 'Du bekommst dein persönliches Portal mit klarem Aufgaben-Dashboard.' },
                  { step: '03', title: 'Dokumente hochladen', desc: 'Sichere, strukturierte Dokumentenverwaltung – alles an einem Ort.' },
                  { step: '04', title: 'Zulassung & Start', desc: 'Nach Prüfung und Zahlung erhältst du deinen Admission Letter.' },
                ].map(item => (
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
                Jetzt bewerben <ArrowRight size={16} />
              </Link>
            </div>
            <div className="hidden lg:block">
              <img src={LIBRARY_IMAGE} alt="Student studying"
                className="rounded-sm object-cover w-full h-[400px] shadow-card-hover" />
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
            <p className="text-slate-600 text-sm mb-3">Weitere Fragen?</p>
            <Link to="/contact" data-testid="faq-contact-link"
              className="text-primary font-semibold hover:underline text-sm flex items-center gap-1 justify-center">
              Kontakt aufnehmen <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="bg-primary py-16" data-testid="cta-banner">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl sm:text-3xl font-heading font-bold text-white mb-4">
            Bereit, deinen Weg zu starten?
          </h2>
          <p className="text-blue-200 mb-8 max-w-xl mx-auto">
            Bewirb dich jetzt und erhalte innerhalb von 24 Stunden deinen persönlichen Portalzugang.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/apply" data-testid="bottom-cta-apply"
              className="bg-white text-primary font-semibold px-8 py-3.5 rounded-sm hover:bg-slate-50 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2">
              Jetzt bewerben <ArrowRight size={18} />
            </Link>
            <Link to="/contact" data-testid="bottom-cta-contact"
              className="border-2 border-white/40 text-white font-semibold px-8 py-3.5 rounded-sm hover:border-white/70 transition-all flex items-center justify-center">
              Kostenlose Beratung
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
