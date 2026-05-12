import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api-hooks';
import {
  BarChart3, Users, TrendingUp, Loader2, Euro, Download,
  Globe2, Calendar, Target, Inbox,
} from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { toast } from 'sonner';

const RANGE_OPTIONS = [
  { key: '7d', label: '7 Tage' },
  { key: '30d', label: '30 Tage' },
  { key: '90d', label: '90 Tage' },
  { key: '12m', label: '12 Monate' },
  { key: 'all', label: 'Alles' },
];

function useAnalytics(range) {
  return useQuery({
    queryKey: ['admin', 'analytics', range],
    queryFn: () => api.get(`/admin/analytics?range=${range}`).then(r => r.data),
    staleTime: 60000,
    keepPreviousData: true,
  });
}

function KpiCard({ icon: Icon, label, value, sub, accent, testId }) {
  return (
    <Card className="border-l-[3px]" style={{ borderLeftColor: accent || 'var(--color-primary)' }} data-testid={testId}>
      <CardContent className="px-4 py-4">
        <div className="flex items-center gap-1.5 mb-2">
          <Icon size={13} style={{ color: accent || 'var(--color-primary)' }} />
          <span className="text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)] font-semibold">{label}</span>
        </div>
        <p className="text-2xl font-extrabold text-[var(--color-text-primary)] tabular-nums leading-none">
          {value ?? '–'}
        </p>
        {sub && <p className="text-[11px] text-[var(--color-text-secondary)] mt-1">{sub}</p>}
      </CardContent>
    </Card>
  );
}

