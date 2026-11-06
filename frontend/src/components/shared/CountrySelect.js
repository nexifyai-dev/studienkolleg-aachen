import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Search, X } from 'lucide-react';
import { COUNTRIES } from '../../lib/countries';

/* Durchsuchbares Länder-Dropdown für saubere Datenerfassung. */
export default function CountrySelect({ value, onChange, placeholder = 'Land wählen…', testId = 'country-select', required = false, name }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const wrapRef = useRef(null);
  const inputRef = useRef(null);
  const triggerRef = useRef(null);

  useEffect(() => {
    const onDoc = (e) => { if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, []);

  useEffect(() => { if (open && inputRef.current) inputRef.current.focus(); }, [open]);

  const filtered = query
    ? COUNTRIES.filter(c => c.toLowerCase().includes(query.toLowerCase()))
    : COUNTRIES;

  const pick = (c) => { onChange(c); setOpen(false); setQuery(''); };
  const clear = () => { onChange(''); triggerRef.current?.focus(); };

  return (
    <div ref={wrapRef} className="relative">
      <button ref={triggerRef} type="button" onClick={() => setOpen(o => !o)} data-testid={testId}
        className="w2g-input w-full flex items-center justify-between gap-2 text-left cursor-pointer">
        <span className={value ? 'mr-8' : 'text-[var(--color-text-tertiary)]'}>{value || placeholder}</span>
        <ChevronDown size={14} className={`shrink-0 text-[var(--color-text-tertiary)] transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {value && (
        <button type="button" onClick={clear} aria-label="Auswahl entfernen" data-testid={`${testId}-clear`}
          className="absolute right-9 top-1/2 -translate-y-1/2 p-1 rounded-sm cursor-pointer text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]">
          <X size={13} />
        </button>
      )}
      {/* Hidden input für native required-Validierung */}
      <input tabIndex={-1} aria-hidden="true" name={name} value={value || ''} required={required} onChange={() => {}}
        className="absolute inset-0 opacity-0 pointer-events-none h-px" />
      {open && (
        <div className="absolute z-30 mt-1 w-full bg-white border border-[var(--color-divider)] rounded-[var(--radius-sm)] shadow-lg overflow-hidden"
          data-testid={`${testId}-dropdown`}>
          <div className="relative border-b border-[var(--color-divider-subtle)]">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
            <input ref={inputRef} value={query} onChange={e => setQuery(e.target.value)}
              placeholder="Land suchen…" data-testid={`${testId}-search`}
              className="w-full pl-8 pr-3 py-2 text-[13px] focus:outline-none" />
          </div>
          <div className="max-h-52 overflow-y-auto" role="listbox">
            {filtered.map(c => (
              <button key={c} type="button" onClick={() => pick(c)} role="option" aria-selected={value === c}
                data-testid={`${testId}-option-${c.replace(/[^a-zA-Z]/g, '')}`}
                className={`w-full text-left px-3 py-1.5 text-[13px] hover:bg-[var(--color-surface-sunken)] transition-colors
                  ${value === c ? 'bg-[var(--color-surface-sunken)] font-semibold text-[var(--color-primary)]' : 'text-[var(--color-text-primary)]'}`}>
                {c}
              </button>
            ))}
            {filtered.length === 0 && (
              <p className="px-3 py-3 text-[12px] text-[var(--color-text-tertiary)] text-center">Kein Land gefunden</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
