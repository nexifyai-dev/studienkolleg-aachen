import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FileSpreadsheet, Download, Loader2, MessageSquare, Users, Table2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { InfoCard } from '../../components/layout/BackstageComponents';
import { toast } from 'sonner';
import { useDashboardStats } from '../../lib/api-hooks';
import { getLang } from '../../lib/utils';
import { API } from '../../lib/apiBase';

const CHART_COLORS = ['#0F7B8A', '#1A3A5C', '#F59E0B', '#8B5CF6', '#EC4899', '#3B82F6', '#10B981', '#EF4444', '#6B7280', '#9CA3AF'];

export default function StaffReportingPage() {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const { data: stats, isLoading } = useDashboardStats();
  const [exporting, setExporting] = useState(false);
  const [period, setPeriod] = useState('all');

  const handleExport = async () => {
    setExporting(true);
    try {
      const url = `${API}/api/export/applications${period !== 'all' ? `?stage=${period}` : ''}`;
      const r = await fetch(url, { credentials: 'include' });
      if (!r.ok) throw new Error('Export fehlgeschlagen');
      const blob = await r.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `bewerbungen_export_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      toast.success(lang === 'de' ? 'Export heruntergeladen' : 'Export downloaded');
    } catch {
      toast.error(lang === 'de' ? 'Export fehlgeschlagen' : 'Export failed');
    } finally {
      setExporting(false);
    }
  };

  const stages = stats?.pipeline || stats?.stages || {};
  const totals = stats || {};

  const totalApps = stats?.total_leads || 0;
  const enrolled = stages.enrolled || 0;
  const inProgress = stages.in_review || 0;
  const conversionRate = totalApps > 0 ? Math.round((enrolled / totalApps) * 100) : 0;

  const pipelineData = [
    { name: lang === 'de' ? 'Neu' : 'New', value: stages.lead_new || 0, color: CHART_COLORS[0] },
    { name: lang === 'de' ? 'Bearbeitung' : 'Review', value: stages.in_review || 0, color: CHART_COLORS[1] },
    { name: lang === 'de' ? 'Dokumente' : 'Docs', value: stages.pending_docs || 0, color: CHART_COLORS[2] },
    { name: 'Interview', value: stages.interview_scheduled || 0, color: CHART_COLORS[3] },
    { name: lang === 'de' ? 'Bed. Angebot' : 'Cond. Offer', value: stages.conditional_offer || 0, color: CHART_COLORS[4] },
    { name: lang === 'de' ? 'Angebot' : 'Offer', value: stages.offer_sent || 0, color: CHART_COLORS[5] },
    { name: lang === 'de' ? 'Eingeschr.' : 'Enrolled', value: stages.enrolled || 0, color: CHART_COLORS[6] },
    { name: lang === 'de' ? 'Abgelehnt' : 'Declined', value: stages.declined || 0, color: CHART_COLORS[7] },
    { name: lang === 'de' ? 'Pausiert' : 'On Hold', value: stages.on_hold || 0, color: CHART_COLORS[8] },
    { name: lang === 'de' ? 'Archiv' : 'Archive', value: stages.archived || 0, color: CHART_COLORS[9] },
  ];

  const pieData = pipelineData.filter(d => d.value > 0);

  return (
    <PageScaffold title="Reporting" icon={<FileSpreadsheet size={20} />} testId="staff-reporting-page">
      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 size={20} className="animate-spin text-[var(--color-text-secondary)]" /></div>
      ) : (
        <>
          {/* KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <InfoCard title={lang === 'de' ? 'Bewerbungen gesamt' : 'Total Applications'}>
              <p data-testid="kpi-total" className="text-2xl font-bold text-[var(--color-text-primary)]">{totalApps}</p>
            </InfoCard>
            <InfoCard title={lang === 'de' ? 'Eingeschrieben' : 'Enrolled'}>
              <p data-testid="kpi-enrolled" className="text-2xl font-bold text-[#10B981]">{enrolled}</p>
            </InfoCard>
            <InfoCard title={lang === 'de' ? 'In Bearbeitung' : 'In Progress'}>
              <p data-testid="kpi-active" className="text-2xl font-bold text-[var(--color-primary)]">{inProgress}</p>
            </InfoCard>
            <InfoCard title={lang === 'de' ? 'Conversion-Rate' : 'Conversion Rate'}>
              <p data-testid="kpi-conversion" className="text-2xl font-bold text-[var(--color-accent)]">{conversionRate}%</p>
            </InfoCard>
          </div>

          {/* Charts: Bar + Pie side by side */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 mb-6">
            <InfoCard title={lang === 'de' ? 'Pipeline-Uebersicht' : 'Pipeline Overview'} className="lg:col-span-3">
              <div data-testid="pipeline-bar-chart" style={{ width: '100%', height: 280 }}>
                <ResponsiveContainer>
                  <BarChart data={pipelineData} margin={{ top: 8, right: 8, left: -16, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-divider-subtle)" />
                    <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'var(--color-text-tertiary)' }} interval={0} angle={-30} textAnchor="end" height={50} />
                    <YAxis tick={{ fontSize: 10, fill: 'var(--color-text-tertiary)' }} allowDecimals={false} />
                    <Tooltip
                      contentStyle={{ background: 'var(--color-surface-elevated)', border: '1px solid var(--color-divider)', borderRadius: 'var(--radius-sm)', fontSize: 12 }}
                      labelStyle={{ fontWeight: 600, color: 'var(--color-text-primary)' }}
                    />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]} name={lang === 'de' ? 'Anzahl' : 'Count'}>
                      {pipelineData.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </InfoCard>
            <InfoCard title={lang === 'de' ? 'Verteilung' : 'Distribution'} className="lg:col-span-2">
              <div data-testid="pipeline-pie-chart" style={{ width: '100%', height: 280 }}>
                {pieData.length > 0 ? (
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="45%" outerRadius={80} innerRadius={40} paddingAngle={2}>
                        {pieData.map((entry, i) => (
                          <Cell key={i} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ background: 'var(--color-surface-elevated)', border: '1px solid var(--color-divider)', borderRadius: 'var(--radius-sm)', fontSize: 12 }} />
                      <Legend wrapperStyle={{ fontSize: 10 }} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Keine Daten' : 'No data'}</div>
                )}
              </div>
            </InfoCard>
          </div>

          {/* System Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
            <InfoCard title={lang === 'de' ? 'Aufgaben' : 'Tasks'}>
              <div className="flex items-center gap-2">
                <Table2 size={14} className="text-[var(--color-text-secondary)]" />
                <span className="text-sm">{stats?.open_tasks || 0} {lang === 'de' ? 'gesamt' : 'total'}</span>
              </div>
            </InfoCard>
            <InfoCard title={lang === 'de' ? 'Nachrichten' : 'Messages'}>
              <div className="flex items-center gap-2">
                <MessageSquare size={14} className="text-[var(--color-text-secondary)]" />
                <span className="text-sm">{stats?.unread_messages || 0} {lang === 'de' ? 'gesamt' : 'total'}</span>
              </div>
            </InfoCard>
            <InfoCard title={lang === 'de' ? 'Benutzer' : 'Users'}>
              <div className="flex items-center gap-2">
                <Users size={14} className="text-[var(--color-text-secondary)]" />
                <span className="text-sm">{stats?.total_users || 0} {lang === 'de' ? 'gesamt' : 'total'}</span>
              </div>
            </InfoCard>
          </div>

          {/* Export */}
          <InfoCard title={lang === 'de' ? 'Daten exportieren' : 'Export Data'}>
            <div className="flex items-center gap-3 mt-1">
              <select data-testid="export-filter" value={period} onChange={e => setPeriod(e.target.value)}
                className="text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2 bg-white">
                <option value="all">{lang === 'de' ? 'Alle Bewerbungen' : 'All Applications'}</option>
                <option value="enrolled">{lang === 'de' ? 'Nur Eingeschriebene' : 'Enrolled Only'}</option>
                <option value="in_review">{lang === 'de' ? 'Nur In Bearbeitung' : 'In Review Only'}</option>
                <option value="pending_docs">{lang === 'de' ? 'Nur Dokumente ausstehend' : 'Pending Docs Only'}</option>
                <option value="declined">{lang === 'de' ? 'Nur Abgelehnte' : 'Declined Only'}</option>
              </select>
              <button data-testid="export-csv-btn" onClick={handleExport} disabled={exporting}
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-[var(--color-primary)] rounded-[var(--radius-sm)] hover:opacity-90 disabled:opacity-50 transition-opacity">
                {exporting ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                CSV Export
              </button>
            </div>
          </InfoCard>
        </>
      )}
    </PageScaffold>
  );
}
