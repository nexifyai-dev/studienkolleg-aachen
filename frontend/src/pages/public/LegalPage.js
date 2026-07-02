import React, { useState, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';
import { ChevronDown, ChevronUp, Printer, Shield, Scale, FileText } from 'lucide-react';

/* ─── Inhalte (unverändert) ───────────────────────────────────────────────── */

const IMPRESSUM_SECTIONS = [
  { title: 'Gesellschaftssitz – Angaben gemaess Paragraph 5 TMG', content: `W2G Academy GmbH\nTheaterstrasse 24\n52062 Aachen\n\nHinweis: Theaterstrasse 24 ist der eingetragene Gesellschaftssitz.\nDer Unterrichts- und Beratungsstandort (Way2Germany / Studienkolleg Aachen) befindet sich in Theaterstrasse 30–32, 52062 Aachen.` },
  { title: 'Vertreten durch', content: 'Geschaeftsfuehrerin: Laura Saboor' },
  { title: 'Kontakt', content: `Telefon: +49 (0) 241 990 322 92\nE-Mail: info@stk-aachen.de` },
  { title: 'Registereintrag', content: `Registergericht: Amtsgericht Aachen\nRegisternummer: HRB 23610` },
  { title: 'Unterrichts-/Beratungsstandort (Way2Germany)', content: `Studienkolleg Aachen / Way2Germany\nTheaterstrasse 30–32\n52062 Aachen\n\nDieser Standort wird fuer Unterricht, Beratung und den Bewerberempfang genutzt.\nEr ist nicht identisch mit dem eingetragenen Gesellschaftssitz.` },
  { title: 'Haftung fuer Inhalte', content: `Als Diensteanbieter sind wir gemaess Paragraph 7 Abs. 1 TMG fuer eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach Paragraph 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, uebermittelte oder gespeicherte fremde Informationen zu ueberwachen oder nach Umstaenden zu forschen, die auf eine rechtswidrige Taetigkeit hinweisen.\n\nVerpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberuehrt. Eine diesbezuegliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung moeglich. Bei Bekanntwerden von entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.` },
  { title: 'Urheberrecht', content: `Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Vervielfaeltigung, Bearbeitung, Verbreitung und jede Art der Verwertung ausserhalb der Grenzen des Urheberrechtes beduerfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.` },
];

const AGB_PARAGRAPHS = [
  { title: 'Paragraph 1 Anbieter und Geltungsbereich', content: `(1) Anbieter der Leistungen ist die W2G Academy GmbH, Theaterstrasse 24, 52062 Aachen, Betreiberin des Studienkollegs Aachen (nachfolgend „Studienkolleg").\n\n(2) Diese Allgemeinen Geschaeftsbedingungen (AGB) gelten fuer saemtliche Vertraege ueber Deutschkurse und studienvorbereitende Schwerpunktkurse zwischen der W2G Academy GmbH und den Kursteilnehmern.\n\n(3) Es gilt die zum Zeitpunkt des Vertragsschlusses gueltige Fassung.\n\n(4) Aenderungen dieser AGB gelten nur fuer zukuenftige Vertragsabschluesse. Bereits bestehende Vertraege bleiben unberuehrt, sofern keine ausdrueckliche Zustimmung des Kursteilnehmers erfolgt.` },
  { title: 'Paragraph 2 Vertragsabschluss', content: `(1) Die Anmeldung zu einem Kurs erfolgt in Textform (z. B. per E-Mail) und stellt ein verbindliches Angebot des Kursteilnehmers zum Abschluss eines Schulungsvertrages dar.\n\n(2) Nach Pruefung der Anmeldung uebersendet das Studienkolleg eine Zahlungsaufforderung ("Payment Request") mit den wesentlichen Vertragsdaten. Dieses Schreiben stellt ein verbindliches Vertragsangebot des Studienkollegs dar.\n\n(3) Der Vertrag kommt zustande, sobald der Teilnehmer die in der Zahlungsaufforderung genannte Kursgebuehr fristgerecht ueberweist.\n\n(4) Die Allgemeinen Geschaeftsbedingungen sind Bestandteil des Vertrags.\n\n(5) Mit Zahlung bestaetigt der Teilnehmer, die Allgemeinen Geschaeftsbedingungen zur Kenntnis genommen zu haben und mit ihrer Geltung einverstanden zu sein.\n\n(6) Erfolgt keine fristgerechte Zahlung, ist das Studienkolleg nicht mehr an das Angebot gebunden.` },
  { title: 'Paragraph 3 Vertragsgegenstand', content: `(1) Vertragsgegenstand ist die Durchfuehrung von:\na) studienvorbereitenden Deutschkursen (A1–C1)\nb) fachbezogenen Schwerpunktkursen (T-, W-, M-, G-Kurs)\n\nHierzu zaehlen insbesondere:\n- die Vorbereitung auf die externe Feststellungspruefung (FSP)\n- die Vorbereitung auf den TestAS als Studierfaehigkeitstest\n- die fachliche Vorbereitung auf eine Berufsausbildung in der entsprechenden Fachrichtung\n- sowie die vertiefende fachliche Vorbereitung auf ein Hochschulstudium\n\n(2) Die konkrete Anschlussoption haengt von den individuellen Voraussetzungen des Kursteilnehmers sowie von den jeweiligen Zulassungsvoraussetzungen der zustaendigen Institutionen ab.\n\n(3) Das Studienkolleg schuldet die ordnungsgemaesse Durchfuehrung des Unterrichts, nicht jedoch die Zulassung zu Pruefungen, Studiengaengen oder Ausbildungsplaetzen.` },
  { title: 'Paragraph 4 Mindestteilnehmerzahl', content: `(1) Sprachkurse: Mindestteilnehmerzahl 6 Personen.\n(2) Schwerpunktkurse: Mindestteilnehmerzahl 10 Personen.\n(3) Wird die Mindestteilnehmerzahl nicht erreicht, kann das Studienkolleg den Kurs verschieben oder vom Vertrag zuruecktreten. Bereits gezahlte Gebuehren werden vollstaendig erstattet.` },
  { title: 'Paragraph 5 Zahlungsbedingungen', content: `(1) Die Kursgebuehr ist innerhalb der in der Zahlungsaufforderung genannten Frist vollstaendig zu entrichten. Die Hoehe der Kursgebuehren richtet sich nach dem individuellen Leistungsumfang und wird im jeweiligen Angebot bzw. in der Zahlungsaufforderung gesondert ausgewiesen.\n(2) Erfolgt keine fristgerechte Zahlung, ist das Studienkolleg nicht verpflichtet, den Kursplatz freizuhalten.\n(3) Bei vereinbarter Ratenzahlung wird die gesamte Restforderung sofort faellig, wenn der Teilnehmer mit zwei aufeinanderfolgenden Raten in Verzug geraet.\n(4) Das Studienkolleg ist berechtigt, Teilnehmer bei Zahlungsverzug bis zum vollstaendigen Ausgleich von der Teilnahme auszuschliessen.\n\nHinweis: Die konkreten Kosten und Gebuehren haengen vom jeweiligen Einzelfall ab (Kurswahl, Startzeitpunkt, Zusatzleistungen, individuelle Vereinbarung) und werden nicht pauschal veroeffentlicht. Verbindliche Preisangaben ergeben sich ausschliesslich aus dem individuellen Angebot.` },
  { title: 'Paragraph 6 Hoehere Gewalt und Unterrichtsform', content: `(1) Bei Ereignissen hoeherer Gewalt oder sonstigen Umstaenden ausserhalb des Einflussbereichs des Studienkollegs (z. B. behoerdliche Anordnungen, Pandemien, Naturereignisse) ist das Studienkolleg berechtigt, den Unterricht in gleichwertiger Online- oder Hybridform durchzufuehren.\n(2) Eine solche Umstellung stellt keinen Kuendigungsgrund dar, sofern der Gesamtumfang der Unterrichtseinheiten gewahrt bleibt.\n(3) Schadensersatzansprueche aufgrund hoeherer Gewalt sind ausgeschlossen, soweit gesetzlich zulaessig.` },
  { title: 'Paragraph 7 Pflichten der Kursteilnehmer', content: `(1) Die Kursteilnehmer verpflichten sich zur regelmaessigen Teilnahme.\n(2) Bei Fehlzeiten von mehr als 50 % kann das Studienkolleg nach paedagogischer Pruefung feststellen, dass das Ausbildungsziel nicht mehr erreichbar ist und den Vertrag aus wichtigem Grund kuendigen.\n(3) Vor Kuendigung erfolgt in der Regel eine schriftliche Abmahnung.\n(4) Die Hausordnung ist Bestandteil des Vertrages.` },
  { title: 'Paragraph 8 Stornierung vor Kursbeginn', content: `(1) Eine Stornierung bedarf der Textform.\n(2) Es gelten folgende pauschalierte Schadensersatzregelungen, sofern nicht im Einzelfall abweichend vereinbart:\n- mehr als 8 Wochen vor Kursbeginn: 20 % der Kursgebuehr, mindestens 500 Euro\n- 8–6 Wochen vor Kursbeginn: 60 %\n- weniger als 6 Wochen vor Kursbeginn: 100 %\n- nach Kursbeginn: 100 %\n\n(3) Massgeblich ist der im Zulassungsbescheid genannte Kursbeginn.\n(4) Dem Kursteilnehmer bleibt der Nachweis vorbehalten, dass kein oder ein wesentlich geringerer Schaden entstanden ist.\n(5) Die tatsaechlichen Stornierungskosten koennen je nach Einzelfall und individueller Vereinbarung abweichen.` },
  { title: 'Paragraph 9 Kursabbruch nach Beginn', content: `(1) Mit Kursbeginn wird der gebuchte Kursplatz fuer die gesamte Vertragsdauer freigehalten. Eine Nachbesetzung ist regelmaessig nicht moeglich.\n(2) Bei Abbruch nach Kursbeginn bleibt die volle Kursgebuehr geschuldet.\n(3) Dem Teilnehmer bleibt der Nachweis vorbehalten, dass kein oder ein geringerer Schaden entstanden ist.` },
  { title: 'Paragraph 10 Visumregelung', content: `(1) Die Verantwortung fuer die Beschaffung der erforderlichen Einreise- oder Aufenthaltsvisa liegt beim Kursteilnehmer.\n(2) Eine teilweise Erstattung der Kursgebuehr erfolgt ausschliesslich dann, wenn:\n- das fuer den gebuchten Kurs erforderliche Visum beantragt wurde\n- die Ablehnung durch einen schriftlichen, vollstaendigen Ablehnungsbescheid der zustaendigen Behoerde nachgewiesen wird (in deutscher oder englischer Sprache)\n- die Ablehnung nicht auf einem vom Kursteilnehmer zu vertretenden Umstand beruht\n\n(3) Eine Erstattung ist insbesondere ausgeschlossen, wenn die Visumsablehnung beruht auf:\n- unzureichendem oder nicht anerkanntem Finanzierungsnachweis\n- unvollstaendigen, widersprüchlichen oder unzutreffenden Angaben/Unterlagen\n- Nichterscheinen zu Terminen bei Behoerden\n- fehlender Mitwirkung im Visumverfahren\n\n(4) In den Faellen des Absatzes 2 erfolgt die Erstattung abzueglich einer Verwaltungspauschale. Die Regelbetraege betragen:\n- 500 Euro bei Schwerpunktkursen\n- 100 Euro je gebuchter Sprachniveaustufe\n\nIm Einzelfall koennen die tatsaechlichen Verwaltungskosten abweichen und werden individuell mitgeteilt.` },
  { title: 'Paragraph 11 Verwaltungsgebuehren', content: `(1) Verwaltungsgebuehren dienen dem Ausgleich durchschnittlich entstehender organisatorischer Kosten, insbesondere fuer:\n- Zulassungsbearbeitung\n- Dokumentenpruefung\n- Behoerdenkommunikation\n- Platzorganisation\n- Buchhaltung und Zahlungsabwicklung\n\n(2) Dem Kursteilnehmer bleibt der Nachweis vorbehalten, dass kein oder ein geringerer Aufwand entstanden ist.` },
  { title: 'Paragraph 12 Haftung', content: `(1) Das Studienkolleg haftet uneingeschraenkt bei Vorsatz, grober Fahrlaessigkeit sowie bei Verletzung von Leben, Koerper oder Gesundheit.\n(2) Bei einfacher Fahrlaessigkeit haftet das Studienkolleg nur bei Verletzung wesentlicher Vertragspflichten und begrenzt auf den vertragstypischen, vorhersehbaren Schaden.\n(3) Die Haftung ist – soweit gesetzlich zulaessig – auf die Hoehe der jeweiligen Kursgebuehr begrenzt.` },
  { title: 'Paragraph 13 Datenschutz', content: `(1) Verantwortlicher im Sinne der DSGVO ist die W2G Academy GmbH, Theaterstrasse 24, 52062 Aachen.\n(2) Die Verarbeitung personenbezogener Daten erfolgt auf Grundlage von Art. 6 Abs. 1 lit. b DSGVO (Vertragserfullung) sowie lit. c DSGVO (gesetzliche Verpflichtung).\n(3) Daten werden nur solange gespeichert, wie gesetzliche Aufbewahrungsfristen bestehen.\n(4) Betroffenenrechte ergeben sich aus Art. 15–21 DSGVO.` },
  { title: 'Paragraph 14 Widerrufsrecht', content: `Verbraucher haben das Recht, binnen 14 Tagen ohne Angabe von Gruenden den Vertrag zu widerrufen.\nDie Frist beginnt mit Vertragsschluss.\nZur Ausuebung genuegt eine eindeutige Erklaerung in Textform an: info@stk-aachen.de\n\nIm Falle eines Widerrufs werden bereits geleistete Zahlungen binnen 14 Tagen zurueckerstattet.\n\nWurde ausdruecklich verlangt, dass der Kurs waehrend der Widerrufsfrist beginnt, ist der anteilige Betrag der bereits erbrachten Leistung zu zahlen.` },
  { title: 'Paragraph 15 Streitbeilegung', content: `Die EU-Kommission stellt eine Plattform zur Online-Streitbeilegung bereit: https://ec.europa.eu/consumers/odr/\n\nDas Studienkolleg ist nicht verpflichtet, an einem Streitbeilegungsverfahren teilzunehmen.` },
  { title: 'Paragraph 16 Rechtswahl', content: `Es gilt deutsches Recht unter Ausschluss des UN-Kaufrechts.\nZwingende Verbraucherschutzvorschriften des Wohnsitzstaates bleiben unberuehrt.\n\nStand: 06.02.2026` },
];

const DATENSCHUTZ_SECTIONS = [
  { title: '1. Verantwortliche Stelle', content: `W2G Academy GmbH\nTheaterstrasse 24\n52062 Aachen\n\nVertreten durch: Geschaeftsfuehrerin Laura Saboor\nTelefon: 0241 / 990 322 92\nE-Mail: info@stk-aachen.de` },
  { title: '2. Datenschutzbeauftragter', content: `Datenschutzbeauftragter:\nHardtstrasse 3\n53474 Bad Neuenahr-Ahrweiler\nE-Mail: datenschutzbeauftragter@privatschule-carpediem.de` },
  { title: '3. Erhobene Daten und Zwecke', content: `Wir verarbeiten folgende personenbezogene Daten:\n\na) Kontaktdaten: Name, Vorname, E-Mail-Adresse, Telefonnummer\nb) Bewerbungsdaten: Herkunftsland, Deutschkenntnisse, gewuenschter Kurs, Starttermin, Land des Schulabschlusses\nc) Dokumente: Sprachzertifikate, Schulzeugnisse, Reisepass (nur verschluesselt gespeichert)\nd) Kommunikationsdaten: Nachrichten ueber das Portal\ne) Technische Daten: IP-Adresse (anonymisiert), Browserdaten, Zugriffszeiten\n\nRechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO (Vertragserfuellung / vorvertragliche Massnahmen), lit. c (gesetzliche Pflicht), lit. f (berechtigte Interessen).` },
  { title: '4. Bewerberportal und Dokumentenverwaltung', content: `Im Rahmen des Bewerberportals werden Dokumente sicher und verschluesselt gespeichert. Dokumente sind ausschliesslich fuer autorisiertes Personal des Studienkollegs und den jeweiligen Bewerber selbst zugaenglich.\n\nAlle Datei-Uploads werden serverseitig verarbeitet. Direkte URLs zu Dateien werden nicht an Dritte weitergegeben.\n\nDie KI-gestuetzte Vorpruefung von Bewerbungsunterlagen dient ausschliesslich der Unterstuetzung des Staff-Teams. KI-Ergebnisse stellen keine bindenden Entscheidungen dar.` },
  { title: '5. Weitergabe von Daten', content: `Eine Uebermittlung Ihrer Daten an Dritte erfolgt nur:\n- im Rahmen der Vertragserfuellung (z. B. Behoerdenkommunikation)\n- bei gesetzlicher Verpflichtung\n- mit Ihrer ausdruecklichen Einwilligung\n\nWir verwenden keine Tracking-Dienste ohne Ihre Einwilligung. Der Einsatz von Analytics-Tools wird gesondert ueber Cookie-Einwilligung geregelt.` },
  { title: '6. Speicherdauer', content: `Bewerbungsdaten werden fuer die Dauer des Bewerbungsprozesses gespeichert, mindestens jedoch fuer die gesetzlich vorgeschriebene Aufbewahrungsfrist (i. d. R. 6 Jahre fuer buchhalterische Belege, 10 Jahre fuer steuerrelevante Unterlagen).\n\nNach Ablauf der Aufbewahrungsfristen werden Ihre Daten automatisch geloescht, sofern keine weiteren Rechtsgrundlagen fuer die Verarbeitung bestehen.` },
  { title: '7. Ihre Rechte (Art. 15–21 DSGVO)', content: `Sie haben das Recht auf:\n- Auskunft (Art. 15 DSGVO)\n- Berichtigung (Art. 16 DSGVO)\n- Loeschung (Art. 17 DSGVO)\n- Einschraenkung der Verarbeitung (Art. 18 DSGVO)\n- Datenuebertragbarkeit (Art. 20 DSGVO)\n- Widerspruch (Art. 21 DSGVO)\n\nZur Geltendmachung Ihrer Rechte wenden Sie sich bitte an: info@stk-aachen.de` },
  { title: '8. Beschwerderecht', content: `Sie haben das Recht, sich bei der zustaendigen Datenschutzbehoerde zu beschweren. Zustaendige Aufsichtsbehoerde in NRW:\n\nLandesbeauftragte fuer Datenschutz und Informationsfreiheit Nordrhein-Westfalen\nKavalleriestrasse 2-4\n40213 Duesseldorf` },
  { title: '9. Cookies und Tracking', content: `Diese Website verwendet technisch notwendige Cookies fuer den Betrieb des Portals (Session-Management, Authentifizierung, Spracheinstellung).\n\nBeim ersten Besuch der Seite werden Sie ueber ein Cookie-Einwilligungsfenster informiert. Sie koennen dort auswaehlen, welche Cookie-Kategorien Sie zulassen moechten:\n\n- Technisch notwendig: Authentifizierung (Login-Session), Sprachauswahl – diese sind fuer den Betrieb der Plattform zwingend erforderlich und koennen nicht deaktiviert werden.\n- Funktionale Cookies: Speicherung Ihrer Cookie-Praeferenzen und Onboarding-Status – diese verbessern die Nutzererfahrung und koennen individuell aktiviert oder deaktiviert werden.\n\nIhre Einwilligung wird lokal gespeichert und kann jederzeit ueber den Link „Cookie-Einstellungen" im Seitenfuss (Footer) erneut aufgerufen und angepasst werden.` },
  { title: '10. Aktualitaet dieser Datenschutzerklaerung', content: `Diese Datenschutzerklaerung ist auf dem Stand der angegebenen Revision. Wir behalten uns vor, sie bei Aenderungen unserer Dienste oder der Rechtslage anzupassen.` },
];

/* ─── Subkomponenten ────────────────────────────────────────────────────── */

function AccordionSection({ title, content, defaultOpen = false, sectionIdx }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-[rgba(10,25,47,0.08)] rounded-[4px] overflow-hidden" data-section-idx={sectionIdx}
      style={{ boxShadow: open ? '0 2px 12px rgba(17,54,85,0.04)' : 'none' }}>
      <button onClick={() => setOpen(!open)}
        className={`w-full flex items-center justify-between px-5 py-4 text-left transition-colors ${open ? 'bg-[var(--color-surface-elevated)]' : 'hover:bg-[var(--color-surface-elevated)]'}`}
        data-testid={`legal-section-${sectionIdx}`}>
        <span className="font-semibold text-[14px] text-[var(--color-primary-dark)] pr-4" style={{ fontFamily: 'var(--font-heading)' }}>{title}</span>
        {open ? <ChevronUp size={16} className="text-[var(--color-text-tertiary)] shrink-0" /> : <ChevronDown size={16} className="text-[var(--color-text-tertiary)] shrink-0" />}
      </button>
      {open && (
        <div className="px-5 pb-5 border-t border-[rgba(10,25,47,0.05)]">
          <div className="pt-4 space-y-1.5">
            {content.split('\n').map((line, i) => {
              if (line.trim() === '') return <div key={i} className="h-3" />;
              return <p key={i} className="text-[13px] text-[var(--color-text-secondary)] leading-[1.8]">{line}</p>;
            })}
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── Impressum-Darstellung ─────────────────────────────────────────────── */

function ImpressumContent({ t, isEN }) {
  return (
    <div data-testid="legal-content-impressum" className="space-y-6">
      {/* Gesellschaftssitz */}
      <div className="rounded-[4px] border border-[rgba(10,25,47,0.08)] overflow-hidden" style={{ boxShadow: '0 2px 12px rgba(17,54,85,0.04)' }}>
        <div className="px-6 py-3" style={{ background: 'linear-gradient(135deg, var(--color-primary-dark), var(--color-primary))' }}>
          <h2 className="text-[13px] font-semibold text-white tracking-[0.02em]">{t('legal_page.company_heading')}</h2>
        </div>
        <div className="px-6 py-6 grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <p className="text-[10px] font-semibold tracking-[0.15em] uppercase mb-2" style={{ color: 'var(--color-accent)' }}>{t('legal_page.company_label')}</p>
            <p className="text-[var(--color-primary-dark)] font-semibold text-[14px]">W2G Academy GmbH</p>
            <p className="text-[var(--color-text-secondary)] text-[13px] mt-1">Theaterstrasse 24</p>
            <p className="text-[var(--color-text-secondary)] text-[13px]">52062 Aachen</p>
            <p className="text-[11px] text-[var(--color-text-tertiary)] mt-1.5">{t('legal_page.registered_seat')}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold tracking-[0.15em] uppercase mb-2" style={{ color: 'var(--color-accent)' }}>{t('legal_page.rep_label')}</p>
            <p className="text-[var(--color-text-secondary)] text-[13px]">{isEN ? 'Managing Director' : 'Geschaeftsfuehrerin'}</p>
            <p className="text-[var(--color-primary-dark)] font-semibold text-[14px]">Laura Saboor</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold tracking-[0.15em] uppercase mb-2" style={{ color: 'var(--color-accent)' }}>{t('legal_page.contact_label')}</p>
            <p className="text-[var(--color-text-secondary)] text-[13px]">{isEN ? 'Phone' : 'Tel'}: <a href="tel:+4924199032292" className="hover:underline" style={{ color: 'var(--color-primary)' }}>+49 (0) 241 990 322 92</a></p>
            <p className="text-[var(--color-text-secondary)] text-[13px]">E-Mail: <a href="mailto:info@stk-aachen.de" className="hover:underline" style={{ color: 'var(--color-primary)' }}>info@stk-aachen.de</a></p>
          </div>
          <div>
            <p className="text-[10px] font-semibold tracking-[0.15em] uppercase mb-2" style={{ color: 'var(--color-accent)' }}>{t('legal_page.registry_label')}</p>
            <p className="text-[var(--color-text-secondary)] text-[13px]">Amtsgericht Aachen</p>
            <p className="text-[var(--color-text-secondary)] text-[13px]">HRB 23610</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold tracking-[0.15em] uppercase mb-2" style={{ color: 'var(--color-accent)' }}>{isEN ? 'Tax Information' : 'Steuerliche Angaben'}</p>
            <p className="text-[var(--color-text-secondary)] text-[13px]">USt-IdNr.: DE333306663</p>
            <p className="text-[var(--color-text-tertiary)] text-[11px] mt-1">Ggf. umsatzsteuerbefreit gem. Paragraph 4 Nr. 21 UStG</p>
          </div>
        </div>
      </div>

      {/* Unterrichtsstandort */}
      <div className="rounded-[4px] border border-[rgba(10,25,47,0.08)] overflow-hidden" style={{ boxShadow: '0 2px 12px rgba(17,54,85,0.04)' }}>
        <div className="px-6 py-3" style={{ background: 'linear-gradient(135deg, var(--color-primary-dark), var(--color-primary))' }}>
          <h2 className="text-[13px] font-semibold text-white tracking-[0.02em]">{t('legal_page.office_heading')}</h2>
        </div>
        <div className="px-6 py-5">
          <p className="text-[var(--color-primary-dark)] font-semibold text-[14px]">Studienkolleg Aachen / Way2Germany</p>
          <p className="text-[var(--color-text-secondary)] text-[13px] mt-1">Theaterstrasse 30–32, 52062 Aachen</p>
          <p className="text-[11px] text-[var(--color-text-tertiary)] mt-3 pt-3 border-t border-[rgba(10,25,47,0.05)]">{t('legal_page.office_note')}</p>
        </div>
      </div>

      {/* Haftung + Urheberrecht */}
      <div className="space-y-3">
        {IMPRESSUM_SECTIONS.filter(s => s.title.includes('Haftung') || s.title.includes('Urheberrecht')).map((s, idx) => (
          <AccordionSection key={s.title} title={s.title} content={s.content} sectionIdx={idx} />
        ))}
      </div>
    </div>
  );
}

function AGBContent() {
  return (
    <div data-testid="legal-content-agb" className="space-y-3">
      {AGB_PARAGRAPHS.map((p, idx) => (
        <AccordionSection key={p.title} title={p.title} content={p.content} sectionIdx={idx} />
      ))}
      <p className="text-[11px] text-[var(--color-text-tertiary)] mt-6 text-right">Stand: 06.02.2026</p>
    </div>
  );
}

function DatenschutzContent() {
  return (
    <div data-testid="legal-content-datenschutz" className="space-y-3">
      {DATENSCHUTZ_SECTIONS.map((s, idx) => (
        <AccordionSection key={s.title} title={s.title} content={s.content} sectionIdx={idx} />
      ))}
      <p className="text-[11px] text-[var(--color-text-tertiary)] mt-6 text-right">Stand: Februar 2026</p>
    </div>
  );
}

const TYPES = {
  legal: { titleKey: 'legal_page.impressum', Component: ImpressumContent, icon: FileText, labelDE: 'Impressum', labelEN: 'Legal Notice' },
  agb: { titleKey: 'legal_page.agb', Component: AGBContent, icon: Scale, labelDE: 'AGB', labelEN: 'Terms' },
  privacy: { titleKey: 'legal_page.privacy', Component: DatenschutzContent, icon: Shield, labelDE: 'Datenschutz', labelEN: 'Privacy' },
};

export default function LegalPage({ type = 'legal' }) {
  const { t, i18n } = useTranslation();
  const config = TYPES[type] || TYPES.legal;
  const { Component, labelDE, labelEN } = config;
  const isEN = i18n.language === 'en';

  const seoMap = {
    legal: { titleKey: 'seo.legal_title', descKey: 'seo.legal_desc', path: '/legal' },
    privacy: { titleKey: 'seo.privacy_title', descKey: 'seo.privacy_desc', path: '/privacy' },
    agb: { titleKey: 'seo.agb_title', descKey: 'seo.agb_desc', path: '/agb' },
  };
  const seo = seoMap[type] || seoMap.legal;

  const tocSections = type === 'legal' ? IMPRESSUM_SECTIONS.map(s => s.title) : type === 'agb' ? AGB_PARAGRAPHS.map(p => p.title) : DATENSCHUTZ_SECTIONS.map(s => s.title);
  const [activeSection, setActiveSection] = useState(0);
  const contentRef = useRef(null);

  const scrollToSection = useCallback((idx) => {
    setActiveSection(idx);
    const el = contentRef.current?.querySelector(`[data-section-idx="${idx}"]`);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, []);

  return (
    <div className="min-h-screen bg-white">
      <SEOHead titleKey={seo.titleKey} descKey={seo.descKey} path={seo.path} />
      <PublicNav />
      <main className="pt-16">

        {/* Hero */}
        <section className="relative overflow-hidden py-[48px] lg:py-[64px]"
          style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' }}>
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12 relative z-10">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-6 h-[2px]" style={{ background: 'var(--color-accent)' }} />
              <span className="text-[11px] font-semibold tracking-[0.2em] uppercase" style={{ color: 'var(--color-accent)' }}>
                {isEN ? 'Legal' : 'Rechtliches'}
              </span>
            </div>
            <h1 className="text-[28px] sm:text-[36px] lg:text-[44px] font-extrabold text-white leading-[1.08] tracking-[-0.03em] mb-4"
              style={{ fontFamily: 'var(--font-heading)' }} data-testid="legal-page-title">
              {isEN ? labelEN : labelDE}
            </h1>
            <p className="text-[15px] text-white/40 leading-[1.7] max-w-[520px]">
              {isEN
                ? 'Legal information, terms & conditions, and privacy policy of the W2G Academy GmbH.'
                : 'Rechtliche Informationen, Allgemeine Geschaeftsbedingungen und Datenschutzerklaerung der W2G Academy GmbH.'}
            </p>

            {/* Tab Navigation */}
            <nav className="flex flex-wrap gap-2 mt-8" data-testid="legal-tabs">
              {Object.entries(TYPES).map(([key, val]) => {
                const Icon = val.icon;
                const isActive = type === key;
                return (
                  <Link key={key}
                    to={key === 'legal' ? '/legal' : `/${key}`}
                    className={`inline-flex items-center gap-2 px-4 py-2 text-[12px] font-semibold rounded-[4px] transition-all ${
                      isActive ? 'text-[var(--color-primary-dark)]' : 'text-white/50 hover:text-white/80 border border-white/10 hover:border-white/20'
                    }`}
                    style={isActive ? { background: 'var(--color-accent)' } : {}}
                    data-testid={`legal-tab-${key}`}>
                    <Icon size={13} /> {isEN ? val.labelEN : val.labelDE}
                  </Link>
                );
              })}
            </nav>
          </div>
        </section>

        {/* Content */}
        <section className="py-[48px] lg:py-[64px]">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">

            {/* EN Notice */}
            {isEN && (
              <div className="mb-8 flex items-start gap-3 p-4 rounded-[4px] border border-[rgba(10,25,47,0.08)]"
                style={{ background: 'var(--color-surface-elevated)' }}>
                <span className="text-[10px] font-bold text-[var(--color-text-tertiary)] mt-0.5 shrink-0">i</span>
                <p className="text-[12px] text-[var(--color-text-secondary)]">{t('legal_page.de_only_note')}</p>
              </div>
            )}

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
              {/* Sticky ToC */}
              {tocSections.length > 3 && (
                <aside className="hidden lg:block lg:col-span-3">
                  <nav className="sticky top-24 space-y-0.5" data-testid="legal-toc">
                    <p className="text-[10px] font-semibold tracking-[0.15em] uppercase mb-3" style={{ color: 'var(--color-accent)' }}>
                      {isEN ? 'Table of Contents' : 'Inhaltsverzeichnis'}
                    </p>
                    {tocSections.map((title, idx) => (
                      <button key={idx} onClick={() => scrollToSection(idx)}
                        className={`block w-full text-left px-3 py-2 text-[12px] rounded-[3px] transition-all ${
                          activeSection === idx
                            ? 'font-semibold border-l-2'
                            : 'text-[var(--color-text-secondary)] hover:text-[var(--color-primary-dark)] hover:bg-[var(--color-surface-elevated)]'
                        }`}
                        style={activeSection === idx ? { color: 'var(--color-primary)', borderColor: 'var(--color-accent)', background: 'rgba(212,175,55,0.06)' } : {}}
                        data-testid={`toc-item-${idx}`}>
                        {title.length > 42 ? title.substring(0, 42) + '...' : title}
                      </button>
                    ))}
                  </nav>
                </aside>
              )}

              {/* Content */}
              <div ref={contentRef} className={tocSections.length > 3 ? 'lg:col-span-9' : 'lg:col-span-12 max-w-3xl'}>
                <Component t={t} isEN={isEN} />
              </div>
            </div>

            {/* Print + Contact */}
            <div className="mt-12 pt-6 border-t border-[rgba(10,25,47,0.08)] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <p className="text-[var(--color-text-tertiary)] text-[12px]">
                {t('legal_page.contact_faq')} – <a href="mailto:info@stk-aachen.de" className="hover:underline" style={{ color: 'var(--color-primary)' }}>info@stk-aachen.de</a>
              </p>
              <button onClick={() => window.print()}
                className="inline-flex items-center gap-2 px-4 py-2 text-[12px] font-semibold rounded-[4px] border border-[rgba(10,25,47,0.1)] text-[var(--color-text-secondary)] hover:border-[rgba(10,25,47,0.25)] hover:text-[var(--color-primary-dark)] transition-all self-start"
                data-testid="legal-print-btn">
                <Printer size={13} /> {isEN ? 'Print / PDF' : 'Drucken / PDF'}
              </button>
            </div>
          </div>
        </section>

      </main>
      <PublicFooter />
    </div>
  );
}
