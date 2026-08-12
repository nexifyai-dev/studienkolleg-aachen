import React from 'react';
import { useTranslation } from 'react-i18next';
import { LayoutDashboard, Columns, Users, CheckSquare, FileText, Receipt, MessageSquare, BarChart3, Sparkles, GraduationCap, MoreHorizontal, CalendarDays } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { PortalShell } from './PortalShell';

export default function StaffLayout() {
  const { user } = useAuth();
  const { t } = useTranslation();
  const isTeacher = user?.role === 'teacher';

  const navItems = isTeacher
    ? [
        { path: '/staff', label: t('layout.teacher.dashboard'), exact: true, testId: 'dashboard', icon: LayoutDashboard },
        { path: '/staff/students', label: t('layout.teacher.students'), testId: 'students', matchPaths: ['/staff/students'], icon: GraduationCap },
        { path: '/staff/messaging', label: t('layout.teacher.messages'), testId: 'messages', icon: MessageSquare },
        { path: '/staff/more', label: t('layout.teacher.more'), testId: 'more', icon: MoreHorizontal },
      ]
    : [
        { path: '/staff', label: t('layout.staff.dashboard'), exact: true, testId: 'dashboard', icon: LayoutDashboard },
        { path: '/staff/kanban', label: t('layout.staff.kanban'), testId: 'kanban', icon: Columns },
        { path: '/staff/cases', label: t('layout.staff.cases'), testId: 'cases', icon: Users },
        { path: '/staff/tasks', label: t('layout.staff.tasks'), testId: 'tasks', icon: CheckSquare },
        { path: '/staff/documents', label: t('layout.staff.documents'), testId: 'documents', icon: FileText },
        { path: '/staff/invoices', label: t('layout.staff.invoices'), testId: 'invoices', icon: Receipt },
        { path: '/staff/quotes', label: t('layout.staff.quotes'), testId: 'quotes', icon: FileText },
        { path: '/staff/messaging', label: t('layout.staff.messages'), testId: 'messages', icon: MessageSquare },
        { path: '/staff/appointments', label: t('layout.staff.appointments', 'Termine'), testId: 'appointments', icon: CalendarDays },
        { path: '/staff/reporting', label: t('layout.staff.reporting'), testId: 'reporting', icon: BarChart3 },
        { path: '/staff/oracle', label: t('layout.staff.oracle'), testId: 'oracle', icon: Sparkles },
      ];

  return (
    <PortalShell
      portalName={isTeacher ? t('layout.teacher_portal') : t('layout.staff_portal')}
      logoHref="/staff"
      navItems={navItems}
      dataTestId={isTeacher ? 'teacher-shell' : 'staff-shell'}
      hideLanguageSwitch
    />
  );
}
