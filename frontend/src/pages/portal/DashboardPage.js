import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';
import { FileText, MessageSquare, CreditCard, CheckCircle, Clock, AlertCircle, BookOpen } from 'lucide-react';
import { STAGE_LABELS } from '../../lib/utils';


export default function DashboardPage() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [summary, setSummary] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const locale = i18n.language === 'en' ? 'en-GB' : 'de-DE';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, appsRes] = await Promise.all([
          apiClient.get(`/api/dashboard/stats`, { withCredentials: true }),
          apiClient.get(`/api/applications`, { withCredentials: true }),
        ]);
        setStats(statsRes.data);
        setApplications(appsRes.data);
        if (user?.role === 'applicant') {
          const summaryRes = await apiClient.get('/api/dashboard/applicant-summary', { withCredentials: true });
          setSummary(summaryRes.data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user?.role]);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  );

  const activeApp = applications[0];
  const stage = activeApp?.current_stage;
  const docsValue = summary
    ? `${summary.documents?.missing || 0}/${summary.documents?.in_review || 0}/${summary.documents?.accepted || 0}`
    : '–';
  const messagesValue = summary
    ? `${summary.messages?.unread || 0}/${summary.messages?.open || 0}`
    : '–';
  const financialsValue = summary
    ? `${summary.financials?.open_invoices || 0}/${summary.financials?.paid || 0}`
    : '–';
  const nextActions = summary?.tasks?.next_actions || [];

  return (
    <div className="space-y-6 animate-fade-in" data-testid="applicant-dashboard">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">
          {t('portal.welcome')}, {user?.full_name?.split(' ')[0] || user?.email}
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          {new Date().toLocaleDateString(locale, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Status card */}
      {activeApp && (
        <div className="bg-primary rounded-sm p-6 text-white" data-testid="dashboard-status-card">
          <p className="text-white/70 text-sm mb-1">{t('portal.current_status')}</p>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-heading font-bold">{STAGE_LABELS[stage] || stage}</h2>
              <p className="text-white/70 text-sm mt-1">{t('portal.application_id')} #{activeApp.id?.slice(-6).toUpperCase()}</p>
            </div>
            <span className="text-xs font-semibold px-3 py-1.5 rounded-sm bg-white/20 text-white">
              {STAGE_LABELS[stage] || stage}
            </span>
          </div>
        </div>
      )}

      {/* No application state */}
      {!activeApp && (
        <div className="bg-slate-50 border border-slate-100 rounded-sm p-6 text-center" data-testid="dashboard-no-app">
          <BookOpen size={32} className="text-primary mx-auto mb-3" />
          <h3 className="font-semibold text-primary mb-2">{t('portal.no_application_title')}</h3>
          <p className="text-slate-600 text-sm mb-4">{t('portal.no_application_desc')}</p>
          <Link to="/apply" className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover transition-colors" data-testid="dashboard-apply-btn">
            {t('portal.apply_now')}
          </Link>
        </div>
      )}

      {/* Quick stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { icon: FileText, label: t('portal.docs_label'), value: docsValue, hint: 'fehlend / in Prüfung / akzeptiert', path: '/portal/documents', testid: 'dash-docs' },
          { icon: MessageSquare, label: t('portal.messages_label'), value: messagesValue, hint: 'ungelesen / offen', path: '/portal/messages', testid: 'dash-messages' },
          { icon: CreditCard, label: t('portal.invoices_label'), value: financialsValue, hint: 'offen / bezahlt', path: '/portal/financials', testid: 'dash-financials' },
          { icon: CheckCircle, label: t('portal.tasks_label'), value: (summary?.tasks?.open ?? stats?.open_tasks ?? '0'), hint: 'offene Aufgaben', path: '/portal/journey', testid: 'dash-tasks' },
        ].map(item => {
          const Icon = item.icon;
          return (
            <Link key={item.testid} to={item.path} data-testid={item.testid}
              className="bg-white border border-slate-200 rounded-sm p-4 hover:border-primary/30 hover:-translate-y-0.5 transition-all">
              <div className="flex items-center gap-2 mb-2">
                <Icon size={16} className="text-primary" />
                <span className="text-xs font-medium text-slate-500">{item.label}</span>
              </div>
              <p className="text-xl font-heading font-bold text-slate-800">{item.value}</p>
              {item.hint && <p className="text-[10px] text-slate-400 mt-1">{item.hint}</p>}
            </Link>
          );
        })}
      </div>

      {/* Next step */}
      <div className="bg-white border border-slate-200 rounded-sm p-5" data-testid="dashboard-next-step">
        <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <Clock size={16} className="text-primary" />
          {t('portal.next_step')}
        </h3>
        {nextActions.length > 0 ? (
          <div className="space-y-2">
            {nextActions.map((action, idx) => (
              <NextStepItem key={`${action.type}-${idx}`} t={t} text={action.title} />
            ))}
          </div>
        ) : stage ? (
          <div className="space-y-2">
            <NextStepItem stage={stage} t={t} />
          </div>
        ) : (
          <p className="text-slate-500 text-sm">{t('portal.no_tasks')}</p>
        )}
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Link to="/portal/documents"
          className="flex items-center gap-3 bg-white border border-slate-200 rounded-sm p-4 hover:border-primary/30 transition-colors"
          data-testid="dash-action-docs">
          <div className="w-9 h-9 bg-primary/10 rounded-sm flex items-center justify-center">
            <FileText size={18} className="text-primary" />
          </div>
          <div>
            <p className="font-medium text-slate-800 text-sm">{t('portal.upload_action')}</p>
            <p className="text-slate-500 text-xs">{t('portal.upload_action_desc')}</p>
          </div>
        </Link>
        <Link to="/portal/messages"
          className="flex items-center gap-3 bg-white border border-slate-200 rounded-sm p-4 hover:border-primary/30 transition-colors"
          data-testid="dash-action-msg">
          <div className="w-9 h-9 bg-primary/10 rounded-sm flex items-center justify-center">
            <MessageSquare size={18} className="text-primary" />
          </div>
          <div>
            <p className="font-medium text-slate-800 text-sm">{t('portal.send_message')}</p>
            <p className="text-slate-500 text-xs">{t('portal.send_message_desc')}</p>
          </div>
        </Link>
      </div>
    </div>
  );
}

function NextStepItem({ stage, text, t }) {
  const resolvedText = text || t(`portal.steps.${stage}`, { defaultValue: t('portal.steps.default') });
  return (
    <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-sm border border-slate-200">
      <AlertCircle size={16} className="text-primary mt-0.5 shrink-0" />
      <p className="text-slate-700 text-sm">{resolvedText}</p>
    </div>
  );
}
