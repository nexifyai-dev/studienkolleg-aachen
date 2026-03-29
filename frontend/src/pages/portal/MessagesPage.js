import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { MessageSquare, Send } from 'lucide-react';
import { formatDate } from '../../lib/utils';
import { useAuth } from '../../contexts/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;

export default function MessagesPage() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMsg, setNewMsg] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/api/conversations`, { withCredentials: true })
      .then(r => { setConversations(r.data); if (r.data[0]) setActiveConv(r.data[0]); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!activeConv) return;
    axios.get(`${API}/api/conversations/${activeConv.id}/messages`, { withCredentials: true })
      .then(r => setMessages(r.data))
      .catch(() => {});
  }, [activeConv]);

  const sendMessage = async e => {
    e.preventDefault();
    if (!newMsg.trim()) return;
    setSending(true);
    try {
      const res = await axios.post(`${API}/api/messages`,
        { conversation_id: activeConv?.id, content: newMsg },
        { withCredentials: true }
      );
      setMessages(p => [...p, res.data]);
      setNewMsg('');
      if (!activeConv) {
        const convs = await axios.get(`${API}/api/conversations`, { withCredentials: true });
        setConversations(convs.data);
        setActiveConv(convs.data[0]);
      }
    } catch {}
    finally { setSending(false); }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;

  return (
    <div className="space-y-4 animate-fade-in" data-testid="messages-page">
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">Nachrichten</h1>
        <p className="text-slate-500 text-sm mt-1">Direkter Kontakt mit dem Team</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-sm overflow-hidden" style={{minHeight: '400px'}}>
        {/* Messages */}
        <div className="p-4 h-64 overflow-y-auto space-y-3" data-testid="messages-list">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <MessageSquare size={32} className="mb-2" />
              <p className="text-sm">Noch keine Nachrichten</p>
            </div>
          ) : (
            messages.map(msg => {
              const isOwn = msg.sender_id === user?.id;
              return (
                <div key={msg.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                  data-testid="message-item">
                  <div className={`max-w-xs rounded-sm px-4 py-2.5 text-sm ${
                    isOwn ? 'bg-primary text-white' : 'bg-slate-100 text-slate-800'
                  }`}>
                    <p>{msg.content}</p>
                    <p className={`text-xs mt-1 ${isOwn ? 'text-blue-200' : 'text-slate-400'}`}>
                      {formatDate(msg.sent_at)}
                    </p>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Input */}
        <div className="border-t border-slate-100 p-3">
          <form onSubmit={sendMessage} className="flex gap-2" data-testid="message-form">
            <input value={newMsg} onChange={e => setNewMsg(e.target.value)}
              placeholder="Nachricht schreiben…" data-testid="message-input"
              className="flex-1 border border-slate-200 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-primary" />
            <button type="submit" disabled={sending || !newMsg.trim()} data-testid="message-send-btn"
              className="bg-primary text-white px-4 py-2 rounded-sm hover:bg-primary-hover disabled:opacity-60 transition-colors">
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
