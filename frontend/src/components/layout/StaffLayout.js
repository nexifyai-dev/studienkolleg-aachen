import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard, Users, Columns, FileText, BarChart2,
  Settings, LogOut, Menu, X, GraduationCap, ShieldCheck, BookOpen
} from 'lucide-react';

export default function StaffLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isTeacher = user?.role === 'teacher';

  const navItems = isTeacher ? [
    { path: '/staff', icon: LayoutDashboard, label: 'Mein Dashboard', exact: true },
  ] : [
    { path: '/staff', icon: LayoutDashboard, label: 'Dashboard', exact: true },
    { path: '/staff/kanban', icon: Columns, label: 'Kanban Board' },
    { path: '/admin', icon: ShieldCheck, label: 'Admin', roles: ['superadmin', 'admin'] },
  ];

  const handleLogout = async () => { await logout(); navigate('/'); };
  const isActive = (path, exact) => exact ? location.pathname === path : location.pathname.startsWith(path);
  const isVisible = (item) => !item.roles || item.roles.includes(user?.role);

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      <aside className={`fixed top-0 left-0 h-full w-64 bg-primary z-50 flex flex-col transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:flex`}>
        <div className="p-4 flex items-center justify-between border-b border-white/10">
          <Link to="/" className="flex items-center gap-2">
            <GraduationCap size={20} className="text-white" />
            <span className="text-white font-heading font-bold text-sm">{isTeacher ? 'W2G Lehrer' : 'W2G Staff'}</span>
          </Link>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-white/60"><X size={18} /></button>
        </div>

        <div className="px-4 py-3 border-b border-white/10">
          <p className="text-white/50 text-xs">Eingeloggt als</p>
          <p className="text-white font-medium text-sm truncate">{user?.full_name || user?.email}</p>
          <span className="text-xs bg-white/10 text-white/70 px-1.5 py-0.5 rounded-sm">{user?.role}</span>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.filter(isVisible).map(item => {
            const Icon = item.icon;
            const active = isActive(item.path, item.exact);
            return (
              <Link key={item.path} to={item.path} onClick={() => setSidebarOpen(false)}
                data-testid={`staff-nav-${item.label.toLowerCase().replace(' ', '-')}`}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium transition-all ${
                  active ? 'bg-white/15 text-white' : 'text-white/60 hover:bg-white/10 hover:text-white'
                }`}>
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="px-3 py-4 border-t border-white/10">
          <button onClick={handleLogout} data-testid="staff-logout-btn"
            className="flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium text-white/60 hover:bg-white/10 hover:text-white w-full">
            <LogOut size={18} />
            <span>Abmelden</span>
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="lg:hidden bg-white border-b border-slate-200 px-4 h-14 flex items-center justify-between">
          <button onClick={() => setSidebarOpen(true)} className="text-slate-600"><Menu size={20} /></button>
          <span className="font-heading font-bold text-primary text-sm">W2G Staff</span>
          <div className="w-8" />
        </header>
        <main className="flex-1 p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
