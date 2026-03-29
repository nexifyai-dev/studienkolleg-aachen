import React from 'react';
import { Link } from 'react-router-dom';
import PublicNav from '../../components/layout/PublicNav';
import PublicFooter from '../../components/layout/PublicFooter';

const COURSES = [
  { key: 'T-Kurs', color: 'blue', subjects: ['Maschinenbau','Elektrotechnik','Industrieengineering','Mathematik','Physik','Informatik (technisch)'], requirement: 'B1 Deutsch' },
  { key: 'M-Kurs', color: 'green', subjects: ['Medizin','Zahnmedizin','Biologie','Biochemie','Pharmazie','Pflegewissenschaft'], requirement: 'B1 Deutsch' },
  { key: 'W-Kurs', color: 'purple', subjects: ['BWL','Wirtschaftsinformatik','Tourismusmanagement','Soziologie','Politikwissenschaft','Jura'], requirement: 'B1 Deutsch' },
  { key: 'M/T-Kurs', color: 'orange', subjects: ['Engineering & Medizin kombiniert','Mathematik','Physik','Biologie'], requirement: 'B1 Deutsch' },
];

const colorMap = {
  blue: { bg: 'bg-blue-50', border: 'border-blue-200', badge: 'bg-blue-100 text-blue-700', dot: 'bg-blue-400' },
  green: { bg: 'bg-green-50', border: 'border-green-200', badge: 'bg-green-100 text-green-700', dot: 'bg-green-400' },
  purple: { bg: 'bg-purple-50', border: 'border-purple-200', badge: 'bg-purple-100 text-purple-700', dot: 'bg-purple-400' },
  orange: { bg: 'bg-orange-50', border: 'border-orange-200', badge: 'bg-orange-100 text-orange-700', dot: 'bg-orange-400' },
};

export default function CoursesPage() {
  return (
    <div className="min-h-screen bg-white">
      <PublicNav />
      <main className="pt-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16">
          <div className="text-center mb-12">
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-primary mb-3">Unsere Kurse</h1>
            <p className="text-slate-600 max-w-xl mx-auto">
              Alle Kurse bereiten auf die offizielle Feststellungsprüfung (FSP) vor. Die FSP-Berechtigung wird durch die zuständige Bezirksregierung entschieden.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {COURSES.map(course => {
              const c = colorMap[course.color];
              return (
                <div key={course.key} className={`border rounded-sm p-6 ${c.bg} ${c.border}`}
                  data-testid={`course-detail-${course.key}`}>
                  <div className="flex items-center justify-between mb-4">
                    <span className={`text-xs font-bold px-3 py-1 rounded-sm ${c.badge}`}>{course.key}</span>
                    <span className="text-xs text-slate-500 bg-white px-2 py-1 rounded-sm border border-slate-200">
                      Voraussetzung: {course.requirement}
                    </span>
                  </div>
                  <h3 className="font-heading font-bold text-primary text-xl mb-3">{course.key}</h3>
                  <p className="text-slate-600 text-sm mb-4">Geeignete Studienbereiche:</p>
                  <ul className="space-y-1.5">
                    {course.subjects.map(s => (
                      <li key={s} className="flex items-center gap-2 text-sm text-slate-700">
                        <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${c.dot}`}></div>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>

          <div className="bg-primary/5 border border-primary/10 rounded-sm p-6 text-center">
            <h3 className="font-heading font-bold text-primary text-lg mb-2">Welcher Kurs passt zu dir?</h3>
            <p className="text-slate-600 text-sm mb-4">Wir helfen dir gerne dabei, den richtigen Kurs für dein Studienziel zu finden.</p>
            <Link to="/apply" className="bg-primary text-white font-semibold px-6 py-3 rounded-sm hover:bg-primary-hover transition-colors inline-block"
              data-testid="courses-apply-btn">
              Jetzt bewerben
            </Link>
          </div>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
