import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { resolveApiUrl } from '../../lib/apiClient';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import SEOHead from '../../components/shared/SEOHead';
import { CheckCircle, Loader2, AlertCircle, Upload, X, FileText, Eye, EyeOff } from 'lucide-react';

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

  const handleDrop = e => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFileChange(docKey, f);
  };

  const sizeOk = !file || file.size <= MAX_FILE_MB * 1024 * 1024;

  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {t(`apply.doc_labels.${docKey}`)} *
        <span className="ml-1 text-xs text-slate-400 font-normal">({t(`apply.doc_descs.${docKey}`)})</span>
      </label>
      {file ? (
        <div className={`flex items-center gap-3 border rounded-sm px-4 py-3 ${sizeOk ? 'border-primary/30 bg-primary/5' : 'border-red-200 bg-red-50'}`}
          data-testid={`file-selected-${docKey}`}>
          <FileText size={18} className={sizeOk ? 'text-primary' : 'text-red-500'} />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-800 truncate">{file.name}</p>
            <p className={`text-xs ${sizeOk ? 'text-slate-500' : 'text-red-600'}`}>
              {sizeOk ? `${(file.size / 1024).toFixed(0)} ${t('apply.file_size_display')}` : t('apply.file_too_large_label')}
            </p>
          </div>
          <button type="button" onClick={() => onClear(docKey)}
            className="text-slate-400 hover:text-red-500 transition-colors shrink-0">
            <X size={16} />
          </button>
        </div>
      ) : (
        <div
          onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-sm px-4 py-5 text-center cursor-pointer transition-all ${
            dragging ? 'border-primary bg-primary/5' : 'border-slate-200 hover:border-primary/60 hover:bg-slate-50'
          }`}
          data-testid={`file-drop-${docKey}`}
        >
          <Upload size={20} className="mx-auto text-slate-400 mb-2" />
          <p className="text-sm text-slate-600">{t('apply.drag_drop')} <span className="text-primary font-medium">{t('apply.browse')}</span></p>
          <p className="text-xs text-slate-400 mt-1">{t('apply.file_types')}</p>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.webp"
            className="hidden"
            onChange={e => e.target.files[0] && onFileChange(docKey, e.target.files[0])}
          />
        </div>
      )}
    </div>
  );
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export default function ApplyPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    country: '',
    course_type: '',
    desired_start: '',
    combo_option: 'none',
    language_level: '',
    degree_country: '',
    notes: '',
    password: '',
    password_confirm: '',
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

    if (!privacyAccepted) {
      setError(t('apply.error_privacy') || 'Bitte akzeptiere die Datenschutzbestimmungen.');
      return;
    }

    if (form.password && form.password.length < 8) {
      setError(t('apply.error_password_short') || 'Passwort muss mindestens 8 Zeichen haben.');
      return;
    }
    if (form.password && form.password !== form.password_confirm) {
      setError(t('apply.error_password_mismatch') || 'Passwörter stimmen nicht überein.');
      return;
    }

    const missingFiles = REQUIRED_DOC_KEYS.filter(k => !files[k]).map(k => t(`apply.doc_labels.${k}`));
    if (missingFiles.length > 0) {
      setError(`${t('apply.error_missing_docs')} ${missingFiles.join(', ')}`);
      return;
    }

    const tooLarge = Object.values(files).filter(Boolean).find(f => f.size > MAX_FILE_MB * 1024 * 1024);
    if (tooLarge) {
      setError(`"${tooLarge.name}" ${t('apply.error_file_too_large')}`);
      return;
    }

    setLoading(true);
    try {
      const documentsPayload = [];
      for (const docKey of REQUIRED_DOC_KEYS) {
        const f = files[docKey];
        if (f) {
          const b64 = await fileToBase64(f);
          documentsPayload.push({
            document_type: docKey,
            filename: f.name,
            content_type: f.type || 'application/octet-stream',
            file_data: b64,
          });
        }
      }

      const payload = {
        full_name: `${form.first_name} ${form.last_name}`.trim(),
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        phone: form.phone,
        date_of_birth: form.date_of_birth,
        country: form.country,
        area_interest: form.course_type === 'Language Course' ? 'language_courses' : 'studienkolleg',
        course_type: form.course_type,
        desired_start: form.desired_start,
        combo_option: form.combo_option !== 'none' ? form.combo_option : null,
        language_level: form.language_level,
        degree_country: form.degree_country,
        notes: form.notes,
        source: 'website_form',
        documents: documentsPayload,
      };

      if (form.password && form.password.length >= 8) {
        payload.password = form.password;
      }

      const res = await axios.post(resolveApiUrl('/api/leads/ingest'), payload, { withCredentials: true });

      if (res.data?.account_created) {
        // Account wurde erstellt, auto-login via Cookie
        await refreshUser();
        navigate('/portal');
      } else {
        setSuccess(true);
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : t('apply.error_generic'));
    } finally {
      setLoading(false);
    }
  };

  const inputCls = 'w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 bg-white';
  const labelCls = 'block text-sm font-medium text-slate-700 mb-1';

  if (success) {
    return (
      <div className="min-h-screen bg-white">
        <SEOHead titleKey="seo.apply_title" descKey="seo.apply_desc" path="/apply" />
        <PublicNav />
        <main className="pt-16">
          <div className="max-w-2xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
            <div className="bg-slate-50 border border-slate-200 rounded-sm p-8 sm:p-10 text-center" data-testid="apply-success">
              <CheckCircle size={48} className="text-primary mx-auto mb-5" />
              <h2 className="text-2xl font-heading font-bold text-slate-800 mb-3">{t('apply.success_title')}</h2>
              <p className="text-slate-600 text-sm mb-2">{t('apply.success_msg1')}</p>
              <p className="text-slate-600 text-sm mb-6">{t('apply.success_msg2')}</p>
              <Link to="/" className="inline-block bg-primary text-white font-semibold px-6 py-3 rounded-sm hover:bg-primary-hover transition-all text-sm">
                {t('apply.back_link')}
              </Link>
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
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
          <div className="text-center mb-8 sm:mb-10">
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-primary mb-3">{t('apply.title')}</h1>
            <p className="text-slate-600">{t('apply.sub')}</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6" data-testid="apply-form">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-sm p-3 flex items-start gap-2 text-red-700 text-sm" data-testid="apply-error">
                <AlertCircle size={16} className="mt-0.5 shrink-0" /> {error}
              </div>
            )}

            {/* Personal Data */}
            <div className="bg-white border border-slate-200 rounded-sm p-5 sm:p-6 space-y-4">
              <h2 className="font-semibold text-slate-800 text-base border-b border-slate-100 pb-3">{t('apply.personal_data')}</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>{t('apply.firstname')} *</label>
                  <input name="first_name" value={form.first_name} onChange={handleChange} required
                    data-testid="apply-input-firstname" className={inputCls} placeholder={t('apply.firstname')} />
                </div>
                <div>
                  <label className={labelCls}>{t('apply.lastname')} *</label>
                  <input name="last_name" value={form.last_name} onChange={handleChange} required
                    data-testid="apply-input-lastname" className={inputCls} placeholder={t('apply.lastname')} />
                </div>
                <div>
                  <label className={labelCls}>{t('apply.email')} *</label>
                  <input name="email" type="email" value={form.email} onChange={handleChange} required
                    data-testid="apply-input-email" className={inputCls} placeholder="deine@email.com" />
                </div>
                <div>
                  <label className={labelCls}>{t('apply.dob')} *</label>
                  <input name="date_of_birth" type="date" value={form.date_of_birth} onChange={handleChange} required
                    data-testid="apply-input-dob" className={inputCls} />
                </div>
                <div>
                  <label className={labelCls}>{t('apply.country')} *</label>
                  <input name="country" value={form.country} onChange={handleChange} required
                    data-testid="apply-input-country" className={inputCls} placeholder={t('apply.country_placeholder')} />
                </div>
                <div>
                  <label className={labelCls}>{t('apply.phone')} *</label>
                  <input name="phone" value={form.phone} onChange={handleChange} required
                    data-testid="apply-input-phone" className={inputCls} placeholder={t('apply.phone_placeholder')} />
                </div>
              </div>
            </div>

            {/* Study Details */}
            <div className="bg-white border border-slate-200 rounded-sm p-5 sm:p-6 space-y-4">
              <h2 className="font-semibold text-slate-800 text-base border-b border-slate-100 pb-3">{t('apply.study_details')}</h2>
              <div>
                <label className={labelCls}>{t('apply.course_type_label')} *</label>
                <select name="course_type" value={form.course_type} onChange={handleChange} required
                  data-testid="apply-select-course" className={inputCls}>
                  <option value="">{t('apply.course_select_placeholder')}</option>
                  {COURSE_VALUES.map((val, i) => <option key={val} value={val}>{t(`apply.courses.${COURSE_KEYS[i]}`)}</option>)}
                </select>
              </div>
              <div>
                <label className={labelCls}>{t('apply.combo_label')}</label>
                <select name="combo_option" value={form.combo_option} onChange={handleChange}
                  data-testid="apply-select-combo" className={inputCls}>
                  {COMBO_VALUES.map((val, i) => <option key={val} value={val}>{t(`apply.combos.${COMBO_KEYS[i]}`)}</option>)}
                </select>
              </div>
              <div>
                <label className={labelCls}>{t('apply.semester_label')} *</label>
                <select name="desired_start" value={form.desired_start} onChange={handleChange} required
                  data-testid="apply-select-semester" className={inputCls}>
                  <option value="">{t('apply.semester_placeholder')}</option>
                  {SEMESTER_VALUES.map((val, i) => <option key={val} value={val}>{t(`apply.semesters.${SEMESTER_KEYS[i]}`)}</option>)}
                </select>
              </div>
              <div>
                <label className={labelCls}>{t('apply.german_level_label')} *</label>
                <select name="language_level" value={form.language_level} onChange={handleChange} required
                  data-testid="apply-select-level" className={inputCls}>
                  <option value="">{t('apply.german_level_placeholder')}</option>
                  {LEVEL_VALUES.map(val => <option key={val} value={val}>{t(`apply.levels.${val}`)}</option>)}
                </select>
              </div>
              <div>
                <label className={labelCls}>{t('apply.degree_country_label')} *</label>
                <input name="degree_country" value={form.degree_country} onChange={handleChange} required
                  data-testid="apply-input-degree-country" className={inputCls}
                  placeholder={t('apply.degree_country_placeholder')} />
              </div>
              <div>
                <label className={labelCls}>{t('apply.notes_label')}</label>
                <textarea name="notes" value={form.notes} onChange={handleChange} rows={3}
                  data-testid="apply-textarea-notes"
                  className={`${inputCls} resize-none`}
                  placeholder={t('apply.notes_placeholder')} />
              </div>
            </div>

            {/* Document Uploads */}
            <div className="bg-white border border-slate-200 rounded-sm p-5 sm:p-6 space-y-5">
              <div>
                <h2 className="font-semibold text-slate-800 text-base border-b border-slate-100 pb-3 mb-1">{t('apply.docs_title')}</h2>
                <p className="text-xs text-slate-500">{t('apply.docs_desc')}</p>
              </div>
              {REQUIRED_DOC_KEYS.map(docKey => (
                <FileDropZone
                  key={docKey}
                  docKey={docKey}
                  file={files[docKey]}
                  onFileChange={handleFileChange}
                  onClear={handleFileClear}
                  t={t}
                />
              ))}
            </div>

            {/* Account-Erstellung */}
            <div className="bg-white border border-slate-200 rounded-sm p-5 sm:p-6 space-y-4">
              <div>
                <h2 className="font-semibold text-slate-800 text-base border-b border-slate-100 pb-3 mb-1">
                  {t('apply.account_title') || 'Portal-Zugang erstellen'}
                </h2>
                <p className="text-xs text-slate-500">
                  {t('apply.account_desc') || 'Erstelle direkt deinen Portalzugang, um den Bewerbungsstatus zu verfolgen, Dokumente nachzureichen und mit dem Team zu kommunizieren.'}
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="relative">
                  <label className={labelCls}>{t('apply.password_label') || 'Passwort'} *</label>
                  <input name="password" type={showPassword ? 'text' : 'password'} value={form.password} onChange={handleChange} required minLength={8}
                    data-testid="apply-input-password" className={inputCls} placeholder="Min. 8 Zeichen" />
                  <button type="button" onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-8 text-slate-400 hover:text-slate-600">
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                <div>
                  <label className={labelCls}>{t('apply.password_confirm_label') || 'Passwort bestätigen'} *</label>
                  <input name="password_confirm" type={showPassword ? 'text' : 'password'} value={form.password_confirm} onChange={handleChange} required minLength={8}
                    data-testid="apply-input-password-confirm" className={inputCls} placeholder="Passwort wiederholen" />
                </div>
              </div>
            </div>

            {/* Privacy Notice + Checkbox */}
            <div className="space-y-3">
              <label className="flex items-start gap-3 cursor-pointer" data-testid="apply-privacy-checkbox">
                <input type="checkbox" checked={privacyAccepted} onChange={e => setPrivacyAccepted(e.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-primary focus:ring-primary" />
                <span className="text-xs text-slate-600">
                  {t('apply.privacy_agree')}{' '}
                  <Link to="/privacy" className="underline text-primary">{t('apply.privacy_link')}</Link>{' '}
                  {t('apply.and')}{' '}
                  <Link to="/agb" className="underline text-primary">{t('apply.agb_link')}</Link>{' '}
                  {t('apply.zu')}
                </span>
              </label>
            </div>

            <button type="submit" disabled={loading} data-testid="apply-submit-btn"
              className="w-full bg-primary text-white font-semibold py-3.5 rounded-sm hover:bg-primary-hover transition-all disabled:opacity-60 flex items-center justify-center gap-2 text-sm">
              {loading && <Loader2 size={18} className="animate-spin" />}
              {loading ? t('apply.submitting') : t('apply.submit_btn')}
            </button>
          </form>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
