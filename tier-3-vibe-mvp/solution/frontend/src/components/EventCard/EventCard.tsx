import type { EventDTO } from '../../api/types';
import { formatDateLabel, formatTimeRangeLabel } from '../../utils/formatDateTime';
import { resolveImageUrl } from '../../utils/imageUrl';
import { Avatar } from '../Avatar/Avatar';
import { CategoryChip } from '../CategoryChip/CategoryChip';
import { EventCta } from '../EventCta/EventCta';
import { SpotsBadge } from '../SpotsBadge/SpotsBadge';
import styles from './EventCard.module.css';

interface EventCardProps {
  event: EventDTO;
  onClick: () => void;
}

export function EventCard({ event, onClick }: EventCardProps) {
  const imageUrl = resolveImageUrl(event.image_url);
  const hostLine =
    event.host_name && event.host_team
      ? `Hosted by ${event.host_name} · ${event.host_team}`
      : event.host_name
        ? `Hosted by ${event.host_name}`
        : null;

  return (
    <article
      className={`${styles.card} ${event.viewer_status === 'confirmed' ? styles.registered : ''}`}
      onClick={onClick}
    >
      <div className={styles.imageWrap}>
        {imageUrl && <img src={imageUrl} alt={`${event.title} cover`} className={styles.image} />}
        <div className={styles.chipOverlay}>
          <CategoryChip eventType={event.event_type} />
        </div>
      </div>

      <div className={styles.body}>
        <div className={styles.dateTime}>
          {formatDateLabel(event.start)} · {formatTimeRangeLabel(event.start, event.end)}
        </div>
        <h3 className={styles.title}>{event.title}</h3>

        {hostLine && (
          <div className={styles.hostRow}>
            <Avatar name={event.host_name ?? ''} index={event.id % 5} size={22} />
            <span className={styles.hostText}>{hostLine}</span>
          </div>
        )}

        {event.location.length > 0 && (
          <div className={styles.location}>{event.location.join(' · ')}</div>
        )}

        <div className={styles.footer}>
          <SpotsBadge
            remainingSpots={event.remaining_spots}
            totalSpots={event.spots}
            viewerStatus={event.viewer_status}
          />
          <EventCta
            eventId={event.id}
            remainingSpots={event.remaining_spots}
            totalSpots={event.spots}
            viewerStatus={event.viewer_status}
            size="card"
          />
        </div>
      </div>
    </article>
  );
}
