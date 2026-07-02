import React from 'react';
import { ExternalLink, BookOpen } from 'lucide-react';

/* shadcn-Komponenten */
import { Card, CardContent } from '../ui/card';

export default function KnowledgeBox({ title, links, lang = 'de' }) {
  if (!links || links.length === 0) return null;

  return (
    <Card className="bg-[var(--color-primary)]/[0.02]" data-testid="knowledge-box">
      <CardContent className="pt-5">
        <div className="flex items-center gap-2 mb-3">
          <BookOpen size={14} className="text-[var(--color-primary)]" />
          <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--color-primary)]">
            {title || (lang === 'de' ? 'Hilfreiche Informationen' : 'Helpful Information')}
          </p>
        </div>
        <div className="space-y-1">
          {links.map((link, i) => (
            <a key={i} href={link.url}
              target={link.url.startsWith('http') ? '_blank' : '_self'}
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-2 py-2 rounded-[var(--radius-xs)] text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] hover:bg-[rgba(10,25,47,0.05)] transition-colors group"
              data-testid={`knowledge-link-${i}`}>
              {link.url.startsWith('http') ? (
                <ExternalLink size={12} className="text-[var(--color-text-tertiary)] group-hover:text-[var(--color-primary)] shrink-0" />
              ) : (
                <BookOpen size={12} className="text-[var(--color-text-tertiary)] group-hover:text-[var(--color-primary)] shrink-0" />
              )}
              <span className="flex-1">{link.label}</span>
              {link.source && <span className="text-[10px] text-[var(--color-text-tertiary)]">{link.source}</span>}
            </a>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
