import type { EventType } from '../../api/types';

// Split from CategoryChip.tsx (a component file) so exporting these
// constants for reuse (CategoryTypeSelector) doesn't break React Fast
// Refresh, which requires component files to only export components.
export const CATEGORY_STYLE: Record<EventType, { background: string; color: string }> = {
  study_group: { background: '#1366B1', color: '#fff' },
  ama: { background: '#8021F8', color: '#fff' },
  workshop: { background: '#32A887', color: '#fff' },
  social: { background: '#DDFD58', color: '#211E1E' },
  other: { background: '#797873', color: '#fff' },
};

export const CATEGORY_LABEL: Record<EventType, string> = {
  study_group: 'Study Group',
  ama: 'AMA',
  workshop: 'Workshop',
  social: 'Social',
  other: 'Other',
};
