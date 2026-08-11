import { getToken } from './tokenStore';
import type { ApiErrorDetail, ApiErrorEnvelope } from './types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details: ApiErrorDetail[] | null;

  constructor(envelope: ApiErrorEnvelope, status: number) {
    super(envelope.message);
    this.name = 'ApiError';
    this.code = envelope.error;
    this.status = status;
    this.details = envelope.details;
  }
}

/** A network-level failure (server unreachable, CORS, DNS) — distinct
 * from ApiError, which means the server responded but rejected the
 * request. Callers that want a generic "something went wrong" message
 * can catch Error broadly, but this lets them distinguish the two when
 * it matters (e.g. showing "check your connection" vs a validation
 * message). */
export class NetworkError extends Error {
  constructor(cause: unknown) {
    super('Could not reach the server.');
    this.name = 'NetworkError';
    this.cause = cause;
  }
}

interface ApiFetchInit extends Omit<RequestInit, 'body'> {
  body?: BodyInit | Record<string, unknown>;
  json?: boolean; // set false to skip JSON.stringify/Content-Type for FormData bodies
}

async function apiFetch<T>(path: string, init: ApiFetchInit = {}): Promise<T> {
  const { body, json = true, headers, ...rest } = init;
  const token = getToken();

  const finalHeaders: HeadersInit = {
    Accept: 'application/json',
    ...(json && body !== undefined ? { 'Content-Type': 'application/json' } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...headers,
  };

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...rest,
      headers: finalHeaders,
      body: json && body !== undefined ? JSON.stringify(body) : (body as BodyInit | undefined),
    });
  } catch (cause) {
    throw new NetworkError(cause);
  }

  if (!response.ok) {
    let envelope: ApiErrorEnvelope;
    try {
      envelope = (await response.json()) as ApiErrorEnvelope;
    } catch {
      envelope = { error: 'unknown_error', message: response.statusText, details: null };
    }
    throw new ApiError(envelope, response.status);
  }

  // 204 No Content (DELETE /event/:id/register) — no body to parse.
  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

/** For the one non-JSON endpoint: GET /event/:id/attendance/download.
 * Reads the response as a Blob and extracts the filename the backend
 * set in Content-Disposition, so the caller can trigger a real browser
 * download without rebuilding anything client-side. */
async function downloadFile(path: string): Promise<{ blob: Blob; filename: string }> {
  const token = getToken();
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  } catch (cause) {
    throw new NetworkError(cause);
  }

  if (!response.ok) {
    let envelope: ApiErrorEnvelope;
    try {
      envelope = (await response.json()) as ApiErrorEnvelope;
    } catch {
      envelope = { error: 'unknown_error', message: response.statusText, details: null };
    }
    throw new ApiError(envelope, response.status);
  }

  const disposition = response.headers.get('Content-Disposition') ?? '';
  const match = /filename="?([^"]+)"?/.exec(disposition);
  const filename = match?.[1] ?? 'attendance.csv';
  const blob = await response.blob();
  return { blob, filename };
}

export { apiFetch, downloadFile };
