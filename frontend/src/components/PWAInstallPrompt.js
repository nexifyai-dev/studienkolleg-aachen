import React, { useEffect, useState } from 'react';
import { X, Download } from 'lucide-react';

/**
 * PWA Install-Prompt Banner – erscheint einmalig,
 * wenn Browser (Chrome/Edge/Android) das beforeinstallprompt-Event feuert.
 * Dismissed-State bleibt für 30 Tage in localStorage.
 */
const DISMISS_KEY = 'stk_pwa_dismissed_until';

export default function PWAInstallPrompt() {
  const [event, setEvent] = useState(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const dismissedUntil = Number(localStorage.getItem(DISMISS_KEY) || 0);
    if (Date.now() < dismissedUntil) return;
    const handler = (e) => {
      e.preventDefault();
      setEvent(e);
      setVisible(true);
    };
    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  if (!visible || !event) return null;

  const install = async () => {
    try {
      await event.prompt();
      await event.userChoice;
    } catch { /* noop */ }
    setVisible(false);
    setEvent(null);
  };

  const dismiss = () => {
    localStorage.setItem(DISMISS_KEY, String(Date.now() + 30 * 24 * 60 * 60 * 1000));
    setVisible(false);
  };

  return (
    <div
      data-testid="pwa-install-prompt"
      className="fixed bottom-4 left-1/2 -translate-x-1/2 z-[60] max-w-md w-[calc(100%-2rem)] bg-white shadow-xl border border-[var(--color-divider)] rounded-[var(--radius-md)] px-4 py-3 flex items-center gap-3"
    >
      <div className="shrink-0 w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--color-primary)]/10 flex items-center justify-center text-[var(--color-primary)]">
        <Download size={18} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-xs font-semibold text-[var(--color-text-primary)]">App installieren</div>
        <div className="text-[11px] text-[var(--color-text-tertiary)]">Studienkolleg Aachen auf Ihrem Startbildschirm.</div>
      </div>
      <button
        onClick={install}
        data-testid="pwa-install-btn"
        className="text-[11px] font-medium px-3 py-1.5 rounded-[var(--radius-sm)] bg-[var(--color-primary)] text-white hover:opacity-90"
      >
        Installieren
      </button>
      <button
        onClick={dismiss}
        data-testid="pwa-install-dismiss"
        className="p-1.5 text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]"
        aria-label="Schließen"
      >
        <X size={14} />
      </button>
    </div>
  );
}
