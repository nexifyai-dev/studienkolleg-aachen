import React, { useEffect, useState, useCallback } from 'react';
import apiClient from '../lib/apiClient';
import { toast } from 'sonner';
import {
  Brain, RefreshCw, Loader2, CheckCircle, XCircle, AlertTriangle,
  FileText, Globe, Languages, Shield, ChevronDown, ChevronUp,
  Edit3, Save, X, Clock, Zap, ArrowRight, UserCheck
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

const stageLabels = {
  new: 'Neu eingegangen',
  lead_new: 'Neue Anfrage',
  documents_pending: 'Unterlagen ausstehend',
  pending_docs: 'Unterlagen angefordert',
  in_review: 'In Pruefung',
  interview_scheduled: 'Beratungsgespraech geplant',
  eligible: 'Zugelassen',
  conditionally_eligible: 'Bedingt zugelassen',
  conditional_offer: 'Vorlaeufige Zusage',
  offer_sent: 'Angebot versandt',
  rejected: 'Abgelehnt',
  declined: 'Abgelehnt',
  enrolled: 'Eingeschrieben',
  on_hold: 'Warteschleife',
  withdrawn: 'Zurueckgezogen',
};

/* ═══════ CHECK-ERGEBNIS ZEILE ═══════ */
function CheckRow({ icon: Icon, label, ok, note, detail, editable, onOverride }) {
  const [expanded, setExpanded] = useState(false);
  const [overrideVal, setOverrideVal] = useState('');
  const [overriding, setOverriding] = useState(false);

  const status = ok === true ? 'pass' : ok === false ? 'fail' : 'warn';
  const colors = {
    pass: { bg: 'bg-[var(--color-success-bg)]', text: 'text-[var(--color-success)]', border: 'border-[var(--color-success-border)]', icon: CheckCircle },
    fail: { bg: 'bg-[var(--color-danger-bg)]', text: 'text-[var(--color-danger)]', border: 'border-[var(--color-danger-border)]', icon: XCircle },
    warn: { bg: 'bg-[var(--color-warning-bg)]', text: 'text-[var(--color-warning)]', border: 'border-[var(--color-warning-border)]', icon: AlertTriangle },
  };
  const c = colors[status];
  const StatusIcon = c.icon;

  return (
    <div className={`border rounded-[var(--radius-sm)] ${c.border} ${c.bg}/30 overflow-hidden`} data-testid={`check-${label.toLowerCase().replace(/\s/g, '-')}`}>
      <button onClick={() => (detail || editable) && setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-3 py-2.5 text-left hover:bg-black/[0.02] transition-colors">
        <StatusIcon size={15} className={`${c.text} shrink-0`} />
        <Icon size={13} className="text-[var(--color-text-tertiary)] shrink-0" />
        <div className="flex-1 min-w-0">
          <span className="text-xs font-semibold text-[var(--color-text-primary)]">{label}</span>
          {note && <p className="text-[10px] text-[var(--color-text-secondary)] mt-0.5 leading-tight">{note}</p>}
        </div>
        <Badge variant={status === 'pass' ? 'success' : status === 'fail' ? 'danger' : 'warning'} size="xs">
          {status === 'pass' ? 'Bestanden' : status === 'fail' ? 'Fehlgeschlagen' : 'Pruefung noetig'}
        </Badge>
        {(detail || editable) && (expanded ? <ChevronUp size={12} className="text-[var(--color-text-tertiary)]" /> : <ChevronDown size={12} className="text-[var(--color-text-tertiary)]" />)}
      </button>
      {expanded && (
        <div className="px-3 pb-3 pt-1 border-t border-[var(--color-divider-subtle)]">
          {detail && <p className="text-[11px] text-[var(--color-text-secondary)] whitespace-pre-wrap leading-relaxed">{detail}</p>}
          {editable && onOverride && (
            <div className="mt-2 flex gap-2">
              {!overriding ? (
                <button onClick={() => setOverriding(true)} className="w2g-btn-secondary text-[10px]"><Edit3 size={10} /> Manuell korrigieren</button>
              ) : (
                <>
                  <input value={overrideVal} onChange={e => setOverrideVal(e.target.value)} placeholder="Korrektur / Begruendung..." className="w2g-input flex-1 text-[11px]" autoFocus />
                  <button onClick={() => { onOverride(label, overrideVal); setOverriding(false); setOverrideVal(''); }} className="w2g-btn-primary text-[10px]"><Save size={10} /></button>
                  <button onClick={() => setOverriding(false)} className="w2g-btn-secondary text-[10px]"><X size={10} /></button>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ═══════ KI-BERICHT SEKTION ═══════ */
function AIReportSection({ report }) {
  const [expanded, setExpanded] = useState(true);
  if (!report) return null;

  const sections = [];
  const lines = report.split('\n');
  let currentSection = null;

  for (const line of lines) {
    const heading = line.match(/^(\d+)\.\s*(.+?):\s*(.*)/);
    const boldHeading = line.match(/^\*\*(\d+)\.\s*(.+?)\*\*:?\s*(.*)/);
    if (heading || boldHeading) {
      const m = heading || boldHeading;
      if (currentSection) sections.push(currentSection);
      currentSection = { num: m[1], title: m[2].replace(/\*\*/g, ''), content: m[3] ? [m[3]] : [] };
    } else if (currentSection && line.trim()) {
      currentSection.content.push(line.trim());
    }
  }
  if (currentSection) sections.push(currentSection);
  if (sections.length === 0) sections.push({ num: '1', title: 'KI-Bericht', content: [report] });

  return (
    <div data-testid="ai-report-section">
      <button onClick={() => setExpanded(!expanded)} className="w-full flex items-center justify-between px-3 py-2 bg-[var(--color-primary)]/5 rounded-[var(--radius-sm)] hover:bg-[var(--color-primary)]/10 transition-colors mb-2">
        <span className="text-xs font-bold text-[var(--color-primary)] flex items-center gap-2"><Brain size={13} /> KI-Analysebericht</span>
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>
      {expanded && (
        <div className="space-y-2">
          {sections.map((s, i) => (
            <div key={i} className="bg-[var(--color-surface-elevated)] rounded-[var(--radius-sm)] px-3 py-2.5" data-testid={`ai-section-${i}`}>
              <p className="text-[10px] font-bold text-[var(--color-primary)] uppercase tracking-wide mb-1">{s.num}. {s.title}</p>
              {s.content.map((c, j) => (
                <p key={j} className="text-[11px] text-[var(--color-text-secondary)] leading-relaxed">{c.replace(/^[-•]\s*/, '').replace(/\*\*/g, '')}</p>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════
   AI SCREENING DELTA PANEL – HAUPTKOMPONENTE
   ══════════════════════════════════════════════════════════════ */
export default function AIScreeningDeltaPanel({ applicationId }) {
  const [screening, setScreening] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rescreening, setRescreening] = useState(false);
  const [overrides, setOverrides] = useState({});
  const [overrideSaving, setOverrideSaving] = useState(false);

  const load = useCallback(async () => {
    try {
      const r = await apiClient.get(`/api/applications/${applicationId}/screening-delta`, { withCredentials: true });
      setScreening(r.data);
    } catch { }
    finally { setLoading(false); }
  }, [applicationId]);

  useEffect(() => { load(); }, [load]);

  const runScreening = async () => {
    setRescreening(true);
    try {
      await apiClient.post(`/api/applications/${applicationId}/manual-rescreen`, {}, { withCredentials: true });
      toast.success('KI-Screening gestartet');
      setTimeout(load, 2000);
    } catch (e) { toast.error(e.response?.data?.detail || 'Screening fehlgeschlagen'); }
    finally { setRescreening(false); }
  };

  const handleOverride = (checkName, reason) => {
    setOverrides(prev => ({ ...prev, [checkName]: { reason, overridden_at: new Date().toISOString() } }));
    toast.success(`Manuelle Korrektur: ${checkName}`);
  };

  const saveOverrides = async () => {
    setOverrideSaving(true);
    try {
      await apiClient.post(`/api/applications/${applicationId}/notes`, {
        content: `KI-Screening manuelle Korrekturen:\n${Object.entries(overrides).map(([k, v]) => `- ${k}: ${v.reason}`).join('\n')}`,
        visibility: 'internal'
      }, { withCredentials: true });
      toast.success('Korrekturen als Notiz gespeichert');
      setOverrides({});
    } catch { toast.error('Fehler beim Speichern'); }
    finally { setOverrideSaving(false); }
  };

  const latest = screening?.latest;
  const localChecks = latest?.local_checks || {};
  const completeness = localChecks.completeness || {};
  const anabin = localChecks.anabin_assessment || {};
  const langCheck = localChecks.language_level_check || {};

  return (
    <Card className="overflow-hidden" data-testid="ai-screening-panel">
      <CardHeader className="flex-row items-center justify-between gap-2 pb-0 bg-[var(--color-primary)]/[0.03]">
        <CardTitle className="flex items-center gap-2 text-xs">
          <Brain size={15} className="text-[var(--color-primary)]" />
          KI-Screening
          {latest?.screened_at && <span className="text-[10px] font-normal text-[var(--color-text-tertiary)] ml-2">{new Date(latest.screened_at).toLocaleString('de-DE')}</span>}
        </CardTitle>
        <div className="flex items-center gap-2">
          {latest && (
            <Badge variant={latest.staff_decision_required ? 'warning' : latest.is_complete ? 'success' : 'danger'} size="sm" data-testid="screening-status-badge">
              {latest.staff_decision_required ? 'Staff-Entscheid noetig' : latest.is_complete ? 'Vorpruefung bestanden' : 'Unvollstaendig'}
            </Badge>
          )}
          <button onClick={runScreening} disabled={rescreening} className="w2g-btn-primary text-xs" data-testid="screening-run-btn">
            {rescreening ? <Loader2 size={12} className="animate-spin" /> : <RefreshCw size={12} />}
            {rescreening ? 'Pruefe...' : latest ? 'Erneut pruefen' : 'Screening starten'}
          </button>
        </div>
      </CardHeader>

      <CardContent className="pt-4 space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={20} className="animate-spin text-[var(--color-primary)]" />
            <span className="ml-2 text-xs text-[var(--color-text-secondary)]">Screening-Daten werden geladen...</span>
          </div>
        ) : !latest ? (
          <div className="text-center py-6 bg-[var(--color-surface-elevated)] rounded-[var(--radius-sm)]" data-testid="screening-empty">
            <Brain size={28} className="mx-auto text-[var(--color-text-tertiary)] mb-2" />
            <p className="text-sm font-bold text-[var(--color-text-primary)]" style={{ fontFamily: 'var(--font-heading)' }}>Noch kein Screening durchgefuehrt</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">Klicken Sie oben auf "Screening starten" um die automatische Vorpruefung zu beginnen.</p>
          </div>
        ) : (
          <>
            {/* ── Status-Vorschlag mit Stage-Label ── */}
            {latest.suggested_stage && (
              <div className="flex items-center gap-3 p-3 bg-[var(--color-primary)]/5 rounded-[var(--radius-sm)] border border-[var(--color-primary)]/20" data-testid="screening-suggestion">
                <Zap size={16} className="text-[var(--color-primary)] shrink-0" />
                <div className="flex-1">
                  <p className="text-xs font-semibold text-[var(--color-primary)]">Empfohlener Status</p>
                  <p className="text-sm font-bold text-[var(--color-text-primary)]">{stageLabels[latest.suggested_stage] || latest.suggested_stage}</p>
                </div>
                {latest.cache_hit && <Badge variant="outline" size="xs"><Clock size={9} /> Cache</Badge>}
                {latest.ai_model && <Badge variant="outline" size="xs">{latest.ai_model}</Badge>}
              </div>
            )}

            {/* ── Regelbasierte Pruefungen (Beweise) ── */}
            <div data-testid="screening-checks">
              <p className="text-[10px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-[0.1em] mb-2">Regelbasierte Pruefungen</p>
              <div className="space-y-2">
                {/* Vollstaendigkeit */}
                <CheckRow icon={FileText} label="Dokumenten-Vollstaendigkeit"
                  ok={completeness.complete}
                  note={completeness.complete
                    ? `Alle ${completeness.total_required || 3} Pflichtdokumente vorhanden (${completeness.total_validated || 0} validiert)`
                    : `${completeness.total_present || 0}/${completeness.total_required || 3} vorhanden – Fehlend: ${(completeness.missing_labels || []).join(', ') || 'Unbekannt'}`}
                  detail={[
                    completeness.present_labels?.length > 0 && `Vorhanden: ${completeness.present_labels.join(', ')}`,
                    completeness.validated_labels?.length > 0 && `Validiert: ${completeness.validated_labels.join(', ')}`,
                    completeness.missing_labels?.length > 0 && `Fehlend: ${completeness.missing_labels.join(', ')}`,
                  ].filter(Boolean).join('\n')}
                  editable onOverride={handleOverride} />

                {/* Sprachniveau */}
                <CheckRow icon={Languages} label="Sprachniveau"
                  ok={langCheck.ok}
                  note={langCheck.note || 'Keine Sprachpruefung'}
                  detail={langCheck.note}
                  editable onOverride={handleOverride} />

                {/* Anabin */}
                <CheckRow icon={Globe} label="Anabin-Kategorie"
                  ok={anabin.category === 'H+' ? true : anabin.category === 'H' ? true : anabin.category === 'D' ? false : null}
                  note={`${anabin.label || 'Unbekannt'} (Kategorie: ${anabin.category || '?'}, Konfidenz: ${anabin.confidence || '?'}, Match: ${anabin.match_type || '?'})`}
                  detail={[
                    anabin.operational_classification && `Einstufung: ${anabin.operational_classification}`,
                    anabin.staff_note && `Staff-Hinweis: ${anabin.staff_note}`,
                    anabin.source && `Quelle: ${anabin.source}`,
                    anabin.requires_staff_decision && 'Staff-Entscheidung erforderlich!',
                    anabin.is_special_case && 'Sonderfall – manuelle Pruefung notwendig.',
                  ].filter(Boolean).join('\n')}
                  editable onOverride={handleOverride} />

                {/* Staff-Entscheid */}
                <CheckRow icon={UserCheck} label="Staff-Entscheid"
                  ok={!latest.staff_decision_required}
                  note={latest.staff_decision_required
                    ? 'Manuelle Pruefung durch Sachbearbeiter erforderlich'
                    : 'Automatische Vorpruefung ausreichend'}
                  detail={latest.decision_note || ''} />
              </div>
            </div>

            {/* ── Fehlende Dokumente (wenn vorhanden) ── */}
            {latest.missing_documents?.length > 0 && (
              <div className="bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)] rounded-[var(--radius-sm)] p-3" data-testid="screening-missing-docs">
                <p className="text-xs font-bold text-[var(--color-danger)] flex items-center gap-1.5 mb-1.5"><AlertTriangle size={12} /> Fehlende Pflichtdokumente</p>
                <ul className="space-y-1">
                  {latest.missing_documents.map((doc, i) => (
                    <li key={i} className="text-[11px] text-[var(--color-danger)] flex items-center gap-1.5">
                      <ArrowRight size={10} /> {doc}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* ── Manuelle Korrekturen speichern ── */}
            {Object.keys(overrides).length > 0 && (
              <div className="flex items-center justify-between p-3 bg-[var(--color-warning-bg)] rounded-[var(--radius-sm)] border border-[var(--color-warning-border)]" data-testid="screening-overrides">
                <div>
                  <p className="text-xs font-bold text-[var(--color-warning)]">{Object.keys(overrides).length} manuelle Korrektur(en)</p>
                  {Object.entries(overrides).map(([k, v]) => (
                    <p key={k} className="text-[10px] text-[var(--color-text-secondary)]">{k}: {v.reason}</p>
                  ))}
                </div>
                <button onClick={saveOverrides} disabled={overrideSaving} className="w2g-btn-primary text-xs" data-testid="screening-save-overrides">
                  {overrideSaving ? <Loader2 size={12} className="animate-spin" /> : <Save size={12} />} Speichern
                </button>
              </div>
            )}

            {/* ── KI-Analysebericht ── */}
            {latest.ai_report && <AIReportSection report={latest.ai_report} />}

            {/* ── KI-Fehler ── */}
            {latest.ai_error && (
              <div className="bg-[var(--color-danger-bg)] rounded-[var(--radius-sm)] p-3 border border-[var(--color-danger-border)]" data-testid="screening-ai-error">
                <p className="text-xs font-bold text-[var(--color-danger)] flex items-center gap-1.5 mb-1"><AlertTriangle size={12} /> KI-Fehler</p>
                <p className="text-[11px] text-[var(--color-danger)]">{latest.ai_error}</p>
              </div>
            )}

            {/* ── Screening-Metadaten ── */}
            <div className="flex items-center gap-4 text-[10px] text-[var(--color-text-tertiary)] pt-2 border-t border-[var(--color-divider-subtle)]" data-testid="screening-meta">
              {latest.ai_model && <span className="flex items-center gap-1"><Brain size={10} /> {latest.ai_model}</span>}
              {latest.ai_tokens_used > 0 && <span className="flex items-center gap-1"><Zap size={10} /> {latest.ai_tokens_used} Tokens</span>}
              {latest.cache_hit && <span className="flex items-center gap-1"><Clock size={10} /> Cache-Treffer</span>}
              <span className="flex items-center gap-1"><Shield size={10} /> Keine bindende Entscheidung</span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
