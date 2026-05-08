import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { toast } from 'sonner';
import { getStageLabel, getLang } from '../../lib/utils';
import AIScreeningDeltaPanel from '../../components/AIScreeningDeltaPanel';
import InvoiceCreateModal from '../../components/staff/InvoiceCreateModal';
import {
  ArrowLeft, RefreshCw, CheckCircle,
  FileText, Clock, XCircle, Loader2,
  Phone, Mail, MessageCircle, Users, GraduationCap, Trash2,
  Edit3, Save, X, Send, StickyNote, History, CalendarClock, Plus,
  CheckSquare, Receipt, BookOpen, AlertTriangle, Download, Upload, Eye
} from 'lucide-react';
import { Card, CardContent } from '../../components/ui/card';
import { InfoCard } from '../../components/layout/BackstageComponents';
import { Badge } from '../../components/ui/badge';
import BrainPanel from '../../components/shared/BrainPanel';
import { API } from '../../lib/apiBase';

/* ─── Natuerliche Sprache fuer technische Begriffe ─────────── */
const SOURCE_LABELS = {
  direct_inquiry: 'Direkte Anfrage',
  website_form: 'Website-Bewerbung',
  partner_referral: 'Partner-Vermittlung',
  email: 'E-Mail-Bewerbung',
  phone: 'Telefonische Anfrage',
  walk_in: 'Persoenliche Vorsprache',
  social_media: 'Soziale Medien',
  referral: 'Empfehlung',
};

const PIPELINE = [
  'lead_new', 'in_review', 'pending_docs', 'interview_scheduled',
  'conditional_offer', 'offer_sent', 'enrolled',
];
const TERMINAL = ['declined', 'on_hold', 'archived'];

const DOC_STATUS = {
  uploaded: { label: 'Hochgeladen', icon: Clock, color: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]' },
  in_review: { label: 'In Pruefung', icon: RefreshCw, color: 'bg-[var(--color-info-bg)] text-[var(--color-info)]' },
  approved: { label: 'Akzeptiert', icon: CheckCircle, color: 'bg-[var(--color-success-bg)] text-[var(--color-success)]' },
  rejected: { label: 'Abgelehnt', icon: XCircle, color: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]' },
};

const DOC_TYPE_LABELS = {
  passport: 'Reisepass / Personalausweis',
  highschool_diploma: 'Schulzeugnis / Hochschulzugangsberechtigung',
  language_certificate: 'Deutsches Sprachzertifikat',
  motivation_letter: 'Motivationsschreiben',
  cv: 'Lebenslauf',
  photo: 'Passfoto',
  other: 'Sonstiges',
};

const ALLOWED_UPLOAD_TYPES = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

/* ═══════ Inline Editable Field ═══════ */
function EditableField({ label, value, field, onSave, type = 'text', displayValue }) {
  const [editing, setEditing] = useState(false);
  const [val, setVal] = useState(value || '');
  const save = () => { onSave(field, val); setEditing(false); };
  return (
    <div className="flex items-center justify-between py-1.5 group" data-testid={`field-${field}`}>
      <dt className="text-[11px] text-[var(--color-text-secondary)] w-24 shrink-0">{label}</dt>
      <dd className="flex-1 text-right">
        {editing ? (
          <div className="flex items-center gap-1 justify-end">
            <input type={type} value={val} onChange={e => setVal(e.target.value)}
              className="text-xs border border-primary/40 rounded-sm px-2 py-1 focus:outline-none focus:ring-1 focus:ring-primary/30 w-40 text-right"
              autoFocus onKeyDown={e => e.key === 'Enter' && save()} />
            <button onClick={save} className="text-primary hover:text-primary/80"><Save size={12} /></button>
            <button onClick={() => setEditing(false)} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]"><X size={12} /></button>
          </div>
        ) : (
          <span className="text-xs text-[var(--color-text-primary)] cursor-pointer hover:text-primary flex items-center justify-end gap-1"
            onClick={() => setEditing(true)}>
            {displayValue || value || <span className="text-[var(--color-text-tertiary)] italic">-</span>}
            <Edit3 size={10} className="text-[var(--color-text-tertiary)] opacity-0 group-hover:opacity-100 transition-opacity" />
          </span>
        )}
      </dd>
    </div>
  );
}

