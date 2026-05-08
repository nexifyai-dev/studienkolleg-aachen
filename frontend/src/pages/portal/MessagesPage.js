import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { MessageSquare, Send, Loader2, Paperclip, FileText, Download, X, Clock, HelpCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { CHAT_QUICK_TOPICS } from '../../lib/portalKnowledge';
import { STAGE_LABELS } from '../../lib/utils';
import { Card, CardContent } from '../../components/ui/card';
import { API } from '../../lib/apiBase';

const MAX_FILE_MB = 10;

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function MessageBubble({ msg, isOwn }) {
  const hasAttachment = msg.attachment && msg.attachment.filename;
  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`} data-testid="message-item">
      <div className={isOwn ? 'w2g-chat-own' : 'w2g-chat-other'}>
        {!isOwn && msg.sender_name && (
          <p className="text-[10px] font-semibold mb-1" style={{ color: 'var(--color-primary)' }}>{msg.sender_name}</p>
        )}
        {hasAttachment ? (
          <div className={`flex items-center gap-2 p-2 rounded-[var(--radius-xs)] ${isOwn ? 'bg-white/10' : 'bg-white border border-[var(--color-divider-subtle)]'} mb-1`}>
            <FileText size={16} className={isOwn ? 'text-white/70' : 'text-primary'} />
            <div className="flex-1 min-w-0">
              <p className={`text-xs font-medium truncate ${isOwn ? 'text-white' : 'text-[var(--color-text-primary)]'}`}>{msg.attachment.filename}</p>
              {msg.attachment.file_size && (
                <p className={`text-[10px] ${isOwn ? 'text-white/50' : 'text-[var(--color-text-tertiary)]'}`}>
                  {(msg.attachment.file_size / 1024).toFixed(0)} KB
                </p>
              )}
            </div>
            <a href={`${API}/api/messages/${msg.id}/attachment`}
              target="_blank" rel="noreferrer"
              data-testid={`download-attachment-${msg.id}`}
              className={`shrink-0 ${isOwn ? 'text-white/70 hover:text-white' : 'text-primary hover:text-primary/70'}`}>
              <Download size={14} />
            </a>
          </div>
        ) : null}
        {msg.content && !msg.content.startsWith('[Datei:') && <p>{msg.content}</p>}
        <p className={`text-[10px] mt-1 ${isOwn ? 'text-white/50' : 'text-[var(--color-text-tertiary)]'}`}>
          {msg.sent_at ? new Date(msg.sent_at).toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) : ''}
        </p>
      </div>
    </div>
  );
}

export default function MessagesPage() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMsg, setNewMsg] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMsgs, setLoadingMsgs] = useState(false);
  const [attachFile, setAttachFile] = useState(null);
  const [currentStage, setCurrentStage] = useState(null);
  const [showTopics, setShowTopics] = useState(true);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const pollRef = useRef(null);
  const lang = i18n.language === 'en' ? 'en' : 'de';

  const initConversation = useCallback(async () => {
    try {
      const [supportRes, appsRes] = await Promise.all([
        apiClient.get('/api/conversations/support', { withCredentials: true }),
        apiClient.get('/api/applications', { withCredentials: true }).catch(() => ({ data: [] })),
      ]);
      const supportConv = supportRes.data;
      if (appsRes.data?.[0]) setCurrentStage(appsRes.data[0].current_stage);
      const convsRes = await apiClient.get('/api/conversations', { withCredentials: true });
      const convsData = convsRes.data;
      const convs = convsData.conversations || convsData || [];
      setConversations(convs);
      const found = convs.find(c => c.id === supportConv?.id);
      setActiveConv(found || convs[0] || supportConv);
    } catch {
      try {
        const convsRes = await apiClient.get('/api/conversations', { withCredentials: true });
        const convsData = convsRes.data;
        const convsList = convsData.conversations || convsData || [];
        setConversations(convsList);
        if (convsList[0]) setActiveConv(convsList[0]);
      } catch {}
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { initConversation(); }, [initConversation]);

  const loadMessages = useCallback(async (convId) => {
    if (!convId) return;
    setLoadingMsgs(true);
    try {
      const r = await apiClient.get(`/api/conversations/${convId}/messages`, { withCredentials: true });
      setMessages(r.data || []);
    } catch {} finally { setLoadingMsgs(false); }
  }, []);

  useEffect(() => {
    if (!activeConv?.id) return;
    loadMessages(activeConv.id);
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(() => loadMessages(activeConv.id), 3000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [activeConv?.id, loadMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if ((!newMsg.trim() && !attachFile)) return;
    setSending(true);
    try {
      if (attachFile && activeConv?.id) {
        const b64 = await fileToBase64(attachFile);
        const res = await apiClient.post(`/api/conversations/${activeConv.id}/attachments`, {
          filename: attachFile.name,
          content_type: attachFile.type || 'application/octet-stream',
          file_data: b64,
          content: newMsg || '',
        }, { withCredentials: true });
        setMessages(p => [...p, res.data]);
        setAttachFile(null);
        setNewMsg('');
      } else {
        const payload = { content: newMsg };
        if (activeConv?.id) payload.conversation_id = activeConv.id;
        const res = await apiClient.post('/api/messages', payload, { withCredentials: true });
        setMessages(p => [...p, res.data]);
        setNewMsg('');
        if (!activeConv?.id) await initConversation();
      }
    } catch {} finally { setSending(false); }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > MAX_FILE_MB * 1024 * 1024) {
      alert(t('portal.file_too_large', { max: MAX_FILE_MB }));
      return;
    }
    setAttachFile(file);
  };

  if (loading) return (
    <div className="w2g-loading">
      <div className="w2g-spinner"></div>
    </div>
  );

  const staffName = activeConv
    ? Object.entries(activeConv.participant_names || {})
        .filter(([id]) => id !== user?.id)
        .map(([, n]) => n).join(', ') || 'Team Studienkolleg'
    : 'Team Studienkolleg';

  return (
    <div className="flex flex-col animate-fade-in space-y-3" style={{ height: 'calc(100vh - 120px)' }} data-testid="messages-page">
      <Card style={{ borderLeft: '4px solid var(--color-primary)' }} data-testid="page-header-card">
        <CardContent className="py-3.5 px-5">
          <div className="min-w-0">
            <h1 className="text-lg font-bold tracking-tight" style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}>
              {lang === 'de' ? 'Nachrichten' : 'Messages'}
            </h1>
            <p className="text-[11px] text-[var(--color-text-secondary)] mt-0.5 leading-relaxed">
              {lang === 'de' ? 'Direkte Kommunikation mit deinem Team' : 'Direct communication with your team'}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="overflow-hidden flex flex-col flex-1 min-h-0 p-0">
        {/* Context Header */}
        <div className="px-4 py-3 border-b border-[var(--color-divider-subtle)] bg-[var(--color-surface-elevated)] shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-primary-muted flex items-center justify-center">
                <MessageSquare size={14} className="text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-[var(--color-text-primary)]">{staffName}</p>
                <p className="text-[10px] text-[var(--color-text-tertiary)]">
                  {lang === 'de' ? 'Support-Kanal' : 'Support Channel'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {currentStage && (
                <span className="text-[10px] text-[var(--color-text-tertiary)] bg-[var(--color-surface-sunken)] px-2 py-1 rounded-sm">
                  Status: {STAGE_LABELS[currentStage] || currentStage}
                </span>
              )}
              <div className="flex items-center gap-1 text-[10px] text-[var(--color-text-tertiary)]">
                <Clock size={10} />
                <span>{lang === 'de' ? 'Antwort: ~24 Std.' : 'Reply: ~24 hrs'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Topics (shown when no messages or toggle) */}
        {showTopics && messages.length === 0 && (
          <div className="px-4 py-3 border-b border-[var(--color-divider-subtle)] bg-primary/[0.02] shrink-0" data-testid="chat-quick-topics">
            <p className="text-[10px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-wide mb-2">
              {lang === 'de' ? 'Schnellzugriff – Wobei koennen wir helfen?' : 'Quick Access – How can we help?'}
            </p>
            <div className="flex flex-wrap gap-1.5">
              {(CHAT_QUICK_TOPICS[lang] || CHAT_QUICK_TOPICS.de).map(topic => (
                <button key={topic.key}
                  onClick={() => { setNewMsg(topic.question); setShowTopics(false); }}
                  className="text-xs px-2.5 py-1.5 bg-white border border-[var(--color-divider)] rounded-sm text-[var(--color-text-secondary)] hover:border-primary/30 hover:text-primary transition-colors flex items-center gap-1"
                  data-testid={`topic-${topic.key}`}>
                  <HelpCircle size={10} />
                  {topic.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages area - flex-1 to fill remaining space */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0" data-testid="messages-list">
          {loadingMsgs && messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 size={20} className="animate-spin text-[var(--color-text-tertiary)]" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-[var(--color-text-tertiary)]">
              <MessageSquare size={32} className="mb-2" />
              <p className="text-sm">{t('portal.no_messages')}</p>
              <p className="text-xs mt-1">{t('portal.first_message_hint')}</p>
            </div>
          ) : (
            messages.map(msg => (
              <MessageBubble key={msg.id} msg={msg} isOwn={msg.sender_id === user?.id} />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Attachment Preview */}
        {attachFile && (
          <div className="px-3 py-2 border-t border-[var(--color-divider-subtle)] flex items-center gap-2 bg-[var(--color-surface-elevated)] shrink-0" data-testid="attachment-preview">
            <FileText size={14} className="text-primary" />
            <span className="text-xs text-[var(--color-text-primary)] truncate flex-1">{attachFile.name} ({(attachFile.size / 1024).toFixed(0)} KB)</span>
            <button onClick={() => setAttachFile(null)} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]"><X size={14} /></button>
          </div>
        )}

        {/* Input area - anchored at bottom */}
        <div className="border-t border-[var(--color-divider-subtle)] p-3 shrink-0">
          <form onSubmit={sendMessage} className="flex gap-2" data-testid="message-form">
            <button type="button" onClick={() => fileInputRef.current?.click()}
              data-testid="message-attach-btn"
              className="text-[var(--color-text-tertiary)] hover:text-primary transition-colors px-2 py-2">
              <Paperclip size={18} />
            </button>
            <input ref={fileInputRef} type="file" className="hidden" onChange={handleFileSelect}
              accept=".pdf,.jpg,.jpeg,.png,.webp,.doc,.docx" />
            <input
              value={newMsg}
              onChange={e => setNewMsg(e.target.value)}
              placeholder={t('portal.write_message')}
              data-testid="message-input"
              className="w2g-input flex-1"
            />
            <button type="submit" disabled={sending || (!newMsg.trim() && !attachFile)}
              data-testid="message-send-btn"
              className="w2g-btn-primary px-4">
              <Send size={16} />
            </button>
          </form>
        </div>
      </Card>
    </div>
  );
}
