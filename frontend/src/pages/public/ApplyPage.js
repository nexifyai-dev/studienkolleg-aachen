import React, { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';
import { CheckCircle, Loader2, AlertCircle, Upload, X, FileText } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const COURSES = [
  { value: 'T-Course', label: 'T-Kurs – Technik (Maschinenbau, Elektrotechnik, Mathematik, Physik)' },
  { value: 'M-Course', label: 'M-Kurs – Medizin (Medizin, Zahnmedizin, Biologie, Pharmazie)' },
  { value: 'W-Course', label: 'W-Kurs – Wirtschaft (BWL, Informatik, Sozialwissenschaften, Jura)' },
  { value: 'M/T-Course', label: 'M/T-Kurs – Kombi Medizin + Technik' },
  { value: 'Language Course', label: 'Sprachkurs (A1–C1 Deutschvorbereitung)' },
];

const COMBO_OPTIONS = [
  { value: 'none', label: 'Keine Kombination' },
  { value: 'T-Course', label: 'Zusätzlich T-Kurs' },
  { value: 'M-Course', label: 'Zusätzlich M-Kurs' },
  { value: 'W-Course', label: 'Zusätzlich W-Kurs' },
];

const SEMESTERS = [
  { value: 'Winter Semester 2025/26', label: 'Wintersemester 2025/26' },
  { value: 'Summer Semester 2026', label: 'Sommersemester 2026' },
  { value: 'Winter Semester 2026/27', label: 'Wintersemester 2026/27' },
  { value: 'Summer Semester 2027', label: 'Sommersemester 2027' },
  { value: 'Winter Semester 2027/28', label: 'Wintersemester 2027/28' },
];

const GERMAN_LEVELS = [
  { value: 'A1', label: 'A1 – Keine oder sehr geringe Kenntnisse' },
  { value: 'A2', label: 'A2 – Grundkenntnisse' },
  { value: 'B1', label: 'B1 – Mittelstufe (für Studienkolleg erforderlich)' },
  { value: 'B2', label: 'B2 – Obermittelstufe' },
  { value: 'C1', label: 'C1 – Fortgeschritten' },
  { value: 'C2', label: 'C2 – Muttersprachliches Niveau' },
];

const REQUIRED_DOCS = [
  {
    key: 'language_certificate',
    label: 'Deutsches Sprachzertifikat *',
    desc: 'Zertifikat über aktuelle Deutschkenntnisse (z. B. Goethe, TELC, DSH, TestDaF)',
    accept: '.pdf,.jpg,.jpeg,.png,.webp',
    required: true,
  },
  {
    key: 'highschool_diploma',
    label: 'Schulzeugnis / Abschlusszeugnis *',
    desc: 'Letztes Zeugnis / Hochschulzugangsberechtigung aus dem Herkunftsland',
    accept: '.pdf,.jpg,.jpeg,.png,.webp',
    required: true,
  },
  {
    key: 'passport',
    label: 'Reisepass *',
    desc: 'Gültiger Reisepass (Personalausweis wird für EU-Bürger akzeptiert)',
    accept: '.pdf,.jpg,.jpeg,.png,.webp',
    required: true,
  },
];

const MAX_FILE_MB = 10;

function FileDropZone({ docConfig, file, onFileChange, onClear }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const handleDrop = e => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFileChange(docConfig.key, f);
  };

  const sizeOk = !file || file.size <= MAX_FILE_MB * 1024 * 1024;

  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {docConfig.label}
        <span className="ml-1 text-xs text-slate-400 font-normal">({docConfig.desc})</span>
      </label>
      {file ? (
        <div className={`flex items-center gap-3 border rounded-sm px-4 py-3 ${sizeOk ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}
          data-testid={`file-selected-${docConfig.key}`}>
          <FileText size={18} className={sizeOk ? 'text-green-600' : 'text-red-500'} />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-800 truncate">{file.name}</p>
            <p className={`text-xs ${sizeOk ? 'text-slate-500' : 'text-red-600'}`}>
              {sizeOk ? `${(file.size / 1024).toFixed(0)} KB` : `Datei zu groß (max. ${MAX_FILE_MB} MB)`}
            </p>
          </div>
          <button type="button" onClick={() => onClear(docConfig.key)}
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
          data-testid={`file-drop-${docConfig.key}`}
        >
          <Upload size={20} className="mx-auto text-slate-400 mb-2" />
          <p className="text-sm text-slate-600">Datei hierher ziehen oder <span className="text-primary font-medium">klicken zum Auswählen</span></p>
          <p className="text-xs text-slate-400 mt-1">PDF, JPG, PNG, WEBP – max. {MAX_FILE_MB} MB</p>
          <input
            ref={inputRef}
            type="file"
            accept={docConfig.accept}
            className="hidden"
            onChange={e => e.target.files[0] && onFileChange(docConfig.key, e.target.files[0])}
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
  });
  const [files, setFiles] = useState({ language_certificate: null, highschool_diploma: null, passport: null });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleChange = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }));
  const handleFileChange = (key, file) => setFiles(p => ({ ...p, [key]: file }));
  const handleFileClear = key => setFiles(p => ({ ...p, [key]: null }));

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');

    // Client-seitige Validierung
    const missingFiles = REQUIRED_DOCS.filter(d => d.required && !files[d.key]).map(d => d.label.replace(' *', ''));
    if (missingFiles.length > 0) {
      setError(`Bitte lade alle Pflichtdokumente hoch: ${missingFiles.join(', ')}`);
      return;
    }

    // Datei-Größe prüfen
    const tooLarge = Object.values(files).filter(Boolean).find(f => f.size > MAX_FILE_MB * 1024 * 1024);
    if (tooLarge) {
      setError(`Datei "${tooLarge.name}" ist zu groß (max. ${MAX_FILE_MB} MB).`);
      return;
    }

    setLoading(true);
    try {
      // Dateien in Base64 konvertieren
      const documentsPayload = [];
      for (const doc of REQUIRED_DOCS) {
        const f = files[doc.key];
        if (f) {
          const b64 = await fileToBase64(f);
          documentsPayload.push({
            document_type: doc.key,
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

      await axios.post(`${API}/api/leads/ingest`, payload);
      setSuccess(true);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Fehler beim Absenden. Bitte versuche es erneut.');
    } finally {
      setLoading(false);
    }
  };

  const inputCls = 'w-full border border-slate-200 rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 bg-white';
  const labelCls = 'block text-sm font-medium text-slate-700 mb-1';

  if (success) {
    return (
      <div className="min-h-screen bg-white">
        <PublicNav />
        <main className="pt-16">
          <div className="max-w-2xl mx-auto px-4 sm:px-6 py-16">
            <div className="bg-green-50 border border-green-200 rounded-sm p-10 text-center" data-testid="apply-success">
              <CheckCircle size={48} className="text-green-500 mx-auto mb-5" />
              <h2 className="text-2xl font-heading font-bold text-green-800 mb-3">Bewerbung eingegangen!</h2>
              <p className="text-green-700 text-sm mb-2">Deine Bewerbung und Dokumente wurden erfolgreich übermittelt.</p>
              <p className="text-green-700 text-sm mb-6">Wir prüfen deine Unterlagen und melden uns innerhalb von 24 Stunden bei dir.</p>
              <Link to="/" className="inline-block bg-primary text-white font-semibold px-6 py-3 rounded-sm hover:bg-primary-hover transition-all text-sm">
                Zurück zur Startseite
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
      <PublicNav />
      <main className="pt-16">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-12">
          <div className="text-center mb-10">
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-primary mb-3">Jetzt bewerben</h1>
            <p className="text-slate-600">Fülle das Formular vollständig aus. Wir melden uns innerhalb von 24 Stunden.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6" data-testid="apply-form">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-sm p-3 flex items-start gap-2 text-red-700 text-sm" data-testid="apply-error">
                <AlertCircle size={16} className="mt-0.5 shrink-0" /> {error}
              </div>
            )}

            {/* Persönliche Daten */}
            <div className="bg-white border border-slate-200 rounded-sm p-5 sm:p-6 space-y-4">
              <h2 className="font-semibold text-slate-800 text-base border-b border-slate-100 pb-3">Persönliche Daten</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>Vorname *</label>
                  <input name="first_name" value={form.first_name} onChange={handleChange} required
                    data-testid="apply-input-firstname" className={inputCls} placeholder="Dein Vorname" />
                </div>
                <div>
                  <label className={labelCls}>Nachname *</label>
                  <input name="last_name" value={form.last_name} onChange={handleChange} required
                    data-testid="apply-input-lastname" className={inputCls} placeholder="Dein Nachname" />
                </div>
                <div>
                  <label className={labelCls}>E-Mail-Adresse *</label>
                  <input name="email" type="email" value={form.email} onChange={handleChange} required
                    data-testid="apply-input-email" className={inputCls} placeholder="deine@email.com" />
                </div>
                <div>
                  <label className={labelCls}>Geburtsdatum *</label>
                  <input name="date_of_birth" type="date" value={form.date_of_birth} onChange={handleChange} required
                    data-testid="apply-input-dob" className={inputCls} />
                </div>
                <div>
                  <label className={labelCls}>Herkunftsland *</label>
                  <input name="country" value={form.country} onChange={handleChange} required
                    data-testid="apply-input-country" className={inputCls} placeholder="z. B. Indien, Ägypten…" />
                </div>
                <div>
                  <label className={labelCls}>Telefon / WhatsApp *</label>
                  <input name="phone" value={form.phone} onChange={handleChange} required
                    data-testid="apply-input-phone" className={inputCls} placeholder="+49 …" />
                </div>
              </div>
            </div>

            {/* Kurs-/Bewerbungsdetails */}
            <div className="bg-white border border-slate-200 rounded-sm p-5 sm:p-6 space-y-4">
              <h2 className="font-semibold text-slate-800 text-base border-b border-slate-100 pb-3">Studiendetails</h2>
              <div>
                <label className={labelCls}>Gewünschter Kurs *</label>
                <select name="course_type" value={form.course_type} onChange={handleChange} required
                  data-testid="apply-select-course" className={inputCls}>
                  <option value="">-- Kurs auswählen --</option>
                  {COURSES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
              <div>
                <label className={labelCls}>Kombination mit weiterem Kurs möglich?</label>
                <select name="combo_option" value={form.combo_option} onChange={handleChange}
                  data-testid="apply-select-combo" className={inputCls}>
                  {COMBO_OPTIONS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
              <div>
                <label className={labelCls}>Gewünschtes Startsemester *</label>
                <select name="desired_start" value={form.desired_start} onChange={handleChange} required
                  data-testid="apply-select-semester" className={inputCls}>
                  <option value="">-- Semester auswählen --</option>
                  {SEMESTERS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
              </div>
              <div>
                <label className={labelCls}>Aktuelles Deutschniveau *</label>
                <select name="language_level" value={form.language_level} onChange={handleChange} required
                  data-testid="apply-select-level" className={inputCls}>
                  <option value="">-- Niveau auswählen --</option>
                  {GERMAN_LEVELS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
                </select>
              </div>
              <div>
                <label className={labelCls}>In welchem Land hast du deinen letzten Schulabschluss gemacht? *</label>
                <input name="degree_country" value={form.degree_country} onChange={handleChange} required
                  data-testid="apply-input-degree-country" className={inputCls}
                  placeholder="z. B. Indien, Ägypten, China…" />
              </div>
              <div>
                <label className={labelCls}>Nachricht / Anmerkungen</label>
                <textarea name="notes" value={form.notes} onChange={handleChange} rows={3}
                  data-testid="apply-textarea-notes"
                  className={`${inputCls} resize-none`}
                  placeholder="Weitere Informationen, Fragen oder besondere Umstände…" />
              </div>
            </div>

            {/* Pflicht-Uploads */}
            <div className="bg-white border border-slate-200 rounded-sm p-5 sm:p-6 space-y-5">
              <div>
                <h2 className="font-semibold text-slate-800 text-base border-b border-slate-100 pb-3 mb-1">Pflichtdokumente hochladen</h2>
                <p className="text-xs text-slate-500">Alle drei Dokumente sind für die Bearbeitung deiner Bewerbung erforderlich. Erlaubte Formate: PDF, JPG, PNG, WEBP (max. 10 MB je Datei).</p>
              </div>
              {REQUIRED_DOCS.map(doc => (
                <FileDropZone
                  key={doc.key}
                  docConfig={doc}
                  file={files[doc.key]}
                  onFileChange={handleFileChange}
                  onClear={handleFileClear}
                />
              ))}
            </div>

            {/* Datenschutz */}
            <p className="text-xs text-slate-500 text-center">
              Mit dem Absenden stimmst du unserer{' '}
              <Link to="/privacy" className="underline text-primary">Datenschutzerklärung</Link>{' '}
              und den{' '}
              <Link to="/agb" className="underline text-primary">AGB</Link>{' '}
              zu.
            </p>

            <button type="submit" disabled={loading} data-testid="apply-submit-btn"
              className="w-full bg-primary text-white font-semibold py-3.5 rounded-sm hover:bg-primary-hover transition-all disabled:opacity-60 flex items-center justify-center gap-2 text-sm">
              {loading && <Loader2 size={18} className="animate-spin" />}
              {loading ? 'Wird übermittelt…' : 'Bewerbung mit Dokumenten absenden'}
            </button>
          </form>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
