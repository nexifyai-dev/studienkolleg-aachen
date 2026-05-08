import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { User, Mail, Globe, Shield, LogOut, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PageScaffold } from '../../components/layout/PageScaffold';
import { Card } from '../../components/ui/card';

export default function ApplicantMorePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const menuItems = [
    { icon: <User size={14} />, label: 'Profil bearbeiten', desc: 'Name, Kontaktdaten, Nationalitaet', path: '/portal/settings' },
    { icon: <Mail size={14} />, label: 'Benachrichtigungen', desc: 'E-Mail-Einstellungen verwalten', path: '/portal/settings' },
    { icon: <Globe size={14} />, label: 'Sprache', desc: 'Deutsch / English', path: '/portal/settings' },
    { icon: <Shield size={14} />, label: 'Datenschutz & Sicherheit', desc: 'Passwort aendern, Datenexport', path: '/portal/settings' },
  ];

  return (
    <PageScaffold
      title="Mehr"
      subtitle="Konto, Einstellungen und Hilfe"
      testId="applicant-more-page"
    >
      {/* User Card */}
      <Card className="flex items-center gap-3 p-4 mb-4" data-testid="more-user-card">
        <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center">
          <User size={18} className="text-[var(--color-primary)]" />
        </div>
        <div>
          <p className="text-sm font-semibold text-[var(--color-text-primary)]">{user?.full_name || user?.email}</p>
          <p className="text-[11px] text-[var(--color-text-tertiary)]">{user?.email}</p>
        </div>
      </Card>

      {/* Menu Items */}
      <div className="space-y-1">
        {menuItems.map((item, i) => (
          <Card
            key={i}
            onClick={() => navigate(item.path)}
            className="flex items-center gap-3 text-left cursor-pointer hover:border-[var(--color-primary)] transition-colors p-3"
            data-testid={`more-item-${i}`}
          >
            <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--color-surface-sunken)] flex items-center justify-center text-[var(--color-primary)]">
              {item.icon}
            </div>
            <div className="flex-1">
              <p className="text-xs font-medium text-[var(--color-text-primary)]">{item.label}</p>
              <p className="text-[10px] text-[var(--color-text-tertiary)]">{item.desc}</p>
            </div>
            <ChevronRight size={12} className="text-[var(--color-text-tertiary)]" />
          </Card>
        ))}
      </div>

      {/* Logout */}
      <Card
        onClick={() => { logout(); navigate('/'); }}
        className="flex items-center gap-3 text-left cursor-pointer hover:border-[var(--color-danger)] transition-colors p-3 mt-1"
        data-testid="more-logout"
      >
        <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--color-primary-muted)] flex items-center justify-center text-[var(--color-primary)]">
          <LogOut size={14} />
        </div>
        <span className="text-xs font-medium text-[var(--color-danger)]">Abmelden</span>
      </Card>
    </PageScaffold>
  );
}
