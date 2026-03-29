import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { Users, Loader2 } from 'lucide-react';
import { STAGE_LABELS, STAGE_COLORS, formatDate } from '../../lib/utils';

export default function PartnerReferralsPage() {
  const { t } = useTranslation();
  const [referrals, setReferrals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get('/api/partner/referrals', { withCredentials: true })
      .then(r => setReferrals(r.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-primary" />
    </div>
  );

  return (
    <div className="space-y-6 animate-fade-in" data-testid="partner-referrals-page">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">{t('partner.referrals')}</h1>
        <p className="text-slate-500 text-sm mt-1">{t('partner.referrals_desc')}</p>
      </div>

      {referrals.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-sm p-8 text-center" data-testid="partner-referrals-empty">
          <Users size={32} className="text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">{t('partner.no_referrals')}</p>
          <p className="text-xs text-slate-400 mt-1">{t('partner.no_referrals_hint')}</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-sm overflow-hidden">
          <table className="w-full text-sm" data-testid="partner-referrals-table">
            <thead className="bg-slate-50 text-left">
              <tr>
                <th className="px-4 py-3 font-medium text-slate-500 text-xs">{t('partner.col_name')}</th>
                <th className="px-4 py-3 font-medium text-slate-500 text-xs">{t('partner.col_course')}</th>
                <th className="px-4 py-3 font-medium text-slate-500 text-xs">{t('partner.col_status')}</th>
                <th className="px-4 py-3 font-medium text-slate-500 text-xs">{t('partner.col_date')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {referrals.map(ref => (
                <tr key={ref.id} data-testid={`partner-referral-${ref.id}`} className="hover:bg-slate-50/50">
                  <td className="px-4 py-3 text-slate-800">{ref.applicant_name || '–'}</td>
                  <td className="px-4 py-3 text-slate-600">{ref.course_type || '–'}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-sm ${STAGE_COLORS[ref.current_stage] || 'bg-slate-100 text-slate-600'}`}>
                      {STAGE_LABELS[ref.current_stage] || ref.current_stage}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{formatDate(ref.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
