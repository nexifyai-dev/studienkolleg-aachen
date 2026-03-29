import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import NotificationBell from '../shared/NotificationBell';
import OnboardingTour from '../OnboardingTour';
import {
  LayoutDashboard, FileText, MessageSquare, CreditCard,
  Settings, BookOpen, LogOut, Menu, X, GraduationCap, Shield,
  ChevronDown, User
} from 'lucide-react';

export default function ApplicantLayout() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const navItems = [
    { path: '/portal', icon: LayoutDashboard, label: t('portal.dashboard'), exact: true },
    { path: '/portal/journey', icon: BookOpen, label: t('portal.journey') },
    { path: '/portal/documents', icon: FileText, label: t('portal.documents') },
    { path: '/portal/messages', icon: MessageSquare, label: t('portal.messages') },
    { path: '/portal/financials', icon: CreditCard, label: t('portal.financials') },
    { path: '/portal/consents', icon: Shield, label: t('portal.consents') },
    { path: '/portal/settings', icon: Settings, label: t('portal.settings') },
  ];

  const handleLogout = async () => { await logout(); navigate('/'); };
  const isActive = (path, exact) => exact ? location.pathname === path : location.pathname.startsWith(path);

  return (
    <div className="min-h-screen bg-brand-bg flex flex-col" data-testid="applicant-layout">
      {/* Top Header */}
      <header className="bg-primary sticky top-0 z-50 shadow-sm">
        <div className="max-w-screen-2xl mx-auto flex items-center justify-between h-14 px-4 lg:px-6">
          {/* Left: Logo + Nav */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2 shrink-0" data-testid="portal-logo">
              <GraduationCap size={20} className="text-white" />
              <span className="text-white font-heading font-bold text-sm hidden sm:inline">STK Aachen</span>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden lg:flex items-center gap-1" data-testid="portal-desktop-nav">
              {navItems.map(item => {
                const Icon = item.icon;
                const active = isActive(item.path, item.exact);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    data-testid={`portal-nav-${item.path.split('/').pop() || 'dashboard'}`}
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

          {/* Right: Notifications + User + Mobile Toggle */}
          <div className="flex items-center gap-3">
            <NotificationBell />

            {/* User Dropdown (Desktop) */}
            <div className="hidden lg:block relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                data-testid="portal-user-menu-btn"
                className="flex items-center gap-2 text-white/70 hover:text-white transition-colors px-2 py-1 rounded-sm hover:bg-white/10"
              >
                <div className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center">
                  <User size={14} className="text-white" />
                </div>
                <div className="text-left hidden xl:block">
                  <p className="text-xs font-medium text-white truncate max-w-[120px]">{user?.full_name || user?.email}</p>
                </div>
                <ChevronDown size={12} className={`text-white/50 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
              </button>

              {userMenuOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                  <div className="absolute right-0 top-full mt-1 bg-white border border-slate-200 rounded-sm shadow-lg z-50 min-w-[180px]" data-testid="portal-user-dropdown">
                    <div className="px-4 py-3 border-b border-slate-100">
                      <p className="text-sm font-medium text-slate-800 truncate">{user?.full_name || user?.email}</p>
                      <p className="text-xs text-slate-400">{user?.role === 'applicant' ? t('portal.role_applicant') : user?.role}</p>
                    </div>
                    <button
                      onClick={handleLogout}
                      data-testid="portal-logout-btn"
                      className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50 hover:text-red-600 transition-colors"
                    >
                      <LogOut size={14} />
                      {t('portal.logout')}
                    </button>
                  </div>
                </>
              )}
            </div>

            {/* Mobile Toggle */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="lg:hidden text-white/70 hover:text-white p-1"
              data-testid="portal-mobile-menu-btn"
            >
              {mobileOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>

        {/* Mobile Nav */}
        {mobileOpen && (
          <div className="lg:hidden border-t border-white/10 bg-primary/95 backdrop-blur-sm" data-testid="portal-mobile-nav">
            <div className="px-4 py-3 border-b border-white/10">
              <p className="text-white/50 text-xs">{t('portal.welcome')}</p>
              <p className="text-white font-medium text-sm truncate">{user?.full_name || user?.email}</p>
            </div>
            <nav className="px-3 py-3 space-y-1">
              {navItems.map(item => {
                const Icon = item.icon;
                const active = isActive(item.path, item.exact);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileOpen(false)}
                    data-testid={`portal-mobile-nav-${item.path.split('/').pop() || 'dashboard'}`}
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
                onClick={() => { handleLogout(); setMobileOpen(false); }}
                data-testid="portal-mobile-logout-btn"
                className="flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium text-white/60 hover:bg-white/10 hover:text-white w-full"
              >
                <LogOut size={16} />
                <span>{t('portal.logout')}</span>
              </button>
            </div>
          </div>
        )}
      </header>

      {/* Content */}
      <main className="flex-1 w-full max-w-screen-2xl mx-auto p-4 lg:p-6">
        <OnboardingTour />
        <Outlet />
      </main>
    </div>
  );
}
