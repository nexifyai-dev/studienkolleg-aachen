import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { CalendarDays, Plus, X, CheckCircle, Clock, Loader2, MapPin } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { getLang } from '../../lib/utils';
import { toast } from 'sonner';

const TYPE_LABELS = {
  de: { consultation: 'Beratung', course: 'Kurs', exam: 'Pruefung', interview: 'Gespraech', other: 'Sonstiges' },
  en: { consultation: 'Consultation', course: 'Course', exam: 'Exam', interview: 'Interview', other: 'Other' },
};

const STATUS_COLORS = {
  confirmed: { bg: '#10B981', border: '#059669' },
  pending: { bg: '#F59E0B', border: '#D97706' },
  cancelled: { bg: '#9CA3AF', border: '#6B7280' },
  completed: { bg: '#6B7280', border: '#4B5563' },
};

export default function ApplicantAppointmentsPage() {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showBooking, setShowBooking] = useState(false);
  const [selectedApt, setSelectedApt] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);

  const L = {
    title: lang === 'de' ? 'Termine & Kalender' : 'Appointments & Calendar',
    subtitle: lang === 'de' ? 'Termine verwalten und neue Beratungsgespraeche buchen.' : 'Manage appointments and book consultations.',
    book: lang === 'de' ? 'Termin buchen' : 'Book Appointment',
    next: lang === 'de' ? 'Naechster Termin' : 'Next Appointment',
    total: lang === 'de' ? 'Termine gesamt' : 'Total Appointments',
    noApt: lang === 'de' ? 'Kein Termin' : 'No appointment',
    cancel: lang === 'de' ? 'Stornieren' : 'Cancel',
    close: lang === 'de' ? 'Schliessen' : 'Close',
    status: lang === 'de' ? 'Status' : 'Status',
    type: lang === 'de' ? 'Art' : 'Type',
    location: lang === 'de' ? 'Ort' : 'Location',
    date: lang === 'de' ? 'Datum' : 'Date',
    time: lang === 'de' ? 'Uhrzeit' : 'Time',
    confirmed: lang === 'de' ? 'Bestaetigt' : 'Confirmed',
    pending: lang === 'de' ? 'Ausstehend' : 'Pending',
    cancelled: lang === 'de' ? 'Storniert' : 'Cancelled',
    completed: lang === 'de' ? 'Abgeschlossen' : 'Completed',
  };

  const statusLabel = (s) => L[s] || s;

  const load = useCallback(async () => {
    try {
      const res = await apiClient.get('/api/appointments', { withCredentials: true });
      setAppointments(res.data || []);
    } catch { /* */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const upcoming = appointments
    .filter(a => a.status !== 'cancelled' && a.date >= new Date().toISOString().slice(0, 10))
    .sort((a, b) => (a.date + a.time).localeCompare(b.date + b.time));

  const calendarEvents = appointments
    .filter(a => a.status !== 'cancelled')
    .map(a => ({
      id: a.id,
      title: a.title || TYPE_LABELS[lang][a.type] || a.type,
      start: a.date + (a.time ? `T${a.time}` : ''),
      end: a.date + (a.time ? `T${addMinutes(a.time, a.duration_min || 30)}` : ''),
      backgroundColor: (STATUS_COLORS[a.status] || STATUS_COLORS.pending).bg,
      borderColor: (STATUS_COLORS[a.status] || STATUS_COLORS.pending).border,
      extendedProps: a,
    }));

  const handleCancel = async (id) => {
    try {
      await apiClient.delete(`/api/appointments/${id}`, { withCredentials: true });
      toast.success(lang === 'de' ? 'Termin storniert' : 'Appointment cancelled');
      setSelectedApt(null);
      load();
    } catch {
      toast.error(lang === 'de' ? 'Stornierung fehlgeschlagen' : 'Cancellation failed');
    }
  };

  return (
    <PageScaffold
      title={L.title}
      subtitle={L.subtitle}
      testId="applicant-appointments-page"
      actions={
        <button onClick={() => { setSelectedDate(null); setShowBooking(true); }} className="w2g-btn-primary" data-testid="book-appointment-btn">
          <Plus size={14} /> {L.book}
        </button>
      }
    >
      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="w2g-card" data-testid="kpi-next-apt">
          <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)]/8 text-[var(--color-primary)]"><CalendarDays size={16} /></div>
          <p className="text-xs uppercase tracking-wider text-[var(--color-text-tertiary)]">{L.next}</p>
          <p className="mt-1 text-sm font-semibold text-[var(--color-text-primary)]">
            {upcoming[0] ? `${upcoming[0].date} ${upcoming[0].time || ''}` : L.noApt}
          </p>
        </div>
        <div className="w2g-card" data-testid="kpi-total-apts">
          <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)]/8 text-[var(--color-primary)]"><Clock size={16} /></div>
          <p className="text-xs uppercase tracking-wider text-[var(--color-text-tertiary)]">{L.total}</p>
          <p className="mt-1 text-sm font-semibold text-[var(--color-text-primary)]">{appointments.filter(a => a.status !== 'cancelled').length}</p>
        </div>
        <div className="w2g-card" data-testid="kpi-upcoming">
          <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-success-bg)] text-[var(--color-success)]"><CheckCircle size={16} /></div>
          <p className="text-xs uppercase tracking-wider text-[var(--color-text-tertiary)]">{L.confirmed}</p>
          <p className="mt-1 text-sm font-semibold text-[var(--color-text-primary)]">{appointments.filter(a => a.status === 'confirmed').length}</p>
        </div>
      </div>

      {/* FullCalendar */}
      <div className="w2g-card p-4" data-testid="appointments-calendar">
        {loading ? (
          <div className="flex items-center justify-center py-16"><Loader2 size={20} className="animate-spin text-[var(--color-text-tertiary)]" /></div>
        ) : (
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            locale={lang}
            headerToolbar={{
              left: 'prev,next today',
              center: 'title',
              right: 'dayGridMonth,timeGridWeek',
            }}
            events={calendarEvents}
            eventClick={(info) => setSelectedApt(info.event.extendedProps)}
            dateClick={(info) => { setSelectedDate(info.dateStr); setShowBooking(true); }}
            height="auto"
            dayMaxEvents={3}
            nowIndicator
            selectable
            buttonText={{
              today: lang === 'de' ? 'Heute' : 'Today',
              month: lang === 'de' ? 'Monat' : 'Month',
              week: lang === 'de' ? 'Woche' : 'Week',
            }}
          />
        )}
      </div>

      {/* Detail Modal */}
      {selectedApt && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => setSelectedApt(null)} data-testid="apt-detail-modal">
          <div className="w-full max-w-md bg-white rounded-[var(--radius-md)] border border-[var(--color-divider)] overflow-hidden" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--color-divider-subtle)]">
              <h2 className="text-base font-bold text-[var(--color-text-primary)]">{selectedApt.title}</h2>
              <button onClick={() => setSelectedApt(null)} className="w2g-btn-icon"><X size={18} /></button>
            </div>
            <div className="px-5 py-4 space-y-3">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="text-xs text-[var(--color-text-tertiary)]">{L.date}</span><p className="font-medium">{selectedApt.date}</p></div>
                <div><span className="text-xs text-[var(--color-text-tertiary)]">{L.time}</span><p className="font-medium">{selectedApt.time || '–'}</p></div>
                <div><span className="text-xs text-[var(--color-text-tertiary)]">{L.type}</span><p className="font-medium">{TYPE_LABELS[lang][selectedApt.type] || selectedApt.type}</p></div>
                <div><span className="text-xs text-[var(--color-text-tertiary)]">{L.status}</span>
                  <p className={`font-medium ${selectedApt.status === 'confirmed' ? 'text-[var(--color-success)]' : selectedApt.status === 'pending' ? 'text-[var(--color-warning)]' : 'text-[var(--color-text-secondary)]'}`}>
                    {statusLabel(selectedApt.status)}
                  </p>
                </div>
              </div>
              {selectedApt.location && (
                <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
                  <MapPin size={14} /> {selectedApt.location}
                </div>
              )}
              {selectedApt.description && (
                <p className="text-sm text-[var(--color-text-secondary)] bg-[var(--color-surface-elevated)] p-3 rounded-[var(--radius-sm)]">{selectedApt.description}</p>
              )}
            </div>
            <div className="px-5 py-3 border-t border-[var(--color-divider-subtle)] flex gap-2">
              {selectedApt.status !== 'cancelled' && (
                <button onClick={() => handleCancel(selectedApt.id)} className="w2g-btn-outline w2g-btn-sm text-[var(--color-danger)] border-[var(--color-danger-border)]" data-testid="apt-cancel-btn">
                  {L.cancel}
                </button>
              )}
              <button onClick={() => setSelectedApt(null)} className="w2g-btn-secondary w2g-btn-sm ml-auto">{L.close}</button>
            </div>
          </div>
        </div>
      )}

      {/* Booking Modal */}
      {showBooking && (
        <BookingModal
          lang={lang}
          initialDate={selectedDate}
          onClose={() => setShowBooking(false)}
          onBooked={() => { setShowBooking(false); load(); }}
        />
      )}
    </PageScaffold>
  );
}

