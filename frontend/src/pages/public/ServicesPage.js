import React from 'react';
import { Link } from 'react-router-dom';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import { Plane, Home, Heart, FileCheck, GraduationCap, ShieldCheck, ArrowRight } from 'lucide-react';

// Echte Bilder von studienkollegaachen.de
const AACHEN_GRAPHIC = "https://www.studienkollegaachen.de/images/grafik_hi_aachen_deutschkurs_german_course_a1_c1-380.webp";

const SERVICES = [
  {
    icon: Plane,
    key: 'visa',
    title: 'Visaunterstützung',
    desc: 'Wir begleiten dich bei der Zusammenstellung aller Visa-Dokumente, Bescheinigungen, Übersetzungen und behördlichen Anforderungen.',
    link: 'https://digital.diplo.de/studium',
    linkLabel: 'Visa-Infoportal',
    highlight: true,
  },
  {
    icon: Home,
    key: 'housing',
    title: 'Unterkunft in Aachen',
    desc: 'Möblierte, bezugsbereite Unterkünfte in Aachen – wir vermitteln passende Wohnlösungen vor deiner Ankunft.',
    link: 'https://stayinaachen.de/',
    linkLabel: 'stayinaachen.de',
  },
  {
    icon: Heart,
    key: 'mentoring',
    title: 'Mentoring & Begleitung',
    desc: 'Persönliche Berater, regelmäßige Check-ins und individuelle Orientierungsunterstützung für einen guten Start.',
  },
  {
    icon: FileCheck,
    key: 'documents',
    title: 'Zeugnisanerkennung',
    desc: 'Wir begleiten dich beim Anerkennungsprozess deiner Schulzeugnisse und Abschlüsse durch deutsche Behörden.',
  },
  {
    icon: GraduationCap,
    key: 'uni',
    title: 'Uni-Bewerbungscoaching',
    desc: 'Von der Kursauswahl über uni-assist bis zur Hochschulbewerbung – wir begleiten dich durch den gesamten Prozess.',
  },
  {
    icon: ShieldCheck,
    key: 'insurance',
    title: 'Krankenversicherung',
    desc: 'Vollständige Versicherungslösungen, die alle Visa- und Hochschulanforderungen erfüllen.',
    link: 'https://www.care-concept.de',
    linkLabel: 'Zu unserem Partner',
  },
];

