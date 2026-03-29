import React, { useEffect, useState, useCallback } from 'react';
import apiClient from '../../lib/apiClient';
import { useAuth } from '../../contexts/AuthContext';
import {
  CheckSquare, Clock, AlertCircle, Plus, Loader2, CheckCircle, X
} from 'lucide-react';

const PRIORITY_COLORS = {
  high: 'bg-red-50 text-red-700 border-red-200',
  normal: 'bg-slate-50 text-slate-700 border-slate-200',
  low: 'bg-slate-50 text-slate-500 border-slate-100',
};
const PRIORITY_LABELS = { high: 'Hoch', normal: 'Normal', low: 'Niedrig' };
const STATUS_ICONS = {
  open: Clock,
  in_progress: AlertCircle,
  done: CheckCircle,
};

export default function StaffTasksPage() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('open');
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', priority: 'normal' });
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    try {
      const r = await apiClient.get('/api/tasks', { withCredentials: true });
      setTasks(r.data || []);
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const createTask = async () => {
    if (!form.title.trim()) return;
    setCreating(true);
    try {
      await apiClient.post('/api/tasks', form, { withCredentials: true });
      setForm({ title: '', description: '', priority: 'normal' });
      setShowCreate(false);
      await load();
    } catch {} finally { setCreating(false); }
  };

  const updateStatus = async (taskId, status) => {
    try {
      await apiClient.put(`/api/tasks/${taskId}`, { status }, { withCredentials: true });
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status } : t));
    } catch {}
  };

  const filtered = filter === 'all' ? tasks : tasks.filter(t => t.status === filter);
  const openCount = tasks.filter(t => t.status === 'open').length;
  const inProgressCount = tasks.filter(t => t.status === 'in_progress').length;
  const doneCount = tasks.filter(t => t.status === 'done').length;

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-primary" />
    </div>
  );

  return (
    <div className="space-y-4 animate-fade-in" data-testid="staff-tasks-page">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-heading font-bold text-primary">Aufgaben</h1>
          <p className="text-slate-500 text-sm">{openCount} offen, {inProgressCount} in Bearbeitung, {doneCount} erledigt</p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          data-testid="create-task-btn"
          className="flex items-center gap-1.5 text-sm font-medium bg-primary text-white px-4 py-2 rounded-sm hover:bg-primary/90 transition-colors"
        >
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
          <input
            value={form.title}
            onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
            placeholder="Titel..."
            data-testid="task-title-input"
            className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary"
          />
          <textarea
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            placeholder="Beschreibung (optional)..."
            data-testid="task-desc-input"
            rows={2}
            className="w-full border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary resize-none"
          />
          <div className="flex items-center gap-3">
            <select
              value={form.priority}
              onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}
              data-testid="task-priority-select"
              className="border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary"
            >
              <option value="low">Niedrig</option>
              <option value="normal">Normal</option>
              <option value="high">Hoch</option>
            </select>
            <button
              onClick={createTask}
              disabled={creating || !form.title.trim()}
              data-testid="task-submit-btn"
              className="bg-primary text-white px-4 py-2 rounded-sm text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {creating ? <Loader2 size={14} className="animate-spin" /> : 'Erstellen'}
            </button>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center gap-1 bg-slate-100 rounded-sm p-1 w-fit">
        {[
          { key: 'open', label: 'Offen', count: openCount },
          { key: 'in_progress', label: 'In Bearbeitung', count: inProgressCount },
          { key: 'done', label: 'Erledigt', count: doneCount },
          { key: 'all', label: 'Alle', count: tasks.length },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            data-testid={`task-filter-${tab.key}`}
            className={`px-3 py-1.5 rounded-sm text-xs font-medium transition-colors ${
              filter === tab.key ? 'bg-white text-primary shadow-sm' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>

      {/* Task List */}
      <div className="space-y-2">
        {filtered.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-sm p-8 text-center text-slate-400">
            <CheckSquare size={28} className="mx-auto mb-2" />
            <p className="text-sm">Keine Aufgaben in dieser Ansicht</p>
          </div>
        ) : (
          filtered.map(task => {
            const StatusIcon = STATUS_ICONS[task.status] || Clock;
            return (
              <div key={task.id} className="bg-white border border-slate-200 rounded-sm p-4 hover:border-primary/20 transition-colors" data-testid={`task-item-${task.id}`}>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <StatusIcon size={14} className={task.status === 'done' ? 'text-green-500' : task.status === 'in_progress' ? 'text-amber-500' : 'text-slate-400'} />
                      <h4 className={`text-sm font-medium ${task.status === 'done' ? 'text-slate-400 line-through' : 'text-slate-800'}`}>{task.title}</h4>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded border ${PRIORITY_COLORS[task.priority] || PRIORITY_COLORS.normal}`}>
                        {PRIORITY_LABELS[task.priority] || task.priority}
                      </span>
                    </div>
                    {task.description && <p className="text-xs text-slate-500 ml-5">{task.description}</p>}
                    <div className="flex items-center gap-3 mt-2 ml-5 text-[10px] text-slate-400">
                      {task.due_date && <span>Fällig: {new Date(task.due_date).toLocaleDateString('de-DE')}</span>}
                      {task.created_at && <span>Erstellt: {new Date(task.created_at).toLocaleDateString('de-DE')}</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    {task.status !== 'in_progress' && task.status !== 'done' && (
                      <button
                        onClick={() => updateStatus(task.id, 'in_progress')}
                        data-testid={`task-start-${task.id}`}
                        className="text-[11px] px-2 py-1 border border-amber-200 text-amber-600 rounded-sm hover:bg-amber-50 transition-colors"
                      >
                        Starten
                      </button>
                    )}
                    {task.status !== 'done' && (
                      <button
                        onClick={() => updateStatus(task.id, 'done')}
                        data-testid={`task-done-${task.id}`}
                        className="text-[11px] px-2 py-1 border border-green-200 text-green-600 rounded-sm hover:bg-green-50 transition-colors"
                      >
                        Erledigt
                      </button>
                    )}
                    {task.status === 'done' && (
                      <button
                        onClick={() => updateStatus(task.id, 'open')}
                        data-testid={`task-reopen-${task.id}`}
                        className="text-[11px] px-2 py-1 border border-slate-200 text-slate-500 rounded-sm hover:bg-slate-50 transition-colors"
                      >
                        Wieder öffnen
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
