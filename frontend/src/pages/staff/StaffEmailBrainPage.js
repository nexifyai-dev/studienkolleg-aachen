import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Mail, Send, CheckCircle, XCircle, Edit3, Loader2, RefreshCw, Inbox, Clock, User, Search, Eye, X, Save, RotateCcw } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { getLang } from '../../lib/utils';
import { toast } from 'sonner';

const DRAFT_STATUS = {
  draft: { label: 'Entwurf', color: 'bg-blue-100 text-blue-700' },
  approved: { label: 'Genehmigt', color: 'bg-green-100 text-green-700' },
  sent: { label: 'Gesendet', color: 'bg-emerald-100 text-emerald-800' },
  rejected: { label: 'Abgelehnt', color: 'bg-red-100 text-red-700' },
  failed: { label: 'Fehler', color: 'bg-red-100 text-red-700' },
};

/* ═══ Draft-Detail Modal ═══ */
function DraftModal({ draft, onClose, onAction, lang }) {
  const [body, setBody] = useState(draft?.body || '');
  const [subject, setSubject] = useState(draft?.subject || '');
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleApprove = async () => {
    setSaving(true);
    try {
      const payload = editing ? { edited_body: body } : {};
      await apiClient.post(`/api/brain/drafts/${draft.id}/approve`, payload);
      toast.success(lang === 'de' ? 'E-Mail gesendet' : 'Email sent');
      onAction();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Fehler');
    } finally { setSaving(false); }
  };

  const handleReject = async () => {
    setSaving(true);
    try {
      await apiClient.post(`/api/brain/drafts/${draft.id}/reject`, { reason: 'Staff-Entscheidung' });
      toast.success(lang === 'de' ? 'Entwurf abgelehnt' : 'Draft rejected');
      onAction();
    } catch { toast.error('Fehler'); }
    finally { setSaving(false); }
  };

  const handleSaveEdit = async () => {
    setSaving(true);
    try {
      await apiClient.post(`/api/brain/drafts/${draft.id}/edit`, { body, subject });
      toast.success(lang === 'de' ? 'Gespeichert' : 'Saved');
      setEditing(false);
    } catch { toast.error('Fehler'); }
    finally { setSaving(false); }
  };

  if (!draft) return null;

  return (
    <div className="w2g-modal-overlay" onClick={onClose} data-testid="draft-modal">
      <div className="w2g-modal max-w-2xl" onClick={e => e.stopPropagation()}>
        <div className="w2g-modal-header">
          <div>
            <h2 className="font-heading text-base font-bold text-[var(--color-primary)] flex items-center gap-2">
              <Mail size={16} /> {editing ? (lang === 'de' ? 'Entwurf bearbeiten' : 'Edit Draft') : (lang === 'de' ? 'KI-Entwurf pruefen' : 'Review AI Draft')}
            </h2>
            <p className="text-[10px] text-[var(--color-text-tertiary)] mt-0.5">{draft.ai_model} · {draft.tokens_used} tokens</p>
          </div>
          <button onClick={onClose} className="w2g-btn-icon" data-testid="draft-modal-close"><X size={18} /></button>
        </div>

        <div className="w2g-modal-body space-y-4 max-h-[60vh] overflow-y-auto">
          {/* Header Info */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div><span className="text-[var(--color-text-tertiary)]">{lang === 'de' ? 'An' : 'To'}</span><p className="font-medium">{draft.to_addr}</p></div>
            <div><span className="text-[var(--color-text-tertiary)]">Status</span>
              <Badge className={DRAFT_STATUS[draft.status]?.color || ''}>{DRAFT_STATUS[draft.status]?.label || draft.status}</Badge>
            </div>
          </div>

          {/* Subject */}
          <div>
            <label className="w2g-label">{lang === 'de' ? 'Betreff' : 'Subject'}</label>
            {editing ? (
              <input value={subject} onChange={e => setSubject(e.target.value)} className="w2g-input text-sm" data-testid="draft-subject-input" />
            ) : (
              <p className="text-sm font-medium text-[var(--color-text-primary)]">{subject}</p>
            )}
          </div>

          {/* Body */}
          <div>
            <label className="w2g-label">{lang === 'de' ? 'Inhalt' : 'Content'}</label>
            {editing ? (
              <textarea value={body} onChange={e => setBody(e.target.value)} rows={12}
                className="w2g-textarea text-sm font-body leading-relaxed" data-testid="draft-body-input" />
            ) : (
              <div className="p-4 bg-[var(--color-surface-elevated)] rounded-[var(--radius-sm)] border border-[var(--color-divider)] text-sm leading-relaxed whitespace-pre-wrap text-[var(--color-text-primary)]"
                data-testid="draft-body-preview">
                {body}
              </div>
            )}
          </div>
        </div>

        <div className="w2g-modal-footer">
          {draft.status === 'draft' && (
            <>
              <button onClick={handleReject} disabled={saving} className="w2g-btn-outline text-[var(--color-danger)] border-[var(--color-danger-border)] text-xs" data-testid="draft-reject">
                <XCircle size={13} /> {lang === 'de' ? 'Ablehnen' : 'Reject'}
              </button>
              <div className="flex-1" />
              {editing ? (
                <>
                  <button onClick={() => setEditing(false)} className="w2g-btn-secondary text-xs">{lang === 'de' ? 'Abbrechen' : 'Cancel'}</button>
                  <button onClick={handleSaveEdit} disabled={saving} className="w2g-btn-secondary text-xs" data-testid="draft-save-edit">
                    <Save size={12} /> {lang === 'de' ? 'Speichern' : 'Save'}
                  </button>
                </>
              ) : (
                <button onClick={() => setEditing(true)} className="w2g-btn-secondary text-xs" data-testid="draft-edit">
                  <Edit3 size={12} /> {lang === 'de' ? 'Bearbeiten' : 'Edit'}
                </button>
              )}
              <button onClick={handleApprove} disabled={saving} className="w2g-btn-primary text-xs" data-testid="draft-approve">
                {saving ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
                {lang === 'de' ? (editing ? 'Speichern & Senden' : 'Genehmigen & Senden') : (editing ? 'Save & Send' : 'Approve & Send')}
              </button>
            </>
          )}
          {draft.status === 'sent' && (
            <p className="text-xs text-[var(--color-success)] flex items-center gap-1"><CheckCircle size={13} /> {lang === 'de' ? 'Gesendet' : 'Sent'} {draft.sent_at ? new Date(draft.sent_at).toLocaleString() : ''}</p>
          )}
          {draft.status === 'rejected' && (
            <p className="text-xs text-[var(--color-danger)] flex items-center gap-1"><XCircle size={13} /> {lang === 'de' ? 'Abgelehnt' : 'Rejected'}</p>
          )}
        </div>
      </div>
    </div>
  );
}

/* ═══ Main Email Brain Page ═══ */
export default function StaffEmailBrainPage() {
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDraft, setSelectedDraft] = useState(null);
  const [filter, setFilter] = useState('all'); // all, needs_reply, has_draft, sent

  const load = useCallback(async () => {
    try {
      const res = await apiClient.get('/api/brain/emails?limit=100');
      setEmails(res.data || []);
    } catch { /* */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const pollInbox = async () => {
    setPolling(true);
    try {
      const res = await apiClient.post('/api/brain/poll-inbox');
      const d = res.data;
      toast.success(`${d.imported || 0} neue E-Mails importiert`);
      load();
    } catch { toast.error('IMAP-Poll fehlgeschlagen'); }
    finally { setPolling(false); }
  };

  const openDraft = async (draftId) => {
    try {
      const res = await apiClient.get(`/api/brain/drafts/${draftId}`);
      setSelectedDraft(res.data);
    } catch { toast.error('Entwurf konnte nicht geladen werden'); }
  };

  const filtered = emails.filter(em => {
    if (filter === 'needs_reply' && em.direction !== 'inbound') return false;
    if (filter === 'has_draft' && !em.has_draft) return false;
    if (filter === 'sent' && em.draft_status !== 'sent') return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (em.from_addr || '').toLowerCase().includes(q) ||
             (em.to_addr || '').toLowerCase().includes(q) ||
             (em.subject || '').toLowerCase().includes(q);
    }
    return true;
  });

  const stats = {
    total: emails.length,
    inbound: emails.filter(e => e.direction === 'inbound').length,
    withDraft: emails.filter(e => e.has_draft).length,
    pendingReview: emails.filter(e => e.draft_status === 'draft').length,
    sent: emails.filter(e => e.draft_status === 'sent').length,
  };

  if (loading) return <div className="w2g-loading"><div className="w2g-spinner" /><p className="w2g-loading-text">{lang === 'de' ? 'Wird geladen...' : 'Loading...'}</p></div>;

  return (
    <PageScaffold
      title={lang === 'de' ? 'E-Mail Brain' : 'Email Brain'}
      subtitle={`${stats.total} E-Mails · ${stats.pendingReview} ${lang === 'de' ? 'Entwuerfe zur Pruefung' : 'drafts to review'}`}
      testId="email-brain-page"
      actions={
        <button onClick={pollInbox} disabled={polling} className="w2g-btn-primary" data-testid="poll-inbox-btn">
          {polling ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          {lang === 'de' ? 'Inbox abrufen' : 'Poll Inbox'}
        </button>
      }
      toolbar={
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                placeholder={lang === 'de' ? 'Absender, Betreff...' : 'Sender, subject...'} className="w2g-search pl-9" data-testid="email-search" />
            </div>
          }
          filters={[
            <select key="filter" value={filter} onChange={e => setFilter(e.target.value)} className="w2g-select text-xs" data-testid="email-filter">
              <option value="all">{lang === 'de' ? 'Alle E-Mails' : 'All Emails'}</option>
              <option value="needs_reply">{lang === 'de' ? 'Eingehend' : 'Inbound'}</option>
              <option value="has_draft">{lang === 'de' ? 'Mit KI-Entwurf' : 'With AI Draft'}</option>
              <option value="sent">{lang === 'de' ? 'Gesendet' : 'Sent'}</option>
            </select>,
          ]}
        />
      }
    >
      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Card><CardContent className="py-3 px-4"><p className="text-xl font-bold">{stats.total}</p><p className="text-[10px] text-[var(--color-text-tertiary)] uppercase">Gesamt</p></CardContent></Card>
        <Card><CardContent className="py-3 px-4"><p className="text-xl font-bold text-[var(--color-primary)]">{stats.inbound}</p><p className="text-[10px] text-[var(--color-text-tertiary)] uppercase">Eingehend</p></CardContent></Card>
        <Card><CardContent className="py-3 px-4"><p className="text-xl font-bold text-[var(--color-accent)]">{stats.withDraft}</p><p className="text-[10px] text-[var(--color-text-tertiary)] uppercase">KI-Entwuerfe</p></CardContent></Card>
        <Card><CardContent className="py-3 px-4"><p className="text-xl font-bold text-[var(--color-warning)]">{stats.pendingReview}</p><p className="text-[10px] text-[var(--color-text-tertiary)] uppercase">Zur Pruefung</p></CardContent></Card>
        <Card><CardContent className="py-3 px-4"><p className="text-xl font-bold text-[var(--color-success)]">{stats.sent}</p><p className="text-[10px] text-[var(--color-text-tertiary)] uppercase">Gesendet</p></CardContent></Card>
      </div>

      {/* Email List */}
      {filtered.length === 0 ? (
        <Card><CardContent className="py-12 text-center">
          <Inbox size={32} className="mx-auto text-[var(--color-text-tertiary)] opacity-30 mb-3" />
          <p className="text-sm text-[var(--color-text-tertiary)]">{lang === 'de' ? 'Keine E-Mails gefunden' : 'No emails found'}</p>
          <button onClick={pollInbox} className="w2g-btn-secondary text-xs mt-3"><RefreshCw size={12} /> Inbox abrufen</button>
        </CardContent></Card>
      ) : (
        <Card data-testid="email-list">
          <div className="divide-y divide-[var(--color-divider)]">
            {filtered.map((em) => (
              <div key={em.id} className="px-4 py-3 hover:bg-[var(--color-surface-elevated)] transition-colors cursor-pointer group" data-testid={`email-row-${em.id}`}>
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${em.direction === 'inbound' ? 'bg-blue-50 text-blue-600' : 'bg-emerald-50 text-emerald-600'}`}>
                    {em.direction === 'inbound' ? <Inbox size={14} /> : <Send size={14} />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-[var(--color-text-primary)] truncate">
                        {em.direction === 'inbound' ? em.from_addr : em.to_addr}
                      </p>
                      {em.applicant_id && <User size={10} className="text-[var(--color-primary)] flex-shrink-0" />}
                      {em.has_draft && (
                        <Badge className={DRAFT_STATUS[em.draft_status]?.color || 'bg-gray-100'} variant="outline">
                          {DRAFT_STATUS[em.draft_status]?.label || em.draft_status}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs font-medium text-[var(--color-text-secondary)] truncate mt-0.5">{em.subject || '(kein Betreff)'}</p>
                    <p className="text-[10px] text-[var(--color-text-tertiary)] truncate mt-0.5">{(em.body || '').slice(0, 120)}...</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-[10px] text-[var(--color-text-tertiary)] whitespace-nowrap">
                      <Clock size={10} className="inline mr-1" />
                      {em.created_at ? new Date(em.created_at).toLocaleDateString('de') : ''}
                    </span>
                    {em.drafts && em.drafts.length > 0 && em.draft_status === 'draft' && (
                      <button onClick={() => openDraft(em.drafts[0].id)}
                        className="w2g-btn-primary text-[10px] px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        data-testid={`review-draft-${em.id}`}>
                        <Eye size={11} /> Pruefen
                      </button>
                    )}
                    {em.drafts && em.drafts.length > 0 && em.draft_status === 'sent' && (
                      <button onClick={() => openDraft(em.drafts[0].id)}
                        className="w2g-btn-secondary text-[10px] px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Eye size={11} /> Ansehen
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Draft Modal */}
      {selectedDraft && (
        <DraftModal
          draft={selectedDraft}
          lang={lang}
          onClose={() => setSelectedDraft(null)}
          onAction={() => { setSelectedDraft(null); load(); }}
        />
      )}
    </PageScaffold>
  );
}
