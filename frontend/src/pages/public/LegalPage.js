import React from 'react';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import { AlertCircle } from 'lucide-react';

const LEGAL_CONTENT = {
  legal: {
    title: 'Impressum',
    content: `
**[OFFEN – Rechtsangaben noch nicht abschließend verifiziert]**

Angaben gemäß § 5 TMG:

W2G Academy GmbH
Theaterstraße 30-32
52062 Aachen

E-Mail: info@stk-aachen.de
Telefon: +49 241 990 322 92

**Hinweis:** Die vollständigen und rechtsverbindlichen Angaben (Geschäftsführung, Registergericht, Handelsregisternummer, USt-IdNr.) sind noch nicht final verifiziert und müssen vor Go-Live bestätigt werden.

Die Verantwortlichkeit für den Inhalt liegt beim Betreiber. Für die Richtigkeit der Angaben wird keine Haftung übernommen.
    `
  },
  privacy: {
    title: 'Datenschutzerklärung',
    content: `
**[OFFEN – Datenschutztext muss vor Go-Live rechtlich geprüft werden]**

Wir nehmen den Schutz deiner persönlichen Daten sehr ernst.

**Erhobene Daten:**
- Kontaktdaten (Name, E-Mail, Telefon)
- Bewerbungsdaten und Dokumente
- Kommunikationsverläufe im Portal

**Zweck:**
Verarbeitung deiner Bewerbung und Begleitung durch den Studienkolleg-Prozess.

**Rechte:**
Du hast das Recht auf Auskunft, Berichtigung, Löschung und Datenübertragbarkeit.

Kontakt für Datenschutzfragen: info@stk-aachen.de

Diese Datenschutzerklärung wird vor dem produktiven Go-Live vollständig rechtlich geprüft und finalisiert.
    `
  },
  agb: {
    title: 'Allgemeine Geschäftsbedingungen',
    content: `
**[OFFEN – AGB noch nicht abschließend geprüft]**

Diese AGB gelten für die Nutzung des Studienkolleg-Aachen-Portals und die angebotenen Leistungen.

**Preise und Zahlungsbedingungen:**
[OFFEN – Preisangaben sind noch nicht final verifiziert und werden vor Go-Live aktualisiert]

**Rücktrittsbedingungen:**
[OFFEN – Refund-/Storno-Logik muss rechtlich final geprüft werden]

**Hinweis:** Diese AGB sind noch nicht endgültig und werden vor dem produktiven Go-Live vollständig rechtlich freigegeben.
    `
  }
};

function renderContent(text) {
  return text.split('\n').map((line, i) => {
    if (line.startsWith('**') && line.endsWith('**')) {
      return <h3 key={i} className="font-semibold text-slate-800 mt-4 mb-2">{line.replace(/\*\*/g, '')}</h3>;
    }
    if (line.startsWith('- ')) {
      return <li key={i} className="text-slate-600 text-sm ml-4">{line.slice(2)}</li>;
    }
    if (line.trim() === '') return <br key={i} />;
    return <p key={i} className="text-slate-600 text-sm leading-relaxed">{line}</p>;
  });
}

export default function LegalPage({ type = 'legal' }) {
  const content = LEGAL_CONTENT[type] || LEGAL_CONTENT.legal;

  return (
    <div className="min-h-screen bg-white">
      <PublicNav />
      <main className="pt-16">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-16">
          <div className="bg-amber-50 border border-amber-200 rounded-sm p-4 mb-8 flex items-start gap-3">
            <AlertCircle size={16} className="text-amber-600 mt-0.5 shrink-0" />
            <p className="text-amber-700 text-sm">
              <strong>Hinweis:</strong> Diese Seite ist noch nicht abschließend rechtlich geprüft und verifiziert.
              Sie wird vor dem produktiven Go-Live vollständig finalisiert.
            </p>
          </div>

          <h1 className="text-3xl font-heading font-bold text-primary mb-8">{content.title}</h1>
          <div className="prose prose-sm max-w-none space-y-2" data-testid="legal-content">
            {renderContent(content.content)}
          </div>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
