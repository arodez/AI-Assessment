import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiFetch, ApiError, NetworkError } from './client';
import { setToken } from './tokenStore';

function mockFetchOnce(response: Partial<Response>) {
  const fetchMock = vi.fn().mockResolvedValue(response as Response);
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

describe('apiFetch', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    setToken(null);
  });

  it('attaches the Authorization header when a token is set', async () => {
    setToken('abc123');
    const fetchMock = mockFetchOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ id: 1 }),
    });

    await apiFetch('/events');

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = init.headers as Record<string, string>;
    expect(headers.Authorization).toBe('Bearer abc123');
  });

  it('omits the Authorization header when no token is set', async () => {
    const fetchMock = mockFetchOnce({ ok: true, status: 200, json: () => Promise.resolve([]) });

    await apiFetch('/events');

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = init.headers as Record<string, string>;
    expect(headers.Authorization).toBeUndefined();
  });

  it('parses a non-2xx response into an ApiError carrying code/status/details', async () => {
    mockFetchOnce({
      ok: false,
      status: 400,
      json: () =>
        Promise.resolve({
          error: 'validation_error',
          message: 'Title is required.',
          details: [{ field: 'title', message: 'Title is required.' }],
        }),
    });

    await expect(apiFetch('/event')).rejects.toMatchObject({
      name: 'ApiError',
      code: 'validation_error',
      status: 400,
      message: 'Title is required.',
      details: [{ field: 'title', message: 'Title is required.' }],
    });
  });

  it('falls back to a generic envelope when the error body is not JSON', async () => {
    mockFetchOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: () => Promise.reject(new Error('not json')),
    });

    await expect(apiFetch('/events')).rejects.toMatchObject({
      code: 'unknown_error',
      status: 500,
    });
  });

  it('returns undefined for a 204 response without attempting to parse a body', async () => {
    const json = vi.fn();
    mockFetchOnce({ ok: true, status: 204, json });

    const result = await apiFetch('/event/1/register', { method: 'DELETE' });

    expect(result).toBeUndefined();
    expect(json).not.toHaveBeenCalled();
  });

  it('wraps a fetch-level failure in a NetworkError', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));

    await expect(apiFetch('/events')).rejects.toBeInstanceOf(NetworkError);
  });
});

describe('ApiError', () => {
  it('carries the envelope fields as instance properties', () => {
    const error = new ApiError(
      { error: 'event_full', message: 'This event is full.', details: null },
      400,
    );

    expect(error.code).toBe('event_full');
    expect(error.status).toBe(400);
    expect(error.message).toBe('This event is full.');
    expect(error.details).toBeNull();
  });
});
