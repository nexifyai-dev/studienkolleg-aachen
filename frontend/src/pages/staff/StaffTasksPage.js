import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'sonner';
import {
  CheckSquare, Clock, AlertCircle, Plus, Loader2, CheckCircle, X,
  Paperclip, Download, FileText, MessageSquare, History, Send,
  Edit3, Save, User, Search, ArrowUpDown, Calendar, List
} from 'lucide-react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { TASK_STATUS_LABELS, TASK_PRIORITY_LABELS, getLang } from '../../lib/utils';

const HISTORY_LABELS_MAP = {
  de: { created: 'Erstellt', status_changed: 'Status geaendert', reassigned: 'Neu zugewiesen', priority_changed: 'Prioritaet geaendert', note_added: 'Notiz hinzugefuegt', attachment_added: 'Anhang hinzugefuegt' },
  en: { created: 'Created', status_changed: 'Status changed', reassigned: 'Reassigned', priority_changed: 'Priority changed', note_added: 'Note added', attachment_added: 'Attachment added' },
};

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/* ═══════ Task Detail Modal ═══════ */
function TaskDetailModal({ task, onClose, onUpdate, staffList, lang }) {
  const STATUS_LABELS = TASK_STATUS_LABELS[lang];
  const PRIORITY_LABELS = TASK_PRIORITY_LABELS[lang];
  const HISTORY_LABELS = HISTORY_LABELS_MAP[lang];
  const [activeTab, setActiveTab] = useState('detail');
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    title: task.title, description: task.description || '',
    priority: task.priority, due_date: task.due_date?.split('T')[0] || '',
    assigned_to: task.assigned_to || '',
  });
  const [saving, setSaving] = useState(false);
  const [notes, setNotes] = useState([]);
  const [attachments, setAttachments] = useState([]);
  const [history, setHistory] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [sendingNote, setSendingNote] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef(null);

  const loadTab = useCallback(async (tab) => {
    try {
      if (tab === 'notes') {
        const r = await apiClient.get(`/api/tasks/${task.id}/notes`, { withCredentials: true });
        setNotes(r.data || []);
      } else if (tab === 'attachments') {
        const r = await apiClient.get(`/api/tasks/${task.id}/attachments`, { withCredentials: true });
        setAttachments(r.data || []);
      } else if (tab === 'history') {
        const r = await apiClient.get(`/api/tasks/${task.id}/history`, { withCredentials: true });
        setHistory(r.data || []);
      }
    } catch {}
  }, [task.id]);

  useEffect(() => { loadTab(activeTab); }, [activeTab, loadTab]);

  const saveEdit = async () => {
    setSaving(true);
    try {
      const payload = {};
      if (form.title !== task.title) payload.title = form.title;
      if (form.description !== (task.description || '')) payload.description = form.description;
      if (form.priority !== task.priority) payload.priority = form.priority;
      if (form.due_date !== (task.due_date?.split('T')[0] || '')) payload.due_date = form.due_date;
      if (form.assigned_to !== (task.assigned_to || '')) payload.assigned_to = form.assigned_to;
      if (Object.keys(payload).length > 0) {
        const r = await apiClient.put(`/api/tasks/${task.id}`, payload, { withCredentials: true });
        onUpdate(r.data);
        toast.success('Aufgabe gespeichert');
      }
      setEditing(false);
    } catch {} finally { setSaving(false); }
  };

  const changeStatus = async (status) => {
    try {
      const r = await apiClient.put(`/api/tasks/${task.id}`, { status }, { withCredentials: true });
      onUpdate(r.data);
      toast.success(`Status: ${STATUS_LABELS[status]}`);
    } catch { toast.error('Fehler beim Statuswechsel'); }
  };

  const addNote = async () => {
    if (!newNote.trim()) return;
    setSendingNote(true);
    try {
      await apiClient.post(`/api/tasks/${task.id}/notes`, { content: newNote.trim() }, { withCredentials: true });
      setNewNote('');
      await loadTab('notes');
      toast.success('Notiz hinzugefügt');
    } catch { toast.error('Fehler'); } finally { setSendingNote(false); }
  };

  const uploadAttachment = async (file) => {
    if (!file || file.size > 10 * 1024 * 1024) return;
    setUploading(true);
    try {
      const b64 = await fileToBase64(file);
      await apiClient.post(`/api/tasks/${task.id}/attachments`, {
        filename: file.name, content_type: file.type || 'application/octet-stream', file_data: b64,
      }, { withCredentials: true });
      await loadTab('attachments');
      toast.success('Datei hochgeladen');
    } catch { toast.error('Upload fehlgeschlagen'); } finally { setUploading(false); }
  };

  const tabs = [
    { key: 'detail', icon: Edit3, label: 'Details' },
    { key: 'notes', icon: MessageSquare, label: `Notizen${notes.length ? ` (${notes.length})` : ''}` },
    { key: 'attachments', icon: Paperclip, label: `Anhaenge${attachments.length ? ` (${attachments.length})` : ''}` },
    { key: 'history', icon: History, label: 'Verlauf' },
  ];

  return (
    <div className="w2g-modal-overlay" onClick={onClose} data-testid="task-detail-modal">
      <div className="w2g-modal max-w-2xl max-h-[85vh] flex flex-col" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="w2g-modal-header shrink-0">
          <div className="flex items-center gap-2 min-w-0">
            <CheckSquare size={16} className="text-primary shrink-0" />
            <h2 className="font-heading font-bold text-primary text-base truncate">{task.title}</h2>
              <span className={`w2g-badge ${
              task.status === 'done' ? 'bg-primary-muted text-primary' :
              task.status === 'in_progress' ? 'bg-primary-muted text-primary' :
              'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'
            }`}>{STATUS_LABELS[task.status]}</span>
          </div>
          <button onClick={onClose} data-testid="task-modal-close" className="w2g-btn-icon"><X size={18} /></button>
        </div>

        {/* Status Actions */}
        <div className="px-5 py-2 border-b border-[var(--color-divider-subtle)] flex items-center gap-2 shrink-0">
          {task.status !== 'in_progress' && task.status !== 'done' && (
            <button onClick={() => changeStatus('in_progress')} data-testid="task-modal-start"
              className="w2g-btn-primary text-xs px-3 py-1.5">Starten</button>
          )}
          {task.status !== 'done' && (
            <button onClick={() => changeStatus('done')} data-testid="task-modal-done"
              className="w2g-btn-primary text-xs px-3 py-1.5">Erledigt</button>
          )}
          {task.status === 'done' && (
            <button onClick={() => changeStatus('open')} data-testid="task-modal-reopen"
              className="w2g-btn-secondary text-xs px-3 py-1.5">Wieder oeffnen</button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex border-b border-[var(--color-divider-subtle)] px-5 shrink-0">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                data-testid={`task-tab-${tab.key}`}
                className={`flex items-center gap-1.5 px-3 py-2.5 text-xs font-medium border-b-2 transition-colors ${
                  activeTab === tab.key ? 'border-primary text-primary' : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
                }`}>
                <Icon size={13} /> {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-5 min-h-0">
          {activeTab === 'detail' && (
            <div className="space-y-4">
              {editing ? (
                <div className="space-y-3" data-testid="task-edit-form">
                  <div>
                    <label className="w2g-label">Titel</label>
                    <input value={form.title} onChange={e => setForm(f => ({...f, title: e.target.value}))}
                      className="w2g-input" />
                  </div>
                  <div>
                    <label className="w2g-label">Beschreibung</label>
                    <textarea value={form.description} onChange={e => setForm(f => ({...f, description: e.target.value}))}
                      rows={3} className="w2g-input resize-none" />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="w2g-label">Prioritaet</label>
                      <select value={form.priority} onChange={e => setForm(f => ({...f, priority: e.target.value}))}
                        className="w2g-select">
                        <option value="low">Niedrig</option><option value="normal">Normal</option><option value="high">Hoch</option>
                      </select>
                    </div>
                    <div>
                      <label className="w2g-label">Faellig</label>
                      <input type="date" value={form.due_date} onChange={e => setForm(f => ({...f, due_date: e.target.value}))}
                        className="w2g-input" />
                    </div>
                  </div>
                  <div>
                    <label className="w2g-label">Zugewiesen an</label>
                    <select value={form.assigned_to} onChange={e => setForm(f => ({...f, assigned_to: e.target.value}))}
                      className="w2g-select">
                      <option value="">-- Nicht zugewiesen --</option>
                      {staffList.map(s => <option key={s.id} value={s.id}>{s.full_name || s.email}</option>)}
                    </select>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={saveEdit} disabled={saving} data-testid="task-edit-save"
                      className="w2g-btn-primary text-xs">
                      {saving ? <Loader2 size={13} className="animate-spin" /> : <Save size={13} />} Speichern
                    </button>
                    <button onClick={() => setEditing(false)} className="w2g-btn-secondary text-xs">Abbrechen</button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3" data-testid="task-detail-view">
                  <div className="flex justify-end">
                    <button onClick={() => setEditing(true)} data-testid="task-edit-btn"
                      className="w2g-btn-table-action">
                      <Edit3 size={12} /> Bearbeiten
                    </button>
                  </div>
                  <dl className="space-y-2 text-sm">
                    <div className="flex"><dt className="w-28 text-[var(--color-text-secondary)] text-xs shrink-0">Beschreibung</dt><dd className="text-[var(--color-text-primary)] text-xs">{task.description || '–'}</dd></div>
                    <div className="flex"><dt className="w-28 text-[var(--color-text-secondary)] text-xs shrink-0">Prioritaet</dt>
                      <dd><span className={`text-xs px-2 py-0.5 rounded-sm font-medium ${
                        task.priority === 'high' ? 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]' : task.priority === 'low' ? 'bg-[var(--color-surface-elevated)] text-[var(--color-text-secondary)]' : 'bg-[var(--color-surface-elevated)] text-[var(--color-text-primary)]'
                      }`}>{PRIORITY_LABELS[task.priority]}</span></dd>
                    </div>
                    <div className="flex"><dt className="w-28 text-[var(--color-text-secondary)] text-xs shrink-0">Zugewiesen</dt><dd className="text-[var(--color-text-primary)] text-xs flex items-center gap-1"><User size={11} />{task.assigned_name || '–'}</dd></div>
                    <div className="flex"><dt className="w-28 text-[var(--color-text-secondary)] text-xs shrink-0">Faellig</dt><dd className="text-[var(--color-text-primary)] text-xs">{task.due_date ? new Date(task.due_date).toLocaleDateString('de-DE') : '–'}</dd></div>
                    <div className="flex"><dt className="w-28 text-[var(--color-text-secondary)] text-xs shrink-0">Erstellt</dt><dd className="text-[var(--color-text-primary)] text-xs">{task.created_at ? new Date(task.created_at).toLocaleString('de-DE') : '–'}</dd></div>
                  </dl>
                </div>
              )}
            </div>
          )}

          {activeTab === 'notes' && (
            <div className="space-y-3">
              <div className="flex gap-2">
                <textarea value={newNote} onChange={e => setNewNote(e.target.value)} placeholder="Notiz hinzufuegen..." rows={2}
                  data-testid="task-note-input"
                  className="flex-1 border border-[var(--color-divider)] rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary resize-none" />
                <button onClick={addNote} disabled={sendingNote || !newNote.trim()} data-testid="task-note-submit"
                  className="self-end bg-primary text-white px-3 py-2 rounded-sm text-xs hover:bg-primary/90 disabled:opacity-50">
                  {sendingNote ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                </button>
              </div>
              {notes.length === 0 && <p className="text-xs text-[var(--color-text-tertiary)] text-center py-4">Noch keine Notizen</p>}
              {notes.map(n => (
                <div key={n.id} className="border border-[var(--color-divider-subtle)] rounded-sm px-3 py-2" data-testid={`task-note-${n.id}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-medium text-primary">{n.author_name}</span>
                    <span className="text-[10px] text-[var(--color-text-tertiary)]">{n.created_at ? new Date(n.created_at).toLocaleString('de-DE') : ''}</span>
                  </div>
                  <p className="text-xs text-[var(--color-text-primary)] whitespace-pre-wrap">{n.content}</p>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'attachments' && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <button onClick={() => fileRef.current?.click()} disabled={uploading} data-testid="task-attach-upload-btn"
                  className="flex items-center gap-1.5 bg-primary text-white px-3 py-2 rounded-sm text-xs font-medium hover:bg-primary/90 disabled:opacity-50">
                  {uploading ? <Loader2 size={13} className="animate-spin" /> : <Paperclip size={13} />}
                  {uploading ? 'Wird hochgeladen...' : 'Datei hochladen'}
                </button>
                <input ref={fileRef} type="file" className="hidden" onChange={e => { if (e.target.files?.[0]) uploadAttachment(e.target.files[0]); e.target.value = ''; }}
                  accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx,.txt,.csv" />
              </div>
              {attachments.length === 0 && <p className="text-xs text-[var(--color-text-tertiary)] text-center py-4">Keine Anhaenge</p>}
              {attachments.map(a => (
                <div key={a.id} className="flex items-center justify-between border border-[var(--color-divider-subtle)] rounded-sm px-3 py-2" data-testid={`task-att-${a.id}`}>
                  <div className="flex items-center gap-2 min-w-0">
                    <FileText size={14} className="text-[var(--color-text-tertiary)] shrink-0" />
                    <div className="min-w-0">
                      <p className="text-xs text-[var(--color-text-primary)] font-medium truncate">{a.filename}</p>
                      <p className="text-[10px] text-[var(--color-text-tertiary)]">{a.uploaded_by_name} · {(a.file_size / 1024).toFixed(0)} KB</p>
                    </div>
                  </div>
                  <a href={`/api/tasks/${task.id}/attachments/${a.id}`} target="_blank" rel="noreferrer"
                    data-testid={`task-att-download-${a.id}`}
                    className="text-primary hover:text-primary/70 shrink-0 p-1"><Download size={14} /></a>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="space-y-0">
              {history.length === 0 && <p className="text-xs text-[var(--color-text-tertiary)] text-center py-4">Kein Verlauf</p>}
              {history.map((h, i) => (
                <div key={i} className="flex items-start gap-2.5 py-2 border-b border-[var(--color-divider-subtle)] last:border-0">
                  <div className="w-5 h-5 rounded-full bg-primary-muted flex items-center justify-center shrink-0 mt-0.5">
                    <History size={10} className="text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-[var(--color-text-primary)]">
                      <span className="font-medium">{HISTORY_LABELS[h.action] || h.action}</span>
                      {h.actor_name && <span className="text-[var(--color-text-tertiary)]"> · {h.actor_name}</span>}
                    </p>
                    {h.old_value && h.new_value && <p className="text-[10px] text-[var(--color-text-secondary)]">{h.old_value} → {h.new_value}</p>}
                    {h.new_value && !h.old_value && <p className="text-[10px] text-[var(--color-text-secondary)]">{h.new_value}</p>}
                  </div>
                  <span className="text-[10px] text-[var(--color-text-tertiary)] shrink-0">
                    {h.occurred_at ? new Date(h.occurred_at).toLocaleString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : ''}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ═══════ Create Task Modal (PopUp statt Inline) ═══════ */
function CreateTaskModal({ onClose, onCreate, staffList }) {
  const [form, setForm] = useState({ title: '', description: '', priority: 'normal', due_date: '', assigned_to: '' });
  const [creating, setCreating] = useState(false);

  const handleCreate = async () => {
    if (!form.title.trim()) return;
    setCreating(true);
    try {
      await onCreate(form);
      onClose();
    } finally { setCreating(false); }
  };

  return (
    <div className="w2g-modal-overlay" onClick={onClose} data-testid="create-task-modal">
      <div className="w2g-modal max-w-lg" onClick={e => e.stopPropagation()}>
        <div className="w2g-modal-header">
          <h2 className="font-heading text-base font-bold text-[var(--color-primary)] flex items-center gap-2">
            <Plus size={16} /> Neue Aufgabe
          </h2>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="close-create-task"><X size={18} /></button>
        </div>
        <div className="w2g-modal-body space-y-4">
          <div>
            <label className="w2g-label">Titel</label>
            <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              placeholder="Was muss erledigt werden?" data-testid="task-title-input"
              className="w2g-input" autoFocus />
          </div>
          <div>
            <label className="w2g-label">Beschreibung</label>
            <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              placeholder="Details zur Aufgabe (optional)..." data-testid="task-desc-input" rows={3}
              className="w2g-textarea" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="w2g-label">Prioritaet</label>
              <select value={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}
                data-testid="task-priority-select" className="w2g-select">
                <option value="low">Niedrig</option><option value="normal">Normal</option><option value="high">Hoch</option>
              </select>
            </div>
            <div>
              <label className="w2g-label">Faellig am</label>
              <input type="date" value={form.due_date} onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))}
                data-testid="task-duedate-input" className="w2g-input" />
            </div>
          </div>
          <div>
            <label className="w2g-label">Zugewiesen an</label>
            <select value={form.assigned_to} onChange={e => setForm(f => ({ ...f, assigned_to: e.target.value }))}
              data-testid="task-assign-select" className="w2g-select">
              <option value="">Mir zuweisen</option>
              {staffList.map(s => <option key={s.id} value={s.id}>{s.full_name || s.email}</option>)}
            </select>
          </div>
        </div>
        <div className="w2g-modal-footer">
          <button onClick={onClose} className="w2g-btn-secondary">Abbrechen</button>
          <button onClick={handleCreate} disabled={creating || !form.title.trim()} data-testid="task-submit-btn"
            className="w2g-btn-primary">
            {creating ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />} Erstellen
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════ Main Tasks Page ═══════ */
export default function StaffTasksPage() {
  const { user } = useAuth();
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const STATUS_LABELS = TASK_STATUS_LABELS[lang];
  const PRIORITY_LABELS = TASK_PRIORITY_LABELS[lang];
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('open');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [assignmentFilter, setAssignmentFilter] = useState('mine');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('due_date');
  const [showCreate, setShowCreate] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [staffList, setStaffList] = useState([]);
  const [viewMode, setViewMode] = useState('list'); // 'list' | 'calendar'

  const load = useCallback(async () => {
    try {
      const [tasksRes, usersRes] = await Promise.all([
        apiClient.get('/api/tasks', { withCredentials: true }),
        apiClient.get('/api/users', { withCredentials: true }).catch(() => ({ data: [] })),
      ]);
      setTasks(tasksRes.data || []);
      const staff = (usersRes.data || []).filter(u => ['staff','admin','superadmin','teacher'].includes(u.role) && u.active !== false);
      setStaffList(staff);
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const createTask = async (form) => {
    if (!form.title.trim()) return;
    try {
      const payload = { title: form.title, description: form.description, priority: form.priority };
      if (form.due_date) payload.due_date = form.due_date;
      if (form.assigned_to) payload.assigned_to = form.assigned_to;
      await apiClient.post('/api/tasks', payload, { withCredentials: true });
      toast.success('Aufgabe erstellt');
      setShowCreate(false);
      await load();
    } catch { toast.error('Fehler beim Erstellen'); }
  };

  const updateStatus = async (taskId, status) => {
    try {
      const r = await apiClient.put(`/api/tasks/${taskId}`, { status }, { withCredentials: true });
      setTasks(prev => prev.map(t => t.id === taskId ? r.data : t));
    } catch {}
  };

  const handleTaskUpdate = (updated) => {
    setTasks(prev => prev.map(t => t.id === updated.id ? updated : t));
    setSelectedTask(updated);
  };

  let filtered = filter === 'all' ? tasks : tasks.filter(t => t.status === filter);
  if (priorityFilter !== 'all') filtered = filtered.filter(t => t.priority === priorityFilter);
  if (assignmentFilter === 'mine') filtered = filtered.filter(t => t.assigned_to === user?.id);
  if (searchQuery) {
    const q = searchQuery.toLowerCase();
    filtered = filtered.filter(t =>
      (t.title || '').toLowerCase().includes(q) ||
      (t.description || '').toLowerCase().includes(q) ||
      (t.assigned_name || '').toLowerCase().includes(q)
    );
  }

  // Sort
  const now = new Date();
  filtered = [...filtered].sort((a, b) => {
    if (sortBy === 'due_date') {
      const aDate = a.due_date ? new Date(a.due_date) : new Date('9999-12-31');
      const bDate = b.due_date ? new Date(b.due_date) : new Date('9999-12-31');
      return aDate - bDate;
    }
    if (sortBy === 'priority') {
      const order = { high: 0, normal: 1, low: 2 };
      return (order[a.priority] ?? 1) - (order[b.priority] ?? 1);
    }
    if (sortBy === 'created') {
      return new Date(b.created_at || 0) - new Date(a.created_at || 0);
    }
    return 0;
  });

  // Helper: is overdue?
  const isOverdue = (task) => task.status !== 'done' && task.due_date && new Date(task.due_date) < now;

  const openCount = tasks.filter(t => t.status === 'open').length;
  const inProgressCount = tasks.filter(t => t.status === 'in_progress').length;
  const doneCount = tasks.filter(t => t.status === 'done').length;
  const overdueCount = tasks.filter(t => isOverdue(t)).length;
  const myCount = tasks.filter(t => (t.status === 'open' || t.status === 'in_progress') && t.assigned_to === user?.id).length;

  if (loading) return <div className="w2g-loading"><div className="w2g-spinner" /><p className="w2g-loading-text">{lang === 'de' ? 'Wird geladen...' : 'Loading...'}</p></div>;

  return (
    <PageScaffold
      title={lang === 'de' ? 'Aufgaben' : 'Tasks'}
      subtitle={`${openCount} ${lang === 'de' ? 'offen' : 'open'}, ${inProgressCount} ${lang === 'de' ? 'in Bearbeitung' : 'in progress'}, ${doneCount} ${lang === 'de' ? 'erledigt' : 'completed'}${overdueCount > 0 ? `, ${overdueCount} ${lang === 'de' ? 'ueberfaellig' : 'overdue'}` : ''}`}
      testId="staff-tasks-page"
      actions={
        <div className="flex items-center gap-2">
          <div className="flex border border-[var(--color-divider)] rounded-[var(--radius-sm)] overflow-hidden" data-testid="task-view-toggle">
            <button onClick={() => setViewMode('list')} className={`px-2.5 py-1.5 text-xs flex items-center gap-1 ${viewMode === 'list' ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-elevated)]'}`} data-testid="task-view-list"><List size={13} /></button>
            <button onClick={() => setViewMode('calendar')} className={`px-2.5 py-1.5 text-xs flex items-center gap-1 ${viewMode === 'calendar' ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-elevated)]'}`} data-testid="task-view-calendar"><Calendar size={13} /></button>
          </div>
          <button onClick={() => setShowCreate(true)} data-testid="create-task-btn" className="w2g-btn-primary">
            <Plus size={14} /> {lang === 'de' ? 'Neue Aufgabe' : 'New Task'}
          </button>
        </div>
      }
      toolbar={
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                placeholder={lang === 'de' ? 'Aufgabe suchen...' : 'Search tasks...'} data-testid="task-search" className="w2g-search pl-9" />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]">
                  <X size={12} />
                </button>
              )}
            </div>
          }
          filters={[
            <div key="status" className="flex items-center gap-0">
              {[
                { key: 'open', label: STATUS_LABELS.open, count: openCount },
                { key: 'in_progress', label: STATUS_LABELS.in_progress, count: inProgressCount },
                { key: 'done', label: STATUS_LABELS.done, count: doneCount },
                { key: 'all', label: lang === 'de' ? 'Alle' : 'All', count: tasks.length },
              ].map(tab => (
                <button key={tab.key} onClick={() => setFilter(tab.key)} data-testid={`task-filter-${tab.key}`}
                  className={filter === tab.key ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}>
                  {tab.label} ({tab.count})
                </button>
              ))}
            </div>,
            <select key="assign" value={assignmentFilter} onChange={e => setAssignmentFilter(e.target.value)} data-testid="task-assignment-filter"
              className="w2g-select text-xs w-auto py-1.5">
              <option value="mine">{lang === 'de' ? 'Meine' : 'Mine'} ({myCount})</option>
              <option value="all">{lang === 'de' ? 'Team' : 'Team'}</option>
            </select>,
            <select key="prio" value={priorityFilter} onChange={e => setPriorityFilter(e.target.value)} data-testid="task-priority-filter"
              className="w2g-select text-xs w-auto py-1.5">
              <option value="all">{lang === 'de' ? 'Alle Prioritaeten' : 'All Priorities'}</option>
              <option value="high">{PRIORITY_LABELS.high}</option><option value="normal">{PRIORITY_LABELS.normal}</option><option value="low">{PRIORITY_LABELS.low}</option>
            </select>,
            <select key="sort" value={sortBy} onChange={e => setSortBy(e.target.value)} data-testid="task-sort"
              className="w2g-select text-xs w-auto py-1.5">
              <option value="due_date">{lang === 'de' ? 'Faelligkeit' : 'Due Date'}</option>
              <option value="priority">{lang === 'de' ? 'Prioritaet' : 'Priority'}</option>
              <option value="created">{lang === 'de' ? 'Erstellt' : 'Created'}</option>
            </select>,
          ]}
        />
      }
      contentClassName="space-y-2"
    >
      {/* Calendar View */}
      {viewMode === 'calendar' ? (
        <Card data-testid="task-calendar-view">
          <CardContent className="p-4">
            <FullCalendar
              plugins={[dayGridPlugin, interactionPlugin]}
              initialView="dayGridMonth"
              locale={lang === 'de' ? 'de' : 'en'}
              headerToolbar={{
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,dayGridWeek',
              }}
              buttonText={lang === 'de' ? { today: 'Heute', month: 'Monat', week: 'Woche' } : undefined}
              height="auto"
              events={filtered.filter(t => t.due_date).map(t => ({
                id: t.id,
                title: t.title,
                date: t.due_date?.split('T')[0],
                backgroundColor: t.status === 'done' ? 'var(--color-success)' : t.priority === 'high' ? 'var(--color-danger)' : isOverdue(t) ? '#EF4444' : 'var(--color-primary)',
                borderColor: 'transparent',
                extendedProps: t,
              }))}
              eventClick={(info) => { setSelectedTask(info.event.extendedProps); }}
              eventContent={(arg) => (
                <div className="px-1 py-0.5 text-[10px] font-medium truncate cursor-pointer" title={arg.event.title}>
                  {arg.event.title}
                </div>
              )}
              dayMaxEvents={4}
            />
            {filtered.filter(t => !t.due_date).length > 0 && (
              <div className="mt-4 p-3 bg-[var(--color-surface-elevated)] rounded-[var(--radius-sm)]">
                <p className="text-[10px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-wider mb-2">
                  {lang === 'de' ? 'Ohne Faelligkeit' : 'No Due Date'} ({filtered.filter(t => !t.due_date).length})
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {filtered.filter(t => !t.due_date).slice(0, 10).map(t => (
                    <button key={t.id} onClick={() => setSelectedTask(t)}
                      className="text-[10px] px-2 py-1 rounded-[var(--radius-xs)] border border-[var(--color-divider)] hover:border-[var(--color-primary)] text-[var(--color-text-secondary)] truncate max-w-[150px]">
                      {t.title}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
      <>
      {/* Task List */}
      {filtered.length === 0 ? (
        <div className="w2g-empty" data-testid="tasks-empty">
          <CheckSquare size={28} className="w2g-empty-icon" />
          <p className="w2g-empty-text">{lang === 'de' ? 'Keine Aufgaben in dieser Ansicht' : 'No tasks in this view'}</p>
        </div>
      ) : (
        filtered.map(task => {
          const overdue = isOverdue(task);
          return (
          <Card key={task.id} className={`cursor-pointer hover:shadow-[var(--shadow-e2)] transition-shadow ${overdue ? 'border-l-[3px] border-l-[var(--color-danger)]' : ''}`} onClick={() => setSelectedTask(task)} data-testid={`task-item-${task.id}`}>
            <CardContent className="px-4 py-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {task.status === 'done' ? <CheckCircle size={14} className="text-[var(--color-success)] shrink-0" /> :
                     overdue ? <AlertCircle size={14} className="text-[var(--color-danger)] shrink-0" /> :
                     task.status === 'in_progress' ? <AlertCircle size={14} className="text-[var(--color-info)] shrink-0" /> :
                     <Clock size={14} className="text-[var(--color-text-tertiary)] shrink-0" />}
                    <h4 className={`text-sm font-medium ${task.status === 'done' ? 'text-[var(--color-text-tertiary)] line-through' : 'text-[var(--color-text-primary)]'}`}>{task.title}</h4>
                    <Badge variant={task.priority === 'high' ? 'danger' : task.priority === 'low' ? 'muted' : 'outline'} size="xs">
                      {PRIORITY_LABELS[task.priority]}
                    </Badge>
                    {overdue && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-[var(--color-danger-bg)] text-[var(--color-danger)] font-semibold border border-[var(--color-danger-border)]" data-testid={`task-overdue-${task.id}`}>
                        {lang === 'de' ? 'Ueberfaellig' : 'Overdue'}
                      </span>
                    )}
                  </div>
                  {task.description && <p className="text-xs text-[var(--color-text-secondary)] ml-5 line-clamp-1">{task.description}</p>}
                  <div className="flex items-center gap-3 mt-1.5 ml-5 text-[10px] text-[var(--color-text-tertiary)]">
                    {task.assigned_name && <span className="flex items-center gap-1"><User size={10} />{task.assigned_name}</span>}
                    {task.due_date && <span className={overdue ? 'text-[var(--color-danger)] font-semibold' : ''}>{lang === 'de' ? 'Faellig' : 'Due'}: {new Date(task.due_date).toLocaleDateString(lang === 'de' ? 'de-DE' : 'en-US')}</span>}
                    {task.created_at && <span>{lang === 'de' ? 'Erstellt' : 'Created'}: {new Date(task.created_at).toLocaleDateString(lang === 'de' ? 'de-DE' : 'en-US')}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1 shrink-0" onClick={e => e.stopPropagation()}>
                  {task.status !== 'in_progress' && task.status !== 'done' && (
                    <button onClick={() => updateStatus(task.id, 'in_progress')} data-testid={`task-start-${task.id}`}
                      className="w2g-btn-table-action">{lang === 'de' ? 'Starten' : 'Start'}</button>
                  )}
                  {task.status !== 'done' && (
                    <button onClick={() => updateStatus(task.id, 'done')} data-testid={`task-done-${task.id}`}
                      className="w2g-btn-table-secondary">{lang === 'de' ? 'Erledigt' : 'Done'}</button>
                  )}
                  {task.status === 'done' && (
                    <button onClick={() => updateStatus(task.id, 'open')} data-testid={`task-reopen-${task.id}`}
                      className="w2g-btn-table-secondary">{lang === 'de' ? 'Wieder oeffnen' : 'Reopen'}</button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
          );
        })
      )}
      </>
      )}

      {/* Create Task Modal */}
      {showCreate && (
        <CreateTaskModal
          onClose={() => setShowCreate(false)}
          onCreate={createTask}
          staffList={staffList}
        />
      )}

      {/* Detail Modal */}
      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          onUpdate={handleTaskUpdate}
          staffList={staffList}
          lang={lang}
        />
      )}
    </PageScaffold>
  );
}
