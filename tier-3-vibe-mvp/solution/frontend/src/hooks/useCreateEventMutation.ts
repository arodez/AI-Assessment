import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createEvent } from '../api/events';
import { eventKeys } from './queryKeys';

export function useCreateEventMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData: FormData) => createEvent(formData),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: eventKeys.list() });
    },
  });
}
