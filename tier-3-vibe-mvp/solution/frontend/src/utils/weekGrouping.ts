import type { EventDTO } from '../api/types';

export interface WeekGroup {
  label: string;
  events: EventDTO[];
}

const MS_PER_DAY = 24 * 60 * 60 * 1000;
const MS_PER_WEEK = 7 * MS_PER_DAY;

/** Monday 00:00 local time of the week containing `date` — weeks are
 * Monday-start, matching typical business-week conventions. */
function startOfWeek(date: Date): Date {
  const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const day = d.getDay(); // 0 = Sunday, 1 = Monday, ...
  const diffToMonday = day === 0 ? 6 : day - 1;
  d.setDate(d.getDate() - diffToMonday);
  return d;
}

function formatWeekRangeLabel(weekStart: Date): string {
  const weekEnd = new Date(weekStart.getTime() + 6 * MS_PER_DAY);
  const startLabel = weekStart
    .toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    .toUpperCase();
  const endLabel = weekEnd
    .toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    .toUpperCase();
  return `${startLabel} – ${endLabel}`;
}

/**
 * GET /events already returns only future events, sorted by start
 * ascending — this just buckets that already-sorted list into
 * week-labeled sections, mirroring the mockup's "This Week"/"Next Week"
 * grouping. Anything beyond the next two weeks falls back to a
 * "MON D – MON D" date-range label, since the mockup only ever
 * demonstrates two buckets but the real seed data spans months.
 */
export function groupEventsByWeek(events: EventDTO[], referenceDate = new Date()): WeekGroup[] {
  const currentWeekStart = startOfWeek(referenceDate);
  const groups: WeekGroup[] = [];
  const labelToGroup = new Map<string, WeekGroup>();

  for (const event of events) {
    const eventWeekStart = startOfWeek(new Date(event.start));
    const weekOffset = Math.round(
      (eventWeekStart.getTime() - currentWeekStart.getTime()) / MS_PER_WEEK,
    );

    let label: string;
    if (weekOffset === 0) label = 'This Week';
    else if (weekOffset === 1) label = 'Next Week';
    else label = formatWeekRangeLabel(eventWeekStart);

    let group = labelToGroup.get(label);
    if (!group) {
      group = { label, events: [] };
      labelToGroup.set(label, group);
      groups.push(group);
    }
    group.events.push(event);
  }

  return groups;
}
