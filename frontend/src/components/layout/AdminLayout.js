import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ShieldCheck, Users, FileText, Settings, LogOut, GraduationCap } from 'lucide-react';

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const navItems = [
    { path: '/admin', label: 'Dashboard', icon: ShieldCheck },
    { path: '/admin/users', label: 'Nutzer', icon: Users },
    { path: '/admin/audit', label: 'Audit Logs', icon: FileText },
  ];

  const handleLogout = async () => { await logout(); navigate('/'); };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <aside className="w-64 bg-slate-900 flex flex-col hidden lg:flex">
        <div className="p-4 border-b border-slate-800 flex items-center gap-2">
          <GraduationCap size={20} className="text-white" />
          <span className="text-white font-heading font-bold text-sm">W2G Admin</span>
        </div>
        <div className="px-4 py-3 border-b border-slate-800">
          <p className="text-slate-400 text-xs">Admin</p>
          <p className="text-white text-sm font-medium truncate">{user?.email}</p>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <Link key={item.path} to={item.path}
                data-testid={`admin-nav-${item.label.toLowerCase()}`}
                className="flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium text-slate-400 hover:bg-slate-800 hover:text-white transition-all">
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="px-3 py-4 border-t border-slate-800">
          <button onClick={handleLogout} data-testid="admin-logout-btn"
            className="flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium text-slate-400 hover:bg-slate-800 hover:text-white w-full">
            <LogOut size={18} />
            <span>Abmelden</span>
          </button>
        </div>
      </aside>
      <div className="flex-1 p-6">
        <Outlet />
      </div>
    </div>
  );
}
