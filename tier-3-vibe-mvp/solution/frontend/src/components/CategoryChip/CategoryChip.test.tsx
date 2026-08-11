import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import type { EventType } from '../../api/types';
import { CategoryChip } from './CategoryChip';

const CASES: { eventType: EventType; label: string }[] = [
  { eventType: 'study_group', label: 'Study Group' },
  { eventType: 'ama', label: 'AMA' },
  { eventType: 'workshop', label: 'Workshop' },
  { eventType: 'social', label: 'Social' },
  { eventType: 'other', label: 'Other' },
];

describe('CategoryChip', () => {
  it.each(CASES)(
    'renders the "$label" label for event_type "$eventType"',
    ({ eventType, label }) => {
      render(<CategoryChip eventType={eventType} />);
      expect(screen.getByText(label)).toBeInTheDocument();
    },
  );
});
