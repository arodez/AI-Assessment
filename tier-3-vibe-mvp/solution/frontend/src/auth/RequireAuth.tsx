import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

/**
 * UX convenience only. Every admin-only mutation the frontend can trigger
 * (POST /event, GET /event/:id/attendance*) is independently enforced
 * server-side with a real 403 — no security depends on this component
 * existing. It just avoids showing a page that would immediately fail
 * every request it makes.
 */
export function RequireAuth() {
  const { token } = useAuth();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
