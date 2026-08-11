import { useState, type FormEvent } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { ApiError } from '../../api/client';
import { useAuth } from '../../auth/AuthContext';
import styles from './LoginPage.module.css';

// Same client-side format check as the mockup — a fast local rejection
// before ever hitting the network. The API is still the final authority:
// it separately rejects malformed emails (400) and well-formed-but-
// unseeded emails (401, since account creation is out of scope).
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function LoginPage() {
  const { token, login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [hasFormatError, setHasFormatError] = useState(false);
  const [apiErrorMessage, setApiErrorMessage] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'checking'>('idle');

  // Already authenticated (e.g. a stored token from a previous session)
  // — forward straight to the feed rather than showing the login form
  // again.
  if (token) {
    return <Navigate to="/events" replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = email.trim();

    if (!EMAIL_PATTERN.test(trimmed)) {
      setHasFormatError(true);
      setApiErrorMessage(null);
      return;
    }

    setHasFormatError(false);
    setApiErrorMessage(null);
    setStatus('checking');

    try {
      await login(trimmed);
      navigate('/events');
    } catch (error) {
      setStatus('idle');
      if (error instanceof ApiError) {
        setApiErrorMessage(error.message);
      } else {
        setApiErrorMessage('Something went wrong. Please try again.');
      }
    }
  }

  const checking = status === 'checking';

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.logoGroup}>
          <div className={styles.logoMark}>
            <span>E</span>
          </div>
          <div className={styles.logoText}>EVENTS HUB</div>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.card}>
          <h1 className={styles.title}>Welcome</h1>
          <p className={styles.subtitle}>
            Enter your work email — we&rsquo;ll take care of the rest.
          </p>

          <form onSubmit={handleSubmit} noValidate>
            <label htmlFor="email" className={styles.label}>
              Work Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                setHasFormatError(false);
                setApiErrorMessage(null);
              }}
              placeholder="you@company.com"
              className={`${styles.input} ${hasFormatError || apiErrorMessage ? styles.inputError : ''}`}
              disabled={checking}
            />

            {hasFormatError && (
              <div className={styles.errorText}>Enter a valid work email to continue.</div>
            )}
            {apiErrorMessage && <div className={styles.errorText}>{apiErrorMessage}</div>}

            <button type="submit" className={styles.submit} disabled={checking}>
              {checking ? 'Checking your account…' : 'Continue'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
