import { Link } from 'react-router-dom';
import { AppHeader } from '../../components/AppHeader/AppHeader';
import { CreateEventForm } from '../../components/CreateEventForm/CreateEventForm';
import styles from './CreateEventPage.module.css';

export function CreateEventPage() {
  return (
    <div className={styles.page}>
      <AppHeader />

      <main className={styles.main}>
        <Link to="/events" className={styles.backLink}>
          &larr; All events
        </Link>
        <h1 className={styles.heading}>Create Event</h1>
        <p className={styles.subheading}>
          Fill in the details below, then publish so it shows up on the events feed.
        </p>

        <CreateEventForm />
      </main>
    </div>
  );
}
