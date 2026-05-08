import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../lib/api-hooks';
import { getLang } from '../../lib/utils';
import {
  Send, Loader2, Plus, Trash2, MessageSquare, Activity, FileText,
  Users, AlertTriangle, BarChart3, PanelLeftClose, PanelLeftOpen,
  Sparkles, Clock
} from 'lucide-react';

/* Backstage-Komponenten */
import {
  ContentHeader,
  FullHeightLayout,
  SplitLayout,
  StatusLine,
} from '../../components/layout/BackstageComponents';

/* ─── API Hooks ──────────────────────────────────────────────────── */
function useOracleContext() {
  return useQuery({
    queryKey: ['oracle', 'context'],
    queryFn: () => api.get('/oracle/context').then(r => r.data),
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

function useOracleConversations() {
  return useQuery({
    queryKey: ['oracle', 'conversations'],
    queryFn: () => api.get('/oracle/conversations').then(r => r.data),
  });
}

function useOracleConversation(id) {
  return useQuery({
    queryKey: ['oracle', 'conversations', id],
    queryFn: () => api.get(`/oracle/conversations/${id}`).then(r => r.data),
    enabled: !!id,
  });
}

function useOracleChat() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/oracle/chat', data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['oracle', 'conversations'] });
    },
  });
}

function useDeleteConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(`/oracle/conversations/${id}`).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['oracle', 'conversations'] });
    },
  });
}

/* ─── Hilfsfunktionen ────────────────────────────────────────────── */
function formatTime(ts) {
  if (!ts) return '';
  const d = new Date(ts);
  return d.toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' });
}

