import { Navigate, Route, Routes } from 'react-router-dom';
import { RequireAdmin } from './auth/RequireAdmin';
import { RequireAuth } from './auth/RequireAuth';
import { CreateEventPage } from './pages/CreateEventPage/CreateEventPage';
import { FeedPage } from './pages/FeedPage/FeedPage';
import { LoginPage } from './pages/LoginPage/LoginPage';
import { OrganizerViewPage } from './pages/OrganizerViewPage/OrganizerViewPage';

/**
 * /login is the effective default/landing route: an unauthenticated
 * visitor always lands there first (root "/" and any unmatched path
 * redirect there too), and LoginPage itself immediately forwards an
 * already-authenticated visitor on to /events — so /events is never
 * reachable as a "default" for someone who isn't authenticated.
 *
 * The Feed's event detail view is an in-page modal driven by component
 * state, not a route — matching the mockup's actual interaction model.
 */
function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />

      <Route element={<RequireAuth />}>
        <Route path="/events" element={<FeedPage />} />

        <Route element={<RequireAdmin />}>
          <Route path="/events/new" element={<CreateEventPage />} />
          <Route path="/events/:id/attendance" element={<OrganizerViewPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;
