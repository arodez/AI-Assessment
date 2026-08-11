import type { LocationType } from '../../api/types';
import styles from './LocationTypeToggle.module.css';

const OPTIONS: { value: LocationType; label: string }[] = [
  { value: 'in_person', label: 'In-person' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'virtual', label: 'Virtual' },
];

interface LocationTypeToggleProps {
  value: LocationType;
  onChange: (value: LocationType) => void;
}

export function LocationTypeToggle({ value, onChange }: LocationTypeToggleProps) {
  return (
    <div className={styles.group}>
      {OPTIONS.map((option) => (
        <button
          key={option.value}
          type="button"
          className={`${styles.chip} ${value === option.value ? styles.active : ''}`}
          onClick={() => onChange(option.value)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
