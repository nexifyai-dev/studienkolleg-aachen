import React from 'react';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import { MapPin, Phone, Mail, MessageCircle, Clock, Building2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-white">
      <PublicNav />
      <main className="pt-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
          <div className="text-center mb-8 sm:mb-12">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-heading font-bold text-primary mb-3">Kontakt</h1>
            <p className="text-slate-600 max-w-md mx-auto">
              Wir sind für dich da – persönlich, schnell und zuverlässig.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">

            {/* Linke Spalte: Kontaktdaten */}
            <div className="lg:col-span-3 space-y-6">

              {/* Bewerber-/Standortkontakt */}
              <div>
                <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3 flex items-center gap-2">
                  <MapPin size={13} /> Studienkolleg / Way2Germany
                </h2>
                <div className="space-y-3">
                  <ContactItem
                    icon={MapPin}
                    title="Standort"
                    value="Theaterstraße 30–32, 52062 Aachen"
                    note="Unterricht, Beratung, Way2Germany Office"
                    href={`https://www.google.com/maps/search/?api=1&query=Theaterstrasse+30-32+Aachen`}
                    external
                  />
                  <ContactItem
                    icon={Phone}
                    title="Telefon"
                    value="+49 241 990 322 92"
                    href="tel:+4924199032292"
                  />
                  <ContactItem
                    icon={Mail}
                    title="E-Mail"
                    value="info@stk-aachen.de"
                    href="mailto:info@stk-aachen.de"
                  />
                  <ContactItem
                    icon={MessageCircle}
                    title="WhatsApp"
                    value="WhatsApp schreiben"
                    href="https://api.whatsapp.com/message/RVKVWFEKNCIRG1?autoload=1&app_absent=0"
                    external
                  />
                  <ContactItem
                    icon={Clock}
                    title="Bürozeiten"
                    value="Mo–Fr: 9:00 – 17:00 Uhr"
                  />
                </div>
              </div>

              {/* Gesellschaftssitz */}
              <div className="pt-4 border-t border-slate-100">
                <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3 flex items-center gap-2">
                  <Building2 size={13} /> Gesellschaftssitz
                </h2>
                <div className="bg-slate-50 rounded-sm border border-slate-200 p-4">
                  <p className="text-sm font-semibold text-slate-800 mb-1">W2G Academy GmbH</p>
                  <p className="text-sm text-slate-600">Theaterstraße 24 · 52062 Aachen</p>
                  <p className="text-sm text-slate-600">Amtsgericht Aachen · HRB 23610</p>
                  <p className="text-sm text-slate-600 mt-1">Geschäftsführerin: Laura Saboor</p>
                  <p className="text-xs text-slate-400 mt-2">
                    Rechtliche Angaben gemäß § 5 TMG –
                    <Link to="/legal" className="text-primary hover:underline ml-1">Impressum</Link>
                  </p>
                </div>
              </div>
            </div>

            {/* Rechte Spalte: CTA */}
            <div className="lg:col-span-2 space-y-4">
              <div className="bg-primary rounded-sm p-6 text-white">
                <h3 className="font-heading font-bold text-lg mb-2">Jetzt bewerben</h3>
                <p className="text-white/70 text-sm mb-5 leading-relaxed">
                  Starte deine Bewerbung mit dem vollständigen Online-Formular.
                  Wir melden uns innerhalb von 24 Stunden.
                </p>
                <Link to="/apply"
                  data-testid="contact-apply-btn"
                  className="block w-full bg-white text-primary text-center font-semibold py-3 rounded-sm hover:bg-slate-50 transition-colors text-sm">
                  Jetzt bewerben →
                </Link>
              </div>

              <div className="bg-slate-50 rounded-sm border border-slate-200 p-5">
                <h3 className="font-semibold text-slate-800 text-sm mb-2">Direkter WhatsApp-Kontakt</h3>
                <p className="text-slate-600 text-xs mb-3 leading-relaxed">
                  Schnelle Fragen, Dokument-Checks oder Terminabstimmung –
                  wir antworten werktags in der Regel innerhalb weniger Stunden.
                </p>
                <a href="https://api.whatsapp.com/message/RVKVWFEKNCIRG1?autoload=1&app_absent=0"
                  target="_blank" rel="noopener noreferrer"
                  data-testid="contact-whatsapp-btn"
                  className="block w-full bg-slate-800 text-white text-center font-semibold py-2.5 rounded-sm hover:bg-slate-900 transition-colors text-sm">
                  WhatsApp öffnen
                </a>
              </div>

              <div className="bg-white rounded-sm border border-slate-200 p-4">
                <p className="text-xs text-slate-500 leading-relaxed">
                  <strong className="text-slate-700">Datenschutzhinweis:</strong> Deine Kontaktdaten
                  werden ausschließlich zur Bearbeitung deiner Anfrage verwendet.
                  Mehr: <Link to="/privacy" className="text-primary hover:underline">Datenschutzerklärung</Link>
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

function ContactItem({ icon: Icon, title, value, href, note, external }) {
  return (
    <div className="flex gap-3 p-3.5 bg-white border border-slate-100 rounded-sm hover:border-primary/20 transition-colors"
      data-testid={`contact-item-${title.toLowerCase()}`}>
      <div className="w-9 h-9 bg-primary/8 rounded-sm flex items-center justify-center shrink-0 border border-primary/15">
        <Icon size={16} className="text-primary" />
      </div>
      <div>
        <p className="text-xs font-medium text-slate-400 mb-0.5">{title}</p>
        {href ? (
          <a href={href} target={external ? '_blank' : undefined}
            rel={external ? 'noopener noreferrer' : undefined}
            className="text-sm font-medium text-primary hover:underline">
            {value}
          </a>
        ) : (
          <p className="text-sm font-medium text-slate-800">{value}</p>
        )}
        {note && <p className="text-xs text-slate-400 mt-0.5">{note}</p>}
      </div>
    </div>
  );
}
