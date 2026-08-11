import { apiFetch } from './client';
import type { LoginResponse } from './types';

export function login(email: string): Promise<LoginResponse> {
  return apiFetch<LoginResponse>('/login', {
    method: 'POST',
    body: { email },
  });
}
