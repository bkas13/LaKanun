'use client'
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api, ApiError, setTokens, clearTokens, getAccessToken } from '../lib/api';

interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  language_pref?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      setLoading(true);
      const data = await api<User>('/api/v1/auth/me');
      setUser(data);
      setError(null);
    } catch (err) {
      clearTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string, rememberMe: boolean = false) => {
    const data = await api<{ access_token: string; refresh_token: string; token_type: string; expires_in: number }>('/api/v1/auth/login', {
      method: 'POST',
      body: { email, password },
      noAuth: true,
    });
    setTokens(data.access_token, data.refresh_token);
    await fetchUser();
  };

  const register = async (name: string, email: string, password: string) => {
    const data = await api<{ access_token: string; refresh_token: string; token_type: string; expires_in: number }>('/api/v1/auth/register', {
      method: 'POST',
      body: { email, name, password },
      noAuth: true,
    });
    setTokens(data.access_token, data.refresh_token);
    await fetchUser();
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  const refreshUser = async () => {
    await fetchUser();
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
