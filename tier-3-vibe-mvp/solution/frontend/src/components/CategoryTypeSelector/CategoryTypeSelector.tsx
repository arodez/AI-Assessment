import type { EventType } from '../../api/types';
import { CATEGORY_LABEL, CATEGORY_STYLE } from '../CategoryChip/categoryStyles';
import styles from './CategoryTypeSelector.module.css';

const CATEGORIES: EventType[] = ['study_group', 'ama', 'workshop', 'social', 'other'];

interface CategoryTypeSelectorProps {
  value: EventType;
  onChange: (value: EventType) => void;
}

/** Reuses CategoryChip's exact enum->style/label map so the selected
 * button's color always matches how the chip renders everywhere else. */
export function CategoryTypeSelector({ value, onChange }: CategoryTypeSelectorProps) {
  return (
    <div className={styles.group}>
      {CATEGORIES.map((eventType) => {
        const selected = eventType === value;
        const { background, color } = CATEGORY_STYLE[eventType];
        return (
          <button
            key={eventType}
            type="button"
            className={styles.chip}
            style={selected ? { background, color, borderColor: background } : undefined}
            onClick={() => onChange(eventType)}
          >
            {CATEGORY_LABEL[eventType]}
          </button>
        );
      })}
    </div>
  );
}
