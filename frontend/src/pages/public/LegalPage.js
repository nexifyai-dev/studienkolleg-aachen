import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import { AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';

/* ─── Inhalte ───────────────────────────────────────────────────────────────── */

const IMPRESSUM_SECTIONS = [
  {
    title: 'Gesellschaftssitz – Angaben gemäß § 5 TMG',
    content: `W2G Academy GmbH
Theaterstraße 24
52062 Aachen

Hinweis: Theaterstraße 24 ist der eingetragene Gesellschaftssitz.
Der Unterrichts- und Beratungsstandort (Way2Germany / Studienkolleg Aachen) befindet sich in Theaterstraße 30–32, 52062 Aachen.`,
  },
  {
    title: 'Vertreten durch',
    content: 'Geschäftsführerin: Laura Saboor',
  },
  {
    title: 'Kontakt',
    content: `Telefon: +49 (0) 241 990 322 92
E-Mail: info@stk-aachen.de`,
  },
  {
    title: 'Registereintrag',
    content: `Registergericht: Amtsgericht Aachen
Registernummer: HRB 23610`,
  },
  {
    title: 'Unterrichts-/Beratungsstandort (Way2Germany)',
    content: `Studienkolleg Aachen / Way2Germany
Theaterstraße 30–32
52062 Aachen

Dieser Standort wird für Unterricht, Beratung und den Bewerberempfang genutzt.
Er ist nicht identisch mit dem eingetragenen Gesellschaftssitz.`,
  },
  {
    title: 'Haftung für Inhalte',
    content: `Als Diensteanbieter sind wir gemäß § 7 Abs. 1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.

Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden von entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.`,
  },
  {
    title: 'Urheberrecht',
    content: `Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.`,
  },
  {
    title: 'Hinweis zur rechtlichen Prüfung',
    content: '[OFFEN – Dieses Impressum wurde auf Basis der gelieferten Angaben erstellt. Eine finale juristische Prüfung und Freigabe vor Go-Live ist erforderlich. Insbesondere: E-Mail-Adresse (info@stk-aachen.de vs info@cd-stk.com) und vollständige Angaben zum Datenschutzbeauftragten müssen abschließend verifiziert werden.]',
  },
];

const AGB_PARAGRAPHS = [
  {
    title: '§1 Anbieter und Geltungsbereich',
    content: `(1) Anbieter der Leistungen ist die W2G Academy GmbH, Theaterstraße 24, 52062 Aachen, Betreiberin des Studienkollegs Aachen (nachfolgend „Studienkolleg").

(2) Diese Allgemeinen Geschäftsbedingungen (AGB) gelten für sämtliche Verträge über Deutschkurse und studienvorbereitende Schwerpunktkurse zwischen der W2G Academy GmbH und den Kursteilnehmern.

(3) Es gilt die zum Zeitpunkt des Vertragsschlusses gültige Fassung.

(4) Änderungen dieser AGB gelten nur für zukünftige Vertragsabschlüsse. Bereits bestehende Verträge bleiben unberührt, sofern keine ausdrückliche Zustimmung des Kursteilnehmers erfolgt.`,
  },
  {
    title: '§2 Vertragsabschluss',
    content: `(1) Die Anmeldung zu einem Kurs erfolgt in Textform (z. B. per E-Mail) und stellt ein verbindliches Angebot des Kursteilnehmers zum Abschluss eines Schulungsvertrages dar.

(2) Nach Prüfung der Anmeldung übersendet das Studienkolleg eine Zahlungsaufforderung ("Payment Request") mit den wesentlichen Vertragsdaten. Dieses Schreiben stellt ein verbindliches Vertragsangebot des Studienkollegs dar.

(3) Der Vertrag kommt zustande, sobald der Teilnehmer die in der Zahlungsaufforderung genannte Kursgebühr fristgerecht überweist.

(4) Die Allgemeinen Geschäftsbedingungen sind Bestandteil des Vertrags.

(5) Mit Zahlung bestätigt der Teilnehmer, die Allgemeinen Geschäftsbedingungen zur Kenntnis genommen zu haben und mit ihrer Geltung einverstanden zu sein.

(6) Erfolgt keine fristgerechte Zahlung, ist das Studienkolleg nicht mehr an das Angebot gebunden.`,
  },
  {
    title: '§3 Vertragsgegenstand',
    content: `(1) Vertragsgegenstand ist die Durchführung von:
a) studienvorbereitenden Deutschkursen (A1–C1)
b) fachbezogenen Schwerpunktkursen (T-, W-, M-, G-Kurs)

Hierzu zählen insbesondere:
• die Vorbereitung auf die externe Feststellungsprüfung (FSP)
• die Vorbereitung auf den TestAS als Studierfähigkeitstest
• die fachliche Vorbereitung auf eine Berufsausbildung in der entsprechenden Fachrichtung
• sowie die vertiefende fachliche Vorbereitung auf ein Hochschulstudium

(2) Die konkrete Anschlussoption hängt von den individuellen Voraussetzungen des Kursteilnehmers sowie von den jeweiligen Zulassungsvoraussetzungen der zuständigen Institutionen ab.

(3) Das Studienkolleg schuldet die ordnungsgemäße Durchführung des Unterrichts, nicht jedoch die Zulassung zu Prüfungen, Studiengängen oder Ausbildungsplätzen.`,
  },
  {
    title: '§4 Mindestteilnehmerzahl',
    content: `(1) Sprachkurse: Mindestteilnehmerzahl 6 Personen.
(2) Schwerpunktkurse: Mindestteilnehmerzahl 10 Personen.
(3) Wird die Mindestteilnehmerzahl nicht erreicht, kann das Studienkolleg den Kurs verschieben oder vom Vertrag zurücktreten. Bereits gezahlte Gebühren werden vollständig erstattet.`,
  },
  {
    title: '§5 Zahlungsbedingungen',
    content: `(1) Die Kursgebühr ist innerhalb der in der Zahlungsaufforderung genannten Frist vollständig zu entrichten. Die Höhe der Kursgebühren richtet sich nach dem individuellen Leistungsumfang und wird im jeweiligen Angebot bzw. in der Zahlungsaufforderung gesondert ausgewiesen.
(2) Erfolgt keine fristgerechte Zahlung, ist das Studienkolleg nicht verpflichtet, den Kursplatz freizuhalten.
(3) Bei vereinbarter Ratenzahlung wird die gesamte Restforderung sofort fällig, wenn der Teilnehmer mit zwei aufeinanderfolgenden Raten in Verzug gerät.
(4) Das Studienkolleg ist berechtigt, Teilnehmer bei Zahlungsverzug bis zum vollständigen Ausgleich von der Teilnahme auszuschließen.

Hinweis: Die konkreten Kosten und Gebühren hängen vom jeweiligen Einzelfall ab (Kurswahl, Startzeitpunkt, Zusatzleistungen, individuelle Vereinbarung) und werden nicht pauschal veröffentlicht. Verbindliche Preisangaben ergeben sich ausschließlich aus dem individuellen Angebot.

[OFFEN – Preisangaben sind noch nicht final verifiziert und werden vor Go-Live aktualisiert.]`,
  },
  {
    title: '§6 Höhere Gewalt und Unterrichtsform',
    content: `(1) Bei Ereignissen höherer Gewalt oder sonstigen Umständen außerhalb des Einflussbereichs des Studienkollegs (z. B. behördliche Anordnungen, Pandemien, Naturereignisse) ist das Studienkolleg berechtigt, den Unterricht in gleichwertiger Online- oder Hybridform durchzuführen.
(2) Eine solche Umstellung stellt keinen Kündigungsgrund dar, sofern der Gesamtumfang der Unterrichtseinheiten gewahrt bleibt.
(3) Schadensersatzansprüche aufgrund höherer Gewalt sind ausgeschlossen, soweit gesetzlich zulässig.`,
  },
  {
    title: '§7 Pflichten der Kursteilnehmer',
    content: `(1) Die Kursteilnehmer verpflichten sich zur regelmäßigen Teilnahme.
(2) Bei Fehlzeiten von mehr als 50 % kann das Studienkolleg nach pädagogischer Prüfung feststellen, dass das Ausbildungsziel nicht mehr erreichbar ist und den Vertrag aus wichtigem Grund kündigen.
(3) Vor Kündigung erfolgt in der Regel eine schriftliche Abmahnung.
(4) Die Hausordnung ist Bestandteil des Vertrages.`,
  },
  {
    title: '§8 Stornierung vor Kursbeginn',
    content: `(1) Eine Stornierung bedarf der Textform.
(2) Es gelten folgende pauschalierte Schadensersatzregelungen, sofern nicht im Einzelfall abweichend vereinbart:
• mehr als 8 Wochen vor Kursbeginn: 20 % der Kursgebühr, mindestens 500 €
• 8–6 Wochen vor Kursbeginn: 60 %
• weniger als 6 Wochen vor Kursbeginn: 100 %
• nach Kursbeginn: 100 %

(3) Maßgeblich ist der im Zulassungsbescheid genannte Kursbeginn.
(4) Dem Kursteilnehmer bleibt der Nachweis vorbehalten, dass kein oder ein wesentlich geringerer Schaden entstanden ist.
(5) Die tatsächlichen Stornierungskosten können je nach Einzelfall und individueller Vereinbarung abweichen.`,
  },
  {
    title: '§9 Kursabbruch nach Beginn',
    content: `(1) Mit Kursbeginn wird der gebuchte Kursplatz für die gesamte Vertragsdauer freigehalten. Eine Nachbesetzung ist regelmäßig nicht möglich.
(2) Bei Abbruch nach Kursbeginn bleibt die volle Kursgebühr geschuldet.
(3) Dem Teilnehmer bleibt der Nachweis vorbehalten, dass kein oder ein geringerer Schaden entstanden ist.`,
  },
  {
    title: '§10 Visumregelung',
    content: `(1) Die Verantwortung für die Beschaffung der erforderlichen Einreise- oder Aufenthaltsvisa liegt beim Kursteilnehmer.
(2) Eine teilweise Erstattung der Kursgebühr erfolgt ausschließlich dann, wenn:
• das für den gebuchten Kurs erforderliche Visum beantragt wurde
• die Ablehnung durch einen schriftlichen, vollständigen Ablehnungsbescheid der zuständigen Behörde nachgewiesen wird (in deutscher oder englischer Sprache)
• die Ablehnung nicht auf einem vom Kursteilnehmer zu vertretenden Umstand beruht

(3) Eine Erstattung ist insbesondere ausgeschlossen, wenn die Visumsablehnung beruht auf:
• unzureichendem oder nicht anerkanntem Finanzierungsnachweis
• unvollständigen, widersprüchlichen oder unzutreffenden Angaben/Unterlagen
• Nichterscheinen zu Terminen bei Behörden
• fehlender Mitwirkung im Visumverfahren

(4) In den Fällen des Absatzes 2 erfolgt die Erstattung abzüglich einer Verwaltungspauschale. Die Regelbeträge betragen:
• 500 € bei Schwerpunktkursen
• 100 € je gebuchter Sprachniveaustufe

Im Einzelfall können die tatsächlichen Verwaltungskosten abweichen und werden individuell mitgeteilt.`,
  },
  {
    title: '§11 Verwaltungsgebühren',
    content: `(1) Verwaltungsgebühren dienen dem Ausgleich durchschnittlich entstehender organisatorischer Kosten, insbesondere für:
• Zulassungsbearbeitung
• Dokumentenprüfung
• Behördenkommunikation
• Platzorganisation
• Buchhaltung und Zahlungsabwicklung

(2) Dem Kursteilnehmer bleibt der Nachweis vorbehalten, dass kein oder ein geringerer Aufwand entstanden ist.`,
  },
  {
    title: '§12 Haftung',
    content: `(1) Das Studienkolleg haftet uneingeschränkt bei Vorsatz, grober Fahrlässigkeit sowie bei Verletzung von Leben, Körper oder Gesundheit.
(2) Bei einfacher Fahrlässigkeit haftet das Studienkolleg nur bei Verletzung wesentlicher Vertragspflichten und begrenzt auf den vertragstypischen, vorhersehbaren Schaden.
(3) Die Haftung ist – soweit gesetzlich zulässig – auf die Höhe der jeweiligen Kursgebühr begrenzt.`,
  },
  {
    title: '§13 Datenschutz',
    content: `(1) Verantwortlicher im Sinne der DSGVO ist die W2G Academy GmbH, Theaterstraße 24, 52062 Aachen.
(2) Die Verarbeitung personenbezogener Daten erfolgt auf Grundlage von Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung) sowie lit. c DSGVO (gesetzliche Verpflichtung).
(3) Daten werden nur solange gespeichert, wie gesetzliche Aufbewahrungsfristen bestehen.
(4) Betroffenenrechte ergeben sich aus Art. 15–21 DSGVO.`,
  },
  {
    title: '§14 Widerrufsrecht',
    content: `Verbraucher haben das Recht, binnen 14 Tagen ohne Angabe von Gründen den Vertrag zu widerrufen.
Die Frist beginnt mit Vertragsschluss.
Zur Ausübung genügt eine eindeutige Erklärung in Textform an: info@stk-aachen.de

Im Falle eines Widerrufs werden bereits geleistete Zahlungen binnen 14 Tagen zurückerstattet.

Wurde ausdrücklich verlangt, dass der Kurs während der Widerrufsfrist beginnt, ist der anteilige Betrag der bereits erbrachten Leistung zu zahlen.`,
  },
  {
    title: '§15 Streitbeilegung',
    content: `Die EU-Kommission stellt eine Plattform zur Online-Streitbeilegung bereit: https://ec.europa.eu/consumers/odr/

Das Studienkolleg ist nicht verpflichtet, an einem Streitbeilegungsverfahren teilzunehmen.`,
  },
  {
    title: '§16 Rechtswahl',
    content: `Es gilt deutsches Recht unter Ausschluss des UN-Kaufrechts.
Zwingende Verbraucherschutzvorschriften des Wohnsitzstaates bleiben unberührt.

Stand: 06.02.2026`,
  },
];

const DATENSCHUTZ_SECTIONS = [
  {
    title: '1. Verantwortliche Stelle',
    content: `W2G Academy GmbH
Theaterstraße 24
52062 Aachen

Vertreten durch: Geschäftsführerin Laura Saboor
Telefon: 0241 / 990 322 92
E-Mail: info@stk-aachen.de

[OFFEN – Widerspruch zwischen info@stk-aachen.de und info@cd-stk.com als Kontakt-E-Mail in verschiedenen Quellen. Bitte vor Go-Live klären.]`,
  },
  {
    title: '2. Datenschutzbeauftragter',
    content: `Datenschutzbeauftragter:
Hardtstraße 3
53474 Bad Neuenahr-Ahrweiler
E-Mail: datenschutzbeauftragter@privatschule-carpediem.de

[OFFEN – Vollständige Kontaktdaten des Datenschutzbeauftragten bitte vor Go-Live final bestätigen.]`,
  },
  {
    title: '3. Erhobene Daten und Zwecke',
    content: `Wir verarbeiten folgende personenbezogene Daten:

a) Kontaktdaten: Name, Vorname, E-Mail-Adresse, Telefonnummer
b) Bewerbungsdaten: Herkunftsland, Deutschkenntnisse, gewünschter Kurs, Starttermin, Land des Schulabschlusses
c) Dokumente: Sprachzertifikate, Schulzeugnisse, Reisepass (nur verschlüsselt gespeichert)
d) Kommunikationsdaten: Nachrichten über das Portal
e) Technische Daten: IP-Adresse (anonymisiert), Browserdaten, Zugriffszeiten

Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung / vorvertragliche Maßnahmen), lit. c (gesetzliche Pflicht), lit. f (berechtigte Interessen).`,
  },
  {
    title: '4. Bewerberportal und Dokumentenverwaltung',
    content: `Im Rahmen des Bewerberportals werden Dokumente sicher und verschlüsselt gespeichert. Dokumente sind ausschließlich für autorisiertes Personal des Studienkollegs und den jeweiligen Bewerber selbst zugänglich.

Alle Datei-Uploads werden serverseitig verarbeitet. Direkte URLs zu Dateien werden nicht an Dritte weitergegeben.

Die KI-gestützte Vorprüfung von Bewerbungsunterlagen dient ausschließlich der Unterstützung des Staff-Teams. KI-Ergebnisse stellen keine bindenden Entscheidungen dar.`,
  },
  {
    title: '5. Weitergabe von Daten',
    content: `Eine Übermittlung Ihrer Daten an Dritte erfolgt nur:
• im Rahmen der Vertragserfüllung (z. B. Behördenkommunikation)
• bei gesetzlicher Verpflichtung
• mit Ihrer ausdrücklichen Einwilligung

Wir verwenden keine Tracking-Dienste ohne Ihre Einwilligung. Der Einsatz von Analytics-Tools wird gesondert über Cookie-Einwilligung geregelt.

[OFFEN – Vollständige Drittanbieter-Liste vor Go-Live prüfen und dokumentieren.]`,
  },
  {
    title: '6. Speicherdauer',
    content: `Bewerbungsdaten werden für die Dauer des Bewerbungsprozesses gespeichert, mindestens jedoch für die gesetzlich vorgeschriebene Aufbewahrungsfrist (i. d. R. 6 Jahre für buchhalterische Belege, 10 Jahre für steuerrelevante Unterlagen).

Nach Ablauf der Aufbewahrungsfristen werden Ihre Daten automatisch gelöscht, sofern keine weiteren Rechtsgrundlagen für die Verarbeitung bestehen.`,
  },
  {
    title: '7. Ihre Rechte (Art. 15–21 DSGVO)',
    content: `Sie haben das Recht auf:
• Auskunft (Art. 15 DSGVO)
• Berichtigung (Art. 16 DSGVO)
• Löschung (Art. 17 DSGVO)
• Einschränkung der Verarbeitung (Art. 18 DSGVO)
• Datenübertragbarkeit (Art. 20 DSGVO)
• Widerspruch (Art. 21 DSGVO)

Zur Geltendmachung Ihrer Rechte wenden Sie sich bitte an: info@stk-aachen.de`,
  },
  {
    title: '8. Beschwerderecht',
    content: `Sie haben das Recht, sich bei der zuständigen Datenschutzbehörde zu beschweren. Zuständige Aufsichtsbehörde in NRW:

Landesbeauftragte für Datenschutz und Informationsfreiheit Nordrhein-Westfalen
Kavalleriestraße 2-4
40213 Düsseldorf`,
  },
  {
    title: '9. Cookies und Tracking',
    content: `Diese Website verwendet technisch notwendige Cookies für den Betrieb des Portals (Session-Management, Authentifizierung).

Weitere Cookies oder Tracking-Dienste werden nur mit Ihrer ausdrücklichen Einwilligung eingesetzt.

[OFFEN – Cookie-Management-System vor Go-Live einrichten und Einwilligungsmanagement implementieren.]`,
  },
  {
    title: '10. Aktualität dieser Datenschutzerklärung',
    content: `Diese Datenschutzerklärung ist auf dem Stand der angegebenen Revision. Wir behalten uns vor, sie bei Änderungen unserer Dienste oder der Rechtslage anzupassen.

[HINWEIS: Diese Datenschutzerklärung muss vor dem produktiven Go-Live vollständig rechtlich geprüft und final freigegeben werden.]`,
  },
];

/* ─── Subkomponenten ────────────────────────────────────────────────────────── */

function AccordionSection({ title, content, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  const isOffen = content.includes('[OFFEN');
  return (
    <div className={`border rounded-sm mb-2 ${isOffen ? 'border-slate-200' : 'border-slate-100'}`}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-3.5 text-left"
        data-testid={`legal-section-${title.replace(/\s+/g, '-').toLowerCase()}`}
      >
        <span className="font-semibold text-sm text-slate-800">{title}</span>
        {open ? <ChevronUp size={16} className="text-slate-400 shrink-0" /> : <ChevronDown size={16} className="text-slate-400 shrink-0" />}
      </button>
      {open && (
        <div className="px-5 pb-5">
          {content.split('\n').map((line, i) => {
            if (line.trim() === '') return <br key={i} />;
            if (line.startsWith('[OFFEN') || line.startsWith('[HINWEIS')) {
              return (
                <div key={i} className="flex items-start gap-2 bg-slate-100 border border-slate-200 rounded-sm px-3 py-2 my-2">
                  <AlertCircle size={14} className="text-slate-500 mt-0.5 shrink-0" />
                  <p className="text-slate-600 text-xs">{line.replace(/\[OFFEN\s*–\s*/g, '').replace(/\[HINWEIS:\s*/g, '').replace(/\]/g, '')}</p>
                </div>
              );
            }
            return <p key={i} className="text-slate-600 text-sm leading-relaxed">{line}</p>;
          })}
        </div>
      )}
    </div>
  );
}

/* ─── Seitentypen ───────────────────────────────────────────────────────────── */

function ImpressumContent({ t, isEN }) {
  return (
    <div data-testid="legal-content-impressum" className="space-y-8">

      {/* Gesellschaftssitz */}
      <div className="border border-slate-100 rounded-sm overflow-hidden">
        <div className="bg-primary px-5 py-3">
          <h2 className="text-sm font-semibold text-white">{t('legal_page.company_heading')}</h2>
        </div>
        <div className="px-5 py-5 grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">{t('legal_page.company_label')}</p>
            <p className="text-slate-800 font-semibold">W2G Academy GmbH</p>
            <p className="text-slate-600 text-sm mt-1">Theaterstraße 24</p>
            <p className="text-slate-600 text-sm">52062 Aachen</p>
            <p className="text-xs text-slate-400 mt-1.5">{t('legal_page.registered_seat')}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">{t('legal_page.rep_label')}</p>
            <p className="text-slate-600 text-sm">{isEN ? 'Managing Director' : 'Geschäftsführerin'}</p>
            <p className="text-slate-800 font-semibold">Laura Saboor</p>
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">{t('legal_page.contact_label')}</p>
            <p className="text-slate-600 text-sm">{isEN ? 'Phone' : 'Tel'}: <a href="tel:+4924199032292" className="text-primary hover:underline">+49 (0) 241 990 322 92</a></p>
            <p className="text-slate-600 text-sm">E-Mail: <a href="mailto:info@stk-aachen.de" className="text-primary hover:underline">info@stk-aachen.de</a></p>
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">{t('legal_page.registry_label')}</p>
            <p className="text-slate-600 text-sm">Amtsgericht Aachen</p>
            <p className="text-slate-600 text-sm">HRB 23610</p>
          </div>
        </div>
      </div>

      {/* Unterrichtsstandort */}
      <div className="border border-slate-100 rounded-sm overflow-hidden">
        <div className="bg-slate-800 px-5 py-3">
          <h2 className="text-sm font-semibold text-white">{t('legal_page.office_heading')}</h2>
        </div>
        <div className="px-5 py-5">
          <p className="text-slate-800 font-semibold">Studienkolleg Aachen / Way2Germany</p>
          <p className="text-slate-600 text-sm mt-1">Theaterstraße 30–32</p>
          <p className="text-slate-600 text-sm">52062 Aachen</p>
          <p className="text-xs text-slate-400 mt-3 border-t border-slate-100 pt-3">
            {t('legal_page.office_note')}
          </p>
        </div>
      </div>

      {/* Haftung + Urheberrecht */}
      <div className="space-y-2">
        {IMPRESSUM_SECTIONS.filter(s => ['Haftung für Inhalte', 'Urheberrecht', 'Hinweis zur rechtlichen Prüfung'].includes(s.title)).map(s => (
          <AccordionSection key={s.title} title={s.title} content={s.content} defaultOpen={s.open} />
        ))}
      </div>
    </div>
  );
}

function AGBContent() {
  return (
    <div data-testid="legal-content-agb">
      {AGB_PARAGRAPHS.map(p => (
        <AccordionSection key={p.title} title={p.title} content={p.content} />
      ))}
      <p className="text-xs text-slate-400 mt-6 text-right">Stand: 06.02.2026</p>
    </div>
  );
}

function DatenschutzContent() {
  return (
    <div data-testid="legal-content-datenschutz">
      {DATENSCHUTZ_SECTIONS.map(s => (
        <AccordionSection key={s.title} title={s.title} content={s.content} />
      ))}
      <p className="text-xs text-slate-400 mt-6 text-right">Stand: Februar 2026</p>
    </div>
  );
}

const TYPES = {
  legal: { titleKey: 'legal_page.impressum', Component: ImpressumContent },
  agb: { titleKey: 'legal_page.agb', Component: AGBContent },
  privacy: { titleKey: 'legal_page.privacy', Component: DatenschutzContent },
};

export default function LegalPage({ type = 'legal' }) {
  const { t, i18n } = useTranslation();
  const config = TYPES[type] || TYPES.legal;
  const { titleKey, Component } = config;
  const isEN = i18n.language === 'en';

  return (
    <div className="min-h-screen bg-white">
      <PublicNav />
      <main className="pt-16">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10 sm:py-16">

          {/* Nav zwischen Legal-Seiten */}
          <nav className="flex flex-wrap gap-2 mb-8" data-testid="legal-tabs">
            {Object.entries(TYPES).map(([key, val]) => (
              <Link
                key={key}
                to={key === 'legal' ? '/legal' : `/${key}`}
                className={`px-3 py-1.5 rounded-sm text-sm font-medium transition-all ${
                  type === key
                    ? 'bg-primary text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
                data-testid={`legal-tab-${key}`}
              >
                {t(val.titleKey)}
              </Link>
            ))}
          </nav>

          {/* EN-Hinweis für Rechtstexte */}
          {isEN && (
            <div className="mb-6 flex items-start gap-3 bg-slate-50 border border-slate-200 rounded-sm px-4 py-3">
              <span className="text-slate-400 text-xs mt-0.5">ⓘ</span>
              <p className="text-slate-600 text-xs">{t('legal_page.de_only_note')}</p>
            </div>
          )}

          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-8" data-testid="legal-page-title">
            {t(titleKey)}
          </h1>

          <Component t={t} isEN={isEN} />

          {/* Kontakt */}
          <div className="mt-10 pt-6 border-t border-slate-100">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <p className="text-slate-400 text-xs">
                {t('legal_page.contact_faq')} –{' '}
                <a href="mailto:info@stk-aachen.de" className="text-primary hover:underline">
                  info@stk-aachen.de
                </a>
              </p>
              <p className="text-slate-300 text-xs">{t('legal_page.review_note')}</p>
            </div>
          </div>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
