import { useMutation, useQueryClient } from '@tanstack/react-query';
import { registerForEvent } from '../api/registrations';
import { eventKeys } from './queryKeys';

export function useRegisterMutation(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => registerForEvent(id),
    onSuccess: (updatedEvent) => {
      // The API returns the full updated event — an instant UI update via
      // setQueryData, no refetch round-trip needed for the detail view.
      queryClient.setQueryData(eventKeys.detail(id), updatedEvent);
      // The list is invalidated (not patched in place) so every card's
      // remaining_spots/viewer_status stays correct without hand-writing
      // a "find this event in the array and patch it" reducer.
      void queryClient.invalidateQueries({ queryKey: eventKeys.list() });
    },
  });
}
