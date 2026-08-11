import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { ApiError } from '../../api/client';
import { AuthContext, type AuthContextValue } from '../../auth/AuthContext';
import { LoginPage } from './LoginPage';

function renderLoginPage(overrides: Partial<AuthContextValue> = {}) {
  const login = vi.fn();
  const value: AuthContextValue = {
    token: null,
    user: null,
    login,
    logout: vi.fn(),
    ...overrides,
  };

  render(
    <AuthContext value={value}>
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/events" element={<div>Feed page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext>,
  );

  return { login };
}

describe('LoginPage', () => {
  it('rejects an invalid email client-side without calling login', () => {
    const { login } = renderLoginPage();

    fireEvent.change(screen.getByPlaceholderText('you@company.com'), {
      target: { value: 'not-an-email' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }));

    expect(screen.getByText('Enter a valid work email to continue.')).toBeInTheDocument();
    expect(login).not.toHaveBeenCalled();
  });

  it('shows a disabled "checking" state while the login request is in flight', async () => {
    let resolveLogin: () => void = () => {};
    const login = vi.fn(
      () =>
        new Promise<void>((resolve) => {
          resolveLogin = resolve;
        }),
    );
    renderLoginPage({ login });

    fireEvent.change(screen.getByPlaceholderText('you@company.com'), {
      target: { value: 'alice.kim@company.com' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }));

    expect(await screen.findByRole('button', { name: 'Checking your account…' })).toBeDisabled();
    resolveLogin();
  });

  it('surfaces the real 401 message on an unrecognized email', async () => {
    const login = vi
      .fn()
      .mockRejectedValue(
        new ApiError(
          { error: 'unauthorized', message: 'Email not recognized.', details: null },
          401,
        ),
      );
    renderLoginPage({ login });

    fireEvent.change(screen.getByPlaceholderText('you@company.com'), {
      target: { value: 'nobody@company.com' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }));

    expect(await screen.findByText('Email not recognized.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Continue' })).not.toBeDisabled();
  });

  it('navigates to /events after a successful login', async () => {
    const login = vi.fn().mockResolvedValue(undefined);
    renderLoginPage({ login });

    fireEvent.change(screen.getByPlaceholderText('you@company.com'), {
      target: { value: 'alice.kim@company.com' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }));

    expect(await screen.findByText('Feed page')).toBeInTheDocument();
  });

  it('redirects to /events immediately when already authenticated', () => {
    renderLoginPage({ token: 'existing-token' });
    expect(screen.getByText('Feed page')).toBeInTheDocument();
  });
});
