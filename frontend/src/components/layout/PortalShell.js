import React, { useMemo, useState, useEffect, useRef, useCallback } from 'react';
import { Link, Outlet, useLocation, useNavigate, useParams } from 'react-router-dom';
import { ChevronDown, Globe, GraduationCap, LogOut, Menu, PanelLeftClose, PanelLeftOpen, User, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import NotificationBell from '../shared/NotificationBell';
import BrainPanel from '../shared/BrainPanel';

const LANG_OPTIONS = [
  { code: 'de', label: 'DE' },
  { code: 'en', label: 'EN' },
];

const SIDEBAR_EXPANDED = 240;
const SIDEBAR_COLLAPSED = 64;

function isItemActive(item, pathname) {
  if (item.exact) return pathname === item.path;
  if (item.matchPaths?.length) return item.matchPaths.some((p) => pathname.startsWith(p));
  return pathname.startsWith(item.path);
}

export function PortalShell({
  portalName,
  logoHref,
  navItems,
  mobileBottomNav = [],
  dataTestId,
  hideLanguageSwitch = false,
}) {
  const { i18n } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const userMenuRef = useRef(null);

  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(() => {
    try {
      const stored = localStorage.getItem('w2g_sidebar_collapsed');
      return stored === null ? true : stored === 'true';
    } catch { return true; }
  });

  useEffect(() => {
    try { localStorage.setItem('w2g_sidebar_collapsed', String(collapsed)); } catch {}
  }, [collapsed]);

  useEffect(() => { setMobileOpen(false); setUserMenuOpen(false); }, [location.pathname]);

  useEffect(() => {
    if (!userMenuOpen) return;
    const handler = (e) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) setUserMenuOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [userMenuOpen]);

  const desktopItems = useMemo(() => navItems.filter((i) => !i.mobileOnly), [navItems]);
  const mobileItems = useMemo(() => navItems.filter((i) => !i.desktopOnly), [navItems]);

  const handleLogout = useCallback(async () => { await logout(); navigate('/'); }, [logout, navigate]);

  const initials = user?.full_name?.trim()?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U';
  const sidebarWidth = collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_EXPANDED;

  return (
    <div className="min-h-screen bg-[var(--color-shell-bg)]" data-testid={dataTestId}>

      {/* ═══ TOPBAR ═══ */}
      <header className="w2g-topbar-frame" data-testid={`${dataTestId}-topbar`}>
        <div className="flex items-center justify-between h-full px-4 lg:px-5 gap-4" style={{ minHeight: 'inherit' }}>
          <div className="flex items-center gap-3 min-w-0">
            <Link to={logoHref} className="flex items-center gap-2.5 shrink-0" data-testid={`${dataTestId}-logo`}>
              <div className="w-9 h-9 bg-[var(--color-primary)] flex items-center justify-center shrink-0" style={{ borderRadius: 'var(--radius-md)' }}>
                <GraduationCap size={18} className="text-white" />
              </div>
              <div className="hidden sm:block min-w-0">
                <p className="text-[10px] font-extrabold uppercase tracking-[0.14em] text-[var(--color-primary)] font-heading leading-none">Way2Germany</p>
                <p className="text-[10px] font-medium text-[var(--color-text-tertiary)] truncate mt-0.5">{portalName}</p>
              </div>
            </Link>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <div className="hidden sm:block"><NotificationBell /></div>

            {!hideLanguageSwitch && (
              <div className="hidden md:flex items-center border border-[var(--color-divider)] bg-white p-0.5" style={{ borderRadius: 'var(--radius-sm)' }} data-testid={`${dataTestId}-language-switch`}>
                {LANG_OPTIONS.map((lang) => (
                  <button key={lang.code} type="button" onClick={() => i18n.changeLanguage(lang.code)}
                    data-testid={`${dataTestId}-lang-${lang.code}`}
                    className={i18n.language === lang.code ? 'w2g-lang-pill w2g-lang-pill-active' : 'w2g-lang-pill'}>
                    {lang.label}
                  </button>
                ))}
              </div>
            )}

            <div className="hidden md:block relative" ref={userMenuRef}>
              <button type="button" onClick={() => setUserMenuOpen((o) => !o)}
                className="flex items-center gap-2 border border-[var(--color-divider)] bg-white px-2 py-1.5 hover:border-[var(--color-primary)] transition-colors"
                style={{ borderRadius: 'var(--radius-md)' }} data-testid={`${dataTestId}-user-menu-button`}>
                <div className="h-7 w-7 flex items-center justify-center bg-[var(--color-primary)] text-[10px] font-bold text-white" style={{ borderRadius: 'var(--radius-sm)' }}>{initials}</div>
                <span className="hidden xl:block max-w-[120px] truncate text-xs font-semibold text-[var(--color-text-primary)]">{user?.full_name || user?.email}</span>
                <ChevronDown size={11} className={`text-[var(--color-text-tertiary)] transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
              </button>
              {userMenuOpen && (
                <div className="absolute right-0 top-[calc(100%+6px)] min-w-[220px] border border-[var(--color-divider)] bg-white overflow-hidden"
                  style={{ borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-e4)', zIndex: 90 }} data-testid={`${dataTestId}-user-dropdown`}>
                  <div className="border-b border-[var(--color-divider-subtle)] px-4 py-3">
                    <p className="text-sm font-semibold text-[var(--color-text-primary)]">{user?.full_name || user?.email}</p>
                    <p className="text-xs text-[var(--color-text-secondary)]">{user?.email}</p>
                  </div>
                  <button type="button" onClick={handleLogout} data-testid={`${dataTestId}-logout-button`}
                    className="flex w-full items-center gap-2 px-4 py-3 text-sm text-[var(--color-text-secondary)] hover:bg-[var(--color-danger-bg)] hover:text-[var(--color-danger)] transition-colors">
                    <LogOut size={14} /> Abmelden
                  </button>
                </div>
              )}
            </div>

            <button type="button" onClick={() => setMobileOpen((o) => !o)}
              className="inline-flex h-9 w-9 items-center justify-center border border-[var(--color-divider)] bg-white lg:hidden"
              style={{ borderRadius: 'var(--radius-sm)' }} data-testid={`${dataTestId}-mobile-toggle`}>
              {mobileOpen ? <X size={16} className="text-[var(--color-text-secondary)]" /> : <Menu size={16} className="text-[var(--color-text-secondary)]" />}
            </button>
          </div>
        </div>
      </header>

      {/* ═══ SIDEBAR (Desktop) ═══ */}
      <aside
        className="hidden lg:flex flex-col fixed bottom-0 left-0 bg-[var(--color-surface)] border-r border-[var(--color-divider)]"
        style={{ top: 'var(--topbar-height)', width: `${sidebarWidth}px`, transition: 'width 200ms ease-out', zIndex: 50 }}
        data-testid={`${dataTestId}-sidebar`}
      >
        <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto overflow-x-hidden" data-testid={`${dataTestId}-sidebar-nav`}>
          {desktopItems.map((item) => {
            const active = isItemActive(item, location.pathname);
            const Icon = item.icon || User;
            return (
              <Link key={item.path} to={item.path}
                data-testid={`${dataTestId}-sidebar-${item.testId || item.label.toLowerCase().replace(/[^a-z0-9]+/gi, '-')}`}
                title={collapsed ? item.label : undefined}
                className={`flex items-center gap-3 text-[13px] font-medium transition-all ${
                  active
                    ? 'bg-[var(--color-primary)] text-white'
                    : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-sunken)] hover:text-[var(--color-primary)]'
                }`}
                style={{
                  borderRadius: 'var(--radius-md)',
                  padding: collapsed ? '10px 0' : '10px 12px',
                  justifyContent: collapsed ? 'center' : 'flex-start',
                  minHeight: '40px',
                }}>
                <Icon size={18} className="shrink-0" />
                {!collapsed && <span className="truncate whitespace-nowrap">{item.label}</span>}
                {!collapsed && item.badge > 0 && (
                  <span className="ml-auto text-[10px] font-bold px-1.5 py-0.5 tabular-nums shrink-0"
                    style={{
                      borderRadius: 'var(--radius-full)',
                      background: active ? 'rgba(255,255,255,0.2)' : 'var(--color-danger-bg)',
                      color: active ? '#fff' : 'var(--color-danger)',
                    }}>{item.badge}</span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-[var(--color-divider)] p-2">
          <button type="button" onClick={() => setCollapsed((c) => !c)}
            data-testid={`${dataTestId}-sidebar-toggle`}
            title={collapsed ? 'Sidebar ausklappen' : 'Sidebar einklappen'}
            className="flex items-center gap-3 w-full text-[12px] font-medium text-[var(--color-text-tertiary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-sunken)] transition-all"
            style={{
              borderRadius: 'var(--radius-md)',
              padding: collapsed ? '10px 0' : '10px 12px',
              justifyContent: collapsed ? 'center' : 'flex-start',
              minHeight: '38px',
            }}>
            {collapsed ? <PanelLeftOpen size={16} className="shrink-0" /> : <PanelLeftClose size={16} className="shrink-0" />}
            {!collapsed && <span className="whitespace-nowrap">Einklappen</span>}
          </button>
        </div>
      </aside>

      {/* ═══ MOBILE OVERLAY ═══ */}
      {mobileOpen && (
        <div className="fixed inset-0 lg:hidden" style={{ zIndex: 65 }} data-testid={`${dataTestId}-mobile-menu`}>
          <div className="absolute inset-0 bg-[rgba(12,29,46,0.4)]" style={{ backdropFilter: 'blur(3px)' }} onClick={() => setMobileOpen(false)} />
          <div className="absolute left-0 right-0 bg-white border-b border-[var(--color-divider)] max-h-[75vh] overflow-y-auto animate-slide-up"
            style={{ top: 'var(--topbar-height-mobile, 56px)', boxShadow: 'var(--shadow-e3)' }}>
            <div className="px-4 py-3 border-b border-[var(--color-divider-subtle)] flex items-center gap-3">
              <div className="h-9 w-9 flex items-center justify-center bg-[var(--color-primary)] text-sm font-bold text-white shrink-0" style={{ borderRadius: 'var(--radius-sm)' }}>{initials}</div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-[var(--color-text-primary)]">{user?.full_name || user?.email}</p>
                <p className="truncate text-xs text-[var(--color-text-tertiary)]">{user?.email}</p>
              </div>
            </div>

            {!hideLanguageSwitch && (
              <div className="px-4 py-2.5 border-b border-[var(--color-divider-subtle)] flex items-center justify-between">
                <span className="flex items-center gap-2 text-sm font-medium text-[var(--color-text-secondary)]"><Globe size={14} /> Sprache</span>
                <div className="flex gap-1">
                  {LANG_OPTIONS.map((lang) => (
                    <button key={lang.code} type="button" onClick={() => i18n.changeLanguage(lang.code)}
                      data-testid={`${dataTestId}-mobile-lang-${lang.code}`}
                      className={i18n.language === lang.code ? 'w2g-lang-pill w2g-lang-pill-active' : 'w2g-lang-pill'}>
                      {lang.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <nav className="p-3 space-y-0.5">
              {mobileItems.map((item) => {
                const active = isItemActive(item, location.pathname);
                const Icon = item.icon || User;
                return (
                  <Link key={item.path} to={item.path} onClick={() => setMobileOpen(false)}
                    data-testid={`${dataTestId}-mobile-nav-${item.testId || item.label.toLowerCase().replace(/[^a-z0-9]+/gi, '-')}`}
                    className={`flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors ${
                      active ? 'bg-[var(--color-primary)] text-white' : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-sunken)]'
                    }`} style={{ borderRadius: 'var(--radius-sm)' }}>
                    <Icon size={16} className="shrink-0" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            <div className="p-3 border-t border-[var(--color-divider-subtle)]">
              <button type="button" onClick={handleLogout} data-testid={`${dataTestId}-mobile-logout-button`}
                className="flex w-full items-center justify-center gap-2 border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] px-4 py-3 text-sm font-medium text-[var(--color-danger)]"
                style={{ borderRadius: 'var(--radius-md)' }}>
                <LogOut size={14} /> Abmelden
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ═══ MAIN CONTENT ═══ */}
      <main
        className="w2g-sidebar-offset min-h-screen"
        style={{ '--sb-w': `${sidebarWidth}px`, paddingTop: 'calc(var(--topbar-height) + 20px)', paddingBottom: mobileBottomNav.length ? '96px' : '32px' }}
      >
        <div className="px-4 sm:px-5 lg:px-6 mx-auto" style={{ maxWidth: 'calc(var(--shell-max-width) + 48px)' }}>
          <Outlet />
        </div>
        {/* Brain KI-Assistent – nur fuer Staff/Admin */}
        {user && ['staff', 'admin', 'superadmin', 'accounting_staff'].includes(user.role) && (
          <BrainPanel
            entityId={location.pathname.match(/\/staff\/cases\/([a-f0-9]{24})/)?.[1] || ''}
            context={`Aktuelle Seite: ${location.pathname}`}
          />
        )}
      </main>

      {/* ═══ BOTTOM NAV (Mobile) ═══ */}
      {mobileBottomNav.length > 0 && (
        <nav className="w2g-bottom-nav lg:hidden" data-testid={`${dataTestId}-bottom-nav`}>
          {mobileBottomNav.map((item) => {
            const active = isItemActive(item, location.pathname);
            const Icon = item.icon || User;
            return (
              <Link key={item.path} to={item.path}
                data-testid={`${dataTestId}-bottom-nav-${item.testId || item.label.toLowerCase().replace(/[^a-z0-9]+/gi, '-')}`}
                className={`w2g-bottom-nav-item ${active ? 'w2g-bottom-nav-item-active' : ''}`}>
                <Icon size={16} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      )}
    </div>
  );
}
