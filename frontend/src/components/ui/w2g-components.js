import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Loader2 } from 'lucide-react';

/* ═══════════════════════════════════════════════════════════════════════
   W2G DESIGN SYSTEM – Zentrale UI-Bibliothek
   Alle wiederverwendbaren Komponenten fuer konsistente UI-Qualitaet.
   Source of Truth fuer Buttons, Badges, Section-Layouts, Cards.
   ═══════════════════════════════════════════════════════════════════════ */

/* ─── BUTTONS ─────────────────────────────────────────────────────────── */
const BTN_BASE = 'inline-flex items-center justify-center gap-2 font-bold transition-all duration-300 rounded-full';

const BTN_VARIANTS = {
  primary: `${BTN_BASE} text-[var(--color-primary-dark)] hover:scale-[1.02]`,
  secondary: `${BTN_BASE} border-2 hover:scale-[1.01]`,
  ghost: `${BTN_BASE} hover:bg-[var(--color-surface-elevated)]`,
  outline: `${BTN_BASE} border-2 border-[rgba(10,25,47,0.15)] text-[var(--color-primary-dark)] hover:border-[rgba(10,25,47,0.3)]`,
  'outline-light': `${BTN_BASE} border-2 border-white/15 text-white/80 hover:border-white/30 hover:text-white`,
};

const BTN_SIZES = {
  sm: 'h-[36px] px-5 text-[12px]',
  md: 'h-[44px] px-6 text-[13px]',
  lg: 'h-[48px] px-8 text-[14px]',
  xl: 'h-[56px] px-10 text-[15px] tracking-wide',
};

export function W2GButton({ variant = 'primary', size = 'lg', children, loading, arrow, className = '', as, to, ...props }) {
  const cls = `${BTN_VARIANTS[variant] || BTN_VARIANTS.primary} ${BTN_SIZES[size] || BTN_SIZES.lg} ${className}`;
  const style = variant === 'primary'
    ? { background: 'var(--color-accent)', boxShadow: '0 4px 24px rgba(212,175,55,0.25)' }
    : variant === 'secondary'
      ? { borderColor: 'var(--color-primary)', color: 'var(--color-primary)' }
      : {};

  const content = (
    <>
      {loading && <Loader2 size={16} className="animate-spin" />}
      {children}
      {arrow && !loading && <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />}
    </>
  );

  if (to) {
    return <Link to={to} className={`group ${cls}`} style={style} {...props}>{content}</Link>;
  }
  return <button className={`group ${cls}`} style={style} disabled={loading} {...props}>{content}</button>;
}

/* ─── SECTION LABEL ───────────────────────────────────────────────────── */
export function SectionLabel({ children, light = false }) {
  return (
    <div className="flex items-center gap-3 mb-6">
      <div className="w-6 h-[2px]" style={{ background: 'var(--color-accent)' }} />
      <span className={`text-[11px] font-semibold tracking-[0.2em] uppercase ${light ? 'text-[var(--color-accent)]' : 'text-[rgba(10,25,47,0.6)]'}`}>
        {children}
      </span>
    </div>
  );
}

/* ─── SECTION HEADING ─────────────────────────────────────────────────── */
export function SectionHeading({ children, light = false, className = '' }) {
  return (
    <h2 className={`text-[28px] sm:text-[36px] lg:text-[44px] font-extrabold leading-[1.1] tracking-[-0.025em] ${light ? 'text-white' : 'text-[var(--color-primary-dark)]'} ${className}`}
      style={{ fontFamily: 'var(--font-heading)' }}>
      {children}
    </h2>
  );
}

/* ─── SECTION WRAPPER ─────────────────────────────────────────────────── */
export function Section({ children, dark = false, className = '', padding = 'py-[64px] md:py-[80px] lg:py-[96px]', id, testId }) {
  return (
    <section className={`${padding} ${dark ? '' : ''} ${className}`}
      style={dark ? { background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' } : {}}
      id={id} data-testid={testId}>
      {dark && <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />}
      <div className="max-w-[1280px] mx-auto px-6 sm:px-8 lg:px-12 relative z-10">
        {children}
      </div>
    </section>
  );
}

/* ─── CARD ────────────────────────────────────────────────────────────── */
export function W2GCard({ children, className = '', hover = true, padding = 'p-6 sm:p-8' }) {
  return (
    <div className={`rounded-[8px] border border-[rgba(10,25,47,0.08)] bg-white overflow-hidden ${padding} ${hover ? 'transition-all duration-300 hover:border-[rgba(10,25,47,0.15)] hover:-translate-y-0.5' : ''} ${className}`}
      style={{ boxShadow: '0 2px 12px rgba(17,54,85,0.04)' }}>
      {children}
    </div>
  );
}

/* ─── BADGE ───────────────────────────────────────────────────────────── */
export function W2GBadge({ children, variant = 'gold', className = '' }) {
  const styles = {
    gold: { background: 'rgba(212,175,55,0.1)', color: 'var(--color-accent)' },
    primary: { background: '#F0F4F8', color: 'var(--color-primary)' },
    success: { background: 'rgba(34,197,94,0.1)', color: '#16a34a' },
    error: { background: 'rgba(239,68,68,0.06)', color: '#EF4444' },
  };
  return (
    <span className={`inline-block text-[10px] font-bold tracking-[0.12em] uppercase px-3 py-1 rounded-full ${className}`}
      style={styles[variant] || styles.gold}>
      {children}
    </span>
  );
}

/* ─── ICON WRAP ───────────────────────────────────────────────────────── */
export function IconWrap({ children, size = 44, className = '' }) {
  return (
    <div className={`inline-flex items-center justify-center shrink-0 rounded-[8px] ${className}`}
      style={{ width: size, height: size, background: 'rgba(212,175,55,0.12)', color: 'var(--color-accent)' }}>
      {children}
    </div>
  );
}

/* ─── DARK HERO ───────────────────────────────────────────────────────── */
export function DarkHero({ children, className = '' }) {
  return (
    <section className={`relative overflow-hidden py-[56px] md:py-[72px] lg:py-[96px] ${className}`}
      style={{ background: 'linear-gradient(170deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)' }}>
      <div className="absolute inset-0 opacity-[0.02]"
        style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, white 1px, transparent 1px)', backgroundSize: '48px 48px' }} />
      <div className="max-w-[1280px] mx-auto px-6 sm:px-8 lg:px-12 relative z-10">
        {children}
      </div>
    </section>
  );
}

/* ─── STAGGER ANIMATION HELPERS ───────────────────────────────────────── */
export const stagger = (vis, idx = 0) => `transition-all duration-700 ${vis ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}`;
export const staggerDelay = (idx) => ({ transitionDelay: `${idx * 80}ms` });
