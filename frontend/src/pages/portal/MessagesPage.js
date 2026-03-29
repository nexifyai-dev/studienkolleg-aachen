import React, { useEffect, useState, useRef, useCallback } from 'react';
import apiClient from '../../lib/apiClient';
import { MessageSquare, Send, Loader2 } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export default function MessagesPage() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMsg, setNewMsg] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMsgs, setLoadingMsgs] = useState(false);
  const messagesEndRef = useRef(null);
  const pollRef = useRef(null);

  const initConversation = useCallback(async () => {
    try {
      // Ensure a support conversation exists
      const supportRes = await apiClient.get('/api/conversations/support', { withCredentials: true });
      const supportConv = supportRes.data;

      // Load all conversations
      const convsRes = await apiClient.get('/api/conversations', { withCredentials: true });
      const convs = convsRes.data || [];
      setConversations(convs);

      // Set active conversation: prefer support, fallback to first
      const found = convs.find(c => c.id === supportConv?.id);
      setActiveConv(found || convs[0] || supportConv);
    } catch {
      // Fallback: just try to load conversations
      try {
        const convsRes = await apiClient.get('/api/conversations', { withCredentials: true });
        setConversations(convsRes.data || []);
        if (convsRes.data?.[0]) setActiveConv(convsRes.data[0]);
      } catch {}
    } finally {
      setLoading(false);
    }
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
    if (!newMsg.trim()) return;
    setSending(true);
    try {
      const payload = { content: newMsg };
      if (activeConv?.id) {
        payload.conversation_id = activeConv.id;
      }
      const res = await apiClient.post('/api/messages', payload, { withCredentials: true });
      setMessages(p => [...p, res.data]);
      setNewMsg('');

      // Reload conversations to update previews
      if (!activeConv?.id) {
        await initConversation();
      }
    } catch {} finally { setSending(false); }
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
    <div className="space-y-4 animate-fade-in" data-testid="messages-page">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">Nachrichten</h1>
        <p className="text-slate-500 text-sm mt-1">Direkter Kontakt mit dem Team</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm overflow-hidden" style={{ minHeight: '400px' }}>
        {/* Header */}
        <div className="px-4 py-3 border-b border-slate-100 bg-slate-50/50 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <MessageSquare size={14} className="text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-800">{staffName}</p>
            <p className="text-[10px] text-slate-400">Support-Kanal</p>
          </div>
        </div>

        {/* Messages */}
        <div className="p-4 overflow-y-auto space-y-3" style={{ height: '320px' }} data-testid="messages-list">
          {loadingMsgs && messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 size={20} className="animate-spin text-slate-400" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <MessageSquare size={32} className="mb-2" />
              <p className="text-sm">Noch keine Nachrichten</p>
              <p className="text-xs mt-1">Schreibe deine erste Nachricht an das Team</p>
            </div>
          ) : (
            messages.map(msg => {
              const isOwn = msg.sender_id === user?.id;
              return (
                <div key={msg.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`} data-testid="message-item">
                  <div className={`max-w-xs sm:max-w-sm rounded-sm px-4 py-2.5 text-sm ${
                    isOwn ? 'bg-primary text-white' : 'bg-slate-100 text-slate-800'
                  }`}>
                    {!isOwn && msg.sender_name && (
                      <p className="text-[10px] font-medium text-primary mb-1">{msg.sender_name}</p>
                    )}
                    <p>{msg.content}</p>
                    <p className={`text-[10px] mt-1 ${isOwn ? 'text-white/50' : 'text-slate-400'}`}>
                      {msg.sent_at ? new Date(msg.sent_at).toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) : ''}
                    </p>
                  </div>
                </div>
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-slate-100 p-3">
          <form onSubmit={sendMessage} className="flex gap-2" data-testid="message-form">
            <input
              value={newMsg}
              onChange={e => setNewMsg(e.target.value)}
              placeholder="Nachricht schreiben..."
              data-testid="message-input"
              className="flex-1 border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary"
            />
            <button
              type="submit"
              disabled={sending || !newMsg.trim()}
              data-testid="message-send-btn"
              className="bg-primary text-white px-4 py-2 rounded-sm hover:bg-primary/90 disabled:opacity-60 transition-colors"
            >
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
