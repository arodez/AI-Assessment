import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import type { LoginUser } from '../api/types';
import { AuthContext, type AuthContextValue } from './AuthContext';
import { RequireAdmin } from './RequireAdmin';

function renderWithUser(user: LoginUser | null) {
  const value: AuthContextValue = {
    token: user ? 'a-token' : null,
    user,
    login: async () => {},
    logout: () => {},
  };

  render(
    <AuthContext value={value}>
      <MemoryRouter initialEntries={['/events/new']}>
        <Routes>
          <Route path="/events" element={<div>Feed page</div>} />
          <Route element={<RequireAdmin />}>
            <Route path="/events/new" element={<div>Create Event page</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </AuthContext>,
  );
}

describe('RequireAdmin', () => {
  it('renders the admin route when the user is an admin', () => {
    renderWithUser({ id: 1, first_name: 'Alice', is_admin: true });
    expect(screen.getByText('Create Event page')).toBeInTheDocument();
  });

  it('redirects a non-admin attendee to /events', () => {
    renderWithUser({ id: 2, first_name: 'Taylor', is_admin: false });
    expect(screen.getByText('Feed page')).toBeInTheDocument();
  });

  it('redirects to /events defensively when there is no user at all', () => {
    renderWithUser(null);
    expect(screen.getByText('Feed page')).toBeInTheDocument();
  });
});
