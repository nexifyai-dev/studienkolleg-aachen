import React, { useState, useRef, useEffect, useMemo } from 'react';
import { Brain, Send, Loader2, X, Minimize2, Maximize2, Sparkles, History } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { getLang } from '../../lib/utils';
import { useTranslation } from 'react-i18next';

/**
 * Markdown-zu-HTML Renderer fuer Brain-Antworten.
 */
function applyInline(text) {
  if (!text) return '';
  let s = text;
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/\*([^*]+?)\*/g, '<em>$1</em>');
  s = s.replace(/`(.+?)`/g, '<code style="background:var(--color-surface-elevated);padding:1px 4px;border-radius:3px;font-size:11px">$1</code>');
  return s;
}

function renderTable(rows) {
  if (!rows.length) return '';
  const ths = rows[0].map(c => '<th>' + applyInline(c) + '</th>').join('');
  const trs = rows.slice(1).map(r => '<tr>' + r.map(c => '<td>' + applyInline(c) + '</td>').join('') + '</tr>').join('');
  return '<table><thead><tr>' + ths + '</tr></thead><tbody>' + trs + '</tbody></table>';
}

function markdownToHtml(text) {
  if (!text) return '';

  // Falls bereits echtes HTML, direkt durchlassen
  if (/<(h[1-6]|table|ul|ol)\b/i.test(text)) {
    return text.replace(/\n/g, '<br/>');
  }

  const lines = text.split('\n');
  const out = [];
  let tableRows = [];
  let inTable = false;

  for (const line of lines) {
    const t = line.trim();

    // Tabelle: |...|
    if (t.startsWith('|') && t.endsWith('|')) {
      if (/^[|\s:_-]+$/.test(t.replace(/[|:\-\s]/g, ''))) continue; // Trennlinie
      if (!inTable) { inTable = true; tableRows = []; }
      tableRows.push(t.split('|').slice(1, -1).map(c => c.trim()));
      continue;
    }
    if (inTable) { out.push(renderTable(tableRows)); inTable = false; tableRows = []; }

    if (t.startsWith('### ')) { out.push('<h4 class="brain-h4">' + applyInline(t.slice(4)) + '</h4>'); continue; }
    if (t.startsWith('## '))  { out.push('<h3 class="brain-h3">' + applyInline(t.slice(3)) + '</h3>'); continue; }
    if (t.startsWith('# '))   { out.push('<h3 class="brain-h3">' + applyInline(t.slice(2)) + '</h3>'); continue; }
    if (/^-{3,}$/.test(t))    { out.push('<hr/>'); continue; }
    if (/^[-*]\s/.test(t))    { out.push('<li>' + applyInline(t.replace(/^[-*]\s+/, '')) + '</li>'); continue; }
    if (/^\d+\.\s/.test(t))   { out.push('<li>' + applyInline(t.replace(/^\d+\.\s+/, '')) + '</li>'); continue; }
    if (!t)                    { out.push(''); continue; }

    out.push('<p>' + applyInline(t) + '</p>');
  }
  if (inTable) out.push(renderTable(tableRows));

  // <li> in <ul> wrappen
  let html = out.join('\n');
  html = html.replace(/((?:<li>.*?<\/li>\s*)+)/g, '<ul>$1</ul>');
  // Leere <p></p> entfernen
  html = html.replace(/<p><\/p>/g, '');
  return html;
}

function BrainContent({ content }) {
  const html = useMemo(() => {
    if (!content || content.length < 3) return `<p>${content || ''}</p>`;
    return markdownToHtml(content);
  }, [content]);
  return (
    <div className="brain-content" dangerouslySetInnerHTML={{ __html: html }} />
  );
}

/**
 * BrainPanel – Kontextueller KI-Assistent, der auf JEDER Seite verfuegbar ist.
 *
 * Props:
 * - entityId: Bewerber-ID oder Application-ID fuer Memory-Kontext
 * - context: Zusaetzlicher Kontext-String (z.B. aktuelle Seite, Daten)
 * - compact: Minimierter Modus (nur Icon)
 */
