import React from 'react';
import { Search, AlertCircle, Inbox, Activity } from 'lucide-react';

const fieldClass = 'w-full border border-slate-200 rounded-sm px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary';

export function PatternShell({ children, testId }) {
  return <div className="bg-white border border-slate-200 rounded-sm p-3" data-testid={testId}>{children}</div>;
}

export function SearchBar({ value, onChange, placeholder, testId, className = 'w-72' }) {
  return (
    <div className={`relative ${className}`}>
      <Search size={14} className="absolute left-2.5 top-2.5 text-slate-400" />
      <input value={value} onChange={onChange} placeholder={placeholder} className={`${fieldClass} pl-8 text-xs`} data-testid={testId} />
    </div>
  );
}

export function FilterBar({ children, testId }) {
  return <PatternShell testId={testId}><div className="flex items-center justify-between flex-wrap gap-2">{children}</div></PatternShell>;
}

export function SelectionBar({ selectedCount, onToggleAll, allSelected, label = 'ausgewählt', testId }) {
  return (
    <div className="flex items-center gap-2 text-xs text-slate-500" data-testid={testId}>
      <button onClick={onToggleAll} className="inline-flex items-center gap-1 border border-slate-200 rounded-sm px-2 py-1 hover:bg-slate-50">
        {allSelected ? 'Auswahl aufheben' : 'Sichtbare auswählen'}
      </button>
      <span>{selectedCount} {label}</span>
    </div>
  );
}

export function BulkActions({ description, children, testId }) {
  return (
    <PatternShell testId={testId}>
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <p className="text-xs text-slate-500">{description}</p>
        <div className="flex items-center gap-2">{children}</div>
      </div>
    </PatternShell>
  );
}

export function QuickActions({ children, testId }) {
  return <div className="grid grid-cols-1 sm:grid-cols-2 gap-3" data-testid={testId}>{children}</div>;
}

export function ActivityPanel({ title = 'Aktivität', children, testId }) {
  return (
    <div className="bg-white border border-slate-200 rounded-sm p-4" data-testid={testId}>
      <h3 className="font-semibold text-slate-700 text-xs flex items-center gap-1.5 mb-2"><Activity size={14} className="text-primary" /> {title}</h3>
      {children}
    </div>
  );
}

export function EmptyState({ icon: Icon = Inbox, title, hint, testId }) {
  return (
    <div className="bg-white border border-slate-200 rounded-sm p-8 text-center" data-testid={testId}>
      <Icon size={32} className="text-slate-300 mx-auto mb-3" />
      <p className="text-slate-500 text-sm">{title}</p>
      {hint && <p className="text-xs text-slate-400 mt-1">{hint}</p>}
    </div>
  );
}

export function ErrorState({ message, testId }) {
  if (!message) return null;
  return (
    <div className="bg-red-50 border border-red-200 rounded-sm p-3 flex items-center gap-2 text-red-700 text-sm" data-testid={testId}>
      <AlertCircle size={16} /> {message}
    </div>
  );
}

export function RecordHeader({ title, status, owner, lastActivity, nextAction, backAction, quickActions, testId }) {
  const items = [
    { label: 'Status', value: status },
    { label: 'Owner', value: owner },
    { label: 'Letzte Aktivität', value: lastActivity },
    { label: 'Nächste Aktion', value: nextAction },
  ];
  return (
    <div className="bg-white border border-slate-200 rounded-sm p-4" data-testid={testId}>
      <div className="flex items-start justify-between gap-3 flex-wrap mb-3">
        <div className="flex items-center gap-3">
          {backAction}
          <h1 className="text-xl font-heading font-bold text-primary">{title}</h1>
        </div>
        <div className="flex items-center gap-2 flex-wrap">{quickActions}</div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {items.map((m) => (
          <div key={m.label} className="bg-slate-50 border border-slate-200 rounded-sm p-2.5">
            <p className="text-[10px] text-slate-500 uppercase tracking-wide">{m.label}</p>
            <p className="text-xs text-slate-700 font-medium mt-0.5">{m.value || '–'}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export { fieldClass };
