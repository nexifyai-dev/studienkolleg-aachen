import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';
import { FileText, MessageSquare, CreditCard, Bell, BookOpen, Loader2, ChevronRight } from 'lucide-react';
import StatusCockpit from '../../components/portal/StatusCockpit';
import ChecklistPanel from '../../components/portal/ChecklistPanel';
import KnowledgeBox from '../../components/portal/KnowledgeBox';
import { generateChecklist, getStageKnowledge } from '../../lib/portalKnowledge';
import { PageScaffold } from '../../components/layout/PageScaffold';

/* shadcn-Komponenten */
import { Card, CardContent } from '../../components/ui/card';

/* ──────────────────────────────────────────────────────────────
   QUICK-STAT KARTE (shadcn Card + Badge)
   ────────────────────────────────────────────────────────────── */
function QuickStatCard({ icon: Icon, label, value, path, testid, alert }) {
  return (
    <Link to={path} data-testid={testid} className="group">
      <Card className="relative hover:shadow-[var(--shadow-e2)] transition-shadow duration-200 border-l-[3px] border-l-[var(--color-primary)]">
        {alert && <span className="absolute top-3 right-3 w-2 h-2 bg-[var(--color-danger)] rounded-full ring-2 ring-[var(--color-surface)] animate-pulse" />}
        <CardContent className="px-4 py-4">
          <div className="flex items-center gap-2 mb-2.5">
            <div className="w-8 h-8 rounded-[var(--radius-sm)] flex items-center justify-center bg-[var(--color-primary-muted)]">
              <Icon size={15} className="text-[var(--color-primary)]" />
            </div>
            <span className="text-[11px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-[0.06em]">{label}</span>
          </div>
          <p className="text-lg font-extrabold text-[var(--color-text-primary)] tabular-nums leading-none" style={{ fontFamily: 'var(--font-heading)' }}>{value}</p>
        </CardContent>
      </Card>
    </Link>
  );
}

/* ──────────────────────────────────────────────────────────────
   QUICK-ACTION KARTE (shadcn Card)
   ────────────────────────────────────────────────────────────── */
function QuickActionCard({ to, icon: Icon, title, desc, testid }) {
  return (
    <Link to={to} data-testid={testid} className="group">
      <Card className="hover:shadow-[var(--shadow-e2)] transition-shadow duration-200">
        <CardContent className="px-4 py-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center shrink-0 transition-colors">
            <Icon size={18} className="text-[var(--color-primary)]" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-[var(--color-text-primary)] group-hover:text-[var(--color-primary)] transition-colors">{title}</p>
            <p className="text-[10px] text-[var(--color-text-tertiary)] mt-0.5">{desc}</p>
          </div>
          <ChevronRight size={14} className="text-[var(--color-text-tertiary)] opacity-0 group-hover:opacity-100 transition-opacity" />
        </CardContent>
      </Card>
    </Link>
  );
}

/* ══════════════════════════════════════════════════════════════
   BEWERBER-DASHBOARD – HAUPTKOMPONENTE
   ══════════════════════════════════════════════════════════════ */
