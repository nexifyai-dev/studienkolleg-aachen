import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { CalendarDays, Plus, X, CheckCircle, Clock, Loader2, MapPin, Users, Search, Edit3, Trash2, Save, XCircle } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { getLang } from '../../lib/utils';
import { toast } from 'sonner';

const TYPE_OPTIONS = [
  { key: 'consultation', de: 'Beratung', en: 'Consultation' },
  { key: 'course', de: 'Kurs', en: 'Course' },
  { key: 'exam', de: 'Pruefung', en: 'Exam' },
  { key: 'interview', de: 'Gespraech', en: 'Interview' },
  { key: 'other', de: 'Sonstiges', en: 'Other' },
];

const STATUS_OPTIONS = [
  { key: 'confirmed', de: 'Bestaetigt', en: 'Confirmed', color: '#10B981' },
  { key: 'pending', de: 'Ausstehend', en: 'Pending', color: '#F59E0B' },
  { key: 'cancelled', de: 'Storniert', en: 'Cancelled', color: '#9CA3AF' },
  { key: 'completed', de: 'Abgeschlossen', en: 'Completed', color: '#6B7280' },
];

function addMinutes(time, min) {
  if (!time) return time;
  const [h, m] = time.split(':').map(Number);
  const total = h * 60 + m + min;
  return `${String(Math.floor(total / 60) % 24).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
}

/* ═══════ Detail / Edit Modal ═══════ */
function AppointmentModal({ apt, onClose, onSaved, onDeleted, lang }) {
  const [editing, setEditing] = useState(!apt.id);
  const [form, setForm] = useState({
    title: apt.title || '', type: apt.type || 'consultation',
    date: apt.date || '', time: apt.time || '', duration_min: apt.duration_min || 30,
    description: apt.description || '', location: apt.location || 'Online (Zoom)',
    status: apt.status || 'confirmed', applicant_id: apt.applicant_id || '',
  });
  const [saving, setSaving] = useState(false);
  const [slots, setSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);

  const typeLabel = (key) => TYPE_OPTIONS.find(t => t.key === key)?.[lang] || key;
  const statusOpt = STATUS_OPTIONS.find(s => s.key === form.status) || STATUS_OPTIONS[0];

  const loadSlots = async (date) => {
    if (!date) return;
    setLoadingSlots(true);
    try {
      const res = await apiClient.get(`/api/appointments/available-slots?date=${date}`);
      setSlots(res.data.slots || []);
    } catch { setSlots([]); }
    finally { setLoadingSlots(false); }
  };

  useEffect(() => { if (editing && form.date) loadSlots(form.date); }, [editing, form.date]);

  const save = async () => {
    if (!form.date || !form.time) { toast.error(lang === 'de' ? 'Datum und Uhrzeit erforderlich' : 'Date and time required'); return; }
    setSaving(true);
    try {
      if (apt.id) {
        await apiClient.put(`/api/appointments/${apt.id}`, form);
        toast.success(lang === 'de' ? 'Termin aktualisiert' : 'Appointment updated');
      } else {
        await apiClient.post('/api/appointments', form);
        toast.success(lang === 'de' ? 'Termin erstellt' : 'Appointment created');
      }
      onSaved();
    } catch { toast.error(lang === 'de' ? 'Fehler beim Speichern' : 'Failed to save'); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    if (!window.confirm(lang === 'de' ? 'Termin wirklich stornieren?' : 'Really cancel this appointment?')) return;
    try {
      await apiClient.delete(`/api/appointments/${apt.id}`);
      toast.success(lang === 'de' ? 'Termin storniert' : 'Appointment cancelled');
      onDeleted();
    } catch { toast.error(lang === 'de' ? 'Stornierung fehlgeschlagen' : 'Cancellation failed'); }
  };

  return (
    <div className="w2g-modal-overlay" onClick={onClose} data-testid="apt-modal">
      <div className="w2g-modal max-w-lg" onClick={e => e.stopPropagation()}>
        <div className="w2g-modal-header">
          <h2 className="font-heading text-base font-bold text-[var(--color-primary)] flex items-center gap-2">
            <CalendarDays size={16} /> {apt.id ? (editing ? (lang === 'de' ? 'Termin bearbeiten' : 'Edit Appointment') : (form.title || 'Termin')) : (lang === 'de' ? 'Neuer Termin' : 'New Appointment')}
          </h2>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="apt-modal-close"><X size={18} /></button>
        </div>
        <div className="w2g-modal-body space-y-4">
          {editing ? (
            <>
              <div>
                <label className="w2g-label">{lang === 'de' ? 'Titel' : 'Title'}</label>
                <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} className="w2g-input" placeholder={lang === 'de' ? 'z.B. Beratung Ahmed' : 'e.g. Consultation Ahmed'} data-testid="apt-title" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="w2g-label">{lang === 'de' ? 'Art' : 'Type'}</label>
                  <select value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))} className="w2g-select" data-testid="apt-type">
                    {TYPE_OPTIONS.map(t => <option key={t.key} value={t.key}>{t[lang]}</option>)}
                  </select>
                </div>
                <div>
                  <label className="w2g-label">Status</label>
                  <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))} className="w2g-select" data-testid="apt-status">
                    {STATUS_OPTIONS.map(s => <option key={s.key} value={s.key}>{s[lang]}</option>)}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="w2g-label">{lang === 'de' ? 'Datum' : 'Date'}</label>
                  <input type="date" value={form.date} onChange={e => { setForm(f => ({ ...f, date: e.target.value, time: '' })); loadSlots(e.target.value); }} className="w2g-input" data-testid="apt-date" />
                </div>
                <div>
                  <label className="w2g-label">{lang === 'de' ? 'Uhrzeit' : 'Time'}</label>
                  <input type="time" value={form.time} onChange={e => setForm(f => ({ ...f, time: e.target.value }))} className="w2g-input" data-testid="apt-time" />
                </div>
              </div>
              {form.date && slots.length > 0 && (
                <div>
                  <label className="w2g-label text-[10px]">{lang === 'de' ? 'Freie Slots' : 'Available Slots'}</label>
                  <div className="flex flex-wrap gap-1">
                    {slots.slice(0, 16).map(s => (
                      <button key={s} onClick={() => setForm(f => ({ ...f, time: s }))}
                        className={`text-[10px] px-2 py-1 rounded border ${form.time === s ? 'border-[var(--color-primary)] bg-[var(--color-primary)] text-white' : 'border-[var(--color-divider)] text-[var(--color-text-secondary)] hover:border-[var(--color-primary)]'}`}
                        data-testid={`apt-slot-${s}`}>{s}</button>
                    ))}
                  </div>
                </div>
              )}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="w2g-label">{lang === 'de' ? 'Dauer (Min.)' : 'Duration (min)'}</label>
                  <input type="number" value={form.duration_min} onChange={e => setForm(f => ({ ...f, duration_min: parseInt(e.target.value) || 30 }))} className="w2g-input" data-testid="apt-duration" />
                </div>
                <div>
                  <label className="w2g-label">{lang === 'de' ? 'Ort' : 'Location'}</label>
                  <input value={form.location} onChange={e => setForm(f => ({ ...f, location: e.target.value }))} className="w2g-input" data-testid="apt-location" />
                </div>
              </div>
              <div>
                <label className="w2g-label">{lang === 'de' ? 'Beschreibung' : 'Description'}</label>
                <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={2} className="w2g-textarea" data-testid="apt-desc" />
              </div>
            </>
          ) : (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="text-xs text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Datum' : 'Date'}</span><p className="font-medium">{form.date}</p></div>
                <div><span className="text-xs text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Uhrzeit' : 'Time'}</span><p className="font-medium">{form.time || '-'}</p></div>
                <div><span className="text-xs text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Art' : 'Type'}</span><p className="font-medium">{typeLabel(form.type)}</p></div>
                <div><span className="text-xs text-[var(--color-text-tertiary)]">Status</span>
                  <p className="font-medium" style={{ color: statusOpt.color }}>{statusOpt[lang]}</p>
                </div>
              </div>
              {apt.user_name && (
                <div className="flex items-center gap-2 text-sm"><Users size={14} className="text-[var(--color-text-tertiary)]" /> {apt.user_name} {apt.user_email ? `(${apt.user_email})` : ''}</div>
              )}
              {form.location && <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]"><MapPin size={14} /> {form.location}</div>}
              {form.description && <p className="text-sm text-[var(--color-text-secondary)] bg-[var(--color-surface-elevated)] p-3 rounded-[var(--radius-sm)]">{form.description}</p>}
            </div>
          )}
        </div>
        <div className="w2g-modal-footer">
          {apt.id && !editing && form.status !== 'cancelled' && (
            <button onClick={handleDelete} className="w2g-btn-outline text-[var(--color-danger)] border-[var(--color-danger-border)] text-xs" data-testid="apt-cancel-btn"><Trash2 size={12} /> {lang === 'de' ? 'Stornieren' : 'Cancel'}</button>
          )}
          <div className="flex-1" />
          {editing ? (
            <>
              <button onClick={() => apt.id ? setEditing(false) : onClose()} className="w2g-btn-secondary text-xs">{lang === 'de' ? 'Abbrechen' : 'Cancel'}</button>
              <button onClick={save} disabled={saving} className="w2g-btn-primary text-xs" data-testid="apt-save"><Save size={12} /> {saving ? <Loader2 size={12} className="animate-spin" /> : (lang === 'de' ? 'Speichern' : 'Save')}</button>
            </>
          ) : (
            <>
              <button onClick={() => setEditing(true)} className="w2g-btn-secondary text-xs" data-testid="apt-edit-btn"><Edit3 size={12} /> {lang === 'de' ? 'Bearbeiten' : 'Edit'}</button>
              <button onClick={onClose} className="w2g-btn-primary text-xs">{lang === 'de' ? 'Schliessen' : 'Close'}</button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/* ═══════ Main Staff Appointments Page ═══════ */
export default function StaffAppointmentsPage() {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null); // apt object or { date, time }
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const load = useCallback(async () => {
    try {
      const res = await apiClient.get('/api/appointments');
      setAppointments(res.data || []);
    } catch { /* */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = appointments.filter(a => {
    if (statusFilter && a.status !== statusFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (a.title || '').toLowerCase().includes(q) ||
             (a.user_name || '').toLowerCase().includes(q) ||
             (a.user_email || '').toLowerCase().includes(q);
    }
    return true;
  });

  const calendarEvents = filtered
    .filter(a => a.status !== 'cancelled')
    .map(a => ({
      id: a.id,
      title: `${a.user_name ? a.user_name + ' - ' : ''}${a.title || TYPE_OPTIONS.find(t => t.key === a.type)?.[lang] || a.type}`,
      start: a.date + (a.time ? `T${a.time}` : ''),
      end: a.date + (a.time ? `T${addMinutes(a.time, a.duration_min || 30)}` : ''),
      backgroundColor: (STATUS_OPTIONS.find(s => s.key === a.status) || STATUS_OPTIONS[0]).color,
      borderColor: 'transparent',
      extendedProps: a,
    }));

  const stats = {
    total: appointments.filter(a => a.status !== 'cancelled').length,
    confirmed: appointments.filter(a => a.status === 'confirmed').length,
    pending: appointments.filter(a => a.status === 'pending').length,
    today: appointments.filter(a => a.status !== 'cancelled' && a.date === new Date().toISOString().slice(0, 10)).length,
  };

  if (loading) return <div className="w2g-loading"><div className="w2g-spinner" /><p className="w2g-loading-text">{lang === 'de' ? 'Wird geladen...' : 'Loading...'}</p></div>;

  return (
    <PageScaffold
      title={lang === 'de' ? 'Terminverwaltung' : 'Appointment Management'}
      subtitle={`${stats.total} ${lang === 'de' ? 'Termine' : 'Appointments'}${stats.today > 0 ? ` · ${stats.today} ${lang === 'de' ? 'heute' : 'today'}` : ''}`}
      testId="staff-appointments-page"
      actions={
        <button onClick={() => setModal({ date: new Date().toISOString().slice(0, 10), time: '', title: '', type: 'consultation', status: 'confirmed' })} className="w2g-btn-primary" data-testid="create-apt-btn">
          <Plus size={14} /> {lang === 'de' ? 'Neuer Termin' : 'New Appointment'}
        </button>
      }
      toolbar={
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                placeholder={lang === 'de' ? 'Name, Titel suchen...' : 'Search name, title...'} className="w2g-search pl-9" data-testid="apt-search" />
              {searchQuery && <button onClick={() => setSearchQuery('')} className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]"><XCircle size={14} /></button>}
            </div>
          }
          filters={[
            <select key="status" value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="w2g-select text-xs" data-testid="apt-status-filter">
              <option value="">{lang === 'de' ? 'Alle Status' : 'All Status'}</option>
              {STATUS_OPTIONS.map(s => <option key={s.key} value={s.key}>{s[lang]}</option>)}
            </select>,
          ]}
        />
      }
    >
      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card data-testid="apt-kpi-total"><CardContent className="py-3 px-4"><p className="text-2xl font-bold text-[var(--color-text-primary)]">{stats.total}</p><p className="text-[10px] text-[var(--color-text-tertiary)] uppercase">{lang === 'de' ? 'Gesamt' : 'Total'}</p></CardContent></Card>
        <Card data-testid="apt-kpi-confirmed"><CardContent className="py-3 px-4"><p className="text-2xl font-bold text-[var(--color-success)]">{stats.confirmed}</p><p className="text-[10px] text-[var(--color-text-tertiary)] uppercase">{lang === 'de' ? 'Bestaetigt' : 'Confirmed'}</p></CardContent></Card>
        <Card data-testid="apt-kpi-pending"><CardContent className="py-3 px-4"><p className="text-2xl font-bold text-[var(--color-warning)]">{stats.pending}</p><p className="text-[10px] text-[var(--color-text-tertiary)] uppercase">{lang === 'de' ? 'Ausstehend' : 'Pending'}</p></CardContent></Card>
        <Card data-testid="apt-kpi-today"><CardContent className="py-3 px-4"><p className="text-2xl font-bold text-[var(--color-primary)]">{stats.today}</p><p className="text-[10px] text-[var(--color-text-tertiary)] uppercase">{lang === 'de' ? 'Heute' : 'Today'}</p></CardContent></Card>
      </div>

      {/* Calendar */}
      <Card data-testid="apt-calendar">
        <CardContent className="p-4">
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            locale={lang}
            headerToolbar={{
              left: 'prev,next today',
              center: 'title',
              right: 'dayGridMonth,timeGridWeek,timeGridDay',
            }}
            events={calendarEvents}
            eventClick={(info) => setModal(info.event.extendedProps)}
            dateClick={(info) => setModal({ date: info.dateStr, time: '', title: '', type: 'consultation', status: 'confirmed', location: 'Online (Zoom)' })}
            height="auto"
            dayMaxEvents={4}
            nowIndicator
            selectable
            buttonText={{
              today: lang === 'de' ? 'Heute' : 'Today',
              month: lang === 'de' ? 'Monat' : 'Month',
              week: lang === 'de' ? 'Woche' : 'Week',
              day: lang === 'de' ? 'Tag' : 'Day',
            }}
          />
        </CardContent>
      </Card>

      {/* Modal */}
      {modal && (
        <AppointmentModal
          apt={modal}
          lang={lang}
          onClose={() => setModal(null)}
          onSaved={() => { setModal(null); load(); }}
          onDeleted={() => { setModal(null); load(); }}
        />
      )}
    </PageScaffold>
  );
}
