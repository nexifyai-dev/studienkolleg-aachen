import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import apiClient from '../../lib/apiClient';
import { MessageSquare, Send, Loader2, Paperclip, FileText, Download, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;
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
      <div className={`max-w-xs sm:max-w-sm rounded-sm px-4 py-2.5 text-sm ${
        isOwn ? 'bg-primary text-white' : 'bg-slate-100 text-slate-800'
      }`}>
        {!isOwn && msg.sender_name && (
          <p className="text-[10px] font-medium text-primary mb-1">{msg.sender_name}</p>
        )}
        {hasAttachment ? (
          <div className={`flex items-center gap-2 p-2 rounded ${isOwn ? 'bg-white/10' : 'bg-white'} mb-1`}>
            <FileText size={16} className={isOwn ? 'text-white/70' : 'text-primary'} />
            <div className="flex-1 min-w-0">
              <p className={`text-xs font-medium truncate ${isOwn ? 'text-white' : 'text-slate-700'}`}>{msg.attachment.filename}</p>
              {msg.attachment.file_size && (
                <p className={`text-[10px] ${isOwn ? 'text-white/50' : 'text-slate-400'}`}>
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
        <p className={`text-[10px] mt-1 ${isOwn ? 'text-white/50' : 'text-slate-400'}`}>
          {msg.sent_at ? new Date(msg.sent_at).toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) : ''}
        </p>
      </div>
    </div>
  );
}

export default function MessagesPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMsg, setNewMsg] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMsgs, setLoadingMsgs] = useState(false);
  const [attachFile, setAttachFile] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const pollRef = useRef(null);

  const initConversation = useCallback(async () => {
    try {
      const supportRes = await apiClient.get('/api/conversations/support', { withCredentials: true });
      const supportConv = supportRes.data;
      const convsRes = await apiClient.get('/api/conversations', { withCredentials: true });
      const convs = convsRes.data || [];
      const found = convs.find(c => c.id === supportConv?.id);
      setActiveConv(found || convs[0] || supportConv);
    } catch {
      try {
        const convsRes = await apiClient.get('/api/conversations', { withCredentials: true });
        if (convsRes.data?.[0]) setActiveConv(convsRes.data[0]);
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
    pollRef.current = setInterval(() => loadMessages(activeConv.id), 8000);
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
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-primary" />
    </div>
  );

  const staffName = activeConv
    ? Object.entries(activeConv.participant_names || {})
        .filter(([id]) => id !== user?.id)
        .map(([, n]) => n).join(', ') || 'Team Studienkolleg'
    : 'Team Studienkolleg';

  return (
    <div className="flex flex-col animate-fade-in" style={{ height: 'calc(100vh - 120px)' }} data-testid="messages-page">
      <div className="mb-3">
        <h1 className="text-xl font-heading font-bold text-primary">{t('portal.messages')}</h1>
        <p className="text-slate-500 text-sm mt-0.5">{t('portal.direct_team_contact')}</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm overflow-hidden flex flex-col flex-1 min-h-0">
        {/* Chat header */}
        <div className="px-4 py-3 border-b border-slate-100 bg-slate-50/50 flex items-center gap-3 shrink-0">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <MessageSquare size={14} className="text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-800">{staffName}</p>
            <p className="text-[10px] text-slate-400">{t('portal.support_channel')}</p>
          </div>
        </div>

        {/* Messages area - flex-1 to fill remaining space */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0" data-testid="messages-list">
          {loadingMsgs && messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 size={20} className="animate-spin text-slate-400" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
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
          <div className="px-3 py-2 border-t border-slate-100 flex items-center gap-2 bg-slate-50 shrink-0" data-testid="attachment-preview">
            <FileText size={14} className="text-primary" />
            <span className="text-xs text-slate-700 truncate flex-1">{attachFile.name} ({(attachFile.size / 1024).toFixed(0)} KB)</span>
            <button onClick={() => setAttachFile(null)} className="text-slate-400 hover:text-red-500"><X size={14} /></button>
          </div>
        )}

        {/* Input area - anchored at bottom */}
        <div className="border-t border-slate-100 p-3 shrink-0">
          <form onSubmit={sendMessage} className="flex gap-2" data-testid="message-form">
            <button type="button" onClick={() => fileInputRef.current?.click()}
              data-testid="message-attach-btn"
              className="text-slate-400 hover:text-primary transition-colors px-2 py-2">
              <Paperclip size={18} />
            </button>
            <input ref={fileInputRef} type="file" className="hidden" onChange={handleFileSelect}
              accept=".pdf,.jpg,.jpeg,.png,.webp,.doc,.docx" />
            <input
              value={newMsg}
              onChange={e => setNewMsg(e.target.value)}
              placeholder={t('portal.write_message')}
              data-testid="message-input"
              className="flex-1 border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary"
            />
            <button type="submit" disabled={sending || (!newMsg.trim() && !attachFile)}
              data-testid="message-send-btn"
              className="bg-primary text-white px-4 py-2 rounded-sm hover:bg-primary/90 disabled:opacity-60 transition-colors">
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
