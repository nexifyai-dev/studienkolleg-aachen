import React from 'react';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import { MapPin, Phone, Mail, MessageCircle, Clock } from 'lucide-react';

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-white">
      <PublicNav />
      <main className="pt-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-16">
          <div className="text-center mb-12">
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-primary mb-3">Kontakt</h1>
            <p className="text-slate-600">Wir sind für dich da – persönlich, schnell und zuverlässig.</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-4">
              {[
                { icon: MapPin, title: 'Adresse', value: 'Theaterstraße 30-32, 52062 Aachen', note: '[OFFEN – nicht abschließend verifiziert]', href: null },
                { icon: Phone, title: 'Telefon', value: '+49 241 990 322 92', href: 'tel:+4924199032292' },
                { icon: Mail, title: 'E-Mail', value: 'info@stk-aachen.de', href: 'mailto:info@stk-aachen.de' },
                { icon: MessageCircle, title: 'WhatsApp', value: 'WhatsApp-Kontakt', href: 'https://api.whatsapp.com/message/RVKVWFEKNCIRG1?autoload=1&app_absent=0' },
                { icon: Clock, title: 'Bürozeiten', value: 'Mo–Fr: 9:00 – 17:00 Uhr', href: null },
              ].map(item => {
                const Icon = item.icon;
                return (
                  <div key={item.title} className="flex gap-4 p-4 border border-slate-100 rounded-sm hover:border-primary/20 transition-colors"
                    data-testid={`contact-item-${item.title.toLowerCase()}`}>
                    <div className="w-10 h-10 bg-accent/30 rounded-sm flex items-center justify-center shrink-0">
                      <Icon size={18} className="text-primary" />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-slate-500 mb-0.5">{item.title}</p>
                      {item.href ? (
                        <a href={item.href} target="_blank" rel="noopener noreferrer"
                          className="text-sm font-medium text-primary hover:underline">{item.value}</a>
                      ) : (
                        <p className="text-sm font-medium text-slate-800">{item.value}</p>
                      )}
                      {item.note && <p className="text-xs text-amber-600 mt-0.5">{item.note}</p>}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="bg-slate-50 rounded-sm border border-slate-100 p-6">
              <h3 className="font-heading font-bold text-primary mb-4">Kurze Anfrage senden</h3>
              <p className="text-slate-600 text-sm mb-6">Oder bewirb dich direkt über unser strukturiertes Bewerbungsformular.</p>
              <a href="/apply"
                className="block w-full bg-primary text-white text-center font-semibold py-3 rounded-sm hover:bg-primary-hover transition-colors"
                data-testid="contact-apply-btn">
                Jetzt bewerben →
              </a>
            </div>
          </div>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
