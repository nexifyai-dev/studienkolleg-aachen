import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { BarChart3, TrendingUp, Users, DollarSign, Calendar } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import apiClient from '../../lib/apiClient';
import { InfoCard, ContentHeader } from '../../components/layout/BackstageComponents';
import { toast } from 'sonner';
import { getLang } from '../../lib/utils';

export default function PartnerTrackingPage() {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiClient.get('/api/partner/dashboard'),
      apiClient.get('/api/partner/commission-summary'),
    ]).then(([dash, summary]) => {
      setData({ dashboard: dash.data, summary: summary.data });
    }).catch(() => toast.error(lang === 'de' ? 'Daten konnten nicht geladen werden' : 'Could not load data'))
      .finally(() => setLoading(false));
  }, [lang]);

  if (loading) return <div className="flex items-center justify-center py-16 text-[var(--color-text-secondary)]">{lang === 'de' ? 'Laden...' : 'Loading...'}</div>;
  if (!data) return <div className="text-center py-16 text-sm text-[var(--color-text-secondary)]">{lang === 'de' ? 'Keine Daten verfuegbar' : 'No data available'}</div>;

  const { dashboard, summary } = data;
  const commission = dashboard.commissions || {};
  const months = summary?.by_month || [];

  const chartData = [...months].reverse().map(m => ({
    name: m.month,
    [lang === 'de' ? 'Verdient' : 'Earned']: m.earned,
    [lang === 'de' ? 'Offen' : 'Pending']: m.pending,
    referrals: m.referrals,
  }));

  return (
    <div className="space-y-6">
      <ContentHeader
        title={lang === 'de' ? 'Performance-Tracking' : 'Performance Tracking'}
        subtitle={lang === 'de' ? 'Uebersicht ueber Ihre Vermittlungsleistung' : 'Overview of your referral performance'}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <InfoCard title={lang === 'de' ? 'Vermittlungen gesamt' : 'Total Referrals'}>
          <div className="flex items-center gap-2">
            <Users size={16} className="text-[var(--color-primary)]" />
            <span data-testid="track-total" className="text-xl font-bold">{dashboard.total_referrals || 0}</span>
          </div>
        </InfoCard>
        <InfoCard title={lang === 'de' ? 'Aktiv' : 'Active'}>
          <div className="flex items-center gap-2">
            <TrendingUp size={16} className="text-[var(--color-accent-teal)]" />
            <span data-testid="track-active" className="text-xl font-bold">{dashboard.active_referrals || 0}</span>
          </div>
        </InfoCard>
        <InfoCard title={lang === 'de' ? 'Eingeschrieben' : 'Enrolled'}>
          <div className="flex items-center gap-2">
            <BarChart3 size={16} className="text-green-600" />
            <span data-testid="track-enrolled" className="text-xl font-bold">{dashboard.enrolled || 0}</span>
          </div>
        </InfoCard>
        <InfoCard title={lang === 'de' ? 'Offene Provision' : 'Open Commission'}>
          <div className="flex items-center gap-2">
            <DollarSign size={16} className="text-[var(--color-accent)]" />
            <span data-testid="track-balance" className="text-xl font-bold">{(commission.balance || 0).toFixed(2)} EUR</span>
          </div>
        </InfoCard>
      </div>

      {/* Recharts Bar Chart */}
      {chartData.length > 0 && (
        <InfoCard title={lang === 'de' ? 'Monatliche Provisionen' : 'Monthly Commissions'}>
          <div data-testid="partner-commission-chart" style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={chartData} margin={{ top: 8, right: 8, left: -8, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-divider-subtle)" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: 'var(--color-text-tertiary)' }} />
                <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-tertiary)' }} />
                <Tooltip
                  contentStyle={{ background: 'var(--color-surface-elevated)', border: '1px solid var(--color-divider)', borderRadius: 'var(--radius-sm)', fontSize: 12 }}
                  formatter={(value) => `${value.toFixed(0)} EUR`}
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey={lang === 'de' ? 'Verdient' : 'Earned'} fill="#10B981" radius={[3, 3, 0, 0]} />
                <Bar dataKey={lang === 'de' ? 'Offen' : 'Pending'} fill="#F59E0B" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </InfoCard>
      )}

      {/* Monthly Table */}
      {months.length > 0 && (
        <InfoCard title={lang === 'de' ? 'Monatliche Uebersicht' : 'Monthly Overview'}>
          <div data-testid="monthly-table" className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border)]">
                  <th className="text-left py-2 pr-4 text-xs font-medium text-[var(--color-text-secondary)]">{lang === 'de' ? 'Monat' : 'Month'}</th>
                  <th className="text-right py-2 px-4 text-xs font-medium text-[var(--color-text-secondary)]">{lang === 'de' ? 'Vermittlungen' : 'Referrals'}</th>
                  <th className="text-right py-2 px-4 text-xs font-medium text-[var(--color-text-secondary)]">{lang === 'de' ? 'Verdient' : 'Earned'}</th>
                  <th className="text-right py-2 pl-4 text-xs font-medium text-[var(--color-text-secondary)]">{lang === 'de' ? 'Offen' : 'Pending'}</th>
                </tr>
              </thead>
              <tbody>
                {months.map(m => (
                  <tr key={m.month} className="border-b border-[var(--color-border)] last:border-0">
                    <td className="py-2.5 pr-4 flex items-center gap-2">
                      <Calendar size={12} className="text-[var(--color-text-secondary)]" />
                      <span className="font-medium">{m.month}</span>
                    </td>
                    <td className="text-right py-2.5 px-4">{m.referrals}</td>
                    <td className="text-right py-2.5 px-4 text-green-600 font-medium">{m.earned.toFixed(2)} EUR</td>
                    <td className="text-right py-2.5 pl-4 text-[var(--color-text-secondary)]">{m.pending.toFixed(2)} EUR</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </InfoCard>
      )}

      {/* Commission rates */}
      <InfoCard title={lang === 'de' ? 'Provisionssaetze' : 'Commission Rates'}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-1">
          {Object.entries(summary?.rates || {}).map(([course, rate]) => (
            <div key={course} className="p-3 bg-[var(--color-surface)] rounded-[var(--radius-sm)] text-center">
              <p className="text-xs text-[var(--color-text-secondary)] mb-1">{course}</p>
              <p className="text-sm font-bold text-[var(--color-text-primary)]">{rate.toFixed(0)} EUR</p>
            </div>
          ))}
        </div>
      </InfoCard>
    </div>
  );
}
