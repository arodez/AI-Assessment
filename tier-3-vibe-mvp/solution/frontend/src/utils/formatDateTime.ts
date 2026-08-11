/** "TUE, AUG 11" — matches the mockup's date-label style. */
export function formatDateLabel(iso: string): string {
  const d = new Date(iso);
  return d
    .toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
    .toUpperCase();
}

function formatTime(d: Date): string {
  const h = d.getHours();
  const h12 = h % 12 === 0 ? 12 : h % 12;
  const m = d.getMinutes().toString().padStart(2, '0');
  return `${h12}:${m}`;
}

/** "AUG 1" — matches the organizer attendance table's compact Signed Up
 * column (no weekday, unlike formatDateLabel). */
export function formatShortDateLabel(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }).toUpperCase();
}

/** "5:30 – 6:30 PM" — matches the mockup's time-label style, collapsing
 * a shared AM/PM suffix when both times land in the same period (e.g.
 * "11:00 AM – 12:30 PM" when they differ). */
export function formatTimeRangeLabel(startIso: string, endIso: string): string {
  const start = new Date(startIso);
  const end = new Date(endIso);
  const startPeriod = start.getHours() >= 12 ? 'PM' : 'AM';
  const endPeriod = end.getHours() >= 12 ? 'PM' : 'AM';

  const startLabel =
    startPeriod === endPeriod ? formatTime(start) : `${formatTime(start)} ${startPeriod}`;
  const endLabel = `${formatTime(end)} ${endPeriod}`;
  return `${startLabel} – ${endLabel}`;
}
