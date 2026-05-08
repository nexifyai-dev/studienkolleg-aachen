import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import {
  ArrowRight, GraduationCap, BookOpen, Heart, Briefcase, Users,
  Clock, Star, ChevronDown, ChevronLeft, ChevronRight,
  Shield, Globe, Award, FileCheck, Play, X
} from 'lucide-react';

/* ── Assets ── */
const IMG = {
  heroWoman: '/images/hero/hero-woman.webp',
  processIllustration: '/images/illustrations/teaching.png',
  successIllustration: '/images/illustrations/transform.png',
  logoStudienkolleg: '/images/logos/studienkolleg-logo.png',
  logoW2G: '/images/logos/w2g-logo.png',
  logoStayInAachen: '/images/logos/stayinaachen-logo.png',
  lauraSaboor: '/images/team/laura-saboor.jpg',
  campusHandshake: '/images/campus/life/handshake-studienkolleg.jpg',
  campusMotivation: '/images/campus/life/motivationsschreiben-unterricht.jpg',
  campusKlasse: '/images/campus/life/klassenzimmer-szene.jpg',
  campusDocs: '/images/campus/life/praesentation-documents.jpg',
  campusHealth: '/images/campus/life/praesentation-healthcare.jpg',
};

const REELS = [
  { key: 'w-kurs', src: '/videos/w-kurs-vorstellung.mp4', poster: '/videos/posters/w-kurs.jpg' },
  { key: 'benefits', src: '/videos/benefits-studienkolleg.mp4', poster: '/videos/posters/benefits.jpg' },
  { key: 'pedro', src: '/videos/pedro-testimonial.mp4', poster: '/videos/posters/pedro.jpg' },
  { key: 'international', src: '/videos/international-students.mp4', poster: '/videos/posters/international.jpg' },
  { key: 'm-kurs', src: '/videos/m-kurs-vorstellung.mp4', poster: '/videos/posters/m-kurs.jpg' },
  { key: 'vokabeln', src: '/videos/deutsch-vokabeln.mp4', poster: '/videos/posters/vokabeln.jpg' },
  { key: 'tipps', src: '/videos/deutsch-tipps.mp4', poster: '/videos/posters/tipps.jpg' },
  { key: 'fsp', src: '/videos/fsp-erklaert.mp4', poster: '/videos/posters/fsp.jpg' },
  { key: 'wohnheim', src: '/videos/wohnheim-tour.mp4', poster: '/videos/posters/wohnheim.jpg' },
];

const MAIN_VIDEOS = [
  { key: 'imagevideo', src: '/videos/imagevideo-studienkolleg.mp4', poster: '/videos/posters/imagevideo.jpg' },
  { key: 'services', src: '/videos/services-studienkolleg.mp4', poster: '/videos/posters/services.jpg' },
];

/* ── Daten ── */
const SEGMENTS = [
  { key: 'studienkolleg', icon: GraduationCap, link: '/courses', accent: 'var(--color-primary)' },
  { key: 'sprachkurse', icon: BookOpen, link: '/courses', accent: 'var(--color-accent-teal)' },
  { key: 'pflege', icon: Heart, link: '/services', accent: 'var(--color-accent-pink)' },
  { key: 'arbeit', icon: Briefcase, link: '/services', accent: 'var(--color-accent)' },
  { key: 'partner', icon: Users, link: '/contact', accent: 'var(--color-primary)' },
];

const PROGRAM_KEYS = ['t', 'm', 'w', 'de'];

const STAT_VALUES = [2847, 94, 45, 12];

const TRUST_ICONS = [Shield, Globe, Award, FileCheck];

/* ── Hooks ── */
function useInView(threshold = 0.15) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVisible(true); obs.disconnect(); } }, { threshold });
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);
  return [ref, visible];
}

function AnimatedCounter({ end, suffix = '', duration = 2000 }) {
  const [count, setCount] = useState(0);
  const [ref, visible] = useInView(0.3);
  useEffect(() => {
    if (!visible) return;
    let start = 0;
    const step = end / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= end) { setCount(end); clearInterval(timer); }
      else setCount(Math.floor(start));
    }, 16);
    return () => clearInterval(timer);
  }, [visible, end, duration]);
  return <span ref={ref}>{count}{suffix}</span>;
}

/* ── Utility: Staggered entrance ── */
const stagger = (visible, idx, base = 'translate-y-6 opacity-0') =>
  visible
    ? `translate-y-0 opacity-100 transition-all duration-700 ease-out`
    : `${base} transition-all duration-700 ease-out`;

const staggerDelay = (idx) => ({ transitionDelay: `${idx * 120}ms` });

/* ────────────────────────────────────────────────────────────────
   HOMEPAGE
   ──────────────────────────────────────────────────────────────── */
