import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Bell, Check, CheckCheck, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../lib/apiClient';

const ICON_MAP = {
  'file-text': 'FileText',
  'refresh-cw': 'RefreshCw',
  'upload': 'Upload',
  'graduation-cap': 'GraduationCap',
  'shield': 'Shield',
  'shield-off': 'ShieldOff',
  'message-square': 'MessageSquare',
  'bell': 'Bell',
};

function timeAgo(dateStr, lang) {
  const now = new Date();
  const d = new Date(dateStr);
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return lang === 'en' ? 'just now' : 'gerade eben';
  if (diff < 3600) {
    const m = Math.floor(diff / 60);
    return lang === 'en' ? `${m}m ago` : `vor ${m} Min.`;
  }
  if (diff < 86400) {
    const h = Math.floor(diff / 3600);
    return lang === 'en' ? `${h}h ago` : `vor ${h} Std.`;
  }
  const days = Math.floor(diff / 86400);
  return lang === 'en' ? `${days}d ago` : `vor ${days} T.`;
}

export default function NotificationBell() {
  const { i18n } = useTranslation();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const ref = useRef(null);
  const lang = i18n.language || 'de';

  const fetchUnreadCount = useCallback(async () => {
    try {
      const res = await apiClient.get('/api/notifications/unread-count');
      setUnreadCount(res.data.count || 0);
    } catch {}
  }, []);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/notifications?limit=20');
      setNotifications(res.data || []);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, [fetchUnreadCount]);

  useEffect(() => {
    if (open) fetchNotifications();
  }, [open, fetchNotifications]);

  useEffect(() => {
    function handleClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const markRead = async (id) => {
    try {
      await apiClient.patch(`/api/notifications/${id}/read`);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch {}
  };

  const markAllRead = async () => {
    try {
      await apiClient.patch('/api/notifications/read-all');
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch {}
  };

  const handleClick = (notif) => {
    if (!notif.read) markRead(notif.id);
    if (notif.link) {
      navigate(notif.link);
      setOpen(false);
    }
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        data-testid="notification-bell"
        className="relative p-2 rounded-md hover:bg-slate-100 transition-colors"
        aria-label="Notifications"
      >
        <Bell size={20} className="text-slate-600" />
        {unreadCount > 0 && (
          <span
            data-testid="notification-badge"
            className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-[10px] font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1"
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div
          data-testid="notification-dropdown"
          className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-white rounded-lg shadow-lg border border-slate-200 z-[9999] max-h-[420px] flex flex-col"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
            <h3 className="text-sm font-semibold text-slate-800">
              {lang === 'en' ? 'Notifications' : 'Benachrichtigungen'}
            </h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllRead}
                  data-testid="mark-all-read-btn"
                  className="text-xs text-primary hover:underline flex items-center gap-1"
                >
                  <CheckCheck size={14} />
                  {lang === 'en' ? 'Mark all read' : 'Alle gelesen'}
                </button>
              )}
              <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X size={16} />
              </button>
            </div>
          </div>

          {/* List */}
          <div className="overflow-y-auto flex-1">
            {loading && notifications.length === 0 && (
              <div className="p-6 text-center text-slate-400 text-sm">
                {lang === 'en' ? 'Loading...' : 'Laden...'}
              </div>
            )}
            {!loading && notifications.length === 0 && (
              <div className="p-6 text-center text-slate-400 text-sm" data-testid="no-notifications">
                {lang === 'en' ? 'No notifications' : 'Keine Benachrichtigungen'}
              </div>
            )}
            {notifications.map(notif => (
              <div
                key={notif.id}
                onClick={() => handleClick(notif)}
                data-testid={`notification-item-${notif.id}`}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleClick(notif); }}
                className={`w-full text-left px-4 py-3 border-b border-slate-50 hover:bg-slate-50 transition-colors flex items-start gap-3 cursor-pointer ${
                  !notif.read ? 'bg-blue-50/40' : ''
                }`}
              >
                <div className={`mt-0.5 w-2 h-2 rounded-full flex-shrink-0 ${
                  notif.read ? 'bg-transparent' : 'bg-primary'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className={`text-sm leading-tight ${notif.read ? 'text-slate-500' : 'text-slate-800 font-medium'}`}>
                    {notif.title}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5 truncate">{notif.message}</p>
                  <p className="text-[10px] text-slate-300 mt-1">{timeAgo(notif.created_at, lang)}</p>
                </div>
                {!notif.read && (
                  <button
                    onClick={(e) => { e.stopPropagation(); markRead(notif.id); }}
                    className="text-slate-300 hover:text-primary flex-shrink-0 mt-1"
                    title={lang === 'en' ? 'Mark as read' : 'Als gelesen markieren'}
                  >
                    <Check size={14} />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