/* ═══════ Stage Progress Bar (klickbar, lesbar, autonom) ═══════ */
function StageProgressBar({ currentStage, onStageClick }) {
  const currentIdx = PIPELINE.indexOf(currentStage);
  const isTerminal = TERMINAL.includes(currentStage);
  return (
    <div data-testid="stage-progress-bar">
      <div className="flex items-stretch rounded-[var(--radius-sm)] overflow-hidden border border-[var(--color-divider-subtle)] bg-[var(--color-surface)]">
        {PIPELINE.map((stage, idx) => {
          const isCurrent = stage === currentStage;
          const isPast = !isTerminal && currentIdx >= 0 && idx < currentIdx;
          const isFuture = !isCurrent && !isPast;
          return (
            <button key={stage} onClick={() => !isCurrent && onStageClick && onStageClick(stage)}
              className={`flex-1 py-3 px-2 text-center transition-all relative cursor-pointer ${
                isCurrent
                  ? 'bg-[var(--color-primary)] text-white shadow-md z-10'
                  : isPast
                  ? 'bg-[var(--color-primary)]/10 text-[var(--color-primary)] hover:bg-[var(--color-primary)]/20'
                  : 'bg-[var(--color-surface-elevated)] text-[var(--color-text-tertiary)] hover:bg-[var(--color-surface-sunken)] hover:text-[var(--color-text-secondary)]'
              }`}
              data-testid={`progress-stage-${stage}`}
              title={`Klicken um Status zu aendern auf: ${getStageLabel(stage, "de")}`}>
              <span className={`block text-[11px] font-bold leading-tight ${isCurrent ? '' : isFuture ? 'opacity-60' : ''}`}>
                {getStageLabel(stage, "de")}
              </span>
              <span className={`block text-[8px] mt-0.5 ${isCurrent ? 'text-white/70' : isPast ? 'text-[var(--color-primary)]/50' : 'text-[var(--color-text-tertiary)]/50'}`}>
                {isPast ? 'Abgeschlossen' : isCurrent ? 'Aktuell' : `Schritt ${idx + 1}`}
              </span>
              {isPast && <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-[var(--color-primary)]/40" />}
              {isCurrent && <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-white/50" />}
            </button>
          );
        })}
      </div>
      {isTerminal && (
        <div className="mt-1 px-4 py-2 bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)] rounded-[var(--radius-sm)] text-center text-xs font-bold text-[var(--color-danger)] flex items-center justify-center gap-2">
          <AlertTriangle size={13} />
          {getStageLabel(currentStage, "de")}
        </div>
      )}
      {/* Terminale Optionen */}
      <div className="flex gap-1.5 mt-1.5 justify-end">
        {TERMINAL.map(ts => (
          <button key={ts} onClick={() => onStageClick && onStageClick(ts)}
            className={`text-[10px] px-2.5 py-1 rounded-[var(--radius-xs)] font-medium transition-all ${
              currentStage === ts
                ? 'bg-[var(--color-danger)] text-white'
                : 'border border-[var(--color-divider)] text-[var(--color-text-tertiary)] hover:border-[var(--color-danger)] hover:text-[var(--color-danger)] hover:bg-[var(--color-danger-bg)]'
            }`}
            disabled={currentStage === ts}
            data-testid={`progress-stage-${ts}`}
            title={getStageLabel(ts, "de")}>
            {getStageLabel(ts, "de")}
          </button>
        ))}
      </div>
    </div>
  );
}

/* ═══════ Generisches PopUp-Modal (Wiederverwendbar) ═══════ */
function PopUpModal({ open, onClose, title, icon: Icon, maxWidth = '600px', maxHeight = '85vh', testId, children }) {
  if (!open) return null;
  return (
    <div className="w2g-modal-overlay" onClick={onClose} data-testid={testId}>
      <div className="w2g-modal" style={{ maxWidth, maxHeight }} onClick={e => e.stopPropagation()}>
        <div className="w2g-modal-header">
          <h3 className="font-heading text-base font-bold text-[var(--color-primary)] flex items-center gap-2">
            {Icon && <Icon size={16} />}{title}
          </h3>
          <button onClick={onClose} className="w2g-btn-icon" data-testid={`${testId}-close`}><X size={16} /></button>
        </div>
        <div className="w2g-modal-body overflow-y-auto" style={{ maxHeight: `calc(${maxHeight} - 60px)` }}>
          {children}
        </div>
      </div>
    </div>
  );
}

/* ═══════ Aufgaben-PopUp-Inhalt (1:1 wie Listenseite) ═══════ */
function TasksPopupContent({ appId, applicantName }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title: '', priority: 'normal', due_date: '', description: '' });
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    try {
      const r = await apiClient.get('/api/tasks', { withCredentials: true });
      setTasks((r.data || []).filter(t => t.application_id === appId));
    } catch {} finally { setLoading(false); }
  }, [appId]);
  useEffect(() => { load(); }, [load]);

  const create = async () => {
    if (!form.title.trim()) return;
    setCreating(true);
    try {
      await apiClient.post('/api/tasks', { ...form, application_id: appId, description: form.description || `Bewerber: ${applicantName || ''}` }, { withCredentials: true });
      toast.success('Aufgabe erstellt');
      setForm({ title: '', priority: 'normal', due_date: '', description: '' });
      setShowCreate(false);
      await load();
    } catch { toast.error('Fehler'); } finally { setCreating(false); }
  };

  const toggleStatus = async (task) => {
    const next = task.status === 'done' ? 'open' : task.status === 'open' ? 'in_progress' : 'done';
    try { await apiClient.put(`/api/tasks/${task.id}`, { status: next }, { withCredentials: true }); await load(); } catch {}
  };

  const PRIO = { high: { label: 'Hoch', cls: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border border-[var(--color-danger-border)]' }, normal: { label: 'Normal', cls: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]' }, low: { label: 'Niedrig', cls: 'bg-[var(--color-surface-elevated)] text-[var(--color-text-tertiary)]' } };
  const STATUS = { open: { label: 'Offen', cls: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]' }, in_progress: { label: 'In Bearbeitung', cls: 'bg-[var(--color-info-bg)] text-[var(--color-info)]' }, done: { label: 'Erledigt', cls: 'bg-[var(--color-success-bg)] text-[var(--color-success)]' } };

  return (
    <div className="space-y-4" data-testid="tasks-popup-content">
      <div className="flex items-center justify-between">
        <p className="text-xs text-[var(--color-text-secondary)]">{tasks.length} Aufgaben fuer diesen Bewerber</p>
        <button onClick={() => setShowCreate(!showCreate)} className="w2g-btn-primary text-xs" data-testid="tasks-popup-create"><Plus size={12} /> Neue Aufgabe</button>
      </div>

      {showCreate && (
        <Card className="border-[var(--color-primary)]/30" data-testid="tasks-popup-form">
          <CardContent className="pt-4 space-y-3">
            <div>
              <label className="w2g-label">Titel</label>
              <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="Was muss erledigt werden?" className="w2g-input w-full text-sm" autoFocus data-testid="task-popup-title" />
            </div>
            <div>
              <label className="w2g-label">Beschreibung</label>
              <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="Details zur Aufgabe..." className="w2g-input w-full text-sm resize-none" rows={2} data-testid="task-popup-desc" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="w2g-label">Prioritaet</label>
                <select value={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.value }))} className="w2g-select w-full text-sm" data-testid="task-popup-priority">
                  <option value="low">Niedrig</option><option value="normal">Normal</option><option value="high">Hoch</option>
                </select>
              </div>
              <div>
                <label className="w2g-label">Faellig am</label>
                <input type="date" value={form.due_date} onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))} className="w2g-input w-full text-sm" data-testid="task-popup-due" />
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={create} disabled={creating || !form.title.trim()} className="w2g-btn-primary text-xs" data-testid="task-popup-submit">
                {creating ? <Loader2 size={12} className="animate-spin" /> : <Plus size={12} />} Erstellen
              </button>
              <button onClick={() => setShowCreate(false)} className="w2g-btn-secondary text-xs">Abbrechen</button>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? <Loader2 size={16} className="animate-spin text-[var(--color-text-tertiary)] mx-auto" /> : (
        <div className="space-y-2">
          {tasks.length === 0 && <p className="text-center text-xs text-[var(--color-text-tertiary)] py-4">Keine Aufgaben vorhanden</p>}
          {tasks.map(t => (
            <div key={t.id} className="flex items-center gap-3 p-3 border border-[var(--color-divider-subtle)] rounded-[var(--radius-sm)] hover:border-[var(--color-primary)]/30 transition-colors" data-testid={`task-popup-item-${t.id}`}>
              <button onClick={() => toggleStatus(t)} className={`shrink-0 ${t.status === 'done' ? 'text-[var(--color-success)]' : 'text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)]'}`} data-testid={`task-toggle-${t.id}`}>
                <CheckCircle size={16} />
              </button>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${t.status === 'done' ? 'text-[var(--color-text-tertiary)] line-through' : 'text-[var(--color-text-primary)]'}`}>{t.title}</p>
                {t.description && <p className="text-[10px] text-[var(--color-text-tertiary)] truncate mt-0.5">{t.description}</p>}
                <div className="flex items-center gap-2 mt-1">
                  {t.due_date && <span className="text-[10px] text-[var(--color-text-tertiary)]">{t.due_date}</span>}
                </div>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                <span className={`text-[9px] px-1.5 py-0.5 rounded-sm font-medium ${PRIO[t.priority]?.cls || PRIO.normal.cls}`}>{PRIO[t.priority]?.label || 'Normal'}</span>
                <span className={`text-[9px] px-1.5 py-0.5 rounded-sm font-medium ${STATUS[t.status]?.cls || STATUS.open.cls}`}>{STATUS[t.status]?.label || t.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ═══════ Rechnungen-PopUp-Inhalt (1:1 wie Listenseite) ═══════ */
function InvoicesPopupContent({ applicantId, appId, applicantName, onCreateNew }) {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    apiClient.get('/api/invoices', { withCredentials: true })
      .then(r => setInvoices((r.data || []).filter(i => i.applicant_id === applicantId)))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [applicantId]);

  const statusLabels = { draft: 'Entwurf', sent: 'Versendet', paid: 'Bezahlt', overdue: 'Ueberfaellig', cancelled: 'Storniert' };
  const statusColors = { draft: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]', sent: 'bg-[var(--color-info-bg)] text-[var(--color-info)]', paid: 'bg-[var(--color-success-bg)] text-[var(--color-success)]', overdue: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]', cancelled: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)]' };

  return (
    <div className="space-y-4" data-testid="invoices-popup-content">
      <div className="flex items-center justify-between">
        <p className="text-xs text-[var(--color-text-secondary)]">{invoices.length} Rechnungen fuer diesen Bewerber</p>
        <button onClick={onCreateNew} className="w2g-btn-primary text-xs" data-testid="invoices-popup-create"><Plus size={12} /> Neue Rechnung</button>
      </div>
      {loading ? <Loader2 size={16} className="animate-spin text-[var(--color-text-tertiary)] mx-auto" /> : (
        <div className="space-y-2">
          {invoices.length === 0 && <p className="text-center text-xs text-[var(--color-text-tertiary)] py-4">Keine Rechnungen vorhanden</p>}
          {invoices.map(inv => (
            <div key={inv.id || inv.invoice_number} className="flex items-center justify-between p-3 border border-[var(--color-divider-subtle)] rounded-[var(--radius-sm)] hover:border-[var(--color-primary)]/30 transition-colors" data-testid={`invoice-popup-item-${inv.invoice_number}`}>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-[var(--color-text-primary)]">{inv.invoice_number}</p>
                <p className="text-[10px] text-[var(--color-text-tertiary)] mt-0.5">{inv.description || 'Keine Beschreibung'}</p>
                {inv.created_at && <p className="text-[10px] text-[var(--color-text-tertiary)]">{new Date(inv.created_at).toLocaleDateString('de-DE')}</p>}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="text-sm font-bold text-[var(--color-text-primary)] tabular-nums">{inv.amount ? `${inv.amount.toFixed(2)} EUR` : ''}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-sm font-medium ${statusColors[inv.status] || statusColors.draft}`}>{statusLabels[inv.status] || inv.status}</span>
                {inv.id && <a href={`${API}/api/invoices/${inv.id}/pdf`} target="_blank" rel="noopener noreferrer" className="text-[var(--color-primary)] hover:text-[var(--color-accent)]" title="PDF herunterladen"><Download size={14} /></a>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ═══════ Notizen-PopUp-Inhalt ═══════ */
function NotesPopupContent({ appId }) {
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    apiClient.get(`/api/applications/${appId}/notes`, { withCredentials: true }).then(r => setNotes(r.data || [])).catch(() => {});
  }, [appId]);

  const addNote = async () => {
    if (!newNote.trim()) return;
    setSaving(true);
    try {
      await apiClient.post(`/api/applications/${appId}/notes`, { content: newNote, visibility: 'internal' }, { withCredentials: true });
      setNewNote('');
      const r = await apiClient.get(`/api/applications/${appId}/notes`, { withCredentials: true });
      setNotes(r.data || []);
      toast.success('Notiz gespeichert');
    } catch { toast.error('Fehler'); } finally { setSaving(false); }
  };

  return (
    <div className="space-y-4" data-testid="notes-popup-content">
      <div className="flex gap-2">
        <input value={newNote} onChange={e => setNewNote(e.target.value)} placeholder="Neue Notiz hinzufuegen..." className="w2g-input flex-1 text-sm" onKeyDown={e => e.key === 'Enter' && addNote()} autoFocus data-testid="notes-popup-input" />
        <button onClick={addNote} disabled={saving || !newNote.trim()} className="w2g-btn-primary text-sm px-4" data-testid="notes-popup-submit">
          {saving ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
        </button>
      </div>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {notes.length === 0 && <p className="text-center text-xs text-[var(--color-text-tertiary)] py-4">Keine Notizen vorhanden</p>}
        {notes.map(n => (
          <div key={n.id} className="bg-[var(--color-surface-elevated)] rounded-[var(--radius-sm)] px-4 py-3" data-testid={`note-popup-${n.id}`}>
            <p className="text-sm text-[var(--color-text-primary)]">{n.content}</p>
            <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1">{n.created_at ? new Date(n.created_at).toLocaleString('de-DE') : ''}{n.author_name ? ` · ${n.author_name}` : ''}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════ Wiedervorlagen-PopUp-Inhalt ═══════ */
function FollowupsPopupContent({ appId }) {
  const [followups, setFollowups] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ due_date: '', reason: '' });
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    try { const r = await apiClient.get('/api/followups', { withCredentials: true }); setFollowups((r.data || []).filter(f => f.application_id === appId)); } catch {}
  }, [appId]);
  useEffect(() => { load(); }, [load]);

  const create = async () => {
    if (!form.due_date || !form.reason) return;
    setCreating(true);
    try {
      await apiClient.post('/api/followups', { application_id: appId, due_date: form.due_date, reason: form.reason }, { withCredentials: true });
      setForm({ due_date: '', reason: '' }); setShowCreate(false); await load();
    } catch {} finally { setCreating(false); }
  };
  const markDone = async (id) => { try { await apiClient.put(`/api/followups/${id}`, { status: 'done' }, { withCredentials: true }); await load(); } catch {} };
  const dismiss = async (id) => { try { await apiClient.delete(`/api/followups/${id}`, { withCredentials: true }); await load(); } catch {} };

  return (
    <div className="space-y-4" data-testid="followups-popup-content">
      <div className="flex items-center justify-between">
        <p className="text-xs text-[var(--color-text-secondary)]">{followups.length} Wiedervorlagen</p>
        <button onClick={() => setShowCreate(!showCreate)} className="w2g-btn-primary text-xs" data-testid="followup-popup-create"><Plus size={12} /> Neue Wiedervorlage</button>
      </div>
      {showCreate && (
        <Card className="border-[var(--color-primary)]/30">
          <CardContent className="pt-4 space-y-3">
            <input type="date" value={form.due_date} onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))} className="w2g-input w-full text-sm" data-testid="followup-popup-date" />
            <input value={form.reason} onChange={e => setForm(f => ({ ...f, reason: e.target.value }))} placeholder="Grund / Aktion..." className="w2g-input w-full text-sm" data-testid="followup-popup-reason" />
            <div className="flex gap-2">
              <button onClick={create} disabled={creating || !form.due_date || !form.reason} className="w2g-btn-primary text-xs" data-testid="followup-popup-submit">{creating ? <Loader2 size={12} className="animate-spin" /> : 'Erstellen'}</button>
              <button onClick={() => setShowCreate(false)} className="w2g-btn-secondary text-xs">Abbrechen</button>
            </div>
          </CardContent>
        </Card>
      )}
      <div className="space-y-2">
        {followups.length === 0 && <p className="text-center text-xs text-[var(--color-text-tertiary)] py-4">Keine Wiedervorlagen vorhanden</p>}
        {followups.map(f => (
          <div key={f.id} className={`flex items-center gap-3 p-3 border border-[var(--color-divider-subtle)] rounded-[var(--radius-sm)] ${f.status === 'done' ? 'opacity-50' : ''}`} data-testid={`followup-popup-${f.id}`}>
            <span className="flex-1 text-sm">{f.reason}</span>
            <span className="text-[10px] text-[var(--color-text-tertiary)] shrink-0 tabular-nums">{f.due_date}</span>
            {f.status !== 'done' && (
              <>
                <button onClick={() => markDone(f.id)} className="text-[var(--color-success)] hover:text-[var(--color-success)]/80" title="Erledigt"><CheckCircle size={14} /></button>
                <button onClick={() => dismiss(f.id)} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]" title="Entfernen"><Trash2 size={14} /></button>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════ Verlauf-PopUp-Inhalt ═══════ */
function HistoryPopupContent({ appId }) {
  const [logs, setLogs] = useState([]);
  useEffect(() => {
    apiClient.get(`/api/audit-logs?target_id=${appId}`, { withCredentials: true }).then(r => setLogs(r.data?.slice(0, 30) || [])).catch(() => {});
  }, [appId]);

  const actionLabels = {
    application_stage_changed: 'Status geaendert',
    document_uploaded: 'Dokument hochgeladen',
    document_reviewed: 'Dokument geprueft',
    invoice_created: 'Rechnung erstellt',
    task_created: 'Aufgabe erstellt',
    email_sent: 'E-Mail gesendet',
    note_added: 'Notiz hinzugefuegt',
    screening_completed: 'KI-Screening abgeschlossen',
  };

  return (
    <div className="space-y-2 max-h-96 overflow-y-auto" data-testid="history-popup-content">
      {logs.length === 0 && <p className="text-center text-xs text-[var(--color-text-tertiary)] py-4">Keine Aktivitaeten vorhanden</p>}
      {logs.map((l, i) => (
        <div key={l.id || i} className="flex items-start gap-3 py-2 border-b border-[var(--color-divider-subtle)] last:border-0">
          <div className="w-2 h-2 rounded-full bg-[var(--color-primary)]/40 mt-1.5 shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-xs text-[var(--color-text-primary)]">{actionLabels[l.action] || l.action}</p>
            {l.details && <p className="text-[10px] text-[var(--color-text-tertiary)] mt-0.5">{typeof l.details === 'string' ? l.details : JSON.stringify(l.details)}</p>}
          </div>
          <span className="text-[10px] text-[var(--color-text-tertiary)] shrink-0 tabular-nums">{l.occurred_at ? new Date(l.occurred_at).toLocaleString('de-DE') : ''}</span>
        </div>
      ))}
    </div>
  );
}

/* ═══════ E-Mail Composer PopUp ═══════ */
function EmailComposerContent({ appId, applicantEmail, applicantName, onSent }) {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [sending, setSending] = useState(false);
  const [templates, setTemplates] = useState([]);

  useEffect(() => { apiClient.get('/api/email-templates', { withCredentials: true }).then(r => setTemplates(r.data || [])).catch(() => {}); }, []);

  const sendEmail = async () => {
    if (!subject || !body) return;
    setSending(true);
    try {
      await apiClient.post(`/api/applications/${appId}/send-email`, { subject, body, to: applicantEmail }, { withCredentials: true });
      toast.success('E-Mail versendet');
      if (onSent) onSent();
    } catch { toast.error('Versand fehlgeschlagen'); } finally { setSending(false); }
  };

  return (
    <div className="space-y-3" data-testid="email-popup-content">
      {templates.length > 0 && (
        <div>
          <label className="w2g-label">Vorlage</label>
          <select onChange={e => { const tpl = templates.find(tp => tp.id === e.target.value); if (tpl) { setSubject(tpl.subject || ''); setBody(tpl.body?.replace('{{name}}', applicantName || '') || ''); } }} className="w2g-select w-full text-sm" data-testid="email-popup-template">
            <option value="">Vorlage waehlen...</option>
            {templates.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
      )}
      <div><label className="w2g-label">An</label><input value={applicantEmail || ''} disabled className="w2g-input w-full text-sm opacity-60" /></div>
      <div><label className="w2g-label">Betreff</label><input value={subject} onChange={e => setSubject(e.target.value)} placeholder="Betreff" className="w2g-input w-full text-sm" autoFocus data-testid="email-popup-subject" /></div>
      <div><label className="w2g-label">Nachricht</label><textarea value={body} onChange={e => setBody(e.target.value)} placeholder="Nachricht..." rows={6} className="w2g-input w-full text-sm resize-none" data-testid="email-popup-body" /></div>
      <button onClick={sendEmail} disabled={sending || !subject || !body} className="w2g-btn-primary w-full text-sm" data-testid="email-popup-send">
        {sending ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />} E-Mail senden
      </button>
    </div>
  );
}

/* ═══════ Portal-Nachricht PopUp ═══════ */
function PortalMessageContent({ appId, applicantId, applicantName, onSent }) {
  const [msg, setMsg] = useState('');
  const [sending, setSending] = useState(false);
  const [convLink, setConvLink] = useState(null);
  const send = async () => {
    if (!msg.trim()) return;
    setSending(true);
    try {
      const res = await apiClient.post('/api/messages', { content: msg, recipient_id: applicantId, channel: 'portal', application_id: appId }, { withCredentials: true });
      toast.success('Portal-Nachricht gesendet');
      const convId = res.data?.conversation_id;
      if (convId) setConvLink(`/staff/messaging?conv=${convId}`);
      if (onSent) onSent();
    } catch { toast.error('Fehler'); } finally { setSending(false); }
  };
  return (
    <div className="space-y-3" data-testid="msg-popup-content">
      <div><label className="w2g-label">An</label><p className="text-sm font-medium text-[var(--color-text-primary)]">{applicantName || 'Bewerber'}</p></div>
      <div><label className="w2g-label">Nachricht</label><textarea value={msg} onChange={e => setMsg(e.target.value)} placeholder="Nachricht an Bewerber..." rows={4} className="w2g-input w-full text-sm resize-none" autoFocus data-testid="msg-popup-input" /></div>
      <button onClick={send} disabled={sending || !msg.trim()} className="w2g-btn-primary w-full text-sm" data-testid="msg-popup-send">{sending ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />} Senden</button>
      {convLink && (
        <a href={convLink} className="text-xs text-primary hover:underline flex items-center gap-1" data-testid="msg-popup-conv-link">
          <MessageCircle size={12} /> Zur Konversation
        </a>
      )}
    </div>
  );
}

/* ═══════ Lehrer-Zuweisung PopUp ═══════ */
function TeacherPopupContent({ applicantId, applicantName }) {
  const [teachers, setTeachers] = useState([]);
  const [assigned, setAssigned] = useState(null);
  const [assigning, setAssigning] = useState(false);
  useEffect(() => {
    Promise.all([
      apiClient.get('/api/teacher/assignments', { withCredentials: true }).catch(() => ({ data: { assignments: [] } })),
      apiClient.get('/api/users', { withCredentials: true }).catch(() => ({ data: [] })),
    ]).then(([aRes, uRes]) => {
      const assignments = Array.isArray(aRes.data?.assignments || aRes.data) ? (aRes.data?.assignments || aRes.data) : [];
      setAssigned(assignments.find(a => a.applicant_id === applicantId) || null);
      setTeachers((Array.isArray(uRes.data) ? uRes.data : []).filter(u => u.role === 'teacher'));
    });
  }, [applicantId]);

  const assign = async (teacherId) => {
    setAssigning(true);
    try {
      await apiClient.post('/api/teacher/assignments', { applicant_id: applicantId, teacher_id: teacherId }, { withCredentials: true });
      toast.success('Lehrer zugewiesen');
      const r = await apiClient.get('/api/teacher/assignments', { withCredentials: true });
      const arr = Array.isArray(r.data?.assignments || r.data) ? (r.data?.assignments || r.data) : [];
      setAssigned(arr.find(a => a.applicant_id === applicantId) || null);
    } catch { toast.error('Zuweisung fehlgeschlagen'); } finally { setAssigning(false); }
  };

  return (
    <div className="space-y-3" data-testid="teacher-popup-content">
      {assigned ? (
        <div className="p-4 bg-[var(--color-success-bg)] rounded-[var(--radius-sm)] border border-[var(--color-success-border)]">
          <p className="text-sm font-medium text-[var(--color-text-primary)]">{assigned.teacher_name || 'Zugewiesen'}</p>
          <p className="text-[10px] text-[var(--color-text-tertiary)]">seit {assigned.created_at ? new Date(assigned.created_at).toLocaleDateString('de-DE') : '-'}</p>
        </div>
      ) : (
        <>
          <p className="text-xs text-[var(--color-text-secondary)]">Kein Lehrer zugewiesen. Waehlen Sie einen Lehrer fuer {applicantName}:</p>
          {teachers.length > 0 ? (
            <select onChange={e => e.target.value && assign(e.target.value)} disabled={assigning} className="w2g-select w-full text-sm" data-testid="teacher-popup-select">
              <option value="">Lehrer auswaehlen...</option>
              {teachers.map(t => <option key={t.id} value={t.id}>{t.full_name}</option>)}
            </select>
          ) : <p className="text-xs text-[var(--color-text-tertiary)]">Keine Lehrer im System vorhanden.</p>}
        </>
      )}
    </div>
  );
}

/* ═══════ Staff Dokument-Upload ═══════ */
function StaffDocUpload({ appId, onUploaded }) {
  const fileRef = React.useRef(null);
  const [uploading, setUploading] = useState(false);
  const [docType, setDocType] = useState('other');
  const [dragActive, setDragActive] = useState(false);

  const processFile = async (file) => {
    if (!file) return;
    if (!ALLOWED_UPLOAD_TYPES.includes(file.type)) { toast.error('Dateityp nicht erlaubt'); return; }
    if (file.size > 10 * 1024 * 1024) { toast.error('Datei zu gross (max. 10 MB)'); return; }
    setUploading(true);
    try {
      const b64 = await new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(r.result.split(',')[1]); r.onerror = rej; r.readAsDataURL(file); });
      await apiClient.post(`/api/applications/${appId}/documents/upload`, { document_type: docType, filename: file.name, content_type: file.type, file_data: b64 }, { withCredentials: true });
      toast.success('Dokument hochgeladen');
      onUploaded();
    } catch (e) { toast.error(e.response?.data?.detail || 'Upload fehlgeschlagen'); } finally { setUploading(false); }
  };

  return (
    <div className="space-y-2" data-testid="staff-doc-upload">
      <div className="flex gap-2">
        <select value={docType} onChange={e => setDocType(e.target.value)} className="w2g-select text-xs flex-1" data-testid="staff-doc-type-select">
          {Object.entries(DOC_TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>
      <div className={`border-2 border-dashed p-4 text-center cursor-pointer transition-all rounded-[var(--radius-sm)] ${dragActive ? 'border-[var(--color-accent)] bg-[var(--color-accent-muted)]' : 'border-[var(--color-divider)] hover:border-[var(--color-primary)] bg-[var(--color-surface-elevated)]'}`}
        onDragOver={e => { e.preventDefault(); setDragActive(true); }} onDragLeave={() => setDragActive(false)}
        onDrop={e => { e.preventDefault(); setDragActive(false); processFile(e.dataTransfer?.files?.[0]); }}
        onClick={() => !uploading && fileRef.current?.click()} data-testid="staff-doc-dropzone">
        <input ref={fileRef} type="file" className="hidden" accept=".pdf,.jpg,.jpeg,.png,.webp,.doc,.docx" onChange={e => { processFile(e.target.files?.[0]); e.target.value = ''; }} />
        {uploading ? <Loader2 size={18} className="mx-auto animate-spin text-[var(--color-accent)]" /> : (
          <><Upload size={18} className="mx-auto text-[var(--color-text-tertiary)] mb-1" /><p className="text-[10px] text-[var(--color-text-secondary)]">Datei hierher ziehen oder klicken</p></>
        )}
      </div>
    </div>
  );
}

/* ═══════ Stage Change Dialog ═══════ */
function StageChangeDialog({ currentStage, targetStage, appId, applicantName, applicantEmail, applicantLang, onComplete, onCancel }) {
  const [reason, setReason] = useState('');
  const [sendNotification, setSendNotification] = useState(true);
  const [createTask, setCreateTask] = useState(false);
  const [taskTitle, setTaskTitle] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const isTerminal = ['declined', 'on_hold'].includes(targetStage);
  const aLang = applicantLang || 'de';
  const isEN = aLang === 'en';

  const execute = async () => {
    setSubmitting(true);
    try {
      await apiClient.put(`/api/applications/${appId}`, { current_stage: targetStage });
      if (reason.trim()) {
        await apiClient.post(`/api/applications/${appId}/notes`, { content: `Status geaendert: ${getStageLabel(currentStage, "de")} → ${getStageLabel(targetStage, "de")}. Grund: ${reason}`, visibility: 'internal' }, { withCredentials: true }).catch(() => {});
      }
      if (sendNotification && applicantEmail) {
        const subject = isEN ? `Status Update: ${getStageLabel(targetStage, "en")}` : `Status-Update: ${getStageLabel(targetStage, "de")}`;
        const body = isEN
          ? `Dear ${applicantName || ''},\n\nYour application status has been updated to: ${getStageLabel(targetStage, "en")}.\n\n${reason ? `Note: ${reason}\n\n` : ''}Best regards,\nStudienkolleg Aachen`
          : `Guten Tag ${applicantName || ''},\n\nIhr Bewerbungsstatus wurde aktualisiert auf: ${getStageLabel(targetStage, "de")}.\n\n${reason ? `Hinweis: ${reason}\n\n` : ''}Mit freundlichen Gruessen,\nStudienkolleg Aachen`;
        await apiClient.post(`/api/applications/${appId}/send-email`, { subject, body, lang: aLang }, { withCredentials: true }).catch(() => {});
      }
      if (createTask && taskTitle.trim()) {
        const d = new Date(); d.setDate(d.getDate() + 3);
        await apiClient.post('/api/tasks', { title: taskTitle, application_id: appId, priority: isTerminal ? 'high' : 'normal', due_date: d.toISOString().slice(0, 10), description: `Auto-Aufgabe: ${getStageLabel(targetStage, "de")}` }, { withCredentials: true }).catch(() => {});
      }
      toast.success(`Status geaendert: ${getStageLabel(targetStage, "de")}`);
      onComplete(targetStage);
    } catch { toast.error('Fehler'); } finally { setSubmitting(false); }
  };

  return (
    <PopUpModal open={true} onClose={onCancel} title="Status aendern" icon={RefreshCw} maxWidth="480px" testId="stage-change-dialog">
      <div className="space-y-4">
        <p className="text-xs text-[var(--color-text-secondary)]">{getStageLabel(currentStage, "de")} → <strong className="text-[var(--color-primary)]">{getStageLabel(targetStage, "de")}</strong></p>
        {isTerminal && (
          <div className="bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)] rounded-[var(--radius-sm)] p-3 text-xs text-[var(--color-danger)] flex items-start gap-2">
            <AlertTriangle size={14} className="shrink-0 mt-0.5" /><span>Achtung: Terminaler Status. Der Bewerber wird als {getStageLabel(targetStage, "de")} markiert.</span>
          </div>
        )}
        <div><label className="w2g-label">Grund / Kommentar {isTerminal && '*'}</label><textarea value={reason} onChange={e => setReason(e.target.value)} placeholder="Warum wird der Status geaendert?" rows={2} className="w2g-input w-full text-sm resize-none" data-testid="stage-change-reason" /></div>
        <label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={sendNotification} onChange={e => setSendNotification(e.target.checked)} className="rounded border-[var(--color-divider)] text-[var(--color-primary)]" data-testid="stage-change-notify" /><span className="text-xs">Bewerber per E-Mail benachrichtigen</span></label>
        <label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={createTask} onChange={e => setCreateTask(e.target.checked)} className="rounded border-[var(--color-divider)] text-[var(--color-primary)]" /><span className="text-xs">Folgeaufgabe erstellen</span></label>
        {createTask && <input value={taskTitle} onChange={e => setTaskTitle(e.target.value)} placeholder="Aufgabentitel..." className="w2g-input w-full text-sm" />}
        <div className="flex justify-end gap-2 pt-2">
          <button onClick={onCancel} className="w2g-btn-secondary text-xs">Abbrechen</button>
          <button onClick={execute} disabled={submitting || (isTerminal && !reason.trim())} className="w2g-btn-primary text-xs" data-testid="stage-change-confirm">{submitting ? <Loader2 size={13} className="animate-spin" /> : 'Bestaetigen'}</button>
        </div>
      </div>
    </PopUpModal>
  );
}

/* ══════════════════════════════════════════════════════════════
   HAUPTKOMPONENTE: ApplicantDetailPage
   ══════════════════════════════════════════════════════════════ */
export default function ApplicantDetailPage() {
  const { id } = useParams();
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [app, setApp] = useState(null);
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [stageDialog, setStageDialog] = useState(null);
  const [rejectDocModal, setRejectDocModal] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [rejectSubmitting, setRejectSubmitting] = useState(false);
  const [previewDoc, setPreviewDoc] = useState(null);

  /* PopUp States */
  const [popup, setPopup] = useState(null); // 'tasks' | 'invoices' | 'notes' | 'followups' | 'history' | 'email' | 'message' | 'teacher' | 'createInvoice'

  /* STAGES nun im StageProgressBar integriert */

  useEffect(() => {
    const load = async () => {
      try {
        const [appRes, docsRes] = await Promise.all([apiClient.get(`/api/applications/${id}`), apiClient.get(`/api/applications/${id}/documents`)]);
        setApp(appRes.data); setDocs(docsRes.data);
      } catch {} finally { setLoading(false); }
    };
    load();
  }, [id, refreshKey]);

  const refresh = () => setRefreshKey(k => k + 1);
  const saveProfileField = async (field, value) => { try { await apiClient.put(`/api/applications/${id}/profile`, { [field]: value }); setApp(prev => ({ ...prev, applicant: { ...prev.applicant, [field]: value } })); refresh(); } catch {} };
  const saveAppField = async (field, value) => { try { await apiClient.put(`/api/applications/${id}`, { [field]: value }); setApp(prev => ({ ...prev, [field]: value })); refresh(); } catch {} };

  if (loading) return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 size={32} className="animate-spin text-[var(--color-primary)]" /><p className="ml-3 text-sm text-[var(--color-text-secondary)]">Fallakte wird geladen...</p></div>;
  if (!app) return <div className="p-6 text-[var(--color-text-secondary)]">Bewerbung nicht gefunden</div>;

  const whatsappUrl = app.applicant?.phone ? `https://wa.me/${app.applicant.phone.replace(/[^0-9+]/g, '').replace('+', '')}?text=${encodeURIComponent(`Hallo ${app.applicant?.full_name || ''}, hier ist das Team vom Studienkolleg Aachen. `)}` : null;
  const docsApproved = docs.filter(d => d.status === 'approved').length;
  const docsPending = docs.filter(d => d.status === 'uploaded' || d.status === 'in_review').length;

  return (
    <div className="space-y-3 animate-fade-in" data-testid="applicant-detail-page">

      {/* ═══ 1. STATUS-BALKEN (GANZ OBEN – klickbar fuer Statuswechsel) ═══ */}
      <StageProgressBar currentStage={app.current_stage} onStageClick={(stage) => stage !== app.current_stage && setStageDialog(stage)} />

      {stageDialog && <StageChangeDialog currentStage={app.current_stage} targetStage={stageDialog} appId={id} applicantName={app.applicant?.full_name} applicantEmail={app.applicant?.email} applicantLang={app.applicant?.language_pref} onComplete={(s) => { setApp(p => ({ ...p, current_stage: s })); setStageDialog(null); refresh(); }} onCancel={() => setStageDialog(null)} />}

      {/* ═══ 2. KOPFZEILE (Name + Kurzinfos integriert) ═══════════════════ */}
      <Card style={{ borderLeft: '4px solid var(--color-primary)' }} data-testid="case-header">
        <CardContent className="py-3.5">
          <div className="flex items-center gap-4 flex-wrap">
            <Link to="/staff/kanban" className="w-9 h-9 rounded-[var(--radius-sm)] flex items-center justify-center bg-[var(--color-surface-sunken)] hover:bg-[var(--color-primary)]/10 text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] transition-all" data-testid="back-to-kanban"><ArrowLeft size={16} /></Link>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 flex-wrap">
                <h1 className="text-lg font-bold tracking-tight" style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}>{app.applicant?.full_name || 'Bewerber'}</h1>
                {app.applicant_number && <span className="text-xs font-mono tracking-wide px-2 py-0.5 rounded-[var(--radius-xs)] bg-[var(--color-primary)]/10 text-[var(--color-primary)] font-bold" data-testid="applicant-number-badge">{app.applicant_number}</span>}
                <Badge variant="default" data-testid="case-stage-badge">{getStageLabel(app.current_stage, "de")}</Badge>
              </div>
              <div className="flex items-center gap-3 mt-1 text-[11px] text-[var(--color-text-secondary)] flex-wrap">
                {app.applicant?.email && <span className="flex items-center gap-1"><Mail size={10} /> {app.applicant.email}</span>}
                {app.applicant?.phone && <span className="flex items-center gap-1"><Phone size={10} /> {app.applicant.phone}</span>}
                {app.course_type && <span className="flex items-center gap-1"><GraduationCap size={10} /> {app.course_type}</span>}
                {app.degree_country && <span className="flex items-center gap-1 font-medium">{app.degree_country}</span>}
                {app.language_level && <span className="flex items-center gap-1">Deutsch: <strong>{app.language_level}</strong></span>}
                <span className="flex items-center gap-1"><FileText size={10} /> {docsApproved}/{docs.length} Dokumente{docsPending > 0 && <span className="text-[var(--color-warning)]">({docsPending} offen)</span>}</span>
                {app.source && <span className="text-[var(--color-text-tertiary)]">{SOURCE_LABELS[app.source] || app.source}</span>}
              </div>
            </div>
            <a href={`${API}/api/applications/${id}/pdf`} target="_blank" rel="noopener noreferrer" data-testid="action-pdf-download" className="w2g-btn-primary text-sm px-4 py-2">
              <Download size={14} /> Fallakte PDF
            </a>
          </div>
        </CardContent>
      </Card>

      {/* ═══ 3. ARBEITSBEREICH: Daten nebeneinander ══════════════════ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <InfoCard title="Persoenliche Daten" icon={Users} testId="personal-data-card">
            <dl className="divide-y divide-[var(--color-divider-subtle)]">
              <EditableField label="Name" value={app.applicant?.full_name} field="full_name" onSave={saveProfileField} />
              <EditableField label="E-Mail" value={app.applicant?.email} field="email" onSave={saveProfileField} />
              <EditableField label="Telefon" value={app.applicant?.phone} field="phone" onSave={saveProfileField} />
              <EditableField label="Land" value={app.applicant?.country} field="country" onSave={saveProfileField} />
              <EditableField label="Geb.-Datum" value={app.date_of_birth} field="date_of_birth" onSave={saveAppField} type="date" />
            </dl>
        </InfoCard>
        <InfoCard title="Bewerbungsdaten" icon={BookOpen} testId="application-data-card">
            <dl className="divide-y divide-[var(--color-divider-subtle)]">
              <EditableField label="Kurstyp" value={app.course_type} field="course_type" onSave={saveAppField} />
              <EditableField label="Bew.-Nr." value={app.applicant_number} field="applicant_number" onSave={() => {}} displayValue={app.applicant_number || '-'} />
              <EditableField label="Semester" value={app.desired_start} field="desired_start" onSave={saveAppField} />
              <EditableField label="Deutsch" value={app.language_level} field="language_level" onSave={saveAppField} />
              <EditableField label="Abschlussland" value={app.degree_country} field="degree_country" onSave={saveAppField} />
              <EditableField label="Kombination" value={app.combo_option} field="combo_option" onSave={saveAppField} />
              <EditableField label="Quelle" value={app.source} field="source" onSave={saveAppField} displayValue={SOURCE_LABELS[app.source] || app.source} />
            </dl>
        </InfoCard>
      </div>

      {/* ═══ 4. DOKUMENTE (Doppelklick zum Oeffnen) ════════════════ */}
      <InfoCard title={`Dokumente (${docs.length})`} icon={FileText} noPadding testId="documents-section">
        <div className="px-5 pb-4 pt-2">
          <StaffDocUpload appId={id} onUploaded={refresh} />
          {docs.length === 0 ? (
            <div className="text-center py-5 border border-dashed border-[var(--color-divider)] rounded-[var(--radius-sm)] bg-[var(--color-surface-elevated)] mt-3" data-testid="docs-empty-state">
              <FileText size={20} className="mx-auto text-[var(--color-text-tertiary)] mb-2" />
              <p className="text-xs text-[var(--color-text-secondary)] mb-2">Keine Dokumente hochgeladen</p>
            </div>
          ) : (
            <ul className="space-y-2 mt-3">
              {docs.map(doc => {
                const s = DOC_STATUS[doc.status] || DOC_STATUS.uploaded;
                const Icon = s.icon;
                const canPreview = doc.has_binary && (doc.content_type === 'application/pdf' || doc.filename?.endsWith('.pdf') || doc.content_type?.startsWith('image/'));
                return (
                  <li key={doc.id}
                    className={`border rounded-[var(--radius-sm)] p-3 cursor-pointer transition-colors ${doc.staff_decision_required ? 'border-[var(--color-warning-border)] bg-[var(--color-warning-bg)]/50' : 'border-[var(--color-divider-subtle)] hover:border-[var(--color-primary)]/30'}`}
                    onDoubleClick={() => canPreview && setPreviewDoc(doc)}
                    title="Doppelklick zum Oeffnen"
                    data-testid={`doc-${doc.id}`}>
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2 min-w-0 flex-1">
                        <FileText size={14} className="text-[var(--color-text-tertiary)] shrink-0" />
                        <div className="min-w-0">
                          <p className="text-xs text-[var(--color-text-primary)] font-medium truncate">{doc.filename || DOC_TYPE_LABELS[doc.document_type] || doc.document_type}</p>
                          <p className="text-[10px] text-[var(--color-text-tertiary)]">{DOC_TYPE_LABELS[doc.document_type] || doc.document_type}{doc.file_size ? ` · ${(doc.file_size / 1024).toFixed(0)} KB` : ''}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {canPreview && <button onClick={(e) => { e.stopPropagation(); setPreviewDoc(doc); }} className="text-[var(--color-primary)] hover:text-[var(--color-accent)]" title="Vorschau" data-testid={`doc-preview-${doc.id}`}><Eye size={13} /></button>}
                        {doc.has_binary && <a href={`${API}/api/documents/${doc.id}/download`} download={doc.filename} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)]" title="Herunterladen" data-testid={`doc-download-${doc.id}`} onClick={e => e.stopPropagation()}><Download size={13} /></a>}
                        <span className={`flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-sm ${s.color}`}><Icon size={11} />{s.label}</span>
                      </div>
                    </div>
                    {doc.validation_status && (
                      <div className="mt-1.5 pt-1.5 border-t border-[var(--color-divider-subtle)]">
                        <div className="flex items-center gap-3 text-[10px]">
                          <span className={`px-1.5 py-0.5 rounded-sm font-medium ${doc.validation_status === 'validated' ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]' : doc.validation_status === 'rejected' ? 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]' : doc.validation_status === 'needs_review' ? 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>{doc.validation_status === 'validated' ? 'Validiert' : doc.validation_status === 'rejected' ? 'Abgelehnt' : doc.validation_status === 'needs_review' ? 'Pruefung noetig' : doc.validation_status}</span>
                        </div>
                      </div>
                    )}
                    {(doc.staff_decision_required || doc.status === 'in_review' || doc.status === 'uploaded') && (
                      <div className="mt-2 flex items-center gap-1.5">
                        <button onClick={async (e) => { e.stopPropagation(); try { await apiClient.put(`/api/documents/${doc.id}/review`, { status: 'approved' }, { withCredentials: true }); toast.success('Akzeptiert'); refresh(); } catch { toast.error('Fehler'); } }} className="w2g-btn-table-action" data-testid={`doc-approve-${doc.id}`}><CheckCircle size={10} />Akzeptieren</button>
                        <button onClick={(e) => { e.stopPropagation(); setRejectDocModal(doc.id); setRejectReason(''); }} className="w2g-btn-table-secondary border-[var(--color-danger-border)] text-[var(--color-danger)] hover:bg-[var(--color-danger)] hover:text-white" data-testid={`doc-reject-${doc.id}`}><XCircle size={10} />Ablehnen</button>
                        <button onClick={async (e) => { e.stopPropagation(); try { await apiClient.post(`/api/documents/${doc.id}/revalidate`, {}, { withCredentials: true }); toast.success('Re-Validierung gestartet'); refresh(); } catch { toast.error('Fehler'); } }} className="w2g-btn-table-secondary" data-testid={`doc-revalidate-${doc.id}`}><RefreshCw size={10} />Erneut pruefen</button>
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </InfoCard>

      {/* ═══ 5. KI-SCREENING ════════════════════════════════════════ */}
      <AIScreeningDeltaPanel applicationId={id} />

      {/* ═══ 5b. QUALIFIZIERUNGSPFAD ═══════════════════════════════ */}
      <QualificationPathPanel applicationId={id} lang={lang} />

      {/* ═══ 6. AKTIONSLEISTE (ganz unten, logisch gruppiert) ══════════ */}
      <Card className="p-0" data-testid="action-toolbar">
        <div className="grid grid-cols-3 divide-x divide-[var(--color-divider-subtle)]">
          {/* ── Kontakt ── */}
          <div className="px-4 py-3">
            <p className="text-[9px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-[0.1em] mb-2">Kontakt</p>
            <div className="flex flex-wrap gap-1.5">
              {app.applicant?.phone && <a href={`tel:${app.applicant.phone.replace(/\s/g, '')}`} className="w2g-btn-secondary text-xs" data-testid="action-call"><Phone size={12} /> Anrufen</a>}
              <button onClick={() => setPopup('email')} className="w2g-btn-secondary text-xs" data-testid="action-email"><Mail size={12} /> E-Mail</button>
              {whatsappUrl && <a href={whatsappUrl} target="_blank" rel="noopener noreferrer" className="w2g-btn-secondary text-xs" data-testid="action-whatsapp"><MessageCircle size={12} /> WhatsApp</a>}
              <button onClick={() => setPopup('message')} className="w2g-btn-secondary text-xs" data-testid="action-portal-msg"><Send size={12} /> Portal</button>
            </div>
          </div>
          {/* ── Aktionen ── */}
          <div className="px-4 py-3">
            <p className="text-[9px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-[0.1em] mb-2">Aktionen</p>
            <div className="flex flex-wrap gap-1.5">
              <button onClick={() => setPopup('tasks')} className="w2g-btn-secondary text-xs" data-testid="action-tasks"><CheckSquare size={12} /> Aufgaben</button>
              <a href="/staff/appointments" className="w2g-btn-secondary text-xs" data-testid="action-appointments"><CalendarClock size={12} /> Termin</a>
              <button onClick={() => setPopup('createInvoice')} className="w2g-btn-primary text-xs" data-testid="action-invoice"><Receipt size={12} /> Rechnung</button>
              <button onClick={() => setPopup('invoices')} className="w2g-btn-outline text-xs" data-testid="action-invoices"><Receipt size={12} /> Rechnungen</button>
            </div>
          </div>
          {/* ── Verwalten ── */}
          <div className="px-4 py-3">
            <p className="text-[9px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-[0.1em] mb-2">Verwalten</p>
            <div className="flex flex-wrap gap-1.5">
              <button onClick={() => setPopup('notes')} className="w2g-btn-secondary text-xs" data-testid="action-notes"><StickyNote size={12} /> Notizen</button>
              <button onClick={() => setPopup('followups')} className="w2g-btn-secondary text-xs" data-testid="action-followups"><CalendarClock size={12} /> Wiedervorlagen</button>
              <button onClick={() => setPopup('teacher')} className="w2g-btn-secondary text-xs" data-testid="action-teacher"><GraduationCap size={12} /> Lehrer</button>
              <button onClick={() => setPopup('history')} className="w2g-btn-secondary text-xs" data-testid="action-history"><History size={12} /> Aktivitaeten</button>
            </div>
          </div>
        </div>
      </Card>

      {/* ═══ ALLE POPUP-MODALS ═════════════════════════════════════ */}
      <PopUpModal open={popup === 'tasks'} onClose={() => setPopup(null)} title={`Aufgaben · ${app.applicant?.full_name}`} icon={CheckSquare} maxWidth="700px" testId="tasks-popup">
        <TasksPopupContent appId={id} applicantName={app.applicant?.full_name} />
      </PopUpModal>

      <PopUpModal open={popup === 'invoices'} onClose={() => setPopup(null)} title={`Rechnungsverlauf · ${app.applicant?.full_name}`} icon={Receipt} maxWidth="750px" testId="invoices-popup">
        <InvoicesPopupContent applicantId={app.applicant_id || id} appId={id} applicantName={app.applicant?.full_name} onCreateNew={() => setPopup('createInvoice')} />
      </PopUpModal>

      <PopUpModal open={popup === 'notes'} onClose={() => setPopup(null)} title={`Notizen · ${app.applicant?.full_name}`} icon={StickyNote} maxWidth="600px" testId="notes-popup">
        <NotesPopupContent appId={id} />
      </PopUpModal>

      <PopUpModal open={popup === 'followups'} onClose={() => setPopup(null)} title={`Wiedervorlagen · ${app.applicant?.full_name}`} icon={CalendarClock} maxWidth="600px" testId="followups-popup">
        <FollowupsPopupContent appId={id} />
      </PopUpModal>

      <PopUpModal open={popup === 'history'} onClose={() => setPopup(null)} title={`Verlauf · ${app.applicant?.full_name}`} icon={History} maxWidth="650px" testId="history-popup">
        <HistoryPopupContent appId={id} />
      </PopUpModal>

      <PopUpModal open={popup === 'email'} onClose={() => setPopup(null)} title={`E-Mail an ${app.applicant?.full_name || 'Bewerber'}`} icon={Mail} maxWidth="600px" testId="email-popup">
        <EmailComposerContent appId={id} applicantEmail={app.applicant?.email} applicantName={app.applicant?.full_name} onSent={() => { setPopup(null); refresh(); }} />
      </PopUpModal>

      <PopUpModal open={popup === 'message'} onClose={() => setPopup(null)} title="Portal-Nachricht" icon={MessageCircle} maxWidth="500px" testId="msg-popup">
        <PortalMessageContent appId={id} applicantId={app.applicant_id} applicantName={app.applicant?.full_name} onSent={() => { setPopup(null); refresh(); }} />
      </PopUpModal>

      <PopUpModal open={popup === 'teacher'} onClose={() => setPopup(null)} title="Lehrer-Zuweisung" icon={GraduationCap} maxWidth="480px" testId="teacher-popup">
        <TeacherPopupContent applicantId={app.applicant_id || id} applicantName={app.applicant?.full_name} />
      </PopUpModal>

      {popup === 'createInvoice' && (
        <InvoiceCreateModal
          applicant={{ id: app.applicant_id, application_id: app.id, full_name: app.applicant?.full_name, applicant_number: app.applicant_number || app.id?.slice(-6).toUpperCase() }}
          onClose={() => setPopup(null)} onCreated={() => { setPopup(null); refresh(); }} />
      )}

      {/* Dokumenten-Vorschau Modal */}
      {previewDoc && (
        <div className="w2g-modal-overlay" onClick={() => setPreviewDoc(null)} data-testid="doc-preview-modal">
          <div className="w2g-modal" style={{ maxWidth: '900px', height: '85vh' }} onClick={e => e.stopPropagation()}>
            <div className="w2g-modal-header">
              <div className="min-w-0 flex-1">
                <h3 className="font-heading text-base font-bold text-[var(--color-primary)] truncate">{previewDoc.filename}</h3>
                <p className="text-[11px] text-[var(--color-text-tertiary)]">{DOC_TYPE_LABELS[previewDoc.document_type] || previewDoc.document_type}</p>
              </div>
              <button onClick={() => setPreviewDoc(null)} className="w2g-btn-icon" data-testid="preview-close"><X size={16} /></button>
            </div>
            <div className="flex-1 overflow-hidden" style={{ height: 'calc(85vh - 130px)' }}>
              {(previewDoc.content_type === 'application/pdf' || previewDoc.filename?.endsWith('.pdf')) ? (
                <iframe src={`${API}/api/documents/${previewDoc.id}/download#toolbar=1`} className="w-full h-full border-0" title={previewDoc.filename} />
              ) : previewDoc.content_type?.startsWith('image/') ? (
                <div className="w-full h-full flex items-center justify-center bg-[var(--color-surface-sunken)] p-4">
                  <img src={`${API}/api/documents/${previewDoc.id}/download`} alt={previewDoc.filename} className="max-w-full max-h-full object-contain rounded-[var(--radius-sm)]" />
                </div>
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center gap-4"><FileText size={48} className="text-[var(--color-text-tertiary)]" /><p className="text-sm text-[var(--color-text-secondary)]">Vorschau nicht verfuegbar</p></div>
              )}
            </div>
            <div className="w2g-modal-footer">
              <a href={`${API}/api/documents/${previewDoc.id}/download`} target="_blank" rel="noopener noreferrer" className="w2g-btn-secondary text-sm">Herunterladen</a>
              <button onClick={() => setPreviewDoc(null)} className="w2g-btn-primary text-sm">Schliessen</button>
            </div>
          </div>
        </div>
      )}

      {/* Dokument-Ablehnungs-Modal */}
      {rejectDocModal && (
        <PopUpModal open={true} onClose={() => setRejectDocModal(null)} title="Dokument ablehnen" icon={XCircle} maxWidth="420px" testId="reject-doc-modal">
          <div className="space-y-4">
            <div><label className="w2g-label">Ablehnungsgrund</label><textarea value={rejectReason} onChange={e => setRejectReason(e.target.value)} placeholder="Bitte geben Sie den Grund der Ablehnung an..." rows={3} className="w2g-input w-full text-sm resize-none" autoFocus data-testid="reject-doc-reason" /></div>
            <p className="text-xs text-[var(--color-text-tertiary)]">Der Bewerber wird ueber die Ablehnung informiert und kann das Dokument erneut hochladen.</p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setRejectDocModal(null)} className="w2g-btn-secondary text-sm">Abbrechen</button>
              <button onClick={async () => {
                if (!rejectReason.trim()) { toast.error('Bitte Ablehnungsgrund angeben'); return; }
                setRejectSubmitting(true);
                try { await apiClient.put(`/api/documents/${rejectDocModal}/review`, { status: 'rejected', rejection_reason: rejectReason }, { withCredentials: true }); toast.success('Dokument abgelehnt'); setRejectDocModal(null); refresh(); } catch { toast.error('Fehler'); } finally { setRejectSubmitting(false); }
              }} disabled={rejectSubmitting || !rejectReason.trim()} className="w2g-btn-primary text-sm" data-testid="reject-doc-confirm">
                {rejectSubmitting ? <Loader2 size={14} className="animate-spin" /> : 'Ablehnen'}
              </button>
            </div>
          </div>
        </PopUpModal>
      )}
    </div>
  );
}


/* ═══ Qualifizierungspfad-Panel ═══════════════════════════════════ */
function QualificationPathPanel({ applicationId, lang }) {
  const [path, setPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [computing, setComputing] = useState(false);

  useEffect(() => {
    apiClient.get(`/api/applications/${applicationId}/qualification-path`, { withCredentials: true })
      .then(r => setPath(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [applicationId]);

  const compute = async () => {
    setComputing(true);
    try {
      const r = await apiClient.post(`/api/applications/${applicationId}/compute-qualification`, {}, { withCredentials: true });
      setPath(r.data);
      toast.success(lang === 'de' ? 'Qualifizierungspfad berechnet' : 'Qualification path computed');
    } catch { toast.error(lang === 'de' ? 'Berechnung fehlgeschlagen' : 'Computation failed'); }
    finally { setComputing(false); }
  };

  if (loading) return null;
  const isComputed = path && path.recommended_path && path.recommended_path !== 'not_computed';

  const PATH_ICONS = {
    direktstudium: '🎓', studienkolleg: '🏫', feststellungspruefung: '📝',
    testas: '📊', sprachkurs_zuerst: '💬', pflegeausbildung: '🏥',
    berufsausbildung: '🔧', anpassungslehrgang: '📋', manuelle_pruefung: '👤',
  };

  const PATH_COLORS = {
    direktstudium: 'border-l-[var(--color-success)] bg-[var(--color-success-bg)]',
    studienkolleg: 'border-l-[var(--color-primary)] bg-[var(--color-primary)]/5',
    feststellungspruefung: 'border-l-[var(--color-info)] bg-[var(--color-info-bg)]',
    testas: 'border-l-[var(--color-accent)] bg-[var(--color-accent-muted)]',
    sprachkurs_zuerst: 'border-l-[var(--color-warning)] bg-[var(--color-warning-bg)]',
    pflegeausbildung: 'border-l-[#EC4899] bg-pink-50',
    manuelle_pruefung: 'border-l-[var(--color-text-tertiary)] bg-[var(--color-surface-elevated)]',
  };

  return (
    <InfoCard title={lang === 'de' ? 'Qualifizierungspfad' : 'Qualification Path'} testId="qualification-path-panel">
      {!isComputed ? (
        <div className="text-center py-4">
          <p className="text-xs text-[var(--color-text-secondary)] mb-3">
            {lang === 'de' ? 'Noch kein Qualifizierungspfad berechnet.' : 'No qualification path computed yet.'}
          </p>
          <button onClick={compute} disabled={computing} className="w2g-btn-primary text-xs" data-testid="compute-qualification-btn">
            {computing ? <Loader2 size={12} className="animate-spin" /> : <GraduationCap size={12} />}
            {lang === 'de' ? 'Jetzt berechnen' : 'Compute Now'}
          </button>
        </div>
      ) : (
        <div className="space-y-3" data-testid="qualification-path-result">
          {/* Pfad-Empfehlung */}
          <div className={`border-l-[3px] rounded-r-[var(--radius-sm)] p-3 ${PATH_COLORS[path.recommended_path] || PATH_COLORS.manuelle_pruefung}`}>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg">{PATH_ICONS[path.recommended_path] || '📋'}</span>
              <span className="text-sm font-bold text-[var(--color-text-primary)]" data-testid="qualification-path-label">
                {lang === 'de' ? path.path_label_de : path.path_label_en}
              </span>
            </div>
            <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed" data-testid="qualification-path-reason">
              {lang === 'de' ? path.reason_de : path.reason_en}
            </p>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-3 gap-2 text-[10px]">
            <div className="p-2 bg-[var(--color-surface-elevated)] rounded-[var(--radius-xs)]">
              <span className="text-[var(--color-text-tertiary)]">Anabin</span>
              <p className="font-bold text-[var(--color-text-primary)]">{path.anabin_category || '–'}</p>
            </div>
            <div className="p-2 bg-[var(--color-surface-elevated)] rounded-[var(--radius-xs)]">
              <span className="text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Sprache' : 'Language'}</span>
              <p className={`font-bold ${path.language_sufficient ? 'text-[var(--color-success)]' : 'text-[var(--color-danger)]'}`}>
                {path.language_level || '–'} {path.language_sufficient ? '✓' : '✗'}
              </p>
            </div>
            <div className="p-2 bg-[var(--color-surface-elevated)] rounded-[var(--radius-xs)]">
              <span className="text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Konfidenz' : 'Confidence'}</span>
              <p className="font-bold text-[var(--color-text-primary)]">{path.confidence || '–'}</p>
            </div>
          </div>

          {/* Naechste Schritte */}
          <div>
            <p className="text-[9px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-wider mb-1">
              {lang === 'de' ? 'Naechste Schritte' : 'Next Steps'}
            </p>
            <ol className="space-y-1">
              {(lang === 'de' ? path.next_steps_de : path.next_steps_en || []).map((step, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-[var(--color-text-secondary)]">
                  <span className="w-4 h-4 shrink-0 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center text-[9px] font-bold mt-0.5">{i + 1}</span>
                  {step}
                </li>
              ))}
            </ol>
          </div>

          {/* Staff-Entscheid Badge */}
          {path.requires_staff_decision && (
            <div className="flex items-center gap-2 p-2 bg-[var(--color-warning-bg)] border border-[var(--color-warning-border)] rounded-[var(--radius-sm)]" data-testid="staff-decision-required">
              <AlertTriangle size={14} className="text-[var(--color-warning)] shrink-0" />
              <span className="text-[10px] font-medium text-[var(--color-warning)]">
                {lang === 'de' ? 'Staff-Entscheidung erforderlich' : 'Staff decision required'}
              </span>
            </div>
          )}

          {/* Neu berechnen */}
          <button onClick={compute} disabled={computing} className="w2g-btn-outline text-[10px] w-full" data-testid="recompute-qualification-btn">
            {computing ? <Loader2 size={10} className="animate-spin" /> : <RefreshCw size={10} />}
            {lang === 'de' ? 'Neu berechnen' : 'Recompute'}
          </button>
        </div>
      )}
    </InfoCard>
  );
}
