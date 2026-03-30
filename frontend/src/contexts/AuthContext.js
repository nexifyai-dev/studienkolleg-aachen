import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import apiClient, { resolveApiUrl } from '../lib/apiClient';
import i18n from '../i18n';

const AuthContext = createContext(null);

function syncLanguage(userData) {
  if (userData?.language_pref && i18n.language !== userData.language_pref) {
    i18n.changeLanguage(userData.language_pref);
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(undefined);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const { data } = await apiClient.get('/api/auth/me');
      setUser(data);
      syncLanguage(data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { checkAuth(); }, [checkAuth]);

  const login = async (email, password) => {
    const { data } = await axios.post(resolveApiUrl('/api/auth/login'), { email, password }, { withCredentials: true });
    setUser(data);
    syncLanguage(data);
    return data;
  };

  const logout = async () => {
    try { await apiClient.post('/api/auth/logout', {}); } catch {}
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const { data } = await apiClient.get('/api/auth/me');
      setUser(data);
      syncLanguage(data);
      return data;
    } catch {
      setUser(null);
      return null;
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}

export function formatApiError(detail) {
  if (!detail) return 'Ein Fehler ist aufgetreten. Bitte versuche es erneut.';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map(e => e?.msg || JSON.stringify(e)).join(' ');
  if (detail?.msg) return detail.msg;
  return String(detail);
}
