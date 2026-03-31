import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../../lib/apiClient';
import { toast } from 'sonner';
import { STAGE_LABELS, STAGE_COLORS } from '../../lib/utils';
import {
  ArrowLeft, Brain, RefreshCw, CheckCircle, AlertCircle,
  FileText, Clock, XCircle, ChevronDown, ChevronUp, Loader2,
  Phone, Mail, MessageCircle, Users, GraduationCap, Trash2,
  Edit3, Save, X, Send, StickyNote, History, CalendarClock, Plus
} from 'lucide-react';
import { RecordHeader } from '../../components/shared/crmPatterns';

/* ═══════ Followup / Wiedervorlage Panel ═══════ */
function FollowupPanel({ appId }) {
  const [followups, setFollowups] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ due_date: '', reason: '' });
  const [creating, setCreating] = useState(false);

  const loadFollowups = useCallback(async () => {
    try {
      const r = await apiClient.get('/api/followups', { withCredentials: true });
      setFollowups((r.data || []).filter(f => f.application_id === appId));
    } catch {}
  }, [appId]);

  useEffect(() => { loadFollowups(); }, [loadFollowups]);

  const create = async () => {
    if (!form.due_date || !form.reason) return;
    setCreating(true);
    try {
      await apiClient.post('/api/followups', {
        application_id: appId,
        due_date: form.due_date,
        reason: form.reason,
      }, { withCredentials: true });
      setForm({ due_date: '', reason: '' });
      setShowCreate(false);
      await loadFollowups();
    } catch {} finally { setCreating(false); }
  };

  const markDone = async (id) => {
    try {
      await apiClient.put(`/api/followups/${id}`, { status: 'done' }, { withCredentials: true });
      await loadFollowups();
    } catch {}
  };

  const dismiss = async (id) => {
    try {
      await apiClient.delete(`/api/followups/${id}`, { withCredentials: true });
      await loadFollowups();
    } catch {}
  };

  return (
    <div className="bg-white border border-slate-200 rounded-sm p-4" data-testid="followup-panel">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-slate-700 text-xs flex items-center gap-1.5">
          <CalendarClock size={14} className="text-primary" /> Wiedervorlagen ({followups.length})
        </h3>
        <button onClick={() => setShowCreate(!showCreate)} data-testid="create-followup-btn"
          className="text-[10px] text-primary hover:underline flex items-center gap-1">
          <Plus size={12} /> Neu
        </button>
      </div>

      {showCreate && (
        <div className="border border-slate-200 rounded-sm p-3 mb-3 space-y-2 bg-slate-50" data-testid="followup-create-form">
          <input type="date" value={form.due_date} onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))}
            data-testid="followup-date" className="w-full text-xs border border-slate-200 rounded-sm px-2 py-1.5 focus:outline-none focus:border-primary" />
          <input value={form.reason} onChange={e => setForm(f => ({ ...f, reason: e.target.value }))}
            placeholder="Grund / Aktion..."
            data-testid="followup-reason" className="w-full text-xs border border-slate-200 rounded-sm px-2 py-1.5 focus:outline-none focus:border-primary" />
          <button onClick={create} disabled={creating || !form.due_date || !form.reason}
            data-testid="followup-submit" className="text-[11px] bg-primary text-white px-3 py-1.5 rounded-sm hover:bg-primary/90 disabled:opacity-50">
            {creating ? <Loader2 size={12} className="animate-spin" /> : 'Erstellen'}
          </button>
        </div>
      )}

      {followups.length === 0 ? (
        <p className="text-[10px] text-slate-400">Keine Wiedervorlagen</p>
      ) : (
        <div className="space-y-1.5">
          {followups.map(f => (
            <div key={f.id} className={`flex items-start justify-between border rounded-sm p-2 text-xs ${
              f.status === 'done' ? 'border-primary/15 bg-primary/5' : 'border-slate-100 bg-slate-50/50'
            }`} data-testid={`followup-item-${f.id}`}>
              <div className="min-w-0">
                <p className={`font-medium ${f.status === 'done' ? 'text-primary line-through' : 'text-slate-700'}`}>{f.reason}</p>
                <p className="text-[10px] text-slate-400">Fällig: {f.due_date}</p>
              </div>
              {f.status !== 'done' && (
                <div className="flex items-center gap-1 shrink-0 ml-2">
                  <button onClick={() => markDone(f.id)} data-testid={`followup-done-${f.id}`}
                    className="text-primary hover:bg-primary/10 p-0.5 rounded"><CheckCircle size={13} /></button>
                  <button onClick={() => dismiss(f.id)} data-testid={`followup-dismiss-${f.id}`}
                    className="text-slate-400 hover:text-red-500 p-0.5 rounded"><Trash2 size={13} /></button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ═══════ Teacher Assignment Panel ═══════ */
function TeacherAssignmentPanel({ applicantId, applicantName }) {
  const [teachers, setTeachers] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState('');
  const [showPicker, setShowPicker] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [assignRes, usersRes] = await Promise.all([
        apiClient.get('/api/teacher/assignments'),
        apiClient.get('/api/teacher/list'),
      ]);
      const all = assignRes.data.assignments || [];
      setAssignments(all.filter(a => a.applicant_id === applicantId));
      setTeachers((usersRes.data || []).filter(u => u.role === 'teacher' && u.active));
    } catch {} finally { setLoading(false); }
  }, [applicantId]);

  useEffect(() => { loadData(); }, [loadData]);

  const assign = async (tid) => {
    setActionLoading(tid);
    try { await apiClient.post(`/api/teacher/assignments?applicant_id=${applicantId}&teacher_id=${tid}`); await loadData(); setShowPicker(false); } catch {} finally { setActionLoading(''); }
  };
  const remove = async (tid) => {
    setActionLoading(tid);
    try { await apiClient.delete(`/api/teacher/assignments?applicant_id=${applicantId}&teacher_id=${tid}`); await loadData(); } catch {} finally { setActionLoading(''); }
  };

  const assignedIds = new Set(assignments.map(a => a.teacher_id));
  const available = teachers.filter(t => !assignedIds.has(t.id));

  if (loading) return <div className="bg-white border border-slate-200 rounded-sm p-4"><Loader2 size={16} className="animate-spin text-slate-400 mx-auto" /></div>;

  return (
    <div className="bg-white border border-slate-200 rounded-sm p-4 space-y-3" data-testid="teacher-assignment-panel">
      <div className="flex items-center justify-between">
        <h4 className="font-semibold text-slate-700 text-xs flex items-center gap-1.5"><GraduationCap size={14} className="text-primary" /> Lehrer-Zuweisung</h4>
        {available.length > 0 && <button onClick={() => setShowPicker(!showPicker)} data-testid="assign-teacher-btn" className="text-[11px] font-medium text-primary hover:underline">+ Zuweisen</button>}
      </div>
      {assignments.map(a => {
        const t = teachers.find(x => x.id === a.teacher_id);
        return (
          <div key={a.teacher_id} className="flex items-center justify-between border border-slate-100 rounded-sm px-3 py-2" data-testid={`assignment-${a.teacher_id}`}>
            <div className="flex items-center gap-2"><GraduationCap size={13} className="text-primary" /><span className="text-xs text-slate-700 font-medium">{t?.full_name || a.teacher_id}</span></div>
            <button onClick={() => remove(a.teacher_id)} disabled={actionLoading === a.teacher_id} className="text-slate-400 hover:text-red-500 p-1" data-testid={`remove-assignment-${a.teacher_id}`}>
              {actionLoading === a.teacher_id ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
            </button>
          </div>
        );
      })}
      {assignments.length === 0 && <p className="text-xs text-slate-400 text-center py-2">Kein Lehrer zugewiesen</p>}
      {showPicker && available.map(t => (
        <button key={t.id} onClick={() => assign(t.id)} disabled={actionLoading === t.id} data-testid={`pick-teacher-${t.id}`}
          className="w-full flex items-center justify-between px-3 py-2 bg-primary/5 border border-primary/20 rounded-sm text-left text-xs hover:bg-primary/10 transition">
          <span className="font-medium text-slate-700">{t.full_name || t.email}</span>
          {actionLoading === t.id ? <Loader2 size={12} className="animate-spin" /> : <span className="text-primary font-medium">Zuweisen</span>}
        </button>
      ))}
    </div>
  );
}

/* ═══════ AI Screening Panel ═══════ */
function AIScreeningPanel({ appId, currentStage, onStageAccepted }) {
  const [screenings, setScreenings] = useState([]);
  const [running, setRunning] = useState(false);
  const [accepting, setAccepting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  const load = useCallback(async () => {
    try { const res = await apiClient.get(`/api/applications/${appId}/ai-screenings`); setScreenings(res.data || []); } catch {} finally { setLoading(false); }
  }, [appId]);
  useEffect(() => { load(); }, [load]);

  const run = async () => { setRunning(true); try { await apiClient.post(`/api/applications/${appId}/ai-screen`); await load(); } catch {} finally { setRunning(false); } };

  const acceptSuggestion = async (suggestedStage) => {
    setAccepting(true);
    try {
      await apiClient.post(`/api/applications/${appId}/accept-ai-suggestion`, { suggested_stage: suggestedStage }, { withCredentials: true });
      if (onStageAccepted) onStageAccepted(suggestedStage);
      toast.success('KI-Vorschlag übernommen');
    } catch { toast.error('Fehler bei der Übernahme'); } finally { setAccepting(false); }
  };

  const latest = screenings[0];

  return (
    <div className="bg-white border border-slate-200 rounded-sm overflow-hidden" data-testid="ai-screening-panel">
      {/* Prominent header with CTA */}
      <div className="bg-primary/5 border-b border-primary/15 px-4 py-3 flex items-center justify-between">
        <h4 className="font-semibold text-primary text-sm flex items-center gap-2"><Brain size={16} className="text-primary" /> KI-Prüfung</h4>
        <button onClick={run} disabled={running} data-testid="ai-screening-run-btn"
          className="flex items-center gap-1.5 bg-primary text-white px-4 py-2 rounded-sm text-xs font-semibold hover:bg-primary/90 disabled:opacity-60 transition-colors shadow-sm">
          {running ? <Loader2 size={13} className="animate-spin" /> : <Brain size={13} />}
          {running ? 'KI analysiert...' : 'KI-Prüfung starten'}
        </button>
      </div>

      <div className="p-4 space-y-3">
        <div className="bg-slate-50 border border-slate-100 rounded-sm px-3 py-1.5"><p className="text-slate-500 text-[10px]">KI-Einschätzung – keine bindende Entscheidung.</p></div>
        {loading && <Loader2 size={16} className="animate-spin text-slate-400 mx-auto" />}
        {!loading && !latest && <p className="text-xs text-slate-400 text-center py-2">Noch keine KI-Prüfung durchgeführt</p>}
        {latest && (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-1.5">
              <div className={`rounded-sm p-2 text-center text-[10px] ${latest.is_complete ? 'bg-primary/8 text-primary' : 'bg-slate-50 text-slate-500'}`}>
                {latest.is_complete ? <CheckCircle size={13} className="mx-auto mb-0.5" /> : <AlertCircle size={13} className="mx-auto mb-0.5" />}
                {latest.is_complete ? 'Vollständig' : `${latest.missing_documents?.length || 0} fehlend`}
              </div>
              <div className="rounded-sm p-2 text-center text-[10px] bg-slate-50">Anabin: <strong>{latest.anabin_category || '–'}</strong></div>
              <div className={`rounded-sm p-2 text-center text-[10px] ${latest.language_level_ok ? 'bg-primary/8 text-primary' : 'bg-red-50 text-red-600'}`}>
                Sprache: {latest.language_level_ok ? 'OK' : 'Fehlt'}
              </div>
              <div className="rounded-sm p-2 text-center text-[10px] bg-slate-50">
                Formal: <strong>{latest.screening_breakdown?.formal_precheck?.status || '–'}</strong>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              <div className="border border-slate-200 rounded-sm p-2.5 bg-white">
                <p className="text-[11px] font-semibold text-slate-700 mb-1">Sicher belegt</p>
                <ul className="space-y-1 text-[11px] text-slate-600 list-disc pl-4">
                  {(latest.screening_breakdown?.completeness?.reasons || []).map((item, idx) => (
                    <li key={`complete-reason-${idx}`}>{item}</li>
                  ))}
                  {(latest.screening_breakdown?.formal_precheck?.reasons || []).map((item, idx) => (
                    <li key={`formal-reason-${idx}`}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="border border-slate-200 rounded-sm p-2.5 bg-slate-50">
                <p className="text-[11px] font-semibold text-slate-700 mb-1">Offen / kritisch</p>
                <ul className="space-y-1 text-[11px] text-slate-600 list-disc pl-4">
                  {(latest.screening_breakdown?.formal_precheck?.risks || []).map((item, idx) => (
                    <li key={`risk-${idx}`} className="text-red-600">{item}</li>
                  ))}
                  {(latest.screening_breakdown?.formal_precheck?.open_points || []).map((item, idx) => (
                    <li key={`open-${idx}`}>{item}</li>
                  ))}
                  {(!latest.screening_breakdown?.formal_precheck?.risks?.length && !latest.screening_breakdown?.formal_precheck?.open_points?.length) && (
                    <li>Keine offenen Punkte aus lokaler Vorprüfung.</li>
                  )}
                </ul>
              </div>
            </div>
            {latest.suggested_stage && (
              <div className="bg-primary/5 border-2 border-primary/25 rounded-sm p-3">
                <div className="flex items-center gap-2 mb-2">
                  <Brain size={14} className="text-primary" />
                  <span className="text-xs text-primary font-semibold">KI-Vorschlag: {STAGE_LABELS[latest.suggested_stage] || latest.suggested_stage}</span>
                </div>
                <div className="mb-2 rounded-sm border border-primary/15 bg-white p-2">
                  <p className="text-[10px] font-semibold text-slate-700 mb-1">Nächste Aktionen (Empfehlung)</p>
                  <ul className="space-y-0.5 text-[10px] text-slate-600 list-disc pl-4">
                    {(latest.next_actions || []).map((a, idx) => <li key={`next-action-${idx}`}>{a}</li>)}
                  </ul>
                </div>
                {latest.suggested_stage !== currentStage && (
                  <button
                    onClick={() => acceptSuggestion(latest.suggested_stage)}
                    disabled={accepting}
                    data-testid="ai-accept-suggestion-btn"
                    className="w-full flex items-center justify-center gap-2 bg-primary text-white px-3 py-2 rounded-sm text-xs font-semibold hover:bg-primary/90 disabled:opacity-60 transition-colors"
                  >
                    {accepting ? <Loader2 size={13} className="animate-spin" /> : <CheckCircle size={13} />}
                    {accepting ? 'Wird übernommen...' : 'Vorschlag übernehmen'}
                  </button>
                )}
                {latest.suggested_stage === currentStage && (
                  <p className="text-[10px] text-primary/70 text-center">Status stimmt bereits mit KI-Vorschlag überein.</p>
                )}
              </div>
            )}
            <div className="rounded-sm border border-slate-200 p-2 text-[10px] text-slate-500 bg-slate-50">
              Datenbasis: {latest.reference_basis?.note || 'Lokale Vorprüfungsregeln ohne Live-Referenzprüfung.'}
            </div>
            {latest.ai_report && (
              <div>
                <button onClick={() => setExpanded(expanded === 'report' ? null : 'report')} data-testid="ai-report-toggle"
                  className="w-full flex items-center justify-between text-[11px] text-slate-500 hover:text-primary py-1 border-t border-slate-100">
                  <span>Prüfungsbericht</span>{expanded === 'report' ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                </button>
                {expanded === 'report' && <pre className="text-[10px] text-slate-600 bg-slate-50 p-3 rounded-sm whitespace-pre-wrap mt-1" data-testid="ai-report-content">{latest.ai_report}</pre>}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

/* ═══════ Inline Edit Field ═══════ */
function EditableField({ label, value, field, onSave }) {
  const [editing, setEditing] = useState(false);
  const [val, setVal] = useState(value || '');
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setSaving(true);
    await onSave(field, val);
    setSaving(false);
    setEditing(false);
  };
  const cancel = () => { setVal(value || ''); setEditing(false); };

  return (
    <div className="flex items-start gap-2 py-1" data-testid={`field-${field}`}>
      <dt className="text-slate-500 text-xs w-24 shrink-0 pt-0.5">{label}:</dt>
      {editing ? (
        <div className="flex items-center gap-1 flex-1">
          <input value={val} onChange={e => setVal(e.target.value)} className="text-sm text-slate-800 border border-primary/30 rounded-sm px-2 py-0.5 flex-1 focus:outline-none focus:ring-1 focus:ring-primary" autoFocus />
          <button onClick={save} disabled={saving} className="text-primary hover:text-primary/80 p-0.5"><Save size={13} /></button>
          <button onClick={cancel} className="text-slate-400 hover:text-slate-600 p-0.5"><X size={13} /></button>
        </div>
      ) : (
        <div className="flex items-center gap-1 flex-1 group">
          <dd className="text-sm text-slate-800 font-medium">{value || '–'}</dd>
          <button onClick={() => setEditing(true)} data-testid={`edit-${field}`} className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-primary transition-opacity p-0.5"><Edit3 size={12} /></button>
        </div>
      )}
    </div>
  );
}

/* ═══════ Case Notes Section ═══════ */
function CaseNotes({ appId }) {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newNote, setNewNote] = useState('');
  const [sending, setSending] = useState(false);

  const load = useCallback(async () => {
    try { const res = await apiClient.get(`/api/applications/${appId}/notes`); setNotes(res.data || []); } catch {} finally { setLoading(false); }
  }, [appId]);
  useEffect(() => { load(); }, [load]);

  const addNote = async () => {
    if (!newNote.trim()) return;
    setSending(true);
    try { await apiClient.post(`/api/applications/${appId}/notes`, { content: newNote.trim(), visibility: 'internal' }); setNewNote(''); await load(); } catch {} finally { setSending(false); }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-sm p-4 space-y-3" data-testid="case-notes">
      <h4 className="font-semibold text-slate-700 text-xs flex items-center gap-1.5"><StickyNote size={14} className="text-primary" /> Interne Notizen</h4>
      <div className="flex gap-2">
        <textarea value={newNote} onChange={e => setNewNote(e.target.value)} placeholder="Notiz hinzufügen..."
          data-testid="note-input" rows={2}
          className="flex-1 border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary resize-none" />
        <button onClick={addNote} disabled={sending || !newNote.trim()} data-testid="note-submit"
          className="self-end bg-primary text-white px-3 py-2 rounded-sm text-xs font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors">
          {sending ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
        </button>
      </div>
      {loading && <Loader2 size={16} className="animate-spin text-slate-400 mx-auto" />}
      {!loading && notes.length === 0 && <p className="text-xs text-slate-400 text-center py-1">Noch keine Notizen</p>}
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {notes.map(n => (
          <div key={n.id} className="border border-slate-100 rounded-sm px-3 py-2" data-testid={`note-${n.id}`}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-medium text-primary">{n.author_name || 'Staff'}</span>
              <span className="text-[10px] text-slate-400">{n.created_at ? new Date(n.created_at).toLocaleString('de-DE') : ''}</span>
            </div>
            <p className="text-xs text-slate-700 whitespace-pre-wrap">{n.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════ Activity History ═══════ */
function ActivityHistory({ appId }) {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try { const res = await apiClient.get(`/api/applications/${appId}/activities`); setActivities(res.data || []); } catch {} finally { setLoading(false); }
    })();
  }, [appId]);

  const actionLabels = {
    stage_changed: 'Status geändert',
    note_added: 'Notiz hinzugefügt',
    profile_field_changed: 'Profil bearbeitet',
    email_sent: 'E-Mail gesendet',
    document_uploaded: 'Dokument hochgeladen',
    application_created: 'Bewerbung erstellt',
    case_email_sent: 'Fall-E-Mail gesendet',
    teacher_assignment_created: 'Lehrer zugewiesen',
    consent_granted: 'Einwilligung erteilt',
    consent_revoked: 'Einwilligung widerrufen',
    case_note_added: 'Notiz erstellt',
    applicant_profile_updated: 'Profil aktualisiert',
  };

  return (
    <div className="bg-white border border-slate-200 rounded-sm p-4 space-y-3" data-testid="activity-history">
      <h4 className="font-semibold text-slate-700 text-xs flex items-center gap-1.5"><History size={14} className="text-primary" /> Bearbeitungsverlauf</h4>
      {loading && <Loader2 size={16} className="animate-spin text-slate-400 mx-auto" />}
      {!loading && activities.length === 0 && <p className="text-xs text-slate-400 text-center py-1">Keine Einträge</p>}
      <div className="space-y-0 max-h-64 overflow-y-auto">
        {activities.slice(0, 30).map((a, i) => (
          <div key={i} className="flex items-start gap-2.5 py-2 border-b border-slate-50 last:border-0">
            <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
              a.action === 'email_sent' ? 'bg-blue-100 text-blue-600' :
              a.action === 'stage_changed' ? 'bg-primary/10 text-primary' :
              a.action?.includes('note') ? 'bg-primary/10 text-primary' :
              'bg-slate-100 text-slate-500'
            }`}>
              {a.action === 'email_sent' ? <Mail size={10} /> :
               a.action === 'stage_changed' ? <RefreshCw size={10} /> :
               a.action?.includes('note') ? <StickyNote size={10} /> :
               <Clock size={10} />}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs text-slate-700">
                <span className="font-medium">{actionLabels[a.action] || a.action}</span>
                {a.actor_name && <span className="text-slate-400"> · {a.actor_name}</span>}
              </p>
              {a.old_value && a.new_value && (
                <p className="text-[10px] text-slate-500 mt-0.5">{a.old_value} → {a.new_value}</p>
              )}
              {a.new_value && !a.old_value && (
                <p className="text-[10px] text-slate-500 mt-0.5">{a.new_value}</p>
              )}
              {a.subject && <p className="text-[10px] text-slate-500 mt-0.5">Betreff: {a.subject}</p>}
              {a.details && typeof a.details === 'object' && Object.keys(a.details).length > 0 && (
                <p className="text-[10px] text-slate-400 mt-0.5">{JSON.stringify(a.details)}</p>
              )}
            </div>
            <span className="text-[10px] text-slate-300 shrink-0 whitespace-nowrap">
              {a.occurred_at ? new Date(a.occurred_at).toLocaleString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════ Case Email Composer ═══════ */
function CaseEmailComposer({ appId, applicantEmail, applicantName }) {
  const [open, setOpen] = useState(false);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const send = async () => {
    if (!subject.trim() || !body.trim()) return;
    setSending(true);
    try {
      await apiClient.post(`/api/applications/${appId}/send-email`, { subject: subject.trim(), body: body.trim(), lang: 'de' });
      setSent(true);
      setTimeout(() => { setSent(false); setOpen(false); setSubject(''); setBody(''); }, 2000);
    } catch {} finally { setSending(false); }
  };

  if (!open) return (
    <button onClick={() => setOpen(true)} data-testid="open-email-composer"
      className="w-full flex items-center justify-center gap-2 text-xs font-medium text-primary border border-primary/25 bg-primary/5 rounded-sm py-2.5 hover:bg-primary/10 transition-colors">
      <Mail size={14} /> E-Mail an Bewerber senden
    </button>
  );

  return (
    <div className="bg-white border border-slate-200 rounded-sm p-4 space-y-3" data-testid="email-composer">
      <div className="flex items-center justify-between">
        <h4 className="font-semibold text-slate-700 text-xs flex items-center gap-1.5"><Mail size={14} className="text-primary" /> E-Mail senden</h4>
        <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-600"><X size={14} /></button>
      </div>
      <p className="text-[10px] text-slate-400">An: {applicantEmail}</p>
      <input value={subject} onChange={e => setSubject(e.target.value)} placeholder="Betreff..."
        data-testid="email-subject" className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary" />
      <textarea value={body} onChange={e => setBody(e.target.value)} placeholder="Nachricht verfassen..."
        data-testid="email-body" rows={4} className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary resize-none" />
      <div className="flex items-center justify-between">
        <p className="text-[10px] text-slate-400">Wird über Studienkolleg Aachen Template gesendet</p>
        <button onClick={send} disabled={sending || !subject.trim() || !body.trim()} data-testid="email-send-btn"
          className="flex items-center gap-1.5 bg-primary text-white px-4 py-2 rounded-sm text-xs font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors">
          {sent ? <><CheckCircle size={13} /> Gesendet</> : sending ? <><Loader2 size={13} className="animate-spin" /> Senden...</> : <><Send size={13} /> Senden</>}
        </button>
      </div>
    </div>
  );
}

/* ═══════ Status Badges ═══════ */
const DOC_STATUS = {
  uploaded: { label: 'Hochgeladen', icon: Clock, color: 'bg-primary/10 text-primary' },
  in_review: { label: 'In Prüfung', icon: Clock, color: 'bg-slate-100 text-slate-600' },
  approved: { label: 'Akzeptiert', icon: CheckCircle, color: 'bg-primary/15 text-primary' },
  rejected: { label: 'Abgelehnt', icon: XCircle, color: 'bg-red-100 text-red-700' },
};

/* ═══════ Main Page ═══════ */
export default function ApplicantDetailPage() {
  const { id } = useParams();
  const [app, setApp] = useState(null);
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stageUpdating, setStageUpdating] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const STAGES = [
    'lead_new', 'in_review', 'pending_docs', 'interview_scheduled',
    'conditional_offer', 'offer_sent', 'enrolled', 'declined', 'on_hold',
  ];

  useEffect(() => {
    const load = async () => {
      try {
        const [appRes, docsRes] = await Promise.all([
          apiClient.get(`/api/applications/${id}`),
          apiClient.get(`/api/applications/${id}/documents`),
        ]);
        setApp(appRes.data);
        setDocs(docsRes.data);
      } catch {} finally { setLoading(false); }
    };
    load();
  }, [id, refreshKey]);

  const updateStage = async newStage => {
    setStageUpdating(true);
    try {
      await apiClient.put(`/api/applications/${id}`, { current_stage: newStage });
      setApp(prev => ({ ...prev, current_stage: newStage }));
      setRefreshKey(k => k + 1);
    } catch {} finally { setStageUpdating(false); }
  };

  const saveProfileField = async (field, value) => {
    try {
      await apiClient.put(`/api/applications/${id}/profile`, { [field]: value });
      setApp(prev => ({
        ...prev,
        applicant: { ...prev.applicant, [field]: value },
      }));
      setRefreshKey(k => k + 1);
    } catch (e) { console.error('Profile save failed', e); }
  };

  const saveAppField = async (field, value) => {
    try {
      await apiClient.put(`/api/applications/${id}`, { [field]: value });
      setApp(prev => ({ ...prev, [field]: value }));
      setRefreshKey(k => k + 1);
    } catch (e) { console.error('App field save failed', e); }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 size={28} className="animate-spin text-primary" /></div>;
  if (!app) return <div className="p-6 text-slate-500">Bewerbung nicht gefunden</div>;

  const whatsappUrl = app.applicant?.phone
    ? `https://wa.me/${app.applicant.phone.replace(/[^0-9+]/g, '').replace('+', '')}?text=${encodeURIComponent(`Hallo ${app.applicant?.full_name || ''}, hier ist das Team vom Studienkolleg Aachen. `)}`
    : null;

  return (
    <div className="space-y-4 animate-fade-in" data-testid="applicant-detail-page">
      <RecordHeader
        title={app.applicant?.full_name || 'Bewerber'}
        status={STAGE_LABELS[app.current_stage] || app.current_stage}
        owner={app.owner_name || app.assigned_to_name || 'Staff-Team'}
        lastActivity={app.updated_at ? new Date(app.updated_at).toLocaleString('de-DE') : '–'}
        nextAction={app.followup_reason || 'Status prüfen und nächsten Schritt setzen'}
        backAction={<Link to="/staff/kanban" className="text-slate-400 hover:text-primary transition-colors" data-testid="back-to-kanban"><ArrowLeft size={18} /></Link>}
        quickActions={(
          <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-sm ${STAGE_COLORS[app.current_stage] || 'bg-slate-100 text-slate-600'}`}>
            {STAGE_LABELS[app.current_stage] || app.current_stage}
          </span>
        )}
        testId="applicant-record-header"
      />

      {/* Quick Actions Bar */}
      <div className="flex flex-wrap gap-2">
        {app.applicant?.phone && (
          <a href={`tel:${app.applicant.phone.replace(/\s/g, '')}`} data-testid="action-call"
            className="flex items-center gap-1.5 text-xs font-medium px-3 py-2 bg-primary/5 text-primary border border-primary/20 rounded-sm hover:bg-primary/10 transition-colors">
            <Phone size={13} /> Anrufen
          </a>
        )}
        {app.applicant?.email && (
          <a href={`mailto:${app.applicant.email}?subject=Ihre Bewerbung – Studienkolleg Aachen`} data-testid="action-mailto"
            className="flex items-center gap-1.5 text-xs font-medium px-3 py-2 bg-slate-50 text-slate-700 border border-slate-200 rounded-sm hover:bg-slate-100 transition-colors">
            <Mail size={13} /> E-Mail (extern)
          </a>
        )}
        {whatsappUrl && (
          <a href={whatsappUrl} target="_blank" rel="noopener noreferrer" data-testid="action-whatsapp"
            className="flex items-center gap-1.5 text-xs font-medium px-3 py-2 bg-primary/8 text-primary border border-primary/20 rounded-sm hover:bg-primary/15 transition-colors">
            <MessageCircle size={13} /> WhatsApp
          </a>
        )}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Left: Data + Docs */}
        <div className="xl:col-span-2 space-y-4">
          {/* Personal Data – Editable */}
          <div className="bg-white border border-slate-200 rounded-sm p-4">
            <h3 className="font-semibold text-slate-700 mb-2 text-xs flex items-center gap-1.5"><Users size={14} className="text-primary" /> Persönliche Daten</h3>
            <dl className="space-y-0.5">
              <EditableField label="Name" value={app.applicant?.full_name} field="full_name" onSave={saveProfileField} />
              <EditableField label="E-Mail" value={app.applicant?.email} field="email" onSave={saveProfileField} />
              <EditableField label="Telefon" value={app.applicant?.phone} field="phone" onSave={saveProfileField} />
              <EditableField label="Land" value={app.applicant?.country} field="country" onSave={saveProfileField} />
              <EditableField label="Geb.-Datum" value={app.date_of_birth} field="date_of_birth" onSave={saveAppField} />
            </dl>
          </div>

          {/* Application Data – Editable */}
          <div className="bg-white border border-slate-200 rounded-sm p-4">
            <h3 className="font-semibold text-slate-700 mb-2 text-xs flex items-center gap-1.5"><FileText size={14} className="text-primary" /> Bewerbungsdaten</h3>
            <dl className="space-y-0.5">
              <EditableField label="Kurstyp" value={app.course_type} field="course_type" onSave={saveAppField} />
              <EditableField label="Semester" value={app.desired_start} field="desired_start" onSave={saveAppField} />
              <EditableField label="Deutsch" value={app.language_level} field="language_level" onSave={saveAppField} />
              <EditableField label="Abschlussland" value={app.degree_country} field="degree_country" onSave={saveAppField} />
              <EditableField label="Kombination" value={app.combo_option} field="combo_option" onSave={saveAppField} />
              <EditableField label="Quelle" value={app.source} field="source" onSave={saveAppField} />
            </dl>
            {app.notes && (
              <div className="mt-2 pt-2 border-t border-slate-100">
                <p className="text-[10px] text-slate-500 mb-0.5">Bewerber-Anmerkung:</p>
                <p className="text-xs text-slate-700 italic">"{app.notes}"</p>
              </div>
            )}
          </div>

          {/* Status Update */}
          <div className="bg-white border border-slate-200 rounded-sm p-4">
            <h3 className="font-semibold text-slate-700 mb-2 text-xs">Status ändern</h3>
            <div className="flex flex-wrap gap-1.5">
              {STAGES.map(stage => (
                <button key={stage} onClick={() => updateStage(stage)} disabled={stageUpdating || app.current_stage === stage}
                  data-testid={`stage-btn-${stage}`}
                  className={`text-[11px] px-2.5 py-1.5 rounded-sm font-medium transition-all disabled:opacity-60 ${
                    app.current_stage === stage ? 'bg-primary text-white' : 'border border-slate-200 text-slate-600 hover:border-primary/50 hover:text-primary'
                  }`}>
                  {STAGE_LABELS[stage] || stage}
                </button>
              ))}
            </div>
          </div>

          {/* Email Composer */}
          <CaseEmailComposer appId={id} applicantEmail={app.applicant?.email} applicantName={app.applicant?.full_name} />

          {/* Documents */}
          <div className="bg-white border border-slate-200 rounded-sm p-4">
            <h3 className="font-semibold text-slate-700 mb-2 text-xs">Dokumente ({docs.length})</h3>
            {docs.length === 0 ? <p className="text-xs text-slate-400">Keine Dokumente</p> : (
              <ul className="space-y-1.5">
                {docs.map(doc => {
                  const s = DOC_STATUS[doc.status] || DOC_STATUS.uploaded;
                  const Icon = s.icon;
                  return (
                    <li key={doc.id} className="flex items-center justify-between border border-slate-100 rounded-sm p-2.5" data-testid={`doc-${doc.id}`}>
                      <div className="flex items-center gap-2"><FileText size={14} className="text-slate-400" /><div><p className="text-xs text-slate-700 font-medium">{doc.filename || doc.document_type}</p><p className="text-[10px] text-slate-400">{doc.document_type}</p></div></div>
                      <span className={`flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-sm ${s.color}`}><Icon size={11} />{s.label}</span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="xl:col-span-1 space-y-4">
          <CaseNotes appId={id} />
          <FollowupPanel appId={id} />
          <ActivityHistory appId={id} />
          <AIScreeningPanel appId={id} currentStage={app.current_stage} onStageAccepted={(newStage) => { setApp(prev => ({ ...prev, current_stage: newStage })); setRefreshKey(k => k + 1); }} />
          <TeacherAssignmentPanel applicantId={app.applicant_id || id} applicantName={app.applicant?.full_name} />
        </div>
      </div>
    </div>
  );
}
