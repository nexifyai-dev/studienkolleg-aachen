import React, { useState, useRef, useEffect, useCallback } from 'react';
import { MessageCircle, X, Send, User, Minus } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';

export default function SupportChatWidget() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [minimized, setMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionUserId, setSessionUserId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // DSGVO: Chat-Verlauf bei User-Wechsel komplett zurücksetzen
  const currentUserId = user?.id || 'visitor';
  useEffect(() => {
    if (currentUserId !== sessionUserId) {
      setMessages([]);
      setSessionUserId(currentUserId);
    }
  }, [currentUserId, sessionUserId]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);

  useEffect(() => {
    if (open && !minimized) inputRef.current?.focus();
  }, [open, minimized]);

  const isPartner = user && ['agency_admin', 'agency_agent', 'affiliate'].includes(user.role);
  const isStaff = user && ['staff', 'admin', 'superadmin', 'accounting_staff', 'teacher'].includes(user.role);
  const greeting = !user
    ? 'Willkommen beim Studienkolleg Aachen! Wie kann ich Ihnen helfen?'
    : isStaff
      ? `Hey ${user.full_name ? user.full_name.split(' ')[0] : ''}! Was kann ich fuer dich tun?`
      : isPartner
        ? `Guten Tag${user.full_name ? ` ${user.full_name.split(' ')[0]}` : ''}! Wie kann ich Ihnen als Partner weiterhelfen?`
        : `Hallo${user.full_name ? ` ${user.full_name.split(' ')[0]}` : ''}! Wie kann ich Ihnen bei Ihrer Bewerbung helfen?`;

  useEffect(() => {
    if (open && messages.length === 0) {
      setMessages([{ role: 'assistant', content: greeting }]);
    }
  }, [open, greeting, messages.length]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput('');
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    try {
      const res = await apiClient.post('/api/support/chat', {
        message: text,
        history: messages.slice(-10),
        language: document.documentElement.lang || 'de',
      }, { withCredentials: true });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.reply }]);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Entschuldigung, ich konnte die Anfrage nicht verarbeiten. Bitte versuche es erneut.' }]);
    } finally {
      setLoading(false);
    }
  };

  const renderMarkdown = (text) => {
    if (!text) return '';
    const lines = text.split('\n');
    const out = [];
    let tableRows = [];
    let inTable = false;

    for (const line of lines) {
      const t = line.trim();

      // Tabelle
      if (t.startsWith('|') && t.endsWith('|')) {
        if (/^[|\s:\-]+$/.test(t.replace(/[|:\-\s]/g, ''))) continue;
        if (!inTable) { inTable = true; tableRows = []; }
        tableRows.push(t.split('|').slice(1, -1).map(c => c.trim()));
        continue;
      }
      if (inTable) {
        const ths = tableRows[0].map(c => '<th style="text-align:left;padding:4px 8px;border-bottom:2px solid var(--color-primary);font-weight:600;font-size:11px">' + inlineMd(c) + '</th>').join('');
        const trs = tableRows.slice(1).map(r => '<tr>' + r.map(c => '<td style="padding:3px 8px;border-bottom:1px solid var(--color-divider);font-size:12px">' + inlineMd(c) + '</td>').join('') + '</tr>').join('');
        out.push('<table style="width:100%;border-collapse:collapse;margin:6px 0"><thead><tr>' + ths + '</tr></thead><tbody>' + trs + '</tbody></table>');
        inTable = false; tableRows = [];
      }

      if (t.startsWith('### ')) { out.push('<div style="font-weight:700;font-size:13px;margin:8px 0 4px;color:var(--color-primary)">' + inlineMd(t.slice(4)) + '</div>'); continue; }
      if (t.startsWith('## ')) { out.push('<div style="font-weight:700;font-size:14px;margin:10px 0 4px;color:var(--color-primary)">' + inlineMd(t.slice(3)) + '</div>'); continue; }
      if (t.startsWith('# ')) { out.push('<div style="font-weight:700;font-size:14px;margin:10px 0 4px;color:var(--color-primary)">' + inlineMd(t.slice(2)) + '</div>'); continue; }
      if (/^-{3,}$/.test(t)) { out.push('<hr style="border:none;border-top:1px solid var(--color-divider);margin:8px 0"/>'); continue; }
      if (/^[-*]\s/.test(t)) { out.push('<li style="margin-left:16px;list-style:disc;font-size:13px">' + inlineMd(t.replace(/^[-*]\s+/, '')) + '</li>'); continue; }
      if (/^\d+\.\s/.test(t)) { out.push('<li style="margin-left:16px;list-style:decimal;font-size:13px">' + inlineMd(t.replace(/^\d+\.\s+/, '')) + '</li>'); continue; }
      if (!t) { out.push('<br/>'); continue; }
      out.push('<p style="margin:2px 0">' + inlineMd(t) + '</p>');
    }
    if (inTable && tableRows.length) {
      const ths = tableRows[0].map(c => '<th style="text-align:left;padding:4px 8px;border-bottom:2px solid var(--color-primary);font-weight:600;font-size:11px">' + inlineMd(c) + '</th>').join('');
      const trs = tableRows.slice(1).map(r => '<tr>' + r.map(c => '<td style="padding:3px 8px;border-bottom:1px solid var(--color-divider);font-size:12px">' + inlineMd(c) + '</td>').join('') + '</tr>').join('');
      out.push('<table style="width:100%;border-collapse:collapse;margin:6px 0"><thead><tr>' + ths + '</tr></thead><tbody>' + trs + '</tbody></table>');
    }
    return out.join('\n');
  };

  const inlineMd = (t) => {
    if (!t) return '';
    return t
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*([^*]+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code style="background:var(--color-surface-sunken);padding:1px 5px;border-radius:3px;font-size:12px">$1</code>');
  };

  /* Mobile-Offset: Chat-Button/Panel ueber der Bottom-Navigation positionieren */
  const mobileBottom = 'max(1.25rem, env(safe-area-inset-bottom, 0px) + 80px)';
  const desktopBottom = '1.25rem';

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} data-testid="support-chat-trigger"
        className="fixed right-5 z-[60] w-14 h-14 bg-[var(--color-accent)] text-[var(--color-primary-dark)] flex items-center justify-center shadow-lg hover:shadow-xl transition-all hover:scale-105"
        style={{ borderRadius: 'var(--radius-full)', bottom: desktopBottom }}
        title="Support-Chat">
        <style>{`@media (max-width:1023px){[data-testid="support-chat-trigger"]{bottom:${mobileBottom} !important}}`}</style>
        <MessageCircle size={24} />
      </button>
    );
  }

  if (minimized) {
    return (
      <div className="fixed right-5 z-[60] flex items-center gap-2" style={{ bottom: desktopBottom }}>
        <style>{`@media (max-width:1023px){[data-testid="support-chat-expand"]{bottom:${mobileBottom} !important}}`}</style>
        <button onClick={() => setMinimized(false)} data-testid="support-chat-expand"
          className="flex items-center gap-2 bg-[var(--color-accent)] text-[var(--color-primary-dark)] px-4 py-3 shadow-lg hover:shadow-xl transition-all font-semibold text-sm"
          style={{ borderRadius: 'var(--radius-full)' }}>
          <MessageCircle size={18} /> Chat
          {messages.length > 1 && <span className="bg-white/30 px-1.5 py-0.5 text-[10px] font-bold" style={{ borderRadius: 'var(--radius-full)' }}>{messages.length}</span>}
        </button>
        <button onClick={() => { setOpen(false); setMinimized(false); }} data-testid="support-chat-close-min"
          className="w-8 h-8 flex items-center justify-center bg-[var(--color-surface)] border border-[var(--color-divider)] text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)] transition-colors"
          style={{ borderRadius: 'var(--radius-full)' }}>
          <X size={14} />
        </button>
      </div>
    );
  }

  return (
    <div className="fixed right-5 z-[60] flex flex-col bg-[var(--color-surface)] border border-[var(--color-divider)] overflow-hidden"
      style={{ width: '380px', maxWidth: 'calc(100vw - 32px)', height: '520px', maxHeight: 'calc(100vh - 100px)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-e4)', bottom: desktopBottom }}
      data-testid="support-chat-panel">
      <style>{`@media (max-width:1023px){[data-testid="support-chat-panel"]{bottom:${mobileBottom} !important;height:420px !important}}`}</style>

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-[var(--color-primary)] text-white shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-[var(--color-accent)] flex items-center justify-center text-[var(--color-primary-dark)] font-bold text-sm" style={{ borderRadius: 'var(--radius-sm)', fontFamily: 'var(--font-heading)' }}>
            W2G
          </div>
          <div>
            <p className="text-sm font-bold">W2G Assistent</p>
            <p className="text-[10px] opacity-80">
              {!user ? 'Studienberatung' : user.role === 'applicant' ? 'Bewerber-Support' : ['agency_admin','agency_agent','affiliate'].includes(user.role) ? 'Partner-Support' : ['staff','admin','superadmin','accounting_staff','teacher'].includes(user.role) ? 'Team-Assistent' : 'Studienberatung'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => setMinimized(true)} data-testid="support-chat-minimize"
            className="p-1.5 hover:bg-white/20 transition-colors" style={{ borderRadius: 'var(--radius-xs)' }}>
            <Minus size={14} />
          </button>
          <button onClick={() => { setOpen(false); setMinimized(false); }} data-testid="support-chat-close"
            className="p-1.5 hover:bg-white/20 transition-colors" style={{ borderRadius: 'var(--radius-xs)' }}>
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3" data-testid="support-chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-7 h-7 flex items-center justify-center shrink-0 text-[10px] font-bold ${msg.role === 'user' ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--color-accent)] text-[var(--color-primary-dark)]'}`}
              style={{ borderRadius: 'var(--radius-sm)', fontFamily: 'var(--font-heading)' }}>
              {msg.role === 'user' ? <User size={13} /> : 'KI'}
            </div>
            <div className={`max-w-[80%] px-3.5 py-2.5 text-[13px] leading-relaxed ${
              msg.role === 'user'
                ? 'bg-[var(--color-primary)] text-white'
                : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-primary)]'
            }`} style={{ borderRadius: msg.role === 'user' ? 'var(--radius-md) var(--radius-xs) var(--radius-md) var(--radius-md)' : 'var(--radius-xs) var(--radius-md) var(--radius-md) var(--radius-md)' }}>
              {msg.role === 'assistant'
                ? <div dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                : msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-2.5">
            <div className="w-7 h-7 flex items-center justify-center bg-[var(--color-accent)] shrink-0 text-[10px] font-bold text-[var(--color-primary-dark)]" style={{ borderRadius: 'var(--radius-sm)', fontFamily: 'var(--font-heading)' }}>
              KI
            </div>
            <div className="bg-[var(--color-surface-sunken)] px-4 py-3 flex items-center gap-1" style={{ borderRadius: 'var(--radius-xs) var(--radius-md) var(--radius-md) var(--radius-md)' }}>
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-text-tertiary)] animate-bounce" style={{ animationDelay: '0ms', animationDuration: '0.6s' }} />
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-text-tertiary)] animate-bounce" style={{ animationDelay: '150ms', animationDuration: '0.6s' }} />
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-text-tertiary)] animate-bounce" style={{ animationDelay: '300ms', animationDuration: '0.6s' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-[var(--color-divider)] p-3 shrink-0">
        <div className="flex items-center gap-2">
          <input ref={inputRef} value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder="Nachricht schreiben..."
            className="w2g-input flex-1 text-sm"
            data-testid="support-chat-input"
            disabled={loading} />
          <button onClick={sendMessage} disabled={!input.trim() || loading}
            data-testid="support-chat-send"
            className="w2g-btn-primary w-10 h-10 p-0 shrink-0"
            style={{ borderRadius: 'var(--radius-sm)', minHeight: 'auto' }}>
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
