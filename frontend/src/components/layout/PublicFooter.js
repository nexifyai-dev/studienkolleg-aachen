import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { GraduationCap, MapPin, Phone, Mail, MessageCircle } from 'lucide-react';

export default function PublicFooter() {
  const { t } = useTranslation();

  return (
    <footer className="bg-primary text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10">

          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-9 h-9 bg-white/15 rounded-sm flex items-center justify-center">
                <GraduationCap size={18} className="text-white" />
              </div>
              <span className="font-heading font-bold text-lg text-white">Studienkolleg Aachen</span>
            </div>
            <p className="text-sm text-white/70 max-w-xs leading-relaxed mb-3">
              Strukturierter, digital begleiteter Weg ins Studium in Deutschland –
              von der Bewerbung bis zur Feststellungsprüfung.
            </p>
            <p className="text-xs text-white/50">
              Way2Germany / W2G Academy GmbH · Amtsgericht Aachen HRB 23610
            </p>
          </div>

          {/* Bewerberbereich Kontakt */}
          <div>
            <h3 className="font-semibold text-sm mb-4 text-white/80 tracking-wide uppercase text-xs">
              Standort & Kontakt
            </h3>
            <div className="space-y-2.5 text-sm text-white/70">
              <div className="flex items-start gap-2">
                <MapPin size={13} className="mt-0.5 shrink-0 opacity-60" />
                <div>
                  <p>Theaterstraße 30–32</p>
                  <p>52062 Aachen</p>
                  <p className="text-xs text-white/45 mt-0.5">Unterricht / Beratung / Way2Germany</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Phone size={13} className="shrink-0 opacity-60" />
                <a href="tel:+4924199032292" className="hover:text-white transition-colors">
                  +49 241 990 322 92
                </a>
              </div>
              <div className="flex items-center gap-2">
                <Mail size={13} className="shrink-0 opacity-60" />
                <a href="mailto:info@stk-aachen.de" className="hover:text-white transition-colors">
                  info@stk-aachen.de
                </a>
              </div>
              <div className="flex items-center gap-2">
                <MessageCircle size={13} className="shrink-0 opacity-60" />
                <a href="https://api.whatsapp.com/message/RVKVWFEKNCIRG1?autoload=1&app_absent=0"
                  target="_blank" rel="noopener noreferrer"
                  className="hover:text-white transition-colors">
                  WhatsApp
                </a>
              </div>
            </div>
          </div>

          {/* Rechtliches + Gesellschaftssitz */}
          <div>
            <h3 className="font-semibold text-sm mb-4 text-white/80 tracking-wide uppercase text-xs">
              Rechtliches
            </h3>
            <ul className="space-y-2 text-sm text-white/70 mb-5">
              <li><Link to="/legal" className="hover:text-white transition-colors">Impressum</Link></li>
              <li><Link to="/privacy" className="hover:text-white transition-colors">Datenschutz</Link></li>
              <li><Link to="/agb" className="hover:text-white transition-colors">AGB</Link></li>
              <li><Link to="/apply" className="hover:text-white transition-colors">Bewerben</Link></li>
            </ul>
            <div className="text-xs text-white/40 space-y-0.5">
              <p className="font-medium text-white/55">Gesellschaftssitz:</p>
              <p>Theaterstraße 24 · 52062 Aachen</p>
            </div>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-white/40">
          <span>© {new Date().getFullYear()} W2G Academy GmbH / Studienkolleg Aachen</span>
          <span>Plattform v1.2.0</span>
        </div>
      </div>
    </footer>
  );
}
