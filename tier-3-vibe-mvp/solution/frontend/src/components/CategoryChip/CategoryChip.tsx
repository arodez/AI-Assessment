import type { EventType } from '../../api/types';
import { Badge } from '../Badge/Badge';
import { CATEGORY_LABEL, CATEGORY_STYLE } from './categoryStyles';

/** Keyed by the exact backend EventType enum value — not the mockup's
 * Title Case label used as internal state, which would need a lossy
 * reverse-mapping if copied as-is. */
export function CategoryChip({ eventType }: { eventType: EventType }) {
  const { background, color } = CATEGORY_STYLE[eventType];
  return (
    <Badge background={background} color={color}>
      {CATEGORY_LABEL[eventType]}
    </Badge>
  );
}
