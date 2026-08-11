import { Link } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import type { EventDTO } from '../../api/types';
import { formatDateLabel, formatTimeRangeLabel } from '../../utils/formatDateTime';
import { resolveImageUrl } from '../../utils/imageUrl';
import { Avatar } from '../Avatar/Avatar';
import { CategoryChip } from '../CategoryChip/CategoryChip';
import { EventCta } from '../EventCta/EventCta';
import { Modal } from '../Modal/Modal';
import { SpotsBadge } from '../SpotsBadge/SpotsBadge';
import styles from './EventDetailModal.module.css';

interface EventDetailModalProps {
  event: EventDTO;
  onClose: () => void;
}

export function EventDetailModal({ event, onClose }: EventDetailModalProps) {
  const { user } = useAuth();
  const imageUrl = resolveImageUrl(event.image_url);
  const confirmedCount = event.spots - event.remaining_spots;

  return (
    <Modal onClose={onClose}>
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
        <h2 className={styles.title}>{event.title}</h2>

        {event.host_name && (
          <div className={styles.hostRow}>
            <Avatar name={event.host_name} index={event.id % 5} />
            <div className={styles.hostText}>
              Hosted by <strong>{event.host_name}</strong>
              {event.host_team ? ` · ${event.host_team}` : ''}
            </div>
          </div>
        )}

        {event.location.length > 0 && (
          <div className={styles.location}>{event.location.join(' · ')}</div>
        )}

        {event.description && <p className={styles.description}>{event.description}</p>}

        <div className={styles.footer}>
          <div>
            <SpotsBadge
              remainingSpots={event.remaining_spots}
              totalSpots={event.spots}
              viewerStatus={event.viewer_status}
            />
            <div className={styles.filledCaption}>
              {confirmedCount} of {event.spots} spots filled
            </div>
          </div>

          <div className={styles.actions}>
            {user?.is_admin && (
              <Link to={`/events/${event.id}/attendance`} className={styles.attendanceLink}>
                Attendance List
              </Link>
            )}
            <EventCta
              eventId={event.id}
              remainingSpots={event.remaining_spots}
              totalSpots={event.spots}
              viewerStatus={event.viewer_status}
              size="modal"
            />
          </div>
        </div>
      </div>
    </Modal>
  );
}
