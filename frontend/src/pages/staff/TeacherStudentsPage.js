import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Users, Search, GraduationCap, Mail, ChevronRight } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { InfoCard, ContentHeader, StatusLine } from '../../components/layout/BackstageComponents';
import { toast } from 'sonner';
import { getStageLabel, getLang } from '../../lib/utils';

export default function TeacherStudentsPage() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();
  const { i18n } = useTranslation();
  const lang = getLang(i18n);

  useEffect(() => {
    apiClient.get('/api/teacher/my-students')
      .then(r => setStudents(r.data?.students || []))
      .catch(() => toast.error(lang === 'de' ? 'Studenten konnten nicht geladen werden' : 'Could not load students'))
      .finally(() => setLoading(false));
  }, [lang]);

  const filtered = students.filter(s =>
    (s.full_name || '').toLowerCase().includes(search.toLowerCase()) ||
    (s.email || '').toLowerCase().includes(search.toLowerCase()) ||
    (s.course_type || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <PageScaffold title={lang === 'de' ? 'Meine Studenten' : 'My Students'} icon={<GraduationCap size={20} />}>
      <ContentHeader title={lang === 'de' ? 'Zugewiesene Studenten' : 'Assigned Students'} subtitle={`${students.length} ${lang === 'de' ? 'Studenten' : 'Students'}`} />

      <div data-testid="teacher-students-search" className="mb-6">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-secondary)]" />
          <input
            type="text" placeholder={lang === 'de' ? 'Name, E-Mail oder Kurs suchen...' : 'Search name, email or course...'}
            value={search} onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-[var(--color-border)] rounded-[var(--radius-sm)] bg-white text-sm focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
          />
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16 text-[var(--color-text-secondary)]">{lang === 'de' ? 'Laden...' : 'Loading...'}</div>
      ) : filtered.length === 0 ? (
        <InfoCard title={lang === 'de' ? 'Keine Studenten' : 'No Students'} className="text-center py-12">
          <p className="text-sm text-[var(--color-text-secondary)]">
            {students.length === 0
              ? (lang === 'de' ? 'Ihnen sind noch keine Studenten zugewiesen. Die Zuweisung erfolgt durch das Staff-Team.' : 'No students assigned yet. Assignment is done by the staff team.')
              : (lang === 'de' ? 'Keine Ergebnisse fuer Ihre Suche.' : 'No results for your search.')}
          </p>
        </InfoCard>
      ) : (
        <div className="space-y-2">
          {filtered.map(s => (
            <div
              key={s.id}
              data-testid={`student-row-${s.id}`}
              onClick={() => navigate(`/staff/students/${s.id}`)}
              className="flex items-center justify-between p-4 bg-white border border-[var(--color-border)] rounded-[var(--radius-sm)] cursor-pointer hover:border-[var(--color-primary)] transition-colors"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-9 h-9 rounded-[var(--radius-sm)] bg-[var(--color-primary)] flex items-center justify-center flex-shrink-0">
                  <Users size={16} className="text-white" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-[var(--color-text-primary)] truncate">{s.full_name || (lang === 'de' ? 'Unbekannt' : 'Unknown')}</p>
                  <div className="flex items-center gap-2 text-xs text-[var(--color-text-secondary)]">
                    <Mail size={11} /><span className="truncate">{s.email}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4 flex-shrink-0">
                {s.course_type && (
                  <span className="text-xs px-2 py-0.5 bg-[var(--color-surface)] rounded-[var(--radius-sm)] font-medium">{s.course_type}</span>
                )}
                <StatusLine
                  label={getStageLabel(s.current_stage, lang) || '\u2013'}
                  variant={s.current_stage === 'enrolled' ? 'success' : s.current_stage === 'declined' ? 'error' : 'info'}
                />
                <ChevronRight size={16} className="text-[var(--color-text-secondary)]" />
              </div>
            </div>
          ))}
        </div>
      )}
    </PageScaffold>
  );
}