function BarChart({ data, valueKey, labelKey, accent, testId, formatValue }) {
  const max = Math.max(1, ...(data || []).map(d => d[valueKey] || 0));
  return (
    <div className="space-y-1.5" data-testid={testId}>
      {(!data || data.length === 0) ? (
        <p className="text-xs text-[var(--color-text-tertiary)] text-center py-6">Keine Daten vorhanden</p>
      ) : data.map((d, i) => {
        const pct = (d[valueKey] / max) * 100;
        return (
          <div key={i} className="flex items-center gap-3">
            <span className="text-[11px] text-[var(--color-text-secondary)] w-28 truncate shrink-0">{d[labelKey]}</span>
            <div className="flex-1 h-5 bg-[var(--color-surface-sunken)] rounded-[var(--radius-full)] overflow-hidden">
              <div
                className="h-full rounded-[var(--radius-full)] transition-all duration-500"
                style={{ width: `${pct}%`, background: accent || 'var(--color-primary)' }}
              />
            </div>
            <span className="text-[11px] font-semibold text-[var(--color-text-primary)] w-16 text-right tabular-nums">
              {formatValue ? formatValue(d[valueKey]) : d[valueKey]}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function TrendChart({ data, valueKey, labelKey, accent, testId, formatValue, height = 120 }) {
  const max = Math.max(1, ...(data || []).map(d => d[valueKey] || 0));
  return (
    <div data-testid={testId}>
      {(!data || data.length === 0) ? (
        <p className="text-xs text-[var(--color-text-tertiary)] text-center py-6">Keine Daten vorhanden</p>
      ) : (
        <>
          <div className="flex items-end gap-1.5" style={{ height }}>
            {data.map((d, i) => {
              const h = max > 0 ? (d[valueKey] / max) * 100 : 0;
              return (
                <div key={i} className="flex-1 flex flex-col items-center justify-end gap-1 group relative">
                  <span className="text-[10px] font-medium text-[var(--color-text-primary)] tabular-nums opacity-0 group-hover:opacity-100 transition-opacity absolute -top-4">
                    {formatValue ? formatValue(d[valueKey]) : d[valueKey]}
                  </span>
                  <div
                    className="w-full rounded-t-sm transition-all duration-500 hover:opacity-80"
                    style={{ height: `${Math.max(2, h)}%`, background: accent || 'var(--color-primary)' }}
                  />
                </div>
              );
            })}
          </div>
          <div className="flex gap-1.5 mt-2">
            {data.map((d, i) => (
              <span key={i} className="flex-1 text-[9px] text-[var(--color-text-tertiary)] text-center truncate">{d[labelKey]}</span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

const SOURCE_LABELS = {
  website_form: 'Website Formular',
  partner_referral: 'Partner Empfehlung',
  direct_inquiry: 'Direkte Anfrage',
  direct: 'Direkt',
  unknown: 'Unbekannt',
};

const STAGE_LABELS = {
  lead_new: 'Neue Anfrage',
  in_review: 'In Bearbeitung',
  pending_docs: 'Unterlagen ausstehend',
  interview_scheduled: 'Beratungsgespräch',
  conditional_offer: 'Vorläufige Zusage',
  offer_sent: 'Angebot versandt',
  enrolled: 'Eingeschrieben',
  declined: 'Abgelehnt',
  on_hold: 'Pausiert',
};

export default function AdminReportsPage() {
  const [range, setRange] = useState('30d');
  const { data, isLoading, isError, refetch } = useAnalytics(range);

  const exportCsv = () => {
    if (!data) return;
    const lines = ['Bereich,Schlüssel,Wert'];
    const k = data.kpis || {};
    Object.entries(k).forEach(([key, val]) => lines.push(`KPI,${key},${val}`));
    (data.revenue_trend || []).forEach(d => lines.push(`Umsatz,${d.month},${d.revenue}`));
    (data.applicant_trend || []).forEach(d => lines.push(`Bewerber/Woche,${d.week},${d.count}`));
    (data.sources || []).forEach(d => lines.push(`Quelle,${d.source},${d.count}`));
    (data.countries || []).forEach(d => lines.push(`Land,${d.country},${d.count}`));
    Object.entries(data.pipeline || {}).forEach(([k2, v2]) => lines.push(`Pipeline,${k2},${v2}`));

    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reports_${range}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('CSV exportiert');
  };

  const pipelineData = useMemo(() => {
    if (!data?.pipeline) return [];
    return Object.entries(data.pipeline)
      .map(([k, v]) => ({ label: STAGE_LABELS[k] || k, count: v }))
      .filter(d => d.count > 0)
      .sort((a, b) => b.count - a.count);
  }, [data]);

  const sourcesData = useMemo(() => {
    return (data?.sources || []).map(s => ({ ...s, label: SOURCE_LABELS[s.source] || s.source }));
  }, [data]);

  const k = data?.kpis || {};
  const fmtCurrency = v => `${(v || 0).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`;

  return (
    <PageScaffold
      title="Reporting"
      subtitle="Systemweite Auswertungen, Umsatz und Pipeline-Analysen"
      testId="admin-reports-page"
      actions={
        <div className="flex items-center gap-2">
          <button onClick={() => refetch()} className="w2g-btn-secondary" data-testid="reports-refresh-btn">
            <Loader2 size={14} className={isLoading ? 'animate-spin' : 'hidden'} /> Aktualisieren
          </button>
          <button onClick={exportCsv} disabled={!data} className="w2g-btn-primary" data-testid="reports-export-btn">
            <Download size={14} /> CSV Export
          </button>
        </div>
      }
      toolbar={
        <div className="flex flex-wrap items-center gap-1.5">
          {RANGE_OPTIONS.map(o => (
            <button key={o.key} onClick={() => setRange(o.key)} data-testid={`reports-range-${o.key}`}
              className={range === o.key ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}>
              {o.label}
            </button>
          ))}
        </div>
      }
    >
      {isError && (
        <Card><CardContent className="px-4 py-6 text-center text-sm text-[var(--color-danger)]">
          Reports konnten nicht geladen werden. <button onClick={() => refetch()} className="underline">Erneut versuchen</button>
        </CardContent></Card>
      )}

      {/* KPI-Karten */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <KpiCard icon={Euro} label="Umsatz (bezahlt)" value={fmtCurrency(k.revenue_total)}
          sub={`${k.revenue_paid_count || 0} bezahlte Rechnungen`}
          accent="var(--color-success)" testId="kpi-revenue" />
        <KpiCard icon={Inbox} label="Offene Rechnungen" value={fmtCurrency(k.revenue_outstanding)}
          sub={`${k.revenue_outstanding_count || 0} offen/überfällig`}
          accent="var(--color-warning)" testId="kpi-outstanding" />
        <KpiCard icon={Users} label="Neue Bewerber" value={k.new_applicants}
          sub={`${k.total_applications_in_range || 0} Bewerbungen im Zeitraum`}
          accent="var(--color-primary)" testId="kpi-new-applicants" />
        <KpiCard icon={Target} label="Konversion" value={`${k.conversion_rate || 0}%`}
          sub={`${k.enrolled_in_range || 0} eingeschrieben`}
          accent="var(--color-accent)" testId="kpi-conversion" />
      </div>

      {/* Trend-Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <Card data-testid="revenue-trend-card">
          <CardContent className="px-5 py-4">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp size={14} className="text-[var(--color-success)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Umsatz / Monat (12 M)</span>
            </div>
            <TrendChart data={data?.revenue_trend} valueKey="revenue" labelKey="label"
              accent="var(--color-success)" formatValue={fmtCurrency} testId="revenue-trend" />
          </CardContent>
        </Card>

        <Card data-testid="applicant-trend-card">
          <CardContent className="px-5 py-4">
            <div className="flex items-center gap-2 mb-4">
              <Calendar size={14} className="text-[var(--color-primary)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Bewerbungen / Woche (8 W)</span>
            </div>
            <TrendChart data={data?.applicant_trend} valueKey="count" labelKey="label"
              accent="var(--color-primary)" testId="applicant-trend" />
          </CardContent>
        </Card>
      </div>

      {/* Verteilungs-Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <Card data-testid="pipeline-card">
          <CardContent className="px-5 py-4">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 size={14} className="text-[var(--color-primary)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Pipeline-Verteilung</span>
            </div>
            <BarChart data={pipelineData} valueKey="count" labelKey="label"
              accent="var(--color-primary)" testId="pipeline-chart" />
          </CardContent>
        </Card>

        <Card data-testid="sources-card">
          <CardContent className="px-5 py-4">
            <div className="flex items-center gap-2 mb-4">
              <Inbox size={14} className="text-[var(--color-accent)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">Quellen</span>
            </div>
            <BarChart data={sourcesData} valueKey="count" labelKey="label"
              accent="var(--color-accent)" testId="sources-chart" />
          </CardContent>
        </Card>
      </div>

      {/* Länder */}
      <Card data-testid="countries-card">
        <CardContent className="px-5 py-4">
          <div className="flex items-center gap-2 mb-4">
            <Globe2 size={14} className="text-[var(--color-success)]" />
            <span className="text-xs font-semibold text-[var(--color-text-primary)]">Top 10 Herkunftsländer</span>
          </div>
          <BarChart data={data?.countries} valueKey="count" labelKey="country"
            accent="var(--color-success)" testId="countries-chart" />
        </CardContent>
      </Card>

      {isLoading && !data && (
        <div className="flex items-center justify-center h-32">
          <Loader2 size={20} className="animate-spin text-[var(--color-primary)]" />
        </div>
      )}
    </PageScaffold>
  );
}
