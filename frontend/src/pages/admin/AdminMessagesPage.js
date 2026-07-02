import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api-hooks';
import { Loader2, Search, Mail, MessageSquare, Lock } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

const CHANNEL_BADGE = {
  email: { label: 'E-Mail', cls: 'bg-[var(--color-info-bg)] text-[var(--color-info)]' },
  portal: { label: 'Portal', cls: 'bg-[var(--color-success-bg)] text-[var(--color-success)]' },
};

export default function AdminMessagesPage() {
  const [channel, setChannel] = React.useState('all');
  const [search, setSearch] = React.useState('');
  const [active, setActive] = React.useState(null);

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'messages-audit', channel],
    queryFn: () => api.get('/conversations', { params: channel !== 'all' ? { channel, limit: 200 } : { limit: 200 } }).then(r => r.data),
    staleTime: 15000,
  });

  const { data: msgs, isLoading: msgsLoading } = useQuery({
    queryKey: ['admin', 'messages-audit-msgs', active?.id],
    queryFn: () => api.get(`/conversations/${active.id}/messages`).then(r => r.data),
    enabled: !!active,
  });

  const convs = (data?.conversations || []).filter(c => {
    const term = search.toLowerCase();
    return !term || (c.display_name || '').toLowerCase().includes(term) ||
      (c.subject || '').toLowerCase().includes(term) ||
      (c.last_message_preview || '').toLowerCase().includes(term);
  });

  return (
    <PageScaffold
      title="Nachrichten-Audit"
      subtitle={`${data?.total ?? 0} Konversationen plattformweit`}
      testId="admin-messages-page"
      toolbar={
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
            <input type="text" value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Name, Betreff oder Inhalt suchen..."
              className="w2g-search pl-9" data-testid="admin-messages-search" />
          </div>
          <select value={channel} onChange={e => { setChannel(e.target.value); setActive(null); }}
            className="text-xs rounded-[var(--radius-sm)] px-2.5 py-2 border border-[var(--color-divider)] bg-[var(--color-surface)] text-[var(--color-text-primary)]"
            data-testid="admin-messages-channel-filter">
            <option value="all">Alle Kanäle</option>
            <option value="portal">Portal</option>
            <option value="email">E-Mail</option>
          </select>
        </div>
      }
    >
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 size={24} className="animate-spin text-[var(--color-primary)]" />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
          <Card className="lg:col-span-2 p-0 overflow-hidden max-h-[70vh] overflow-y-auto" data-testid="admin-conversations-list">
            {convs.map(c => {
              const badge = CHANNEL_BADGE[c.channel] || CHANNEL_BADGE.portal;
              return (
                <button key={c.id} onClick={() => setActive(c)}
                  className={`w-full text-left px-4 py-3 border-b border-[var(--color-divider-subtle)] transition-colors
                    ${active?.id === c.id ? 'bg-[var(--color-surface-sunken)]' : 'hover:bg-[var(--color-surface-sunken)]'}`}
                  data-testid={`admin-conv-${c.id}`}>
                  <div className="flex items-center justify-between gap-2 mb-0.5">
                    <span className="text-xs font-semibold text-[var(--color-text-primary)] truncate">
                      {c.display_name || c.subject || 'Konversation'}
                    </span>
                    <span className={`shrink-0 inline-flex px-1.5 py-0.5 text-[9px] font-medium rounded-[var(--radius-full)] ${badge.cls}`}>
                      {badge.label}
                    </span>
                  </div>
                  {c.subject && <div className="text-[11px] text-[var(--color-text-secondary)] truncate">{c.subject}</div>}
                  <div className="flex items-center justify-between gap-2 mt-0.5">
                    <span className="text-[10px] text-[var(--color-text-tertiary)] truncate">
                      {(c.last_message_preview || '').slice(0, 60)}
                    </span>
                    <span className="shrink-0 text-[10px] text-[var(--color-text-tertiary)]">
                      {c.last_message_at ? new Date(c.last_message_at).toLocaleDateString('de-DE') : ''}
                    </span>
                  </div>
                </button>
              );
            })}
            {convs.length === 0 && (
              <div className="text-center py-10 text-xs text-[var(--color-text-tertiary)]">Keine Konversationen</div>
            )}
          </Card>

          <Card className="lg:col-span-3 p-0 overflow-hidden max-h-[70vh] flex flex-col" data-testid="admin-messages-panel">
            {!active ? (
              <div className="flex-1 flex flex-col items-center justify-center gap-2 text-[var(--color-text-tertiary)] py-16">
                <MessageSquare size={28} />
                <span className="text-xs">Konversation auswählen (Nur-Lesen-Audit)</span>
              </div>
            ) : (
              <>
                <div className="px-4 py-3 border-b border-[var(--color-divider)] flex items-center gap-2">
                  <Mail size={14} className="text-[var(--color-primary)]" />
                  <div>
                    <div className="text-xs font-semibold text-[var(--color-text-primary)]">{active.display_name || active.subject || 'Konversation'}</div>
                    <div className="text-[10px] text-[var(--color-text-tertiary)]">
                      Status: {active.status} · Zugewiesen: {active.assigned_to_name || '—'}
                    </div>
                  </div>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {msgsLoading ? (
                    <div className="flex justify-center py-8"><Loader2 size={18} className="animate-spin text-[var(--color-primary)]" /></div>
                  ) : (msgs || []).map(m => (
                    <div key={m.id} className="rounded-[var(--radius-sm)] border border-[var(--color-divider-subtle)] bg-[var(--color-surface-elevated)] p-3" data-testid={`audit-msg-${m.id}`}>
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="text-[11px] font-semibold text-[var(--color-text-primary)]">{m.sender_name || 'System'}</span>
                        <span className="flex items-center gap-1.5 text-[10px] text-[var(--color-text-tertiary)]">
                          {m.visibility === 'internal' && (
                            <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-[var(--radius-full)] bg-[var(--color-warning-bg)] text-[var(--color-warning)]">
                              <Lock size={8} /> Intern
                            </span>
                          )}
                          {m.sent_at ? new Date(m.sent_at).toLocaleString('de-DE') : ''}
                        </span>
                      </div>
                      <p className="text-xs text-[var(--color-text-secondary)] whitespace-pre-wrap break-words">{m.content}</p>
                    </div>
                  ))}
                  {!msgsLoading && (msgs || []).length === 0 && (
                    <div className="text-center py-8 text-xs text-[var(--color-text-tertiary)]">Keine Nachrichten</div>
                  )}
                </div>
              </>
            )}
          </Card>
        </div>
      )}
    </PageScaffold>
  );
}
