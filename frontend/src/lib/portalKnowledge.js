/**
 * Portal Knowledge Layer – Zentrale Wissensquelle fuer das Bewerberportal.
 *
 * ARCHITEKTUR: Alle Bedeutungen, Erklaerungen, Hilfen und Handlungsanweisungen
 * sind hier zentral definiert und werden von allen Portal-Komponenten konsumiert.
 *
 * Keine harten Strings in den Seiten – alles aus dieser Source of Truth.
 */

// ─── STATUS-WISSENSMODELL ────────────────────────────────────────────────────
// Jeder Stage hat: Bedeutung, Erklaerung, wer ist am Zug, naechste Schritte,
// Risiken, CTAs, Wissenslinks, Fortschritt
export const STAGE_KNOWLEDGE = {
  lead_new: {
    de: {
      label: 'Anfrage eingegangen',
      meaning: 'Wir haben deine Anfrage erhalten und pruefen jetzt, welcher Bildungsweg fuer dich infrage kommt.',
      whatsHappening: 'Sichtung deiner Basisdaten und erste Zuordnung.',
      whoResponsible: 'team',
      whoLabel: 'Unser Team ist am Zug',
      nextSteps: ['Wir pruefen deine Angaben', 'Fehlende Dokumente werden angefordert', 'Erste Einschaetzung deines Bildungswegs'],
      risks: [],
      ctas: [
        { label: 'Dokumente hochladen', path: '/portal/documents', icon: 'FileText' },
        { label: 'Profil vervollstaendigen', path: '/portal/settings', icon: 'User' },
      ],
      knowledgeLinks: [
        { label: 'Welche Dokumente brauche ich?', url: '#docs-help' },
        { label: 'Was ist ein Studienkolleg?', url: 'https://www.studienkollegs.de/' },
      ],
      eta: '1-2 Werktage',
    },
    en: {
      label: 'Application Received',
      meaning: 'We have received your application and are now checking which educational path suits you.',
      whatsHappening: 'Review of your basic data and initial assignment.',
      whoResponsible: 'team',
      whoLabel: 'Our team is working on it',
      nextSteps: ['We review your information', 'Missing documents will be requested', 'Initial assessment of your pathway'],
      risks: [],
      ctas: [
        { label: 'Upload documents', path: '/portal/documents', icon: 'FileText' },
        { label: 'Complete your profile', path: '/portal/settings', icon: 'User' },
      ],
      knowledgeLinks: [
        { label: 'Which documents do I need?', url: '#docs-help' },
        { label: 'What is a Studienkolleg?', url: 'https://www.studienkollegs.de/' },
      ],
      eta: '1-2 business days',
    },
    progress: 10,
  },
  contacted: {
    de: {
      label: 'Kontaktiert',
      meaning: 'Wir haben dich kontaktiert und warten auf deine Rueckmeldung oder weitere Informationen.',
      whatsHappening: 'Warten auf deine Antwort.',
      whoResponsible: 'applicant',
      whoLabel: 'Du bist am Zug',
      nextSteps: ['Antworte auf unsere Nachricht', 'Stelle fehlende Informationen bereit'],
      risks: ['Verzoegerung bei fehlender Rueckmeldung'],
      ctas: [
        { label: 'Nachrichten lesen', path: '/portal/messages', icon: 'MessageSquare' },
        { label: 'Dokumente hochladen', path: '/portal/documents', icon: 'FileText' },
      ],
      knowledgeLinks: [],
      eta: 'Abhaengig von deiner Antwort',
    },
    en: {
      label: 'Contacted',
      meaning: 'We have reached out to you and are waiting for your response or additional information.',
      whatsHappening: 'Waiting for your reply.',
      whoResponsible: 'applicant',
      whoLabel: 'Your action needed',
      nextSteps: ['Reply to our message', 'Provide missing information'],
      risks: ['Delay if no response received'],
      ctas: [
        { label: 'Read messages', path: '/portal/messages', icon: 'MessageSquare' },
        { label: 'Upload documents', path: '/portal/documents', icon: 'FileText' },
      ],
      knowledgeLinks: [],
      eta: 'Depends on your response',
    },
    progress: 15,
  },
  pending_docs: {
    de: {
      label: 'Unterlagen angefordert',
      meaning: 'Wir benoetigen noch Dokumente von dir, um deine Bewerbung weiter bearbeiten zu koennen.',
      whatsHappening: 'Warten auf fehlende Unterlagen.',
      whoResponsible: 'applicant',
      whoLabel: 'Du bist am Zug',
      nextSteps: ['Lade fehlende Dokumente hoch', 'Pruefe die Dokumentenanforderungen'],
      risks: ['Bearbeitung kann erst nach Dokumenteingang fortgesetzt werden'],
      ctas: [
        { label: 'Dokumente hochladen', path: '/portal/documents', icon: 'FileText' },
        { label: 'Hilfe zu Dokumenten', path: '/portal/documents#help', icon: 'HelpCircle' },
      ],
      knowledgeLinks: [
        { label: 'Dokumentenleitfaden', url: '#docs-help' },
        { label: 'Welche Formate werden akzeptiert?', url: '#docs-formats' },
      ],
      eta: 'Abhaengig von deinem Upload',
    },
    en: {
      label: 'Documents Requested',
      meaning: 'We need additional documents from you to continue processing your application.',
      whatsHappening: 'Waiting for missing documents.',
      whoResponsible: 'applicant',
      whoLabel: 'Your action needed',
      nextSteps: ['Upload missing documents', 'Check document requirements'],
      risks: ['Processing cannot continue until documents are received'],
      ctas: [
        { label: 'Upload documents', path: '/portal/documents', icon: 'FileText' },
        { label: 'Document help', path: '/portal/documents#help', icon: 'HelpCircle' },
      ],
      knowledgeLinks: [
        { label: 'Document guide', url: '#docs-help' },
        { label: 'Which formats are accepted?', url: '#docs-formats' },
      ],
      eta: 'Depends on your upload',
    },
    progress: 25,
  },
  documents_requested: { /* alias */ },
  docs_requested: { /* alias */ },
  docs_received: {
    de: {
      label: 'Dokumente eingegangen',
      meaning: 'Wir haben deine Dokumente erhalten und bereiten die Pruefung vor.',
      whatsHappening: 'Dokumentenpruefung wird vorbereitet.',
      whoResponsible: 'team',
      whoLabel: 'Unser Team ist am Zug',
      nextSteps: ['Formale Pruefung deiner Unterlagen', 'Anabin-Abgleich fuer Schulabschluss'],
      risks: [],
      ctas: [
        { label: 'Status verfolgen', path: '/portal/journey', icon: 'MapPin' },
      ],
      knowledgeLinks: [
        { label: 'Was wird geprueft?', url: '#review-process' },
        { label: 'Was ist Anabin?', url: 'https://anabin.kmk.org/' },
      ],
      eta: '3-5 Werktage',
    },
    en: {
      label: 'Documents Received',
      meaning: 'We have received your documents and are preparing the review.',
      whatsHappening: 'Document review is being prepared.',
      whoResponsible: 'team',
      whoLabel: 'Our team is working on it',
      nextSteps: ['Formal review of your documents', 'Anabin verification for diploma'],
      risks: [],
      ctas: [
        { label: 'Track status', path: '/portal/journey', icon: 'MapPin' },
      ],
      knowledgeLinks: [
        { label: 'What is being reviewed?', url: '#review-process' },
        { label: 'What is Anabin?', url: 'https://anabin.kmk.org/' },
      ],
      eta: '3-5 business days',
    },
    progress: 40,
  },
  docs_review: {
    de: {
      label: 'In Pruefung',
      meaning: 'Deine Unterlagen werden aktuell von unserem Team geprueft.',
      whatsHappening: 'Dokumentenpruefung, Anabin-Abgleich, Sprachstand-Bewertung.',
      whoResponsible: 'team',
      whoLabel: 'Unser Team ist am Zug',
      nextSteps: ['Ergebnis der Pruefung', 'Ggf. Rueckfragen zu einzelnen Dokumenten'],
      risks: ['Bei Sonderfaellen kann die Pruefung laenger dauern'],
      ctas: [
        { label: 'Nachrichten pruefen', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [
        { label: 'Wie laeuft die Vorpruefung?', url: '#review-process' },
        { label: 'DAAD: Hochschulzugang', url: 'https://www.daad.de/' },
      ],
      eta: '3-7 Werktage',
    },
    en: {
      label: 'Under Review',
      meaning: 'Your documents are currently being reviewed by our team.',
      whatsHappening: 'Document review, Anabin verification, language assessment.',
      whoResponsible: 'team',
      whoLabel: 'Our team is working on it',
      nextSteps: ['Review result', 'Possible follow-up questions about documents'],
      risks: ['Special cases may require additional review time'],
      ctas: [
        { label: 'Check messages', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [
        { label: 'How does the review work?', url: '#review-process' },
        { label: 'DAAD: University Access', url: 'https://www.daad.de/' },
      ],
      eta: '3-7 business days',
    },
    progress: 50,
  },
  in_review: {
    de: {
      label: 'In Bearbeitung',
      meaning: 'Dein Fall wird aktuell bearbeitet. Wir pruefen alle Unterlagen und Angaben.',
      whatsHappening: 'Bewertung deiner Unterlagen und Eignung.',
      whoResponsible: 'team',
      whoLabel: 'Unser Team ist am Zug',
      nextSteps: ['Ergebnis der Pruefung', 'Ggf. Kursempfehlung oder Rueckfragen'],
      risks: [],
      ctas: [
        { label: 'Nachrichten pruefen', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [
        { label: 'Was passiert jetzt?', url: '#review-process' },
      ],
      eta: '3-5 Werktage',
    },
    en: {
      label: 'Under Review',
      meaning: 'Your case is currently being processed. We are reviewing all documents and information.',
      whatsHappening: 'Evaluation of your documents and eligibility.',
      whoResponsible: 'team',
      whoLabel: 'Our team is working on it',
      nextSteps: ['Review result', 'Possible course recommendation or follow-up'],
      risks: [],
      ctas: [
        { label: 'Check messages', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [
        { label: 'What happens now?', url: '#review-process' },
      ],
      eta: '3-5 business days',
    },
    progress: 45,
  },
  interview_scheduled: {
    de: {
      label: 'Beratungsgespraech geplant',
      meaning: 'Ein Beratungsgespraech ist fuer dich vereinbart. Bereite dich vor!',
      whatsHappening: 'Dein Beratungstermin wird vorbereitet.',
      whoResponsible: 'applicant',
      whoLabel: 'Bereite dich vor',
      nextSteps: ['Termin wahrnehmen', 'Fragen vorbereiten', 'Alle Unterlagen bereithalten'],
      risks: ['Verpasster Termin kann zu Verzoegerungen fuehren'],
      ctas: [
        { label: 'Nachrichten pruefen', path: '/portal/messages', icon: 'MessageSquare' },
        { label: 'Dokumente pruefen', path: '/portal/documents', icon: 'FileText' },
      ],
      knowledgeLinks: [
        { label: 'Tipps fuer das Beratungsgespraech', url: '#interview-tips' },
      ],
      eta: 'Siehe Terminbestaetigung',
    },
    en: {
      label: 'Consultation Scheduled',
      meaning: 'A consultation appointment has been scheduled for you. Get prepared!',
      whatsHappening: 'Your consultation is being prepared.',
      whoResponsible: 'applicant',
      whoLabel: 'Prepare yourself',
      nextSteps: ['Attend the appointment', 'Prepare your questions', 'Have all documents ready'],
      risks: ['Missing the appointment may cause delays'],
      ctas: [
        { label: 'Check messages', path: '/portal/messages', icon: 'MessageSquare' },
        { label: 'Review documents', path: '/portal/documents', icon: 'FileText' },
      ],
      knowledgeLinks: [
        { label: 'Tips for the consultation', url: '#interview-tips' },
      ],
      eta: 'See appointment confirmation',
    },
    progress: 55,
  },
  conditional_offer: {
    de: {
      label: 'Vorlaeufige Zusage',
      meaning: 'Du hast eine vorlaeufige Zusage erhalten! Es gibt noch offene Bedingungen.',
      whatsHappening: 'Pruefung ob alle Bedingungen erfuellt sind.',
      whoResponsible: 'applicant',
      whoLabel: 'Du bist am Zug',
      nextSteps: ['Offene Bedingungen erfuellen', 'Ggf. Zahlung leisten', 'Fehlende Nachweise einreichen'],
      risks: ['Zusage verfaellt bei Nichterfuellung der Bedingungen'],
      ctas: [
        { label: 'Rechnungen pruefen', path: '/portal/financials', icon: 'CreditCard' },
        { label: 'Dokumente pruefen', path: '/portal/documents', icon: 'FileText' },
      ],
      knowledgeLinks: [
        { label: 'Was bedeutet vorlaeufige Zusage?', url: '#conditional-offer' },
      ],
      eta: 'Abhaengig von dir',
    },
    en: {
      label: 'Conditional Offer',
      meaning: 'You have received a conditional offer! There are still open conditions.',
      whatsHappening: 'Checking if all conditions are met.',
      whoResponsible: 'applicant',
      whoLabel: 'Your action needed',
      nextSteps: ['Fulfill open conditions', 'Make payment if required', 'Submit missing documents'],
      risks: ['Offer expires if conditions are not met'],
      ctas: [
        { label: 'Check invoices', path: '/portal/financials', icon: 'CreditCard' },
        { label: 'Check documents', path: '/portal/documents', icon: 'FileText' },
      ],
      knowledgeLinks: [
        { label: 'What does conditional offer mean?', url: '#conditional-offer' },
      ],
      eta: 'Depends on you',
    },
    progress: 65,
  },
  offer_sent: {
    de: {
      label: 'Angebot versandt',
      meaning: 'Ein Angebot wurde dir zugesandt. Bitte pruefe und bestaetige es.',
      whatsHappening: 'Warten auf deine Bestaetigung.',
      whoResponsible: 'applicant',
      whoLabel: 'Du bist am Zug',
      nextSteps: ['Angebot pruefen', 'Zahlung leisten', 'Platz reservieren'],
      risks: ['Plaetze sind begrenzt – zeitnahe Reaktion empfohlen'],
      ctas: [
        { label: 'Rechnungen pruefen', path: '/portal/financials', icon: 'CreditCard' },
        { label: 'Nachrichten lesen', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [],
      eta: 'Bitte zeitnah reagieren',
    },
    en: {
      label: 'Offer Sent',
      meaning: 'An offer has been sent to you. Please review and confirm it.',
      whatsHappening: 'Waiting for your confirmation.',
      whoResponsible: 'applicant',
      whoLabel: 'Your action needed',
      nextSteps: ['Review the offer', 'Make payment', 'Reserve your spot'],
      risks: ['Spots are limited – timely response recommended'],
      ctas: [
        { label: 'Check invoices', path: '/portal/financials', icon: 'CreditCard' },
        { label: 'Read messages', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [],
      eta: 'Please respond promptly',
    },
    progress: 70,
  },
  enrolled: {
    de: {
      label: 'Eingeschrieben',
      meaning: 'Herzlichen Glueckwunsch! Du bist eingeschrieben. Bereite dich auf deinen Start vor.',
      whatsHappening: 'Startvorbereitung laeuft.',
      whoResponsible: 'team',
      whoLabel: 'Wir bereiten alles vor',
      nextSteps: ['Visa-Vorbereitung', 'Anreise planen', 'Kursstart vorbereiten'],
      risks: [],
      ctas: [
        { label: 'Nachrichten pruefen', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [
        { label: 'Make it in Germany: Vorbereitung', url: 'https://www.make-it-in-germany.com/' },
        { label: 'Visum beantragen', url: 'https://digital.diplo.de/' },
      ],
      eta: 'Siehe Kursstart',
    },
    en: {
      label: 'Enrolled',
      meaning: 'Congratulations! You are enrolled. Prepare for your start.',
      whatsHappening: 'Start preparation is underway.',
      whoResponsible: 'team',
      whoLabel: 'We are preparing everything',
      nextSteps: ['Visa preparation', 'Plan your arrival', 'Prepare for course start'],
      risks: [],
      ctas: [
        { label: 'Check messages', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [
        { label: 'Make it in Germany: Preparation', url: 'https://www.make-it-in-germany.com/' },
        { label: 'Apply for visa', url: 'https://digital.diplo.de/' },
      ],
      eta: 'See course start date',
    },
    progress: 90,
  },
  invoice_open: {
    de: {
      label: 'Rechnung offen',
      meaning: 'Es gibt eine offene Rechnung. Bitte leiste die Zahlung, um fortzufahren.',
      whatsHappening: 'Warten auf Zahlungseingang.',
      whoResponsible: 'applicant',
      whoLabel: 'Du bist am Zug',
      nextSteps: ['Rechnung bezahlen', 'Zahlungsbestaetigung abwarten'],
      risks: ['Verzoegerung bei ausbleibender Zahlung'],
      ctas: [
        { label: 'Rechnungen ansehen', path: '/portal/financials', icon: 'CreditCard' },
        { label: 'Hilfe bei Zahlung', path: '/portal/messages', icon: 'HelpCircle' },
      ],
      knowledgeLinks: [],
      eta: 'Abhaengig von deiner Zahlung',
    },
    en: {
      label: 'Invoice Open',
      meaning: 'There is an open invoice. Please make the payment to continue.',
      whatsHappening: 'Waiting for payment.',
      whoResponsible: 'applicant',
      whoLabel: 'Your action needed',
      nextSteps: ['Pay the invoice', 'Wait for payment confirmation'],
      risks: ['Delay if payment is not received'],
      ctas: [
        { label: 'View invoices', path: '/portal/financials', icon: 'CreditCard' },
        { label: 'Payment help', path: '/portal/messages', icon: 'HelpCircle' },
      ],
      knowledgeLinks: [],
      eta: 'Depends on your payment',
    },
    progress: 60,
  },
  payment_received: {
    de: {
      label: 'Zahlung eingegangen',
      meaning: 'Deine Zahlung ist bei uns eingegangen. Wir bearbeiten die naechsten Schritte.',
      whatsHappening: 'Zahlungsbestaetigung und Weiterbearbeitung.',
      whoResponsible: 'team',
      whoLabel: 'Unser Team ist am Zug',
      nextSteps: ['Bestaetigung der Anmeldung', 'Weitere Informationen zum Kursstart'],
      risks: [],
      ctas: [
        { label: 'Status verfolgen', path: '/portal/journey', icon: 'MapPin' },
      ],
      knowledgeLinks: [],
      eta: '1-3 Werktage',
    },
    en: {
      label: 'Payment Received',
      meaning: 'Your payment has been received. We are processing the next steps.',
      whatsHappening: 'Payment confirmation and further processing.',
      whoResponsible: 'team',
      whoLabel: 'Our team is working on it',
      nextSteps: ['Registration confirmation', 'Further course start information'],
      risks: [],
      ctas: [
        { label: 'Track status', path: '/portal/journey', icon: 'MapPin' },
      ],
      knowledgeLinks: [],
      eta: '1-3 business days',
    },
    progress: 80,
  },
  completed: {
    de: {
      label: 'Abgeschlossen',
      meaning: 'Dein Bewerbungsprozess ist abgeschlossen.',
      whatsHappening: 'Keine weiteren Schritte erforderlich.',
      whoResponsible: 'none',
      whoLabel: 'Abgeschlossen',
      nextSteps: [],
      risks: [],
      ctas: [],
      knowledgeLinks: [],
      eta: '',
    },
    en: {
      label: 'Completed',
      meaning: 'Your application process is complete.',
      whatsHappening: 'No further steps required.',
      whoResponsible: 'none',
      whoLabel: 'Completed',
      nextSteps: [],
      risks: [],
      ctas: [],
      knowledgeLinks: [],
      eta: '',
    },
    progress: 100,
  },
  on_hold: {
    de: {
      label: 'Warteschleife',
      meaning: 'Dein Fall ist aktuell pausiert. Dies kann verschiedene Gruende haben.',
      whatsHappening: 'Fall ist pausiert – wir informieren dich bei Aenderungen.',
      whoResponsible: 'team',
      whoLabel: 'Unser Team klaert',
      nextSteps: ['Abwarten', 'Bei Fragen den Chat nutzen'],
      risks: ['Moegliche Verzoegerung deines Starts'],
      ctas: [
        { label: 'Rueckfrage stellen', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [],
      eta: 'Wird mitgeteilt',
    },
    en: {
      label: 'On Hold',
      meaning: 'Your case is currently paused. This can have various reasons.',
      whatsHappening: 'Case is paused – we will inform you of changes.',
      whoResponsible: 'team',
      whoLabel: 'Our team is clarifying',
      nextSteps: ['Wait for update', 'Use chat for questions'],
      risks: ['Possible delay of your start date'],
      ctas: [
        { label: 'Ask a question', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [],
      eta: 'To be communicated',
    },
    progress: 30,
  },
  declined: {
    de: {
      label: 'Abgelehnt',
      meaning: 'Deine Bewerbung konnte leider nicht angenommen werden.',
      whatsHappening: 'Ablehnung ausgesprochen.',
      whoResponsible: 'none',
      whoLabel: 'Entscheidung getroffen',
      nextSteps: ['Gruende verstehen', 'Alternative Wege pruefen'],
      risks: [],
      ctas: [
        { label: 'Nachrichten lesen', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [
        { label: 'Alternative Bildungswege', url: 'https://www.make-it-in-germany.com/' },
        { label: 'Anerkennung in Deutschland', url: 'https://www.anerkennung-in-deutschland.de/' },
      ],
      eta: '',
    },
    en: {
      label: 'Declined',
      meaning: 'Unfortunately, your application could not be accepted.',
      whatsHappening: 'Decision has been made.',
      whoResponsible: 'none',
      whoLabel: 'Decision made',
      nextSteps: ['Understand the reasons', 'Explore alternative pathways'],
      risks: [],
      ctas: [
        { label: 'Read messages', path: '/portal/messages', icon: 'MessageSquare' },
      ],
      knowledgeLinks: [
        { label: 'Alternative educational paths', url: 'https://www.make-it-in-germany.com/' },
        { label: 'Recognition in Germany', url: 'https://www.anerkennung-in-deutschland.de/' },
      ],
      eta: '',
    },
    progress: 0,
  },
};

// Aliases
STAGE_KNOWLEDGE.documents_requested = STAGE_KNOWLEDGE.pending_docs;
STAGE_KNOWLEDGE.docs_requested = STAGE_KNOWLEDGE.pending_docs;

// Fallback for unknown stages
export function getStageKnowledge(stage, lang = 'de') {
  const entry = STAGE_KNOWLEDGE[stage];
  if (!entry) {
    return {
      label: stage || 'Unbekannt',
      meaning: lang === 'de'
        ? 'Dein aktueller Status wird geprueft.'
        : 'Your current status is being reviewed.',
      whatsHappening: '',
      whoResponsible: 'team',
      whoLabel: lang === 'de' ? 'Unser Team klaert' : 'Our team is clarifying',
      nextSteps: [],
      risks: [],
      ctas: [],
      knowledgeLinks: [],
      eta: '',
    };
  }
  return { ...(entry[lang] || entry.de), progress: entry.progress || 0 };
}

// ─── DOKUMENT-WISSENSMODELL ──────────────────────────────────────────────────
export const DOCUMENT_KNOWLEDGE = {
  passport: {
    de: {
      label: 'Reisepass / Personalausweis',
      purpose: 'Identitaetsnachweis – notwendig fuer die Identifikation und spaeter fuer das Visum.',
      quality: 'Gut lesbarer Scan oder Foto aller relevanten Seiten. Keine abgeschnittenen Ecken.',
      formats: 'PDF, JPG, PNG (max. 10 MB)',
      required: true,
    },
    en: {
      label: 'Passport / ID Card',
      purpose: 'Proof of identity – required for identification and later for your visa.',
      quality: 'Clear scan or photo of all relevant pages. No cut corners.',
      formats: 'PDF, JPG, PNG (max 10 MB)',
      required: true,
    },
    icon: 'Shield',
  },
  highschool_diploma: {
    de: {
      label: 'Schulzeugnis / Hochschulzugangsberechtigung',
      purpose: 'Nachweis deines Schulabschlusses – Grundlage fuer die Pruefung deiner Hochschulzugangsberechtigung (HZB) und die Zuordnung zum Studienkolleg-Kurs.',
      quality: 'Vollstaendiges Zeugnis mit allen Seiten, gut lesbar. Bei nicht-lateinischer Schrift: beeidigte Uebersetzung beifuegen.',
      formats: 'PDF, JPG, PNG (max. 10 MB)',
      required: true,
    },
    en: {
      label: 'School Certificate / University Entrance Qualification',
      purpose: 'Proof of your school qualification – basis for assessing your university entrance qualification (HZB) and course assignment.',
      quality: 'Complete certificate with all pages, clearly readable. For non-Latin scripts: include sworn translation.',
      formats: 'PDF, JPG, PNG (max 10 MB)',
      required: true,
    },
    icon: 'GraduationCap',
  },
  school_certificate: {
    de: {
      label: 'Schulzeugnis',
      purpose: 'Nachweis deines Schulabschlusses fuer die Vorpruefung.',
      quality: 'Vollstaendiges Zeugnis, gut lesbar.',
      formats: 'PDF, JPG, PNG (max. 10 MB)',
      required: true,
    },
    en: {
      label: 'School Certificate',
      purpose: 'Proof of your school qualification for preliminary review.',
      quality: 'Complete certificate, clearly readable.',
      formats: 'PDF, JPG, PNG (max 10 MB)',
      required: true,
    },
    icon: 'GraduationCap',
  },
  language_certificate: {
    de: {
      label: 'Deutsches Sprachzertifikat',
      purpose: 'Nachweis deiner Deutschkenntnisse – entscheidend fuer die Kurszuordnung und den Sprachpfad (z.B. B1 fuer Studienkolleg).',
      quality: 'Offizielles Zertifikat (z.B. Goethe, TestDaF, telc). Vollstaendig und gut lesbar.',
      formats: 'PDF, JPG, PNG (max. 10 MB)',
      required: true,
    },
    en: {
      label: 'German Language Certificate',
      purpose: 'Proof of your German language skills – crucial for course assignment and language pathway (e.g. B1 for Studienkolleg).',
      quality: 'Official certificate (e.g. Goethe, TestDaF, telc). Complete and clearly readable.',
      formats: 'PDF, JPG, PNG (max 10 MB)',
      required: true,
    },
    icon: 'Languages',
  },
  photo: {
    de: {
      label: 'Passfoto',
      purpose: 'Fuer offizielle Dokumente und dein Studierendenprofil.',
      quality: 'Biometrisches Passfoto (35x45mm), aktuell, neutraler Hintergrund.',
      formats: 'JPG, PNG (max. 5 MB)',
      required: false,
    },
    en: {
      label: 'Passport Photo',
      purpose: 'For official documents and your student profile.',
      quality: 'Biometric passport photo (35x45mm), recent, neutral background.',
      formats: 'JPG, PNG (max 5 MB)',
      required: false,
    },
    icon: 'Camera',
  },
  birth_certificate: {
    de: {
      label: 'Geburtsurkunde',
      purpose: 'Ergaenzender Identitaetsnachweis, ggf. fuer Visum oder Anmeldung erforderlich.',
      quality: 'Gut lesbarer Scan. Bei nicht-lateinischer Schrift: beeidigte Uebersetzung.',
      formats: 'PDF, JPG, PNG (max. 10 MB)',
      required: false,
    },
    en: {
      label: 'Birth Certificate',
      purpose: 'Supplementary proof of identity, may be required for visa or registration.',
      quality: 'Clear scan. For non-Latin scripts: include sworn translation.',
      formats: 'PDF, JPG, PNG (max 10 MB)',
      required: false,
    },
    icon: 'FileText',
  },
  other: {
    de: {
      label: 'Sonstiges Dokument',
      purpose: 'Zusaetzliche Unterlagen, die fuer deinen Fall relevant sein koennen.',
      quality: 'Gut lesbar, vollstaendig.',
      formats: 'PDF, JPG, PNG, DOC (max. 10 MB)',
      required: false,
    },
    en: {
      label: 'Other Document',
      purpose: 'Additional documents that may be relevant to your case.',
      quality: 'Clearly readable, complete.',
      formats: 'PDF, JPG, PNG, DOC (max 10 MB)',
      required: false,
    },
    icon: 'File',
  },
};

export function getDocumentKnowledge(docType, lang = 'de') {
  const entry = DOCUMENT_KNOWLEDGE[docType];
  if (!entry) return DOCUMENT_KNOWLEDGE.other[lang];
  return { ...(entry[lang] || entry.de), icon: entry.icon };
}

// ─── CHAT QUICK TOPICS ──────────────────────────────────────────────────────
export const CHAT_QUICK_TOPICS = {
  de: [
    { key: 'missing_docs', label: 'Fehlende Dokumente', question: 'Welche Dokumente fehlen noch fuer meine Bewerbung?' },
    { key: 'status_explain', label: 'Meinen Status verstehen', question: 'Was bedeutet mein aktueller Status und was sind die naechsten Schritte?' },
    { key: 'doc_rejected', label: 'Dokument abgelehnt', question: 'Ein Dokument wurde abgelehnt. Was soll ich tun?' },
    { key: 'payment_help', label: 'Zahlung / Rechnung', question: 'Ich habe eine Frage zu einer Rechnung oder Zahlung.' },
    { key: 'language_path', label: 'Sprachkurs / B1', question: 'Welchen Sprachkurs brauche ich und wie erreiche ich B1?' },
    { key: 'visa_info', label: 'Visum & Einreise', question: 'Was muss ich fuer mein Visum und die Einreise wissen?' },
    { key: 'fsp_info', label: 'FSP / Sonderfall', question: 'Was ist die Feststellungspruefung und betrifft sie mich?' },
    { key: 'general', label: 'Allgemeine Frage', question: 'Ich habe eine allgemeine Frage zu meiner Bewerbung.' },
  ],
  en: [
    { key: 'missing_docs', label: 'Missing Documents', question: 'Which documents are still missing for my application?' },
    { key: 'status_explain', label: 'Understand My Status', question: 'What does my current status mean and what are the next steps?' },
    { key: 'doc_rejected', label: 'Document Rejected', question: 'A document was rejected. What should I do?' },
    { key: 'payment_help', label: 'Payment / Invoice', question: 'I have a question about an invoice or payment.' },
    { key: 'language_path', label: 'Language Course / B1', question: 'Which language course do I need and how do I reach B1?' },
    { key: 'visa_info', label: 'Visa & Entry', question: 'What do I need to know about my visa and entry?' },
    { key: 'fsp_info', label: 'FSP / Special Case', question: 'What is the FSP and does it apply to me?' },
    { key: 'general', label: 'General Question', question: 'I have a general question about my application.' },
  ],
};

// ─── DYNAMIC CHECKLIST LOGIC ─────────────────────────────────────────────────
// Generates checklist items based on application state, documents and profile
export function generateChecklist(application, documents, invoices, lang = 'de') {
  const items = [];
  const docTypes = (documents || []).map(d => d.document_type);
  const docStatuses = {};
  (documents || []).forEach(d => { docStatuses[d.document_type] = d.status; });

  const required = ['passport', 'language_certificate'];
  const schoolDocs = ['highschool_diploma', 'school_certificate'];
  const hasSchoolDoc = schoolDocs.some(t => docTypes.includes(t));

  // Check required documents
  required.forEach(type => {
    const docInfo = DOCUMENT_KNOWLEDGE[type];
    const docLabel = docInfo ? (docInfo[lang]?.label || docInfo.de?.label) : type;
    if (!docTypes.includes(type)) {
      items.push({
        key: `upload_${type}`, priority: 'high', status: 'missing',
        label: lang === 'de' ? `${docLabel} hochladen` : `Upload ${docLabel}`,
        description: lang === 'de' ? 'Pflichtdokument fehlt' : 'Required document missing',
        path: '/portal/documents', icon: 'FileText',
      });
    } else if (docStatuses[type] === 'rejected') {
      items.push({
        key: `reupload_${type}`, priority: 'high', status: 'action_needed',
        label: lang === 'de' ? `${docLabel} erneut hochladen` : `Re-upload ${docLabel}`,
        description: lang === 'de' ? 'Dokument wurde abgelehnt' : 'Document was rejected',
        path: '/portal/documents', icon: 'AlertTriangle',
      });
    } else if (docStatuses[type] === 'pending' || docStatuses[type] === 'uploaded') {
      items.push({
        key: `review_${type}`, priority: 'low', status: 'in_progress',
        label: lang === 'de' ? `${docLabel} wird geprueft` : `${docLabel} under review`,
        description: lang === 'de' ? 'Warte auf Pruefungsergebnis' : 'Waiting for review result',
        path: '/portal/documents', icon: 'Clock',
      });
    } else if (docStatuses[type] === 'approved' || docStatuses[type] === 'accepted') {
      items.push({
        key: `done_${type}`, priority: 'none', status: 'done',
        label: lang === 'de' ? `${docLabel} akzeptiert` : `${docLabel} accepted`,
        description: '',
        path: '/portal/documents', icon: 'CheckCircle',
      });
    }
  });

  // School document
  if (!hasSchoolDoc) {
    items.push({
      key: 'upload_school', priority: 'high', status: 'missing',
      label: lang === 'de' ? 'Schulzeugnis hochladen' : 'Upload school certificate',
      description: lang === 'de' ? 'Pflichtdokument fuer Hochschulzugangspruefung' : 'Required for university entrance assessment',
      path: '/portal/documents', icon: 'GraduationCap',
    });
  }

  // Profile completeness
  const applicant = application?.applicant || {};
  if (!applicant.full_name || !applicant.country || !applicant.date_of_birth) {
    items.push({
      key: 'complete_profile', priority: 'medium', status: 'action_needed',
      label: lang === 'de' ? 'Profil vervollstaendigen' : 'Complete your profile',
      description: lang === 'de' ? 'Persoenliche Daten ergaenzen' : 'Add personal information',
      path: '/portal/settings', icon: 'User',
    });
  }

  // Invoice check
  const openInvoices = (invoices || []).filter(i => i.status === 'open' || i.status === 'overdue');
  if (openInvoices.length > 0) {
    items.push({
      key: 'pay_invoice', priority: 'high', status: 'action_needed',
      label: lang === 'de' ? `${openInvoices.length} offene Rechnung(en)` : `${openInvoices.length} open invoice(s)`,
      description: lang === 'de' ? 'Bitte leiste die Zahlung' : 'Please make the payment',
      path: '/portal/financials', icon: 'CreditCard',
    });
  }

  // Sort: high > medium > low > none; missing/action > in_progress > done
  const priorityOrder = { high: 0, medium: 1, low: 2, none: 3 };
  const statusOrder = { missing: 0, action_needed: 1, in_progress: 2, done: 3 };
  items.sort((a, b) => {
    const p = (priorityOrder[a.priority] || 3) - (priorityOrder[b.priority] || 3);
    if (p !== 0) return p;
    return (statusOrder[a.status] || 3) - (statusOrder[b.status] || 3);
  });

  return items;
}
