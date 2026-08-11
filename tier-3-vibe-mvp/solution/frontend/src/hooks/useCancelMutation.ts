import { useMutation, useQueryClient } from '@tanstack/react-query';
import { cancelRegistration } from '../api/registrations';
import { eventKeys } from './queryKeys';

export function useCancelMutation(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => cancelRegistration(id),
    onSuccess: () => {
      // DELETE returns no body, so there's nothing to setQueryData with —
      // a refetch (via invalidate) is the only correct option here.
      void queryClient.invalidateQueries({ queryKey: eventKeys.detail(id) });
      void queryClient.invalidateQueries({ queryKey: eventKeys.list() });
    },
  });
}
