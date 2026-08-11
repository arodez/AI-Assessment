import type { AttendeeDTO } from '../../api/types';
import { formatShortDateLabel } from '../../utils/formatDateTime';
import { Avatar } from '../Avatar/Avatar';
import { StatusPill } from '../StatusPill/StatusPill';
import styles from './AttendeeTable.module.css';

interface AttendeeTableProps {
  attendees: AttendeeDTO[];
}

/** Renders the real 4-column roster (full_name, email, sign_up_at,
 * status). The mockup's table also has a "Team" column built from fake
 * generated data with no backing field anywhere in the API — dropped
 * here rather than fabricated. */
export function AttendeeTable({ attendees }: AttendeeTableProps) {
  if (attendees.length === 0) {
    return <p className={styles.empty}>No one has signed up yet.</p>;
  }

  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th className={styles.th}>Attendee</th>
            <th className={styles.th}>Signed Up</th>
            <th className={styles.th}>Status</th>
          </tr>
        </thead>
        <tbody>
          {attendees.map((attendee, index) => {
            const cancelled = attendee.status === 'Cancelled';
            return (
              <tr
                key={`${attendee.email}-${attendee.sign_up_at}`}
                className={cancelled ? styles.cancelledRow : undefined}
              >
                <td className={styles.td}>
                  <div className={styles.attendeeCell}>
                    <Avatar
                      name={attendee.full_name}
                      index={index % 5}
                      size={26}
                      muted={cancelled}
                    />
                    <div>
                      <div className={`${styles.name} ${cancelled ? styles.cancelledName : ''}`}>
                        {attendee.full_name}
                      </div>
                      <div className={styles.email}>{attendee.email}</div>
                    </div>
                  </div>
                </td>
                <td className={styles.signedUp}>{formatShortDateLabel(attendee.sign_up_at)}</td>
                <td className={styles.td}>
                  <StatusPill status={attendee.status} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
