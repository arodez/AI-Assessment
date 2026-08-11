import type { EventDTO } from '../../api/types';
import { formatDateLabel, formatTimeRangeLabel } from '../../utils/formatDateTime';
import { resolveImageUrl } from '../../utils/imageUrl';
import { CategoryChip } from '../CategoryChip/CategoryChip';
import styles from './OrganizerHeader.module.css';

interface OrganizerHeaderProps {
  event: EventDTO;
  confirmedCount: number;
  cancelledCount: number;
}

export function OrganizerHeader({ event, confirmedCount, cancelledCount }: OrganizerHeaderProps) {
  const imageUrl = resolveImageUrl(event.image_url);

  return (
    <div className={styles.card}>
      <div className={styles.identity}>
        {imageUrl && <img src={imageUrl} alt={`${event.title} cover`} className={styles.thumb} />}
        <div>
          <div className={styles.chipWrap}>
            <CategoryChip eventType={event.event_type} />
          </div>
          <h1 className={styles.title}>{event.title}</h1>
          <div className={styles.meta}>
            {formatDateLabel(event.start)} · {formatTimeRangeLabel(event.start, event.end)}
            {event.location.length > 0 && ` · ${event.location.join(' · ')}`}
          </div>
        </div>
      </div>

      <div className={styles.stats}>
        <div>
          <div className={styles.statValue}>
            {confirmedCount}/{event.spots}
          </div>
          <div className={styles.statLabel}>Spots Filled</div>
        </div>
        <div>
          <div className={`${styles.statValue} ${styles.confirmed}`}>{confirmedCount}</div>
          <div className={styles.statLabel}>Confirmed</div>
        </div>
        <div>
          <div className={`${styles.statValue} ${styles.cancelled}`}>{cancelledCount}</div>
          <div className={styles.statLabel}>Cancelled</div>
        </div>
      </div>
    </div>
  );
}
