import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import apiClient from '../../lib/apiClient';
import { Users, UserCheck, Award, Link2, Loader2 } from 'lucide-react';

export default function PartnerDashboardPage() {
  const { t } = useTranslation();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get('/api/partner/dashboard', { withCredentials: true })
      .then(r => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-primary" />
    </div>
  );

  return (
    <div className="space-y-6 animate-fade-in" data-testid="partner-dashboard">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">{t('partner.welcome')}, {stats?.partner_name}</h1>
        <p className="text-slate-500 text-sm mt-1">{t('partner.overview')}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-sm p-5" data-testid="partner-stat-total">
          <div className="flex items-center gap-2 mb-2">
            <Users size={16} className="text-primary" />
            <span className="text-xs font-medium text-slate-500">{t('partner.total_referrals')}</span>
          </div>
          <p className="text-3xl font-heading font-bold text-slate-800">{stats?.total_referrals || 0}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-sm p-5" data-testid="partner-stat-active">
          <div className="flex items-center gap-2 mb-2">
            <UserCheck size={16} className="text-primary" />
            <span className="text-xs font-medium text-slate-500">{t('partner.active_referrals')}</span>
          </div>
          <p className="text-3xl font-heading font-bold text-slate-800">{stats?.active_referrals || 0}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-sm p-5" data-testid="partner-stat-enrolled">
          <div className="flex items-center gap-2 mb-2">
            <Award size={16} className="text-primary" />
            <span className="text-xs font-medium text-slate-500">{t('partner.enrolled')}</span>
          </div>
          <p className="text-3xl font-heading font-bold text-slate-800">{stats?.enrolled || 0}</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm p-5">
        <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <Link2 size={16} className="text-primary" />
          {t('partner.quick_actions')}
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Link to="/partner/referrals" data-testid="partner-action-referrals"
            className="flex items-center gap-3 border border-slate-200 rounded-sm p-4 hover:border-primary/30 transition-colors">
            <Users size={18} className="text-primary" />
            <div>
              <p className="font-medium text-slate-800 text-sm">{t('partner.view_referrals')}</p>
              <p className="text-xs text-slate-500">{t('partner.view_referrals_desc')}</p>
            </div>
          </Link>
          <Link to="/partner/link" data-testid="partner-action-link"
            className="flex items-center gap-3 border border-slate-200 rounded-sm p-4 hover:border-primary/30 transition-colors">
            <Link2 size={18} className="text-primary" />
            <div>
              <p className="font-medium text-slate-800 text-sm">{t('partner.get_link')}</p>
              <p className="text-xs text-slate-500">{t('partner.get_link_desc')}</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
