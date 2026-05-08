import React, { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';
import {
  Users, BookOpen, Shield, Clock, CheckCircle, AlertCircle,
  Mail, Phone, Search, XCircle
} from 'lucide-react';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { Card, CardContent } from '../../components/ui/card';
import { getStageLabel, STAGE_COLORS as STAGE_CLR, getLang } from '../../lib/utils';

const STAGE_COLORS = STAGE_CLR;

export default function TeacherDashboard() {
  const { user } = useAuth();
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');

  const FILTER_TABS = [
    { key: 'all', label: lang === 'de' ? 'Alle' : 'All' },
    { key: 'active', label: lang === 'de' ? 'Aktiv' : 'Active' },
    { key: 'enrolled', label: lang === 'de' ? 'Eingeschrieben' : 'Enrolled' },
  ];

  useEffect(() => {
    const load = async () => {
      try {
        const res = await apiClient.get('/api/teacher/my-students', { withCredentials: true });
        setStudents(res.data.students || []);
      } catch (e) {
        if (e.response?.status === 403) {
          setError(lang === 'de' ? 'Zugriff nur fuer Lehrer-Accounts.' : 'Access restricted to teacher accounts.');
        } else {
          setError(lang === 'de' ? 'Daten konnten nicht geladen werden.' : 'Could not load data.');
        }
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filteredStudents = useMemo(() => {
    let list = students;

    // Stage filter
    if (activeFilter === 'active') {
      list = list.filter(s => !['enrolled', 'declined', 'archived'].includes(s.current_stage));
    } else if (activeFilter === 'enrolled') {
      list = list.filter(s => s.current_stage === 'enrolled');
    }

    // Search filter
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      list = list.filter(s =>
        (s.full_name || '').toLowerCase().includes(q) ||
        (s.email || '').toLowerCase().includes(q) ||
        (s.course_type || '').toLowerCase().includes(q) ||
        (s.degree_country || '').toLowerCase().includes(q)
      );
    }

    return list;
  }, [students, activeFilter, searchQuery]);

  const enrolledCount = students.filter(s => s.current_stage === 'enrolled').length;
  const activeCount = students.filter(s => !['enrolled', 'declined', 'archived'].includes(s.current_stage)).length;

  if (loading) return <div className="w2g-loading"><div className="w2g-spinner" /><p className="w2g-loading-text">Wird geladen...</p></div>;

  return (
    <PageScaffold
      title="Lehrer-Dashboard"
      subtitle={`Willkommen, ${user?.full_name || user?.email} - Ihre zugewiesenen Lernenden`}
      testId="teacher-dashboard"
      toolbar={
        <ToolbarRow
          search={
            <div className="relative w-full md:w-72 shrink-0">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                placeholder="Name, E-Mail, Kurs..."
                data-testid="teacher-search"
                className="w2g-search pl-9" />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]">
                  <XCircle size={13} />
                </button>
              )}
            </div>
          }
          filters={FILTER_TABS.map(tab => {
            const count = tab.key === 'all' ? students.length : tab.key === 'active' ? activeCount : enrolledCount;
            return (
              <button key={tab.key} onClick={() => setActiveFilter(tab.key)}
                data-testid={`teacher-filter-${tab.key}`}
                className={activeFilter === tab.key ? 'w2g-filter-pill-active' : 'w2g-filter-pill-inactive'}>
                {tab.label} ({count})
              </button>
            );
          })}
        />
      }
    >
      {/* Info Banner */}
      <div className="w2g-info-box-accent" data-testid="teacher-info-banner">
        <Shield size={18} className="text-primary mt-0.5 shrink-0" />
        <div>
          <p className="text-sm font-medium text-primary">Datenschutzhinweis</p>
          <p className="text-xs text-[var(--color-text-secondary)] mt-1">
            Sie sehen nur Lernende, die Ihnen zugewiesen wurden und der Datenweitergabe zugestimmt haben.
            Die angezeigten Daten sind auf den Betreuungszweck begrenzt.
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)] rounded-sm p-3 flex items-center gap-2 text-[var(--color-danger)] text-sm" data-testid="teacher-error">
          <AlertCircle size={16} /> {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
        <Card data-testid="teacher-stat-total">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-md bg-primary-muted flex items-center justify-center">
                <Users size={20} className="text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[var(--color-text-primary)]">{students.length}</p>
                <p className="text-xs text-[var(--color-text-secondary)]">Zugewiesene Lernende</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card data-testid="teacher-stat-enrolled">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-md bg-primary-muted flex items-center justify-center">
                <CheckCircle size={20} className="text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[var(--color-text-primary)]">{enrolledCount}</p>
                <p className="text-xs text-[var(--color-text-secondary)]">Eingeschrieben</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card data-testid="teacher-stat-pending">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-md bg-primary-muted flex items-center justify-center">
                <Clock size={20} className="text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[var(--color-text-primary)]">{activeCount}</p>
                <p className="text-xs text-[var(--color-text-secondary)]">In Bearbeitung</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Student List */}
      {filteredStudents.length === 0 ? (
        <div className="w2g-empty" data-testid="teacher-empty">
          <BookOpen size={28} className="w2g-empty-icon" />
          <p className="w2g-empty-text">
            {searchQuery || activeFilter !== 'all' ? 'Keine Treffer fuer diese Filterung' : 'Keine Lernenden zugewiesen'}
          </p>
          <p className="w2g-empty-hint">
            {!searchQuery && activeFilter === 'all' && 'Zuweisungen werden durch das Staff-Team vorgenommen.'}
          </p>
        </div>
      ) : (
        <Card className="p-0 overflow-hidden" data-testid="teacher-student-list">
          <div className="px-5 py-3 border-b border-[var(--color-divider-subtle)] flex items-center justify-between">
            <h2 className="font-semibold text-[var(--color-text-primary)] text-sm">
              Lernende ({filteredStudents.length}{filteredStudents.length !== students.length ? ` von ${students.length}` : ''})
            </h2>
          </div>
          <div className="divide-y divide-[var(--color-divider-subtle)]">
            {filteredStudents.map(student => (
              <div key={student.id} className="px-5 py-3.5 hover:bg-[var(--color-surface-elevated)] transition-colors" data-testid={`teacher-student-${student.id}`}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-9 h-9 rounded-sm bg-primary-muted flex items-center justify-center shrink-0">
                      <span className="text-xs font-bold text-primary">{(student.full_name || '?')[0].toUpperCase()}</span>
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <p className="font-medium text-[var(--color-text-primary)] text-sm truncate">{student.full_name}</p>
                        {student.current_stage && (
                          <span className={`text-[10px] px-2 py-0.5 rounded-sm border font-medium ${STAGE_COLORS[student.current_stage] || 'bg-[var(--color-surface-elevated)] text-[var(--color-text-secondary)] border-[var(--color-divider)]'}`}>
                            {getStageLabel(student.current_stage, lang)}
                          </span>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-[var(--color-text-secondary)]">
                        {student.email && <span className="truncate">{student.email}</span>}
                        {student.course_type && (
                          <span className="flex items-center gap-1"><BookOpen size={11} /> {student.course_type}</span>
                        )}
                        {student.language_level && <span>Deutsch: {student.language_level}</span>}
                        {student.degree_country && <span>{student.degree_country}</span>}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-1.5 shrink-0">
                    {student.email && (
                      <a href={`mailto:${student.email}`} data-testid={`teacher-mail-${student.id}`}
                        className="w2g-btn-icon" title="E-Mail">
                        <Mail size={15} />
                      </a>
                    )}
                    {student.phone && (
                      <a href={`tel:${student.phone}`} data-testid={`teacher-call-${student.id}`}
                        className="w2g-btn-icon" title="Anrufen">
                        <Phone size={15} />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </PageScaffold>
  );
}