export default function HomePage() {
  const { t } = useTranslation();
  const [heroRef, heroVis] = useInView(0.1);
  const [teamRef, teamVis] = useInView(0.1);
  const [campusRef, campusVis] = useInView(0.1);
  const [segRef, segVis] = useInView(0.1);
  const [reelsRef, reelsVis] = useInView(0.1);
  const [vidRef, vidVis] = useInView(0.1);
  const [progRef, progVis] = useInView(0.1);
  const [statRef, statVis] = useInView(0.1);
  const [procRef, procVis] = useInView(0.1);
  const [trustRef, trustVis] = useInView(0.1);
  const [testRef, testVis] = useInView(0.1);
  const [faqRef, faqVis] = useInView(0.1);
  const [ctaRef, ctaVis] = useInView(0.1);

  const [openFaq, setOpenFaq] = useState(null);
  const [testimonialIdx, setTestimonialIdx] = useState(0);
  const [activeReel, setActiveReel] = useState(null);
  const [lightboxReel, setLightboxReel] = useState(null);
  const [activeMainVideo, setActiveMainVideo] = useState(null);
  const reelsScrollRef = useRef(null);
  const reelVideosRef = useRef({});
  const reelsSectionElRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  /* ── Scroll-basierter Playback-Speed für Reels ── */
  useEffect(() => {
    let rafId;
    let loadStarted = false;
    let loadTimer = null;
    let loadIdx = 0;

    // Einzelnes Video laden (gestaffelt) - nur wenn im Scroll-Viewport
    const loadNextVideo = () => {
      const videos = Object.values(reelVideosRef.current).filter(Boolean);
      if (loadIdx >= videos.length) {
        clearInterval(loadTimer);
        loadTimer = null;
        return;
      }
      const vid = videos[loadIdx];
      loadIdx++;
      if (vid && vid.readyState < 1) {
        vid.preload = 'auto';
        vid.load();
      }
    };

    const tick = () => {
      const el = reelsSectionElRef.current;
      if (!el) { rafId = requestAnimationFrame(tick); return; }

      const rect = el.getBoundingClientRect();
      const vh = window.innerHeight;
      const top = Math.max(0, rect.top);
      const bottom = Math.min(vh, rect.bottom);
      const visibleH = Math.max(0, bottom - top);
      const ratio = rect.height > 0 ? visibleH / rect.height : 0;
      const videos = Object.values(reelVideosRef.current).filter(Boolean);

      if (ratio < 0.05) {
        // Nicht sichtbar → pausieren
        videos.forEach(vid => { if (!vid.paused) vid.pause(); });
      } else {
        // Gestaffelt laden: nur einmal starten
        if (!loadStarted) {
          loadStarted = true;
          loadTimer = setInterval(loadNextVideo, 600);
          loadNextVideo(); // Sofort das erste
        }

        const speed = Math.max(0.1, Math.min(1.0, (ratio - 0.05) / 0.55));

        videos.forEach(vid => {
          if (vid.readyState >= 2) {
            try { vid.playbackRate = speed; } catch (_) {}
            if (vid.paused) {
              vid.play().catch(() => {});
            }
          }
        });
      }

      rafId = requestAnimationFrame(tick);
    };

    rafId = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(rafId);
      if (loadTimer) clearInterval(loadTimer);
    };
  }, []);

  const updateScrollState = useCallback(() => {
    const el = reelsScrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 8);
    setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 8);
  }, []);

  const scrollReels = useCallback((dir) => {
    const el = reelsScrollRef.current;
    if (!el) return;
    const cardW = 260;
    el.scrollBy({ left: dir * cardW * 2, behavior: 'smooth' });
    setTimeout(updateScrollState, 400);
  }, [updateScrollState]);

  const handleReelPlay = useCallback((key) => {
    // Klick: Ton an/aus umschalten – Video läuft immer weiter
    setActiveReel(prev => {
      const newKey = prev === key ? null : key;
      Object.entries(reelVideosRef.current).forEach(([k, el]) => {
        if (!el) return;
        if (k === key && prev !== key) {
          el.muted = false;
        } else {
          el.muted = true;
        }
      });
      return newKey;
    });
  }, []);

  const handleMainVideoPlay = useCallback((key) => {
    setActiveMainVideo(prev => prev === key ? null : key);
  }, []);

  const nextTestimonial = useCallback(() => setTestimonialIdx(i => (i + 1) % 3), []);
  const prevTestimonial = useCallback(() => setTestimonialIdx(i => (i - 1 + 3) % 3), []);

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-surface-elevated)', fontFamily: 'var(--font-body)' }}>
      <PublicNav />
      <main>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 1: HERO – Echtes Markenfoto, Editorial Copy
           ═══════════════════════════════════════════════════════════ */}
        <section ref={heroRef} className="relative overflow-hidden" data-testid="hero-section"
          style={{ background: 'linear-gradient(160deg, var(--color-primary-dark) 0%, var(--color-primary) 40%, var(--color-primary-light) 80%, var(--color-accent-teal) 100%)' }}>
          <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle at 25% 25%, white 1px, transparent 1px)', backgroundSize: '32px 32px' }} />

          <div className="max-w-[1280px] mx-auto px-6 lg:px-12 relative z-10">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-6 items-center min-h-[90vh] lg:min-h-[720px]">

              {/* LEFT: Content – 7 Spalten */}
              <div className={`lg:col-span-7 pt-24 sm:pt-32 lg:pt-0 pb-8 lg:pb-0 ${stagger(heroVis, 0)}`}>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-8 h-[2px]" style={{ background: 'var(--color-accent)' }} />
                  <span className="text-[11px] font-semibold tracking-[0.2em] uppercase" style={{ color: 'var(--color-accent)' }}>
                    {t('hero.badge')}
                  </span>
                </div>

                <h1 className="text-[36px] sm:text-[48px] lg:text-[56px] font-extrabold text-white leading-[1.08] tracking-[-0.03em] mb-6"
                  style={{ fontFamily: 'var(--font-heading)' }} data-testid="hero-title">
                  {t('hero.headline_1')}<br />
                  <span style={{ color: 'var(--color-accent)' }}>{t('hero.headline_accent')}</span> {t('hero.headline_dash')}<br />
                  <span className="text-white/80">{t('hero.headline_2')}</span>
                </h1>

                <p className="text-[15px] lg:text-[17px] leading-[1.7] text-white/45 max-w-[520px] mb-10">
                  {t('hero.sub')}
                </p>

                <div className="flex flex-col sm:flex-row gap-4 mb-12">
                  <Link to="/apply" data-testid="hero-cta-primary"
                    className="inline-flex items-center justify-center gap-2.5 h-[56px] px-8 text-[15px] font-bold tracking-wide text-[var(--color-primary-dark)] rounded-full group transition-all duration-300 hover:scale-[1.02]"
                    style={{ background: 'var(--color-accent)', boxShadow: '0 4px 20px rgba(212,175,55,0.3)' }}>
                    {t('hero.cta_primary')} <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                  </Link>
                  <Link to="/booking" data-testid="hero-cta-secondary"
                    className="inline-flex items-center justify-center gap-2 h-[56px] px-8 text-[15px] font-semibold text-white/80 border-2 border-white/15 rounded-full transition-all duration-300 hover:border-white/30 hover:text-white">
                    {t('hero.cta_secondary')}
                  </Link>
                </div>

                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-1.5">
                    {[...Array(5)].map((_, i) => <Star key={i} size={13} className="fill-[var(--color-accent)] text-[var(--color-accent)]" />)}
                    <span className="text-[12px] text-white/40 ml-1.5">4.9 / 5</span>
                  </div>
                  <div className="w-[1px] h-4 bg-white/10" />
                  <span className="text-[12px] text-white/40">{t('hero.stat_graduates')}</span>
                  <div className="w-[1px] h-4 bg-white/10" />
                  <span className="text-[12px] text-white/40">{t('hero.stat_countries')}</span>
                </div>
              </div>

              {/* RIGHT: Markenfoto – 5 Spalten, vertikal ZENTRIERT (Drittel-Regel) */}
              <div className={`hidden lg:flex lg:col-span-5 items-center justify-center lg:justify-end ${stagger(heroVis, 1)}`}
                style={staggerDelay(1)}>
                <img src={IMG.heroWoman} alt="Studienberaterin – Persönliche Begleitung"
                  className="w-[520px] xl:w-[560px] h-auto object-contain max-h-[75vh]"
                  style={{ filter: 'drop-shadow(0 20px 60px rgba(0,0,0,0.25))' }}
                  data-testid="hero-illustration" />
              </div>
            </div>
          </div>
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 1b: LEADERSHIP – Laura Saboor, Managing Director
           ═══════════════════════════════════════════════════════════ */}
        <section ref={teamRef} className="py-[56px] md:py-[72px] lg:py-24" data-testid="team-section">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">

              {/* LEFT: Portrait – 4 Spalten */}
              <div className={`lg:col-span-4 flex justify-center lg:justify-start ${stagger(teamVis, 0)}`}>
                <div className="relative">
                  <div className="w-[240px] h-[240px] sm:w-[280px] sm:h-[280px] lg:w-[320px] lg:h-[320px] rounded-full overflow-hidden border-[3px] border-[var(--color-primary)]/10 relative z-10"
                    style={{ boxShadow: '0 16px 48px rgba(17,54,85,0.12), 0 4px 12px rgba(17,54,85,0.06)' }}>
                    <img src={IMG.lauraSaboor} alt="Laura Saboor – Managing Director"
                      className="w-full h-full object-cover object-top"
                      data-testid="team-laura-portrait" />
                  </div>
                  {/* Dekorativer Akzent-Ring */}
                  <div className="absolute -top-3 -right-3 w-[240px] h-[240px] sm:w-[280px] sm:h-[280px] lg:w-[320px] lg:h-[320px] rounded-full border-2 border-dashed opacity-20"
                    style={{ borderColor: 'var(--color-accent)' }} />
                </div>
              </div>

              {/* RIGHT: Editorial Text – 8 Spalten */}
              <div className={`lg:col-span-8 ${stagger(teamVis, 1)}`} style={staggerDelay(1)}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
                  <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">{t('home.team_label')}</span>
                </div>
                <h2 className="text-[28px] sm:text-[36px] lg:text-[44px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-3"
                  style={{ fontFamily: 'var(--font-heading)' }}>
                  {t('home.team_name')}
                </h2>
                <p className="text-[14px] font-bold tracking-[0.04em] uppercase mb-6"
                  style={{ color: 'var(--color-accent)' }}>
                  {t('home.team_role')}
                </p>
                <blockquote className="relative pl-6 mb-8 border-l-[3px]" style={{ borderColor: 'var(--color-accent)' }}>
                  <p className="text-[17px] lg:text-[19px] text-[var(--color-primary-dark)]/70 leading-[1.75] italic">
                    {t('home.team_quote')}
                  </p>
                </blockquote>
                <p className="text-[15px] text-[var(--color-text-secondary)] leading-[1.7] max-w-[560px] mb-8">
                  {t('home.team_bio')}
                </p>
                <Link to="/contact" data-testid="team-contact-cta"
                  className="inline-flex items-center gap-2.5 text-[14px] font-semibold text-[var(--color-primary)] hover:gap-3.5 transition-all duration-300 group">
                  {t('home.team_cta')} <ArrowRight size={15} className="group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>
          </div>
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 1c: CAMPUS LIFE – Authentische Einblicke
           ═══════════════════════════════════════════════════════════ */}
        <section ref={campusRef} className="py-[56px] md:py-[72px] lg:py-24 bg-[var(--color-surface-sunken)]" data-testid="campus-life-section">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className={`mb-12 lg:mb-16 max-w-[600px] ${stagger(campusVis, 0)}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
                <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">{t('home.campus_label')}</span>
              </div>
              <h2 className="text-[32px] sm:text-[40px] lg:text-[48px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-4"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('home.campus_title')}
              </h2>
              <p className="text-[15px] text-[var(--color-text-secondary)] leading-[1.7]">
                {t('home.campus_desc')}
              </p>
            </div>

            {/* Bento-Grid: 3er-Reihe oben, 2er-Reihe unten – bündig */}
            <div className="grid grid-cols-2 lg:grid-cols-12 gap-3 lg:gap-4">

              {/* ── REIHE 1: Drei Bilder, gleiche Höhe (4+5+3 = 12 Spalten) ── */}
              <div className={`col-span-1 lg:col-span-4 ${stagger(campusVis, 0)}`} style={staggerDelay(0)}>
                <div className="relative overflow-hidden rounded-[4px] group h-[240px] lg:h-[280px]">
                  <img src={IMG.campusKlasse} alt="Unterricht am Studienkolleg – Klassenzimmer"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.03]"
                    data-testid="campus-img-klasse" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-primary-dark)]/60 via-transparent to-transparent" />
                  <div className="absolute bottom-0 left-0 p-4 lg:p-5">
                    <p className="text-[13px] font-semibold text-white/90">{t('home.campus_img_klasse')}</p>
                  </div>
                </div>
              </div>

              <div className={`col-span-1 lg:col-span-5 ${stagger(campusVis, 1)}`} style={staggerDelay(1)}>
                <div className="relative overflow-hidden rounded-[4px] group h-[240px] lg:h-[280px]">
                  <img src={IMG.campusDocs} alt="Workshop: Wichtige Dokumente für dein Studium"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.03]"
                    data-testid="campus-img-docs" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-primary-dark)]/60 via-transparent to-transparent" />
                  <div className="absolute bottom-0 left-0 p-4 lg:p-5">
                    <p className="text-[13px] font-semibold text-white/90">{t('home.campus_img_docs')}</p>
                  </div>
                </div>
              </div>

              <div className={`col-span-2 lg:col-span-3 ${stagger(campusVis, 2)}`} style={staggerDelay(2)}>
                <div className="relative overflow-hidden rounded-[4px] group h-[240px] lg:h-[280px]">
                  <img src={IMG.campusHealth} alt="Vortrag: Das deutsche Gesundheitssystem"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.03]"
                    data-testid="campus-img-health" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-primary-dark)]/60 via-transparent to-transparent" />
                  <div className="absolute bottom-0 left-0 p-4 lg:p-5">
                    <p className="text-[13px] font-semibold text-white/90">{t('home.campus_img_health')}</p>
                  </div>
                </div>
              </div>

              {/* ── REIHE 2: Zwei große Bilder, gleiche Höhe (7+5 = 12 Spalten) ── */}
              <div className={`col-span-1 lg:col-span-7 ${stagger(campusVis, 3)}`} style={staggerDelay(3)}>
                <div className="relative overflow-hidden rounded-[4px] group h-[240px] lg:h-[340px]">
                  <img src={IMG.campusHandshake} alt="Partnerschaft vor dem Studienkolleg Aachen"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.03]"
                    data-testid="campus-img-handshake" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-primary-dark)]/60 via-transparent to-transparent" />
                  <div className="absolute bottom-0 left-0 p-5 lg:p-6">
                    <span className="inline-block text-[10px] font-bold tracking-[0.15em] uppercase px-3 py-1.5 rounded-[2px] mb-2"
                      style={{ background: 'rgba(212,175,55,0.9)', color: 'var(--color-primary-dark)' }}>{t('home.campus_img_handshake_badge')}</span>
                    <p className="text-[14px] font-semibold text-white/90">{t('home.campus_img_handshake_text')}</p>
                  </div>
                </div>
              </div>

              <div className={`col-span-1 lg:col-span-5 ${stagger(campusVis, 4)}`} style={staggerDelay(4)}>
                <div className="relative overflow-hidden rounded-[4px] group h-[240px] lg:h-[340px]">
                  <img src={IMG.campusMotivation} alt="Motivationsschreiben-Unterricht"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.03]"
                    data-testid="campus-img-motivation" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-primary-dark)]/60 via-transparent to-transparent" />
                  <div className="absolute bottom-0 left-0 p-4 lg:p-5">
                    <p className="text-[13px] font-semibold text-white/90">{t('home.campus_img_motivation')}</p>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 1d: VIDEO REELS – Karussell mit Navigation
           ═══════════════════════════════════════════════════════════ */}
        <section ref={(el) => { if (reelsRef) reelsRef.current = el; reelsSectionElRef.current = el; }} className="py-[56px] md:py-[72px] lg:py-24 relative overflow-hidden"
          style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' }}
          data-testid="reels-section">
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12 relative z-10">
            <div className={`mb-10 lg:mb-14 flex items-end justify-between gap-6 ${stagger(reelsVis, 0)}`}>
              <div className="max-w-[600px]">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
                  <span className="text-[11px] font-semibold tracking-[0.2em] uppercase" style={{ color: 'var(--color-accent)' }}>{t('home.reels_label')}</span>
                </div>
                <h2 className="text-[32px] sm:text-[40px] lg:text-[48px] font-extrabold text-white leading-[1.1] tracking-[-0.025em] mb-4"
                  style={{ fontFamily: 'var(--font-heading)' }}>
                  {t('home.reels_title')}
                </h2>
                <p className="text-[15px] text-white/40 leading-[1.7]">
                  {t('home.reels_desc')}
                </p>
              </div>
              {/* Carousel Navigation Arrows */}
              <div className="hidden md:flex items-center gap-2 shrink-0 pb-1">
                <button onClick={() => scrollReels(-1)} disabled={!canScrollLeft}
                  className="w-10 h-10 rounded-full border border-white/15 flex items-center justify-center text-white/50 transition-all duration-300 hover:border-white/40 hover:text-white disabled:opacity-20 disabled:cursor-not-allowed"
                  data-testid="reels-prev" aria-label="Vorheriges Video">
                  <ChevronLeft size={16} />
                </button>
                <button onClick={() => scrollReels(1)} disabled={!canScrollRight}
                  className="w-10 h-10 rounded-full border border-white/15 flex items-center justify-center text-white/50 transition-all duration-300 hover:border-white/40 hover:text-white disabled:opacity-20 disabled:cursor-not-allowed"
                  data-testid="reels-next" aria-label="Naechstes Video">
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>

            {/* Manueller Scroll-Container */}
            <div className="relative">
              <div ref={reelsScrollRef}
                onScroll={updateScrollState}
                className="flex gap-4 lg:gap-5 overflow-x-auto pb-4 -mx-6 px-6 lg:-mx-12 lg:px-12 snap-x snap-mandatory scrollbar-hide"
                style={{ scrollBehavior: 'smooth' }}>
                {REELS.map((reel, idx) => (
                  <div key={reel.key}
                    className={`shrink-0 snap-start ${stagger(reelsVis, idx)}`}
                    style={{ ...staggerDelay(idx), width: '240px' }}
                    data-testid={`reel-${reel.key}`}>
                    <div className="relative rounded-[8px] overflow-hidden border border-white/10 group cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:border-white/25"
                      style={{ height: '426px', boxShadow: '0 4px 20px rgba(0,0,0,0.2)' }}
                      onClick={() => handleReelPlay(reel.key)}>
                      <video
                        data-reel-key={reel.key}
                        src={reel.src}
                        poster={reel.poster}
                        className="absolute inset-0 w-full h-full object-cover"
                        muted
                        loop
                        playsInline
                        preload="none"
                        ref={el => { if (el) reelVideosRef.current[reel.key] = el; }}
                      />
                      <div className="absolute inset-0 pointer-events-none"
                        style={{ background: 'linear-gradient(to top, rgba(10,32,54,0.85) 0%, rgba(10,32,54,0.15) 40%, transparent 60%)' }} />
                      {/* Ton-Indikator */}
                      <div className="absolute top-3 right-3 z-20">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center backdrop-blur-sm transition-all duration-300 ${
                          activeReel === reel.key
                            ? 'bg-[rgba(212,175,55,0.95)] scale-100'
                            : 'bg-white/15 scale-90 opacity-0 group-hover:opacity-100 group-hover:scale-100'
                        }`}>
                          {activeReel === reel.key ? (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
                          ) : (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>
                          )}
                        </div>
                      </div>
                      {/* Fullscreen-Button */}
                      <div className="absolute top-3 left-3 z-20">
                        <button
                          onClick={(e) => { e.stopPropagation(); setLightboxReel(reel); }}
                          className="w-8 h-8 rounded-full bg-white/15 flex items-center justify-center backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-all duration-300 hover:bg-white/30"
                          aria-label="Vollbild oeffnen"
                          data-testid={`reel-fullscreen-${reel.key}`}>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
                        </button>
                      </div>
                      {/* Badge + Info */}
                      <div className="absolute bottom-0 left-0 right-0 p-4">
                        <span className="inline-block text-[9px] font-bold tracking-[0.15em] uppercase px-2.5 py-1 rounded-[2px] mb-2"
                          style={{ background: 'rgba(212,175,55,0.95)', color: 'var(--color-primary-dark)' }}>
                          {t(`home.reels.${reel.key}.badge`)}
                        </span>
                        <p className="text-[14px] font-bold text-white leading-tight mb-0.5"
                          style={{ fontFamily: 'var(--font-heading)' }}>{t(`home.reels.${reel.key}.title`)}</p>
                        <p className="text-[11px] text-white/60">{t(`home.reels.${reel.key}.desc`)}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Mobile Scroll Indicator */}
            <div className="flex md:hidden items-center justify-center gap-1.5 mt-4">
              {REELS.map((reel, i) => (
                <div key={reel.key} className="w-1.5 h-1.5 rounded-full transition-all duration-300"
                  style={{ background: i < 3 ? 'rgba(212,175,55,0.8)' : 'rgba(255,255,255,0.2)' }} />
              ))}
            </div>
          </div>

          {/* Reel Lightbox Modal */}
          {lightboxReel && (
            <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
              onClick={() => setLightboxReel(null)} data-testid="reel-lightbox">
              <div className="relative max-w-[400px] w-full" style={{ maxHeight: '85vh' }} onClick={e => e.stopPropagation()}>
                <button onClick={() => setLightboxReel(null)}
                  className="absolute -top-10 right-0 w-8 h-8 rounded-full bg-white/15 flex items-center justify-center text-white hover:bg-white/30 transition-colors z-10"
                  data-testid="reel-lightbox-close" aria-label="Schliessen">
                  <X size={18} />
                </button>
                <div className="rounded-xl overflow-hidden bg-black" style={{ aspectRatio: '9/16' }}>
                  <video
                    src={lightboxReel.src}
                    poster={lightboxReel.poster}
                    className="w-full h-full object-cover"
                    controls
                    autoPlay
                    playsInline
                    data-testid="reel-lightbox-video"
                  />
                </div>
                <div className="mt-3 text-center">
                  <p className="text-white font-bold text-sm" style={{ fontFamily: 'var(--font-heading)' }}>
                    {t(`home.reels.${lightboxReel.key}.title`)}
                  </p>
                  <p className="text-white/50 text-xs mt-0.5">
                    {t(`home.reels.${lightboxReel.key}.desc`)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 2: SEGMENTE – Bento-Grid, kein uniformes Raster
           ═══════════════════════════════════════════════════════════ */}
        <section ref={segRef} className="py-[56px] md:py-[72px] lg:py-24" data-testid="segments-section">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            {/* Section Header – links ausgerichtet */}
            <div className={`mb-12 lg:mb-16 max-w-[600px] ${stagger(segVis, 0)}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
                <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">{t('home.segments_label')}</span>
              </div>
              <h2 className="text-[32px] sm:text-[40px] lg:text-[48px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-4"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('home.segments_title')}
              </h2>
              <p className="text-[15px] text-[var(--color-text-secondary)] leading-[1.7]">
                {t('home.segments_desc')}
              </p>
            </div>

            {/* Bento Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-5">
              {SEGMENTS.map((seg, idx) => (
                <Link key={seg.key} to={seg.link}
                  className={`group relative p-6 lg:p-8 rounded-[4px] border transition-all duration-500 hover:-translate-y-1 ${
                    idx === 0 ? 'sm:col-span-2 lg:col-span-2 bg-[var(--color-primary-dark)] border-transparent text-white' : 'bg-white border-[var(--color-primary)]/8 hover:border-[var(--color-primary)]/20'
                  } ${stagger(segVis, idx)}`}
                  style={staggerDelay(idx)}
                  data-testid={`segment-${seg.key}`}>

                  <div className="flex items-start gap-5">
                    <div className={`w2g-icon-wrap shrink-0 ${
                      idx === 0 ? '!bg-[rgba(212,175,55,0.15)]' : ''
                    }`}>
                      <seg.icon size={20} style={{ color: 'var(--color-accent)' }} />
                    </div>
                    <div className="flex-1">
                      <h3 className={`text-[17px] font-bold mb-1.5 tracking-tight ${
                        idx === 0 ? 'text-white' : 'text-[var(--color-primary-dark)]'
                      }`} style={{ fontFamily: 'var(--font-heading)' }}>
                        {t(`home.segments.${seg.key}.label`)}
                      </h3>
                      <p className={`text-[13px] leading-[1.7] ${
                        idx === 0 ? 'text-white/45' : 'text-[var(--color-text-secondary)]'
                      }`}>{t(`home.segments.${seg.key}.desc`)}</p>
                    </div>
                    <ArrowRight size={16} className={`shrink-0 mt-1 transition-transform duration-300 group-hover:translate-x-1 ${
                      idx === 0 ? 'text-white/30' : 'text-[var(--color-primary)]/20'
                    }`} />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 2b: VIDEO-SHOWCASE – Eigene MP4-Videos mit Poster
           ═══════════════════════════════════════════════════════════ */}
        <section ref={vidRef} className="relative py-[56px] md:py-[72px] lg:py-24 overflow-hidden"
          style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' }}
          data-testid="video-section">
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12 relative z-10">
            <div className={`text-center mb-12 lg:mb-16 ${stagger(vidVis, 0)}`}>
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
                <span className="text-[11px] font-semibold tracking-[0.2em] uppercase" style={{ color: 'var(--color-accent)' }}>{t('home.video_label')}</span>
                <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
              </div>
              <h2 className="text-[32px] sm:text-[40px] lg:text-[48px] font-extrabold text-white leading-[1.1] tracking-[-0.025em] mb-4"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('home.video_title')}
              </h2>
              <p className="text-[15px] text-white/40 max-w-[520px] mx-auto leading-[1.7]">
                {t('home.video_desc_header')}
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
              {MAIN_VIDEOS.map((vid, idx) => (
                <div key={vid.key} className={`group ${stagger(vidVis, idx)}`} style={staggerDelay(idx)}>
                  <div className="relative rounded-[6px] overflow-hidden border border-white/10 cursor-pointer"
                    style={{ boxShadow: '0 16px 48px rgba(0,0,0,0.3), 0 4px 12px rgba(0,0,0,0.2)' }}
                    onClick={() => handleMainVideoPlay(vid.key)}
                    data-testid={`video-${vid.key}`}>
                    <div className="relative" style={{ aspectRatio: '16/9' }}>
                      <video
                        src={vid.src}
                        poster={vid.poster}
                        className="absolute inset-0 w-full h-full object-cover"
                        playsInline
                        preload="metadata"
                        ref={el => {
                          if (el) {
                            if (activeMainVideo === vid.key) {
                              el.controls = true;
                              el.muted = false;
                              el.play().catch(() => {});
                            } else {
                              el.controls = false;
                              el.pause();
                              el.muted = true;
                            }
                          }
                        }}
                      />
                      {/* Play-Overlay – nur sichtbar wenn Video nicht aktiv */}
                      {activeMainVideo !== vid.key && (
                        <div className="absolute inset-0 flex items-center justify-center bg-[var(--color-primary-dark)]/20 transition-colors duration-300 group-hover:bg-[var(--color-primary-dark)]/10">
                          <div className="w-16 h-16 rounded-full flex items-center justify-center transition-transform duration-300 group-hover:scale-110"
                            style={{ background: 'rgba(212,175,55,0.95)', boxShadow: '0 4px 24px rgba(212,175,55,0.4)' }}>
                            <Play size={24} className="text-[var(--color-primary-dark)] ml-1" fill="#0a2036" />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  <p className="mt-4 text-[13px] font-semibold text-white/60 tracking-wide" style={{ fontFamily: 'var(--font-heading)' }}>
                    {t(`home.video_titles.${vid.key}`)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>



        {/* ═══════════════════════════════════════════════════════════
            SECTION 3: PROGRAMME – Editorial Grid mit Hierarchie
           ═══════════════════════════════════════════════════════════ */}
        <section ref={progRef} className="py-[56px] md:py-[72px] lg:py-24 bg-[var(--color-surface-sunken)]" data-testid="programs-section">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className={`mb-12 lg:mb-16 max-w-[600px] ${stagger(progVis, 0)}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
                <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">{t('home.programs_label')}</span>
              </div>
              <h2 className="text-[32px] sm:text-[40px] lg:text-[48px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-4"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('home.programs_title')}
              </h2>
              <p className="text-[15px] text-[var(--color-text-secondary)] leading-[1.7]">
                {t('home.programs_desc')}
              </p>
            </div>

            {/* Asymmetrisches Grid: 1 Feature + 3 Standard */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-5">
              {/* Featured Card */}
              <div className={`lg:col-span-5 group ${stagger(progVis, 0)}`} style={staggerDelay(0)}>
                <div className="bg-[var(--color-primary-dark)] rounded-[4px] p-8 lg:p-10 h-full flex flex-col justify-between min-h-[380px] relative overflow-hidden"
                  data-testid="program-t">
                  <div className="absolute top-0 right-0 w-[200px] h-[200px] opacity-[0.04]"
                    style={{ background: 'radial-gradient(circle, white 0%, transparent 70%)' }} />
                  <div>
                    <span className="inline-block text-[10px] font-bold tracking-[0.15em] uppercase px-3 py-1.5 rounded-[2px] mb-6"
                      style={{ background: 'rgba(212,175,55,0.15)', color: 'var(--color-accent)' }}>
                      {t('home.programs.t.badge')}
                    </span>
                    <h3 className="text-[24px] lg:text-[28px] font-extrabold text-white leading-[1.15] tracking-tight mb-4"
                      style={{ fontFamily: 'var(--font-heading)' }}>
                      {t('home.programs.t.title')}
                    </h3>
                    <p className="text-[14px] text-white/40 leading-[1.7] max-w-[360px]">
                      {t('home.programs.t.desc')}
                    </p>
                  </div>
                  <div className="flex items-center justify-between mt-8">
                    <div className="flex items-center gap-4 text-[11px] text-white/35">
                      <span className="flex items-center gap-1.5"><Clock size={12} /> {t('home.programs.t.duration')}</span>
                      <span className="flex items-center gap-1.5"><GraduationCap size={12} /> {t('home.programs.t.start')}</span>
                    </div>
                    <Link to="/courses" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-white/40 group-hover:border-white/30 group-hover:text-white transition-all">
                      <ArrowRight size={14} />
                    </Link>
                  </div>
                </div>
              </div>

              {/* Rechte 3 Karten */}
              <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4 lg:gap-5">
                {PROGRAM_KEYS.slice(1).map((pKey, idx) => (
                  <div key={pKey}
                    className={`group bg-white rounded-[4px] border border-[var(--color-primary)]/8 p-6 lg:p-8 hover:border-[var(--color-primary)]/20 transition-all duration-500 hover:-translate-y-0.5 ${stagger(progVis, idx + 1)}`}
                    style={staggerDelay(idx + 1)}
                    data-testid={`program-${pKey}`}>
                    <div className="flex items-start justify-between gap-6">
                      <div className="flex-1">
                        <span className="inline-block text-[10px] font-bold tracking-[0.15em] uppercase px-2.5 py-1 rounded-[2px] mb-3"
                          style={{ background: '#F0F4F8', color: 'var(--color-primary)' }}>
                          {t(`home.programs.${pKey}.badge`)}
                        </span>
                        <h3 className="text-[17px] font-bold text-[var(--color-primary-dark)] mb-1.5 tracking-tight" style={{ fontFamily: 'var(--font-heading)' }}>{t(`home.programs.${pKey}.title`)}</h3>
                        <p className="text-[13px] text-[var(--color-text-secondary)] leading-[1.7]">{t(`home.programs.${pKey}.desc`)}</p>
                      </div>
                      <div className="flex items-center gap-3 shrink-0 text-[11px] text-[var(--color-text-secondary)]/60">
                        <span className="flex items-center gap-1"><Clock size={11} /> {t(`home.programs.${pKey}.duration`)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`mt-10 ${stagger(progVis, 5)}`} style={staggerDelay(5)}>
              <Link to="/courses" className="inline-flex items-center gap-2.5 text-[14px] font-semibold text-[var(--color-primary)] hover:gap-3.5 transition-all duration-300 group">
                {t('home.all_programs_link')} <ArrowRight size={15} className="group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 4: STATISTIK – High-Contrast Inversion
           ═══════════════════════════════════════════════════════════ */}
        <section ref={statRef} className="relative py-[56px] md:py-[72px] lg:py-24 overflow-hidden" data-testid="stats-section"
          style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' }}>
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12 relative z-10">
            <div className={`text-center mb-12 lg:mb-16 ${stagger(statVis, 0)}`}>
              <h2 className="text-[32px] sm:text-[40px] lg:text-[48px] font-extrabold text-white leading-[1.1] tracking-[-0.025em] mb-4"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('home.stats_title')}
              </h2>
              <p className="text-[15px] text-white/40 max-w-[480px] mx-auto leading-[1.7]">
                {t('home.stats_desc')}
              </p>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
              {STAT_VALUES.map((val, i) => (
                <div key={i} className={`text-center ${stagger(statVis, i)}`} style={staggerDelay(i)}>
                  <div className="text-[40px] sm:text-[48px] lg:text-[56px] font-extrabold leading-none mb-3 tracking-tight"
                    style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-accent)' }}>
                    <AnimatedCounter end={val} suffix={t(`home.stats_items.${i}.suffix`)} />
                  </div>
                  <p className="text-[13px] text-white/40 tracking-wide">{t(`home.stats_items.${i}.label`)}</p>
                </div>
              ))}
            </div>
          </div>
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 5: PROZESS – Asymmetrisch 7/5 Grid
           ═══════════════════════════════════════════════════════════ */}
        <section ref={procRef} className="py-[56px] md:py-[72px] lg:py-24" data-testid="process-section">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">

              {/* LEFT: Steps – 7 Spalten */}
              <div className={`lg:col-span-7 ${stagger(procVis, 0)}`}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
                  <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">{t('home.process_title')}</span>
                </div>
                <h2 className="text-[32px] sm:text-[40px] lg:text-[48px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-10"
                  style={{ fontFamily: 'var(--font-heading)' }}>
                  {t('home.process_desc')}
                </h2>

                <div className="space-y-0">
                  {['01','02','03','04'].map((num, idx) => (
                    <div key={num}
                      className={`flex items-start gap-5 py-7 border-b border-[var(--color-primary)]/8 last:border-b-0 ${stagger(procVis, idx)}`}
                      style={staggerDelay(idx)}>
                      <span className="text-[28px] lg:text-[32px] font-extrabold tracking-tight shrink-0 w-[48px] leading-none pt-0.5"
                        style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-accent)' }}>
                        {num}
                      </span>
                      <div>
                        <h3 className="text-[16px] font-bold text-[var(--color-primary-dark)] mb-1.5 tracking-tight leading-tight" style={{ fontFamily: 'var(--font-heading)' }}>
                          {t(`home.steps.${idx}.title`)}
                        </h3>
                        <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7]">{t(`home.steps.${idx}.desc`)}</p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-10 flex gap-4">
                  <Link to="/apply" className="inline-flex items-center justify-center gap-2.5 h-[56px] px-8 text-[15px] font-bold tracking-wide text-white rounded-full group transition-all duration-300 hover:scale-[1.02]"
                    style={{ background: 'var(--color-primary)', boxShadow: '0 4px 20px rgba(17,54,85,0.2)' }}
                    data-testid="process-cta">
                    Bewerbung starten <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                  </Link>
                  <Link to="/booking" className="inline-flex items-center justify-center gap-2 h-[56px] px-8 text-[15px] font-semibold text-[var(--color-primary)] border-2 border-[var(--color-primary)]/15 rounded-full transition-all duration-300 hover:border-[var(--color-primary)]/30">
                    Beratung buchen
                  </Link>
                </div>
              </div>

              {/* RIGHT: 3D Illustration – 5 Spalten, Monitor nach links gespiegelt */}
              <div className={`lg:col-span-5 flex justify-center ${stagger(procVis, 5)}`} style={staggerDelay(5)}>
                <img src={IMG.processIllustration} alt="Student am Arbeitsplatz"
                  className="w-[300px] sm:w-[360px] lg:w-[420px] h-auto"
                  style={{ filter: 'drop-shadow(0 32px 64px rgba(17,54,85,0.08))', transform: 'scaleX(-1)' }}
                  data-testid="process-illustration" />
              </div>
            </div>
          </div>
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 6: TRUST – Clean Grid
           ═══════════════════════════════════════════════════════════ */}
        <section ref={trustRef} className="py-[56px] md:py-[72px] lg:py-24 bg-[var(--color-surface-sunken)]" data-testid="trust-section">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className={`mb-12 lg:mb-16 max-w-[600px] ${stagger(trustVis, 0)}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
                <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">{t('home.trust_label')}</span>
              </div>
              <h2 className="text-[32px] sm:text-[40px] lg:text-[48px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em]"
                style={{ fontFamily: 'var(--font-heading)' }}>
                {t('home.trust_title')}
              </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-5">
              {TRUST_ICONS.map((TIcon, i) => (
                <div key={i}
                  className={`bg-white rounded-[4px] border border-[var(--color-primary)]/8 p-6 lg:p-8 transition-all duration-500 hover:-translate-y-1 ${stagger(trustVis, i)}`}
                  style={staggerDelay(i)}>
                  <div className="w2g-icon-wrap mb-5">
                    <TIcon size={20} style={{ color: 'var(--color-accent)' }} />
                  </div>
                  <h3 className="text-[15px] font-bold text-[var(--color-primary-dark)] mb-2 tracking-tight" style={{ fontFamily: 'var(--font-heading)' }}>
                    {t(`home.trust_items.${i}.title`)}
                  </h3>
                  <p className="text-[13px] text-[var(--color-text-secondary)] leading-[1.7]">{t(`home.trust_items.${i}.desc`)}</p>
                </div>
              ))}
            </div>

            {/* Partner-Logos */}
            <div className={`mt-12 lg:mt-16 pt-10 border-t border-[var(--color-primary)]/8 ${stagger(trustVis, 5)}`} style={staggerDelay(5)}>
              <p className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-text-secondary)]/40 mb-6">{t('home.trusted_by')}</p>
              <div className="flex items-center gap-8 lg:gap-12 flex-wrap">
                <img src="/images/logos/studienkolleg-logo.png" alt="Studienkolleg Aachen" className="h-8 lg:h-10 w-auto object-contain opacity-60 hover:opacity-100 transition-opacity" data-testid="partner-logo-stk" />
                <img src="/images/logos/w2g-logo.png" alt="Way2Germany" className="h-8 lg:h-10 w-auto object-contain opacity-60 hover:opacity-100 transition-opacity" data-testid="partner-logo-w2g" />
                <img src="/images/logos/stayinaachen-logo.png" alt="Stay in Aachen" className="h-8 lg:h-10 w-auto object-contain opacity-60 hover:opacity-100 transition-opacity" data-testid="partner-logo-sia" />
              </div>
            </div>
          </div>
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 7: TESTIMONIALS – Editorial Zitat
           ═══════════════════════════════════════════════════════════ */}
        <section ref={testRef} className="py-[56px] md:py-[72px] lg:py-24" data-testid="testimonials-section">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
              {/* Left – Label */}
              <div className={`lg:col-span-4 ${stagger(testVis, 0)}`}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
                  <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">{t('home.testimonials_label')}</span>
                </div>
                <h2 className="text-[32px] sm:text-[40px] lg:text-[44px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-4"
                  style={{ fontFamily: 'var(--font-heading)' }}>
                  {t('trust.title', 'Was unsere Studierenden sagen')}
                </h2>
                <div className="flex items-center gap-3 mt-6">
                  <button onClick={prevTestimonial} className="w-10 h-10 rounded-full border border-[var(--color-primary)]/10 flex items-center justify-center text-[var(--color-primary)]/40 hover:border-[var(--color-primary)]/30 hover:text-[var(--color-primary)] transition-all" data-testid="testimonial-prev">
                    <ChevronLeft size={16} />
                  </button>
                  <button onClick={nextTestimonial} className="w-10 h-10 rounded-full border border-[var(--color-primary)]/10 flex items-center justify-center text-[var(--color-primary)]/40 hover:border-[var(--color-primary)]/30 hover:text-[var(--color-primary)] transition-all" data-testid="testimonial-next">
                    <ChevronRight size={16} />
                  </button>
                  <span className="text-[12px] text-[var(--color-text-secondary)]/50 ml-2">{testimonialIdx + 1} / 3</span>
                </div>
              </div>

              {/* Right – Quote Card */}
              <div className={`lg:col-span-8 ${stagger(testVis, 1)}`} style={staggerDelay(1)}>
                <div className="relative bg-[var(--color-primary-dark)] rounded-[4px] p-8 sm:p-10 lg:p-12">
                  <div className="absolute top-6 left-8 text-[80px] leading-none font-serif"
                    style={{ color: 'rgba(212,175,55,0.15)' }}>"</div>
                  <blockquote className="relative z-10">
                    <p className="text-[18px] lg:text-[20px] text-white/80 leading-[1.7] mb-8 max-w-[560px]">
                      {t(`home.testimonials.${testimonialIdx}.text`)}
                    </p>
                    <footer className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full flex items-center justify-center text-[14px] font-bold"
                        style={{ background: 'rgba(212,175,55,0.15)', color: 'var(--color-accent)' }}>
                        {t(`home.testimonials.${testimonialIdx}.name`).charAt(0)}
                      </div>
                      <div>
                        <cite className="text-[14px] font-semibold text-white not-italic block">{t(`home.testimonials.${testimonialIdx}.name`)}</cite>
                        <span className="text-[12px] text-white/35">{t(`home.testimonials.${testimonialIdx}.country`)} · {t(`home.testimonials.${testimonialIdx}.course`)}</span>
                      </div>
                    </footer>
                  </blockquote>
                </div>
              </div>
            </div>
          </div>
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 8: FAQ – Minimal Accordion
           ═══════════════════════════════════════════════════════════ */}
        <section ref={faqRef} className="py-[56px] md:py-[72px] lg:py-24 bg-[var(--color-surface-sunken)]" data-testid="faq-section">
          <div className="max-w-[1280px] mx-auto px-6 lg:px-12">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
              <div className={`lg:col-span-4 ${stagger(faqVis, 0)}`}>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-6 h-[2px] bg-[var(--color-accent)]" />
                  <span className="text-[11px] font-semibold tracking-[0.2em] uppercase text-[var(--color-primary)]/60">FAQ</span>
                </div>
                <h2 className="text-[32px] sm:text-[40px] lg:text-[44px] font-extrabold text-[var(--color-primary-dark)] leading-[1.1] tracking-[-0.025em] mb-4"
                  style={{ fontFamily: 'var(--font-heading)' }}>
                  {t('faq.title')}
                </h2>
                <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7]">
                  {t('faq.still_questions')} <Link to="/contact" className="font-semibold text-[var(--color-primary)] hover:underline" data-testid="faq-contact-link">{t('faq.contact_link')}</Link>
                </p>
              </div>

              <div className="lg:col-span-8">
                <div className="divide-y divide-[var(--color-primary)]/8">
                  {[0,1,2,3,4].map((i) => (
                    <div key={i} className={stagger(faqVis, i)} style={staggerDelay(i)}>
                      <button
                        onClick={() => setOpenFaq(openFaq === i ? null : i)}
                        className="w-full py-5 flex items-center justify-between text-left group"
                        data-testid={`faq-item-${i}`}>
                        <span className={`text-[15px] font-semibold pr-4 transition-colors ${openFaq === i ? 'text-[var(--color-primary)]' : 'text-[var(--color-primary-dark)]'}`}
                          style={{ fontFamily: 'var(--font-heading)' }}>
                          {t(`home.faqs.${i}.q`)}
                        </span>
                        <ChevronDown size={16} className={`shrink-0 text-[var(--color-text-secondary)]/40 transition-transform duration-300 ${openFaq === i ? 'rotate-180' : ''}`} />
                      </button>
                      <div className={`overflow-hidden transition-all duration-300 ${openFaq === i ? 'max-h-[200px] pb-5' : 'max-h-0'}`}>
                        <p className="text-[14px] text-[var(--color-text-secondary)] leading-[1.7] max-w-[600px]">{t(`home.faqs.${i}.a`)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>


        {/* ═══════════════════════════════════════════════════════════
            SECTION 9: CTA – Premium Conversion Banner
           ═══════════════════════════════════════════════════════════ */}
        <section ref={ctaRef} className="py-[64px] md:py-[80px] lg:py-[96px]" data-testid="cta-section">
          <div className="max-w-[1280px] mx-auto px-6 sm:px-8 lg:px-12">
            <div className="relative overflow-hidden rounded-[12px]"
              style={{ background: 'linear-gradient(160deg, var(--color-primary-dark) 0%, var(--color-primary) 50%, var(--color-primary-light) 100%)' }}>
              <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '32px 32px' }} />

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
                {/* Text */}
                <div className={`lg:col-span-7 p-8 sm:p-12 lg:p-16 xl:p-20 ${stagger(ctaVis, 0)}`}>
                  <h2 className="text-[28px] sm:text-[36px] lg:text-[44px] font-extrabold text-white leading-[1.1] tracking-[-0.025em] mb-5"
                    style={{ fontFamily: 'var(--font-heading)' }}>
                    {t('home.cta_title', 'Bereit für dein')}<br />
                    <span style={{ color: 'var(--color-accent)' }}>{t('home.cta_title_accent', 'Studium in Deutschland?')}</span>
                  </h2>
                  <p className="text-[15px] text-white/40 leading-[1.7] max-w-[440px] mb-10">
                    {t('home.cta_desc')}
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <Link to="/apply" data-testid="cta-apply"
                      className="inline-flex items-center justify-center gap-2.5 h-[56px] px-10 text-[15px] font-bold tracking-wide text-[var(--color-primary-dark)] rounded-full group transition-all duration-300 hover:scale-[1.02]"
                      style={{ background: 'var(--color-accent)', boxShadow: '0 4px 24px rgba(212,175,55,0.3)' }}>
                      {t('hero.cta_primary')} <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                    </Link>
                    <Link to="/booking" data-testid="cta-booking"
                      className="inline-flex items-center justify-center gap-2 h-[56px] px-8 text-[15px] font-semibold text-white/80 border-2 border-white/15 rounded-full transition-all duration-300 hover:border-white/30 hover:text-white">
                      {t('home.cta_consultation')}
                    </Link>
                  </div>
                </div>

                {/* 3D Illustration */}
                <div className={`hidden sm:flex lg:col-span-5 items-center justify-center lg:justify-end p-8 sm:p-10 lg:p-12 ${stagger(ctaVis, 1)}`} style={staggerDelay(1)}>
                  <img src={IMG.successIllustration} alt="Erfolgreicher Studienabschluss"
                    className="w-[200px] sm:w-[240px] lg:w-[300px] h-auto"
                    style={{ filter: 'drop-shadow(0 24px 48px rgba(0,0,0,0.15))' }}
                    data-testid="cta-illustration" />
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>
      <PublicFooter />
    </div>
  );
}
