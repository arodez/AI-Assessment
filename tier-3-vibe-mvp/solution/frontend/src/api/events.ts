import { apiFetch } from './client';
import type { EventDTO } from './types';

export function listEvents(): Promise<EventDTO[]> {
  return apiFetch<EventDTO[]>('/events');
}

export function getEvent(id: number): Promise<EventDTO> {
  return apiFetch<EventDTO>(`/event/${id}/details`);
}

/** Caller builds the multipart FormData (see CreateEventForm/buildFormData.ts)
 * — this just posts it as-is, with json:false so client.ts skips
 * JSON.stringify/Content-Type (the browser sets the correct multipart
 * boundary header itself when given a FormData body). */
export function createEvent(formData: FormData): Promise<EventDTO> {
  return apiFetch<EventDTO>('/event', {
    method: 'POST',
    body: formData,
    json: false,
  });
}
