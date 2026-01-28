import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { authService } from '../services/api';
import type { User } from '../types';
import { useAppStore } from '../stores/appStore';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const setUserInStore = useAppStore((state) => state.setUser);
  const setAuthenticatedInStore = useAppStore((state) => state.setAuthenticated);

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        if (token) {
          const userProfile = await authService.getProfile();
          setUser(userProfile as User);
          setIsAuthenticated(true);
          setUserInStore(userProfile as User);
          setAuthenticatedInStore(true);
        }
      } catch {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        setIsAuthenticated(false);
        setUserInStore(null);
        setAuthenticatedInStore(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const response = await authService.login({ email, password });
    localStorage.setItem('auth_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    
    const userProfile = await authService.getProfile();
    setUser(userProfile as User);
    setIsAuthenticated(true);
    setUserInStore(userProfile as User);
    setAuthenticatedInStore(true);
  }, [setAuthenticatedInStore, setUserInStore]);

  const logout = useCallback(async () => {
    try {
      const refresh_token = localStorage.getItem('refresh_token');
      if (refresh_token) {
        await authService.logout();
      }
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      setIsAuthenticated(false);
      setUserInStore(null);
      setAuthenticatedInStore(false);
    }
  }, [setAuthenticatedInStore, setUserInStore]);

  const register = useCallback(async (email: string, password: string, name: string) => {
    const response = await authService.register({ email, password, name });
    localStorage.setItem('auth_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    
    const userProfile = await authService.getProfile();
    setUser(userProfile as User);
    setIsAuthenticated(true);
    setUserInStore(userProfile as User);
    setAuthenticatedInStore(true);
  }, [setAuthenticatedInStore, setUserInStore]);

  const refreshUser = useCallback(async () => {
    try {
      const userProfile = await authService.getProfile();
      setUser(userProfile as User);
      setUserInStore(userProfile as User);
      setAuthenticatedInStore(true);
    } catch {
      // If refresh fails, user might be logged out
      setUser(null);
      setIsAuthenticated(false);
      setUserInStore(null);
      setAuthenticatedInStore(false);
    }
  }, [setAuthenticatedInStore, setUserInStore]);

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    register,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export type { User, AuthContextType };
