import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ShieldCheck, Users, FileText, LogOut, GraduationCap, LayoutDashboard } from 'lucide-react';

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/admin', label: 'Dashboard', icon: LayoutDashboard, exact: true },
    { path: '/admin/users', label: 'Nutzer', icon: Users },
    { path: '/admin/audit', label: 'Audit Logs', icon: FileText },
    { path: '/staff', label: 'Staff Hub', icon: ShieldCheck },
  ];
  const isActive = (item) => item.exact ? location.pathname === item.path : location.pathname.startsWith(item.path);

  const handleLogout = async () => { await logout(); navigate('/'); };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col" data-testid="admin-layout">
      <header className="bg-primary sticky top-0 z-50 shadow-sm">
        <div className="max-w-screen-2xl mx-auto h-14 px-4 lg:px-6 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-white">
            <GraduationCap size={20} />
            <span className="font-heading font-bold text-sm">W2G Admin</span>
          </Link>
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map(item => {
              const Icon = item.icon;
              return (
                <Link key={item.path} to={item.path}
                  data-testid={`admin-nav-${item.label.toLowerCase().replace(/\s/g, '-')}`}
                  className={`flex items-center gap-2 px-3 py-2 rounded-sm text-sm font-medium transition-all ${
                    isActive(item) ? 'bg-white/15 text-white' : 'text-white/70 hover:bg-white/10 hover:text-white'
                  }`}>
                  <Icon size={16} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
          <div className="flex items-center gap-3">
            <div className="hidden lg:block text-right">
              <p className="text-xs text-white/50">Admin</p>
              <p className="text-xs text-white truncate max-w-[180px]">{user?.email}</p>
            </div>
            <button onClick={handleLogout} data-testid="admin-logout-btn"
              className="flex items-center gap-2 px-3 py-1.5 rounded-sm text-sm font-medium text-white/70 hover:bg-white/10 hover:text-white">
              <LogOut size={16} />
              <span>Abmelden</span>
            </button>
          </div>
        </div>
      </header>
      <main className="flex-1 w-full max-w-screen-2xl mx-auto p-4 lg:p-6">
        <nav className="md:hidden mb-4 grid grid-cols-2 gap-2">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <Link key={item.path} to={item.path}
                data-testid={`admin-mobile-nav-${item.label.toLowerCase().replace(/\s/g, '-')}`}
                className={`flex items-center gap-2 px-3 py-2 rounded-sm text-sm font-medium border transition-all ${
                  isActive(item)
                    ? 'border-primary/30 text-primary bg-primary/5'
                    : 'border-slate-200 text-slate-600 hover:border-primary/30'
                }`}>
                <Icon size={16} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <Outlet />
      </main>
    </div>
  );
}
