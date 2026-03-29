import React, { useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/apiClient';
import { Users, BookOpen, Shield, Clock, CheckCircle, AlertCircle, Mail, Phone } from 'lucide-react';

export default function TeacherDashboard() {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const res = await apiClient.get('/api/teacher/my-students', { withCredentials: true });
        setStudents(res.data.students || []);
      } catch (e) {
        if (e.response?.status === 403) {
          setError('Zugriff nur für Lehrer-Accounts.');
        } else {
          setError('Daten konnten nicht geladen werden.');
        }
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
  );

  const stageLabels = {
    lead_new: 'Neu',
    in_review: 'In Prüfung',
    pending_docs: 'Dokumente ausstehend',
    interview_scheduled: 'Interview geplant',
    conditional_offer: 'Bedingte Zusage',
    offer_sent: 'Angebot versendet',
    enrolled: 'Eingeschrieben',
    declined: 'Abgelehnt',
    on_hold: 'Zurückgestellt',
    archived: 'Archiviert',
  };

  const stageColors = {
    lead_new: 'bg-blue-50 text-blue-700 border-blue-200',
    in_review: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    pending_docs: 'bg-orange-50 text-orange-700 border-orange-200',
    enrolled: 'bg-green-50 text-green-700 border-green-200',
    declined: 'bg-red-50 text-red-700 border-red-200',
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="teacher-dashboard">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-heading font-bold text-primary">Lehrer-Dashboard</h1>
        <p className="text-slate-500 text-sm">
          Willkommen, {user?.full_name || user?.email} – Ihre zugewiesenen Lernenden
        </p>
      </div>

      {/* Info Banner */}
      <div className="bg-primary/5 border border-primary/20 rounded-sm p-4 flex items-start gap-3" data-testid="teacher-info-banner">
        <Shield size={18} className="text-primary mt-0.5 shrink-0" />
        <div>
          <p className="text-sm font-medium text-primary">Datenschutzhinweis</p>
          <p className="text-xs text-slate-600 mt-1">
            Sie sehen nur Lernende, die Ihnen zugewiesen wurden und der Datenweitergabe zugestimmt haben.
            Die angezeigten Daten sind auf den Betreuungszweck begrenzt. Finanzdaten, Passdaten und interne Notizen sind nicht einsehbar.
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-sm p-3 flex items-center gap-2 text-red-700 text-sm" data-testid="teacher-error">
          <AlertCircle size={16} /> {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-sm p-5" data-testid="teacher-stat-total">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-sm bg-primary/8 flex items-center justify-center">
              <Users size={20} className="text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">{students.length}</p>
              <p className="text-xs text-slate-500">Zugewiesene Lernende</p>
            </div>
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-sm p-5" data-testid="teacher-stat-enrolled">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-sm bg-primary/8 flex items-center justify-center">
              <CheckCircle size={20} className="text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">
                {students.filter(s => s.current_stage === 'enrolled').length}
              </p>
              <p className="text-xs text-slate-500">Eingeschrieben</p>
            </div>
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-sm p-5" data-testid="teacher-stat-pending">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-sm bg-primary/8 flex items-center justify-center">
              <Clock size={20} className="text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">
                {students.filter(s => !['enrolled', 'declined', 'archived'].includes(s.current_stage)).length}
              </p>
              <p className="text-xs text-slate-500">In Bearbeitung</p>
            </div>
          </div>
        </div>
      </div>

      {/* Student List */}
      {students.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-sm p-10 text-center" data-testid="teacher-empty">
          <BookOpen size={32} className="text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">Keine Lernenden zugewiesen oder keine aktive Einwilligung vorhanden.</p>
          <p className="text-xs text-slate-400 mt-1">Zuweisungen werden durch das Staff-Team vorgenommen.</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-sm" data-testid="teacher-student-list">
          <div className="p-4 border-b border-slate-100">
            <h2 className="font-semibold text-slate-800">Zugewiesene Lernende ({students.length})</h2>
          </div>
          <div className="divide-y divide-slate-100">
            {students.map(student => (
              <div key={student.id} className="p-4 hover:bg-slate-50 transition-colors" data-testid={`teacher-student-${student.id}`}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium text-slate-800 text-sm truncate">{student.full_name}</p>
                      {student.current_stage && (
                        <span className={`text-xs px-2 py-0.5 rounded-sm border ${stageColors[student.current_stage] || 'bg-slate-50 text-slate-600 border-slate-200'}`}>
                          {stageLabels[student.current_stage] || student.current_stage}
                        </span>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
                      {student.course_type && (
                        <span className="flex items-center gap-1">
                          <BookOpen size={12} /> {student.course_type}
                        </span>
                      )}
                      {student.language_level && (
                        <span>Deutsch: {student.language_level}</span>
                      )}
                      {student.degree_country && (
                        <span>Abschluss: {student.degree_country}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    {student.email && (
                      <a href={`mailto:${student.email}`} className="p-2 text-slate-400 hover:text-primary transition-colors rounded-sm hover:bg-primary/5" title="E-Mail">
                        <Mail size={16} />
                      </a>
                    )}
                    {student.phone && (
                      <a href={`tel:${student.phone}`} className="p-2 text-slate-400 hover:text-primary transition-colors rounded-sm hover:bg-primary/5" title="Anrufen">
                        <Phone size={16} />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
