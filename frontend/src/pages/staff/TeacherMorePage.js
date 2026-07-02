import React from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare, Users } from 'lucide-react';
import { PageScaffold } from '../../components/layout/PageScaffold';

export default function TeacherMorePage() {
  return (
    <PageScaffold title="Mehr" subtitle="Zusätzliche Lehrfunktionen und feste Sprungpunkte in einem einheitlichen Raster." testId="teacher-more-page">
      <div className="grid gap-4 md:grid-cols-2">
        <Link to="/staff/students" className="w2g-card" data-testid="teacher-more-students"><div className="mb-4 flex h-10 w-10 items-center justify-center rounded-[var(--radius-lg)] bg-[rgba(10,25,47,0.08)] text-[var(--color-primary)]"><Users size={18} /></div><h2 className="text-base font-semibold text-[var(--color-text-primary)]">Lernende</h2><p className="mt-2 text-sm text-[var(--color-text-secondary)]">Datenschutzgerecht eingegrenzte Übersicht aller zugewiesenen Lernenden.</p></Link>
        <Link to="/staff/teacher/messages" className="w2g-card" data-testid="teacher-more-messages"><div className="mb-4 flex h-10 w-10 items-center justify-center rounded-[var(--radius-lg)] bg-[rgba(10,25,47,0.08)] text-[var(--color-primary)]"><MessageSquare size={18} /></div><h2 className="text-base font-semibold text-[var(--color-text-primary)]">Support-Nachrichten</h2><p className="mt-2 text-sm text-[var(--color-text-secondary)]">Lehr- und Betreuungsanfragen mit festem Kontextpanel.</p></Link>
      </div>
    </PageScaffold>
  );
}
