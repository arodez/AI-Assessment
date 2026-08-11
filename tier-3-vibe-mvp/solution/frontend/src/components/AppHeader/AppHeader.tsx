import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { Avatar } from '../Avatar/Avatar';
import styles from './AppHeader.module.css';

/** Shared across all 3 authenticated pages (Feed, Create Event,
 * Organizer View) rather than re-implemented per page. */
export function AppHeader() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleSwitchAccount() {
    logout();
    navigate('/login');
  }

  return (
    <header className={styles.header}>
      <Link to="/events" className={styles.logoGroup}>
        <div className={styles.logoMark}>
          <span>E</span>
        </div>
        <div className={styles.logoText}>EVENTS HUB</div>
      </Link>

      <div className={styles.actions}>
        {user?.is_admin && (
          <Link to="/events/new" className={styles.createLink}>
            + Create an Event
          </Link>
        )}
        <div className={styles.userGroup}>
          <span className={styles.greeting}>Hey, {user?.first_name}</span>
          <Avatar name={user?.first_name ?? ''} />
          <button type="button" className={styles.switchAccount} onClick={handleSwitchAccount}>
            Switch account
          </button>
        </div>
      </div>
    </header>
  );
}
