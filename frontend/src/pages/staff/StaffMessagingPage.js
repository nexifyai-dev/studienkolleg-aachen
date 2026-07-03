import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import DOMPurify from 'dompurify';
import apiClient from '../../lib/apiClient';
import { useAuth } from '../../contexts/AuthContext';
import { formatDate, getStageLabel, STAGE_COLORS, getLang } from '../../lib/utils';
import {
  MessageSquare, Send, Search, ArrowLeft, Loader2,
  Paperclip, FileText, Download, X, Mail,
  MessageCircle, Inbox, Filter, CheckCheck, AlertTriangle,
  User, Eye, EyeOff, StickyNote, RefreshCw,
  CheckCircle, XCircle, ArrowUpRight, Plus, Receipt,
  Sparkles, ChevronDown, ChevronUp, RotateCcw, Pen
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import { Card, CardContent } from '../../components/ui/card';
import { API } from '../../lib/apiBase';

const MAX_FILE_MB = 10;
const IMAP_SYNC_INTERVAL = 60000;

const CHANNEL_CFG = {
  portal: { label: 'Portal', color: 'bg-[var(--color-info-bg)] text-[var(--color-info)] border-[var(--color-info-border)]', icon: MessageSquare },
  email: { label: 'E-Mail', color: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border-[var(--color-warning-border)]', icon: Mail },
  whatsapp: { label: 'WhatsApp', color: 'bg-[var(--color-success-bg)] text-[var(--color-success)] border-[var(--color-success-border)]', icon: MessageCircle },
};

const STATUS_CFG = {
  open: { label: 'Offen', color: 'bg-[var(--color-info-bg)] text-[var(--color-info)] border-[var(--color-info-border)]', icon: Inbox },
  answered: { label: 'Beantwortet', color: 'bg-[var(--color-success-bg)] text-[var(--color-success)] border-[var(--color-success-border)]', icon: CheckCheck },
  escalated: { label: 'Eskaliert', color: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border-[var(--color-danger-border)]', icon: AlertTriangle },
  closed: { label: 'Geschlossen', color: 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)] border-[var(--color-divider)]', icon: XCircle },
};

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function ChannelBadge({ channel }) {
  const c = CHANNEL_CFG[channel] || CHANNEL_CFG.portal;
  const I = c.icon;
  return (
    <span className={`inline-flex items-center gap-1 text-[9px] font-semibold px-1.5 py-0.5 rounded border ${c.color}`}
      aria-label={`Kanal: ${c.label}`}>
      <I size={9} aria-hidden="true" />{c.label}
    </span>
  );
}

function StatusBadge({ status }) {
  const s = STATUS_CFG[status] || STATUS_CFG.open;
  const I = s.icon;
  return (
    <span className={`inline-flex items-center gap-1 text-[9px] font-semibold px-1.5 py-0.5 rounded border ${s.color}`}
      aria-label={`Status: ${s.label}`}>
      <I size={9} aria-hidden="true" />{s.label}
    </span>
  );
}

function ConvItem({ conv, active, onClick, userId }) {
  const others = Object.entries(conv.participant_names || {}).filter(([id]) => id !== userId).map(([, n]) => n);
  const displayName = conv.display_name || (others.length > 0 ? others.join(', ') : null);
  const name = displayName || conv.subject || conv.external_email || 'Konversation';
  const ch = conv.channel || 'portal';
  const unread = conv.unread_count || 0;

  return (
    <button onClick={onClick} data-testid={`conv-item-${conv.id}`}
      aria-label={`Konversation mit ${name}, ${CHANNEL_CFG[ch]?.label}, ${unread > 0 ? unread + ' ungelesen' : 'keine ungelesenen'}`}
      aria-current={active ? 'true' : undefined}
      className={`w-full text-left px-3 py-2.5 border-b border-[var(--color-divider-subtle)] hover:bg-[var(--color-surface-elevated)] transition-colors focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.3)] focus:ring-inset ${active ? 'bg-[rgba(10,25,47,0.05)] border-l-2 border-l-[var(--color-primary)]' : ''}`}>
      <div className="flex items-start gap-2.5">
        <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center shrink-0 mt-0.5" aria-hidden="true">
          <span className="text-[10px] font-bold text-[var(--color-primary)]">{name[0]?.toUpperCase() || '?'}</span>
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-1">
            <p className={`text-xs font-medium truncate ${unread > 0 ? 'text-[var(--color-text-primary)] font-semibold' : 'text-[var(--color-text-primary)]'}`}>{name}</p>
            <span className="text-[9px] text-[var(--color-text-tertiary)] shrink-0">{conv.last_message_at ? formatDate(conv.last_message_at) : ''}</span>
          </div>
          <div className="flex items-center gap-1 mt-0.5">
            <ChannelBadge channel={ch} />
            <StatusBadge status={conv.status || 'open'} />
            {unread > 0 && <span className="ml-auto bg-[var(--color-primary)] text-white text-[9px] font-bold w-4 h-4 rounded-full flex items-center justify-center" aria-label={`${unread} ungelesene Nachrichten`}>{unread}</span>}
          </div>
          {conv.last_message_preview && <p className={`text-[10px] truncate mt-0.5 ${unread > 0 ? 'text-[var(--color-text-secondary)] font-medium' : 'text-[var(--color-text-tertiary)]'}`}>{conv.last_message_preview}</p>}
        </div>
      </div>
    </button>
  );
}

function EmailHtmlRenderer({ html }) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'b', 'i', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'table', 'thead', 'tbody', 'tr', 'td', 'th', 'img', 'blockquote', 'hr', 'pre', 'code'],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'style', 'class', 'src', 'alt', 'width', 'height', 'colspan', 'rowspan'],
    ALLOW_DATA_ATTR: false,
  });
  return (
    <div
      className="email-html-content text-[13px] leading-relaxed max-w-full overflow-x-auto"
      dangerouslySetInnerHTML={{ __html: clean }}
    />
  );
}

