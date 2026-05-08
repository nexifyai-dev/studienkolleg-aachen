import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { useAuth } from '../../contexts/AuthContext';
import { Users, UserCheck, Award, Link2, Copy, CheckCircle, ChevronRight, TrendingUp, ArrowRight, ExternalLink, Share2, Euro, Wallet } from 'lucide-react';
import { getStageLabel, STAGE_COLORS, formatDate, getLang } from '../../lib/utils';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';

export default function PartnerDashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [referrals, setReferrals] = useState([]);
  const [linkData, setLinkData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    Promise.all([
      apiClient.get('/api/partner/dashboard', { withCredentials: true }).then(r => r.data).catch(() => null),
      apiClient.get('/api/partner/referrals', { withCredentials: true }).then(r => r.data).catch(() => []),
      apiClient.get('/api/partner/referral-link', { withCredentials: true }).then(r => r.data).catch(() => null),
    ]).then(([s, r, l]) => {
      setStats(s);
      setReferrals(r || []);
      setLinkData(l);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="w2g-loading"><div className="w2g-spinner" /><p className="w2g-loading-text">Partner-Bereich wird geladen...</p></div>;

  const fullLink = linkData ? `${window.location.origin}${linkData.link}` : '';
  const copyLink = () => {
    navigator.clipboard.writeText(fullLink).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(() => {});
  };

  const recentReferrals = referrals.slice(0, 5);

  return (
    <PageScaffold
      title="Partner Dashboard"
      subtitle={`Willkommen, ${stats?.partner_name || user?.full_name || user?.email} / ${new Date().toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}`}
      testId="partner-dashboard"
    >
      {/* KPI-Zone */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4" data-testid="partner-kpi-zone">
        {[
          { label: 'Gesamt Vermittlungen', value: stats?.total_referrals || 0, icon: Users, accent: 'var(--color-primary)', link: '/partner/referrals', testId: 'partner-stat-total' },
          { label: 'Aktive Vermittlungen', value: stats?.active_referrals || 0, icon: UserCheck, accent: 'var(--color-info)', link: '/partner/referrals', testId: 'partner-stat-active' },
          { label: 'Eingeschrieben', value: stats?.enrolled || 0, icon: Award, accent: 'var(--color-success)', link: '/partner/referrals', testId: 'partner-stat-enrolled' },
          { label: 'Verdient', value: `${(stats?.commissions?.earned || 0).toLocaleString('de-DE')} EUR`, icon: Euro, accent: 'var(--color-success)', link: '/partner/tracking', testId: 'partner-stat-earned', isText: true },
          { label: 'Offenes Guthaben', value: `${(stats?.commissions?.balance || 0).toLocaleString('de-DE')} EUR`, icon: Wallet, accent: 'var(--color-accent)', link: '/partner/tracking', testId: 'partner-stat-balance', isText: true },
        ].map(kpi => (
          <Link key={kpi.testId} to={kpi.link} className="group" data-testid={`${kpi.testId}-link`}>
            <Card style={{ borderLeft: `3px solid ${kpi.accent}` }} data-testid={kpi.testId}>
              <CardContent className="px-4 py-3">
                <div className="flex items-center justify-between mb-3">
                  <div className="w2g-stat-icon"><kpi.icon size={16} /></div>
                  <ChevronRight size={14} className="text-[var(--color-text-tertiary)] opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <p className="w2g-stat-value tabular-nums">{kpi.value}</p>
                <p className="w2g-stat-label">{kpi.label}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Linke Spalte */}
        <div className="lg:col-span-8 space-y-5">

          {/* Referral-Link Card */}
          {linkData && (
            <Card data-testid="partner-referral-link-card">
              <CardContent className="px-5 py-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="w2g-section-heading">
                    <Link2 size={14} /> Dein Empfehlungslink
                  </h3>
                  <Link to="/partner/link" className="w2g-section-action flex items-center gap-1">
                    Verwalten <ExternalLink size={11} />
                  </Link>
                </div>
                <div className="flex items-center gap-2">
                  <input readOnly value={fullLink} data-testid="partner-dash-link-input"
                    className="w2g-input flex-1 bg-[var(--color-surface-elevated)] text-[var(--color-text-primary)] text-sm cursor-text" />
                  <button onClick={copyLink} data-testid="partner-dash-link-copy" className="w2g-btn-primary whitespace-nowrap">
                    {copied ? <><CheckCircle size={14} /> Kopiert</> : <><Copy size={14} /> Kopieren</>}
                  </button>
                </div>
                <p className="text-xs text-[var(--color-text-tertiary)] mt-3">
                  Teile diesen Link mit Interessenten. Jede Bewerbung ueber diesen Link wird automatisch Dir zugeordnet.
                </p>
              </CardContent>
            </Card>
          )}

          {/* Letzte Vermittlungen */}
          <Card className="p-0 overflow-hidden" data-testid="partner-recent-referrals">
            <div className="px-5 py-3.5 border-b border-[var(--color-divider)] flex items-center justify-between">
              <h3 className="w2g-section-heading">
                <Users size={14} /> Vermittlungen
              </h3>
              <Link to="/partner/referrals" className="w2g-section-action flex items-center gap-1" data-testid="partner-all-referrals-link">
                Alle <ArrowRight size={12} />
              </Link>
            </div>
            {recentReferrals.length === 0 ? (
              <div className="py-12 text-center">
                <Share2 size={28} className="mx-auto mb-3 text-[var(--color-accent)]" />
                <p className="font-heading text-sm font-bold text-[var(--color-primary)] mb-1">Noch keine Vermittlungen</p>
                <p className="text-xs text-[var(--color-text-secondary)] max-w-xs mx-auto">
                  Teile deinen Empfehlungslink, um Bewerbungen zu generieren und Provisionen zu verdienen.
                </p>
                {linkData && (
                  <button onClick={copyLink} data-testid="partner-empty-copy-btn" className="w2g-btn-primary mt-4">
                    <Copy size={14} /> Link jetzt kopieren
                  </button>
                )}
              </div>
            ) : (
              <table className="w2g-table" data-testid="partner-referrals-table">
                <thead>
                  <tr>
                    <th>Bewerber</th>
                    <th>Status</th>
                    <th className="hidden md:table-cell">Datum</th>
                  </tr>
                </thead>
                <tbody>
                  {recentReferrals.map(ref => (
                    <tr key={ref.id} data-testid={`partner-ref-${ref.id}`}>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-[var(--color-primary)] flex items-center justify-center shrink-0" style={{ borderRadius: 'var(--radius-sm)' }}>
                            <span className="text-[11px] font-bold text-white">{(ref.applicant_name || '?')[0].toUpperCase()}</span>
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm font-semibold text-[var(--color-text-primary)] truncate">{ref.applicant_name || 'Unbekannt'}</p>
                            <p className="text-[11px] text-[var(--color-text-tertiary)]">{ref.course_type || '\u2013'}</p>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={`w2g-badge text-[11px] font-semibold ${STAGE_COLORS[ref.current_stage] || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
                          {getStageLabel(ref.current_stage, 'de')}
                        </span>
                      </td>
                      <td className="hidden md:table-cell text-xs text-[var(--color-text-secondary)]">{formatDate(ref.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Card>
        </div>

        {/* Rechte Spalte */}
        <div className="lg:col-span-4 space-y-5">

          {/* Schnellzugriff */}
          <Card data-testid="partner-quick-actions">
            <CardContent className="px-5 py-4">
              <h3 className="w2g-section-heading mb-4">Schnellzugriff</h3>
            <div className="space-y-1">
              {[
                { to: '/partner/referrals', icon: Users, label: 'Alle Vermittlungen', desc: 'Bewerbungen einsehen' },
                { to: '/partner/link', icon: Link2, label: 'Empfehlungslink', desc: 'Link teilen & verwalten' },
                { to: '/partner/tracking', icon: TrendingUp, label: 'Tracking & Analytics', desc: 'Performance-KPIs' },
                { to: '/partner/messages', icon: null, label: 'Nachrichten', desc: 'Kommunikation mit dem Team' },
                { to: '/partner/settings', icon: null, label: 'Einstellungen', desc: 'Kontodaten verwalten' },
              ].map(item => {
                const Icon = item.icon || ChevronRight;
                return (
                  <Link key={item.to} to={item.to}
                    data-testid={`partner-quick-${item.to.split('/').pop()}`}
                    className="flex items-center gap-3 px-3 py-2.5 text-sm text-[var(--color-text-secondary)] hover:bg-[var(--color-primary)] hover:text-white transition-all" style={{ borderRadius: 'var(--radius-sm)' }}>
                    <Icon size={15} className="shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium">{item.label}</p>
                      <p className="text-[10px] opacity-70">{item.desc}</p>
                    </div>
                  </Link>
                );
              })}
            </div>
            </CardContent>
          </Card>

          {/* Info-Box */}
          <div className="w2g-info-box-accent" data-testid="partner-info-box">
            <Award size={18} className="text-[var(--color-accent)] shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-[var(--color-primary)]">Provisionsmodell</p>
              <p className="text-xs text-[var(--color-text-secondary)] mt-1 leading-relaxed">
                Fuer jede erfolgreiche Einschreibung ueber deinen Link erhaeltst du eine Provision. Details findest du unter Tracking & Analytics.
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageScaffold>
  );
}
