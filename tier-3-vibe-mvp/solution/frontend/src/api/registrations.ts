import { apiFetch } from './client';
import type { EventDTO } from './types';

/** Acts on the caller's own registration (identity comes from the JWT,
 * not the request body) — returns the updated event so the caller can
 * update the UI instantly without a second round-trip. */
export function registerForEvent(id: number): Promise<EventDTO> {
  return apiFetch<EventDTO>(`/event/${id}/register`, { method: 'POST' });
}

/** 204 No Content — client.ts returns undefined without attempting to
 * parse a body. */
export function cancelRegistration(id: number): Promise<void> {
  return apiFetch<void>(`/event/${id}/register`, { method: 'DELETE' });
}
