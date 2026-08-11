/**
 * Typed 1:1 against solution/backend/docs/API.md.
 *
 * ViewerStatus and AttendanceStatus are deliberately NOT the same union.
 * They come from different endpoints, describe different things, and use
 * different casing:
 *
 * - ViewerStatus ("confirmed"|"cancelled"|null): from GET /events and
 *   GET /event/:id/details. Answers "is the person making THIS request
 *   registered for this event?" — computed per-viewer, can be null (no
 *   registration exists at all).
 * - AttendanceStatus ("Confirmed"|"Cancelled"): from the admin-only
 *   GET /event/:id/attendance roster. Answers "for each person who has
 *   ever registered, what's their status?" — one value per roster row,
 *   never null (a roster row only exists because someone registered).
 *
 * Unifying these into one type would either wrongly allow null on a
 * roster row or wrongly reject the API's real lowercase viewer values.
 */

export type EventType = 'study_group' | 'ama' | 'workshop' | 'social' | 'other';
export type LocationType = 'in_person' | 'hybrid' | 'virtual';
export type ViewerStatus = 'confirmed' | 'cancelled' | null;
export type AttendanceStatus = 'Confirmed' | 'Cancelled';

export interface EventDTO {
  id: number;
  title: string;
  start: string;
  end: string;
  spots: number;
  remaining_spots: number;
  event_type: EventType;
  location_type: LocationType;
  description: string | null;
  image_url: string | null;
  location: string[];
  host_name: string | null;
  host_team: string | null;
  viewer_status: ViewerStatus;
  created_at: string;
  updated_at: string;
}

export interface AttendeeDTO {
  full_name: string;
  email: string;
  sign_up_at: string;
  status: AttendanceStatus;
}

export interface LoginUser {
  id: number;
  first_name: string;
  is_admin: boolean;
}

export interface LoginResponse {
  access_token: string;
  user: LoginUser;
}

export interface ApiErrorDetail {
  field: string;
  message: string;
}

export interface ApiErrorEnvelope {
  error: string;
  message: string;
  details: ApiErrorDetail[] | null;
}
