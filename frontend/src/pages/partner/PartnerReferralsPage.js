import React, { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { Users, Search, XCircle } from 'lucide-react';
import { getStageLabel, STAGE_COLORS, formatDate, getLang } from '../../lib/utils';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

export default function PartnerReferralsPage() {
  const { t } = useTranslation();
  const [referrals, setReferrals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    apiClient.get('/api/partner/referrals', { withCredentials: true })
      .then(r => setReferrals(r.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    if (!searchTerm) return referrals;
    const q = searchTerm.toLowerCase();
    return referrals.filter(r =>
      (r.applicant_name || '').toLowerCase().includes(q) ||
      (r.course_type || '').toLowerCase().includes(q) ||
      (r.current_stage || '').toLowerCase().includes(q)
    );
  }, [referrals, searchTerm]);

  if (loading) return <div className="w2g-loading"><div className="w2g-spinner" /><p className="w2g-loading-text">Wird geladen...</p></div>;

  return (
    <PageScaffold
      title={t('partner.referrals')}
      subtitle={t('partner.referrals_desc')}
      testId="partner-referrals-page"
      toolbar={referrals.length > 0 ? (
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72 shrink-0">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
                placeholder="Referrals durchsuchen..."
                data-testid="partner-referrals-search"
                className="w2g-search pl-9" />
              {searchTerm && (
                <button onClick={() => setSearchTerm('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]">
                  <XCircle size={13} />
                </button>
              )}
            </div>
          }
        />
      ) : null}
    >
      {filtered.length === 0 ? (
        <div className="w2g-empty" data-testid="partner-referrals-empty">
          <Users size={28} className="w2g-empty-icon" />
          <p className="w2g-empty-text">{searchTerm ? 'Keine Treffer' : t('partner.no_referrals')}</p>
          <p className="w2g-empty-hint">{!searchTerm && t('partner.no_referrals_hint')}</p>
        </div>
      ) : (
        <Card className="p-0 overflow-hidden">
          <table className="w2g-table" data-testid="partner-referrals-table">
            <thead>
              <tr>
                <th>{t('partner.col_name')}</th>
                <th>{t('partner.col_course')}</th>
                <th>{t('partner.col_status')}</th>
                <th>{t('partner.col_date')}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(ref => (
                <tr key={ref.id} data-testid={`partner-referral-${ref.id}`} className="hover:bg-[var(--color-surface-elevated)] transition-colors">
                  <td className="text-sm text-[var(--color-text-primary)] font-medium">{ref.applicant_name || '\u2013'}</td>
                  <td className="text-sm text-[var(--color-text-secondary)]">{ref.course_type || '\u2013'}</td>
                  <td>
                    <span className={`w2g-badge ${STAGE_COLORS[ref.current_stage] || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
                      {getStageLabel(ref.current_stage, 'de')}
                    </span>
                  </td>
                  <td className="text-xs text-[var(--color-text-secondary)]">{formatDate(ref.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </PageScaffold>
  );
}
