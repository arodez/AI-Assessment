import { QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthContext, type AuthContextValue } from '../../auth/AuthContext';
import { makeEvent } from '../../test/fixtures';
import { createTestQueryClient } from '../../test/testUtils';
import { OrganizerViewPage } from './OrganizerViewPage';

vi.mock('../../api/events', () => ({
  getEvent: vi.fn(),
  listEvents: vi.fn(),
  createEvent: vi.fn(),
}));

vi.mock('../../api/attendance', () => ({
  getAttendance: vi.fn(),
  downloadAttendanceCsv: vi.fn(),
}));

import { getEvent } from '../../api/events';
import { downloadAttendanceCsv, getAttendance } from '../../api/attendance';

const ATTENDEES = [
  {
    full_name: 'Jordan Lee',
    email: 'jordan.lee@company.com',
    sign_up_at: '2026-08-07T18:00:00',
    status: 'Cancelled' as const,
  },
  {
    full_name: 'Maria Chen',
    email: 'maria.chen@company.com',
    sign_up_at: '2026-08-08T16:00:00',
    status: 'Confirmed' as const,
  },
  {
    full_name: "Sam O'Neil",
    email: 'sam.oneil@company.com',
    sign_up_at: '2026-08-09T09:00:00',
    status: 'Confirmed' as const,
  },
];

function renderPage() {
  const queryClient = createTestQueryClient();
  const authValue: AuthContextValue = {
    token: 'a-token',
    user: { id: 1, first_name: 'Alice', is_admin: true },
    login: async () => {},
    logout: () => {},
  };

  render(
    <QueryClientProvider client={queryClient}>
      <AuthContext value={authValue}>
        <MemoryRouter initialEntries={['/events/11/attendance']}>
          <Routes>
            <Route path="/events/:id/attendance" element={<OrganizerViewPage />} />
          </Routes>
        </MemoryRouter>
      </AuthContext>
    </QueryClientProvider>,
  );
}

describe('OrganizerViewPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getEvent).mockResolvedValue(
      makeEvent({ id: 11, title: 'End-of-Summer Rooftop Social', spots: 6, remaining_spots: 4 }),
    );
    vi.mocked(getAttendance).mockResolvedValue(ATTENDEES);
    vi.mocked(downloadAttendanceCsv).mockResolvedValue({
      blob: new Blob(['full_name,email,sign_up_at,status'], { type: 'text/csv' }),
      filename: 'end-of-summer-rooftop-social-2026-09-18-2026-08-10.csv',
    });
    Object.assign(navigator, { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } });
  });

  it('renders the event header and the full roster', async () => {
    renderPage();

    expect(await screen.findByText('End-of-Summer Rooftop Social')).toBeInTheDocument();
    expect(screen.getByText('Attendees · 3')).toBeInTheDocument();
    expect(screen.getByText('Jordan Lee')).toBeInTheDocument();
    expect(screen.getByText('Maria Chen')).toBeInTheDocument();
    expect(getEvent).toHaveBeenCalledWith(11);
    expect(getAttendance).toHaveBeenCalledWith(11);
  });

  it('copies exactly the real 4-column CSV shape — not the mockup\'s 5-column "Team" version', async () => {
    renderPage();
    await screen.findByText('Jordan Lee');

    fireEvent.click(screen.getByRole('button', { name: 'Copy to clipboard' }));

    await waitFor(() => expect(navigator.clipboard.writeText).toHaveBeenCalledTimes(1));
    const copiedText = vi.mocked(navigator.clipboard.writeText).mock.calls[0]![0];
    const [header, ...rows] = copiedText.split('\r\n');
    expect(header).toBe('full_name,email,sign_up_at,status');
    expect(rows).toHaveLength(3);
    expect(rows[0]).toBe('Jordan Lee,jordan.lee@company.com,2026-08-07T18:00:00,Cancelled');
  });

  it('shows a transient "Copied!" confirmation after copying', async () => {
    renderPage();
    await screen.findByText('Jordan Lee');

    fireEvent.click(screen.getByRole('button', { name: 'Copy to clipboard' }));

    expect(await screen.findByRole('button', { name: 'Copied!' })).toBeInTheDocument();
  });

  it('exports via the real download endpoint rather than rebuilding the CSV client-side', async () => {
    renderPage();
    await screen.findByText('Jordan Lee');

    fireEvent.click(screen.getByRole('button', { name: 'Export CSV' }));

    await waitFor(() => expect(downloadAttendanceCsv).toHaveBeenCalledWith(11));
  });
});
