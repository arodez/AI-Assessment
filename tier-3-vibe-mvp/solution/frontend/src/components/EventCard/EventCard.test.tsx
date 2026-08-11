import { QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { makeEvent } from '../../test/fixtures';
import { createTestQueryClient } from '../../test/testUtils';
import { EventCard } from './EventCard';

vi.mock('../../api/registrations', () => ({
  registerForEvent: vi.fn(),
  cancelRegistration: vi.fn(),
}));

function renderCard(event = makeEvent()) {
  const onClick = vi.fn();
  const queryClient = createTestQueryClient();
  render(
    <QueryClientProvider client={queryClient}>
      <EventCard event={event} onClick={onClick} />
    </QueryClientProvider>,
  );
  return { onClick };
}

describe('EventCard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows "Sign up" and the plain spots-left badge for an open event', () => {
    renderCard(makeEvent({ remaining_spots: 8, spots: 10, viewer_status: null }));
    expect(screen.getByRole('button', { name: 'Sign up' })).toBeInTheDocument();
    expect(screen.getByText('8 spots left')).toBeInTheDocument();
  });

  it('shows the "Only N left" badge under the 20% low-spots threshold', () => {
    renderCard(makeEvent({ remaining_spots: 1, spots: 10, viewer_status: null }));
    expect(screen.getByText('Only 1 left')).toBeInTheDocument();
  });

  it('shows "Fully booked" and disables the CTA when there are no remaining spots', () => {
    renderCard(makeEvent({ remaining_spots: 0, spots: 10, viewer_status: null }));
    expect(screen.getByRole('button', { name: 'Fully booked' })).toBeDisabled();
  });

  it('shows the registered state ("You’re going ✓" + Cancel) when the viewer is confirmed', () => {
    renderCard(makeEvent({ remaining_spots: 4, spots: 10, viewer_status: 'confirmed' }));
    expect(screen.getByText('You’re going ✓')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
  });

  it('shows "Sign up again" when the viewer previously cancelled and spots remain', () => {
    renderCard(makeEvent({ remaining_spots: 4, spots: 10, viewer_status: 'cancelled' }));
    expect(screen.getByRole('button', { name: 'Sign up again' })).toBeInTheDocument();
  });

  it('calls onClick when the card body is clicked', () => {
    const { onClick } = renderCard(makeEvent({ title: 'Docker Basics' }));
    fireEvent.click(screen.getByText('Docker Basics'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('does not bubble a CTA click into the card’s onClick (stopPropagation)', () => {
    const { onClick } = renderCard(
      makeEvent({ remaining_spots: 4, spots: 10, viewer_status: null }),
    );
    fireEvent.click(screen.getByRole('button', { name: 'Sign up' }));
    expect(onClick).not.toHaveBeenCalled();
  });
});
