import { useState } from 'react';
import { AppHeader } from '../../components/AppHeader/AppHeader';
import { EventDetailModal } from '../../components/EventDetailModal/EventDetailModal';
import { WeekSection } from '../../components/WeekSection/WeekSection';
import { useEventsQuery } from '../../hooks/useEventsQuery';
import { groupEventsByWeek } from '../../utils/weekGrouping';
import styles from './FeedPage.module.css';

export function FeedPage() {
  const { data: events, isLoading, isError } = useEventsQuery();
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null);

  const weeks = events ? groupEventsByWeek(events) : [];
  const selectedEvent = events?.find((e) => e.id === selectedEventId) ?? null;

  return (
    <div className={styles.page}>
      <AppHeader />

      <main className={styles.main}>
        <div className={styles.intro}>
          <h1 className={styles.heading}>Upcoming Events</h1>
          <p className={styles.subheading}>
            Study groups, AMAs, workshops, and get-togethers happening across the company. Grab a
            spot before it&rsquo;s gone.
          </p>
        </div>

        {isLoading && <p className={styles.emptyState}>Loading events…</p>}
        {isError && (
          <p className={styles.errorState}>Could not load events. Please try again shortly.</p>
        )}
        {events && events.length === 0 && (
          <p className={styles.emptyState}>No upcoming events yet — check back soon.</p>
        )}

        {weeks.map((week) => (
          <WeekSection
            key={week.label}
            label={week.label}
            events={week.events}
            onSelectEvent={setSelectedEventId}
          />
        ))}
      </main>

      {selectedEvent && (
        <EventDetailModal event={selectedEvent} onClose={() => setSelectedEventId(null)} />
      )}
    </div>
  );
}
