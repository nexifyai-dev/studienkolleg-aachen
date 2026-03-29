import React, { useEffect, useState, useCallback, useRef } from 'react';
import apiClient from '../../lib/apiClient';
import { useAuth } from '../../contexts/AuthContext';
import { formatDate } from '../../lib/utils';
import {
  MessageSquare, Send, Users, Search, ArrowLeft, Loader2
} from 'lucide-react';

function ConversationItem({ conv, active, onClick, currentUserId }) {
  const otherNames = Object.entries(conv.participant_names || {})
    .filter(([id]) => id !== currentUserId)
    .map(([, name]) => name);
  const displayName = otherNames.length > 0 ? otherNames.join(', ') : 'Konversation';
  const otherRoles = Object.entries(conv.participant_roles || {})
    .filter(([id]) => id !== currentUserId)
    .map(([, role]) => role);
  const roleLabel = otherRoles[0] || '';

  return (
    <button
      onClick={onClick}
      data-testid={`conv-item-${conv.id}`}
      className={`w-full text-left px-4 py-3 border-b border-slate-100 hover:bg-slate-50 transition-colors ${active ? 'bg-primary/5 border-l-2 border-l-primary' : ''}`}
    >
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
          <span className="text-xs font-bold text-primary">{displayName[0]?.toUpperCase() || '?'}</span>
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium text-slate-800 truncate">{displayName}</p>
            <span className="text-[10px] text-slate-400 shrink-0">
              {conv.last_message_at ? formatDate(conv.last_message_at) : ''}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {roleLabel && <span className="text-[10px] text-primary/70 bg-primary/5 px-1.5 py-0.5 rounded">{roleLabel}</span>}
            {conv.last_message_preview && (
              <p className="text-xs text-slate-400 truncate">{conv.last_message_preview}</p>
            )}
          </div>
        </div>
      </div>
    </button>
  );
}

export default function StaffMessagingPage() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMsg, setNewMsg] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMsgs, setLoadingMsgs] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showList, setShowList] = useState(true);
  const messagesEndRef = useRef(null);
  const pollRef = useRef(null);

  const loadConversations = useCallback(async () => {
    try {
      const r = await apiClient.get('/api/conversations', { withCredentials: true });
      setConversations(r.data || []);
    } catch {}
  }, []);

  useEffect(() => {
    loadConversations().finally(() => setLoading(false));
  }, [loadConversations]);

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

  const selectConv = (conv) => {
    setActiveConv(conv);
    setShowList(false);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMsg.trim() || !activeConv?.id) return;
    setSending(true);
    try {
      const res = await apiClient.post('/api/messages',
        { conversation_id: activeConv.id, content: newMsg },
        { withCredentials: true }
      );
      setMessages(p => [...p, res.data]);
      setNewMsg('');
      loadConversations();
    } catch {} finally { setSending(false); }
  };

  const filtered = searchTerm
    ? conversations.filter(c => {
        const names = Object.values(c.participant_names || {}).join(' ').toLowerCase();
        return names.includes(searchTerm.toLowerCase());
      })
    : conversations;

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={24} className="animate-spin text-primary" />
    </div>
  );

  const otherName = activeConv
    ? Object.entries(activeConv.participant_names || {})
        .filter(([id]) => id !== user?.id)
        .map(([, n]) => n).join(', ') || 'Konversation'
    : '';

  return (
    <div className="animate-fade-in" data-testid="staff-messaging-page">
      <div className="mb-4">
        <h1 className="text-xl font-heading font-bold text-primary">Nachrichten</h1>
        <p className="text-slate-500 text-sm">In-App Kommunikation mit Bewerbern</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm overflow-hidden flex" style={{ height: 'calc(100vh - 200px)', minHeight: '400px' }}>
        {/* Conversation List */}
        <div className={`w-full md:w-80 border-r border-slate-200 flex flex-col shrink-0 ${!showList && activeConv ? 'hidden md:flex' : 'flex'}`}>
          <div className="p-3 border-b border-slate-100">
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                placeholder="Suchen..."
                data-testid="conv-search"
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-sm focus:outline-none focus:border-primary"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-slate-400 p-6">
                <MessageSquare size={28} className="mb-2" />
                <p className="text-sm">Keine Konversationen</p>
              </div>
            ) : (
              filtered.map(c => (
                <ConversationItem
                  key={c.id}
                  conv={c}
                  active={activeConv?.id === c.id}
                  onClick={() => selectConv(c)}
                  currentUserId={user?.id}
                />
              ))
            )}
          </div>
        </div>

        {/* Message Area */}
        <div className={`flex-1 flex flex-col ${showList && !activeConv ? 'hidden md:flex' : 'flex'}`}>
          {activeConv ? (
            <>
              {/* Chat Header */}
              <div className="px-4 py-3 border-b border-slate-100 flex items-center gap-3 bg-slate-50/50">
                <button onClick={() => setShowList(true)} className="md:hidden text-slate-400 hover:text-primary">
                  <ArrowLeft size={18} />
                </button>
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-xs font-bold text-primary">{otherName[0]?.toUpperCase() || '?'}</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-800">{otherName}</p>
                  <p className="text-[10px] text-slate-400">{activeConv.participants?.length || 0} Teilnehmer</p>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3" data-testid="staff-messages-list">
                {loadingMsgs && messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <Loader2 size={20} className="animate-spin text-slate-400" />
                  </div>
                ) : messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-slate-400">
                    <MessageSquare size={28} className="mb-2" />
                    <p className="text-sm">Noch keine Nachrichten</p>
                  </div>
                ) : (
                  messages.map(msg => {
                    const isOwn = msg.sender_id === user?.id;
                    return (
                      <div key={msg.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`} data-testid="staff-message-item">
                        <div className={`max-w-sm rounded-sm px-4 py-2.5 text-sm ${isOwn ? 'bg-primary text-white' : 'bg-slate-100 text-slate-800'}`}>
                          {!isOwn && msg.sender_name && (
                            <p className={`text-[10px] font-medium mb-1 ${isOwn ? 'text-white/70' : 'text-primary'}`}>{msg.sender_name}</p>
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
                <form onSubmit={sendMessage} className="flex gap-2" data-testid="staff-message-form">
                  <input
                    value={newMsg}
                    onChange={e => setNewMsg(e.target.value)}
                    placeholder="Nachricht schreiben..."
                    data-testid="staff-message-input"
                    className="flex-1 border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary"
                  />
                  <button
                    type="submit"
                    disabled={sending || !newMsg.trim()}
                    data-testid="staff-message-send"
                    className="bg-primary text-white px-4 py-2 rounded-sm hover:bg-primary/90 disabled:opacity-60 transition-colors"
                  >
                    <Send size={16} />
                  </button>
                </form>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <Users size={32} className="mb-3" />
              <p className="text-sm font-medium">Konversation auswählen</p>
              <p className="text-xs mt-1">Wähle links eine Konversation aus</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
