import { apiFetch, downloadFile } from './client';
import type { AttendeeDTO } from './types';

export function getAttendance(id: number): Promise<AttendeeDTO[]> {
  return apiFetch<AttendeeDTO[]>(`/event/${id}/attendance`);
}

export function downloadAttendanceCsv(id: number): Promise<{ blob: Blob; filename: string }> {
  return downloadFile(`/event/${id}/attendance/download`);
}
