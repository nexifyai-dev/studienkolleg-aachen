import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';
import { FileText, MessageSquare, CheckCircle, Clock, AlertCircle, BookOpen, Shield, CalendarClock, RefreshCcw } from 'lucide-react';
import { STAGE_LABELS } from '../../lib/utils';


export default function DashboardPage() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const locale = i18n.language === 'en' ? 'en-GB' : 'de-DE';

  const fetchData = async () => {
    setError(false);
    setLoading(true);
    try {
      const [statsRes, appsRes] = await Promise.all([
        apiClient.get(`/api/dashboard/stats`, { withCredentials: true }),
        apiClient.get(`/api/applications`, { withCredentials: true }),
      ]);
      setStats(statsRes.data);
      setApplications(appsRes.data);
    } catch (e) {
      console.error(e);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  );

  const activeApp = applications[0];
  const stage = activeApp?.current_stage;
  const needs = buildNeeds({ stats, stage });
  const nextSteps = buildNextSteps({ stage, needs, t });
  const quickActions = buildQuickActions({ needs, t });

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

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-sm p-4 flex items-start justify-between gap-3" data-testid="dashboard-error-state">
          <div>
            <p className="text-sm font-semibold text-red-700">{t('portal.dashboard_error_title')}</p>
            <p className="text-xs text-red-600 mt-1">{t('portal.dashboard_error_desc')}</p>
          </div>
          <button
            onClick={fetchData}
            className="bg-white border border-red-200 text-red-700 px-3 py-2 rounded-sm text-xs font-medium hover:bg-red-50 inline-flex items-center gap-1.5"
            data-testid="dashboard-retry-btn"
          >
            <RefreshCcw size={12} />
            {t('portal.retry')}
          </button>
        </div>
      )}

      {/* Quick stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { icon: FileText, label: t('portal.docs_need_label'), value: stats?.missing_documents ?? 0, path: '/portal/documents', testid: 'dash-docs' },
          { icon: MessageSquare, label: t('portal.messages_need_label'), value: stats?.unread_messages ?? 0, path: '/portal/messages', testid: 'dash-messages' },
          { icon: CheckCircle, label: t('portal.tasks_need_label'), value: stats?.open_tasks ?? 0, path: '/portal/journey', testid: 'dash-tasks' },
          { icon: Shield, label: t('portal.consent_need_label'), value: stats?.consent_missing ? t('portal.consent_required_short') : t('portal.ok_short'), path: '/portal/consents', testid: 'dash-consent' },
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
        {nextSteps.length > 0 ? (
          <div className="space-y-2">
            {nextSteps.map((item) => (
              <NextStepItem key={item.key} item={item} t={t} />
            ))}
          </div>
        ) : (
          <div className="bg-slate-50 border border-slate-200 rounded-sm p-4" data-testid="dashboard-next-step-empty">
            <p className="text-slate-500 text-sm">{t('portal.next_step_empty')}</p>
            <Link to="/apply" className="mt-3 inline-flex text-xs font-semibold text-primary hover:text-primary-hover">
              {t('portal.apply_now')}
            </Link>
          </div>
        )}
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {quickActions.length > 0 ? quickActions.map((action) => {
          const Icon = action.icon;
          return (
            <Link
              key={action.key}
              to={action.path}
              className="flex items-center gap-3 bg-white border border-slate-200 rounded-sm p-4 hover:border-primary/30 transition-colors"
              data-testid={`dash-action-${action.key}`}
            >
              <div className="w-9 h-9 bg-primary/10 rounded-sm flex items-center justify-center">
                <Icon size={18} className="text-primary" />
              </div>
              <div>
                <p className="font-medium text-slate-800 text-sm">{action.title}</p>
                <p className="text-slate-500 text-xs">{action.desc}</p>
              </div>
            </Link>
          );
        }) : (
          <div className="sm:col-span-2 bg-slate-50 border border-slate-200 rounded-sm p-4" data-testid="dashboard-actions-empty">
            <p className="text-sm text-slate-600">{t('portal.actions_empty')}</p>
            <Link to="/portal/journey" className="mt-3 inline-flex text-xs font-semibold text-primary hover:text-primary-hover">
              {t('portal.open_journey')}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

function buildNeeds({ stats, stage }) {
  return {
    missingDocuments: stats?.missing_documents || 0,
    unreadMessages: stats?.unread_messages || 0,
    openTasks: stats?.open_tasks || 0,
    consentMissing: Boolean(stats?.consent_missing),
    dueSoonTasks: stats?.due_soon_tasks || 0,
    stage,
  };
}

function buildNextSteps({ stage, needs, t }) {
  if (!stage) return [];
  const list = [];

  if (needs.missingDocuments > 0) {
    list.push({
      key: 'docs-now',
      priority: 'now',
      text: t('portal.steps.docs_requested'),
      ctaLabel: t('portal.upload_action'),
      path: '/portal/documents',
    });
  }
  if (needs.unreadMessages > 0) {
    list.push({
      key: 'msg-now',
      priority: 'now',
      text: t('portal.steps.contacted'),
      ctaLabel: t('portal.reply_now'),
      path: '/portal/messages',
    });
  }
  if (needs.consentMissing) {
    list.push({
      key: 'consent-now',
      priority: 'now',
      text: t('portal.steps.consent_required'),
      ctaLabel: t('portal.grant_consent_action'),
      path: '/portal/consents',
    });
  }
  if (needs.dueSoonTasks > 0) {
    list.push({
      key: 'tasks-soon',
      priority: 'soon',
      text: t('portal.steps.tasks_due_soon', { count: needs.dueSoonTasks }),
      ctaLabel: t('portal.open_journey'),
      path: '/portal/journey',
    });
  }

  list.push({
    key: `stage-${stage}`,
    priority: list.length === 0 ? 'now' : 'info',
    text: t(`portal.steps.${stage}`, { defaultValue: t('portal.steps.default') }),
    ctaLabel: stage === 'process_next' ? t('portal.schedule_action') : t('portal.open_journey'),
    path: stage === 'process_next' ? '/portal/messages' : '/portal/journey',
  });

  const priorityWeight = { now: 0, soon: 1, info: 2 };
  return list.sort((a, b) => priorityWeight[a.priority] - priorityWeight[b.priority]);
}

function buildQuickActions({ needs, t }) {
  const actions = [];
  if (needs.missingDocuments > 0) {
    actions.push({ key: 'docs', icon: FileText, path: '/portal/documents', title: t('portal.upload_action'), desc: t('portal.quick_docs_desc', { count: needs.missingDocuments }) });
  }
  if (needs.unreadMessages > 0) {
    actions.push({ key: 'messages', icon: MessageSquare, path: '/portal/messages', title: t('portal.reply_now'), desc: t('portal.quick_messages_desc', { count: needs.unreadMessages }) });
  }
  if (needs.consentMissing) {
    actions.push({ key: 'consent', icon: Shield, path: '/portal/consents', title: t('portal.grant_consent_action'), desc: t('portal.quick_consent_desc') });
  }
  if (needs.stage === 'process_next' || needs.stage === 'payment_received') {
    actions.push({ key: 'appointment', icon: CalendarClock, path: '/portal/messages', title: t('portal.schedule_action'), desc: t('portal.quick_appointment_desc') });
  }
  return actions.slice(0, 4);
}

function NextStepItem({ item, t }) {
  const badgeClass = item.priority === 'now'
    ? 'bg-red-50 text-red-700 border-red-100'
    : item.priority === 'soon'
    ? 'bg-amber-50 text-amber-700 border-amber-100'
    : 'bg-slate-100 text-slate-600 border-slate-200';
  return (
    <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-sm border border-slate-200">
      <AlertCircle size={16} className="text-primary mt-0.5 shrink-0" />
      <div className="space-y-2 flex-1">
        <div className="flex items-center justify-between gap-3">
          <span className={`text-[10px] font-semibold px-2 py-0.5 border rounded-sm ${badgeClass}`}>
            {t(`portal.priority.${item.priority}`)}
          </span>
          <Link to={item.path} className="text-xs font-semibold text-primary hover:text-primary-hover">
            {item.ctaLabel}
          </Link>
        </div>
        <p className="text-slate-700 text-sm">{item.text}</p>
      </div>
    </div>
  );
}
