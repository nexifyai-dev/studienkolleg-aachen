import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import { CheckCircle, ArrowRight, ChevronDown, ChevronUp } from 'lucide-react';

const COURSES = [
  {
    key: 'T-Kurs',
    slug: 't',
    label: 'Technik & Naturwissenschaften',
    subjects: [
      'Maschinenbau', 'Elektrotechnik', 'Industrieengineering',
      'Informatik (technisch)', 'Mathematik', 'Physik',
    ],
    fsp: 'Feststellungsprüfung Technik',
    language: 'Mindest B1 Deutsch',
    for: 'Für angehende Ingenieure und Naturwissenschaftler',
    accentClass: 'border-l-primary',
  },
  {
    key: 'M-Kurs',
    slug: 'm',
    label: 'Medizin & Biowissenschaften',
    subjects: [
      'Medizin', 'Zahnmedizin', 'Biologie', 'Biochemie',
      'Pharmazie', 'Pflegewissenschaft',
    ],
    fsp: 'Feststellungsprüfung Medizin/Bio',
    language: 'Mindest B1 Deutsch',
    for: 'Für angehende Mediziner und Biowissenschaftler',
    accentClass: 'border-l-slate-600',
  },
  {
    key: 'W-Kurs',
    slug: 'w',
    label: 'Wirtschaft & Sozialwissenschaften',
    subjects: [
      'BWL', 'Wirtschaftsinformatik', 'Tourismusmanagement',
      'Soziologie', 'Politikwissenschaft', 'Jura',
    ],
    fsp: 'Feststellungsprüfung Wirtschaft',
    language: 'Mindest B1 Deutsch',
    for: 'Für angehende Wirtschafts- und Sozialwissenschaftler',
    accentClass: 'border-l-slate-400',
  },
  {
    key: 'M/T-Kurs',
    slug: 'mt',
    label: 'Kombination Medizin + Technik',
    subjects: [
      'Ingenieurmedizin', 'Biomedizintechnik',
      'Mathematik', 'Physik', 'Biologie',
    ],
    fsp: 'Feststellungsprüfung M+T',
    language: 'Mindest B1 Deutsch',
    for: 'Für Studierende mit breitem Fächerinteresse',
    accentClass: 'border-l-primary',
  },
];

const LANGUAGE_COURSES = [
  { level: 'A1', label: 'Anfänger', desc: 'Keine Vorkenntnisse erforderlich – strukturierter Einstieg.' },
  { level: 'A2', label: 'Grundstufe', desc: 'Aufbau auf A1-Kenntnisse, Alltagskommunikation.' },
  { level: 'B1', label: 'Mittelstufe', desc: 'Voraussetzung für Studienkolleg-Kurse.' },
  { level: 'B2', label: 'Obermittelstufe', desc: 'Flüssige Kommunikation, komplexe Texte.' },
  { level: 'C1', label: 'Fortgeschritten', desc: 'Studiumsreifes Deutsch, DSH-Vorbereitung.' },
];

