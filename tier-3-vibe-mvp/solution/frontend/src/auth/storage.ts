import type { LoginUser } from '../api/types';

const STORAGE_KEY = 'eventsHubAuth';

export interface StoredAuth {
  token: string;
  user: LoginUser;
}

/** Single JSON blob under one key — not the mockup's separate
 * eventsHubRole/eventsHubEmail keys, which could be left inconsistent by
 * a partial write (e.g. a failure between setting the two). */
export function readStoredAuth(): StoredAuth | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as StoredAuth;
    if (typeof parsed.token !== 'string' || typeof parsed.user?.id !== 'number') {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function writeStoredAuth(auth: StoredAuth): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
}

export function clearStoredAuth(): void {
  localStorage.removeItem(STORAGE_KEY);
}
