import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { downloadAttendanceCsv } from '../../api/attendance';
import { AppHeader } from '../../components/AppHeader/AppHeader';
import { AttendeeTable } from '../../components/AttendeeTable/AttendeeTable';
import { OrganizerHeader } from '../../components/OrganizerHeader/OrganizerHeader';
import { useAttendanceQuery } from '../../hooks/useAttendanceQuery';
import { useEventQuery } from '../../hooks/useEventQuery';
import { buildAttendanceCsv } from '../../utils/attendanceCsv';
import styles from './OrganizerViewPage.module.css';

export function OrganizerViewPage() {
  const params = useParams<{ id: string }>();
  // An unparseable id just flows through to the queries below, which hit
  // the backend's own `bad_request` validation (see docs/API.md) and
  // surface through the existing isError states — no separate guard
  // needed here, matching the "route guards are UX only" principle used
  // elsewhere (the backend is always the real authority).
  const eventId = Number(params.id);

  const eventQuery = useEventQuery(eventId);
  const attendanceQuery = useAttendanceQuery(eventId);

  const [copied, setCopied] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  async function handleCopy() {
    if (!attendanceQuery.data) return;
    const csv = buildAttendanceCsv(attendanceQuery.data);
    try {
      await navigator.clipboard.writeText(csv);
    } catch {
      return;
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  }

  async function handleExportCsv() {
    setExportError(null);
    try {
      const { blob, filename } = await downloadAttendanceCsv(eventId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch {
      setExportError('Could not export the CSV. Please try again.');
    }
  }

  const attendees = attendanceQuery.data ?? [];
  const confirmedCount = attendees.filter((a) => a.status === 'Confirmed').length;
  const cancelledCount = attendees.length - confirmedCount;

  return (
    <div className={styles.page}>
      <AppHeader />

      <main className={styles.main}>
        <Link to="/events" className={styles.backLink}>
          &larr; All events
        </Link>

        {eventQuery.isLoading && <p className={styles.stateText}>Loading event…</p>}
        {eventQuery.isError && <p className={styles.errorText}>Could not load this event.</p>}
        {eventQuery.data && (
          <OrganizerHeader
            event={eventQuery.data}
            confirmedCount={confirmedCount}
            cancelledCount={cancelledCount}
          />
        )}

        <div className={styles.toolbar}>
          <h2 className={styles.attendeesHeading}>Attendees &middot; {attendees.length}</h2>
          <div className={styles.actions}>
            <button
              type="button"
              className={`${styles.copyButton} ${copied ? styles.copied : ''}`}
              onClick={() => void handleCopy()}
            >
              {copied ? 'Copied!' : 'Copy to clipboard'}
            </button>
            <button
              type="button"
              className={styles.exportButton}
              onClick={() => void handleExportCsv()}
            >
              Export CSV
            </button>
          </div>
        </div>

        {exportError && <p className={styles.errorText}>{exportError}</p>}

        {attendanceQuery.isLoading && <p className={styles.stateText}>Loading attendees…</p>}
        {attendanceQuery.isError && <p className={styles.errorText}>Could not load attendees.</p>}
        {attendanceQuery.data && <AttendeeTable attendees={attendanceQuery.data} />}
      </main>
    </div>
  );
}