function MsgBubble({ msg, isOwn }) {
  const att = msg.attachment;
  const ch = msg.channel || 'portal';
  const isInternal = msg.visibility === 'internal';
  const isEmail = ch === 'email';
  const hasHtml = isEmail && msg.html_content;

  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`} data-testid="staff-message-item"
      role="listitem">
      <div className={`max-w-lg rounded-[var(--radius-md)] px-3.5 py-2 text-sm ${
        isInternal ? 'bg-[var(--color-warning-bg)] border border-[var(--color-warning-border)] text-[var(--color-warning)]' :
        isOwn ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--color-surface-sunken)] text-[var(--color-text-primary)]'
      }`}>
        <div className="flex items-center gap-2 mb-0.5">
          {isInternal && <StickyNote size={10} className="text-[var(--color-warning)]" aria-hidden="true" />}
          {!isOwn && msg.sender_name && (
            <p className={`text-[10px] font-medium ${isInternal ? 'text-[var(--color-warning)]' : isOwn ? 'text-white/70' : 'text-[var(--color-primary)]'}`}>
              {msg.sender_name}
            </p>
          )}
          {isInternal && <span className="text-[8px] font-bold text-[var(--color-warning)] bg-[var(--color-warning-bg)] px-1 rounded">INTERN</span>}
          {isEmail && !isInternal && (
            <span className={`text-[8px] font-semibold px-1 py-0.5 rounded ${isOwn ? 'bg-white/15 text-white/80' : 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning-border)]'}`}>
              <Mail size={8} className="inline mr-0.5" aria-hidden="true" />E-Mail
            </span>
          )}
        </div>
        {msg.email_subject && (
          <p className={`text-[10px] font-semibold mb-1 ${isOwn ? 'text-white/80' : 'text-[var(--color-text-secondary)]'}`}>
            Betreff: {msg.email_subject}
          </p>
        )}
        {att?.filename && (
          <div className={`flex items-center gap-2 p-2 rounded ${isOwn ? 'bg-white/10' : isInternal ? 'bg-[var(--color-warning-bg)]' : 'bg-white'} mb-1`}>
            <FileText size={14} className={isOwn ? 'text-white/70' : 'text-[var(--color-primary)]'} aria-hidden="true" />
            <div className="flex-1 min-w-0">
              <p className={`text-[10px] font-medium truncate ${isOwn ? 'text-white' : 'text-[var(--color-text-primary)]'}`}>{att.filename}</p>
            </div>
            <a href={`${API}/api/messages/${msg.id}/attachment`} target="_blank" rel="noreferrer"
              className={`shrink-0 ${isOwn ? 'text-white/70 hover:text-white' : 'text-[var(--color-primary)]'}`}
              aria-label={`Anhang ${att.filename} herunterladen`}>
              <Download size={12} />
            </a>
          </div>
        )}
        {hasHtml ? (
          <div className={`${isOwn ? 'text-white [&_a]:text-[var(--color-info-border)]' : ''} [&_a]:underline`}>
            <EmailHtmlRenderer html={msg.html_content} />
          </div>
        ) : (
          msg.content && !msg.content.startsWith('[Datei:') && (
            <p className="text-[13px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
          )
        )}
        <p className={`text-[9px] mt-1 ${isInternal ? 'text-[var(--color-warning)]' : isOwn ? 'text-white/40' : 'text-[var(--color-text-tertiary)]'}`}>
          {msg.sent_at ? new Date(msg.sent_at).toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) : ''}
        </p>
      </div>
    </div>
  );
}

