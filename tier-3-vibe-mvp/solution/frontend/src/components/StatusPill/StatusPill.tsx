import type { AttendanceStatus } from '../../api/types';
import { Badge } from '../Badge/Badge';

const STATUS_STYLE: Record<AttendanceStatus, { background: string; color: string }> = {
  Confirmed: { background: 'rgba(50,168,135,0.15)', color: '#1f6f57' },
  Cancelled: { background: '#F1F0EA', color: '#a2a19c' },
};

/** Organizer attendance table's per-row status pill — takes the real
 * AttendanceStatus union (Capitalized, never null), not ViewerStatus. */
export function StatusPill({ status }: { status: AttendanceStatus }) {
  const { background, color } = STATUS_STYLE[status];
  return (
    <Badge background={background} color={color}>
      {status}
    </Badge>
  );
}
