import { useCallback, useMemo, useState, type ReactNode } from 'react';
import { login as loginRequest } from '../api/auth';
import { setToken as setStoredToken } from '../api/tokenStore';
import { AuthContext, type AuthContextValue } from './AuthContext';
import { clearStoredAuth, readStoredAuth, writeStoredAuth, type StoredAuth } from './storage';
import type { LoginUser } from '../api/types';

function initialAuth(): StoredAuth | null {
  const stored = readStoredAuth();
  // Prime tokenStore synchronously, in the same tick as the initial
  // render — not inside a useEffect — so the very first React Query
  // request fired by a page under <RequireAuth> already has the token,
  // and so there's no render where an already-logged-in user briefly
  // sees the login page before auth state catches up.
  setStoredToken(stored?.token ?? null);
  return stored;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<StoredAuth | null>(initialAuth);

  const login = useCallback(async (email: string) => {
    const response = await loginRequest(email);
    const nextAuth: StoredAuth = { token: response.access_token, user: response.user };
    setStoredToken(nextAuth.token);
    writeStoredAuth(nextAuth);
    setAuth(nextAuth);
  }, []);

  const logout = useCallback(() => {
    setStoredToken(null);
    clearStoredAuth();
    setAuth(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      token: auth?.token ?? null,
      user: (auth?.user ?? null) as LoginUser | null,
      login,
      logout,
    }),
    [auth, login, logout],
  );

  return <AuthContext value={value}>{children}</AuthContext>;
}
