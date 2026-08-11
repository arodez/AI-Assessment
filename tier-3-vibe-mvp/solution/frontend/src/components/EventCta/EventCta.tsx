import type { MouseEvent } from 'react';
import { ApiError } from '../../api/client';
import type { ViewerStatus } from '../../api/types';
import { useCancelMutation } from '../../hooks/useCancelMutation';
import { useRegisterMutation } from '../../hooks/useRegisterMutation';
import { deriveEventDisplayState } from '../../utils/eventStatus';
import styles from './EventCta.module.css';

interface EventCtaProps {
  eventId: number;
  remainingSpots: number;
  totalSpots: number;
  viewerStatus: ViewerStatus;
  size: 'card' | 'modal';
}

/**
 * Extracted from EventCard so EventDetailModal can share the EXACT same
 * Sign-up/Cancel/Full branching at a larger size, not a copy-pasted
 * second implementation that could drift out of sync.
 */
export function EventCta({
  eventId,
  remainingSpots,
  totalSpots,
  viewerStatus,
  size,
}: EventCtaProps) {
  const registerMutation = useRegisterMutation(eventId);
  const cancelMutation = useCancelMutation(eventId);
  const state = deriveEventDisplayState(remainingSpots, totalSpots, viewerStatus);
  const pending = registerMutation.isPending || cancelMutation.isPending;

  const error = registerMutation.error ?? cancelMutation.error;
  const errorMessage = error instanceof ApiError ? error.message : null;

  function stopAndRun(event: MouseEvent, action: () => void) {
    // Both EventCard and EventDetailModal render this inside a clickable
    // card/backdrop — a CTA click must not also trigger the parent's
    // onClick (opening/closing the card/modal).
    event.stopPropagation();
    action();
  }

  if (state === 'registered') {
    return (
      <div className={styles.wrapper}>
        <button
          type="button"
          className={styles.cancelLink}
          disabled={pending}
          onClick={(e) => stopAndRun(e, () => cancelMutation.mutate())}
        >
          Cancel
        </button>
        {errorMessage && <span className={styles.cancelLink}>{errorMessage}</span>}
      </div>
    );
  }

  const ctaLabel =
    state === 'full' ? 'Fully booked' : state === 'cancelled' ? 'Sign up again' : 'Sign up';

  return (
    <div className={styles.wrapper}>
      <button
        type="button"
        className={`${styles.mainCta} ${styles[size]}`}
        disabled={state === 'full' || pending}
        onClick={(e) => stopAndRun(e, () => registerMutation.mutate())}
      >
        {ctaLabel}
      </button>
      {errorMessage && <span className={styles.cancelLink}>{errorMessage}</span>}
    </div>
  );
}
