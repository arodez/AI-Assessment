import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { AuthContext, type AuthContextValue } from './AuthContext';
import { RequireAuth } from './RequireAuth';

function renderWithToken(token: string | null) {
  const value: AuthContextValue = {
    token,
    user: token ? { id: 1, first_name: 'Alice', is_admin: false } : null,
    login: async () => {},
    logout: () => {},
  };

  render(
    <AuthContext value={value}>
      <MemoryRouter initialEntries={['/events']}>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route element={<RequireAuth />}>
            <Route path="/events" element={<div>Feed page</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </AuthContext>,
  );
}

describe('RequireAuth', () => {
  it('renders the protected route when a token is present', () => {
    renderWithToken('a-token');
    expect(screen.getByText('Feed page')).toBeInTheDocument();
  });

  it('redirects to /login when there is no token', () => {
    renderWithToken(null);
    expect(screen.getByText('Login page')).toBeInTheDocument();
  });
});
