import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { Link2, Copy, CheckCircle, Loader2 } from 'lucide-react';

export default function PartnerLinkPage() {
  const { t } = useTranslation();
  const [linkData, setLinkData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    apiClient.get('/api/partner/referral-link', { withCredentials: true })
      .then(r => setLinkData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const fullLink = linkData ? `${window.location.origin}${linkData.link}` : '';

  const copyLink = () => {
    navigator.clipboard.writeText(fullLink).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-primary" />
    </div>
  );

  return (
    <div className="space-y-6 animate-fade-in" data-testid="partner-link-page">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">{t('partner.referral_link')}</h1>
        <p className="text-slate-500 text-sm mt-1">{t('partner.referral_link_desc')}</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm p-6 max-w-lg">
        <div className="flex items-center gap-2 mb-4">
          <Link2 size={16} className="text-primary" />
          <h3 className="font-semibold text-slate-800 text-sm">{t('partner.your_link')}</h3>
        </div>

        <div className="flex items-center gap-2">
          <input
            readOnly
            value={fullLink}
            data-testid="partner-link-input"
            className="flex-1 border border-slate-200 rounded-sm px-3 py-2 text-sm bg-slate-50 text-slate-700"
          />
          <button onClick={copyLink} data-testid="partner-link-copy-btn"
            className="flex items-center gap-1.5 bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary/90 transition-colors">
            {copied ? <CheckCircle size={14} /> : <Copy size={14} />}
            {copied ? t('partner.copied') : t('partner.copy')}
          </button>
        </div>

        <p className="text-xs text-slate-400 mt-3">{t('partner.link_hint')}</p>
      </div>
    </div>
  );
}
