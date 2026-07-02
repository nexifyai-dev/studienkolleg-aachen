import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { AlertCircle, Search, Plus, Send, Loader2, X, CheckCircle } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { toast } from 'sonner';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';

/* ═══════ Anfrage-Modal ═══════ */
function RequestModal({ onClose, onCreated, lang }) {
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [sending, setSending] = useState(false);
  const presets = lang === 'de'
    ? [
        { t: 'Frage zum Bewerbungsstatus', d: 'Ich moechte den aktuellen Stand meiner Bewerbung erfahren.' },
        { t: 'Dokument nachreichen', d: 'Ich moechte ein weiteres Dokument einreichen.' },
        { t: 'Terminaenderung', d: 'Ich moechte meinen Termin verschieben oder aendern.' },
        { t: 'Rechnungsfrage', d: 'Ich habe eine Frage zu meiner Rechnung.' },
      ]
    : [
        { t: 'Application status inquiry', d: 'I would like to know the current status of my application.' },
        { t: 'Submit additional document', d: 'I would like to submit an additional document.' },
        { t: 'Appointment change', d: 'I would like to reschedule my appointment.' },
        { t: 'Invoice question', d: 'I have a question about my invoice.' },
      ];

  const submit = async () => {
    if (!title.trim()) return;
    setSending(true);
    try {
      await apiClient.post('/api/tasks', { title, description: desc });
      toast.success(lang === 'de' ? 'Anfrage gesendet' : 'Request sent');
      onCreated();
      onClose();
    } catch (e) {
      toast.error(e.response?.data?.detail || (lang === 'de' ? 'Fehler beim Senden' : 'Failed to send'));
    } finally { setSending(false); }
  };

  return (
    <div className="w2g-modal-overlay" onClick={onClose} data-testid="request-modal">
      <div className="w2g-modal max-w-lg" onClick={e => e.stopPropagation()}>
        <div className="w2g-modal-header">
          <h2 className="font-heading text-base font-bold text-[var(--color-primary)] flex items-center gap-2">
            <Send size={16} /> {lang === 'de' ? 'Anfrage an Verwaltung' : 'Request to Administration'}
          </h2>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="close-request-modal"><X size={18} /></button>
        </div>
        <div className="w2g-modal-body space-y-4">
          <div>
            <label className="w2g-label">{lang === 'de' ? 'Schnellauswahl' : 'Quick Select'}</label>
            <div className="grid grid-cols-2 gap-2">
              {presets.map((p, i) => (
                <button key={i} onClick={() => { setTitle(p.t); setDesc(p.d); }}
                  className={`text-left p-2.5 border rounded-[var(--radius-sm)] text-xs transition-all ${title === p.t ? 'border-[var(--color-primary)] bg-[rgba(10,25,47,0.05)]' : 'border-[var(--color-divider)] hover:border-[rgba(10,25,47,0.4)]'}`}
                  data-testid={`preset-${i}`}>
                  {p.t}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="w2g-label">{lang === 'de' ? 'Betreff' : 'Subject'}</label>
            <input value={title} onChange={e => setTitle(e.target.value)} placeholder={lang === 'de' ? 'Worum geht es?' : 'What is this about?'} className="w2g-input" data-testid="request-title" />
          </div>
          <div>
            <label className="w2g-label">{lang === 'de' ? 'Beschreibung' : 'Description'}</label>
            <textarea value={desc} onChange={e => setDesc(e.target.value)} rows={3} placeholder={lang === 'de' ? 'Details zu deiner Anfrage...' : 'Details about your request...'} className="w2g-textarea" data-testid="request-desc" />
          </div>
        </div>
        <div className="w2g-modal-footer">
          <button onClick={onClose} className="w2g-btn-secondary">{lang === 'de' ? 'Abbrechen' : 'Cancel'}</button>
          <button onClick={submit} disabled={sending || !title.trim()} className="w2g-btn-primary" data-testid="request-submit">
            {sending ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />} {lang === 'de' ? 'Senden' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ApplicantTasksPage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const lang = i18n.language === 'en' ? 'en' : 'de';

  const STATUS_LABELS = {
    open: lang === 'de' ? 'Offen' : 'Open',
    in_progress: lang === 'de' ? 'In Bearbeitung' : 'In Progress',
    done: lang === 'de' ? 'Erledigt' : 'Completed',
  };

  const [tasks, setTasks] = useState([]);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('all');
  const [priorityOnly, setPriorityOnly] = useState(false);
  const [showRequest, setShowRequest] = useState(false);

  const loadTasks = () => {
    apiClient.get('/api/tasks', { withCredentials: true }).then((response) => setTasks(response.data || [])).catch(() => setTasks([]));
  };

  useEffect(() => { loadTasks(); }, []);

  const filteredTasks = useMemo(() => tasks.filter((task) => {
    const matchesStatus = status === 'all' || task.status === status;
    const matchesPriority = !priorityOnly || task.priority === 'high';
    const query = search.toLowerCase();
    const matchesSearch = !query || (task.title || '').toLowerCase().includes(query) || (task.description || '').toLowerCase().includes(query);
    return matchesStatus && matchesPriority && matchesSearch;
  }), [priorityOnly, search, status, tasks]);

  const handleTaskAction = (task) => {
    const type = (task.type || task.category || '').toLowerCase();
    if (type.includes('document') || type.includes('dokument') || type.includes('upload')) {
      navigate('/portal/documents');
    } else if (type.includes('message') || type.includes('nachricht') || type.includes('communication')) {
      navigate('/portal/messages');
    } else if (type.includes('payment') || type.includes('zahlung') || type.includes('invoice') || type.includes('rechnung')) {
      navigate('/portal/financials');
    } else {
      navigate('/portal/documents');
    }
  };

  return (
    <PageScaffold
      title={lang === 'de' ? 'Aufgaben & Checkliste' : 'Tasks & Checklist'}
      subtitle={lang === 'de'
        ? 'Jede Aufgabe erklaert, warum sie noetig ist und welcher naechste Schritt erwartet wird.'
        : 'Each task explains why it is needed and what the next step will be.'}
      testId="applicant-tasks-page"
      toolbar={<ToolbarRow
        search={<div className="relative"><Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" /><input value={search} onChange={(event) => setSearch(event.target.value)} className="w2g-search pl-10" placeholder={lang === 'de' ? 'Aufgaben durchsuchen...' : 'Search tasks...'} data-testid="applicant-tasks-search" /></div>}
        filters={[
          <select key="status" value={status} onChange={(event) => setStatus(event.target.value)} className="w2g-select" data-testid="applicant-tasks-status-filter">
            <option value="all">{lang === 'de' ? 'Status' : 'Status'}</option>
            <option value="open">{STATUS_LABELS.open}</option>
            <option value="in_progress">{STATUS_LABELS.in_progress}</option>
            <option value="done">{STATUS_LABELS.done}</option>
          </select>,
        ]}
        primaryAction={
          <div className="flex items-center gap-2">
            <button type="button" onClick={() => setPriorityOnly((value) => !value)} className={priorityOnly ? 'w2g-btn-primary' : 'w2g-btn-secondary'} data-testid="applicant-tasks-priority-toggle">{lang === 'de' ? 'Nur dringend' : 'Urgent only'}</button>
            <button type="button" onClick={() => setShowRequest(true)} className="w2g-btn-primary" data-testid="applicant-send-request-btn">
              <Send size={14} /> {lang === 'de' ? 'Anfrage senden' : 'Send Request'}
            </button>
          </div>
        }
      />}
    >
      <div className="space-y-4" data-testid="applicant-tasks-list">
        {filteredTasks.length === 0 ? (
          <div className="w2g-empty" data-testid="applicant-tasks-empty">
            <AlertCircle size={28} className="w2g-empty-icon" />
            <p className="w2g-empty-text">{lang === 'de' ? 'Aktuell gibt es keine passenden Aufgaben fuer diese Filterung.' : 'No tasks match your current filter.'}</p>
          </div>
        ) : filteredTasks.map((task) => (
          <article key={task.id} className="w2g-card" data-testid={`applicant-task-card-${task.id}`}>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <h2 className="text-base font-semibold text-[var(--color-text-primary)]">{task.title}</h2>
                  <span className="w2g-badge bg-[rgba(10,25,47,0.08)] text-[var(--color-primary)]">{STATUS_LABELS[task.status] || task.status}</span>
                  {task.priority === 'high' ? <span className="w2g-badge bg-[var(--color-danger-bg)] text-[var(--color-danger)]">{lang === 'de' ? 'Dringend' : 'Urgent'}</span> : null}
                </div>
                <p className="text-sm text-[var(--color-text-secondary)]">{task.description || (lang === 'de' ? 'Diese Aufgabe ist fuer deinen weiteren Prozessschritt relevant.' : 'This task is relevant for your next process step.')}</p>
                <div className="mt-3 flex flex-wrap gap-4 text-xs text-[var(--color-text-secondary)]">
                  <span>{lang === 'de' ? 'Bezug' : 'Related to'}: {task.application_id ? (lang === 'de' ? 'Aktive Bewerbung' : 'Active application') : (lang === 'de' ? 'Portalprozess' : 'Portal process')}</span>
                  <span>{lang === 'de' ? 'Faellig' : 'Due'}: {task.due_date ? new Date(task.due_date).toLocaleDateString(lang === 'de' ? 'de-DE' : 'en-US') : (lang === 'de' ? 'Ohne feste Frist' : 'No deadline')}</span>
                </div>
              </div>
              {task.status !== 'done' && (
                <button type="button" className="w2g-btn-primary" onClick={() => handleTaskAction(task)} data-testid={`applicant-task-cta-${task.id}`}>
                  {lang === 'de' ? 'Jetzt erledigen' : 'Complete now'}
                </button>
              )}
            </div>
          </article>
        ))}
      </div>

      {showRequest && <RequestModal onClose={() => setShowRequest(false)} onCreated={loadTasks} lang={lang} />}
    </PageScaffold>
  );
}
