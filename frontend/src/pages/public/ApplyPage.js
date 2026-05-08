import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';
import { CheckCircle, Loader2, AlertCircle, Upload, X, FileText, Eye, EyeOff, HelpCircle, Shield, Clock } from 'lucide-react';

const COURSE_VALUES = ['T-Course', 'M-Course', 'W-Course', 'M/T-Course', 'Language Course'];
const COURSE_KEYS = ['t', 'm', 'w', 'mt', 'lang'];
const COMBO_VALUES = ['none', 'T-Course', 'M-Course', 'W-Course'];
const COMBO_KEYS = ['none', 't', 'm', 'w'];
const SEMESTER_VALUES = ['Winter Semester 2025/26', 'Summer Semester 2026', 'Winter Semester 2026/27', 'Summer Semester 2027', 'Winter Semester 2027/28'];
const SEMESTER_KEYS = ['ws2526', 'ss26', 'ws2627', 'ss27', 'ws2728'];
const LEVEL_VALUES = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
const REQUIRED_DOC_KEYS = ['language_certificate', 'highschool_diploma', 'passport'];
const MAX_FILE_MB = 10;

function FileDropZone({ docKey, file, onFileChange, onClear, t }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const handleDrop = e => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) onFileChange(docKey, f); };
  const sizeOk = !file || file.size <= MAX_FILE_MB * 1024 * 1024;

  return (
    <div>
      <label className="w2g-label">
        {t(`apply.doc_labels.${docKey}`)} *
        <span className="ml-1 text-xs text-[var(--color-text-tertiary)] font-normal">({t(`apply.doc_descs.${docKey}`)})</span>
      </label>
      {file ? (
        <div className={`flex items-center gap-3 border rounded-[var(--radius-sm)] px-4 py-3 ${sizeOk ? 'border-[var(--color-primary)]/30 bg-[var(--color-primary)]/5' : 'border-[var(--color-danger-border)] bg-[var(--color-danger-bg)]'}`}
          data-testid={`file-selected-${docKey}`}>
          <FileText size={18} className={sizeOk ? 'text-[var(--color-primary)]' : 'text-[var(--color-danger)]'} />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-[var(--color-text-primary)] truncate">{file.name}</p>
            <p className={`text-xs ${sizeOk ? 'text-[var(--color-text-secondary)]' : 'text-[var(--color-danger)]'}`}>
              {sizeOk ? `${(file.size / 1024).toFixed(0)} ${t('apply.file_size_display')}` : t('apply.file_too_large_label')}
            </p>
          </div>
          <button type="button" onClick={() => onClear(docKey)} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)] transition-colors shrink-0"><X size={16} /></button>
        </div>
      ) : (
        <div onDragOver={e => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)}
          onDrop={handleDrop} onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-[var(--radius-sm)] px-4 py-5 text-center cursor-pointer transition-all ${
            dragging ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5' : 'border-[var(--color-divider)] hover:border-[var(--color-primary)]/60 hover:bg-[var(--color-surface-elevated)]'
          }`} data-testid={`file-drop-${docKey}`}>
          <Upload size={20} className="mx-auto text-[var(--color-text-tertiary)] mb-2" />
          <p className="text-sm text-[var(--color-text-secondary)]">{t('apply.drag_drop')} <span className="text-[var(--color-primary)] font-medium">{t('apply.browse')}</span></p>
          <p className="text-xs text-[var(--color-text-tertiary)] mt-1">{t('apply.file_types')}</p>
          <input ref={inputRef} type="file" accept=".pdf,.jpg,.jpeg,.png,.webp" className="hidden"
            onChange={e => e.target.files[0] && onFileChange(docKey, e.target.files[0])} />
        </div>
      )}
    </div>
  );
}


export default function ApplyPage() {
  const { t, i18n } = useTranslation();
  const isDE = i18n.language !== 'en';
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '', phone: '', date_of_birth: '', country: '',
    course_type: '', desired_start: '', combo_option: 'none', language_level: '',
    degree_country: '', notes: '', password: '', password_confirm: '',
  });
  const [files, setFiles] = useState({ language_certificate: null, highschool_diploma: null, passport: null });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);

  const handleChange = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }));
  const handleFileChange = (key, file) => setFiles(p => ({ ...p, [key]: file }));
  const handleFileClear = key => setFiles(p => ({ ...p, [key]: null }));

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    if (!privacyAccepted) { setError(t('apply.error_privacy') || 'Bitte akzeptiere die Datenschutzbestimmungen.'); return; }
    if (form.password && form.password.length < 8) { setError(t('apply.error_password_short') || 'Passwort muss mindestens 8 Zeichen haben.'); return; }
    if (form.password && form.password !== form.password_confirm) { setError(t('apply.error_password_mismatch') || 'Passwoerter stimmen nicht ueberein.'); return; }
    const missingFiles = REQUIRED_DOC_KEYS.filter(k => !files[k]).map(k => t(`apply.doc_labels.${k}`));
    if (missingFiles.length > 0) { setError(`${t('apply.error_missing_docs')} ${missingFiles.join(', ')}`); return; }
    const tooLarge = Object.values(files).filter(Boolean).find(f => f.size > MAX_FILE_MB * 1024 * 1024);
    if (tooLarge) { setError(`"${tooLarge.name}" ${t('apply.error_file_too_large')}`); return; }

    setLoading(true);
    try {
      // Phase 1: Dokumente einzeln vorab hochladen (Multipart)
      const documentsPayload = [];
      for (const docKey of REQUIRED_DOC_KEYS) {
        const f = files[docKey];
        if (f) {
          const formData = new FormData();
          formData.append('file', f);
          formData.append('document_type', docKey);
          try {
            const uploadRes = await apiClient.post(`/api/leads/upload-temp`, formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
              timeout: 120000,
            });
            documentsPayload.push({
              document_type: docKey,
              filename: f.name,
              content_type: f.type || 'application/octet-stream',
              upload_token: uploadRes.data.upload_token,
            });
          } catch (uploadErr) {
            const msg = uploadErr.response?.data?.detail || `Upload fehlgeschlagen: ${f.name}`;
            setError(msg);
            setLoading(false);
            return;
          }
        }
      }

      // Phase 2: Leichter Form-Payload (nur Text + Tokens, kein Base64)
      const payload = {
        full_name: `${form.first_name} ${form.last_name}`.trim(),
        first_name: form.first_name, last_name: form.last_name, email: form.email,
        phone: form.phone, date_of_birth: form.date_of_birth, country: form.country,
        area_interest: form.course_type === 'Language Course' ? 'language_courses' : 'studienkolleg',
        course_type: form.course_type, desired_start: form.desired_start,
        combo_option: form.combo_option !== 'none' ? form.combo_option : null,
        language_level: form.language_level, degree_country: form.degree_country,
        notes: form.notes, source: 'website_form', documents: documentsPayload,
        language_pref: i18n.language === 'en' ? 'en' : 'de',
      };
      if (form.password && form.password.length >= 8) payload.password = form.password;
      const res = await apiClient.post(`/api/leads/ingest`, payload, { withCredentials: true });
      if (res.data?.account_created) { await refreshUser(); navigate('/portal'); }
      else { setSuccess(true); }
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (err.response?.status === 413 || err.message?.includes('payload')) {
        setError(isDE ? 'Die hochgeladenen Dateien sind zu gross. Bitte reduziere die Dateigroesse und versuche es erneut.' : 'The uploaded files are too large. Please reduce the file size and try again.');
      } else if (!err.response) {
        setError(isDE ? 'Verbindungsfehler. Bitte pruefe deine Internetverbindung und versuche es erneut.' : 'Connection error. Please check your internet connection and try again.');
      } else {
        setError(t('apply.error_generic'));
      }
    } finally { setLoading(false); }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-white">
        <SEOHead titleKey="seo.apply_title" descKey="seo.apply_desc" path="/apply" />
        <PublicNav />
        <main className="pt-16">
          <div className="w2g-section-narrow py-10 sm:py-16">
            <div className="w2g-card p-8 sm:p-10 text-center max-w-2xl mx-auto" data-testid="apply-success">
              <div className="w-16 h-16 bg-[var(--color-primary)]/10 rounded-full flex items-center justify-center mx-auto mb-5">
                <CheckCircle size={32} className="text-[var(--color-primary)]" />
              </div>
              <h2 className="w2g-heading-md mb-3">{t('apply.success_title')}</h2>
              <p className="text-[var(--color-text-secondary)] text-sm mb-2">{t('apply.success_msg1')}</p>
              <p className="text-[var(--color-text-secondary)] text-sm mb-6">{t('apply.success_msg2')}</p>
              <Link to="/" className="w2g-btn-primary px-6 py-3 text-sm">{t('apply.back_link')}</Link>
            </div>
          </div>
        </main>
        <PublicFooter />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <SEOHead titleKey="seo.apply_title" descKey="seo.apply_desc" path="/apply" />
      <PublicNav />
      <main className="pt-16">
        {/* Hero Header */}
        <section className="relative overflow-hidden py-10 sm:py-14">
          <div className="absolute inset-0" style={{ background: 'linear-gradient(155deg, var(--color-primary-dark) 0%, var(--color-primary) 50%, var(--color-primary-light) 100%)' }} />
          <div className="absolute top-[-20%] right-[10%] w-[400px] h-[400px] rounded-full opacity-[0.04]" style={{ background: 'white' }} />
          <div className="w2g-section-narrow text-center relative z-10">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white mb-3 tracking-[-0.025em]" style={{ fontFamily: 'var(--font-heading)' }}>{t('apply.title')}</h1>
            <p className="text-white/50 max-w-xl mx-auto text-sm sm:text-base">{t('apply.sub')}</p>
          </div>
        </section>

        {/* Guidance Bar */}
        <div className="border-b border-[var(--color-divider-subtle)] bg-[var(--color-surface-elevated)]/80">
          <div className="w2g-section-narrow py-4">
            <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-[var(--color-text-secondary)]">
              <span className="flex items-center gap-1.5"><Clock size={13} className="text-[var(--color-primary)]" />{isDE ? 'ca. 10 Min. Bearbeitungszeit' : 'approx. 10 min. completion time'}</span>
              <span className="flex items-center gap-1.5"><Shield size={13} className="text-[var(--color-primary)]" />{isDE ? 'DSGVO-konform & verschluesselt' : 'GDPR compliant & encrypted'}</span>
              <span className="flex items-center gap-1.5"><HelpCircle size={13} className="text-[var(--color-primary)]" />{isDE ? 'Support via WhatsApp' : 'Support via WhatsApp'}</span>
            </div>
          </div>
        </div>

        <div className="w2g-section-narrow py-8 sm:py-12 max-w-2xl">
          <form onSubmit={handleSubmit} className="space-y-6" data-testid="apply-form">
            {error && (
              <div className="bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)] rounded-[var(--radius-sm)] p-3 flex items-start gap-2 text-[var(--color-danger)] text-sm" data-testid="apply-error">
                <AlertCircle size={16} className="mt-0.5 shrink-0" /> {error}
              </div>
            )}

            {/* Personal Data */}
            <div className="w2g-card space-y-4">
              <h2 className="font-bold text-[var(--color-primary)] text-base border-b border-[var(--color-divider-subtle)] pb-3">{t('apply.personal_data')}</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div><label className="w2g-label">{t('apply.firstname')} *</label><input name="first_name" value={form.first_name} onChange={handleChange} required data-testid="apply-input-firstname" className="w2g-input" placeholder={t('apply.firstname')} /></div>
                <div><label className="w2g-label">{t('apply.lastname')} *</label><input name="last_name" value={form.last_name} onChange={handleChange} required data-testid="apply-input-lastname" className="w2g-input" placeholder={t('apply.lastname')} /></div>
                <div><label className="w2g-label">{t('apply.email')} *</label><input name="email" type="email" value={form.email} onChange={handleChange} required data-testid="apply-input-email" className="w2g-input" placeholder="deine@email.com" /></div>
                <div><label className="w2g-label">{t('apply.dob')} *</label><input name="date_of_birth" type="date" value={form.date_of_birth} onChange={handleChange} required data-testid="apply-input-dob" className="w2g-input" /></div>
                <div><label className="w2g-label">{t('apply.country')} *</label><input name="country" value={form.country} onChange={handleChange} required data-testid="apply-input-country" className="w2g-input" placeholder={t('apply.country_placeholder')} /></div>
                <div><label className="w2g-label">{t('apply.phone')} *</label><input name="phone" value={form.phone} onChange={handleChange} required data-testid="apply-input-phone" className="w2g-input" placeholder={t('apply.phone_placeholder')} /></div>
              </div>
            </div>

            {/* Study Details */}
            <div className="w2g-card space-y-4">
              <h2 className="font-bold text-[var(--color-primary)] text-base border-b border-[var(--color-divider-subtle)] pb-3">{t('apply.study_details')}</h2>
              <div><label className="w2g-label">{t('apply.course_type_label')} *</label><select name="course_type" value={form.course_type} onChange={handleChange} required data-testid="apply-select-course" className="w2g-select"><option value="">{t('apply.course_select_placeholder')}</option>{COURSE_VALUES.map((val, i) => <option key={val} value={val}>{t(`apply.courses.${COURSE_KEYS[i]}`)}</option>)}</select></div>
              <div><label className="w2g-label">{t('apply.combo_label')}</label><select name="combo_option" value={form.combo_option} onChange={handleChange} data-testid="apply-select-combo" className="w2g-select">{COMBO_VALUES.map((val, i) => <option key={val} value={val}>{t(`apply.combos.${COMBO_KEYS[i]}`)}</option>)}</select></div>
              <div><label className="w2g-label">{t('apply.semester_label')} *</label><select name="desired_start" value={form.desired_start} onChange={handleChange} required data-testid="apply-select-semester" className="w2g-select"><option value="">{t('apply.semester_placeholder')}</option>{SEMESTER_VALUES.map((val, i) => <option key={val} value={val}>{t(`apply.semesters.${SEMESTER_KEYS[i]}`)}</option>)}</select></div>
              <div><label className="w2g-label">{t('apply.german_level_label')} *</label><select name="language_level" value={form.language_level} onChange={handleChange} required data-testid="apply-select-level" className="w2g-select"><option value="">{t('apply.german_level_placeholder')}</option>{LEVEL_VALUES.map(val => <option key={val} value={val}>{t(`apply.levels.${val}`)}</option>)}</select></div>
              <div><label className="w2g-label">{t('apply.degree_country_label')} *</label><input name="degree_country" value={form.degree_country} onChange={handleChange} required data-testid="apply-input-degree-country" className="w2g-input" placeholder={t('apply.degree_country_placeholder')} /></div>
              <div><label className="w2g-label">{t('apply.notes_label')}</label><textarea name="notes" value={form.notes} onChange={handleChange} rows={3} data-testid="apply-textarea-notes" className="w2g-input resize-none" placeholder={t('apply.notes_placeholder')} /></div>
            </div>

            {/* Documents */}
            <div className="w2g-card space-y-5">
              <div>
                <h2 className="font-bold text-[var(--color-primary)] text-base border-b border-[var(--color-divider-subtle)] pb-3 mb-1">{t('apply.docs_title')}</h2>
                <p className="text-xs text-[var(--color-text-secondary)]">{t('apply.docs_desc')}</p>
              </div>
              {REQUIRED_DOC_KEYS.map(docKey => (
                <FileDropZone key={docKey} docKey={docKey} file={files[docKey]} onFileChange={handleFileChange} onClear={handleFileClear} t={t} />
              ))}
            </div>

            {/* Portal-Zugang */}
            <div className="w2g-card space-y-4">
              <div>
                <h2 className="font-bold text-[var(--color-primary)] text-base border-b border-[var(--color-divider-subtle)] pb-3 mb-1">
                  {t('apply.account_title') || 'Portal-Zugang erstellen'}
                </h2>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  {t('apply.account_desc') || 'Erstelle direkt deinen Portalzugang, um den Bewerbungsstatus zu verfolgen, Dokumente nachzureichen und mit dem Team zu kommunizieren.'}
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="relative">
                  <label className="w2g-label">{t('apply.password_label') || 'Passwort'} *</label>
                  <input name="password" type={showPassword ? 'text' : 'password'} value={form.password} onChange={handleChange} required minLength={8}
                    data-testid="apply-input-password" className="w2g-input" placeholder="Min. 8 Zeichen" />
                  <button type="button" onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-8 text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]">
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                <div>
                  <label className="w2g-label">{t('apply.password_confirm_label') || 'Passwort bestaetigen'} *</label>
                  <input name="password_confirm" type={showPassword ? 'text' : 'password'} value={form.password_confirm} onChange={handleChange} required minLength={8}
                    data-testid="apply-input-password-confirm" className="w2g-input" placeholder="Passwort wiederholen" />
                </div>
              </div>
            </div>

            {/* Privacy */}
            <div className="space-y-3">
              <label className="flex items-start gap-3 cursor-pointer" data-testid="apply-privacy-checkbox">
                <input type="checkbox" checked={privacyAccepted} onChange={e => setPrivacyAccepted(e.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-[var(--color-divider)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]" />
                <span className="text-xs text-[var(--color-text-secondary)]">
                  {t('apply.privacy_agree')}{' '}
                  <Link to="/privacy" className="underline text-[var(--color-primary)]">{t('apply.privacy_link')}</Link>{' '}
                  {t('apply.and')}{' '}
                  <Link to="/agb" className="underline text-[var(--color-primary)]">{t('apply.agb_link')}</Link>{' '}
                  {t('apply.zu')}
                </span>
              </label>
            </div>

            <button type="submit" disabled={loading} data-testid="apply-submit-btn"
              className="w2g-btn-primary w-full py-3.5 text-sm font-semibold">
              {loading && <Loader2 size={18} className="animate-spin" />}
              {loading ? t('apply.submitting') : t('apply.submit_btn')}
            </button>

            {/* Bereits registriert? */}
            <p className="text-center text-sm text-[var(--color-text-secondary)]">
              {isDE ? 'Bereits registriert?' : 'Already registered?'}{' '}
              <Link to="/auth/login" className="text-[var(--color-primary)] font-semibold hover:underline">
                {isDE ? 'Zum Login' : 'Go to Login'}
              </Link>
            </p>
          </form>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
