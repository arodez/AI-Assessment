import { describe, expect, it } from 'vitest';
import { deriveEventDisplayState } from './eventStatus';

describe('deriveEventDisplayState', () => {
  it('returns "registered" when the viewer is confirmed, regardless of remaining spots', () => {
    expect(deriveEventDisplayState(0, 10, 'confirmed')).toBe('registered');
    expect(deriveEventDisplayState(5, 10, 'confirmed')).toBe('registered');
  });

  it('returns "cancelled" when the viewer cancelled and spots still remain', () => {
    expect(deriveEventDisplayState(3, 10, 'cancelled')).toBe('cancelled');
  });

  it('returns "full" when the viewer cancelled but the event has since backfilled to full', () => {
    expect(deriveEventDisplayState(0, 10, 'cancelled')).toBe('full');
  });

  it('returns "full" when there are no remaining spots and the viewer never registered', () => {
    expect(deriveEventDisplayState(0, 10, null)).toBe('full');
  });

  it('returns "low" when remaining/total is under the 20% threshold', () => {
    expect(deriveEventDisplayState(1, 10, null)).toBe('low');
  });

  it('returns "open" exactly at the 20% boundary (strict less-than, not less-or-equal)', () => {
    expect(deriveEventDisplayState(2, 10, null)).toBe('open');
  });

  it('returns "open" comfortably above the 20% threshold', () => {
    expect(deriveEventDisplayState(8, 10, null)).toBe('open');
  });
});
