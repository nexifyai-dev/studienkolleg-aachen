import React from 'react';
import { useTranslation } from 'react-i18next';
import { LayoutDashboard, FolderOpen, Users, UserCog, Euro, Handshake, BookOpen, Cpu, Scale, Shield, BarChart3, Settings, MessageSquare, FileCheck2, ArrowLeftRight } from 'lucide-react';
import { PortalShell } from './PortalShell';

export default function AdminLayout() {
  const { t } = useTranslation();

  const navItems = [
    { path: '/admin', label: t('layout.admin.dashboard'), exact: true, testId: 'dashboard', icon: LayoutDashboard },
    { path: '/admin/cases', label: t('layout.admin.cases'), testId: 'cases', icon: FolderOpen },
    { path: '/admin/messages', label: 'Nachrichten', testId: 'messages', icon: MessageSquare },
    { path: '/admin/documents', label: 'Dokumente', testId: 'documents', icon: FileCheck2 },
    { path: '/admin/staff', label: 'Mitarbeiter', testId: 'staff', icon: UserCog },
    { path: '/admin/users', label: t('layout.admin.users'), testId: 'users', icon: Users },
    { path: '/admin/partners', label: t('layout.admin.partners'), testId: 'partners', icon: Handshake },
    { path: '/admin/finance', label: 'Finanzen', testId: 'finance', icon: Euro },
    { path: '/admin/reports', label: t('layout.admin.reports'), testId: 'reports', icon: BarChart3 },
    { path: '/admin/knowledge', label: t('layout.admin.knowledge'), testId: 'knowledge', icon: BookOpen },
    { path: '/admin/jobs', label: t('layout.admin.jobs'), testId: 'jobs', icon: Cpu },
    { path: '/admin/rules', label: t('layout.admin.rules'), testId: 'rules', icon: Scale },
    { path: '/admin/audit', label: t('layout.admin.audit'), testId: 'audit', icon: Shield },
    { path: '/admin/settings', label: t('layout.admin.settings'), testId: 'settings', icon: Settings },
    { path: '/staff', label: 'Staff-Ansicht', testId: 'staff-view', icon: ArrowLeftRight },
  ];

  return (
    <PortalShell portalName={t('layout.admin_portal')} logoHref="/admin" navItems={navItems} dataTestId="admin-shell" hideLanguageSwitch />
  );
}
