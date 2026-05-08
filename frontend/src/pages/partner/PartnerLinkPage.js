import React, { useState, useEffect } from 'react';
import { Link2, Copy, Check } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { InfoCard, ContentHeader } from '../../components/layout/BackstageComponents';
import { toast } from 'sonner';

// Always build the shareable referral link from the user's current origin —
// that's the URL the partner is actually looking at and wants to forward.
const APP_URL = typeof window !== 'undefined' ? window.location.origin : '';

export default function PartnerLinkPage() {
  const [linkData, setLinkData] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    apiClient.get('/api/partner/referral-link')
      .then(r => setLinkData(r.data))
      .catch(() => toast.error('Link konnte nicht geladen werden'));
  }, []);

  const fullLink = linkData ? `${APP_URL}${linkData.link}` : '';

  const copyLink = () => {
    navigator.clipboard.writeText(fullLink).then(() => {
      setCopied(true);
      toast.success('Link kopiert');
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="space-y-6">
      <ContentHeader title="Empfehlungslink" subtitle="Teilen Sie Ihren persoenlichen Link mit potenziellen Bewerbern" />

      <InfoCard title="Ihr persoenlicher Empfehlungslink">
        {linkData ? (
          <div className="mt-2 space-y-4">
            <div className="flex items-center gap-2">
              <div className="flex-1 p-3 bg-[var(--color-surface)] rounded-[var(--radius-sm)] border border-[var(--color-border)] font-mono text-sm break-all">
                {fullLink}
              </div>
              <button
                data-testid="copy-link-btn" onClick={copyLink}
                className="flex items-center gap-1.5 px-4 py-3 text-sm font-medium text-white bg-[var(--color-primary)] rounded-[var(--radius-sm)] hover:opacity-90 flex-shrink-0"
              >
                {copied ? <Check size={14} /> : <Copy size={14} />}
                {copied ? 'Kopiert' : 'Kopieren'}
              </button>
            </div>
            <div className="flex items-center gap-2 text-xs text-[var(--color-text-secondary)]">
              <Link2 size={12} />
              <span>Referral-Code: <code className="bg-[var(--color-surface)] px-1.5 py-0.5 rounded">{linkData.referral_code}</code></span>
            </div>
            <p className="text-xs text-[var(--color-text-secondary)]">
              Wenn ein Bewerber ueber diesen Link eine Bewerbung einreicht, wird diese automatisch Ihrem Partner-Konto zugeordnet.
            </p>
          </div>
        ) : (
          <div className="py-4 text-sm text-[var(--color-text-secondary)]">Laden...</div>
        )}
      </InfoCard>

      <InfoCard title="Verwendung">
        <ul className="space-y-2 mt-1 text-sm text-[var(--color-text-secondary)]">
          <li className="flex items-start gap-2"><span className="text-[var(--color-primary)] font-bold">1.</span> Kopieren Sie den Link oben</li>
          <li className="flex items-start gap-2"><span className="text-[var(--color-primary)] font-bold">2.</span> Teilen Sie ihn mit interessierten Studienkolleg-Bewerbern</li>
          <li className="flex items-start gap-2"><span className="text-[var(--color-primary)] font-bold">3.</span> Verfolgen Sie Ihre Vermittlungen unter "Tracking"</li>
        </ul>
      </InfoCard>
    </div>
  );
}
