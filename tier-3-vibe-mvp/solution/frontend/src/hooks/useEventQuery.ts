import { useQuery } from '@tanstack/react-query';
import { getEvent } from '../api/events';
import { eventKeys } from './queryKeys';

export function useEventQuery(id: number) {
  return useQuery({ queryKey: eventKeys.detail(id), queryFn: () => getEvent(id) });
}
