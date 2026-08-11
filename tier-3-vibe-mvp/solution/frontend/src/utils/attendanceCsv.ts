import type { AttendeeDTO } from '../api/types';

// Only quote a field that contains a comma, quote, or newline — matches
// Python's csv.writer default (QUOTE_MINIMAL) behavior used by the
// backend's own export (see app/services/csv_export.py), so "Copy to
// clipboard" produces text consistent with what "Export CSV" downloads.
function escapeCsvField(value: string): string {
  if (/[",\r\n]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

/**
 * Builds the real 4-column roster CSV (full_name,email,sign_up_at,status)
 * client-side, for the "Copy to clipboard" action only. The mockup's
 * version has a 5th "Team" column built from fake generated data with no
 * backing field anywhere in the real API — dropped here rather than
 * fabricated. "Export CSV" downloads the backend's own file instead of
 * rebuilding it, so this function's output only ever needs to match that
 * file's shape, not replace it.
 */
export function buildAttendanceCsv(attendees: AttendeeDTO[]): string {
  const header = ['full_name', 'email', 'sign_up_at', 'status'];
  const rows = attendees.map((a) => [a.full_name, a.email, a.sign_up_at, a.status]);
  return [header, ...rows].map((row) => row.map(escapeCsvField).join(',')).join('\r\n');
}
