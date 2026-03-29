import React from 'react';
import { Link } from 'react-router-dom';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import { Plane, Home, Heart, FileCheck, GraduationCap, ShieldCheck } from 'lucide-react';

const SERVICES = [
  { icon: Plane, title: 'Visaunterstützung', desc: 'Wir helfen bei allen notwendigen Visa-Dokumenten, Bescheinigungen und Übersetzungen.', link: 'https://digital.diplo.de/studium', linkLabel: 'Mehr erfahren' },
  { icon: Home, title: 'Unterkunft in Aachen', desc: 'Möblierte Unterkunftslösungen in Aachen – bereit vor deiner Ankunft.', link: 'https://stayinaachen.de/', linkLabel: 'stayinaachen.de' },
  { icon: Heart, title: 'Mentoring & Begleitung', desc: 'Persönliche Berater, regelmäßige Check-ins und Orientierungsunterstützung für einen guten Start in Deutschland.' },
  { icon: FileCheck, title: 'Zeugnisanerkennung', desc: 'Wir begleiten dich beim Anerkennungsprozess deiner Schulzeugnisse durch deutsche Behörden.' },
  { icon: GraduationCap, title: 'Uni-Bewerbungscoaching', desc: 'Von der Kursauswahl bis zum uni-assist – wir sind an deiner Seite.' },
  { icon: ShieldCheck, title: 'Krankenversicherung', desc: 'Vollständige Versicherungslösungen, die Visa- und Hochschulanforderungen erfüllen.', link: 'https://www.care-concept.de', linkLabel: 'Zu unserem Partner' },
];

export default function ServicesPage() {
  return (
    <div className="min-h-screen bg-white">
      <PublicNav />
      <main className="pt-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16">
          <div className="text-center mb-12">
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-primary mb-3">Unsere Services</h1>
            <p className="text-slate-600 max-w-xl mx-auto">
              Wir begleiten dich weit über den Unterricht hinaus – von der Visa-Vorbereitung bis zur Wohnungssuche.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {SERVICES.map(service => {
              const Icon = service.icon;
              return (
                <div key={service.title}
                  className="border border-slate-100 rounded-sm p-6 hover:-translate-y-1 hover:shadow-card-hover transition-all duration-300 bg-white"
                  data-testid={`service-card-${service.title.toLowerCase().replace(/ /g, '-')}`}>
                  <div className="w-10 h-10 bg-accent/30 rounded-sm flex items-center justify-center mb-4">
                    <Icon size={20} className="text-primary" />
                  </div>
                  <h3 className="font-heading font-bold text-primary text-lg mb-2">{service.title}</h3>
                  <p className="text-slate-600 text-sm leading-relaxed mb-4">{service.desc}</p>
                  {service.link && (
                    <a href={service.link} target="_blank" rel="noopener noreferrer"
                      className="text-primary text-sm font-medium hover:underline">{service.linkLabel} →</a>
                  )}
                </div>
              );
            })}
          </div>

          <div className="mt-12 text-center">
            <Link to="/apply" className="bg-primary text-white font-semibold px-8 py-3.5 rounded-sm hover:bg-primary-hover transition-colors inline-block"
              data-testid="services-apply-btn">
              Jetzt bewerben und loslegen →
            </Link>
          </div>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
