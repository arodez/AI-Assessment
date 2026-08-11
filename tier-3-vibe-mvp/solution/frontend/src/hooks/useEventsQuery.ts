import { useQuery } from '@tanstack/react-query';
import { listEvents } from '../api/events';
import { eventKeys } from './queryKeys';

export function useEventsQuery() {
  return useQuery({ queryKey: eventKeys.list(), queryFn: listEvents });
}
