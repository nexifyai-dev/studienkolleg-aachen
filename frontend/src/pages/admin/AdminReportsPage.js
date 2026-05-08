import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api-hooks';
import { BarChart3, Users, FileText, TrendingUp, Loader2, Clock } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';

function useAdminStats() {
  return useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: () => api.get('/dashboard/stats').then(r => r.data),
    staleTime: 30000,
  });
}

function useApplications() {
  return useQuery({
    queryKey: ['admin', 'applications'],
    queryFn: () => api.get('/applications').then(r => r.data),
    staleTime: 30000,
  });
}

export default function AdminReportsPage() {
  const { data: stats, isLoading: loadingStats } = useAdminStats();
  const { data: apps, isLoading: loadingApps } = useApplications();

  if (loadingStats || loadingApps) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-[var(--color-primary)]" />
    </div>
  );

  const stageDistribution = {};
  (apps || []).forEach(a => {
    const stage = a.current_stage || 'unknown';
    stageDistribution[stage] = (stageDistribution[stage] || 0) + 1;
  });

  const totalApps = (apps || []).length;
  const sortedStages = Object.entries(stageDistribution).sort((a, b) => b[1] - a[1]);

  return (
    <PageScaffold
      title="Reporting"
      subtitle="Systemweite Auswertungen und Pipeline-Analysen"
      testId="admin-reports-page"
    >
      {/* KPI-Karten */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { icon: <Users size={14} />, label: 'Bewerbungen gesamt', value: totalApps, color: 'var(--color-primary)' },
          { icon: <FileText size={14} />, label: 'Rechnungen', value: stats?.total_invoices ?? 0, color: 'var(--color-accent)' },
          { icon: <Clock size={14} />, label: 'Offene Aufgaben', value: stats?.open_tasks ?? 0, color: 'var(--color-warning)' },
          { icon: <TrendingUp size={14} />, label: 'Benutzer', value: stats?.total_users ?? 0, color: 'var(--color-success)' },
        ].map((kpi, i) => (
          <Card key={i} data-testid={`kpi-card-${i}`}>
            <CardContent className="px-4 py-3">
              <div className="flex items-center gap-1.5 mb-1">
                <span style={{ color: kpi.color }}>{kpi.icon}</span>
                <span className="text-[10px] uppercase tracking-[0.12em] text-[var(--color-text-tertiary)]">{kpi.label}</span>
              </div>
              <p className="text-xl font-bold text-[var(--color-text-primary)]">{kpi.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Pipeline-Verteilung */}
      <Card data-testid="pipeline-report">
        <CardContent className="px-5 py-4">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 size={14} className="text-[var(--color-primary)]" />
            <span className="text-xs font-semibold text-[var(--color-text-primary)]">Pipeline-Verteilung</span>
          </div>
          <div className="space-y-2">
            {sortedStages.map(([stage, count]) => {
              const pct = totalApps > 0 ? Math.round((count / totalApps) * 100) : 0;
              return (
                <div key={stage} className="flex items-center gap-3" data-testid={`pipeline-${stage}`}>
                  <span className="text-xs text-[var(--color-text-secondary)] w-32 truncate">{stage.replace(/_/g, ' ')}</span>
                  <div className="flex-1 h-5 bg-[var(--color-surface-sunken)] rounded-[var(--radius-full)] overflow-hidden">
                    <div
                      className="h-full bg-[var(--color-primary)] rounded-[var(--radius-full)] transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="text-xs font-semibold text-[var(--color-text-primary)] w-12 text-right">{count} ({pct}%)</span>
                </div>
              );
            })}
            {sortedStages.length === 0 && (
              <p className="text-xs text-[var(--color-text-tertiary)] text-center py-4">Keine Daten vorhanden</p>
            )}
          </div>
        </CardContent>
      </Card>
    </PageScaffold>
  );
}
