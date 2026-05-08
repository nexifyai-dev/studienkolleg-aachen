import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';
import { CheckCircle, ArrowRight, ChevronDown, ChevronUp, GraduationCap, BookOpen, Briefcase, Heart } from 'lucide-react';

/* ── Daten ── */
const COURSE_DATA = {
  t: { icon: BookOpen, color: 'var(--color-primary)', subjects: ['Maschinenbau', 'Elektrotechnik', 'Industrieengineering', 'Informatik (technisch)', 'Mathematik', 'Physik', 'Architektur', 'Bauingenieurwesen'] },
  m: { icon: Heart, color: 'var(--color-primary)', subjects: ['Medizin', 'Zahnmedizin', 'Biologie', 'Biochemie', 'Pharmazie', 'Pflegewissenschaft', 'Veterinärmedizin', 'Lebensmittelchemie'] },
  w: { icon: Briefcase, color: 'var(--color-accent)', subjects: ['BWL', 'Wirtschaftsinformatik', 'Tourismusmanagement', 'Soziologie', 'Politikwissenschaft', 'Jura', 'Volkswirtschaftslehre', 'Medienwissenschaft'] },
  deutsch: { icon: GraduationCap, color: 'var(--color-primary)', subjects: [] },
};
const COURSE_SLUGS = ['t', 'm', 'w', 'deutsch'];

const SEMESTERS = [
  { sem: 'Wintersemester 2025/26', start: 'Oktober 2025', status: 'running' },
  { sem: 'Sommersemester 2026', start: 'April 2026', status: 'open' },
  { sem: 'Wintersemester 2026/27', start: 'Oktober 2026', status: 'open' },
  { sem: 'Sommersemester 2027', start: 'April 2027', status: 'soon' },
];

const LANG_LEVELS = [
  { level: 'A1', hoursDE: '80–120 Std.', hoursEN: '80–120 hrs' },
  { level: 'A2', hoursDE: '80–120 Std.', hoursEN: '80–120 hrs' },
  { level: 'B1', hoursDE: '120–160 Std.', hoursEN: '120–160 hrs' },
  { level: 'B2', hoursDE: '120–160 Std.', hoursEN: '120–160 hrs' },
  { level: 'C1', hoursDE: '160–200 Std.', hoursEN: '160–200 hrs' },
];

/* ── Animate on scroll ── */
function useInView(threshold = 0.1) {
  const ref = useRef(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVis(true); obs.unobserve(el); } }, { threshold });
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);
  return [ref, vis];
}
const stagger = (vis, idx) => `transition-all duration-700 ${vis ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}`;
const staggerDelay = (idx) => ({ transitionDelay: `${idx * 80}ms` });

