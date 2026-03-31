import React, { useEffect, useState, useCallback, useRef } from 'react';
import apiClient from '../../lib/apiClient';
import { toast } from 'sonner';
import {
  CheckSquare, Clock, AlertCircle, Plus, Loader2, CheckCircle, X,
  Paperclip, Download, FileText, MessageSquare, History, Send,
  Edit3, Save, User
} from 'lucide-react';
import { FilterBar, SearchBar, BulkActions, EmptyState } from '../../components/shared/crmPatterns';

const PRIORITY_LABELS = { high: 'Hoch', normal: 'Normal', low: 'Niedrig' };
const STATUS_LABELS = { open: 'Offen', in_progress: 'In Bearbeitung', done: 'Erledigt' };
const HISTORY_LABELS = {
  created: 'Erstellt', status_changed: 'Status geaendert', reassigned: 'Neu zugewiesen',
  priority_changed: 'Prioritaet geaendert', note_added: 'Notiz hinzugefuegt', attachment_added: 'Anhang hinzugefuegt',
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
function TaskDetailModal({ task, onClose, onUpdate, staffList }) {
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
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={onClose} data-testid="task-detail-modal">
      <div className="bg-white rounded-sm shadow-lg max-w-2xl w-full max-h-[85vh] flex flex-col" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="px-5 py-3 border-b border-slate-200 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2 min-w-0">
            <CheckSquare size={16} className="text-primary shrink-0" />
            <h2 className="font-heading font-bold text-primary text-base truncate">{task.title}</h2>
            <span className={`text-[10px] px-2 py-0.5 rounded-sm font-medium shrink-0 ${
              task.status === 'done' ? 'bg-primary/10 text-primary' :
              task.status === 'in_progress' ? 'bg-primary/5 text-primary' :
              'bg-slate-100 text-slate-600'
            }`}>{STATUS_LABELS[task.status]}</span>
          </div>
          <button onClick={onClose} data-testid="task-modal-close" className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
        </div>

        {/* Status Actions */}
        <div className="px-5 py-2 border-b border-slate-100 flex items-center gap-2 shrink-0">
          {task.status !== 'in_progress' && task.status !== 'done' && (
            <button onClick={() => changeStatus('in_progress')} data-testid="task-modal-start"
              className="text-xs font-medium bg-primary text-white px-3 py-1.5 rounded-sm hover:bg-primary/90 transition-colors">Starten</button>
          )}
          {task.status !== 'done' && (
            <button onClick={() => changeStatus('done')} data-testid="task-modal-done"
              className="text-xs font-medium bg-primary text-white px-3 py-1.5 rounded-sm hover:bg-primary/90 transition-colors">Erledigt</button>
          )}
          {task.status === 'done' && (
            <button onClick={() => changeStatus('open')} data-testid="task-modal-reopen"
              className="text-xs font-medium border border-slate-200 text-slate-600 px-3 py-1.5 rounded-sm hover:bg-slate-50 transition-colors">Wieder oeffnen</button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-100 px-5 shrink-0">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                data-testid={`task-tab-${tab.key}`}
                className={`flex items-center gap-1.5 px-3 py-2.5 text-xs font-medium border-b-2 transition-colors ${
                  activeTab === tab.key ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'
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
                    <label className="block text-xs font-medium text-slate-600 mb-1">Titel</label>
                    <input value={form.title} onChange={e => setForm(f => ({...f, title: e.target.value}))}
                      className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">Beschreibung</label>
                    <textarea value={form.description} onChange={e => setForm(f => ({...f, description: e.target.value}))}
                      rows={3} className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary resize-none" />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-600 mb-1">Prioritaet</label>
                      <select value={form.priority} onChange={e => setForm(f => ({...f, priority: e.target.value}))}
                        className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary">
                        <option value="low">Niedrig</option><option value="normal">Normal</option><option value="high">Hoch</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-600 mb-1">Faellig</label>
                      <input type="date" value={form.due_date} onChange={e => setForm(f => ({...f, due_date: e.target.value}))}
                        className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">Zugewiesen an</label>
                    <select value={form.assigned_to} onChange={e => setForm(f => ({...f, assigned_to: e.target.value}))}
                      className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary">
                      <option value="">-- Nicht zugewiesen --</option>
                      {staffList.map(s => <option key={s.id} value={s.id}>{s.full_name || s.email}</option>)}
                    </select>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={saveEdit} disabled={saving} data-testid="task-edit-save"
                      className="flex items-center gap-1.5 bg-primary text-white px-4 py-2 rounded-sm text-xs font-medium hover:bg-primary/90 disabled:opacity-50">
                      {saving ? <Loader2 size={13} className="animate-spin" /> : <Save size={13} />} Speichern
                    </button>
                    <button onClick={() => setEditing(false)} className="border border-slate-200 text-slate-600 px-4 py-2 rounded-sm text-xs hover:bg-slate-50">Abbrechen</button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3" data-testid="task-detail-view">
                  <div className="flex justify-end">
                    <button onClick={() => setEditing(true)} data-testid="task-edit-btn"
                      className="flex items-center gap-1 text-xs text-primary font-medium hover:underline">
                      <Edit3 size={12} /> Bearbeiten
                    </button>
                  </div>
                  <dl className="space-y-2 text-sm">
                    <div className="flex"><dt className="w-28 text-slate-500 text-xs shrink-0">Beschreibung</dt><dd className="text-slate-800 text-xs">{task.description || '–'}</dd></div>
                    <div className="flex"><dt className="w-28 text-slate-500 text-xs shrink-0">Prioritaet</dt>
                      <dd><span className={`text-xs px-2 py-0.5 rounded-sm font-medium ${
                        task.priority === 'high' ? 'bg-red-50 text-red-700' : task.priority === 'low' ? 'bg-slate-50 text-slate-500' : 'bg-slate-50 text-slate-700'
                      }`}>{PRIORITY_LABELS[task.priority]}</span></dd>
                    </div>
                    <div className="flex"><dt className="w-28 text-slate-500 text-xs shrink-0">Zugewiesen</dt><dd className="text-slate-800 text-xs flex items-center gap-1"><User size={11} />{task.assigned_name || '–'}</dd></div>
                    <div className="flex"><dt className="w-28 text-slate-500 text-xs shrink-0">Faellig</dt><dd className="text-slate-800 text-xs">{task.due_date ? new Date(task.due_date).toLocaleDateString('de-DE') : '–'}</dd></div>
                    <div className="flex"><dt className="w-28 text-slate-500 text-xs shrink-0">Erstellt</dt><dd className="text-slate-800 text-xs">{task.created_at ? new Date(task.created_at).toLocaleString('de-DE') : '–'}</dd></div>
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
                  className="flex-1 border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary resize-none" />
                <button onClick={addNote} disabled={sendingNote || !newNote.trim()} data-testid="task-note-submit"
                  className="self-end bg-primary text-white px-3 py-2 rounded-sm text-xs hover:bg-primary/90 disabled:opacity-50">
                  {sendingNote ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                </button>
              </div>
              {notes.length === 0 && <p className="text-xs text-slate-400 text-center py-4">Noch keine Notizen</p>}
              {notes.map(n => (
                <div key={n.id} className="border border-slate-100 rounded-sm px-3 py-2" data-testid={`task-note-${n.id}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-medium text-primary">{n.author_name}</span>
                    <span className="text-[10px] text-slate-400">{n.created_at ? new Date(n.created_at).toLocaleString('de-DE') : ''}</span>
                  </div>
                  <p className="text-xs text-slate-700 whitespace-pre-wrap">{n.content}</p>
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
              {attachments.length === 0 && <p className="text-xs text-slate-400 text-center py-4">Keine Anhaenge</p>}
              {attachments.map(a => (
                <div key={a.id} className="flex items-center justify-between border border-slate-100 rounded-sm px-3 py-2" data-testid={`task-att-${a.id}`}>
                  <div className="flex items-center gap-2 min-w-0">
                    <FileText size={14} className="text-slate-400 shrink-0" />
                    <div className="min-w-0">
                      <p className="text-xs text-slate-700 font-medium truncate">{a.filename}</p>
                      <p className="text-[10px] text-slate-400">{a.uploaded_by_name} · {(a.file_size / 1024).toFixed(0)} KB</p>
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
              {history.length === 0 && <p className="text-xs text-slate-400 text-center py-4">Kein Verlauf</p>}
              {history.map((h, i) => (
                <div key={i} className="flex items-start gap-2.5 py-2 border-b border-slate-50 last:border-0">
                  <div className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                    <History size={10} className="text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-slate-700">
                      <span className="font-medium">{HISTORY_LABELS[h.action] || h.action}</span>
                      {h.actor_name && <span className="text-slate-400"> · {h.actor_name}</span>}
                    </p>
                    {h.old_value && h.new_value && <p className="text-[10px] text-slate-500">{h.old_value} → {h.new_value}</p>}
                    {h.new_value && !h.old_value && <p className="text-[10px] text-slate-500">{h.new_value}</p>}
                  </div>
                  <span className="text-[10px] text-slate-300 shrink-0">
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

/* ═══════ Main Tasks Page ═══════ */
export default function StaffTasksPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('open');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', priority: 'normal', due_date: '', assigned_to: '' });
  const [creating, setCreating] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [staffList, setStaffList] = useState([]);
  const [query, setQuery] = useState('');
  const [selectedTaskIds, setSelectedTaskIds] = useState([]);
  const [bulkStatus, setBulkStatus] = useState('in_progress');

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

  const createTask = async () => {
    if (!form.title.trim()) return;
    setCreating(true);
    try {
      const payload = { title: form.title, description: form.description, priority: form.priority };
      if (form.due_date) payload.due_date = form.due_date;
      if (form.assigned_to) payload.assigned_to = form.assigned_to;
      await apiClient.post('/api/tasks', payload, { withCredentials: true });
      setForm({ title: '', description: '', priority: 'normal', due_date: '', assigned_to: '' });
      setShowCreate(false);
      await load();
    } catch {} finally { setCreating(false); }
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
  if (query.trim()) {
    const q = query.trim().toLowerCase();
    filtered = filtered.filter((t) => [t.title, t.description, t.assigned_name, t.application_id, t.status]
      .filter(Boolean).join(' ').toLowerCase().includes(q));
  }
  const openCount = tasks.filter(t => t.status === 'open').length;
  const inProgressCount = tasks.filter(t => t.status === 'in_progress').length;
  const doneCount = tasks.filter(t => t.status === 'done').length;

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 size={24} className="animate-spin text-primary" /></div>;

  return (
    <div className="space-y-4 animate-fade-in" data-testid="staff-tasks-page">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-heading font-bold text-primary">Aufgaben</h1>
          <p className="text-slate-500 text-sm">{openCount} offen, {inProgressCount} in Bearbeitung, {doneCount} erledigt</p>
        </div>
        <button onClick={() => setShowCreate(!showCreate)} data-testid="create-task-btn"
          className="flex items-center gap-1.5 text-sm font-medium bg-primary text-white px-4 py-2 rounded-sm hover:bg-primary/90 transition-colors">
          <Plus size={14} /> Neue Aufgabe
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="bg-white border border-slate-200 rounded-sm p-4 space-y-3" data-testid="task-create-form">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Neue Aufgabe</h3>
            <button onClick={() => setShowCreate(false)} className="text-slate-400 hover:text-slate-600"><X size={16} /></button>
          </div>
          <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
            placeholder="Titel..." data-testid="task-title-input"
            className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
          <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            placeholder="Beschreibung (optional)..." data-testid="task-desc-input" rows={2}
            className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary resize-none" />
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <select value={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}
              data-testid="task-priority-select"
              className="border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary">
              <option value="low">Niedrig</option><option value="normal">Normal</option><option value="high">Hoch</option>
            </select>
            <input type="date" value={form.due_date} onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))}
              data-testid="task-duedate-input"
              className="border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
            <select value={form.assigned_to} onChange={e => setForm(f => ({ ...f, assigned_to: e.target.value }))}
              data-testid="task-assign-select"
              className="border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary">
              <option value="">Mir zuweisen</option>
              {staffList.map(s => <option key={s.id} value={s.id}>{s.full_name || s.email}</option>)}
            </select>
            <button onClick={createTask} disabled={creating || !form.title.trim()} data-testid="task-submit-btn"
              className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors">
              {creating ? <Loader2 size={14} className="animate-spin" /> : 'Erstellen'}
            </button>
          </div>
        </div>
      )}

      <FilterBar testId="task-filter-bar">
        <div className="flex items-center gap-1 bg-slate-100 rounded-sm p-1">
          {[
            { key: 'open', label: 'Offen', count: openCount },
            { key: 'in_progress', label: 'In Bearbeitung', count: inProgressCount },
            { key: 'done', label: 'Erledigt', count: doneCount },
            { key: 'all', label: 'Alle', count: tasks.length },
          ].map(tab => (
            <button key={tab.key} onClick={() => setFilter(tab.key)} data-testid={`task-filter-${tab.key}`}
              className={`px-3 py-1.5 rounded-sm text-xs font-medium transition-colors ${
                filter === tab.key ? 'bg-white text-primary shadow-sm' : 'text-slate-500 hover:text-slate-700'
              }`}>{tab.label} ({tab.count})</button>
          ))}
        </div>
        <select value={priorityFilter} onChange={e => setPriorityFilter(e.target.value)} data-testid="task-priority-filter"
          className="text-xs border border-slate-200 rounded-sm px-2 py-1.5 text-slate-600 focus:outline-none focus:border-primary">
          <option value="all">Alle Prioritaeten</option>
          <option value="high">Hoch</option><option value="normal">Normal</option><option value="low">Niedrig</option>
        </select>
        <SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Suche: Titel, Beschreibung, Zuweisung, Status..." testId="task-search-input" className="w-72" />
      </FilterBar>

      <BulkActions testId="task-bulk-actions" description="Sammelaktionen nur für aktuell gefilterte Aufgaben.">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSelectedTaskIds(selectedTaskIds.length === filtered.length ? [] : filtered.map(t => t.id))}
            className="text-xs border border-slate-200 rounded-sm px-2 py-1 hover:bg-slate-50"
          >
            {selectedTaskIds.length === filtered.length ? 'Auswahl aufheben' : 'Alle gefilterten auswählen'}
          </button>
          <span className="text-xs text-slate-500">{selectedTaskIds.length} ausgewählt</span>
        </div>
        <div className="flex items-center gap-2">
          <select value={bulkStatus} onChange={e => setBulkStatus(e.target.value)} className="text-xs border border-slate-200 rounded-sm px-2 py-1.5">
            <option value="open">Offen</option>
            <option value="in_progress">In Bearbeitung</option>
            <option value="done">Erledigt</option>
          </select>
          <button
            disabled={!selectedTaskIds.length}
            onClick={async () => {
              const updates = await Promise.allSettled(selectedTaskIds.map((id) =>
                apiClient.put(`/api/tasks/${id}`, { status: bulkStatus }, { withCredentials: true })
              ));
              const successById = new Map();
              updates.forEach((r, idx) => {
                if (r.status === 'fulfilled') successById.set(selectedTaskIds[idx], r.value.data);
              });
              setTasks(prev => prev.map(t => successById.get(t.id) || t));
              setSelectedTaskIds([]);
            }}
            className="text-xs bg-primary text-white rounded-sm px-3 py-1.5 disabled:opacity-40"
            data-testid="task-bulk-status-btn"
          >
            Sammelaktion: Status setzen
          </button>
        </div>
      </BulkActions>

      {/* Task List */}
      <div className="space-y-2">
        {filtered.length === 0 ? (
          <EmptyState icon={CheckSquare} title="Keine Aufgaben in dieser Ansicht" testId="tasks-empty" />
        ) : (
          filtered.map(task => (
            <div key={task.id} onClick={() => setSelectedTask(task)}
              className="bg-white border border-slate-200 rounded-sm p-4 hover:border-primary/30 transition-colors cursor-pointer" data-testid={`task-item-${task.id}`}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <input
                      type="checkbox"
                      checked={selectedTaskIds.includes(task.id)}
                      onChange={(e) => {
                        e.stopPropagation();
                        setSelectedTaskIds(prev => e.target.checked ? [...prev, task.id] : prev.filter(id => id !== task.id));
                      }}
                      onClick={(e) => e.stopPropagation()}
                      data-testid={`task-select-${task.id}`}
                    />
                    {task.status === 'done' ? <CheckCircle size={14} className="text-primary shrink-0" /> :
                     task.status === 'in_progress' ? <AlertCircle size={14} className="text-primary shrink-0" /> :
                     <Clock size={14} className="text-slate-400 shrink-0" />}
                    <h4 className={`text-sm font-medium ${task.status === 'done' ? 'text-slate-400 line-through' : 'text-slate-800'}`}>{task.title}</h4>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-sm border font-medium ${
                      task.priority === 'high' ? 'bg-red-50 text-red-700 border-red-200' :
                      task.priority === 'low' ? 'bg-slate-50 text-slate-500 border-slate-100' :
                      'bg-slate-50 text-slate-700 border-slate-200'
                    }`}>{PRIORITY_LABELS[task.priority]}</span>
                  </div>
                  {task.description && <p className="text-xs text-slate-500 ml-5 line-clamp-1">{task.description}</p>}
                  <div className="flex items-center gap-3 mt-1.5 ml-5 text-[10px] text-slate-400">
                    {task.assigned_name && <span className="flex items-center gap-1"><User size={10} />{task.assigned_name}</span>}
                    {task.due_date && <span>Faellig: {new Date(task.due_date).toLocaleDateString('de-DE')}</span>}
                    {task.created_at && <span>Erstellt: {new Date(task.created_at).toLocaleDateString('de-DE')}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1 shrink-0" onClick={e => e.stopPropagation()}>
                  {task.status !== 'in_progress' && task.status !== 'done' && (
                    <button onClick={() => updateStatus(task.id, 'in_progress')} data-testid={`task-start-${task.id}`}
                      className="text-[11px] px-2.5 py-1.5 bg-primary text-white rounded-sm hover:bg-primary/90 transition-colors font-medium">Starten</button>
                  )}
                  {task.status !== 'done' && (
                    <button onClick={() => updateStatus(task.id, 'done')} data-testid={`task-done-${task.id}`}
                      className="text-[11px] px-2.5 py-1.5 border border-primary text-primary rounded-sm hover:bg-primary/5 transition-colors font-medium">Erledigt</button>
                  )}
                  {task.status === 'done' && (
                    <button onClick={() => updateStatus(task.id, 'open')} data-testid={`task-reopen-${task.id}`}
                      className="text-[11px] px-2.5 py-1.5 border border-slate-200 text-slate-500 rounded-sm hover:bg-slate-50 transition-colors font-medium">Wieder oeffnen</button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Detail Modal */}
      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          onUpdate={handleTaskUpdate}
          staffList={staffList}
        />
      )}
    </div>
  );
}
