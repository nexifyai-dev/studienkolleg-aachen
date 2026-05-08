import React from 'react';
import { List, LayoutGrid } from 'lucide-react';

export default function ViewToggle({ view, onChange }) {
  return (
    <div className="inline-flex items-center border border-[var(--color-divider)] bg-white p-0.5" style={{ borderRadius: 'var(--radius-sm)' }} data-testid="view-toggle">
      <button onClick={() => onChange('list')} data-testid="view-toggle-list"
        className={`flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-semibold transition-all ${
          view === 'list'
            ? 'bg-[var(--color-primary)] text-white'
            : 'text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)]'
        }`} style={{ borderRadius: 'var(--radius-xs)' }}>
        <List size={13} /> Liste
      </button>
      <button onClick={() => onChange('grid')} data-testid="view-toggle-grid"
        className={`flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-semibold transition-all ${
          view === 'grid'
            ? 'bg-[var(--color-primary)] text-white'
            : 'text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)]'
        }`} style={{ borderRadius: 'var(--radius-xs)' }}>
        <LayoutGrid size={13} /> Kacheln
      </button>
    </div>
  );
}
