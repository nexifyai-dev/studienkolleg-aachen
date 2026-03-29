import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';
import { CheckCircle, ArrowRight, ChevronDown, ChevronUp } from 'lucide-react';

const COURSES_DE = {
  t: {
    subjects: ['Maschinenbau', 'Elektrotechnik', 'Industrieengineering', 'Informatik (technisch)', 'Mathematik', 'Physik'],
    accentClass: 'border-l-primary',
  },
  m: {
    subjects: ['Medizin', 'Zahnmedizin', 'Biologie', 'Biochemie', 'Pharmazie', 'Pflegewissenschaft'],
    accentClass: 'border-l-slate-600',
  },
  w: {
    subjects: ['BWL', 'Wirtschaftsinformatik', 'Tourismusmanagement', 'Soziologie', 'Politikwissenschaft', 'Jura'],
    accentClass: 'border-l-slate-400',
  },
  mt: {
    subjects: ['Ingenieurmedizin', 'Biomedizintechnik', 'Mathematik', 'Physik', 'Biologie'],
    accentClass: 'border-l-primary',
  },
};

const COURSE_SLUGS = ['t', 'm', 'w', 'mt'];

const COURSE_KEYS = { t: 'T-Kurs', m: 'M-Kurs', w: 'W-Kurs', mt: 'M/T-Kurs' };

const LANG_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1'];

function CourseCard({ slug, t }) {
  const [open, setOpen] = useState(false);
  const { subjects, accentClass } = COURSES_DE[slug];
  const key = COURSE_KEYS[slug];
  return (
    <div
      className={`bg-white border border-slate-200 border-l-4 ${accentClass} rounded-sm hover:shadow-card-hover transition-all`}
      data-testid={`course-detail-${slug}`}
    >
      <div className="p-5 sm:p-6">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div>
            <span className="inline-block text-xs font-bold px-2.5 py-1 rounded-sm bg-primary/8 text-primary border border-primary/20 mb-2">
              {key}
            </span>
            <h3 className="font-heading font-bold text-primary text-lg sm:text-xl">
              {t(`courses_page.course_cards.${slug}.label`)}
            </h3>
          </div>
          <span className="shrink-0 text-xs text-slate-500 bg-slate-50 px-2 py-1 rounded-sm border border-slate-100 whitespace-nowrap">
            {t('courses_page.lang_req')}
          </span>
        </div>
        <p className="text-slate-500 text-sm mb-4 italic">
          {t(`courses_page.course_cards.${slug}.for`)}
        </p>

        <button
          onClick={() => setOpen(!open)}
          className="flex items-center gap-1.5 text-sm text-primary hover:underline font-medium mb-2"
          data-testid={`course-expand-${slug}`}
        >
          {t('courses_page.expand_btn')}
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>

        {open && (
          <ul className="space-y-1.5 mt-2 mb-3">
            {subjects.map(s => (
              <li key={s} className="flex items-center gap-2 text-sm text-slate-700">
                <div className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                {s}
              </li>
            ))}
          </ul>
        )}

        <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
          <p className="text-xs text-slate-400">{t(`courses_page.course_cards.${slug}.fsp`)}</p>
          <Link to="/apply"
            className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
            data-testid={`course-apply-${slug}`}
          >
            {t('nav.apply')} <ArrowRight size={12} />
          </Link>
        </div>
      </div>
    </div>
  );
}

const SEMESTER_BADGES = {
  running: 'semester_running',
  open: 'semester_open',
  soon: 'semester_soon',
};

const SEMESTERS = [
  { sem: 'Wintersemester 2025/26', start: 'Oktober 2025', type: 'running' },
  { sem: 'Sommersemester 2026', start: 'April 2026', type: 'open' },
  { sem: 'Wintersemester 2026/27', start: 'Oktober 2026', type: 'open' },
  { sem: 'Sommersemester 2027', start: 'April 2027', type: 'soon' },
  { sem: 'Wintersemester 2027/28', start: 'Oktober 2027', type: 'soon' },
];

