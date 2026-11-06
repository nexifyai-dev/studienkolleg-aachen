import React from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Loader2, Calendar, MessageCircle, CheckCircle, AlertTriangle, Link2, Unlink, Send, RefreshCcw } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';
import { API } from '../../lib/apiBase';
import { csrfRequestInterceptor } from '../../lib/csrf';

const api = axios.create({ baseURL: `${API}/api`, withCredentials: true });
api.interceptors.request.use(csrfRequestInterceptor);

function StatusPill({ ok, label }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-medium rounded-[var(--radius-full)] ${ok
      ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]'
      : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)]'}`}>
      {ok ? <CheckCircle size={9} /> : <AlertTriangle size={9} />} {label}
    </span>
  );
}

function GoogleCalendarSection() {
  const qc = useQueryClient();
  const [busy, setBusy] = React.useState('');

  const status = useQuery({
    queryKey: ['integrations', 'google'],
    queryFn: () => api.get('/oauth/google/status').then(r => r.data),
  });

  // Handle callback params
  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const g = params.get('google');
    if (g === 'connected') { toast.success('Google Kalender verbunden'); qc.invalidateQueries({ queryKey: ['integrations', 'google'] }); }
    if (g === 'error') toast.error('Google-Verbindung fehlgeschlagen');
    if (g) window.history.replaceState({}, '', window.location.pathname);
  }, [qc]);

  const connect = async () => {
    setBusy('connect');
    try {
      const r = await api.get('/oauth/google/authorize');
      if (r.data?.authorization_url) window.location.href = r.data.authorization_url;
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Verbindungsaufbau fehlgeschlagen');
    } finally { setBusy(''); }
  };

  const disconnect = async () => {
    if (!window.confirm('Google Kalender-Verbindung wirklich trennen?')) return;
    setBusy('disconnect');
    try {
      await api.post('/oauth/google/disconnect');
      toast.success('Verbindung getrennt');
      qc.invalidateQueries({ queryKey: ['integrations', 'google'] });
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Trennen fehlgeschlagen');
    } finally { setBusy(''); }
  };

  const s = status.data || {};

  return (
    <Card className="p-5" data-testid="google-calendar-section">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--color-primary)]/10 flex items-center justify-center text-[var(--color-primary)]">
            <Calendar size={18} />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">Google Kalender</h3>
            <p className="text-[11px] text-[var(--color-text-tertiary)] mt-0.5">Termine automatisch synchronisieren (Erstellung, Update, Löschung)</p>
          </div>
        </div>
        <div className="flex gap-1.5 shrink-0">
          <StatusPill ok={s.configured} label={s.configured ? 'API konfiguriert' : 'API nicht konfiguriert'} />
          <StatusPill ok={s.connected} label={s.connected ? 'Verbunden' : 'Nicht verbunden'} />
        </div>
      </div>

      {!s.configured && (
        <div className="mt-4 p-3 rounded-[var(--radius-sm)] bg-[var(--color-warning-bg)]/40 border border-[var(--color-warning)]/30 text-[11px] text-[var(--color-text-secondary)] leading-relaxed">
          <strong>Setup benötigt:</strong> In <code className="font-mono">/app/backend/.env</code> die Variablen <code className="font-mono">GOOGLE_CLIENT_ID</code>, <code className="font-mono">GOOGLE_CLIENT_SECRET</code> und optional <code className="font-mono">GOOGLE_CALENDAR_ID</code> setzen.
          <br />OAuth-Consent-Screen im Google Cloud Console konfigurieren und Redirect-URI eintragen:
          <div className="mt-1 font-mono text-[10px] break-all">{window.location.origin}/api/oauth/google/callback</div>
        </div>
      )}

      {s.configured && (
        <div className="mt-4 space-y-3">
          {s.connected ? (
            <>
              <div className="text-[11px] text-[var(--color-text-secondary)] space-y-0.5">
                <div><span className="text-[var(--color-text-tertiary)]">Verbunden als:</span> <span className="font-medium text-[var(--color-text-primary)]">{s.connected_email || '(unbekannt)'}</span></div>
                <div><span className="text-[var(--color-text-tertiary)]">Kalender-ID:</span> <span className="font-mono">{s.calendar_id}</span></div>
                <div><span className="text-[var(--color-text-tertiary)]">Verbunden am:</span> {s.connected_at ? new Date(s.connected_at).toLocaleString('de-DE') : '–'}</div>
              </div>
              <div className="flex gap-2">
                <button onClick={disconnect} disabled={busy === 'disconnect'} className="w2g-btn-secondary text-xs flex items-center gap-1.5" data-testid="google-disconnect-btn">
                  {busy === 'disconnect' ? <Loader2 size={12} className="animate-spin" /> : <Unlink size={12} />} Trennen
                </button>
                <button onClick={() => qc.invalidateQueries({ queryKey: ['integrations', 'google'] })} className="w2g-btn-secondary text-xs flex items-center gap-1.5" data-testid="google-refresh-btn">
                  <RefreshCcw size={12} /> Neu prüfen
                </button>
              </div>
            </>
          ) : (
            <button onClick={connect} disabled={busy === 'connect'} className="w2g-btn-primary text-xs flex items-center gap-1.5" data-testid="google-connect-btn">
              {busy === 'connect' ? <Loader2 size={12} className="animate-spin" /> : <Link2 size={12} />} Mit Google Kalender verbinden
            </button>
          )}
        </div>
      )}
    </Card>
  );
}

