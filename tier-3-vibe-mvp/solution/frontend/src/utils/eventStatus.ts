import type { ViewerStatus } from '../api/types';

export type EventDisplayState = 'registered' | 'cancelled' | 'full' | 'low' | 'open';

/**
 * Single source of truth for badge/CTA branching — shared by SpotsBadge
 * and EventCta so their state logic can never drift apart into two
 * slightly-different implementations.
 *
 * "low" threshold: remaining/total < 20%. Not defined anywhere in BRIEF,
 * the API, or the mockup (which only demonstrates the visual state) —
 * this value was confirmed with the user rather than assumed silently.
 */
export function deriveEventDisplayState(
  remaining: number,
  total: number,
  viewerStatus: ViewerStatus,
): EventDisplayState {
  if (viewerStatus === 'confirmed') return 'registered';
  if (viewerStatus === 'cancelled') {
    // A cancelled slot could have been backfilled by someone else since
    // — re-signup isn't exempt from the full-event check, so don't offer
    // "sign up again" as if it were guaranteed to succeed.
    return remaining <= 0 ? 'full' : 'cancelled';
  }
  if (remaining <= 0) return 'full';
  if (remaining / total < 0.2) return 'low';
  return 'open';
}
