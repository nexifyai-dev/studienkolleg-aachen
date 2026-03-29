import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { FileText, MessageSquare, CreditCard, CheckCircle, Clock, AlertCircle, BookOpen } from 'lucide-react';
import { STAGE_LABELS, STAGE_COLORS } from '../../lib/utils';

const API = process.env.REACT_APP_BACKEND_URL;

export default function DashboardPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, appsRes] = await Promise.all([
          axios.get(`${API}/api/dashboard/stats`, { withCredentials: true }),
          axios.get(`${API}/api/applications`, { withCredentials: true }),
        ]);
        setStats(statsRes.data);
        setApplications(appsRes.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  );

  const activeApp = applications[0];
  const stage = activeApp?.current_stage;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="applicant-dashboard">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">
          {t('portal.welcome')}, {user?.full_name?.split(' ')[0] || user?.email}
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          {new Date().toLocaleDateString('de-DE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Status card */}
      {activeApp && (
        <div className="bg-primary rounded-sm p-6 text-white" data-testid="dashboard-status-card">
          <p className="text-blue-200 text-sm mb-1">Dein aktueller Status</p>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-heading font-bold">{STAGE_LABELS[stage] || stage}</h2>
              <p className="text-blue-200 text-sm mt-1">Bewerbung #{activeApp.id?.slice(-6).toUpperCase()}</p>
            </div>
            <span className={`text-xs font-semibold px-3 py-1.5 rounded-sm bg-white/20 text-white`}>
              {STAGE_LABELS[stage] || stage}
            </span>
          </div>
        </div>
      )}

      {/* No application state */}
      {!activeApp && (
        <div className="bg-blue-50 border border-blue-100 rounded-sm p-6 text-center" data-testid="dashboard-no-app">
          <BookOpen size={32} className="text-primary mx-auto mb-3" />
          <h3 className="font-semibold text-primary mb-2">Noch keine Bewerbung</h3>
          <p className="text-slate-600 text-sm mb-4">Starte jetzt deinen Bewerbungsprozess.</p>
          <Link to="/apply" className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary-hover transition-colors">
            Jetzt bewerben
          </Link>
        </div>
      )}

      {/* Quick stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { icon: FileText, label: 'Dokumente', value: '–', path: '/portal/documents', testid: 'dash-docs' },
          { icon: MessageSquare, label: 'Nachrichten', value: '–', path: '/portal/messages', testid: 'dash-messages' },
          { icon: CreditCard, label: 'Rechnungen', value: '–', path: '/portal/financials', testid: 'dash-financials' },
          { icon: CheckCircle, label: 'Aufgaben', value: stats?.open_tasks || '0', path: '/portal/journey', testid: 'dash-tasks' },
        ].map(item => {
          const Icon = item.icon;
          return (
            <Link key={item.label} to={item.path} data-testid={item.testid}
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
        {stage ? (
          <div className="space-y-2">
            <NextStepItem stage={stage} />
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
          <div className="w-9 h-9 bg-accent/30 rounded-sm flex items-center justify-center">
            <FileText size={18} className="text-primary" />
          </div>
          <div>
            <p className="font-medium text-slate-800 text-sm">Dokument hochladen</p>
            <p className="text-slate-500 text-xs">Lade deine Unterlagen sicher hoch</p>
          </div>
        </Link>
        <Link to="/portal/messages"
          className="flex items-center gap-3 bg-white border border-slate-200 rounded-sm p-4 hover:border-primary/30 transition-colors"
          data-testid="dash-action-msg">
          <div className="w-9 h-9 bg-accent/30 rounded-sm flex items-center justify-center">
            <MessageSquare size={18} className="text-primary" />
          </div>
          <div>
            <p className="font-medium text-slate-800 text-sm">Nachricht senden</p>
            <p className="text-slate-500 text-xs">Direkt mit dem Team kommunizieren</p>
          </div>
        </Link>
      </div>
    </div>
  );
}

function NextStepItem({ stage }) {
  const steps = {
    lead_new: 'Deine Bewerbung ist eingegangen. Wir melden uns in Kürze.',
    contacted: 'Wir haben dich kontaktiert. Bitte antworte auf unsere Nachrichten.',
    docs_requested: 'Bitte lade die angeforderten Dokumente hoch.',
    docs_received: 'Deine Dokumente sind eingegangen. Wir prüfen sie.',
    docs_review: 'Deine Dokumente werden aktuell geprüft. Bitte habe etwas Geduld.',
    invoice_open: 'Du hast eine offene Rechnung. Bitte prüfe deine Zahlungen.',
    payment_received: 'Deine Zahlung ist bestätigt. Nächste Schritte folgen.',
    process_next: 'Wir begleiten dich zu den nächsten Schritten (Visum, Kurs, Bewerbung).',
    completed: 'Dein Prozess ist abgeschlossen. Herzlichen Glückwunsch!',
  };
  const text = steps[stage] || 'Warte auf die nächste Information von uns.';
  return (
    <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-sm border border-blue-100">
      <AlertCircle size={16} className="text-blue-600 mt-0.5 shrink-0" />
      <p className="text-blue-800 text-sm">{text}</p>
    </div>
  );
}