export default function ServicesPage() {
  return (
    <div className="min-h-screen bg-white">
      <PublicNav />
      <main className="pt-16">

        {/* Hero */}
        <section className="bg-primary py-16 sm:py-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-heading font-bold text-white mb-4">
              Unsere Services
            </h1>
            <p className="text-blue-200 text-base sm:text-lg max-w-xl mx-auto leading-relaxed">
              Wir begleiten dich weit über den Unterricht hinaus –
              von der ersten Anfrage bis zum ersten Semester in Deutschland.
            </p>
          </div>
        </section>

        {/* Services-Grid */}
        <section className="py-16 sm:py-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {SERVICES.map(service => {
                const Icon = service.icon;
                return (
                  <div
                    key={service.key}
                    className={`bg-white border rounded-sm p-6 hover:-translate-y-1 hover:shadow-card-hover transition-all duration-300 ${
                      service.highlight ? 'border-primary/30' : 'border-slate-200'
                    }`}
                    data-testid={`service-card-${service.key}`}
                  >
                    <div className="w-10 h-10 bg-primary/8 border border-primary/15 rounded-sm flex items-center justify-center mb-5">
                      <Icon size={18} className="text-primary" />
                    </div>
                    <h3 className="font-heading font-bold text-primary text-lg mb-2">{service.title}</h3>
                    <p className="text-slate-600 text-sm leading-relaxed mb-4">{service.desc}</p>
                    {service.link && (
                      <a href={service.link} target="_blank" rel="noopener noreferrer"
                        className="text-primary text-sm font-medium hover:underline flex items-center gap-1">
                        {service.linkLabel} <ArrowRight size={13} />
                      </a>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Aachen-Grafik + Standort-Info */}
        <section className="py-16 sm:py-20 bg-slate-50 border-t border-b border-slate-100">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
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
                  Unser Standort in Aachen
                </h2>
                <p className="text-slate-600 mb-5 leading-relaxed">
                  Das Studienkolleg Aachen befindet sich zentral in der Stadt – gut erreichbar,
                  international vernetzt und direkt im Herzen einer der führenden
                  Hochschulstädte Deutschlands.
                </p>
                <div className="space-y-3">
                  {[
                    { label: 'Unterricht & Beratung', val: 'Theaterstraße 30–32, 52062 Aachen' },
                    { label: 'Bürozeiten', val: 'Mo–Fr: 9:00–17:00 Uhr' },
                    { label: 'Kontakt', val: 'info@stk-aachen.de · +49 241 990 322 92' },
                  ].map(item => (
                    <div key={item.label} className="flex gap-3 text-sm">
                      <span className="text-slate-400 w-36 shrink-0">{item.label}:</span>
                      <span className="text-slate-700 font-medium">{item.val}</span>
                    </div>
                  ))}
                </div>
                <Link to="/contact"
                  className="mt-6 inline-flex items-center gap-2 border-2 border-primary text-primary font-semibold px-5 py-2.5 rounded-sm hover:bg-primary hover:text-white transition-all text-sm"
                  data-testid="services-contact-btn">
                  Kontakt aufnehmen <ArrowRight size={15} />
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Prozess-Überblick */}
        <section className="py-16 sm:py-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <h2 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-3 text-center">
              Wie wir dich begleiten
            </h2>
            <p className="text-slate-600 text-center mb-10 max-w-lg mx-auto">
              Von der ersten Kontaktaufnahme bis zum erfolgreichen Kursabschluss.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {[
                { step: '01', title: 'Erstberatung', desc: 'Wir prüfen deine Unterlagen und empfehlen den passenden Kurs.' },
                { step: '02', title: 'Visa & Formalitäten', desc: 'Wir unterstützen beim Visum, der Anmeldung und allen Behördengängen.' },
                { step: '03', title: 'Unterkunft & Anreise', desc: 'Deine Unterkunft ist bereit, bevor du ankommst.' },
                { step: '04', title: 'Kurs & Prüfung', desc: 'Intensiver Unterricht, Prüfungsvorbereitung und persönliche Begleitung.' },
              ].map(item => (
                <div key={item.step}
                  className="bg-white border border-slate-200 rounded-sm p-5"
                  data-testid={`process-step-${item.step}`}>
                  <span className="inline-block w-8 h-8 bg-primary text-white text-xs font-bold rounded-sm flex items-center justify-center mb-4">
                    {item.step}
                  </span>
                  <h3 className="font-semibold text-slate-800 text-sm mb-2">{item.title}</h3>
                  <p className="text-slate-500 text-xs leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="bg-primary py-16">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 text-center">
            <h2 className="text-2xl sm:text-3xl font-heading font-bold text-white mb-4">
              Bereit loszulegen?
            </h2>
            <p className="text-blue-200 mb-8 max-w-lg mx-auto">
              Bewirb dich jetzt und erhalte innerhalb von 24 Stunden eine persönliche Rückmeldung.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/apply"
                data-testid="services-cta-apply"
                className="bg-white text-primary font-semibold px-8 py-3.5 rounded-sm hover:bg-slate-50 transition-all inline-flex items-center justify-center gap-2">
                Jetzt bewerben <ArrowRight size={16} />
              </Link>
              <Link to="/contact"
                data-testid="services-cta-contact"
                className="border-2 border-white/40 text-white font-semibold px-8 py-3.5 rounded-sm hover:border-white/70 transition-all inline-flex items-center justify-center">
                Beratung anfragen
              </Link>
            </div>
          </div>
        </section>

      </main>
      <PublicFooter />
    </div>
  );
}
