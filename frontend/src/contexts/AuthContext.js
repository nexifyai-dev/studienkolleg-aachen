import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import apiClient from '../lib/apiClient';

const API = process.env.REACT_APP_BACKEND_URL;
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(undefined);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const { data } = await apiClient.get('/api/auth/me');
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { checkAuth(); }, [checkAuth]);

  const login = async (email, password) => {
    // Login uses raw axios (no interceptor loop needed – this IS the auth call)
    const { data } = await axios.post(`${API}/api/auth/login`, { email, password }, { withCredentials: true });
    setUser(data);
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
