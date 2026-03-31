import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import { LOGIN_PATH } from '../../constants/routes';
import { LayoutDashboard, Users, Link2, Settings, LogOut } from 'lucide-react';

export default function PartnerLayout() {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate(LOGIN_PATH);
  };

  const navItems = [
    { path: '/partner', icon: LayoutDashboard, label: t('partner.dashboard'), end: true },
    { path: '/partner/referrals', icon: Users, label: t('partner.referrals') },
    { path: '/partner/link', icon: Link2, label: t('partner.referral_link') },
    { path: '/partner/settings', icon: Settings, label: t('partner.settings') },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top bar */}
      <header className="h-14 bg-white border-b border-slate-200 fixed top-0 left-0 right-0 z-50 flex items-center px-4 sm:px-6">
        <div className="flex items-center gap-2 mr-6">
          <div className="w-7 h-7 rounded-sm bg-primary flex items-center justify-center">
            <span className="text-white font-heading font-bold text-xs">W2G</span>
          </div>
          <span className="font-heading font-bold text-primary text-sm hidden sm:block">Partner Portal</span>
        </div>

        <nav className="flex items-center gap-1 flex-1">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <NavLink key={item.path} to={item.path} end={item.end}
                data-testid={`partner-nav-${item.path.split('/').pop() || 'dashboard'}`}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-1.5 rounded-sm text-xs font-medium transition-colors ${
                    isActive ? 'bg-primary/10 text-primary' : 'text-slate-600 hover:bg-slate-100'
                  }`
                }
              >
                <Icon size={14} />
                <span className="hidden sm:inline">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          <button onClick={() => i18n.changeLanguage(i18n.language === 'de' ? 'en' : 'de')}
            className="text-xs font-medium text-slate-500 hover:text-primary px-2 py-1 rounded-sm transition-colors">
            {i18n.language === 'de' ? 'EN' : 'DE'}
          </button>
          <span className="text-xs text-slate-500 hidden sm:block">{user?.full_name}</span>
          <button onClick={handleLogout} data-testid="partner-logout-btn"
            className="text-slate-400 hover:text-red-500 transition-colors">
            <LogOut size={16} />
          </button>
        </div>
      </header>

      <main className="pt-14 px-4 sm:px-6 py-6 max-w-5xl mx-auto">
        <Outlet />
      </main>
    </div>
  );
}
