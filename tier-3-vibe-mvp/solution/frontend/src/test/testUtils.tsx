import { QueryClient } from '@tanstack/react-query';

/** Fresh, retry-disabled QueryClient per test — the app's real defaults
 * (retry: 1, 15s staleTime) would make failure-path tests slow and
 * occasionally flaky under fake/real timers. */
export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
}
