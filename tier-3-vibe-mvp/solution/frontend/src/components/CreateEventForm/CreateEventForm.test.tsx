import { QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { makeEvent } from '../../test/fixtures';
import { createTestQueryClient } from '../../test/testUtils';
import { CreateEventForm } from './CreateEventForm';

vi.mock('../../api/events', () => ({
  createEvent: vi.fn().mockResolvedValue(undefined),
  listEvents: vi.fn(),
  getEvent: vi.fn(),
}));

import { createEvent } from '../../api/events';

function renderForm() {
  const queryClient = createTestQueryClient();
  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <CreateEventForm />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

function submit() {
  fireEvent.click(screen.getByRole('button', { name: 'Publish event' }));
}

describe('CreateEventForm validation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(createEvent).mockResolvedValue(makeEvent());
  });

  it('blocks submission and shows every required-field error on an empty form', async () => {
    renderForm();
    submit();

    expect(await screen.findByText('Title must be at least 3 characters.')).toBeInTheDocument();
    expect(screen.getByText('Pick a date.')).toBeInTheDocument();
    // Default location type is "in_person", which requires a room/building.
    expect(screen.getByText('Add a room or building.')).toBeInTheDocument();
    expect(createEvent).not.toHaveBeenCalled();
  });

  it('requires an http(s) link for a virtual event', async () => {
    renderForm();
    fireEvent.click(screen.getByRole('button', { name: 'Virtual' }));
    submit();

    expect(await screen.findByText('Enter a valid http(s) link.')).toBeInTheDocument();
    expect(createEvent).not.toHaveBeenCalled();
  });

  it('rejects a non-http(s) virtual link', async () => {
    renderForm();
    fireEvent.click(screen.getByRole('button', { name: 'Virtual' }));
    fireEvent.change(screen.getByPlaceholderText('e.g. Zoom, Google Meet link'), {
      target: { value: 'not-a-url' },
    });
    submit();

    expect(await screen.findByText('Enter a valid http(s) link.')).toBeInTheDocument();
    expect(createEvent).not.toHaveBeenCalled();
  });

  it('requires both a room and a valid link for a hybrid event', async () => {
    renderForm();
    fireEvent.click(screen.getByRole('button', { name: 'Hybrid' }));
    submit();

    expect(await screen.findByText('Add a room or building.')).toBeInTheDocument();
  });

  it('rejects a title under 3 characters', async () => {
    renderForm();
    fireEvent.change(screen.getByPlaceholderText('e.g. Figma Variables Workshop'), {
      target: { value: 'ab' },
    });
    submit();

    expect(await screen.findByText('Title must be at least 3 characters.')).toBeInTheDocument();
  });

  it('rejects an end time that is not after the start time', async () => {
    renderForm();
    fireEvent.change(screen.getByPlaceholderText('e.g. Figma Variables Workshop'), {
      target: { value: 'Docker Basics Workshop' },
    });
    fireEvent.change(document.querySelector('input[type="date"]')!, {
      target: { value: '2026-09-15' },
    });
    const timeInputs = document.querySelectorAll('input[type="time"]');
    fireEvent.change(timeInputs[0]!, { target: { value: '11:00' } });
    fireEvent.change(timeInputs[1]!, { target: { value: '10:00' } });
    fireEvent.change(screen.getByPlaceholderText('e.g. Room 12, Rooftop Terrace'), {
      target: { value: 'Room 12' },
    });
    submit();

    expect(await screen.findByText('End time must be after start time.')).toBeInTheDocument();
    expect(createEvent).not.toHaveBeenCalled();
  });

  it('rejects a non-positive spots value', async () => {
    renderForm();
    fireEvent.change(screen.getByLabelText('Spots Available'), { target: { value: '0' } });
    submit();

    expect(await screen.findByText('Spots must be at least 1.')).toBeInTheDocument();
  });

  it('submits a correctly-shaped multipart FormData on a valid submission and navigates away', async () => {
    renderForm();

    fireEvent.change(screen.getByPlaceholderText('e.g. Figma Variables Workshop'), {
      target: { value: 'Docker Basics Workshop' },
    });
    fireEvent.change(document.querySelector('input[type="date"]')!, {
      target: { value: '2026-09-15' },
    });
    const timeInputs = document.querySelectorAll('input[type="time"]');
    fireEvent.change(timeInputs[0]!, { target: { value: '10:00' } });
    fireEvent.change(timeInputs[1]!, { target: { value: '11:00' } });
    fireEvent.change(screen.getByPlaceholderText('e.g. Room 12, Rooftop Terrace'), {
      target: { value: 'Room 12, The Studio' },
    });
    fireEvent.change(screen.getByLabelText('Spots Available'), { target: { value: '15' } });

    submit();

    await waitFor(() => expect(createEvent).toHaveBeenCalledTimes(1));

    const formData = vi.mocked(createEvent).mock.calls[0]![0];
    expect(formData.get('title')).toBe('Docker Basics Workshop');
    expect(formData.get('start')).toBe('2026-09-15T10:00:00');
    expect(formData.get('end')).toBe('2026-09-15T11:00:00');
    expect(formData.get('spots')).toBe('15');
    expect(formData.get('event_type')).toBe('workshop');
    expect(formData.get('location_type')).toBe('in_person');
    expect(formData.get('location')).toBe(JSON.stringify(['Room 12, The Studio']));
    expect(formData.has('description')).toBe(false);
    expect(formData.has('image')).toBe(false);
  });
});