/* ─── Markdown-aehnliches Rendering (Strikt CI-konform) ──────────── */
function renderContent(text) {
  if (!text) return null;
  const lines = text.split('\n');
  const elements = [];
  let inTable = false;
  let tableRows = [];

  const flushTable = () => {
    if (tableRows.length > 0) {
      const hasHeader = tableRows.length > 1;
      elements.push(
        <div key={`table-${elements.length}`} className="overflow-x-auto my-3 rounded-[var(--radius-sm)] border border-[var(--color-divider-subtle)]">
          <table>
            {hasHeader && (
              <thead>
                <tr>
                  {tableRows[0].map((cell, ci) => (
                    <th key={ci}>{cell.trim()}</th>
                  ))}
                </tr>
              </thead>
            )}
            <tbody>
              {tableRows.slice(hasHeader ? 1 : 0).map((row, ri) => (
                <tr key={ri}>
                  {row.map((cell, ci) => (
                    <td key={ci}>{cell.trim()}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      tableRows = [];
    }
    inTable = false;
  };

  const processInline = (str) => {
    return str
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`(.*?)`/g, '<code>$1</code>');
  };

  lines.forEach((line, i) => {
    /* Tabellen-Erkennung */
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      const cells = line.split('|').filter(c => c.trim() !== '' && !c.match(/^[\s-:]+$/));
      if (cells.length > 0) {
        if (!line.match(/^\|[\s-:]+\|/)) {
          inTable = true;
          tableRows.push(cells);
        }
      }
      return;
    }
    if (inTable) flushTable();

    /* Ueberschriften */
    if (line.startsWith('#### ')) {
      elements.push(<h4 key={i}>{line.slice(5)}</h4>);
    } else if (line.startsWith('### ')) {
      elements.push(<h4 key={i}>{line.slice(4)}</h4>);
    } else if (line.startsWith('## ')) {
      elements.push(<h3 key={i}>{line.slice(3)}</h3>);
    } else if (line.startsWith('# ')) {
      elements.push(<h2 key={i}>{line.slice(2)}</h2>);
    } else if (line.startsWith('**') && line.endsWith('**')) {
      /* Fettgedruckte Zeile als Mini-Header */
      elements.push(
        <p key={i} className="font-bold mt-2.5 mb-0.5" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-heading)', fontSize: '12px' }}>
          {line.replace(/\*\*/g, '')}
        </p>
      );
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      /* Aufzaehlung */
      elements.push(
        <div key={i} className="flex gap-2 ml-1 py-0.5">
          <span className="mt-[3px] w-1 h-1 rounded-full shrink-0" style={{ background: 'var(--color-accent)' }} />
          <span dangerouslySetInnerHTML={{ __html: processInline(line.slice(2)) }} />
        </div>
      );
    } else if (line.match(/^\d+\.\s/)) {
      /* Nummerierte Liste */
      const num = line.match(/^(\d+)\./)[1];
      elements.push(
        <div key={i} className="flex gap-2 ml-1 py-0.5">
          <span className="font-bold tabular-nums min-w-[16px] text-right shrink-0" style={{ color: 'var(--color-primary)', fontFamily: 'var(--font-heading)' }}>{num}.</span>
          <span dangerouslySetInnerHTML={{ __html: processInline(line.replace(/^\d+\.\s/, '')) }} />
        </div>
      );
    } else if (line.startsWith('---') || line.startsWith('___')) {
      /* Trennlinie */
      elements.push(<hr key={i} className="my-2 border-t border-[var(--color-divider-subtle)]" />);
    } else if (line.startsWith('> ')) {
      /* Zitat/Blockquote */
      elements.push(
        <div key={i} className="border-l-2 pl-3 py-1 my-1 text-[11px] italic" style={{ borderColor: 'var(--color-accent)', color: 'var(--color-text-secondary)' }}>
          <span dangerouslySetInnerHTML={{ __html: processInline(line.slice(2)) }} />
        </div>
      );
    } else if (line.trim() === '') {
      elements.push(<div key={i} className="h-1" />);
    } else {
      elements.push(<p key={i} dangerouslySetInnerHTML={{ __html: processInline(line) }} />);
    }
  });
  if (inTable) flushTable();
  return elements;
}

/* ─── Quick-Commands ─────────────────────────────────────────────── */
const QUICK_COMMANDS = [
  { label: 'Pipeline-Status', query: 'Gib mir eine vollstaendige Pipeline-Uebersicht aller Bewerbungen mit Handlungsempfehlungen.' },
  { label: 'Offene Aufgaben', query: 'Welche Aufgaben sind offen oder ueberfaellig? Priorisiere nach Dringlichkeit.' },
  { label: 'Rechnungsstatus', query: 'Wie ist der aktuelle Rechnungsstatus? Gibt es ueberfaellige oder offene Posten?' },
  { label: 'Tagesbericht', query: 'Erstelle einen kompakten Tagesbericht: Pipeline, offene Tasks, Rechnungen, ausstehende Dokumente. Was muss HEUTE passieren?' },
];

/* ─── Kontext-Karten (InfoCard-basiert) ──────────────────────────── */
function ContextPanel({ context }) {
  if (!context) return null;
  const cards = [
    { icon: Users, label: 'Bewerbungen', value: context.applications?.total || 0, sub: Object.entries(context.applications?.pipeline || {}).slice(0, 2).map(([k, v]) => `${k}: ${v}`).join(', ') },
    { icon: FileText, label: 'Offene Tasks', value: context.tasks?.open || 0, sub: context.tasks?.overdue > 0 ? `${context.tasks.overdue} ueberfaellig` : 'Keine ueberfaellig' },
    { icon: BarChart3, label: 'Rechnungen', value: context.invoices?.total || 0, sub: Object.entries(context.invoices?.by_status || {}).map(([k, v]) => `${k}: ${v.count}`).join(', ') },
    { icon: AlertTriangle, label: 'Docs offen', value: context.documents?.pending_review || 0, sub: `${context.documents?.total || 0} gesamt` },
  ];

  return (
    <div className="p-3 border-b border-[var(--color-divider)] space-y-2" data-testid="oracle-context-cards">
      {cards.map((c, i) => (
        <div
          key={i}
          className="p-2.5 rounded-[var(--radius-sm)] border border-[var(--color-divider-subtle)] bg-[var(--color-surface-elevated)]"
          data-testid={`oracle-context-card-${i}`}
        >
          <div className="flex items-center gap-2 mb-1">
            <div className="w-6 h-6 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center shrink-0">
              <c.icon size={12} className="text-[var(--color-primary)]" />
            </div>
            <span className="text-[10px] font-semibold uppercase tracking-[0.06em] text-[var(--color-text-tertiary)]">{c.label}</span>
          </div>
          <div className="text-lg font-bold text-[var(--color-text-primary)] tabular-nums" style={{ fontFamily: 'var(--font-heading)' }}>{c.value}</div>
          <div className="text-[9px] text-[var(--color-text-tertiary)] mt-0.5 truncate">{c.sub}</div>
        </div>
      ))}
    </div>
  );
}

/* ─── Konversationsliste ─────────────────────────────────────────── */
function ConversationList({ conversations, activeId, onSelect, onNew, onDelete }) {
  return (
    <div className="flex flex-col flex-1 min-h-0" data-testid="oracle-conversation-list">
      <div className="p-2.5 pb-2">
        <button onClick={onNew} className="w2g-btn-primary w2g-btn-sm w-full" data-testid="oracle-new-conversation-btn">
          <Plus size={14} /> Neue Konversation
        </button>
      </div>
      <div className="flex-1 overflow-y-auto px-2.5 pb-2 space-y-0.5">
        {(!conversations || conversations.length === 0) && (
          <p className="text-[10px] text-[var(--color-text-tertiary)] px-2 py-4 text-center">
            Noch keine Konversationen
          </p>
        )}
        {conversations?.map(c => (
          <div key={c.id}
            className={`group flex items-center gap-2 px-2.5 py-2 rounded-[var(--radius-sm)] cursor-pointer text-xs transition-colors
              ${activeId === c.id
                ? 'bg-[var(--color-primary)] text-white font-medium'
                : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-sunken)]'}`}
            onClick={() => onSelect(c.id)} data-testid={`oracle-conv-${c.id}`}>
            <MessageSquare size={12} className="shrink-0" />
            <span className="flex-1 truncate">{c.title}</span>
            <button onClick={(e) => { e.stopPropagation(); onDelete(c.id); }}
              className="opacity-0 group-hover:opacity-100 p-0.5 hover:text-[var(--color-danger)] transition-opacity"
              data-testid={`oracle-delete-conv-${c.id}`}>
              <Trash2 size={11} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Chat-Bereich ───────────────────────────────────────────────── */
function ChatArea({ messages, isLoading, onSend }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = useCallback(() => {
    const msg = input.trim();
    if (!msg || isLoading) return;
    setInput('');
    onSend(msg);
  }, [input, isLoading, onSend]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-0" data-testid="oracle-chat-area">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
        {(!messages || messages.length === 0) && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-14 h-14 rounded-[var(--radius-lg)] bg-[var(--color-primary-muted)] flex items-center justify-center mb-4">
              <Activity size={24} className="text-[var(--color-primary)]" />
            </div>
            <h3 className="text-base font-bold text-[var(--color-primary)] mb-1" style={{ fontFamily: 'var(--font-heading)' }}>Oracle</h3>
            <p className="text-xs text-[var(--color-text-tertiary)] max-w-sm leading-relaxed">
              Zentrale Wissensquelle mit Live-Daten. Stelle Fragen zu Bewerbungen, Aufgaben, Rechnungen oder lass dir einen Tagesbericht erstellen.
            </p>
            <div className="flex flex-wrap gap-2 mt-5 justify-center">
              {QUICK_COMMANDS.map((qc, i) => (
                <button key={i} onClick={() => onSend(qc.query)}
                  className="w2g-btn-outline w2g-btn-xs" data-testid={`oracle-quick-cmd-${i}`}>
                  {qc.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages?.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`} data-testid={`oracle-msg-${i}`}>
            <div className={`max-w-[80%] rounded-[var(--radius-md)] px-4 py-2.5 text-xs leading-relaxed
              ${msg.role === 'user'
                ? 'bg-[var(--color-primary)] text-white'
                : 'bg-[var(--color-surface-elevated)] text-[var(--color-text-primary)] border border-[var(--color-divider-subtle)]'}`}>
              {msg.role === 'user' ? (
                <p>{msg.content}</p>
              ) : (
                <div className="oracle-response">{renderContent(msg.content)}</div>
              )}
              {msg.timestamp && (
                <div className={`text-[9px] mt-1.5 ${msg.role === 'user' ? 'text-white/50' : 'text-[var(--color-text-tertiary)]'}`}>
                  {formatTime(msg.timestamp)}
                  {msg.model && ` \u00B7 ${msg.model}`}
                  {msg.tokens_used > 0 && ` \u00B7 ${msg.tokens_used} tokens`}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start" data-testid="oracle-loading">
            <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider-subtle)] rounded-[var(--radius-md)] px-4 py-2.5 flex items-center gap-2">
              <Loader2 size={14} className="animate-spin text-[var(--color-primary)]" />
              <span className="text-xs text-[var(--color-text-tertiary)]">Oracle denkt nach...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Commands (wenn Nachrichten vorhanden) */}
      {messages && messages.length > 0 && (
        <div className="flex gap-1.5 px-5 pb-2 overflow-x-auto scrollbar-hide">
          {QUICK_COMMANDS.map((qc, i) => (
            <button key={i} onClick={() => onSend(qc.query)} disabled={isLoading}
              className="whitespace-nowrap px-2.5 py-1 text-[10px] font-medium border border-[var(--color-divider)]
                         rounded-[var(--radius-full)] text-[var(--color-text-tertiary)]
                         hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]
                         disabled:opacity-40 transition-colors">
              {qc.label}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="border-t border-[var(--color-divider)] p-4" data-testid="oracle-input-area">
        <div className="flex gap-2">
          <textarea ref={inputRef} value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown} placeholder="Frage an das Oracle stellen..."
            rows={1} className="w2g-textarea flex-1 resize-none min-h-[38px] py-2" data-testid="oracle-chat-input" />
          <button onClick={handleSend} disabled={!input.trim() || isLoading}
            className="w2g-btn-primary px-4" data-testid="oracle-send-btn">
            {isLoading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Haupt-Komponente (Backstage-Architektur) ───────────────────── */
export default function OraclePage() {
  const [activeConvId, setActiveConvId] = useState(null);
  const [localMessages, setLocalMessages] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const { data: context } = useOracleContext();
  const { data: conversations } = useOracleConversations();
  const { data: activeConv } = useOracleConversation(activeConvId);
  const chatMutation = useOracleChat();
  const deleteMutation = useDeleteConversation();

  useEffect(() => {
    if (activeConv?.messages) {
      setLocalMessages(activeConv.messages);
    }
  }, [activeConv]);

  const handleSend = useCallback((message) => {
    const userMsg = { role: 'user', content: message, timestamp: new Date().toISOString() };
    setLocalMessages(prev => [...prev, userMsg]);

    chatMutation.mutate(
      { message, conversation_id: activeConvId },
      {
        onSuccess: (data) => {
          if (!activeConvId && data.conversation_id) {
            setActiveConvId(data.conversation_id);
          }
          const assistantMsg = {
            role: 'assistant',
            content: data.response,
            timestamp: new Date().toISOString(),
            model: data.model,
            tokens_used: data.tokens_used,
          };
          setLocalMessages(prev => [...prev, assistantMsg]);
        },
        onError: () => {
          setLocalMessages(prev => [...prev, {
            role: 'assistant',
            content: 'Fehler bei der Verbindung zum Oracle. Bitte erneut versuchen.',
            timestamp: new Date().toISOString(),
          }]);
        },
      }
    );
  }, [activeConvId, chatMutation]);

  const handleNewConversation = () => {
    setActiveConvId(null);
    setLocalMessages([]);
  };

  const handleSelectConversation = (id) => {
    setActiveConvId(id);
    setLocalMessages([]);
  };

  const handleDeleteConversation = (id) => {
    deleteMutation.mutate(id);
    if (activeConvId === id) handleNewConversation();
  };

  /* Metadata fuer den Header */
  const headerMeta = context ? [
    { icon: Users, label: `${context.applications?.total || 0} Bewerbungen` },
    { icon: FileText, label: `${context.tasks?.open || 0} offene Tasks` },
    { icon: BarChart3, label: `${context.invoices?.total || 0} Rechnungen` },
  ] : [];

  /* StatusLine-Items */
  const statusItems = context ? [
    { icon: Clock, label: 'Letztes Update', value: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }) },
    { icon: Sparkles, label: 'Konversationen', value: conversations?.length || 0 },
    { icon: MessageSquare, label: 'Nachrichten', value: localMessages.length, color: localMessages.length > 0 ? 'var(--color-primary)' : undefined },
  ] : [];

  return (
    <div className="flex flex-col gap-3 animate-fade-in" data-testid="oracle-page">
      {/* Backstage ContentHeader */}
      <ContentHeader
        title="Oracle"
        subtitle="Zentrale Wissensquelle &middot; Live-Daten &middot; KI-gestuetzt"
        metadata={headerMeta}
        testId="page-header-card"
      />

      {/* Backstage FullHeightLayout + SplitLayout */}
      <FullHeightLayout headerOffset={60} testId="oracle-full-height">
        <SplitLayout
          sidebarWidth={256}
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          toggleIcon={
            sidebarOpen
              ? <PanelLeftClose size={12} className="text-[var(--color-text-tertiary)]" />
              : <PanelLeftOpen size={12} className="text-[var(--color-text-tertiary)]" />
          }
          testId="oracle-split"
          sidebar={
            <>
              <ContextPanel context={context} />
              <ConversationList
                conversations={conversations}
                activeId={activeConvId}
                onSelect={handleSelectConversation}
                onNew={handleNewConversation}
                onDelete={handleDeleteConversation}
              />
            </>
          }
        >
          <ChatArea
            messages={localMessages}
            isLoading={chatMutation.isPending}
            onSend={handleSend}
          />
        </SplitLayout>
      </FullHeightLayout>

      {/* Backstage StatusLine */}
      <StatusLine items={statusItems} testId="oracle-status-line" />
    </div>
  );
}
