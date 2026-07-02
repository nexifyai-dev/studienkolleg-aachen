import React from 'react';
import { Link } from 'react-router-dom';
import { getStageKnowledge } from '../../lib/portalKnowledge';
import { ArrowRight, Clock, ExternalLink, User, Users, CheckCircle } from 'lucide-react';

/* shadcn-Komponenten */
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';

export default function StatusCockpit({ stage, applicationId, lang = 'de' }) {
  const info = getStageKnowledge(stage, lang);
  if (!info) return null;

  const progress = info.progress || 0;
  const isApplicantAction = info.whoResponsible === 'applicant';

  return (
    <Card className="overflow-hidden" data-testid="status-cockpit">
      {/* Status Header (dunkler Hintergrund) */}
      <div className="bg-[var(--color-primary)] px-5 py-5 text-white">
        <div className="flex items-center justify-between mb-2">
          <p className="text-white/70 text-[10px] font-semibold tracking-[0.1em] uppercase">
            {lang === 'de' ? 'Dein aktueller Status' : 'Your Current Status'}
          </p>
          {applicationId && (
            <Badge variant="outline" size="xs" className="border-white/20 text-white/50 bg-transparent">
              #{applicationId?.slice(-6).toUpperCase()}
            </Badge>
          )}
        </div>
        <h2 className="text-lg font-extrabold mb-1" style={{ fontFamily: 'var(--font-heading)' }}>{info.label}</h2>
        <p className="text-white/80 text-sm">{info.meaning}</p>
        {/* Fortschrittsbalken */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-[10px] text-white/60 mb-1.5">
            <span>{lang === 'de' ? 'Fortschritt' : 'Progress'}</span>
            <span className="tabular-nums font-semibold">{progress}%</span>
          </div>
          <div className="h-1.5 bg-white/20 rounded-[var(--radius-full)] overflow-hidden">
            <div className="h-full bg-white/80 rounded-[var(--radius-full)] transition-all duration-700" style={{ width: `${progress}%` }} />
          </div>
        </div>
      </div>

      {/* Details */}
      <CardContent className="pt-5 space-y-4">
        {/* Zustaendigkeit */}
        <div className="flex items-start gap-3" data-testid="status-responsibility">
          <div className={`w-8 h-8 rounded-[var(--radius-sm)] flex items-center justify-center shrink-0 ${isApplicantAction ? 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]' : 'bg-[rgba(10,25,47,0.1)] text-[var(--color-primary)]'}`}>
            {isApplicantAction ? <User size={16} /> : <Users size={16} />}
          </div>
          <div>
            <p className="text-xs font-semibold text-[var(--color-text-primary)]">{info.whoLabel}</p>
            {info.whatsHappening && <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">{info.whatsHappening}</p>}
          </div>
        </div>

        {/* Naechste Schritte */}
        {info.nextSteps?.length > 0 && (
          <div data-testid="status-next-steps">
            <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--color-text-tertiary)] mb-2">
              {lang === 'de' ? 'Naechste Schritte' : 'Next Steps'}
            </p>
            <ul className="space-y-1.5">
              {info.nextSteps.map((step, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-[var(--color-text-secondary)]">
                  <ArrowRight size={12} className="text-[var(--color-primary)] mt-0.5 shrink-0" />
                  <span>{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Risiken/Hinweise */}
        {info.risks?.length > 0 && (
          <div className="bg-[var(--color-warning-bg)] border border-[var(--color-warning-border)] rounded-[var(--radius-sm)] p-3" data-testid="status-risks">
            <p className="text-xs font-semibold text-[var(--color-warning)] mb-1">
              {lang === 'de' ? 'Hinweise' : 'Notes'}
            </p>
            {info.risks.map((risk, i) => (
              <p key={i} className="text-xs text-[var(--color-warning)]">{risk}</p>
            ))}
          </div>
        )}

        {/* Voraussichtliche Dauer */}
        {info.eta && (
          <div className="flex items-center gap-2 text-xs text-[var(--color-text-secondary)]">
            <Clock size={12} />
            <span>{lang === 'de' ? 'Voraussichtliche Dauer: ' : 'Estimated time: '}{info.eta}</span>
          </div>
        )}

        {/* CTAs */}
        {info.ctas?.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-1" data-testid="status-ctas">
            {info.ctas.map((cta, i) => (
              <Link key={i} to={cta.path} className={i === 0 ? 'w2g-btn-primary text-xs' : 'w2g-btn-secondary text-xs'}>
                {cta.label}
              </Link>
            ))}
          </div>
        )}

        {/* Wissenslinks */}
        {info.knowledgeLinks?.length > 0 && (
          <div className="border-t border-[var(--color-divider-subtle)] pt-3 mt-3" data-testid="status-knowledge">
            <p className="text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-[0.1em] mb-2">
              {lang === 'de' ? 'Hilfreiche Informationen' : 'Helpful Information'}
            </p>
            <div className="flex flex-wrap gap-2">
              {info.knowledgeLinks.map((link, i) => (
                <a key={i} href={link.url} target={link.url.startsWith('http') ? '_blank' : '_self'}
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors">
                  {link.url.startsWith('http') ? <ExternalLink size={10} /> : <CheckCircle size={10} />}
                  {link.label}
                </a>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