function WhatsAppSection() {
  const qc = useQueryClient();
  const [busy, setBusy] = React.useState(false);
  const [form, setForm] = React.useState({ to: '', body: '' });

  const status = useQuery({
    queryKey: ['integrations', 'whatsapp'],
    queryFn: () => api.get('/whatsapp/status').then(r => r.data),
  });

  const messages = useQuery({
    queryKey: ['integrations', 'whatsapp', 'messages'],
    queryFn: () => api.get('/whatsapp/messages?limit=20').then(r => r.data?.messages || []),
    refetchInterval: 15000,
  });

  const send = async () => {
    if (!form.to || !form.body) return toast.error('Bitte Empfänger und Nachricht ausfüllen');
    setBusy(true);
    try {
      const r = await api.post('/whatsapp/send', form);
      if (r.data?.status === 'sent') toast.success('WhatsApp gesendet');
      else if (r.data?.status === 'skipped') toast.warning('Twilio nicht konfiguriert – Nachricht übersprungen');
      else toast.error(r.data?.reason || 'Senden fehlgeschlagen');
      setForm({ to: '', body: '' });
      qc.invalidateQueries({ queryKey: ['integrations', 'whatsapp'] });
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Senden fehlgeschlagen');
    } finally { setBusy(false); }
  };

  const s = status.data || {};

  return (
    <Card className="p-5" data-testid="whatsapp-section">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[#25D366]/10 flex items-center justify-center text-[#25D366]">
            <MessageCircle size={18} />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">WhatsApp (Twilio)</h3>
            <p className="text-[11px] text-[var(--color-text-tertiary)] mt-0.5">Bewerber-Benachrichtigungen über WhatsApp Business API</p>
          </div>
        </div>
        <StatusPill ok={s.configured} label={s.configured ? 'Konfiguriert' : 'Nicht konfiguriert'} />
      </div>

      {!s.configured ? (
        <div className="mt-4 p-3 rounded-[var(--radius-sm)] bg-[var(--color-warning-bg)]/40 border border-[var(--color-warning)]/30 text-[11px] text-[var(--color-text-secondary)] leading-relaxed">
          <strong>Setup benötigt:</strong> In <code className="font-mono">/app/backend/.env</code> setzen:
          <ul className="mt-1 space-y-0.5 font-mono text-[10px]">
            <li>TWILIO_ACCOUNT_SID</li>
            <li>TWILIO_AUTH_TOKEN</li>
            <li>TWILIO_WHATSAPP_FROM (z.B. whatsapp:+14155238886)</li>
          </ul>
        </div>
      ) : (
        <>
          <div className="mt-4 text-[11px] text-[var(--color-text-secondary)] space-y-0.5">
            <div><span className="text-[var(--color-text-tertiary)]">Absender:</span> <span className="font-mono">{s.from_number}</span></div>
            <div><span className="text-[var(--color-text-tertiary)]">Account SID:</span> <span className="font-mono">{s.account_sid_prefix}</span></div>
          </div>

          <div className="mt-4 pt-4 border-t border-[var(--color-divider-subtle)]">
            <div className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)] mb-2">Test-Nachricht senden</div>
            <div className="space-y-2">
              <input
                value={form.to}
                onChange={e => setForm(f => ({ ...f, to: e.target.value }))}
                placeholder="+491701234567"
                className="w-full text-xs rounded-[var(--radius-sm)] px-3 py-2 border border-[var(--color-divider)] bg-[var(--color-surface)]"
                data-testid="whatsapp-to-input"
              />
              <textarea
                value={form.body}
                onChange={e => setForm(f => ({ ...f, body: e.target.value }))}
                placeholder="Nachricht..."
                rows={3}
                className="w-full text-xs rounded-[var(--radius-sm)] px-3 py-2 border border-[var(--color-divider)] bg-[var(--color-surface)]"
                data-testid="whatsapp-body-input"
              />
              <button onClick={send} disabled={busy} className="w2g-btn-primary text-xs flex items-center gap-1.5 disabled:opacity-50" data-testid="whatsapp-send-btn">
                {busy ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />} Senden
              </button>
            </div>
          </div>
        </>
      )}

      {/* Log */}
      <div className="mt-4 pt-4 border-t border-[var(--color-divider-subtle)]">
        <div className="text-[10px] uppercase tracking-wide text-[var(--color-text-tertiary)] mb-2">Letzte Nachrichten</div>
        <div className="space-y-1.5" data-testid="whatsapp-log">
          {(messages.data || []).length === 0 ? (
            <div className="text-[11px] text-[var(--color-text-tertiary)] italic">Noch keine Nachrichten protokolliert</div>
          ) : (messages.data || []).map(m => (
            <div key={m.id} className="flex items-center justify-between gap-2 text-[11px] px-2 py-1.5 rounded-[var(--radius-sm)] bg-[var(--color-surface-sunken)]">
              <div className="min-w-0 flex-1">
                <div className="font-mono text-[10px] text-[var(--color-text-tertiary)]">{m.to}</div>
                <div className="text-[var(--color-text-secondary)] truncate">{m.body}</div>
              </div>
              <span className={`shrink-0 text-[9px] font-medium uppercase px-1.5 py-0.5 rounded ${m.status === 'sent' ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]'
                : m.status === 'failed' ? 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]'
                : 'bg-[var(--color-surface)] text-[var(--color-text-tertiary)]'}`}>{m.status}</span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

export default function AdminIntegrationsPage() {
  return (
    <PageScaffold
      title="Integrationen"
      subtitle="Externe Dienste verbinden – Google Kalender, WhatsApp"
      testId="admin-integrations-page"
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <GoogleCalendarSection />
        <WhatsAppSection />
      </div>
    </PageScaffold>
  );
}
