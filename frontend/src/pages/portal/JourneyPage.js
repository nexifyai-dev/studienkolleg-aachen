import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { CheckCircle, Circle, Loader2, ArrowRight, Info } from 'lucide-react';
import { getStageLabel, getLang } from '../../lib/utils';
import StatusCockpit from '../../components/portal/StatusCockpit';
import KnowledgeBox from '../../components/portal/KnowledgeBox';
import { getStageKnowledge } from '../../lib/portalKnowledge';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';

const ALL_STAGES = [
  'lead_new', 'contacted', 'pending_docs', 'docs_received',
  'in_review', 'interview_scheduled', 'conditional_offer',
  'enrolled', 'completed',
];

export default function JourneyPage() {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get('/api/applications', { withCredentials: true })
      .then(r => {
        const data = r.data;
        setApplications(Array.isArray(data) ? data : (data.applications || []));
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="w2g-loading"><div className="w2g-spinner" /><p className="w2g-loading-text">{lang === 'de' ? 'Wird geladen...' : 'Loading...'}</p></div>;

  const activeApp = applications[0];
  const stage = activeApp?.current_stage || '';
  const stageIdx = ALL_STAGES.indexOf(stage);
  const stageInfo = stage ? getStageKnowledge(stage, lang) : null;

  return (
    <PageScaffold
      title={lang === 'de' ? 'Bewerbungsstatus' : 'Application Status'}
      subtitle={lang === 'de' ? 'Verfolge den Fortschritt deiner Bewerbung' : 'Track your application progress'}
      testId="journey-page"
    >
      {applications.length === 0 ? (
        <div className="w2g-empty" data-testid="journey-empty">
          <Circle size={32} className="w2g-empty-icon" />
          <p className="w2g-empty-text">
            {lang === 'de' ? 'Noch keine aktive Bewerbung' : 'No active application yet'}
          </p>
        </div>
      ) : (
        <>
          {activeApp && <StatusCockpit stage={stage} applicationId={activeApp.id} lang={lang} />}

          {activeApp && (
            <Card data-testid="journey-timeline">
              <CardContent className="px-5 py-5">
                <h3 className="text-sm font-bold text-[var(--color-text-primary)] mb-5">
                  {lang === 'de' ? 'Bewerbungsverlauf' : 'Application Timeline'}
                </h3>
                <div className="relative">
                  {ALL_STAGES.map((s, idx) => {
                    const isComplete = stageIdx >= 0 && idx < stageIdx;
                    const isCurrent = s === stage;
                    const isFuture = stageIdx >= 0 ? idx > stageIdx : true;

                    return (
                      <div key={s} className="flex gap-4 relative" data-testid={`journey-stage-${s}`}>
                        {/* Vertikale Verbindungslinie */}
                        <div className="flex flex-col items-center" style={{ width: 32 }}>
                          {/* Kreis */}
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 transition-all duration-300 ${
                            isComplete
                              ? 'bg-[var(--color-primary)] shadow-sm'
                              : isCurrent
                                ? 'bg-white border-[3px] border-[var(--color-primary)] shadow-md shadow-[var(--color-primary)]/20'
                                : 'bg-[var(--color-surface-sunken)] border-2 border-[var(--color-divider)]'
                          }`}>
                            {isComplete ? (
                              <CheckCircle size={16} className="text-white" strokeWidth={2.5} />
                            ) : isCurrent ? (
                              <div className="w-3 h-3 rounded-full bg-[var(--color-primary)] animate-pulse" />
                            ) : (
                              <Circle size={14} className="text-[var(--color-divider)]" />
                            )}
                          </div>
                          {/* Linie zum naechsten */}
                          {idx < ALL_STAGES.length - 1 && (
                            <div className={`w-0.5 flex-1 min-h-[28px] mt-1 mb-1 rounded-full transition-colors ${
                              isComplete ? 'bg-[var(--color-primary)]' : 'bg-[var(--color-divider)]'
                            }`} />
                          )}
                        </div>

                        {/* Label + Beschreibung */}
                        <div className={`pb-5 flex-1 ${idx === ALL_STAGES.length - 1 ? 'pb-0' : ''}`}>
                          <p className={`text-sm leading-tight transition-colors ${
                            isComplete
                              ? 'text-[var(--color-text-primary)] font-medium'
                              : isCurrent
                                ? 'text-[var(--color-primary)] font-bold text-base'
                                : 'text-[var(--color-text-tertiary)] font-normal'
                          }`}>
                            {getStageLabel(s, lang)}
                          </p>
                          {isCurrent && (
                            <div className="flex items-center gap-1.5 mt-1">
                              <ArrowRight size={11} className="text-[var(--color-primary)]" />
                              <span className="text-xs font-semibold text-[var(--color-primary)]">
                                {lang === 'de' ? 'Aktueller Schritt' : 'Current step'}
                              </span>
                            </div>
                          )}
                          {isComplete && (
                            <p className="text-[10px] text-[var(--color-success)] mt-0.5 font-medium">
                              {lang === 'de' ? 'Abgeschlossen' : 'Completed'}
                            </p>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {stageInfo?.knowledgeLinks?.length > 0 && (
            <KnowledgeBox
              title={lang === 'de' ? 'Passende Informationen' : 'Relevant Information'}
              links={[
                ...(stageInfo.knowledgeLinks || []),
                { label: 'Studienkollegs.de', url: 'https://www.studienkollegs.de/', source: lang === 'de' ? 'Offiziell' : 'Official' },
              ]}
              lang={lang}
            />
          )}
        </>
      )}
    </PageScaffold>
  );
}
