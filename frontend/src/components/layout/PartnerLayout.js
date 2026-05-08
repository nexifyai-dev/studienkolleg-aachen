import React from 'react';
import { useTranslation } from 'react-i18next';
import { LayoutDashboard, Users, TrendingUp, MessageSquare, Settings } from 'lucide-react';
import { PortalShell } from './PortalShell';

export default function PartnerLayout() {
  const { t } = useTranslation();

  const navItems = [
    { path: '/partner', label: t('layout.partner.dashboard'), exact: true, testId: 'dashboard', icon: LayoutDashboard },
    { path: '/partner/referrals', label: t('layout.partner.referrals'), testId: 'referrals', icon: Users },
    { path: '/partner/tracking', label: t('layout.partner.tracking'), testId: 'tracking', matchPaths: ['/partner/tracking', '/partner/link'], icon: TrendingUp },
    { path: '/partner/messages', label: t('layout.partner.messages'), testId: 'messages', icon: MessageSquare },
    { path: '/partner/settings', label: t('layout.partner.settings'), testId: 'settings', icon: Settings },
  ];

  return <PortalShell portalName={t('layout.partner_portal')} logoHref="/partner" navItems={navItems} dataTestId="partner-shell" hideLanguageSwitch />;
}
