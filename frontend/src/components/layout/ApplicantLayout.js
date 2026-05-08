import React from 'react';
import { useTranslation } from 'react-i18next';
import { LayoutDashboard, Route, ListChecks, FileText, MessageSquare, CreditCard, CalendarDays, MoreHorizontal, MenuSquare } from 'lucide-react';
import OnboardingTour from '../OnboardingTour';
import { PortalShell } from './PortalShell';

export default function ApplicantLayout() {
  const { t } = useTranslation();

  const navItems = [
    { path: '/portal', label: t('layout.applicant.dashboard'), exact: true, testId: 'dashboard', icon: LayoutDashboard },
    { path: '/portal/journey', label: t('layout.applicant.status'), testId: 'status', icon: Route },
    { path: '/portal/tasks', label: t('layout.applicant.tasks'), testId: 'tasks', icon: ListChecks },
    { path: '/portal/documents', label: t('layout.applicant.documents'), testId: 'documents', icon: FileText },
    { path: '/portal/messages', label: t('layout.applicant.messages'), testId: 'messages', icon: MessageSquare },
    { path: '/portal/financials', label: t('layout.applicant.financials'), testId: 'financials', icon: CreditCard },
    { path: '/portal/appointments', label: t('layout.applicant.appointments'), testId: 'appointments', icon: CalendarDays },
    { path: '/portal/more', label: t('layout.applicant.more'), testId: 'more', icon: MoreHorizontal },
  ];

  const mobileBottomNav = [
    { path: '/portal', label: t('layout.applicant_mobile.home'), testId: 'dashboard', icon: LayoutDashboard, exact: true },
    { path: '/portal/tasks', label: t('layout.applicant_mobile.tasks'), testId: 'tasks', icon: ListChecks },
    { path: '/portal/documents', label: t('layout.applicant_mobile.docs'), testId: 'documents', icon: FileText },
    { path: '/portal/messages', label: t('layout.applicant_mobile.chat'), testId: 'messages', icon: MessageSquare },
    { path: '/portal/more', label: t('layout.applicant_mobile.more'), testId: 'more', icon: MenuSquare },
  ];

  return (
    <>
      <OnboardingTour />
      <PortalShell
        portalName={t('layout.applicant_portal')}
        logoHref="/portal"
        navItems={navItems}
        mobileBottomNav={mobileBottomNav}
        dataTestId="applicant-shell"
      />
    </>
  );
}