export default function BrainPanel({ entityId, context = '', compact = false }) {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [open, setOpen] = useState(false);
  const [minimized, setMinimized] = useState(compact);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [memories, setMemories] = useState(null);
  const [showMemory, setShowMemory] = useState(false);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (open && inputRef.current) inputRef.current.focus();
  }, [open]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const ask = async (directQuery) => {
    const q = (typeof directQuery === 'string' ? directQuery : query).trim();
    if (!q || loading) return;
    setQuery('');
    setMessages(prev => [...prev, { role: 'user', content: q }]);
    setLoading(true);

    try {
      const res = await apiClient.post('/api/brain/ask', {
        query: q, entity_id: entityId || '', context, lang,
      });
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.content || (lang === 'de' ? 'Ich konnte leider keine passende Antwort finden. Bitte formuliere die Frage etwas anders.' : 'I could not find a matching answer. Please rephrase your question.'),
        model: res.data.model,
        tokens: res.data.tokens,
      }]);
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: lang === 'de' ? 'Fehler bei der Verarbeitung.' : 'Processing error.',
        error: true,
      }]);
    } finally { setLoading(false); }
  };

  const loadMemories = async () => {
    if (!entityId) return;
    try {
      const res = await apiClient.get(`/api/brain/recall/${entityId}`);
      setMemories(res.data);
      setShowMemory(true);
    } catch { /* */ }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(); }
  };

  // Floating-Button wenn geschlossen
  if (!open) {
    return (
      <button onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-[70] w-12 h-12 rounded-full bg-[var(--color-primary)] text-white shadow-lg hover:shadow-xl transition-all hover:scale-105 flex items-center justify-center"
        data-testid="brain-toggle" title={lang === 'de' ? 'KI-Assistent' : 'AI Assistant'}>
        <Brain size={22} />
      </button>
    );
  }

  return (
    <div className={`fixed z-[70] shadow-2xl rounded-xl border border-[var(--color-divider)] bg-[var(--color-surface)] flex flex-col overflow-hidden transition-all ${minimized ? 'bottom-6 right-6 w-72 h-14' : 'bottom-6 right-6 w-[420px] h-[560px]'}`}
      data-testid="brain-panel">

      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2.5 bg-[var(--color-primary)] text-white cursor-pointer select-none" onClick={() => setMinimized(m => !m)}>
        <Brain size={16} />
        <span className="text-sm font-bold flex-1">{lang === 'de' ? 'Brain – KI-Assistent' : 'Brain – AI Assistant'}</span>
        <div className="flex items-center gap-1">
          {entityId && (
            <button onClick={(e) => { e.stopPropagation(); loadMemories(); }}
              className="p-1 rounded hover:bg-white/20 transition" title={lang === 'de' ? 'Erinnerungen' : 'Memories'}
              data-testid="brain-memory-btn">
              <History size={13} />
            </button>
          )}
          <button onClick={(e) => { e.stopPropagation(); setMinimized(m => !m); }}
            className="p-1 rounded hover:bg-white/20 transition">
            {minimized ? <Maximize2 size={13} /> : <Minimize2 size={13} />}
          </button>
          <button onClick={(e) => { e.stopPropagation(); setOpen(false); }}
            className="p-1 rounded hover:bg-white/20 transition" data-testid="brain-close">
            <X size={13} />
          </button>
        </div>
      </div>

      {!minimized && (
        <>
          {/* Memory-Panel */}
          {showMemory && memories && (
            <div className="border-b border-[var(--color-divider)] bg-[var(--color-surface-elevated)] p-3 max-h-32 overflow-y-auto">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">
                  {lang === 'de' ? `${memories.count} Erinnerungen` : `${memories.count} Memories`}
                </span>
                <button onClick={() => setShowMemory(false)} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]"><X size={12} /></button>
              </div>
              <div className="space-y-0.5">
                {memories.memories?.slice(0, 8).map((m, i) => (
                  <div key={i} className="text-[10px] text-[var(--color-text-secondary)] flex items-start gap-1">
                    <span className="text-[8px] bg-[var(--color-primary)]/10 text-[var(--color-primary)] px-1 rounded mt-0.5 whitespace-nowrap">{m.category}</span>
                    <span>{m.fact}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chat-Bereich */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {messages.length === 0 && (
              <div className="text-center py-8">
                <Sparkles size={28} className="mx-auto text-[var(--color-primary)] opacity-40 mb-3" />
                <p className="text-xs text-[var(--color-text-tertiary)]">
                  {lang === 'de' ? 'Frage mich alles ueber Bewerber, Dokumente, Aufgaben, Rechnungen...' : 'Ask me anything about applicants, documents, tasks, invoices...'}
                </p>
                <div className="flex flex-wrap gap-1.5 justify-center mt-3">
                  {(lang === 'de'
                    ? ['Wie ist der aktuelle Stand?', 'Welche Aufgaben sind offen?', 'Zeige die Pipeline', 'Was muss ich als naechstes tun?']
                    : ['What is the current status?', 'Which tasks are open?', 'Show pipeline', 'What should I do next?']
                  ).map((q, i) => (
                    <button key={i} onClick={() => ask(q)}
                      className="text-[10px] px-2 py-1 rounded-full border border-[var(--color-divider)] text-[var(--color-text-secondary)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition"
                      data-testid={`brain-suggestion-${i}`}>
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-xl px-3 py-2 text-xs leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-[var(--color-primary)] text-white rounded-br-sm'
                    : msg.error
                      ? 'bg-[var(--color-danger)]/10 text-[var(--color-danger)] border border-[var(--color-danger-border)] rounded-bl-sm'
                      : 'bg-[var(--color-surface-elevated)] text-[var(--color-text-primary)] border border-[var(--color-divider)] rounded-bl-sm'
                }`}>
                  {msg.role === 'user' ? (
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  ) : (
                    <BrainContent content={msg.content} />
                  )}
                  {msg.model && (
                    <div className="mt-1.5 text-[8px] opacity-40 flex items-center gap-1">
                      <span className="inline-block w-1.5 h-1.5 rounded-full bg-[var(--color-success)]" />
                      {msg.model} · {msg.tokens} tokens
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] rounded-xl rounded-bl-sm px-3 py-2">
                  <Loader2 size={14} className="animate-spin text-[var(--color-primary)]" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-[var(--color-divider)] p-2.5 bg-[var(--color-surface)]">
            <div className="flex gap-2">
              <textarea ref={inputRef} value={query} onChange={e => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={lang === 'de' ? 'Frage stellen...' : 'Ask a question...'}
                rows={1} className="flex-1 text-xs bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] rounded-lg px-3 py-2 resize-none focus:border-[var(--color-primary)] focus:outline-none"
                data-testid="brain-input" />
              <button onClick={() => ask()} disabled={loading || !query.trim()}
                className="w-8 h-8 rounded-lg bg-[var(--color-primary)] text-white flex items-center justify-center disabled:opacity-40 hover:opacity-90 transition"
                data-testid="brain-send">
                <Send size={14} />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