function CourseCard({ course }) {
  const [open, setOpen] = useState(false);
  return (
    <div
      className={`bg-white border border-slate-200 border-l-4 ${course.accentClass} rounded-sm hover:shadow-card-hover transition-all`}
      data-testid={`course-detail-${course.slug}`}
    >
      <div className="p-6">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div>
            <span className="inline-block text-xs font-bold px-2.5 py-1 rounded-sm bg-primary/8 text-primary border border-primary/20 mb-2">
              {course.key}
            </span>
            <h3 className="font-heading font-bold text-primary text-xl">{course.label}</h3>
          </div>
          <span className="shrink-0 text-xs text-slate-500 bg-slate-50 px-2 py-1 rounded-sm border border-slate-100 whitespace-nowrap">
            {course.language}
          </span>
        </div>
        <p className="text-slate-500 text-sm mb-4 italic">{course.for}</p>

        <button
          onClick={() => setOpen(!open)}
          className="flex items-center gap-1.5 text-sm text-primary hover:underline font-medium mb-2"
          data-testid={`course-expand-${course.slug}`}
        >
          Geeignete Studienbereiche
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>

        {open && (
          <ul className="space-y-1.5 mt-2 mb-3">
            {course.subjects.map(s => (
              <li key={s} className="flex items-center gap-2 text-sm text-slate-700">
                <div className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                {s}
              </li>
            ))}
          </ul>
        )}

        <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
          <p className="text-xs text-slate-400">{course.fsp}</p>
          <Link to="/apply"
            className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
            data-testid={`course-apply-${course.slug}`}
          >
            Jetzt bewerben <ArrowRight size={12} />
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function CoursesPage() {
  return (
    <div className="min-h-screen bg-white">
      <PublicNav />
      <main className="pt-16">

        {/* Hero */}
        <section className="bg-primary py-16 sm:py-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-heading font-bold text-white mb-4">
              Unsere Kurse
            </h1>
            <p className="text-blue-200 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
              Strukturierte Vorbereitung auf die Feststellungsprüfung (FSP) –
              die offizielle Hochschulzugangsvoraussetzung für internationale Studierende in Deutschland.
            </p>
          </div>
        </section>

        {/* FSP Hinweis */}
        <section className="border-b border-slate-100">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6">
            <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 rounded-sm px-5 py-4">
              <CheckCircle size={16} className="text-primary mt-0.5 shrink-0" />
              <p className="text-sm text-slate-600 leading-relaxed">
                <strong className="text-slate-800">Feststellungsprüfung (FSP):</strong>{' '}
                Alle Kurse bereiten auf die FSP vor. Die Berechtigung zur Teilnahme wird durch die
                zuständige Bezirksregierung entschieden. Das Studienkolleg begleitet dich durch den
                gesamten Prozess.
              </p>
            </div>
          </div>
        </section>

        {/* Hauptkurse */}
        <section className="py-16 sm:py-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="mb-10">
              <h2 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-3">
                Studienvorbereitende Schwerpunktkurse
              </h2>
              <p className="text-slate-600 max-w-2xl">
                Wähle den Kurs, der zu deinem angestrebten Studienfach passt. Unsere Sachberater
                helfen dir bei der Auswahl.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {COURSES.map(course => <CourseCard key={course.key} course={course} />)}
            </div>
          </div>
        </section>

        {/* Sprachkurse */}
        <section className="py-16 sm:py-20 bg-slate-50 border-t border-slate-100">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-start">
              <div>
                <span className="inline-block text-xs font-bold px-2.5 py-1 rounded-sm bg-primary/8 text-primary border border-primary/20 mb-4">
                  Sprachkurs
                </span>
                <h2 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-4">
                  Deutsch A1–C1
                </h2>
                <p className="text-slate-600 mb-6 leading-relaxed">
                  Unsere Sprachkurse bereiten sprachlich auf das Studienkolleg oder
                  das deutsche Studium vor. B1 ist die Mindestvoraussetzung für alle
                  studienvorbereitenden Kurse.
                </p>
                <Link to="/apply"
                  className="inline-flex items-center gap-2 bg-primary text-white font-semibold px-6 py-3 rounded-sm hover:bg-primary-hover transition-all"
                  data-testid="language-course-apply-btn">
                  Sprachkurs anfragen <ArrowRight size={16} />
                </Link>
              </div>
              <div className="grid grid-cols-1 gap-3">
                {LANGUAGE_COURSES.map(lc => (
                  <div key={lc.level}
                    className="bg-white border border-slate-200 rounded-sm px-4 py-3 flex items-start gap-3"
                    data-testid={`lang-level-${lc.level}`}>
                    <span className="font-bold text-primary text-sm w-8 shrink-0">{lc.level}</span>
                    <div>
                      <p className="font-semibold text-slate-800 text-sm">{lc.label}</p>
                      <p className="text-slate-500 text-xs">{lc.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Kursstart-Übersicht */}
        <section className="py-16 sm:py-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <h2 className="text-2xl font-heading font-bold text-primary mb-6">
              Verfügbare Startzeitpunkte
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { sem: 'Wintersemester 2025/26', start: 'Oktober 2025', badge: 'Läuft' },
                { sem: 'Sommersemester 2026', start: 'April 2026', badge: 'Offen' },
                { sem: 'Wintersemester 2026/27', start: 'Oktober 2026', badge: 'Offen' },
                { sem: 'Sommersemester 2027', start: 'April 2027', badge: 'Bald' },
                { sem: 'Wintersemester 2027/28', start: 'Oktober 2027', badge: 'Bald' },
              ].map(s => (
                <div key={s.sem}
                  className="bg-white border border-slate-200 rounded-sm px-5 py-4"
                  data-testid={`semester-${s.sem.replace(/\s+/g, '-').toLowerCase()}`}>
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-semibold text-slate-800 text-sm">{s.sem}</p>
                    <span className={`text-xs px-2 py-0.5 rounded-sm ${
                      s.badge === 'Läuft' ? 'bg-primary/10 text-primary border border-primary/25' :
                      s.badge === 'Offen' ? 'bg-primary/8 text-primary border border-primary/20' :
                      'bg-slate-50 text-slate-500 border border-slate-200'
                    }`}>{s.badge}</span>
                  </div>
                  <p className="text-slate-500 text-xs">Kursstart: {s.start}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="bg-primary py-16">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 text-center">
            <h2 className="text-2xl sm:text-3xl font-heading font-bold text-white mb-4">
              Welcher Kurs passt zu dir?
            </h2>
            <p className="text-blue-200 mb-8 max-w-xl mx-auto">
              Wir helfen dir bei der Kursauswahl und begleiten dich von der ersten Anfrage bis zur Zulassung.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/apply"
                data-testid="courses-cta-apply"
                className="bg-white text-primary font-semibold px-8 py-3.5 rounded-sm hover:bg-slate-50 transition-all inline-flex items-center justify-center gap-2">
                Jetzt bewerben <ArrowRight size={16} />
              </Link>
              <Link to="/contact"
                data-testid="courses-cta-contact"
                className="border-2 border-white/40 text-white font-semibold px-8 py-3.5 rounded-sm hover:border-white/70 transition-all inline-flex items-center justify-center">
                Beratungsgespräch anfragen
              </Link>
            </div>
          </div>
        </section>

      </main>
      <PublicFooter />
    </div>
  );
}
