import type { EventDTO } from '../../api/types';
import { EventCard } from '../EventCard/EventCard';
import styles from './WeekSection.module.css';

interface WeekSectionProps {
  label: string;
  events: EventDTO[];
  onSelectEvent: (id: number) => void;
}

export function WeekSection({ label, events, onSelectEvent }: WeekSectionProps) {
  return (
    <section className={styles.section}>
      <div className={styles.header}>
        <span className={styles.label}>{label}</span>
        <div className={styles.divider} />
      </div>
      <div className={styles.grid}>
        {events.map((event) => (
          <EventCard key={event.id} event={event} onClick={() => onSelectEvent(event.id)} />
        ))}
      </div>
    </section>
  );
}
