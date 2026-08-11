/**
 * Deliberately NOT a React module — a plain module-level variable client.ts
 * reads from. Keeps the fetch layer free of any React dependency, which
 * avoids a circular import with AuthContext (AuthProvider is the only
 * thing that calls setToken/clearToken; client.ts only ever reads it).
 */

let currentToken: string | null = null;

export function setToken(token: string | null): void {
  currentToken = token;
}

export function getToken(): string | null {
  return currentToken;
}
