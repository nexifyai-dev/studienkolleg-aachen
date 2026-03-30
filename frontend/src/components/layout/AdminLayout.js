import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ShieldCheck, Users, FileText, LogOut, GraduationCap, Menu, X } from 'lucide-react';

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { path: '/admin', label: 'Dashboard', icon: ShieldCheck },
    { path: '/admin/users', label: 'Nutzer', icon: Users },
    { path: '/admin/audit', label: 'Audit Logs', icon: FileText },
  ];

  const handleLogout = async () => { await logout(); navigate('/'); };
  const isActive = (path) => path === '/admin' ? location.pathname === path : location.pathname.startsWith(path);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col" data-testid="admin-layout">
      <header className="bg-primary sticky top-0 z-50 shadow-sm">
        <div className="max-w-screen-2xl mx-auto flex items-center justify-between h-14 px-4 lg:px-6">
          <div className="flex items-center gap-6">
            <Link to="/admin" className="flex items-center gap-2 shrink-0" data-testid="admin-logo">
              <GraduationCap size={20} className="text-white" />
              <span className="text-white font-heading font-bold text-sm">W2G Admin</span>
            </Link>
            <nav className="hidden lg:flex items-center gap-1" data-testid="admin-desktop-nav">
              {navItems.map(item => {
                const Icon = item.icon;
                return (
                  <Link key={item.path} to={item.path}
                    data-testid={`admin-nav-${item.label.toLowerCase().replace(/\s/g, '-')}`}
                    className={`flex items-center gap-2 px-3 py-2 rounded-sm text-sm font-medium transition-all ${
                      isActive(item.path)
                        ? 'bg-white/15 text-white'
                        : 'text-white/60 hover:bg-white/10 hover:text-white'
                    }`}>
                    <Icon size={16} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden lg:block text-right">
              <p className="text-xs text-white/70">Admin</p>
              <p className="text-xs text-white truncate max-w-[180px]">{user?.full_name || user?.email}</p>
            </div>
            <button onClick={handleLogout} data-testid="admin-logout-btn"
              className="hidden lg:flex items-center gap-2 px-3 py-2 rounded-sm text-sm font-medium text-white/70 hover:bg-white/10 hover:text-white">
              <LogOut size={16} />
              <span>Abmelden</span>
            </button>
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="lg:hidden text-white/70 hover:text-white p-1"
              data-testid="admin-mobile-menu-btn"
            >
              {mobileOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>
        {mobileOpen && (
          <div className="lg:hidden border-t border-white/10 bg-primary/95 backdrop-blur-sm" data-testid="admin-mobile-nav">
            <div className="px-4 py-3 border-b border-white/10">
              <p className="text-white/50 text-xs">Eingeloggt als</p>
              <p className="text-white font-medium text-sm truncate">{user?.full_name || user?.email}</p>
            </div>
            <nav className="px-3 py-3 space-y-1">
              {navItems.map(item => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileOpen(false)}
                    data-testid={`admin-mobile-nav-${item.label.toLowerCase().replace(/\s/g, '-')}`}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium transition-all ${
                      isActive(item.path)
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
                data-testid="admin-mobile-logout-btn"
                className="flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium text-white/60 hover:bg-white/10 hover:text-white w-full"
              >
                <LogOut size={16} />
                <span>Abmelden</span>
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
