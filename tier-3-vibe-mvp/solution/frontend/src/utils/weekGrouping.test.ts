import { describe, expect, it } from 'vitest';
import { makeEvent } from '../test/fixtures';
import { groupEventsByWeek } from './weekGrouping';

// A fixed Monday reference so "This Week"/"Next Week" boundaries are
// deterministic regardless of when the suite actually runs.
const REFERENCE = new Date(2024, 0, 1, 12); // Mon Jan 1 2024, noon

describe('groupEventsByWeek', () => {
  it('buckets an event in the same Monday-start week as "This Week"', () => {
    const groups = groupEventsByWeek(
      [makeEvent({ id: 1, start: '2024-01-03T10:00:00' })],
      REFERENCE,
    );
    expect(groups[0]?.label).toBe('This Week');
  });

  it('includes Sunday as the last day of the current Monday-start week', () => {
    const groups = groupEventsByWeek(
      [makeEvent({ id: 1, start: '2024-01-07T10:00:00' })],
      REFERENCE,
    );
    expect(groups[0]?.label).toBe('This Week');
  });

  it('buckets an event exactly one week out as "Next Week"', () => {
    const groups = groupEventsByWeek(
      [makeEvent({ id: 1, start: '2024-01-08T10:00:00' })],
      REFERENCE,
    );
    expect(groups[0]?.label).toBe('Next Week');
  });

  it('falls back to a "MON D – MON D" date-range label two or more weeks out', () => {
    const groups = groupEventsByWeek(
      [makeEvent({ id: 1, start: '2024-01-15T10:00:00' })],
      REFERENCE,
    );
    expect(groups[0]?.label).toBe('JAN 15 – JAN 21');
  });

  it('groups events sharing a week label under one bucket, preserving encounter order', () => {
    const groups = groupEventsByWeek(
      [
        makeEvent({ id: 1, start: '2024-01-03T09:00:00' }),
        makeEvent({ id: 2, start: '2024-01-08T09:00:00' }),
        makeEvent({ id: 3, start: '2024-01-04T09:00:00' }),
      ],
      REFERENCE,
    );

    expect(groups).toHaveLength(2);
    expect(groups[0]?.label).toBe('This Week');
    expect(groups[0]?.events.map((e) => e.id)).toEqual([1, 3]);
    expect(groups[1]?.label).toBe('Next Week');
  });

  it('returns an empty array for an empty event list', () => {
    expect(groupEventsByWeek([], REFERENCE)).toEqual([]);
  });
});
