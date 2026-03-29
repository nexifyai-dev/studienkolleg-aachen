import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { GraduationCap, MapPin, Phone, Mail, AlertCircle } from 'lucide-react';

export default function PublicFooter() {
  const { t } = useTranslation();

  return (
    <footer className="bg-primary text-white">
      {/* Open items notice */}
      <div className="bg-yellow-900/40 border-b border-yellow-800/30 px-4 py-2">
        <div className="max-w-7xl mx-auto flex items-center gap-2 text-xs text-yellow-200">
          <AlertCircle size={12} />
          <span>[OFFEN] Kontaktdaten und Adresse noch nicht abschließend verifiziert. Verwendung unter Vorbehalt.</span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-white/10 rounded-sm flex items-center justify-center">
                <GraduationCap size={18} className="text-white" />
              </div>
              <span className="font-heading font-bold text-lg">Studienkolleg Aachen</span>
            </div>
            <p className="text-sm text-blue-200 max-w-xs leading-relaxed">
              Dein strukturierter, digital begleiteter Weg ins Studium in Deutschland.
            </p>
            <p className="text-xs text-blue-300 mt-3">
              Way2Germany / W2G Academy GmbH
            </p>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold text-sm mb-4 text-accent">Kontakt</h3>
            <div className="space-y-2 text-sm text-blue-200">
              <div className="flex items-start gap-2">
                <MapPin size={14} className="mt-0.5 shrink-0" />
                <span>Theaterstraße 30-32<br />52062 Aachen</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone size={14} className="shrink-0" />
                <a href="tel:+4924199032292" className="hover:text-white transition-colors">+49 241 990 322 92</a>
              </div>
              <div className="flex items-center gap-2">
                <Mail size={14} className="shrink-0" />
                <a href="mailto:info@stk-aachen.de" className="hover:text-white transition-colors">info@stk-aachen.de</a>
              </div>
            </div>
          </div>

          {/* Links */}
          <div>
            <h3 className="font-semibold text-sm mb-4 text-accent">Rechtliches</h3>
            <ul className="space-y-2 text-sm text-blue-200">
              <li><Link to="/legal" className="hover:text-white transition-colors">Impressum</Link></li>
              <li><Link to="/privacy" className="hover:text-white transition-colors">Datenschutz</Link></li>
              <li><Link to="/agb" className="hover:text-white transition-colors">AGB</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-blue-300">
          <span>© {new Date().getFullYear()} Studienkolleg Aachen / Way2Germany</span>
          <span>Plattform: W2G Platform v1.0</span>
        </div>
      </div>
    </footer>
  );
}