function ContextPanel({ convId }) {
  const [ctx, setCtx] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!convId) return;
    setLoading(true);
    apiClient.get(`/api/conversations/${convId}/context`, { withCredentials: true })
      .then(r => setCtx(r.data))
      .catch(() => setCtx(null))
      .finally(() => setLoading(false));
  }, [convId]);

  if (loading) return <div className="flex items-center justify-center h-32"><Loader2 size={16} className="animate-spin text-[var(--color-text-tertiary)]" aria-label="Lade Kontext..." /></div>;

  const app = ctx?.application;
  const applicant = ctx?.applicant;
  const tasks = ctx?.tasks || [];
  const docs = ctx?.documents || [];
  const invoices = ctx?.invoices || [];
  const openTasks = tasks.filter(t => t.status === 'open' || t.status === 'in_progress');

  return (
    <aside className="space-y-3 text-xs" data-testid="msg-context-panel" aria-label="Konversationskontext">
      {app ? (
        <div className="w2g-panel p-3">
          <h4 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-2">Fallakte</h4>
          <div className="space-y-1.5">
            {applicant && (
              <div className="flex items-center gap-2">
                <User size={12} className="text-[var(--color-text-tertiary)]" aria-hidden="true" />
                <span className="font-medium text-[var(--color-text-primary)]">{applicant.name}</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <span className={`text-[9px] px-1.5 py-0.5 rounded-sm font-medium ${STAGE_COLORS[app.current_stage] || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
                {getStageLabel(app.current_stage, 'de')}
              </span>
              {app.course_type && <span className="text-[var(--color-text-tertiary)]">{app.course_type}</span>}
            </div>
            <Link to={`/staff/applications/${app.id}`} className="text-white bg-[var(--color-primary)] px-2 py-0.5 rounded-sm hover:bg-[rgba(10,25,47,0.9)] flex items-center gap-1 text-[10px] font-medium mt-1 focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]" data-testid="ctx-case-link">
              <ArrowUpRight size={10} aria-hidden="true" /> Fallakte oeffnen
            </Link>
          </div>
        </div>
      ) : (
        <div className="w2g-panel p-3 text-center">
          <p className="text-[var(--color-text-tertiary)] text-[10px]">Kein Fall zugeordnet</p>
        </div>
      )}

      <div className="w2g-panel p-3">
        <h4 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Aufgaben ({openTasks.length} offen)</h4>
        {openTasks.length === 0 ? (
          <p className="text-[10px] text-[var(--color-text-tertiary)]">Keine offenen Aufgaben</p>
        ) : (
          <ul className="space-y-1">
            {openTasks.slice(0, 4).map(t => (
              <li key={t.id} className="flex items-center gap-1.5 py-0.5">
                <CheckCircle size={10} className={t.priority === 'high' ? 'text-[var(--color-danger)]' : 'text-[var(--color-text-tertiary)]'} aria-hidden="true" />
                <span className="truncate text-[var(--color-text-primary)]">{t.title}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="w2g-panel p-3">
        <h4 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Dokumente ({docs.length})</h4>
        {docs.length === 0 ? (
          <p className="text-[10px] text-[var(--color-text-tertiary)]">Keine Dokumente</p>
        ) : (
          <ul className="space-y-1">
            {docs.slice(0, 4).map(d => (
              <li key={d.id} className="flex items-center gap-1.5 py-0.5">
                <FileText size={10} className={d.status === 'approved' ? 'text-[var(--color-success)]' : 'text-[var(--color-warning)]'} aria-hidden="true" />
                <span className="truncate text-[var(--color-text-primary)]">{d.filename || d.document_type}</span>
                <span className={`ml-auto text-[8px] px-1 rounded ${d.status === 'approved' ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]' : 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]'}`}>{d.status}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="w2g-panel p-3">
        <h4 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Rechnungen ({invoices.length})</h4>
        {invoices.length === 0 ? (
          <p className="text-[10px] text-[var(--color-text-tertiary)]">Keine Rechnungen</p>
        ) : (
          <ul className="space-y-1">
            {invoices.slice(0, 3).map(inv => (
              <li key={inv.id} className="flex items-center justify-between py-0.5">
                <span className="flex items-center gap-1"><Receipt size={10} className="text-[var(--color-text-tertiary)]" aria-hidden="true" />{inv.status}</span>
                <span className="font-medium">{(inv.amount || 0).toFixed(2)} EUR</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="w2g-panel p-3">
        <h4 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)] mb-1.5">Kanal-Status</h4>
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5"><div className="w-4 h-4 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center"><MessageSquare size={9} className="text-[var(--color-primary)]" /></div> Portal</span>
            <span className="text-[9px] bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)] px-1.5 py-0.5 rounded font-medium">Aktiv</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5"><div className="w-4 h-4 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center"><Mail size={9} className="text-[var(--color-primary)]" /></div> E-Mail</span>
            <span className="text-[9px] bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)] px-1.5 py-0.5 rounded font-medium">SMTP/IMAP</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5"><div className="w-4 h-4 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center"><MessageCircle size={9} className="text-[var(--color-primary)]" /></div> WhatsApp</span>
            <span className="text-[9px] bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)] px-1.5 py-0.5 rounded font-medium">Nur Link</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default function StaffMessagingPage() {
  const { user } = useAuth();
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const PAGE_SIZE = 30;
  const [convs, setConvs] = useState([]);
  const [totalConvs, setTotalConvs] = useState(0);
  const [active, setActive] = useState(null);
  const [msgs, setMsgs] = useState([]);
  const [newMsg, setNewMsg] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMsgs, setLoadingMsgs] = useState(false);
  const [search, setSearch] = useState('');
  const [showList, setShowList] = useState(true);
  const [attachFile, setAttachFile] = useState(null);
  const [showNewConv, setShowNewConv] = useState(false);
  const [applicants, setApplicants] = useState([]);
  const [newConvSearch, setNewConvSearch] = useState('');
  const [channelFilter, setChannelFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [stats, setStats] = useState({});
  const [isInternal, setIsInternal] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [lastSyncCount, setLastSyncCount] = useState(null);
  const [signature, setSignature] = useState('');
  const [signatureEditing, setSignatureEditing] = useState(false);
  const [showSignature, setShowSignature] = useState(false);
  const [showAiPopup, setShowAiPopup] = useState(false);
  const [aiHints, setAiHints] = useState('');
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiResult, setAiResult] = useState('');
  const [aiTemplate, setAiTemplate] = useState('');
  const [aiDetectedLang, setAiDetectedLang] = useState('');
  const fileRef = useRef(null);
  const endRef = useRef(null);
  const pollRef = useRef(null);
  const convPollRef = useRef(null);
  const imapSyncRef = useRef(null);

  const loadConvs = useCallback(async (append = false, skip = 0) => {
    try {
      let params = [`limit=${PAGE_SIZE}`, `skip=${skip}`];
      if (channelFilter !== 'all') params.push(`channel=${channelFilter}`);
      if (statusFilter !== 'all') params.push(`status=${statusFilter}`);
      const qs = `?${params.join('&')}`;
      const r = await apiClient.get(`/api/conversations${qs}`, { withCredentials: true });
      const data = r.data;
      const items = data.conversations || data || [];
      const total = data.total ?? items.length;
      if (append) {
        setConvs(prev => [...prev, ...items]);
      } else {
        setConvs(items);
      }
      setTotalConvs(total);
    } catch { /* Netzwerkfehler ignorieren */ }
  }, [channelFilter, statusFilter]);

  const loadStats = useCallback(async () => {
    try { const r = await apiClient.get('/api/conversations/stats', { withCredentials: true }); setStats(r.data || {}); } catch { /* ignorieren */ }
  }, []);

  const loadApplicants = useCallback(async () => {
    try { const r = await apiClient.get('/api/users/contacts/applicants', { withCredentials: true }); setApplicants(r.data || []); } catch { /* ignorieren */ }
  }, []);

  const syncImap = useCallback(async (silent = false) => {
    setSyncing(true);
    try {
      const r = await apiClient.post('/api/messaging/sync-imap', {}, { withCredentials: true });
      const count = r.data?.synced || 0;
      setLastSyncCount(count);
      if (!silent && count > 0) {
        toast.success(`${count} neue E-Mail${count > 1 ? 's' : ''} synchronisiert`);
      }
      if (count > 0) {
        loadConvs();
        loadStats();
      }
    } catch {
      if (!silent) toast.error('IMAP-Sync fehlgeschlagen');
    } finally {
      setSyncing(false);
    }
  }, [loadConvs, loadStats]);

  // Initial load + auto-sync IMAP on mount
  useEffect(() => {
    const init = async () => {
      await Promise.all([loadConvs(), loadApplicants(), loadStats()]);
      setLoading(false);
      // Auto IMAP sync on first load (silent)
      syncImap(true);
    };
    init();

    // Signatur laden: API (per-user aus DB)
    apiClient.get('/api/email-signature', { withCredentials: true })
      .then(r => {
        const apiSig = r.data?.signature || '';
        if (apiSig) {
          setSignature(apiSig);
        }
      })
      .catch(() => {});

    // Poll conversations every 5s
    convPollRef.current = setInterval(() => { loadConvs(); loadStats(); }, 5000);
    // Auto IMAP sync every 60s
    imapSyncRef.current = setInterval(() => syncImap(true), IMAP_SYNC_INTERVAL);

    return () => {
      if (convPollRef.current) clearInterval(convPollRef.current);
      if (imapSyncRef.current) clearInterval(imapSyncRef.current);
    };
  }, [loadConvs, loadApplicants, loadStats, syncImap]);

  useEffect(() => { loadConvs(); }, [channelFilter, statusFilter, loadConvs]);

  const loadMsgs = useCallback(async (convId) => {
    if (!convId) return;
    setLoadingMsgs(true);
    try {
      const r = await apiClient.get(`/api/conversations/${convId}/messages`, { withCredentials: true });
      setMsgs(r.data || []);
      apiClient.put(`/api/conversations/${convId}/read-all`, {}, { withCredentials: true }).catch(() => {});
    } catch { /* ignorieren */ } finally { setLoadingMsgs(false); }
  }, []);

  useEffect(() => {
    if (!active?.id) return;
    loadMsgs(active.id);
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(() => loadMsgs(active.id), 4000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [active?.id, loadMsgs]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs]);

  const selectConv = (c) => { setActive(c); setShowList(false); };

  const sendMsg = async (e) => {
    e.preventDefault();
    if ((!newMsg.trim() && !attachFile) || !active?.id) return;
    setSending(true);
    try {
      if (attachFile) {
        const b64 = await fileToBase64(attachFile);
        const res = await apiClient.post(`/api/conversations/${active.id}/attachments`, { filename: attachFile.name, content_type: attachFile.type || 'application/octet-stream', file_data: b64, content: newMsg || '' }, { withCredentials: true });
        setMsgs(p => [...p, res.data]);
        setAttachFile(null);
      } else {
        const channel = active.channel || 'portal';
        const res = await apiClient.post('/api/messages', {
          conversation_id: active.id,
          content: newMsg,
          channel: channel,
          visibility: isInternal ? 'internal' : 'public',
        }, { withCredentials: true });
        setMsgs(p => [...p, res.data]);
      }
      setNewMsg('');
      setIsInternal(false);
      loadConvs();
    } catch { toast.error('Senden fehlgeschlagen'); } finally { setSending(false); }
  };

  const updateConvStatus = async (convId, status) => {
    try {
      await apiClient.put(`/api/conversations/${convId}`, { status }, { withCredentials: true });
      setActive(prev => prev ? { ...prev, status } : prev);
      toast.success(`Status: ${STATUS_CFG[status]?.label}`);
      loadConvs();
    } catch { toast.error('Fehler'); }
  };

  const generateAiEmail = async () => {
    setAiGenerating(true);
    try {
      const res = await apiClient.post('/api/messaging/generate-email', {
        conversation_id: active?.id || null,
        hints: aiHints,
        template: aiTemplate || undefined,
      }, { withCredentials: true });
      setAiResult(res.data?.generated_text || '');
      setAiDetectedLang(res.data?.detected_lang || '');
    } catch {
      toast.error('KI-Generierung fehlgeschlagen');
    } finally {
      setAiGenerating(false);
    }
  };

  const saveSignatureToApi = async (sigText) => {
    try {
      await apiClient.put('/api/email-signature', { signature: sigText }, { withCredentials: true });
      toast.success('Signatur gespeichert');
    } catch {
      toast.error('Signatur konnte nicht gespeichert werden');
    }
  };

  const resetSignatureToDefault = async () => {
    try {
      // Delete custom signature by saving empty, then reload default
      const r = await apiClient.get('/api/email-signature?reset=1', { withCredentials: true });
      const defaultSig = r.data?.signature || '';
      setSignature(defaultSig);
      await saveSignatureToApi(defaultSig);
      toast.success('Signatur auf Standard zurueckgesetzt');
    } catch {
      toast.error('Fehler beim Zuruecksetzen');
    }
  };

  const startNewConv = async (recipientId) => {
    try {
      await apiClient.post('/api/messages', { content: 'Hallo, wie kann ich Ihnen helfen?', recipient_id: recipientId, channel: 'portal' }, { withCredentials: true });
      setShowNewConv(false); setNewConvSearch('');
      await loadConvs();
      const r = await apiClient.get('/api/conversations', { withCredentials: true });
      const rData = r.data;
      const rList = rData.conversations || rData || [];
      const nc = rList.find(c => c.participants?.includes(recipientId));
      if (nc) selectConv(nc);
    } catch { /* ignorieren */ }
  };

  const startNewConvByEmail = async () => {
    try {
      const r = await apiClient.post('/api/conversations/start-by-email', { email: newConvSearch.trim() }, { withCredentials: true });
      setShowNewConv(false); setNewConvSearch('');
      await loadConvs();
      const cr = await apiClient.get('/api/conversations', { withCredentials: true });
      const cList = cr.data.conversations || cr.data || [];
      const nc = cList.find(c => c.id === r.data.conversation_id);
      if (nc) selectConv(nc);
    } catch { /* ignorieren */ }
  };

  const filteredApps = newConvSearch ? applicants.filter(a => { const q = newConvSearch.toLowerCase(); return (a.full_name || '').toLowerCase().includes(q) || (a.email || '').toLowerCase().includes(q); }) : applicants.slice(0, 10);
  const filtered = search ? convs.filter(c => { const n = Object.values(c.participant_names || {}).join(' ').toLowerCase(); const subj = (c.subject || '').toLowerCase(); const ext = (c.external_email || '').toLowerCase(); return n.includes(search.toLowerCase()) || subj.includes(search.toLowerCase()) || ext.includes(search.toLowerCase()); }) : convs;

  if (loading) return <div className="flex items-center justify-center h-64" role="status"><Loader2 size={24} className="animate-spin text-[var(--color-primary)]" /><span className="sr-only">Lade Kommunikation...</span></div>;

  const otherName = active ? Object.entries(active.participant_names || {}).filter(([id]) => id !== user?.id).map(([, n]) => n).join(', ') || active.subject || active.external_email || 'Konversation' : '';
  const activeCh = active?.channel || 'portal';

  return (
    <div className="flex flex-col animate-fade-in" style={{ height: 'calc(100vh - 120px)' }} data-testid="staff-messaging-page" role="main" aria-label="Kommunikationszentrale">
      {/* Header – PageScaffold-konform */}
      <header className="mb-2 shrink-0 space-y-2">
        <Card style={{ borderLeft: '4px solid var(--color-primary)' }} data-testid="messaging-header-card">
          <CardContent className="py-3">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div className="min-w-0">
                <h1 className="text-lg font-bold tracking-tight flex items-center gap-2" style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-primary)' }}>
                  <Inbox size={18} aria-hidden="true" /> Kommunikation
                </h1>
                <p className="text-[11px] text-[var(--color-text-secondary)] mt-0.5">
                  Zentrale Inbox | Portal + E-Mail (IMAP/SMTP) aktiv | WhatsApp nur Link
                  {stats.unread > 0 && <span className="ml-2 bg-[var(--color-danger-bg)] text-[var(--color-danger)] text-[9px] font-bold px-1.5 py-0.5 border border-[var(--color-danger-border)]" aria-live="polite">{stats.unread} ungelesen</span>}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => syncImap(false)} disabled={syncing}
                  className="w2g-btn-secondary text-[10px] px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.3)]"
                  data-testid="imap-sync-btn"
                  aria-label="E-Mails vom Server synchronisieren"
                  title="E-Mails abrufen (IMAP)">
                  {syncing ? <Loader2 size={12} className="animate-spin" /> : <Mail size={12} aria-hidden="true" />}
                  {' '}Sync
                  {lastSyncCount !== null && <span className="ml-1 text-[8px] text-[var(--color-text-tertiary)]">({lastSyncCount})</span>}
                </button>
                <button onClick={() => { loadConvs(); loadStats(); }}
                  className="w2g-btn-secondary text-[10px] px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.3)]"
                  data-testid="refresh-btn"
                  aria-label="Konversationen aktualisieren">
                  <RefreshCw size={12} aria-hidden="true" />
                </button>
                <button onClick={() => setShowNewConv(!showNewConv)} data-testid="new-conv-btn"
                  className="w2g-btn-primary text-[10px] focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.5)]"
                  aria-label="Neue Nachricht erstellen">
                  <Plus size={12} aria-hidden="true" /> Neue Nachricht
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Filter Row */}
        <Card data-testid="messaging-filters-card">
          <CardContent className="py-2.5 px-4">
            <nav className="flex items-center gap-2 flex-wrap" data-testid="messaging-filters" aria-label="Kanalfilter">
              <div className="flex items-center gap-1" role="group" aria-label="Nach Kanal filtern">
                <Filter size={11} className="text-[var(--color-text-tertiary)]" aria-hidden="true" />
                {[
                  { key: 'all', label: 'Alle', count: stats.total || 0 },
                  { key: 'portal', label: 'Portal', count: stats.portal || 0 },
                  { key: 'email', label: 'E-Mail', count: stats.email || 0 },
                  { key: 'whatsapp', label: 'WhatsApp', count: stats.whatsapp || 0 },
                ].map(f => (
                  <button key={f.key} onClick={() => setChannelFilter(f.key)} data-testid={`channel-filter-${f.key}`}
                    aria-pressed={channelFilter === f.key}
                    className={channelFilter === f.key ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}>
                    {f.label} <span className="text-[8px] opacity-70">{f.count}</span>
                  </button>
                ))}
              </div>
              <div className="w-px h-4 bg-[var(--color-divider)]" aria-hidden="true" />
              <div className="flex items-center gap-1" role="group" aria-label="Nach Status filtern">
                {[
                  { key: 'all', label: 'Alle Status' },
                  { key: 'open', label: 'Offen' },
                  { key: 'answered', label: 'Beantwortet' },
                  { key: 'escalated', label: 'Eskaliert' },
                  { key: 'closed', label: 'Geschlossen' },
                ].map(f => (
                  <button key={f.key} onClick={() => setStatusFilter(f.key)} data-testid={`status-filter-${f.key}`}
                    aria-pressed={statusFilter === f.key}
                    className={statusFilter === f.key ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}>
                    {f.label} {f.key !== 'all' && <span className="text-[8px] opacity-70">{stats[f.key] || 0}</span>}
                  </button>
                ))}
              </div>
            </nav>
          </CardContent>
        </Card>
      </header>

      {/* New Conversation Panel */}
      {showNewConv && (
        <div className="w2g-card mb-2 shrink-0 p-3" data-testid="new-conv-panel" role="dialog" aria-label="Neue Konversation starten">
          <h3 className="font-semibold text-[var(--color-text-primary)] text-xs mb-2">Bewerber auswaehlen</h3>
          <div className="relative mb-2">
            <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" aria-hidden="true" />
            <input value={newConvSearch} onChange={e => setNewConvSearch(e.target.value)} placeholder="Name oder E-Mail..." data-testid="new-conv-search"
              aria-label="Bewerber suchen"
              className="w-full pl-7 pr-3 py-1.5 text-[11px] border border-[var(--color-divider)] rounded-sm focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.3)] focus:border-[var(--color-primary)]" />
          </div>
          <div className="max-h-32 overflow-y-auto space-y-0.5" aria-label="Bewerberauswahl">
            {filteredApps.length === 0 ? (
              /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(newConvSearch.trim()) ? (
                <button onClick={startNewConvByEmail} data-testid="new-conv-create-lead"
                  className="w-full flex items-center gap-2 px-2 py-2 rounded-sm text-left bg-[rgba(212,175,55,0.08)] hover:bg-[rgba(212,175,55,0.15)] border border-[rgba(212,175,55,0.3)] transition-colors">
                  <Plus size={12} className="text-[var(--color-accent)] shrink-0" aria-hidden="true" />
                  <span className="text-[10px] font-medium text-[var(--color-text-primary)]">
                    „{newConvSearch.trim()}" als neuen Lead anlegen & Konversation starten
                  </span>
                </button>
              ) : (
                <p className="text-[10px] text-[var(--color-text-tertiary)] text-center py-2">Keine Bewerber gefunden – E-Mail-Adresse eingeben, um einen neuen Lead anzulegen</p>
              )
            ) : filteredApps.map(a => (
              <button key={a.id} onClick={() => startNewConv(a.id)} data-testid={`new-conv-pick-${a.id}`}
                className="w-full flex items-center gap-2 px-2 py-1.5 rounded-sm text-left hover:bg-[rgba(10,25,47,0.05)] focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.3)]">
                <div className="w-5 h-5 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center shrink-0" aria-hidden="true"><span className="text-[8px] font-bold text-[var(--color-primary)]">{(a.full_name || '?')[0].toUpperCase()}</span></div>
                <div className="min-w-0"><p className="text-[10px] font-medium text-[var(--color-text-primary)] truncate">{a.full_name || 'Unbekannt'}</p><p className="text-[8px] text-[var(--color-text-tertiary)] truncate">{a.email}</p></div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 3-Column Layout */}
      <Card className="overflow-hidden flex flex-1 min-h-0 p-0">
        {/* Col 1: Conversation List */}
        <nav className={`w-full md:w-72 lg:w-80 border-r border-[var(--color-divider)] flex flex-col shrink-0 ${!showList && active ? 'hidden md:flex' : 'flex'}`}
          aria-label="Konversationsliste">
          <div className="p-2 border-b border-[var(--color-divider-subtle)]">
            <div className="relative">
              <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" aria-hidden="true" />
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Suchen..." data-testid="conv-search"
                aria-label="Konversationen durchsuchen"
                className="w-full pl-7 pr-3 py-1.5 text-[11px] border border-[var(--color-divider)] rounded-md focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.3)] focus:border-[var(--color-primary)]" />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto" role="list">
            {filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-[var(--color-text-tertiary)] p-4">
                <Inbox size={24} className="mb-2" aria-hidden="true" />
                <p className="text-xs font-medium">{lang === 'de' ? 'Keine Konversationen' : 'No conversations'}</p>
                <p className="text-[10px] mt-1">{lang === 'de' ? 'Klicken Sie auf "Sync" um E-Mails abzurufen' : 'Click "Sync" to fetch emails'}</p>
              </div>
            ) : (
              <>
                {filtered.map(c => <ConvItem key={c.id} conv={c} active={active?.id === c.id} onClick={() => selectConv(c)} userId={user?.id} />)}
                {convs.length < totalConvs && (
                  <button onClick={() => loadConvs(true, convs.length)} data-testid="load-more-convs"
                    className="w-full py-2 text-[10px] text-[var(--color-primary)] font-medium hover:bg-[var(--color-surface-elevated)] transition-colors">
                    {lang === 'de' ? `Mehr laden (${convs.length}/${totalConvs})` : `Load more (${convs.length}/${totalConvs})`}
                  </button>
                )}
              </>
            )}
          </div>
        </nav>

        {/* Col 2: Thread */}
        <section className={`flex-1 flex flex-col min-w-0 ${showList && !active ? 'hidden md:flex' : 'flex'}`}
          aria-label="Nachrichtenverlauf">
          {active ? (
            <>
              {/* Thread Header */}
              <div className="px-3 py-2 border-b border-[var(--color-divider-subtle)] flex items-center gap-2 bg-[var(--color-surface-elevated)] shrink-0">
                <button onClick={() => setShowList(true)} className="md:hidden text-[var(--color-text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.3)] rounded" aria-label="Zurueck zur Liste"><ArrowLeft size={16} /></button>
                <div className="w-7 h-7 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center shrink-0" aria-hidden="true"><span className="text-[10px] font-bold text-[var(--color-primary)]">{otherName[0]?.toUpperCase() || '?'}</span></div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <p className="text-xs font-medium text-[var(--color-text-primary)] truncate">{otherName}</p>
                    <ChannelBadge channel={activeCh} />
                    <StatusBadge status={active.status || 'open'} />
                  </div>
                  {active.subject && activeCh === 'email' && (
                    <p className="text-[9px] text-[var(--color-text-secondary)] mt-0.5 truncate">Betreff: {active.subject}</p>
                  )}
                  {active.assigned_to_name && <p className="text-[9px] text-[var(--color-text-tertiary)] mt-0.5 flex items-center gap-1"><User size={9} aria-hidden="true" /> Zustaendig: {active.assigned_to_name}</p>}
                </div>
                {/* Status Actions */}
                <div className="flex items-center gap-1 shrink-0" role="group" aria-label="Konversationsaktionen">
                  {(active.status || 'open') !== 'escalated' && <button onClick={() => updateConvStatus(active.id, 'escalated')} className="text-[9px] px-1.5 py-1 rounded border border-[var(--color-danger-border)] text-[var(--color-danger)] hover:bg-[var(--color-danger-bg)] focus:outline-none focus:ring-2 focus:ring-red-300" data-testid="conv-escalate" aria-label="Eskalieren"><AlertTriangle size={10} /></button>}
                  {(active.status || 'open') !== 'closed' && <button onClick={() => updateConvStatus(active.id, 'closed')} className="text-[9px] px-1.5 py-1 rounded border border-[var(--color-divider)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-elevated)] focus:outline-none focus:ring-2 focus:ring-slate-300" data-testid="conv-close" aria-label="Schliessen"><XCircle size={10} /></button>}
                  {(active.status || 'open') === 'closed' && <button onClick={() => updateConvStatus(active.id, 'open')} className="text-[9px] px-1.5 py-1 rounded border border-[var(--color-info-border)] text-[var(--color-info)] hover:bg-[var(--color-info-bg)] focus:outline-none focus:ring-2 focus:ring-blue-300" data-testid="conv-reopen" aria-label="Wiedereroeffnen"><RefreshCw size={10} /></button>}
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto px-3 py-2 space-y-2" data-testid="staff-messages-list" role="list" aria-label="Nachrichten">
                {loadingMsgs && msgs.length === 0 ? <div className="flex items-center justify-center h-full" role="status"><Loader2 size={18} className="animate-spin text-[var(--color-text-tertiary)]" /><span className="sr-only">Lade Nachrichten...</span></div>
                  : msgs.length === 0 ? <div className="flex flex-col items-center justify-center h-full text-[var(--color-text-tertiary)]"><MessageSquare size={24} className="mb-2" aria-hidden="true" /><p className="text-xs">Noch keine Nachrichten</p></div>
                    : msgs.map(m => <MsgBubble key={m.id} msg={m} isOwn={m.sender_id === user?.id} />)}
                <div ref={endRef} />
              </div>

              {/* Attachment Preview */}
              {attachFile && (
                <div className="px-3 py-1.5 border-t border-[var(--color-divider-subtle)] flex items-center gap-2 bg-[var(--color-surface-elevated)]">
                  <FileText size={12} className="text-[var(--color-primary)]" aria-hidden="true" />
                  <span className="text-[10px] text-[var(--color-text-primary)] truncate flex-1">{attachFile.name}</span>
                  <button onClick={() => setAttachFile(null)} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)] focus:outline-none" aria-label="Anhang entfernen"><X size={12} /></button>
                </div>
              )}

              {/* Compose */}
              <div className="border-t border-[var(--color-divider-subtle)] p-2 shrink-0">
                <div className="flex items-center gap-2 mb-1.5">
                  <button onClick={() => setIsInternal(!isInternal)} data-testid="toggle-internal"
                    aria-pressed={isInternal}
                    aria-label={isInternal ? 'Interne Notiz (nur fuer Staff sichtbar)' : 'Oeffentliche Nachricht'}
                    className={`text-[9px] font-medium px-2 py-0.5 border transition-all flex items-center gap-1 focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.3)] ${isInternal ? 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border-[var(--color-warning-border)]' : 'bg-white text-[var(--color-text-secondary)] border-[var(--color-divider)] hover:border-[var(--color-warning-border)]'}`}>
                    {isInternal ? <EyeOff size={9} aria-hidden="true" /> : <Eye size={9} aria-hidden="true" />} {isInternal ? 'Interne Notiz' : 'Oeffentlich'}
                  </button>
                  <ChannelBadge channel={activeCh} />
                  {activeCh === 'email' && !isInternal && (
                    <span className="text-[8px] text-[var(--color-success)] bg-[var(--color-success-bg)] px-1.5 py-0.5 rounded border border-[var(--color-success-border)] font-medium">
                      SMTP-Versand + Signatur
                    </span>
                  )}
                  {/* AI Generate Button */}
                  {activeCh === 'email' && !isInternal && (
                    <button
                      type="button"
                      onClick={() => { setShowAiPopup(true); setAiResult(''); setAiHints(''); setAiTemplate(''); setAiDetectedLang(''); }}
                      className="ml-auto text-[9px] font-medium px-2 py-0.5 rounded border border-[rgba(10,25,47,0.3)] bg-[rgba(10,25,47,0.05)] text-[var(--color-primary)] hover:bg-[rgba(10,25,47,0.1)] transition-colors flex items-center gap-1 focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.3)]"
                      data-testid="ai-generate-btn"
                      aria-label="KI-Antwort generieren"
                    >
                      <Sparkles size={10} /> KI-Entwurf
                    </button>
                  )}
                </div>
                <form onSubmit={sendMsg} className="flex gap-1.5" data-testid="staff-message-form">
                  <button type="button" onClick={() => fileRef.current?.click()} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)] px-1.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.3)] rounded" data-testid="staff-attach-btn" aria-label="Datei anhaengen"><Paperclip size={15} /></button>
                  <input ref={fileRef} type="file" className="hidden" onChange={e => { const f = e.target.files?.[0]; if (f) { if (f.size > MAX_FILE_MB * 1024 * 1024) { toast.error(`Max ${MAX_FILE_MB} MB`); return; } setAttachFile(f); } }} accept=".pdf,.jpg,.jpeg,.png,.webp,.doc,.docx" aria-label="Datei auswaehlen" />
                  <input value={newMsg} onChange={e => setNewMsg(e.target.value)}
                    placeholder={isInternal ? 'Interne Notiz schreiben...' : activeCh === 'email' ? 'E-Mail-Antwort schreiben (mit Signatur)...' : 'Nachricht schreiben...'}
                    data-testid="staff-message-input"
                    aria-label={isInternal ? 'Interne Notiz eingeben' : 'Nachricht eingeben'}
                    className={`flex-1 border rounded-md px-2.5 py-1.5 text-xs focus:outline-none focus:ring-2 ${isInternal ? 'border-[var(--color-warning-border)] bg-[rgba(255,251,235,0.3)] focus:ring-[var(--color-warning-border)] focus:border-[var(--color-warning-border)]' : 'border-[var(--color-divider)] focus:ring-[rgba(10,25,47,0.2)] focus:border-[var(--color-primary)]'}`} />
                  <button type="submit" disabled={sending || (!newMsg.trim() && !attachFile)} data-testid="staff-message-send"
                    aria-label="Nachricht senden"
                    className={`px-3 py-1.5 rounded-md text-white disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1 ${isInternal ? 'bg-[var(--color-warning)] hover:bg-[rgba(217,119,6,0.9)] focus:ring-[var(--color-warning)]' : 'bg-[var(--color-primary)] hover:bg-[rgba(10,25,47,0.9)] focus:ring-[var(--color-primary)]'}`}>
                    <Send size={14} />
                  </button>
                </form>

                {/* Collapsible Signature Toggle */}
                {activeCh === 'email' && !isInternal && (
                  <div className="flex items-center gap-2 mt-1.5">
                    <button
                      type="button"
                      onClick={() => setShowSignature(!showSignature)}
                      className="text-[9px] text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)] flex items-center gap-1 transition-colors"
                      data-testid="toggle-signature-btn"
                      aria-expanded={showSignature}
                      aria-label="Signatur ein-/ausblenden"
                    >
                      <Pen size={9} /> Signatur {showSignature ? <ChevronUp size={9} /> : <ChevronDown size={9} />}
                    </button>
                  </div>
                )}
              </div>

              {/* Collapsible Email Signature */}
              {activeCh === 'email' && !isInternal && showSignature && (
                <div className="px-3 pb-2 pt-0 shrink-0 animate-fade-in">
                  <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-divider)] rounded-[var(--radius-sm)] overflow-hidden" data-testid="email-signature" aria-label="E-Mail-Signatur">
                    <div className="flex items-center justify-between px-2.5 py-1.5 border-b border-[var(--color-divider-subtle)]">
                      <p className="text-[9px] text-[var(--color-text-tertiary)] font-medium uppercase tracking-wide flex items-center gap-1">
                        <span className="w-4 h-4 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center">
                          <FileText size={9} className="text-[var(--color-primary)]" />
                        </span>
                        Meine Signatur
                      </p>
                      <div className="flex items-center gap-1">
                        {signatureEditing && (
                          <button
                            type="button"
                            onClick={resetSignatureToDefault}
                            className="text-[8px] font-medium text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)] transition-colors flex items-center gap-0.5"
                            data-testid="signature-reset-btn"
                          >
                            <RotateCcw size={8} /> Standard
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={() => {
                            if (signatureEditing) {
                              saveSignatureToApi(signature);
                            }
                            setSignatureEditing(!signatureEditing);
                          }}
                          className="text-[9px] font-medium px-1.5 py-0.5 rounded-[var(--radius-sm)] border border-[var(--color-divider)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-sunken)] hover:text-[var(--color-primary)] transition-colors"
                          data-testid="signature-edit-btn"
                        >
                          {signatureEditing ? 'Speichern' : 'Bearbeiten'}
                        </button>
                      </div>
                    </div>
                    {signatureEditing ? (
                      <textarea
                        value={signature}
                        onChange={(e) => setSignature(e.target.value)}
                        className="w-full px-2.5 py-2 text-[10px] text-[var(--color-text-secondary)] bg-transparent border-none focus:outline-none resize-none leading-relaxed"
                        rows={6}
                        data-testid="signature-textarea"
                        aria-label="Signatur bearbeiten"
                      />
                    ) : (
                      <div className="px-2.5 py-2 text-[10px] text-[var(--color-text-secondary)] leading-relaxed whitespace-pre-line" data-testid="signature-preview">
                        {signature || 'Keine Signatur konfiguriert'}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* AI Email Generation Popup */}
              {showAiPopup && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" data-testid="ai-email-popup-overlay">
                  <div className="bg-white rounded-lg shadow-2xl w-full max-w-lg mx-4 overflow-hidden border border-[var(--color-divider)]" data-testid="ai-email-popup">
                    {/* Header */}
                    <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-divider)] bg-[rgba(10,25,47,0.05)]">
                      <h3 className="text-sm font-semibold text-[var(--color-primary)] flex items-center gap-2">
                        <Sparkles size={14} /> KI-Mail-Entwurf
                      </h3>
                      <button onClick={() => setShowAiPopup(false)} className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors" data-testid="ai-popup-close">
                        <X size={16} />
                      </button>
                    </div>

                    <div className="p-4 space-y-3 max-h-[70vh] overflow-y-auto">
                      {/* Template Category Picker */}
                      <div>
                        <label className="text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wide block mb-1.5">
                          Vorlage waehlen
                        </label>
                        <div className="flex flex-wrap gap-1.5" data-testid="ai-template-picker">
                          {[
                            { key: '', label: 'Frei formulieren' },
                            { key: 'documents_request', label: 'Unterlagen anfordern' },
                            { key: 'status_update', label: 'Status-Update' },
                            { key: 'appointment', label: 'Termin' },
                            { key: 'offer', label: 'Zusage' },
                            { key: 'rejection', label: 'Absage' },
                            { key: 'payment_reminder', label: 'Zahlungserinnerung' },
                            { key: 'welcome', label: 'Willkommen' },
                            { key: 'follow_up', label: 'Nachfrage' },
                          ].map(t => (
                            <button
                              key={t.key}
                              type="button"
                              onClick={() => setAiTemplate(t.key)}
                              data-testid={`ai-tpl-${t.key || 'free'}`}
                              className={`text-[10px] px-2.5 py-1 rounded-full border transition-all font-medium ${
                                aiTemplate === t.key
                                  ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]'
                                  : 'bg-white text-[var(--color-text-secondary)] border-[var(--color-divider)] hover:border-[rgba(10,25,47,0.4)] hover:text-[var(--color-primary)]'
                              }`}
                            >
                              {t.label}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Hints Input */}
                      <div>
                        <label className="text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wide block mb-1">
                          Hinweise (optional)
                        </label>
                        <textarea
                          value={aiHints}
                          onChange={e => setAiHints(e.target.value)}
                          placeholder="z.B. Sprachzertifikat fehlt, Termin am Freitag 14 Uhr, Kurs beginnt im Oktober..."
                          className="w-full border border-[var(--color-divider)] rounded-md px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-[rgba(10,25,47,0.2)] focus:border-[var(--color-primary)] resize-none"
                          rows={2}
                          data-testid="ai-hints-input"
                        />
                      </div>

                      {/* Info: auto language detection */}
                      <p className="text-[9px] text-[var(--color-text-tertiary)] flex items-center gap-1">
                        <Mail size={9} /> Sprache wird automatisch aus dem Bewerberprofil erkannt
                      </p>

                      {/* Generate Button */}
                      <button
                        type="button"
                        onClick={generateAiEmail}
                        disabled={aiGenerating}
                        className="w-full py-2 rounded-md text-white bg-[var(--color-primary)] hover:bg-[rgba(10,25,47,0.9)] disabled:opacity-50 transition-colors text-xs font-medium flex items-center justify-center gap-2"
                        data-testid="ai-generate-submit"
                      >
                        {aiGenerating ? <><Loader2 size={12} className="animate-spin" /> Generiere...</> : <><Sparkles size={12} /> Entwurf generieren</>}
                      </button>

                      {/* Result */}
                      {aiResult && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <label className="text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wide">
                              Vorschlag
                            </label>
                            {aiDetectedLang && (
                              <span className="text-[8px] px-1.5 py-0.5 rounded bg-[var(--color-surface-sunken)] text-[var(--color-text-tertiary)] font-medium">
                                {aiDetectedLang === 'de' ? 'Deutsch' : aiDetectedLang === 'en' ? 'English' : aiDetectedLang}
                              </span>
                            )}
                          </div>
                          <div className="border border-[var(--color-divider)] rounded-md p-3 bg-[var(--color-surface-elevated)] text-xs leading-relaxed whitespace-pre-wrap" data-testid="ai-result-text">
                            {aiResult}
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => { setNewMsg(aiResult); setShowAiPopup(false); toast.success('Entwurf uebernommen'); }}
                              className="flex-1 py-1.5 rounded-md text-white bg-[var(--color-success)] hover:bg-[rgba(5,150,105,0.9)] text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
                              data-testid="ai-accept-btn"
                            >
                              <CheckCircle size={12} /> Uebernehmen
                            </button>
                            <button
                              type="button"
                              onClick={generateAiEmail}
                              disabled={aiGenerating}
                              className="flex-1 py-1.5 rounded-md border border-[var(--color-divider)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-elevated)] text-xs font-medium flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
                              data-testid="ai-regenerate-btn"
                            >
                              {aiGenerating ? <Loader2 size={12} className="animate-spin" /> : <RotateCcw size={12} />} Neu generieren
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-[var(--color-text-tertiary)]">
              <Inbox size={32} className="mb-3 text-[var(--color-text-tertiary)]" aria-hidden="true" />
              <p className="text-sm font-medium">Kommunikation</p>
              <p className="text-[10px] mt-1 text-[var(--color-text-tertiary)] max-w-xs text-center">Waehlen Sie eine Konversation aus der Liste oder starten Sie eine neue Nachricht.</p>
              <button onClick={() => syncImap(false)} disabled={syncing}
                className="mt-3 text-[10px] text-white bg-[var(--color-primary)] px-3 py-1.5 rounded-sm hover:bg-[rgba(10,25,47,0.9)] font-medium flex items-center gap-1 focus:outline-none"
                data-testid="empty-sync-btn"
                aria-label="E-Mails synchronisieren">
                {syncing ? <Loader2 size={10} className="animate-spin" /> : <Mail size={10} aria-hidden="true" />}
                E-Mails synchronisieren
              </button>
            </div>
          )}
        </section>

        {/* Col 3: Context Panel */}
        {active && (
          <div className="hidden lg:flex w-64 border-l border-[var(--color-divider)] flex-col overflow-y-auto bg-[var(--color-surface-elevated)] p-2" data-testid="context-panel-wrapper">
            <ContextPanel convId={active.id} />
          </div>
        )}
      </Card>
    </div>
  );
}
