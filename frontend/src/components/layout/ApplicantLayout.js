import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard, FileText, MessageSquare, CreditCard,
  Settings, BookOpen, LogOut, Menu, X, GraduationCap, ChevronRight, Shield
} from 'lucide-react';
import OnboardingTour from '../OnboardingTour';

export default function ApplicantLayout() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    { path: '/portal', icon: LayoutDashboard, label: t('portal.dashboard'), exact: true },
    { path: '/portal/journey', icon: BookOpen, label: t('portal.journey') },
    { path: '/portal/documents', icon: FileText, label: t('portal.documents') },
    { path: '/portal/messages', icon: MessageSquare, label: t('portal.messages') },
    { path: '/portal/financials', icon: CreditCard, label: t('portal.financials') },
    { path: '/portal/consents', icon: Shield, label: t('portal.settings') === 'Settings' ? 'Consents' : 'Einwilligungen' },
    { path: '/portal/settings', icon: Settings, label: t('portal.settings') },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const isActive = (path, exact) => exact ? location.pathname === path : location.pathname.startsWith(path);

  return (
    <div className="min-h-screen bg-brand-bg flex">
      {/* Sidebar overlay mobile */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 h-full w-64 bg-primary z-50 flex flex-col transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:flex`}>
        {/* Logo */}
        <div className="p-4 flex items-center justify-between border-b border-white/10">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-7 h-7 bg-white/10 rounded-sm flex items-center justify-center">
              <GraduationCap size={16} className="text-white" />
            </div>
            <span className="text-white font-heading font-bold text-sm">STK Aachen</span>
          </Link>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-white/60 hover:text-white">
            <X size={18} />
          </button>
        </div>

        {/* User info */}
        <div className="px-4 py-3 border-b border-white/10">
          <p className="text-white/50 text-xs">{t('portal.welcome')}</p>
          <p className="text-white font-medium text-sm truncate">{user?.full_name || user?.email}</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(item => {
            const Icon = item.icon;
            const active = isActive(item.path, item.exact);
            return (
              <Link key={item.path} to={item.path}
                onClick={() => setSidebarOpen(false)}
                data-testid={`portal-nav-${item.path.split('/').pop() || 'dashboard'}`}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium transition-all ${
                  active ? 'bg-white/15 text-white' : 'text-white/60 hover:bg-white/10 hover:text-white'
                }`}>
                <Icon size={18} />
                <span>{item.label}</span>
                {active && <ChevronRight size={14} className="ml-auto" />}
              </Link>
            );
          })}
        </nav>

        {/* Logout */}
        <div className="px-3 py-4 border-t border-white/10">
          <button onClick={handleLogout} data-testid="portal-logout-btn"
            className="flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium text-white/60 hover:bg-white/10 hover:text-white w-full transition-all">
            <LogOut size={18} />
            <span>{t('portal.logout')}</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar mobile */}
        <header className="lg:hidden bg-white border-b border-slate-200 px-4 h-14 flex items-center justify-between">
          <button onClick={() => setSidebarOpen(true)} className="text-slate-600" data-testid="sidebar-toggle">
            <Menu size={20} />
          </button>
          <span className="font-heading font-bold text-primary text-sm">Studienkolleg Aachen</span>
          <div className="w-8" />
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-6 max-w-5xl w-full">
          <OnboardingTour />
          <Outlet />
        </main>
      </div>
    </div>
  );
}
