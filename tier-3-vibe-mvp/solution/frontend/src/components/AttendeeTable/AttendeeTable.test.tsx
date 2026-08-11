import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import type { AttendeeDTO } from '../../api/types';
import { AttendeeTable } from './AttendeeTable';

const ATTENDEES: AttendeeDTO[] = [
  {
    full_name: 'Grace Hopper',
    email: 'grace.hopper@company.com',
    sign_up_at: '2026-08-08T09:00:00',
    status: 'Confirmed',
  },
  {
    full_name: 'Alan Turing',
    email: 'alan.turing@company.com',
    sign_up_at: '2026-08-07T09:00:00',
    status: 'Cancelled',
  },
];

describe('AttendeeTable', () => {
  it('renders every attendee row with name, email, and status', () => {
    render(<AttendeeTable attendees={ATTENDEES} />);

    expect(screen.getByText('Grace Hopper')).toBeInTheDocument();
    expect(screen.getByText('grace.hopper@company.com')).toBeInTheDocument();
    expect(screen.getByText('Confirmed')).toBeInTheDocument();
    expect(screen.getByText('Alan Turing')).toBeInTheDocument();
    expect(screen.getByText('Cancelled')).toBeInTheDocument();
  });

  it('applies strikethrough/muted styling to a cancelled row only', () => {
    render(<AttendeeTable attendees={ATTENDEES} />);

    const confirmedName = screen.getByText('Grace Hopper');
    const cancelledName = screen.getByText('Alan Turing');

    expect(confirmedName.className).not.toMatch(/cancelledName/);
    expect(cancelledName.className).toMatch(/cancelledName/);
  });

  it('dims the whole row for a cancelled attendee', () => {
    render(<AttendeeTable attendees={ATTENDEES} />);

    const cancelledRow = screen.getByText('Alan Turing').closest('tr');
    const confirmedRow = screen.getByText('Grace Hopper').closest('tr');

    expect(cancelledRow?.className).toMatch(/cancelledRow/);
    expect(confirmedRow?.className).toBeFalsy();
  });

  it('shows a friendly empty state when there are no attendees', () => {
    render(<AttendeeTable attendees={[]} />);
    expect(screen.getByText('No one has signed up yet.')).toBeInTheDocument();
  });
});
