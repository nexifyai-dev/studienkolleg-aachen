import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { User, ArrowLeft, Mail, Phone, GraduationCap, FileText, Calendar, Globe2 } from 'lucide-react';
import apiClient from '../../lib/apiClient';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { InfoCard, ContentHeader, StatusLine } from '../../components/layout/BackstageComponents';
import { toast } from 'sonner';
import { getStageLabel, getLang } from '../../lib/utils';

export default function TeacherStudentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { i18n } = useTranslation();
  const lang = getLang(i18n);
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get('/api/teacher/my-students')
      .then(r => {
        const found = (r.data?.students || []).find(s => s.id === id);
        setStudent(found || null);
      })
      .catch(() => toast.error(lang === 'de' ? 'Student konnte nicht geladen werden' : 'Could not load student'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <PageScaffold title={lang === 'de' ? 'Student laden...' : 'Loading student...'}><div className="flex items-center justify-center py-16 text-[var(--color-text-secondary)]">{lang === 'de' ? 'Laden...' : 'Loading...'}</div></PageScaffold>
  );
  if (!student) return (
    <PageScaffold title={lang === 'de' ? 'Student nicht gefunden' : 'Student not found'}>
      <div className="text-center py-16">
        <p className="text-sm text-[var(--color-text-secondary)] mb-4">{lang === 'de' ? 'Kein Zugriff oder Student nicht gefunden.' : 'No access or student not found.'}</p>
        <button onClick={() => navigate('/staff/students')} className="text-sm text-[var(--color-primary)] hover:underline">{lang === 'de' ? 'Zurueck zur Liste' : 'Back to list'}</button>
      </div>
    </PageScaffold>
  );

  return (
    <PageScaffold title={student.full_name || (lang === 'de' ? 'Student' : 'Student')} icon={<User size={20} />}>
      <button
        data-testid="back-to-students" onClick={() => navigate('/staff/students')}
        className="flex items-center gap-1.5 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] mb-4 transition-colors"
      >
        <ArrowLeft size={14} /> {lang === 'de' ? 'Zurueck zur Studentenliste' : 'Back to students'}
      </button>

      <ContentHeader title={student.full_name || (lang === 'de' ? 'Unbekannt' : 'Unknown')} subtitle={lang === 'de' ? 'Studentenprofil (zweckgebundener Zugriff)' : 'Student profile (purpose-bound access)'} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <InfoCard title={lang === 'de' ? 'Kontaktdaten' : 'Contact Details'}>
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm">
              <Mail size={14} className="text-[var(--color-text-secondary)]" />
              <a href={`mailto:${student.email}`} className="text-[var(--color-primary)] hover:underline">{student.email}</a>
            </div>
            {student.phone && (
              <div className="flex items-center gap-2 text-sm">
                <Phone size={14} className="text-[var(--color-text-secondary)]" />
                <span>{student.phone}</span>
              </div>
            )}
          </div>
        </InfoCard>

        <InfoCard title={lang === 'de' ? 'Bewerbungsdaten' : 'Application Data'}>
          <div className="space-y-3">
            {student.course_type && (
              <div className="flex items-center gap-2 text-sm">
                <GraduationCap size={14} className="text-[var(--color-text-secondary)]" />
                <span className="font-medium">{student.course_type}</span>
              </div>
            )}
            {student.degree_country && (
              <div className="flex items-center gap-2 text-sm">
                <Globe2 size={14} className="text-[var(--color-text-secondary)]" />
                <span>{student.degree_country}</span>
              </div>
            )}
            {student.language_level && (
              <div className="flex items-center gap-2 text-sm">
                <FileText size={14} className="text-[var(--color-text-secondary)]" />
                <span>{lang === 'de' ? 'Sprachniveau' : 'Language Level'}: {student.language_level}</span>
              </div>
            )}
            <div className="flex items-center gap-2 text-sm">
              <Calendar size={14} className="text-[var(--color-text-secondary)]" />
              <StatusLine
                label={getStageLabel(student.current_stage, lang) || '\u2013'}
                variant={student.current_stage === 'enrolled' ? 'success' : student.current_stage === 'declined' ? 'error' : 'info'}
              />
            </div>
          </div>
        </InfoCard>
      </div>

      <div className="mt-6 p-4 bg-[var(--color-surface)] rounded-[var(--radius-sm)] border border-[var(--color-border)]">
        <p className="text-xs text-[var(--color-text-secondary)]">
          {lang === 'de'
            ? 'Hinweis: Als Lehrkraft sehen Sie ausschliesslich zweckgebundene Daten mit aktiver Einwilligung des Studenten. Finanz-, KI-Screening- und interne Notizen sind nicht einsehbar.'
            : 'Note: As a teacher, you only see purpose-bound data with active student consent. Financial, AI screening, and internal notes are not visible.'}
        </p>
      </div>
    </PageScaffold>
  );
}