export default function CoursesPage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-white">
      <SEOHead titleKey="seo.courses_title" descKey="seo.courses_desc" path="/courses" />
      <PublicNav />
      <main className="pt-16">

        {/* Hero */}
        <section className="bg-primary py-10 sm:py-16 lg:py-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
            <h1 className="text-2xl sm:text-4xl lg:text-5xl font-heading font-bold text-white mb-3 sm:mb-4">
              {t('courses_page.hero_title')}
            </h1>
            <p className="text-white/70 text-sm sm:text-base lg:text-lg max-w-2xl mx-auto leading-relaxed">
              {t('courses_page.hero_sub')}
            </p>
          </div>
        </section>

        {/* FSP Hinweis */}
        <section className="border-b border-slate-100">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6">
            <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 rounded-sm px-5 py-4">
              <CheckCircle size={16} className="text-primary mt-0.5 shrink-0" />
              <p className="text-sm text-slate-600 leading-relaxed">
                {t('courses_page.fsp_notice')}
              </p>
            </div>
          </div>
        </section>

        {/* Hauptkurse */}
        <section className="py-10 sm:py-16 lg:py-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="mb-8 sm:mb-10">
              <h2 className="text-xl sm:text-2xl lg:text-3xl font-heading font-bold text-primary mb-3">
                {t('courses_page.main_title')}
              </h2>
              <p className="text-slate-600 max-w-2xl">
                {t('courses_page.main_desc')}
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {COURSE_SLUGS.map(slug => <CourseCard key={slug} slug={slug} t={t} />)}
            </div>
          </div>
        </section>

        {/* Sprachkurse */}
        <section className="py-10 sm:py-16 lg:py-20 bg-slate-50 border-t border-slate-100">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-10 items-start">
              <div>
                <span className="inline-block text-xs font-bold px-2.5 py-1 rounded-sm bg-primary/8 text-primary border border-primary/20 mb-4">
                  {t('courses_page.lang_badge')}
                </span>
                <h2 className="text-2xl sm:text-3xl font-heading font-bold text-primary mb-4">
                  {t('courses_page.lang_course_title')}
                </h2>
                <p className="text-slate-600 mb-6 leading-relaxed">
                  {t('courses_page.lang_course_desc')}
                </p>
                <Link to="/apply"
                  className="inline-flex items-center gap-2 bg-primary text-white font-semibold px-6 py-3 rounded-sm hover:bg-primary-hover transition-all"
                  data-testid="language-course-apply-btn">
                  {t('courses_page.lang_course_btn')} <ArrowRight size={16} />
                </Link>
              </div>
              <div className="grid grid-cols-1 gap-3">
                {LANG_LEVELS.map(level => (
                  <div key={level}
                    className="bg-white border border-slate-200 rounded-sm px-4 py-3 flex items-start gap-3"
                    data-testid={`lang-level-${level}`}>
                    <span className="font-bold text-primary text-sm w-8 shrink-0">{level}</span>
                    <div>
                      <p className="font-semibold text-slate-800 text-sm">{t(`courses_page.levels.${level}.label`)}</p>
                      <p className="text-slate-500 text-xs">{t(`courses_page.levels.${level}.desc`)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Kursstart-Übersicht */}
        <section className="py-10 sm:py-16 lg:py-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <h2 className="text-xl sm:text-2xl font-heading font-bold text-primary mb-5 sm:mb-6">
              {t('courses_page.starts_title')}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {SEMESTERS.map(s => (
                <div key={s.sem}
                  className="bg-white border border-slate-200 rounded-sm px-5 py-4"
                  data-testid={`semester-${s.sem.replace(/\s+/g, '-').toLowerCase()}`}>
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-semibold text-slate-800 text-sm">{s.sem}</p>
                    <span className={`text-xs px-2 py-0.5 rounded-sm ${
                      s.type === 'running' ? 'bg-primary/10 text-primary border border-primary/25' :
                      s.type === 'open' ? 'bg-primary/8 text-primary border border-primary/20' :
                      'bg-slate-50 text-slate-500 border border-slate-200'
                    }`}>{t(`courses_page.${SEMESTER_BADGES[s.type]}`)}</span>
                  </div>
                  <p className="text-slate-500 text-xs">{t('courses_page.semester_start')}: {s.start}</p>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-400 mt-4">{t('courses_page.starts_note')}</p>
          </div>
        </section>

        {/* CTA */}
        <section className="bg-primary py-10 sm:py-14 lg:py-16">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 text-center">
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-heading font-bold text-white mb-3 sm:mb-4">
              {t('courses_page.cta_title')}
            </h2>
            <p className="text-white/70 mb-6 sm:mb-8 max-w-xl mx-auto">
              {t('courses_page.cta_desc')}
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/apply"
                data-testid="courses-cta-apply"
                className="bg-white text-primary font-semibold px-6 sm:px-8 py-3 sm:py-3.5 rounded-sm hover:bg-slate-50 transition-all inline-flex items-center justify-center gap-2 text-sm sm:text-base">
                {t('courses_page.cta_apply')} <ArrowRight size={16} />
              </Link>
              <Link to="/contact"
                data-testid="courses-cta-contact"
                className="border-2 border-white/40 text-white font-semibold px-6 sm:px-8 py-3 sm:py-3.5 rounded-sm hover:border-white/70 transition-all inline-flex items-center justify-center text-sm sm:text-base">
                {t('courses_page.cta_contact')}
              </Link>
            </div>
          </div>
        </section>

      </main>
      <PublicFooter />
    </div>
  );
}
