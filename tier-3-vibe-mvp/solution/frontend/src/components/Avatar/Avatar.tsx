import { getInitials } from '../../utils/initials';
import styles from './Avatar.module.css';

interface AvatarProps {
  name: string;
  /** Rotating avatar palette index (host row, attendee table). Omit for
   * the single fixed header-greeting color. */
  index?: number;
  size?: number;
  /** Organizer attendee table's cancelled rows use a flat muted grey
   * instead of the rotating palette color. */
  muted?: boolean;
}

export function Avatar({ name, index, size = 36, muted = false }: AvatarProps) {
  const background = muted
    ? 'var(--color-muted)'
    : index === undefined
      ? 'var(--color-avatar-default)'
      : `var(--avatar-color-${index % 5})`;

  return (
    <div
      className={styles.avatar}
      style={{ background, '--size': `${size}px` } as React.CSSProperties}
    >
      <span className={styles.initials} style={{ fontSize: size <= 24 ? '10px' : '13px' }}>
        {getInitials(name)}
      </span>
    </div>
  );
}
