import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../../lib/apiClient';
import { STAGE_LABELS, STAGE_COLORS, formatDate } from '../../lib/utils';
import {
  ArrowLeft, Brain, RefreshCw, CheckCircle, AlertCircle,
  FileText, Clock, XCircle, ChevronDown, ChevronUp, Loader2,
  Phone, Mail, MessageCircle, Building2
} from 'lucide-react';

const DOC_STATUS = {
  uploaded: { label: 'Hochgeladen', icon: Clock, color: 'bg-blue-100 text-blue-700' },
  in_review: { label: 'In Prüfung', icon: Clock, color: 'bg-yellow-100 text-yellow-700' },
  approved: { label: 'Akzeptiert', icon: CheckCircle, color: 'bg-green-100 text-green-700' },
  rejected: { label: 'Abgelehnt', icon: XCircle, color: 'bg-red-100 text-red-700' },
};

const ANABIN_COLORS = {
  'H+': 'bg-green-100 text-green-700',
  'H': 'bg-blue-100 text-blue-700',
  'D': 'bg-red-100 text-red-700',
  'prüfen': 'bg-amber-100 text-amber-700',
  'unbekannt': 'bg-slate-100 text-slate-600',
};

function AIScreeningPanel({ appId }) {
  const [screenings, setScreenings] = useState([]);
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  const load = useCallback(async () => {
    try {
      const res = await apiClient.get(`/api/applications/${appId}/ai-screenings`, { withCredentials: true });
      setScreenings(res.data || []);
    } catch {}
    finally { setLoading(false); }
  }, [appId]);

  useEffect(() => { load(); }, [load]);

  const runScreening = async () => {
    setRunning(true);
    try {
      await apiClient.post(`/api/applications/${appId}/ai-screen`, {}, { withCredentials: true });
      await load();
    } catch (e) {
      console.error('AI screening error', e);
    } finally {
      setRunning(false);
    }
  };

  const latest = screenings[0];

  return (
    <div className="bg-white border border-slate-200 rounded-sm p-5 space-y-4" data-testid="ai-screening-panel">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain size={18} className="text-primary" />
          <h3 className="font-semibold text-slate-700 text-sm">KI-Bewerberprüfung</h3>
          <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">AI Suggestion</span>
        </div>
        <button onClick={runScreening} disabled={running}
          data-testid="ai-screening-run-btn"
          className="flex items-center gap-1.5 text-xs font-medium text-primary border border-primary/30 px-3 py-1.5 rounded-sm hover:bg-primary/5 disabled:opacity-60 transition-all">
          {running ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          {running ? 'Prüfung läuft…' : 'Neue KI-Prüfung starten'}
        </button>
      </div>

      {/* Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-sm px-3 py-2 flex items-start gap-2">
        <AlertCircle size={13} className="text-amber-600 mt-0.5 shrink-0" />
        <p className="text-amber-700 text-xs">
          <strong>KI-Einschätzung – keine bindende Entscheidung.</strong> Alle Vorschläge müssen vom Staff-Team überprüft und bestätigt werden.
        </p>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-6">
          <Loader2 size={20} className="animate-spin text-slate-400" />
        </div>
      )}

      {!loading && screenings.length === 0 && (
        <div className="text-center py-6" data-testid="ai-screening-empty">
          <Brain size={28} className="text-slate-300 mx-auto mb-2" />
          <p className="text-slate-500 text-sm">Noch keine KI-Prüfung durchgeführt.</p>
          <p className="text-slate-400 text-xs mt-1">Klicke auf „Neue KI-Prüfung starten" um zu beginnen.</p>
        </div>
      )}

      {latest && (
        <div className="space-y-3" data-testid="ai-screening-latest">
          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-2">
            <div className={`rounded-sm p-3 text-center ${latest.is_complete ? 'bg-green-50 border border-green-200' : 'bg-amber-50 border border-amber-200'}`}>
              {latest.is_complete
                ? <CheckCircle size={16} className="text-green-500 mx-auto mb-1" />
                : <AlertCircle size={16} className="text-amber-500 mx-auto mb-1" />}
              <p className="text-xs font-medium text-slate-700">Vollständigkeit</p>
              <p className={`text-xs ${latest.is_complete ? 'text-green-700' : 'text-amber-700'}`}>
                {latest.is_complete ? 'Vollständig' : `${latest.missing_documents?.length || 0} fehlend`}
              </p>
            </div>
            <div className={`rounded-sm p-3 text-center border ${ANABIN_COLORS[latest.anabin_category] || 'bg-slate-50 border-slate-200'}`}>
              <p className="text-xs font-medium text-slate-700 mb-0.5">Anabin</p>
              <p className="text-sm font-bold">{latest.anabin_category || '–'}</p>
            </div>
            <div className={`rounded-sm p-3 text-center border ${latest.language_level_ok ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
              {latest.language_level_ok
                ? <CheckCircle size={16} className="text-green-500 mx-auto mb-1" />
                : <XCircle size={16} className="text-red-500 mx-auto mb-1" />}
              <p className="text-xs font-medium text-slate-700">Sprachniveau</p>
              <p className={`text-xs ${latest.language_level_ok ? 'text-green-700' : 'text-red-700'}`}>
                {latest.language_level_ok ? 'Ausreichend' : 'Nicht ausreichend'}
              </p>
            </div>
          </div>

          {/* Fehlende Dokumente */}
          {latest.missing_documents?.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-sm px-4 py-3">
              <p className="text-xs font-semibold text-red-700 mb-1">Fehlende Pflichtdokumente:</p>
              <ul className="space-y-1">
                {latest.missing_documents.map(d => (
                  <li key={d} className="text-xs text-red-600 flex items-center gap-1.5">
                    <XCircle size={12} /> {d}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Statusvorschlag */}
          <div className="flex items-center gap-2 bg-primary/5 border border-primary/20 rounded-sm px-4 py-3">
            <Brain size={14} className="text-primary shrink-0" />
            <div>
              <p className="text-xs text-slate-500">KI-Statusvorschlag</p>
              <p className="text-sm font-semibold text-primary">
                {STAGE_LABELS[latest.suggested_stage] || latest.suggested_stage}
              </p>
            </div>
          </div>

          {/* AI Report (ausklappbar) */}
          {latest.ai_report && (
            <div>
              <button
                onClick={() => setExpanded(expanded === 'report' ? null : 'report')}
                className="w-full flex items-center justify-between text-xs font-medium text-slate-600 hover:text-primary py-2 border-t border-slate-100"
                data-testid="ai-report-toggle"
              >
                <span>Vollständiger KI-Prüfungsbericht</span>
                {expanded === 'report' ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
              {expanded === 'report' && (
                <div className="bg-slate-50 rounded-sm border border-slate-200 p-4 mt-1" data-testid="ai-report-content">
                  <pre className="text-xs text-slate-700 whitespace-pre-wrap font-sans leading-relaxed">
                    {latest.ai_report}
                  </pre>
                </div>
              )}
            </div>
          )}

          {latest.ai_error && (
            <div className="bg-red-50 border border-red-200 rounded-sm px-3 py-2 text-xs text-red-600">
              KI-Fehler: {latest.ai_error}
            </div>
          )}

          <p className="text-xs text-slate-400 text-right">
            Geprüft: {latest.screened_at ? new Date(latest.screened_at).toLocaleString('de-DE') : '–'}
          </p>
        </div>
      )}

      {/* Verlauf */}
      {screenings.length > 1 && (
        <div>
          <button
            onClick={() => setExpanded(expanded === 'history' ? null : 'history')}
            className="w-full flex items-center justify-between text-xs font-medium text-slate-500 hover:text-primary py-2 border-t border-slate-100"
          >
            <span>Prüfungsverlauf ({screenings.length} Prüfungen)</span>
            {expanded === 'history' ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          {expanded === 'history' && (
            <div className="space-y-2 mt-2">
              {screenings.slice(1).map((s, i) => (
                <div key={s.screening_id || i} className="text-xs bg-slate-50 rounded-sm border border-slate-100 px-3 py-2 flex justify-between items-center">
                  <span className="text-slate-600">
                    Vollständig: {s.is_complete ? 'Ja' : 'Nein'} · Anabin: {s.anabin_category}
                  </span>
                  <span className="text-slate-400">{s.screened_at ? new Date(s.screened_at).toLocaleDateString('de-DE') : '–'}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ApplicantDetailPage() {
  const { id } = useParams();
  const [app, setApp] = useState(null);
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stageUpdating, setStageUpdating] = useState(false);

  const STAGES = [
    'lead_new', 'in_review', 'pending_docs', 'interview_scheduled',
    'conditional_offer', 'offer_sent', 'enrolled', 'declined', 'on_hold',
  ];

  useEffect(() => {
    const load = async () => {
      try {
        const [appRes, docsRes] = await Promise.all([
          apiClient.get(`/api/applications/${id}`, { withCredentials: true }),
          apiClient.get(`/api/applications/${id}/documents`, { withCredentials: true }),
        ]);
        setApp(appRes.data);
        setDocs(docsRes.data);
      } catch {}
      finally { setLoading(false); }
    };
    load();
  }, [id]);

  const updateStage = async newStage => {
    setStageUpdating(true);
    try {
      await apiClient.put(`/api/applications/${id}`, { current_stage: newStage }, { withCredentials: true });
      setApp(prev => ({ ...prev, current_stage: newStage }));
    } catch {}
    finally { setStageUpdating(false); }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={28} className="animate-spin text-primary" />
    </div>
  );
  if (!app) return <div className="p-6 text-slate-500">Bewerbung nicht gefunden</div>;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="applicant-detail-page">
      <div className="flex items-center gap-3">
        <Link to="/staff/kanban" className="text-slate-400 hover:text-primary transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-heading font-bold text-primary">
          {app.applicant?.full_name || 'Bewerber'}
        </h1>
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-sm ${STAGE_COLORS[app.current_stage] || 'bg-slate-100 text-slate-600'}`}>
          {STAGE_LABELS[app.current_stage] || app.current_stage}
        </span>
      </div>

      {/* Hauptbereich */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">

        {/* Linke Spalte: Daten + Dokumente */}
        <div className="xl:col-span-2 space-y-4">

          {/* Persönliche Daten */}
          <div className="bg-white border border-slate-200 rounded-sm p-5">
            <h3 className="font-semibold text-slate-700 mb-3 text-sm">Persönliche Daten</h3>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
              {[
                ['Name', app.applicant?.full_name || '–'],
                ['E-Mail', app.applicant?.email || '–'],
                ['Telefon', app.applicant?.phone || '–'],
                ['Herkunftsland', app.applicant?.country || '–'],
                ['Geburtsdatum', app.date_of_birth || '–'],
                ['Erstellt', formatDate(app.created_at)],
              ].map(([label, value]) => (
                <div key={label} className="flex gap-2">
                  <dt className="text-slate-500 w-28 shrink-0">{label}:</dt>
                  <dd className="text-slate-800 font-medium">{value}</dd>
                </div>
              ))}
            </dl>

            {/* Kommunikations-Shortcuts */}
            <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap gap-2">
              {app.applicant?.phone && (
                <a href={`tel:${app.applicant.phone.replace(/\s/g,'')}`}
                  data-testid="detail-click-to-dial"
                  className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 bg-green-50 text-green-700 border border-green-200 rounded-sm hover:bg-green-100 transition-colors">
                  <Phone size={13} /> Anrufen
                </a>
              )}
              {app.applicant?.email && (
                <a href={`mailto:${app.applicant.email}?subject=Ihre Bewerbung beim Studienkolleg Aachen`}
                  data-testid="detail-email-link"
                  className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-sm hover:bg-blue-100 transition-colors">
                  <Mail size={13} /> E-Mail schreiben
                </a>
              )}
              {app.applicant?.phone && (
                <a href={`https://wa.me/${app.applicant.phone.replace(/[^0-9+]/g,'').replace('+','')}`}
                  target="_blank" rel="noopener noreferrer"
                  data-testid="detail-whatsapp-link"
                  className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-sm hover:bg-emerald-100 transition-colors">
                  <MessageCircle size={13} /> WhatsApp
                </a>
              )}
            </div>
          </div>

          {/* Bewerbungsdetails */}
          <div className="bg-white border border-slate-200 rounded-sm p-5">
            <h3 className="font-semibold text-slate-700 mb-3 text-sm">Bewerbungsdetails</h3>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
              {[
                ['Gewünschter Kurs', app.course_type || '–'],
                ['Wunschsemester', app.desired_start || '–'],
                ['Deutschniveau', app.language_level || '–'],
                ['Abschlussland', app.degree_country || '–'],
                ['Kombination', app.combo_option || 'Keine'],
                ['Quelle', app.source || '–'],
              ].map(([label, value]) => (
                <div key={label} className="flex gap-2">
                  <dt className="text-slate-500 w-28 shrink-0">{label}:</dt>
                  <dd className="text-slate-800 font-medium">{value}</dd>
                </div>
              ))}
            </dl>
            {app.notes && (
              <div className="mt-3 pt-3 border-t border-slate-100">
                <dt className="text-slate-500 text-xs mb-1">Anmerkungen des Bewerbers:</dt>
                <dd className="text-slate-700 text-sm italic">"{app.notes}"</dd>
              </div>
            )}
          </div>

          {/* Status-Update */}
          <div className="bg-white border border-slate-200 rounded-sm p-5">
            <h3 className="font-semibold text-slate-700 mb-3 text-sm">Status ändern</h3>
            <div className="flex flex-wrap gap-2">
              {STAGES.map(stage => (
                <button
                  key={stage}
                  onClick={() => updateStage(stage)}
                  disabled={stageUpdating || app.current_stage === stage}
                  data-testid={`stage-btn-${stage}`}
                  className={`text-xs px-3 py-1.5 rounded-sm font-medium transition-all disabled:opacity-60 ${
                    app.current_stage === stage
                      ? 'bg-primary text-white'
                      : 'border border-slate-200 text-slate-600 hover:border-primary/50 hover:text-primary'
                  }`}
                >
                  {STAGE_LABELS[stage] || stage}
                </button>
              ))}
            </div>
          </div>

          {/* Dokumente */}
          <div className="bg-white border border-slate-200 rounded-sm p-5">
            <h3 className="font-semibold text-slate-700 mb-3 text-sm">Dokumente ({docs.length})</h3>
            {docs.length === 0 ? (
              <p className="text-slate-400 text-sm">Noch keine Dokumente hochgeladen</p>
            ) : (
              <ul className="space-y-2">
                {docs.map(doc => {
                  const statusCfg = DOC_STATUS[doc.status] || DOC_STATUS.uploaded;
                  const Icon = statusCfg.icon;
                  return (
                    <li key={doc.id} className="flex items-center justify-between text-sm border border-slate-100 rounded-sm p-3"
                      data-testid={`detail-doc-${doc.id}`}>
                      <div className="flex items-center gap-2">
                        <FileText size={16} className="text-slate-400" />
                        <div>
                          <p className="text-slate-700 font-medium text-xs">{doc.filename || doc.document_type}</p>
                          <p className="text-slate-400 text-xs">{doc.document_type} · {doc.has_binary ? 'Datei vorhanden' : 'Nur Metadaten'}</p>
                        </div>
                      </div>
                      <span className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-sm ${statusCfg.color}`}>
                        <Icon size={12} />
                        {statusCfg.label}
                      </span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>

        {/* Rechte Spalte: KI-Prüfung */}
        <div className="xl:col-span-1">
          <AIScreeningPanel appId={id} />
        </div>
      </div>
    </div>
  );
}
