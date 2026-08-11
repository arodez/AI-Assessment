import { createContext, useContext } from 'react';
import type { LoginUser } from '../api/types';

export interface AuthContextValue {
  token: string | null;
  user: LoginUser | null;
  login: (email: string) => Promise<void>;
  logout: () => void;
}

// Split from AuthProvider.tsx (rather than one file exporting both the
// context/hook and the provider component) so React Fast Refresh can
// reliably hot-reload the provider component on its own.
export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (ctx === null) {
    // Fail loud in dev rather than silently returning undefined — a
    // component rendered outside <AuthProvider> is a real bug.
    throw new Error('useAuth() must be used within an <AuthProvider>.');
  }
  return ctx;
}