function addMinutes(time, min) {
  if (!time) return time;
  const [h, m] = time.split(':').map(Number);
  const total = h * 60 + m + min;
  return `${String(Math.floor(total / 60) % 24).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
}

function BookingModal({ lang, initialDate, onClose, onBooked }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ type: 'consultation', date: initialDate || '', time: '', description: '' });
  const [slots, setSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const TYPE_L = TYPE_LABELS[lang];
  const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1);
  const minDate = tomorrow.toISOString().slice(0, 10);

  const loadSlots = async (date) => {
    setLoadingSlots(true);
    try {
      const res = await apiClient.get(`/api/appointments/available-slots?date=${date}`, { withCredentials: true });
      setSlots(res.data.slots || []);
    } catch { setSlots([]); }
    finally { setLoadingSlots(false); }
  };

  const handleDateChange = (date) => {
    setForm(f => ({ ...f, date, time: '' }));
    if (date) loadSlots(date);
  };

  useEffect(() => { if (initialDate) loadSlots(initialDate); }, [initialDate]);

  const submit = async () => {
    setSubmitting(true);
    try {
      await apiClient.post('/api/appointments', {
        title: `${TYPE_L[form.type] || 'Termin'} – ${lang === 'de' ? 'Terminanfrage' : 'Appointment Request'}`,
        type: form.type, date: form.date, time: form.time,
        description: form.description, location: 'Online (Zoom)',
      }, { withCredentials: true });
      setSuccess(true);
      setTimeout(() => onBooked(), 1200);
    } catch { setSubmitting(false); toast.error(lang === 'de' ? 'Buchung fehlgeschlagen' : 'Booking failed'); }
  };

  const L = {
    bookTitle: lang === 'de' ? 'Termin buchen' : 'Book Appointment',
    step1: lang === 'de' ? '1. Art des Termins' : '1. Appointment Type',
    step2: lang === 'de' ? '2. Datum & Uhrzeit' : '2. Date & Time',
    step3: lang === 'de' ? '3. Bestaetigung' : '3. Confirmation',
    next: lang === 'de' ? 'Weiter' : 'Next',
    back: lang === 'de' ? 'Zurueck' : 'Back',
    dateLabel: lang === 'de' ? 'Datum' : 'Date',
    slotsLabel: lang === 'de' ? 'Verfuegbare Zeiten' : 'Available Slots',
    noSlots: lang === 'de' ? 'Keine Slots an diesem Tag' : 'No slots on this day',
    notes: lang === 'de' ? 'Anmerkungen (optional)' : 'Notes (optional)',
    confirm: lang === 'de' ? 'Termin buchen' : 'Book Appointment',
    success: lang === 'de' ? 'Termin erfolgreich gebucht!' : 'Appointment booked!',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" data-testid="booking-modal">
      <div className="w-full max-w-lg bg-white rounded-[var(--radius-md)] overflow-hidden border border-[var(--color-divider)]">
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--color-divider-subtle)]">
          <h2 className="text-base font-bold text-[var(--color-text-primary)]">{L.bookTitle}</h2>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="booking-modal-close"><X size={18} /></button>
        </div>
        {success ? (
          <div className="px-5 py-10 text-center">
            <CheckCircle size={40} className="mx-auto text-[var(--color-success)] mb-3" />
            <p className="text-base font-semibold">{L.success}</p>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">{form.date} {form.time}</p>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-2 px-5 pt-4">
              {[1, 2, 3].map(s => (
                <div key={s} className={`flex-1 h-1 rounded-full ${step >= s ? 'bg-[var(--color-primary)]' : 'bg-[var(--color-surface-sunken)]'}`} />
              ))}
            </div>
            <div className="px-5 py-5 space-y-4">
              {step === 1 && (
                <>
                  <p className="text-sm font-medium">{L.step1}</p>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(TYPE_L).map(([key, label]) => (
                      <button key={key} onClick={() => setForm(f => ({ ...f, type: key }))}
                        className={`px-3 py-2.5 rounded-[var(--radius-md)] border text-sm font-medium transition-all ${
                          form.type === key ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5 text-[var(--color-primary)]' : 'border-[var(--color-divider)] text-[var(--color-text-secondary)]'
                        }`} data-testid={`booking-type-${key}`}>{label}</button>
                    ))}
                  </div>
                  <button onClick={() => setStep(2)} className="w2g-btn-primary w-full" data-testid="booking-next-1">{L.next}</button>
                </>
              )}
              {step === 2 && (
                <>
                  <p className="text-sm font-medium">{L.step2}</p>
                  <div>
                    <label className="text-xs text-[var(--color-text-secondary)] mb-1 block">{L.dateLabel}</label>
                    <input type="date" min={minDate} value={form.date}
                      onChange={e => handleDateChange(e.target.value)}
                      className="w2g-input w-full" data-testid="booking-date" />
                  </div>
                  {form.date && (
                    loadingSlots ? (
                      <div className="flex justify-center py-4"><Loader2 size={18} className="animate-spin text-[var(--color-text-tertiary)]" /></div>
                    ) : (
                      <div>
                        <label className="text-xs text-[var(--color-text-secondary)] mb-1 block">{L.slotsLabel}</label>
                        <div className="grid grid-cols-4 gap-1.5 max-h-40 overflow-y-auto">
                          {slots.length === 0 ? (
                            <p className="col-span-4 text-xs text-[var(--color-text-tertiary)] py-2">{L.noSlots}</p>
                          ) : slots.map(slot => (
                            <button key={slot} onClick={() => setForm(f => ({ ...f, time: slot }))}
                              className={`px-2 py-1.5 rounded-md border text-xs font-medium transition-all ${
                                form.time === slot ? 'border-[var(--color-primary)] bg-[var(--color-primary)] text-white' : 'border-[var(--color-divider)] text-[var(--color-text-secondary)]'
                              }`} data-testid={`booking-slot-${slot}`}>{slot}</button>
                          ))}
                        </div>
                      </div>
                    )
                  )}
                  <div className="flex gap-2 mt-2">
                    <button onClick={() => setStep(1)} className="w2g-btn-secondary flex-1">{L.back}</button>
                    <button onClick={() => setStep(3)} disabled={!form.date || !form.time}
                      className="w2g-btn-primary flex-1" data-testid="booking-next-2">{L.next}</button>
                  </div>
                </>
              )}
              {step === 3 && (
                <>
                  <p className="text-sm font-medium">{L.step3}</p>
                  <div className="bg-[var(--color-surface-elevated)] rounded-[var(--radius-md)] p-4 space-y-2 text-sm">
                    <div className="flex justify-between"><span className="text-[var(--color-text-secondary)]">{lang === 'de' ? 'Art' : 'Type'}:</span><span className="font-medium">{TYPE_L[form.type]}</span></div>
                    <div className="flex justify-between"><span className="text-[var(--color-text-secondary)]">{L.dateLabel}:</span><span className="font-medium">{form.date}</span></div>
                    <div className="flex justify-between"><span className="text-[var(--color-text-secondary)]">{lang === 'de' ? 'Uhrzeit' : 'Time'}:</span><span className="font-medium">{form.time}</span></div>
                    <div className="flex justify-between"><span className="text-[var(--color-text-secondary)]">{lang === 'de' ? 'Ort' : 'Location'}:</span><span className="font-medium">Online (Zoom)</span></div>
                  </div>
                  <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                    placeholder={L.notes} className="w2g-input w-full resize-none" rows={2} data-testid="booking-notes" />
                  <div className="flex gap-2 mt-2">
                    <button onClick={() => setStep(2)} className="w2g-btn-secondary flex-1">{L.back}</button>
                    <button onClick={submit} disabled={submitting}
                      className="w2g-btn-primary flex-1" data-testid="booking-confirm">
                      {submitting ? <Loader2 size={14} className="animate-spin" /> : L.confirm}
                    </button>
                  </div>
                </>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
