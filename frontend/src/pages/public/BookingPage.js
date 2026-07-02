import React, { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';
import { CalendarDays, Clock, MapPin, CheckCircle, Loader2, Phone, Mail, ArrowRight, ArrowLeft, Shield, Star, Users, Video } from 'lucide-react';
import apiClient from '../../lib/apiClient';

const TYPE_OPTIONS = [
  { key: 'consultation', de: 'Erstberatung', en: 'Initial Consultation', icon: Users, desc_de: 'Individuelle Beratung zu Ihren Moeglichkeiten', desc_en: 'Individual counseling on your options' },
  { key: 'course', de: 'Kursberatung', en: 'Course Consultation', icon: CalendarDays, desc_de: 'Welcher Kurs passt zu Ihrem Profil?', desc_en: 'Which course fits your profile?' },
  { key: 'exam', de: 'Pruefungsberatung', en: 'Exam Consultation', icon: CheckCircle, desc_de: 'Alles zur Feststellungspruefung', desc_en: 'Everything about the assessment exam' },
  { key: 'interview', de: 'Bewerbungsgespraech', en: 'Application Interview', icon: Video, desc_de: 'Persoenliches Gespraech zur Bewerbung', desc_en: 'Personal application interview' },
];

const TRUST_ITEMS_DE = [
  { value: '2.500+', label: 'Erfolgreiche Bewerber' },
  { value: '98%', label: 'Zufriedenheit' },
  { value: '30 Min.', label: 'Kostenlose Beratung' },
  { value: '24h', label: 'Terminbestaetigung' },
];
const TRUST_ITEMS_EN = [
  { value: '2,500+', label: 'Successful Applicants' },
  { value: '98%', label: 'Satisfaction Rate' },
  { value: '30 Min.', label: 'Free Consultation' },
  { value: '24h', label: 'Confirmation Time' },
];

export default function BookingPage() {
  const { i18n } = useTranslation();
  const isEN = i18n.language === 'en';

  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ name: '', email: '', phone: '', type: 'consultation', date: '', time: '', message: '' });
  const [slots, setSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDate = tomorrow.toISOString().slice(0, 10);

  const trustItems = isEN ? TRUST_ITEMS_EN : TRUST_ITEMS_DE;

  const loadSlots = useCallback(async (date) => {
    setLoadingSlots(true);
    try {
      const res = await apiClient.get(`/api/appointments/public-slots?date=${date}`);
      setSlots(res.data.slots || []);
    } catch { setSlots([]); }
    finally { setLoadingSlots(false); }
  }, []);

  const handleDateChange = (date) => {
    setForm(f => ({ ...f, date, time: '' }));
    if (date) loadSlots(date);
  };

  const submit = async () => {
    setError('');
    setSubmitting(true);
    try {
      await apiClient.post('/api/appointments/public-booking', form);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || (isEN ? 'An error occurred. Please try again.' : 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.'));
    } finally { setSubmitting(false); }
  };

  return (
    <div className="min-h-screen bg-white">
      <SEOHead titleKey="seo.booking_title" descKey="seo.booking_desc" path="/booking" />
      <PublicNav />
      <main className="pt-16">
        {/* Premium Hero */}
        <section className="w2g-hero-gradient">
          <div className="relative max-w-[var(--shell-max-width)] mx-auto px-[var(--page-gutter)] py-14 sm:py-20">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur-sm border border-white/20 rounded-full px-4 py-1.5 text-white/90 text-xs font-medium mb-5">
                <CalendarDays size={13} />
                {isEN ? 'Free & non-binding' : 'Kostenlos & unverbindlich'}
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white mb-4 leading-tight tracking-[-0.025em]" style={{ fontFamily: 'var(--font-heading)' }} data-testid="booking-page-title">
                {isEN ? 'Book Your Personal Consultation' : 'Ihre persoenliche Beratung buchen'}
              </h1>
              <p className="text-base sm:text-lg text-white/50 leading-relaxed max-w-xl">
                {isEN
                  ? 'Get expert guidance on your journey to study in Germany. Our team provides personalized advice tailored to your academic goals.'
                  : 'Erhalten Sie eine individuelle Beratung fuer Ihren Weg zum Studium in Deutschland. Unser Team beratet Sie persoenlich zu Ihren akademischen Zielen.'}
              </p>
            </div>
          </div>
        </section>

        {/* Trust Bar */}
        <section className="border-b border-[var(--color-divider-subtle)] bg-[rgba(250,251,252,0.8)]" data-testid="booking-trust-bar">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 sm:grid-cols-4 divide-x divide-[var(--color-divider)]">
              {trustItems.map((item, i) => (
                <div key={i} className="py-4 sm:py-5 px-4 text-center">
                  <p className="text-lg sm:text-xl font-bold text-[var(--color-primary)]">{item.value}</p>
                  <p className="text-[11px] text-[var(--color-text-secondary)] mt-0.5">{item.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Main Content */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

            {/* Left: Booking Form */}
            <div className="lg:col-span-8">
              {success ? (
                <div className="w2g-card text-center py-14" data-testid="booking-success">
                  <div className="w-16 h-16 mx-auto bg-[var(--color-success-bg)] rounded-full flex items-center justify-center mb-5">
                    <CheckCircle size={32} className="text-[var(--color-success)]" />
                  </div>
                  <h2 className="text-xl font-bold text-[var(--color-text-primary)] mb-2">
                    {isEN ? 'Appointment Requested!' : 'Terminanfrage gesendet!'}
                  </h2>
                  <p className="text-sm text-[var(--color-text-secondary)] max-w-md mx-auto mb-6">
                    {isEN
                      ? `Your appointment for ${form.date} at ${form.time} has been requested. We will confirm via email to ${form.email}.`
                      : `Ihre Terminanfrage fuer den ${form.date} um ${form.time} Uhr wurde gesendet. Wir bestaetigen per E-Mail an ${form.email}.`}
                  </p>
                  <a href="/apply" className="w2g-btn-primary inline-flex items-center gap-2" data-testid="booking-to-apply">
                    {isEN ? 'Start Application' : 'Jetzt bewerben'} <ArrowRight size={14} />
                  </a>
                </div>
              ) : (
                <div className="w2g-card p-0 overflow-hidden" data-testid="booking-form">
                  {/* Step Header */}
                  <div className="bg-[var(--color-surface-elevated)] border-b border-[var(--color-divider)] px-6 py-4">
                    <div className="flex items-center gap-3">
                      {[
                        { num: 1, de: 'Terminart & Kontakt', en: 'Type & Contact' },
                        { num: 2, de: 'Datum & Uhrzeit', en: 'Date & Time' },
                        { num: 3, de: 'Bestaetigung', en: 'Confirmation' },
                      ].map((s, i) => (
                        <React.Fragment key={s.num}>
                          <div className="flex items-center gap-2">
                            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold transition-all ${
                              step >= s.num ? 'bg-[var(--color-primary)] text-white shadow-sm' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)]'
                            }`}>{s.num}</div>
                            <span className={`hidden sm:inline text-xs font-medium ${step >= s.num ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-tertiary)]'}`}>
                              {isEN ? s.en : s.de}
                            </span>
                          </div>
                          {i < 2 && <div className={`flex-1 h-0.5 rounded ${step > s.num ? 'bg-[var(--color-primary)]' : 'bg-[var(--color-surface-sunken)]'}`} />}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>

                  <div className="p-6">
                    {error && <div className="mb-5 p-3 rounded-[var(--radius-md)] bg-[var(--color-danger-bg)] text-[var(--color-danger)] text-sm border border-[var(--color-danger-border)]">{error}</div>}

                    {step === 1 && (
                      <div className="space-y-5">
                        <div>
                          <h3 className="text-base font-semibold text-[var(--color-text-primary)] mb-1">{isEN ? 'Choose Appointment Type' : 'Terminart waehlen'}</h3>
                          <p className="text-xs text-[var(--color-text-secondary)] mb-3">{isEN ? 'Select the type of consultation that best fits your needs.' : 'Waehlen Sie die Beratungsart, die am besten zu Ihren Beduerfnissen passt.'}</p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                            {TYPE_OPTIONS.map(opt => {
                              const Icon = opt.icon;
                              return (
                                <button key={opt.key} onClick={() => setForm(f => ({ ...f, type: opt.key }))}
                                  className={`text-left px-4 py-3.5 rounded-[var(--radius-md)] border-2 transition-all ${
                                    form.type === opt.key
                                      ? 'border-[var(--color-primary)] bg-[rgba(10,25,47,0.05)] shadow-sm'
                                      : 'border-[var(--color-divider)] hover:border-[var(--color-divider)] bg-white'
                                  }`} data-testid={`booking-type-${opt.key}`}>
                                  <div className="flex items-center gap-3">
                                    <div className={`w-9 h-9 rounded-[var(--radius-md)] flex items-center justify-center shrink-0 ${form.type === opt.key ? 'bg-[rgba(10,25,47,0.1)] text-[var(--color-primary)]' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)]'}`}>
                                      <Icon size={16} />
                                    </div>
                                    <div>
                                      <p className={`text-sm font-semibold ${form.type === opt.key ? 'text-[var(--color-primary)]' : 'text-[var(--color-text-primary)]'}`}>{isEN ? opt.en : opt.de}</p>
                                      <p className="text-[11px] text-[var(--color-text-tertiary)]">{isEN ? opt.desc_en : opt.desc_de}</p>
                                    </div>
                                  </div>
                                </button>
                              );
                            })}
                          </div>
                        </div>

                        <div className="border-t border-[var(--color-divider-subtle)] pt-5">
                          <h3 className="text-base font-semibold text-[var(--color-text-primary)] mb-3">{isEN ? 'Your Contact Details' : 'Ihre Kontaktdaten'}</h3>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div>
                              <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{isEN ? 'Full Name' : 'Vollstaendiger Name'} *</label>
                              <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                                className="w2g-input w-full" data-testid="booking-name" placeholder={isEN ? 'Your name' : 'Ihr Name'} />
                            </div>
                            <div>
                              <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">E-Mail *</label>
                              <input type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                                className="w2g-input w-full" data-testid="booking-email" placeholder={isEN ? 'Your email' : 'Ihre E-Mail'} />
                            </div>
                          </div>
                          <div className="mt-3">
                            <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{isEN ? 'Phone (optional)' : 'Telefon (optional)'}</label>
                            <input value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
                              className="w2g-input w-full" data-testid="booking-phone" placeholder="+49..." />
                          </div>
                        </div>

                        <button onClick={() => setStep(2)} disabled={!form.name || !form.email}
                          className="w2g-btn-primary w-full flex items-center justify-center gap-2" data-testid="booking-step1-next">
                          {isEN ? 'Next: Choose Date' : 'Weiter: Datum waehlen'} <ArrowRight size={14} />
                        </button>
                      </div>
                    )}

                    {step === 2 && (
                      <div className="space-y-5">
                        <div>
                          <h3 className="text-base font-semibold text-[var(--color-text-primary)] mb-1">{isEN ? 'Choose Date & Time' : 'Datum & Uhrzeit waehlen'}</h3>
                          <p className="text-xs text-[var(--color-text-secondary)] mb-3">{isEN ? 'Select your preferred date, then pick an available time slot.' : 'Waehlen Sie Ihr Wunschdatum und anschliessend eine verfuegbare Uhrzeit.'}</p>
                        </div>
                        <div>
                          <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{isEN ? 'Date' : 'Datum'} *</label>
                          <input type="date" min={minDate} value={form.date}
                            onChange={e => handleDateChange(e.target.value)}
                            className="w2g-input w-full" data-testid="public-booking-date" />
                        </div>
                        {form.date && (
                          loadingSlots ? (
                            <div className="flex justify-center py-8"><Loader2 size={22} className="animate-spin text-[var(--color-text-tertiary)]" /></div>
                          ) : (
                            <div>
                              <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-2 block">{isEN ? 'Available Times' : 'Verfuegbare Zeiten'} *</label>
                              {slots.length === 0 ? (
                                <div className="text-center py-6 bg-[var(--color-surface-elevated)] rounded-[var(--radius-md)] border border-dashed border-[var(--color-divider)]">
                                  <Clock size={20} className="mx-auto text-[var(--color-text-tertiary)] mb-2" />
                                  <p className="text-sm text-[var(--color-text-tertiary)]">{isEN ? 'No slots available on this date.' : 'Keine Termine an diesem Tag verfuegbar.'}</p>
                                </div>
                              ) : (
                                <div className="grid grid-cols-4 sm:grid-cols-6 gap-2">
                                  {slots.map(slot => (
                                    <button key={slot} onClick={() => setForm(f => ({ ...f, time: slot }))}
                                      className={`px-2 py-2.5 rounded-[var(--radius-md)] border-2 text-xs font-semibold transition-all ${
                                        form.time === slot ? 'border-[var(--color-primary)] bg-[var(--color-primary)] text-white shadow-sm' : 'border-[var(--color-divider)] text-[var(--color-text-secondary)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]'
                                      }`} data-testid={`public-slot-${slot}`}>{slot}</button>
                                  ))}
                                </div>
                              )}
                            </div>
                          )
                        )}
                        <div className="flex gap-3 pt-2">
                          <button onClick={() => setStep(1)} className="w2g-btn-secondary flex-1 flex items-center justify-center gap-2">
                            <ArrowLeft size={14} /> {isEN ? 'Back' : 'Zurueck'}
                          </button>
                          <button onClick={() => setStep(3)} disabled={!form.date || !form.time}
                            className="w2g-btn-primary flex-1 flex items-center justify-center gap-2" data-testid="booking-step2-next">
                            {isEN ? 'Next: Confirm' : 'Weiter: Bestaetigen'} <ArrowRight size={14} />
                          </button>
                        </div>
                      </div>
                    )}

                    {step === 3 && (
                      <div className="space-y-5">
                        <div>
                          <h3 className="text-base font-semibold text-[var(--color-text-primary)] mb-1">{isEN ? 'Confirm Your Appointment' : 'Termin bestaetigen'}</h3>
                          <p className="text-xs text-[var(--color-text-secondary)] mb-3">{isEN ? 'Please review your details before submitting.' : 'Bitte pruefen Sie Ihre Angaben vor dem Absenden.'}</p>
                        </div>
                        <div className="bg-gradient-to-br from-[var(--color-surface-elevated)] to-[var(--color-surface-sunken)] rounded-[var(--radius-md)] p-5 border border-[var(--color-divider)] space-y-3">
                          {[
                            { label: isEN ? 'Name' : 'Name', value: form.name },
                            { label: 'E-Mail', value: form.email },
                            { label: isEN ? 'Type' : 'Art', value: TYPE_OPTIONS.find(o => o.key === form.type)?.[isEN ? 'en' : 'de'] },
                            { label: isEN ? 'Date' : 'Datum', value: form.date },
                            { label: isEN ? 'Time' : 'Uhrzeit', value: `${form.time} Uhr` },
                            { label: isEN ? 'Location' : 'Ort', value: 'Online (Zoom)' },
                          ].map(({ label, value }) => (
                            <div key={label} className="flex items-center justify-between py-1.5 border-b border-[rgba(226,232,240,0.6)] last:border-0">
                              <span className="text-xs text-[var(--color-text-secondary)]">{label}</span>
                              <span className="text-sm font-medium text-[var(--color-text-primary)]">{value}</span>
                            </div>
                          ))}
                        </div>
                        <div>
                          <label className="text-xs font-medium text-[var(--color-text-secondary)] mb-1 block">{isEN ? 'Message (optional)' : 'Nachricht (optional)'}</label>
                          <textarea value={form.message} onChange={e => setForm(f => ({ ...f, message: e.target.value }))}
                            className="w2g-input w-full resize-none" rows={2} data-testid="public-booking-message"
                            placeholder={isEN ? 'Your questions or notes...' : 'Ihre Fragen oder Anmerkungen...'} />
                        </div>
                        <div className="flex gap-3">
                          <button onClick={() => setStep(2)} className="w2g-btn-secondary flex-1 flex items-center justify-center gap-2">
                            <ArrowLeft size={14} /> {isEN ? 'Back' : 'Zurueck'}
                          </button>
                          <button onClick={submit} disabled={submitting}
                            className="w2g-btn-primary flex-1 flex items-center justify-center gap-2" data-testid="public-booking-submit">
                            {submitting ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle size={14} />}
                            {isEN ? 'Book Appointment' : 'Termin buchen'}
                          </button>
                        </div>
                        <div className="flex items-center justify-center gap-2 text-[10px] text-[var(--color-text-tertiary)] pt-1">
                          <Shield size={11} />
                          {isEN
                            ? 'Your data is protected. By submitting, you agree to our privacy policy.'
                            : 'Ihre Daten sind geschuetzt. Mit dem Absenden stimmen Sie unserer Datenschutzerklaerung zu.'}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Right: Info Sidebar */}
            <aside className="lg:col-span-4 space-y-4">
              <div className="w2g-card border-2 border-[rgba(10,25,47,0.1)]" data-testid="booking-info-card">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-8 h-8 rounded-[var(--radius-md)] bg-[rgba(10,25,47,0.1)] flex items-center justify-center">
                    <Star size={15} className="text-[var(--color-primary)]" />
                  </div>
                  <h2 className="text-sm font-bold text-[var(--color-text-primary)]">{isEN ? 'How It Works' : 'So funktioniert es'}</h2>
                </div>
                <div className="space-y-4">
                  {[
                    { icon: CalendarDays, text: isEN ? 'Choose your preferred date and time slot' : 'Waehlen Sie Ihr Wunschdatum und Zeitfenster', step: '1' },
                    { icon: Mail, text: isEN ? 'Receive instant confirmation by email' : 'Sofortige Bestaetigung per E-Mail erhalten', step: '2' },
                    { icon: Video, text: isEN ? '30 min free consultation via Zoom' : '30 Min. kostenlose Beratung via Zoom', step: '3' },
                  ].map(({ icon: Icon, text, step: s }) => (
                    <div key={s} className="flex items-start gap-3">
                      <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--color-primary)] text-white text-[10px] font-bold shrink-0">
                        {s}
                      </div>
                      <p className="text-sm text-[var(--color-text-secondary)] leading-snug pt-0.5">{text}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="w2g-card" data-testid="booking-contact-card">
                <h2 className="text-sm font-bold text-[var(--color-text-primary)] mb-3">{isEN ? 'Direct Contact' : 'Direkter Kontakt'}</h2>
                <div className="space-y-2.5">
                  <a href="tel:+4924199032292" className="flex items-center gap-3 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] transition-colors group">
                    <div className="w-8 h-8 rounded-[var(--radius-md)] bg-[var(--color-surface-sunken)] group-hover:bg-[rgba(10,25,47,0.1)] flex items-center justify-center transition-colors">
                      <Phone size={14} className="text-[var(--color-text-tertiary)] group-hover:text-[var(--color-primary)]" />
                    </div>
                    +49 241 990 322 92
                  </a>
                  <a href="mailto:info@stk-aachen.de" className="flex items-center gap-3 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] transition-colors group">
                    <div className="w-8 h-8 rounded-[var(--radius-md)] bg-[var(--color-surface-sunken)] group-hover:bg-[rgba(10,25,47,0.1)] flex items-center justify-center transition-colors">
                      <Mail size={14} className="text-[var(--color-text-tertiary)] group-hover:text-[var(--color-primary)]" />
                    </div>
                    info@stk-aachen.de
                  </a>
                  <a href="https://maps.google.com/?q=Theaterstra%C3%9Fe+30-32,+52062+Aachen" target="_blank" rel="noreferrer" className="flex items-center gap-3 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] transition-colors group">
                    <div className="w-8 h-8 rounded-[var(--radius-md)] bg-[var(--color-surface-sunken)] group-hover:bg-[rgba(10,25,47,0.1)] flex items-center justify-center transition-colors">
                      <MapPin size={14} className="text-[var(--color-text-tertiary)] group-hover:text-[var(--color-primary)]" />
                    </div>
                    Theaterstr. 30-32, 52062 Aachen
                  </a>
                </div>
              </div>

              <div className="w2g-card" data-testid="booking-office-hours">
                <h2 className="text-sm font-bold text-[var(--color-text-primary)] mb-3">{isEN ? 'Office Hours' : 'Sprechzeiten'}</h2>
                <div className="space-y-1.5 text-sm">
                  <div className="flex justify-between"><span className="text-[var(--color-text-secondary)]">{isEN ? 'Mon - Fri' : 'Mo - Fr'}</span><span className="font-medium text-[var(--color-text-primary)]">09:00 - 17:00</span></div>
                  <div className="flex justify-between"><span className="text-[var(--color-text-secondary)]">{isEN ? 'Sat - Sun' : 'Sa - So'}</span><span className="font-medium text-[var(--color-text-tertiary)]">{isEN ? 'Closed' : 'Geschlossen'}</span></div>
                </div>
              </div>
            </aside>
          </div>
        </section>
      </main>
      <PublicFooter />
    </div>
  );
}
