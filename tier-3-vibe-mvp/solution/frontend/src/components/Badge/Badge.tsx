import type { ReactNode } from 'react';
import styles from './Badge.module.css';

interface BadgeProps {
  background: string;
  color: string;
  children: ReactNode;
}

/** Generic pill primitive — the visual mechanics (padding, radius, font)
 * live here once; the state->color mapping is each caller's own business
 * logic (see CategoryChip, SpotsBadge, StatusPill). */
export function Badge({ background, color, children }: BadgeProps) {
  return (
    <span className={styles.badge} style={{ background, color }}>
      {children}
    </span>
  );
}
