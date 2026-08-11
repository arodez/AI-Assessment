import type { ViewerStatus } from '../../api/types';
import { deriveEventDisplayState } from '../../utils/eventStatus';
import { Badge } from '../Badge/Badge';

interface SpotsBadgeProps {
  remainingSpots: number;
  totalSpots: number;
  viewerStatus: ViewerStatus;
}

export function SpotsBadge({ remainingSpots, totalSpots, viewerStatus }: SpotsBadgeProps) {
  const state = deriveEventDisplayState(remainingSpots, totalSpots, viewerStatus);

  switch (state) {
    case 'full':
      return (
        <Badge background="#211E1E" color="#fff">
          Fully booked
        </Badge>
      );
    case 'registered':
      return (
        <Badge background="rgba(50,168,135,0.16)" color="#1f6f57">
          You&rsquo;re going &#10003;
        </Badge>
      );
    case 'cancelled':
      // The mockup's Feed screen spells this "Canceled" (single L); the
      // rest of the app (API status values, attendance roster) uses
      // "Cancelled" (double L, matching the DB enum) — normalized to the
      // latter here for consistency rather than reproducing the mockup's
      // inconsistent spelling.
      return (
        <Badge background="#F1F0EA" color="#a2a19c">
          Cancelled
        </Badge>
      );
    case 'low':
      return (
        <Badge background="#FFCFD6" color="#BA2229">
          Only {remainingSpots} left
        </Badge>
      );
    case 'open':
      return (
        <Badge background="#F1F0EA" color="#797873">
          {remainingSpots} spots left
        </Badge>
      );
  }
}
