import React, { useState, useEffect, useCallback } from 'react';
import { Settings, Save, Plus, Trash2, AlertCircle } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { InfoCard, ContentHeader } from '../../components/layout/BackstageComponents';
import { toast } from 'sonner';

const DEFAULT_RULES = [
  { key: 'min_language_level', label: 'Mindest-Sprachniveau', type: 'select', options: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'], value: 'B1' },
  { key: 'require_passport', label: 'Reisepass erforderlich', type: 'boolean', value: true },
  { key: 'require_diploma', label: 'Abschlusszeugnis erforderlich', type: 'boolean', value: true },
  { key: 'require_language_cert', label: 'Sprachzertifikat erforderlich', type: 'boolean', value: true },
  { key: 'auto_screening_on_upload', label: 'Auto-KI-Screening bei Upload', type: 'boolean', value: true },
  { key: 'max_days_pending_docs', label: 'Max. Tage fuer Dokumentennachforderung', type: 'number', value: 14 },
  { key: 'auto_decline_incomplete_after_days', label: 'Auto-Ablehnung nach Tagen (unvollstaendig)', type: 'number', value: 60 },
  { key: 'interview_required_stages', label: 'Interview-Pflicht ab Stage', type: 'select', options: ['in_review', 'pending_docs', 'conditional_offer'], value: 'conditional_offer' },
];

export default function AdminRulesPage() {
  const [rules, setRules] = useState(DEFAULT_RULES);
  const [customRules, setCustomRules] = useState([]);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    apiClient.get('/api/system/settings').then(r => {
      const saved = r.data?.screening_rules;
      if (saved && typeof saved === 'object') {
        setRules(prev => prev.map(rule => ({
          ...rule, value: saved[rule.key] !== undefined ? saved[rule.key] : rule.value,
        })));
        if (saved._custom) setCustomRules(saved._custom);
      }
    }).catch(() => {});
  }, []);

  const updateRule = useCallback((key, value) => {
    setRules(prev => prev.map(r => r.key === key ? { ...r, value } : r));
    setDirty(true);
  }, []);

  const addCustomRule = () => {
    setCustomRules(prev => [...prev, { key: `custom_${Date.now()}`, label: '', type: 'boolean', value: false }]);
    setDirty(true);
  };

  const removeCustomRule = (idx) => {
    setCustomRules(prev => prev.filter((_, i) => i !== idx));
    setDirty(true);
  };

  const saveRules = async () => {
    setSaving(true);
    try {
      const payload = {};
      rules.forEach(r => { payload[r.key] = r.value; });
      payload._custom = customRules;
      await apiClient.put('/api/system/settings', { screening_rules: payload });
      toast.success('Screening-Regeln gespeichert');
      setDirty(false);
    } catch {
      toast.error('Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  return (
    <PageScaffold title="Screening-Regeln" icon={<Settings size={20} />}>
      <ContentHeader title="KI-Screening-Regeln" subtitle="Konfiguration der automatischen Bewertungslogik" />

      <div className="flex items-center justify-between mb-4">
        <p className="text-xs text-[var(--color-text-secondary)]">
          Aenderungen werden erst nach Speichern wirksam. Bestehende Screenings bleiben unveraendert.
        </p>
        <button
          data-testid="save-rules-btn" onClick={saveRules} disabled={!dirty || saving}
          className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-[var(--color-primary)] rounded-[var(--radius-sm)] disabled:opacity-50 hover:opacity-90 transition-opacity"
        >
          <Save size={14} /> {saving ? 'Speichern...' : 'Speichern'}
        </button>
      </div>

      <div className="space-y-4">
        <InfoCard title="Pflicht-Dokumentregeln">
          <div className="space-y-3">
            {rules.filter(r => r.type === 'boolean').map(rule => (
              <label key={rule.key} data-testid={`rule-${rule.key}`} className="flex items-center justify-between py-1.5">
                <span className="text-sm text-[var(--color-text-primary)]">{rule.label}</span>
                <button
                  onClick={() => updateRule(rule.key, !rule.value)}
                  className={`w-10 h-5 rounded-full transition-colors relative ${rule.value ? 'bg-[var(--color-primary)]' : 'bg-gray-300'}`}
                >
                  <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${rule.value ? 'left-5' : 'left-0.5'}`} />
                </button>
              </label>
            ))}
          </div>
        </InfoCard>

        <InfoCard title="Schwellenwerte">
          <div className="space-y-3">
            {rules.filter(r => r.type === 'select').map(rule => (
              <div key={rule.key} data-testid={`rule-${rule.key}`} className="flex items-center justify-between">
                <span className="text-sm text-[var(--color-text-primary)]">{rule.label}</span>
                <select
                  value={rule.value} onChange={e => updateRule(rule.key, e.target.value)}
                  className="text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-1.5 bg-white"
                >
                  {rule.options.map(o => <option key={o} value={o}>{o}</option>)}
                </select>
              </div>
            ))}
            {rules.filter(r => r.type === 'number').map(rule => (
              <div key={rule.key} data-testid={`rule-${rule.key}`} className="flex items-center justify-between">
                <span className="text-sm text-[var(--color-text-primary)]">{rule.label}</span>
                <input
                  type="number" value={rule.value} min={1} max={365}
                  onChange={e => updateRule(rule.key, parseInt(e.target.value) || 0)}
                  className="w-20 text-sm text-right border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-1.5"
                />
              </div>
            ))}
          </div>
        </InfoCard>

        <InfoCard title="Benutzerdefinierte Regeln">
          <div className="space-y-2 mb-3">
            {customRules.length === 0 && (
              <p className="text-xs text-[var(--color-text-secondary)] py-2">Keine benutzerdefinierten Regeln konfiguriert.</p>
            )}
            {customRules.map((cr, idx) => (
              <div key={cr.key} className="flex items-center gap-2">
                <input
                  type="text" placeholder="Regelname..." value={cr.label}
                  onChange={e => {
                    setCustomRules(prev => prev.map((r, i) => i === idx ? { ...r, label: e.target.value } : r));
                    setDirty(true);
                  }}
                  className="flex-1 text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-1.5"
                />
                <button onClick={() => removeCustomRule(idx)} className="p-1.5 text-red-500 hover:bg-red-50 rounded-[var(--radius-sm)]">
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
          <button onClick={addCustomRule} className="flex items-center gap-1.5 text-xs text-[var(--color-primary)] hover:underline">
            <Plus size={12} /> Regel hinzufuegen
          </button>
        </InfoCard>
      </div>

      <div className="mt-6 p-3 bg-amber-50 border border-amber-200 rounded-[var(--radius-sm)] flex items-start gap-2">
        <AlertCircle size={14} className="text-amber-600 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-amber-800">
          Die KI-Screening-Regeln beeinflussen die automatische Bewertung neuer Bewerbungen.
          Bereits abgeschlossene Screenings werden nicht retroaktiv geaendert.
        </p>
      </div>
    </PageScaffold>
  );
}