export default function DashboardPage() {
  const { i18n } = useTranslation();
  const { user } = useAuth();
  const [applications, setApplications] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const lang = i18n.language === 'en' ? 'en' : 'de';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [appsRes, docsRes, invRes, convRes] = await Promise.all([
          apiClient.get('/api/applications', { withCredentials: true }),
          apiClient.get('/api/documents/my', { withCredentials: true }).catch(() => ({ data: [] })),
          apiClient.get('/api/invoices/my', { withCredentials: true }).catch(() => ({ data: [] })),
          apiClient.get('/api/conversations', { withCredentials: true }).catch(() => ({ data: [] })),
        ]);
        setApplications(appsRes.data || []);
        setDocuments(docsRes.data || []);
        setInvoices(invRes.data || []);
        const convData = convRes.data;
        setConversations(convData.conversations || convData || []);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    };
    fetchData();
  }, []);

  /* ── LOADING STATE ─────────────────────────────────────── */
  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]" data-testid="portal-dashboard-loading">
      <div className="text-center space-y-3">
        <Loader2 size={32} className="animate-spin text-[var(--color-primary)] mx-auto" />
        <p className="text-sm font-medium text-[var(--color-text-secondary)]">
          {lang === 'de' ? 'Dein Portal wird geladen...' : 'Loading your portal...'}
        </p>
      </div>
    </div>
  );

  const activeApp = applications[0];
  const stage = activeApp?.current_stage;
  const stageInfo = stage ? getStageKnowledge(stage, lang) : null;
  const checklist = activeApp ? generateChecklist(activeApp, documents, invoices, lang) : [];
  const openTasks = checklist.filter(i => i.status !== 'done').length;
  const unreadMessages = conversations.reduce((acc, c) => acc + (c.unread_count || 0), 0);
  const openInvoices = invoices.filter(i => i.status === 'open' || i.status === 'overdue').length;

  /* ── RENDER ────────────────────────────────────────────── */
  return (
    <PageScaffold
      title={`${lang === 'de' ? 'Willkommen' : 'Welcome'}, ${user?.full_name?.split(' ')[0] || user?.email}`}
      subtitle={new Date().toLocaleDateString(lang === 'en' ? 'en-GB' : 'de-DE',
        { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
      testId="applicant-dashboard"
    >

      {/* ═══ KEINE BEWERBUNG ═══════════════════════════════ */}
      {!activeApp && (
        <Card data-testid="dashboard-no-app">
          <CardContent className="py-12 text-center">
            <BookOpen size={32} className="mx-auto mb-3 text-[var(--color-primary)]" />
            <h3 className="font-bold text-[var(--color-primary)] mb-2 text-sm" style={{ fontFamily: 'var(--font-heading)' }}>
              {lang === 'de' ? 'Noch keine Bewerbung' : 'No application yet'}
            </h3>
            <p className="text-xs text-[var(--color-text-secondary)] mb-4">
              {lang === 'de'
                ? 'Starte jetzt deine Bewerbung beim Studienkolleg Aachen.'
                : 'Start your application at Studienkolleg Aachen now.'}
            </p>
            <Link to="/apply" className="w2g-btn-primary" data-testid="dashboard-apply-btn">
              {lang === 'de' ? 'Jetzt bewerben' : 'Apply Now'}
            </Link>
          </CardContent>
        </Card>
      )}

      {/* ═══ STATUS COCKPIT ════════════════════════════════ */}
      {activeApp && (
        <>
          {activeApp.applicant_number && (
            <div className="flex items-center gap-2 -mt-1 mb-1" data-testid="portal-applicant-number">
              <span className="text-xs text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Bewerbernummer' : 'Application No.'}:</span>
              <span className="text-xs font-mono font-bold text-[var(--color-primary)] bg-[var(--color-primary-muted)] px-2 py-0.5 rounded-[var(--radius-xs)]">{activeApp.applicant_number}</span>
            </div>
          )}
          <StatusCockpit stage={stage} applicationId={activeApp.id} lang={lang} />
        </>
      )}

      {/* ═══ QUICK STATS ═══════════════════════════════════ */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3" data-testid="portal-stats-zone">
        <QuickStatCard
          icon={FileText}
          label={lang === 'de' ? 'Dokumente' : 'Documents'}
          value={documents.length}
          path="/portal/documents"
          testid="dash-docs"
          alert={documents.some(d => d.status === 'rejected')}
        />
        <QuickStatCard
          icon={MessageSquare}
          label={lang === 'de' ? 'Nachrichten' : 'Messages'}
          value={unreadMessages > 0 ? `${unreadMessages} ${lang === 'de' ? 'neu' : 'new'}` : '\u2013'}
          path="/portal/messages"
          testid="dash-messages"
          alert={unreadMessages > 0}
        />
        <QuickStatCard
          icon={CreditCard}
          label={lang === 'de' ? 'Rechnungen' : 'Invoices'}
          value={openInvoices > 0 ? `${openInvoices} ${lang === 'de' ? 'offen' : 'open'}` : '\u2013'}
          path="/portal/financials"
          testid="dash-financials"
          alert={openInvoices > 0}
        />
        <QuickStatCard
          icon={Bell}
          label={lang === 'de' ? 'Aufgaben' : 'Tasks'}
          value={openTasks}
          path="/portal/journey"
          testid="dash-tasks"
          alert={openTasks > 0}
        />
      </div>

      {/* ═══ CHECKLISTE + WISSENSBOX ═══════════════════════ */}
      {activeApp && (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
          <div className="lg:col-span-3">
            <ChecklistPanel items={checklist} lang={lang} />
          </div>
          <div className="lg:col-span-2">
            <KnowledgeBox
              title={lang === 'de' ? 'Hilfe & Wissen' : 'Help & Knowledge'}
              links={[
                ...(stageInfo?.knowledgeLinks || []),
                { label: lang === 'de' ? 'Was ist ein Studienkolleg?' : 'What is a Studienkolleg?', url: 'https://www.studienkollegs.de/' },
                { label: 'Anabin (KMK)', url: 'https://anabin.kmk.org/', source: lang === 'de' ? 'Offizielle Quelle' : 'Official Source' },
                { label: 'DAAD', url: 'https://www.daad.de/', source: lang === 'de' ? 'Studium in DE' : 'Study in DE' },
                { label: lang === 'de' ? 'Visum & Einreise' : 'Visa & Entry', url: 'https://digital.diplo.de/', source: lang === 'de' ? 'Auswaertiges Amt' : 'Foreign Office' },
              ]}
              lang={lang}
            />
          </div>
        </div>
      )}

      {/* ═══ QUICK ACTIONS ═════════════════════════════════ */}
      {activeApp && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <QuickActionCard
            to="/portal/documents"
            icon={FileText}
            title={lang === 'de' ? 'Dokumente verwalten' : 'Manage Documents'}
            desc={lang === 'de' ? 'Hochladen, pruefen, Status einsehen' : 'Upload, review, check status'}
            testid="dash-action-docs"
          />
          <QuickActionCard
            to="/portal/messages"
            icon={MessageSquare}
            title={lang === 'de' ? 'Nachricht senden' : 'Send Message'}
            desc={lang === 'de' ? 'Direkt mit unserem Team kommunizieren' : 'Communicate directly with our team'}
            testid="dash-action-msg"
          />
        </div>
      )}
    </PageScaffold>
  );
}