export default function CoursesPage() {
  const { t, i18n } = useTranslation();
  const isEN = i18n.language === 'en';
  const location = useLocation();
  const [expandedCourse, setExpandedCourse] = useState(null);
  const [heroRef, heroVis] = useInView(0.1);
  const [coursesRef, coursesVis] = useInView(0.1);
  const [langRef, langVis] = useInView(0.1);
  const [semRef, semVis] = useInView(0.1);
  const [ctaRef, ctaVis] = useInView(0.1);

  // Scroll-to-hash bei Anker-Navigation
  useEffect(() => {
    if (location.hash) {
      const id = location.hash.replace('#', '');
      const slug = id.replace('course-', '');
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); setExpandedCourse(slug); }
      }, 400);
    }
  }, [location.hash]);

  const toggleCourse = useCallback((slug) => {
    setExpandedCourse(prev => prev === slug ? null : slug);
  }, []);

  return (
    <div className="min-h-screen bg-white">
      <SEOHead titleKey="seo.courses_title" descKey="seo.courses_desc" path="/courses" />
      <PublicNav />
      <main className="pt-16">

        {/* ═══ HERO ═══ */}
        <section ref={heroRef} className="relative overflow-hidden py-[72px] lg:py-[96px]"
          style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' }}>
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12 relative z-10">
            <div className={`max-w-[640px] ${stagger(heroVis, 0)}`}>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-6 h-[2px]" style={{ background: 'var(--color-accent)' }} />
                <span className="text-[11px] font-semibold tracking-[0.2em] uppercase" style={{ color: 'var(--color-accent)' }}>
                  {t('courses_page.hero_badge', 'Studienkolleg-Kurse')}
                </span>
              </div>
              <h1 className="text-[36px] sm:text-[48px] lg:text-[56px] font-extrabold text-white leading-[1.08] tracking-[-0.03em] mb-6"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('courses_page.hero_title')}
              </h1>
              <p className="text-[15px] lg:text-[17px] text-white/40 leading-[1.7] max-w-[520px]">
                {t('courses_page.hero_sub')}
              </p>
            </div>
          </div>
        </section>

        {/* ═══ FSP HINWEIS ═══ */}
        <div className="max-w-[1280px] mx-auto px-6 lg:px-12 py-6">
          <div className="flex items-start gap-3 p-4 rounded-[4px]" style={{ background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.15)' }}>
            <CheckCircle size={16} style={{ color: 'var(--color-accent)' }} className="mt-0.5 shrink-0" />
            <p className="text-[13px] text-[var(--color-text-secondary)] leading-[1.7]">
              {t('courses_page.fsp_notice')}
            </p>
          </div>
        </div>

        {/* ═══ KURS-KARTEN ═══ */}
        <section ref={coursesRef} className="py-[48px] lg:py-[72px]">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className={`mb-12 lg:mb-16 max-w-[560px] ${stagger(coursesVis, 0)}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-6 h-[2px]" style={{ background: 'var(--color-accent)' }} />
                <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">
                  {t('courses_page.section_label', 'Schwerpunktkurse')}
                </span>
              </div>
              <h2 className="text-[32px] sm:text-[40px] lg:text-[48px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-4"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('courses_page.main_title')}
              </h2>
              <p className="text-[15px] text-[var(--color-text-secondary)] leading-[1.7]">
                {t('courses_page.main_desc')}
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              {COURSE_SLUGS.map((slug, idx) => {
                const course = COURSE_DATA[slug];
                const Icon = course.icon;
                const isExpanded = expandedCourse === slug;
                return (
                  <div key={slug} className={`group ${stagger(coursesVis, idx)}`} style={staggerDelay(idx)}
                    id={`course-${slug}`}
                    data-testid={`course-detail-${slug}`}>
                    <div className="p-5 sm:p-6 lg:p-8 rounded-[8px] border border-[var(--color-primary)]/8 transition-all duration-300 hover:border-[var(--color-primary)]/15 overflow-hidden"
                      style={{ boxShadow: '0 2px 12px rgba(17,54,85,0.04)' }}>
                      <div className="flex flex-wrap items-start justify-between gap-3 mb-5">
                        <div className="flex items-start gap-3 min-w-0">
                          <div className="w2g-icon-wrap shrink-0">
                            <Icon size={20} />
                          </div>
                          <div className="min-w-0">
                            <h3 className="text-[17px] sm:text-[18px] font-bold text-[var(--color-primary-dark)] mb-1" style={{ fontFamily: 'var(--font-heading)' }}>
                              {t(`courses_page.course_cards.${slug}.label`)}
                            </h3>
                            <p className="text-[12px] sm:text-[13px] text-[var(--color-text-secondary)] italic leading-[1.6]">
                              {t(`courses_page.course_cards.${slug}.for`)}
                            </p>
                          </div>
                        </div>
                        <span className="text-[11px] font-bold px-2.5 py-1 rounded-[2px] shrink-0"
                          style={{ background: 'rgba(212,175,55,0.1)', color: 'var(--color-accent)' }}>
                          {slug === 'deutsch' ? 'A1–C1' : t('courses_page.lang_req', 'B2 erforderlich')}
                        </span>
                      </div>

                      <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7] mb-5">
                        {t(`courses_page.course_cards.${slug}.desc`, slug === 't'
                          ? 'Der T-Kurs bereitet auf technische und ingenieurwissenschaftliche Studiengänge vor. Im Fokus stehen Mathematik, Physik und Deutsch auf akademischem Niveau.'
                          : slug === 'm'
                          ? 'Der M-Kurs ist die Vorbereitung auf medizinische, biologische und pharmazeutische Studiengänge. Biologie, Chemie und Mathematik bilden das Fundament.'
                          : slug === 'w'
                          ? 'Der W-Kurs bereitet auf wirtschafts- und sozialwissenschaftliche Studiengänge vor. BWL-Grundlagen, Mathematik und Deutsch stehen im Mittelpunkt.'
                          : 'Unsere Deutsch-Intensivkurse führen von der Anfängerstufe A1 bis zum Hochschulniveau C1. Kleine Gruppen, qualifizierte Dozenten und prüfungsorientiertes Training.'
                        )}
                      </p>

                      {course.subjects.length > 0 && (
                        <>
                          <button onClick={() => toggleCourse(slug)}
                            className="flex items-center gap-1.5 text-[13px] font-semibold mb-4 transition-colors"
                            style={{ color: 'var(--color-primary)' }}
                            data-testid={`course-expand-${slug}`}>
                            {isExpanded ? (isEN ? 'Hide subjects' : 'Fächer ausblenden') : (isEN ? 'Show subjects' : 'Fächer anzeigen')}
                            {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          </button>
                          {isExpanded && (
                            <div className="grid grid-cols-2 gap-2 mb-5">
                              {course.subjects.map(s => (
                                <div key={s} className="flex items-center gap-2 text-[13px] text-[var(--color-primary-dark)]">
                                  <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: 'var(--color-accent)' }} />
                                  {s}
                                </div>
                              ))}
                            </div>
                          )}
                        </>
                      )}

                      <div className="pt-4 border-t border-[var(--color-primary)]/6 flex items-center justify-between">
                        <p className="text-[12px] text-[var(--color-text-secondary)]">{t(`courses_page.course_cards.${slug}.fsp`)}</p>
                        <Link to="/apply" className="text-[13px] font-semibold flex items-center gap-1 transition-all hover:gap-2"
                          style={{ color: 'var(--color-primary)' }} data-testid={`course-apply-${slug}`}>
                          {t('nav.apply')} <ArrowRight size={13} />
                        </Link>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* ═══ SPRACHKURSE ═══ */}
        <section ref={langRef} className="py-[48px] lg:py-[72px] bg-[var(--color-surface-sunken)]">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
              <div className={`lg:col-span-5 ${stagger(langVis, 0)}`}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-6 h-[2px]" style={{ background: 'var(--color-accent)' }} />
                  <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">
                    {t('courses_page.lang_badge')}
                  </span>
                </div>
                <h2 className="text-[32px] sm:text-[40px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-5"
                  style={{ fontFamily: 'var(--font-heading)' }}>
                  {t('courses_page.lang_course_title')}
                </h2>
                <p className="text-[15px] text-[var(--color-text-secondary)] leading-[1.7] mb-8">
                  {t('courses_page.lang_course_desc')}
                </p>
                <Link to="/apply" data-testid="language-course-apply-btn"
                  className="inline-flex items-center gap-2.5 h-[48px] px-8 text-[14px] font-bold rounded-full transition-all hover:scale-[1.02] group"
                  style={{ background: 'var(--color-accent)', color: 'var(--color-primary-dark)' }}>
                  {t('courses_page.lang_course_btn')} <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
                </Link>
              </div>
              <div className={`lg:col-span-7 space-y-3 ${stagger(langVis, 1)}`} style={staggerDelay(1)}>
                {LANG_LEVELS.map((item, idx) => (
                  <div key={item.level} className="flex items-start sm:items-center gap-4 sm:gap-5 p-4 rounded-[4px] bg-white border border-[var(--color-primary)]/6"
                    style={{ boxShadow: '0 1px 4px rgba(17,54,85,0.03)' }} data-testid={`lang-level-${item.level}`}>
                    <span className="text-[18px] sm:text-[20px] font-extrabold w-[40px] sm:w-[48px] shrink-0" style={{ color: 'var(--color-accent)', fontFamily: 'var(--font-heading)' }}>
                      {item.level}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-[13px] sm:text-[14px] font-semibold text-[var(--color-primary-dark)]">{t(`courses_page.levels.${item.level}.label`)}</p>
                      <p className="text-[11px] sm:text-[12px] text-[var(--color-text-secondary)]">{t(`courses_page.levels.${item.level}.desc`)}</p>
                    </div>
                    <span className="text-[11px] sm:text-[12px] text-[var(--color-text-secondary)] shrink-0 hidden sm:block">{isEN ? item.hoursEN : item.hoursDE}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ═══ SEMESTER-ÜBERSICHT ═══ */}
        <section ref={semRef} className="py-[48px] lg:py-[72px]">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className={`text-center mb-12 ${stagger(semVis, 0)}`}>
              <h2 className="text-[32px] sm:text-[40px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-4"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('courses_page.starts_title')}
              </h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {SEMESTERS.map((s, idx) => (
                <div key={s.sem} className={`p-5 rounded-[4px] border transition-all ${
                  s.status === 'open' ? 'border-[var(--color-accent)]/30 bg-[rgba(212,175,55,0.03)]' : 'border-[var(--color-primary)]/6'
                } ${stagger(semVis, idx)}`} style={staggerDelay(idx)}
                  data-testid={`semester-${s.sem.replace(/\s+/g, '-').toLowerCase()}`}>
                  <div className="flex items-center justify-between mb-3">
                    <span className={`text-[10px] font-bold tracking-[0.1em] uppercase px-2 py-0.5 rounded-[2px] ${
                      s.status === 'running' ? 'bg-[#113655]/10 text-[var(--color-primary)]' :
                      s.status === 'open' ? 'text-[var(--color-primary-dark)]' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'
                    }`} style={s.status === 'open' ? { background: 'rgba(212,175,55,0.15)', color: 'var(--color-primary-dark)' } : {}}>
                      {t(`courses_page.${s.status === 'running' ? 'semester_running' : s.status === 'open' ? 'semester_open' : 'semester_soon'}`)}
                    </span>
                  </div>
                  <p className="text-[15px] font-bold text-[var(--color-primary-dark)] mb-1" style={{ fontFamily: 'var(--font-heading)' }}>{s.sem}</p>
                  <p className="text-[13px] text-[var(--color-text-secondary)]">{t('courses_page.semester_start')}: {s.start}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ═══ CTA ═══ */}
        <section ref={ctaRef} className="relative py-[72px] lg:py-[96px] overflow-hidden"
          style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' }}>
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />
          <div className="max-w-[640px] mx-auto px-6 lg:px-12 text-center relative z-10">
            <div className={stagger(ctaVis, 0)}>
              <h2 className="text-[32px] sm:text-[40px] font-extrabold text-white leading-[1.1] tracking-[-0.025em] mb-4"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('courses_page.cta_title')}
              </h2>
              <p className="text-[15px] text-white/40 leading-[1.7] mb-8">{t('courses_page.cta_desc')}</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/apply" data-testid="courses-cta-apply"
                  className="inline-flex items-center justify-center gap-2.5 h-[52px] px-10 text-[14px] font-bold rounded-full transition-all hover:scale-[1.02] group"
                  style={{ background: 'var(--color-accent)', color: 'var(--color-primary-dark)' }}>
                  {t('courses_page.cta_apply')} <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
                </Link>
                <Link to="/contact" data-testid="courses-cta-contact"
                  className="inline-flex items-center justify-center h-[52px] px-8 text-[14px] font-semibold text-white/70 border-2 border-white/15 rounded-full transition-all hover:border-white/30 hover:text-white">
                  {t('courses_page.cta_contact')}
                </Link>
              </div>
            </div>
          </div>
        </section>

      </main>
      <PublicFooter />
    </div>
  );
}
