import { useQuery } from '@tanstack/react-query';
import { getAttendance } from '../api/attendance';
import { eventKeys } from './queryKeys';

export function useAttendanceQuery(id: number) {
  return useQuery({ queryKey: eventKeys.attendance(id), queryFn: () => getAttendance(id) });
}
