import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import NotificationBell from '../shared/NotificationBell';
import {
  LayoutDashboard, Users, Link2, Settings, LogOut,
  Menu, X, GraduationCap, ChevronDown, User
} from 'lucide-react';

export default function PartnerLayout() {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/partner', icon: LayoutDashboard, label: t('partner.dashboard'), exact: true },
    { path: '/partner/referrals', icon: Users, label: t('partner.referrals') },
    { path: '/partner/link', icon: Link2, label: t('partner.referral_link') },
    { path: '/partner/settings', icon: Settings, label: t('partner.settings') },
  ];

  const isActive = (path, exact) => (exact ? location.pathname === path : location.pathname.startsWith(path));

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col" data-testid="partner-layout">
      <header className="bg-primary sticky top-0 z-50 shadow-sm border-b border-white/10">
        <div className="max-w-screen-2xl mx-auto flex items-center justify-between h-14 px-4 lg:px-6">
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2 shrink-0" data-testid="partner-logo">
              <GraduationCap size={20} className="text-white" />
              <span className="text-white font-heading font-bold text-sm hidden sm:inline">Partner Portal</span>
            </Link>

            <nav className="hidden lg:flex items-center gap-1" data-testid="partner-desktop-nav">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path, item.exact);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    data-testid={`partner-nav-${item.path.split('/').pop() || 'dashboard'}`}
                    className={`flex items-center gap-2 px-3 py-2 rounded-sm text-sm font-medium transition-all ${
                      active
                        ? 'bg-white/15 text-white'
                        : 'text-white/60 hover:bg-white/10 hover:text-white'
                    }`}
                  >
                    <Icon size={16} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="flex items-center gap-3">
            <NotificationBell />

            <button
              onClick={() => i18n.changeLanguage(i18n.language === 'de' ? 'en' : 'de')}
              className="hidden lg:inline-flex text-xs font-medium text-white/70 hover:text-white px-2 py-1 rounded-sm transition-colors hover:bg-white/10"
              data-testid="partner-lang-toggle"
            >
              {i18n.language === 'de' ? 'EN' : 'DE'}
            </button>

            <div className="hidden lg:block relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                data-testid="partner-user-menu-btn"
                className="flex items-center gap-2 text-white/70 hover:text-white transition-colors px-2 py-1 rounded-sm hover:bg-white/10"
              >
                <div className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center">
                  <User size={14} className="text-white" />
                </div>
                <div className="text-left hidden xl:block">
                  <p className="text-xs font-medium text-white truncate max-w-[140px]">{user?.full_name || user?.email}</p>
                  <p className="text-[10px] text-white/50">{user?.role}</p>
                </div>
                <ChevronDown size={12} className={`text-white/50 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
              </button>

              {userMenuOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                  <div className="absolute right-0 top-full mt-1 bg-white border border-slate-200 rounded-sm shadow-lg z-50 min-w-[180px]" data-testid="partner-user-dropdown">
                    <div className="px-4 py-3 border-b border-slate-100">
                      <p className="text-sm font-medium text-slate-800 truncate">{user?.full_name || user?.email}</p>
                      <p className="text-xs text-slate-400">{user?.role}</p>
                    </div>
                    <button
                      onClick={handleLogout}
                      data-testid="partner-logout-btn"
                      className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50 hover:text-red-600 transition-colors"
                    >
                      <LogOut size={14} />
                      {t('portal.logout')}
                    </button>
                  </div>
                </>
              )}
            </div>

            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="lg:hidden text-white/70 hover:text-white p-1"
              data-testid="partner-mobile-menu-btn"
            >
              {mobileOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>

        {mobileOpen && (
          <div className="lg:hidden border-t border-white/10 bg-primary/95 backdrop-blur-sm" data-testid="partner-mobile-nav">
            <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="text-white/50 text-xs">{t('portal.welcome')}</p>
                <p className="text-white font-medium text-sm truncate">{user?.full_name || user?.email}</p>
              </div>
              <button
                onClick={() => i18n.changeLanguage(i18n.language === 'de' ? 'en' : 'de')}
                className="text-xs font-medium text-white/70 hover:text-white px-2 py-1 rounded-sm transition-colors hover:bg-white/10"
                data-testid="partner-mobile-lang-toggle"
              >
                {i18n.language === 'de' ? 'EN' : 'DE'}
              </button>
            </div>
            <nav className="px-3 py-3 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path, item.exact);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileOpen(false)}
                    data-testid={`partner-mobile-nav-${item.path.split('/').pop() || 'dashboard'}`}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium transition-all ${
                      active
                        ? 'bg-white/15 text-white'
                        : 'text-white/60 hover:bg-white/10 hover:text-white'
                    }`}
                  >
                    <Icon size={16} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
            <div className="px-3 py-3 border-t border-white/10">
              <button
                onClick={() => {
                  handleLogout();
                  setMobileOpen(false);
                }}
                data-testid="partner-mobile-logout-btn"
                className="flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium text-white/60 hover:bg-white/10 hover:text-white w-full"
              >
                <LogOut size={16} />
                <span>{t('portal.logout')}</span>
              </button>
            </div>
          </div>
        )}
      </header>

      <main className="flex-1 w-full max-w-screen-2xl mx-auto p-4 lg:p-6">
        <Outlet />
      </main>
    </div>
  );
}
