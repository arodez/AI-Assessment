import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './AuthContext';

/** Same UX-convenience caveat as RequireAuth — the backend's
 * @admin_required decorator is the real enforcement boundary. Nested
 * under <RequireAuth> in the route table, so `user` is guaranteed
 * non-null here in practice, but checked defensively anyway. */
export function RequireAdmin() {
  const { user } = useAuth();

  if (!user?.is_admin) {
    return <Navigate to="/events" replace />;
  }

  return <Outlet />;
}
