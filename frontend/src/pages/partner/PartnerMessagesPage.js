import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, Loader2 } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { ContentHeader } from '../../components/layout/BackstageComponents';
import { toast } from 'sonner';

export default function PartnerMessagesPage() {
  const [conversations, setConversations] = useState([]);
  const [selected, setSelected] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMsg, setNewMsg] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    apiClient.get('/api/messaging/conversations')
      .then(r => setConversations(r.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const selectConv = async (conv) => {
    setSelected(conv);
    try {
      const r = await apiClient.get(`/api/messaging/conversations/${conv.id}/messages`);
      setMessages(r.data || []);
    } catch {
      toast.error('Nachrichten konnten nicht geladen werden');
    }
  };

  const sendMessage = async () => {
    if (!newMsg.trim() || !selected) return;
    setSending(true);
    try {
      await apiClient.post(`/api/messaging/conversations/${selected.id}/messages`, {
        content: newMsg, visibility: 'shared',
      });
      setNewMsg('');
      const r = await apiClient.get(`/api/messaging/conversations/${selected.id}/messages`);
      setMessages(r.data || []);
    } catch {
      toast.error('Nachricht konnte nicht gesendet werden');
    } finally {
      setSending(false);
    }
  };

  if (loading) return <div className="flex items-center justify-center py-16"><Loader2 size={20} className="animate-spin" /></div>;

  return (
    <div className="space-y-4">
      <ContentHeader title="Nachrichten" subtitle="Kommunikation mit dem Team" />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4" style={{ minHeight: 400 }}>
        {/* Conversations list */}
        <div className="border border-[var(--color-border)] rounded-[var(--radius-sm)] overflow-hidden">
          <div className="p-3 bg-[var(--color-surface)] border-b border-[var(--color-border)]">
            <p className="text-xs font-medium text-[var(--color-text-secondary)]">Konversationen ({conversations.length})</p>
          </div>
          <div className="overflow-y-auto" style={{ maxHeight: 350 }}>
            {conversations.length === 0 ? (
              <p className="p-4 text-xs text-[var(--color-text-secondary)] text-center">Keine Konversationen</p>
            ) : conversations.map(c => (
              <div
                key={c.id} onClick={() => selectConv(c)}
                data-testid={`conv-${c.id}`}
                className={`p-3 cursor-pointer border-b border-[var(--color-border)] last:border-0 hover:bg-[var(--color-surface)] transition-colors ${selected?.id === c.id ? 'bg-[var(--color-surface)]' : ''}`}
              >
                <p className="text-sm font-medium text-[var(--color-text-primary)] truncate">{c.subject || 'Konversation'}</p>
                <p className="text-xs text-[var(--color-text-secondary)] mt-0.5 truncate">{c.last_message || '–'}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="md:col-span-2 border border-[var(--color-border)] rounded-[var(--radius-sm)] flex flex-col">
          {!selected ? (
            <div className="flex-1 flex items-center justify-center text-sm text-[var(--color-text-secondary)]">
              <MessageSquare size={16} className="mr-2" /> Konversation auswaehlen
            </div>
          ) : (
            <>
              <div className="p-3 bg-[var(--color-surface)] border-b border-[var(--color-border)]">
                <p className="text-sm font-medium">{selected.subject || 'Konversation'}</p>
              </div>
              <div className="flex-1 overflow-y-auto p-4 space-y-3" style={{ maxHeight: 280 }}>
                {messages.map((m, i) => (
                  <div key={m.id || i} className={`flex ${m.sender_role === 'affiliate' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[75%] p-3 rounded-[var(--radius-sm)] text-sm ${m.sender_role === 'affiliate' ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--color-surface)]'}`}>
                      <p>{m.content}</p>
                      <p className="text-xs mt-1 opacity-60">{m.sender_name || '–'}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-3 border-t border-[var(--color-border)] flex gap-2">
                <input
                  data-testid="partner-msg-input" type="text" value={newMsg}
                  onChange={e => setNewMsg(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && sendMessage()}
                  placeholder="Nachricht schreiben..."
                  className="flex-1 text-sm border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2"
                />
                <button onClick={sendMessage} disabled={sending || !newMsg.trim()}
                  className="px-3 py-2 bg-[var(--color-primary)] text-white rounded-[var(--radius-sm)] hover:opacity-90 disabled:opacity-50">
                  {sending ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
