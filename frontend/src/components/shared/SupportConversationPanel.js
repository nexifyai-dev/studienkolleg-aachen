import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { HelpCircle, Loader2, MessageSquare, Send } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { useAuth } from '../../contexts/AuthContext';
import { PageScaffold } from '../layout/PageScaffold';

function MessageBubble({ message, isOwn }) {
  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[92%] rounded-[var(--radius-lg)] px-4 py-3 text-sm ${isOwn ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-primary)]'}`} data-testid={`support-message-${message.id}`}>
        {!isOwn && message.sender_name ? <p className="mb-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--color-text-secondary)]">{message.sender_name}</p> : null}
        <p className="whitespace-pre-wrap">{message.content}</p>
        <p className={`mt-1 text-[10px] ${isOwn ? 'text-white/60' : 'text-[var(--color-text-tertiary)]'}`}>
          {message.sent_at ? new Date(message.sent_at).toLocaleString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : ''}
        </p>
      </div>
    </div>
  );
}

export function SupportConversationPanel({
  title,
  subtitle,
  testId,
  quickTopics = [],
  contextBlocks = [],
  actionLinks = [],
}) {
  const { user } = useAuth();
  const [conversation, setConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const endRef = useRef(null);

  const loadConversation = async () => {
    try {
      const supportRes = await apiClient.get('/api/conversations/support', { withCredentials: true });
      const conv = supportRes.data;
      setConversation(conv);
      if (conv?.id) {
        const msgRes = await apiClient.get(`/api/conversations/${conv.id}/messages`, { withCredentials: true });
        setMessages(msgRes.data || []);
      }
    } catch {
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversation();
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const otherNames = useMemo(() => {
    if (!conversation?.participant_names) return 'Support-Team';
    return Object.entries(conversation.participant_names)
      .filter(([id]) => id !== user?.id)
      .map(([, value]) => value)
      .join(', ') || 'Support-Team';
  }, [conversation, user?.id]);

  const sendMessage = async (event) => {
    event.preventDefault();
    if (!input.trim() || !conversation?.id) return;
    setSending(true);
    try {
      const response = await apiClient.post('/api/messages', { conversation_id: conversation.id, content: input.trim() }, { withCredentials: true });
      setMessages((current) => [...current, response.data]);
      setInput('');
    } finally {
      setSending(false);
    }
  };

  return (
    <PageScaffold title={title} subtitle={subtitle} testId={testId}>
      <div className="grid gap-4 xl:grid-cols-[280px_minmax(0,1fr)_320px]">
        <aside className="w2g-card p-0 overflow-hidden" data-testid={`${testId}-conversation-list`}>
          <div className="border-b border-[var(--color-divider-subtle)] px-5 py-4">
            <p className="text-xs uppercase tracking-[0.16em] text-[var(--color-text-tertiary)]">Konversationen</p>
          </div>
          <div className="p-4">
            <button type="button" className="flex w-full items-start gap-3 rounded-[var(--radius-lg)] bg-[var(--color-primary)]/6 px-4 py-4 text-left" data-testid={`${testId}-support-thread`}>
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--color-primary)] text-white">
                <MessageSquare size={16} />
              </div>
              <div>
                <p className="text-sm font-semibold text-[var(--color-text-primary)]">{otherNames}</p>
                <p className="text-xs text-[var(--color-text-secondary)]">Direkter Support- und Klärungskanal</p>
              </div>
            </button>
          </div>
        </aside>

        <section className="w2g-card p-0 overflow-hidden" data-testid={`${testId}-chat-panel`}>
          <div className="border-b border-[var(--color-divider-subtle)] px-5 py-4">
            <p className="text-sm font-semibold text-[var(--color-text-primary)]">{otherNames}</p>
            <p className="text-xs text-[var(--color-text-secondary)]">Antwortweg für Status-, Dokument- und Abrechnungsfragen</p>
          </div>

          <div className="min-h-[460px] space-y-3 overflow-y-auto bg-[var(--color-surface-elevated)]/70 px-5 py-4" data-testid={`${testId}-messages`}>
            {loading ? (
              <div className="flex h-full items-center justify-center text-[var(--color-text-tertiary)]"><Loader2 size={20} className="animate-spin" /></div>
            ) : messages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center gap-3 text-center text-[var(--color-text-secondary)]">
                <HelpCircle size={26} className="text-[var(--color-primary)]" />
                <div>
                  <p className="text-sm font-semibold text-[var(--color-text-primary)]">Noch keine Nachrichten</p>
                  <p className="text-xs text-[var(--color-text-secondary)]">Starte den Austausch direkt mit dem Support-Team.</p>
                </div>
              </div>
            ) : (
              messages.map((message) => <MessageBubble key={message.id} message={message} isOwn={message.sender_id === user?.id} />)
            )}
            <div ref={endRef} />
          </div>

          <div className="border-t border-[var(--color-divider-subtle)] px-5 py-4">
            {quickTopics.length > 0 ? (
              <div className="mb-3 flex flex-wrap gap-2" data-testid={`${testId}-quick-topics`}>
                {quickTopics.map((topic) => (
                  <button key={topic} type="button" onClick={() => setInput(topic)} className="rounded-full border border-[var(--color-divider)] bg-white px-3 py-1.5 text-xs font-semibold text-[var(--color-text-secondary)] transition-colors hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]" data-testid={`${testId}-quick-topic-${topic.toLowerCase().replace(/[^a-z0-9]+/gi, '-')}`}>
                    {topic}
                  </button>
                ))}
              </div>
            ) : null}
            <form onSubmit={sendMessage} className="flex gap-3" data-testid={`${testId}-composer`}>
              <textarea value={input} onChange={(event) => setInput(event.target.value)} rows={3} className="w2g-input resize-none py-3" placeholder="Ihre Nachricht…" data-testid={`${testId}-composer-input`} />
              <button type="submit" disabled={sending || !input.trim()} className="w2g-btn-primary self-end px-4" data-testid={`${testId}-composer-submit`}>
                {sending ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              </button>
            </form>
          </div>
        </section>

        <aside className="space-y-4" data-testid={`${testId}-context-panel`}>
          {contextBlocks.map((block) => (
            <div key={block.title} className="w2g-card" data-testid={`${testId}-context-${block.title.toLowerCase().replace(/[^a-z0-9]+/gi, '-')}`}>
              <h2 className="mb-3 text-sm font-semibold text-[var(--color-text-primary)]">{block.title}</h2>
              <div className="space-y-3">
                {block.items.map((item) => (
                  <div key={item.label} className="rounded-[var(--radius-lg)] border border-[var(--color-divider)] bg-[var(--color-surface-elevated)] px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-[var(--color-text-tertiary)]">{item.label}</p>
                    <p className="mt-1 text-sm font-semibold text-[var(--color-text-primary)]">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}

          <div className="w2g-card" data-testid={`${testId}-action-links`}>
            <h2 className="mb-3 text-sm font-semibold text-[var(--color-text-primary)]">Schnellaktionen</h2>
            <div className="space-y-2">
              {actionLinks.map((action) => (
                <Link key={action.to} to={action.to} className="flex items-center justify-between rounded-[var(--radius-lg)] border border-[var(--color-divider)] bg-[var(--color-surface-elevated)] px-4 py-3 text-sm font-semibold text-[var(--color-text-primary)] transition-colors hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]" data-testid={`${testId}-action-${action.label.toLowerCase().replace(/[^a-z0-9]+/gi, '-')}`}>
                  <span>{action.label}</span>
                  <span aria-hidden="true">→</span>
                </Link>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </PageScaffold>
  );
}
