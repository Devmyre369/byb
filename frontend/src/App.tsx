
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
import ProfileSetupPage from "./pages/ProfileSetupPage";
import ProfilePage from "./pages/ProfilePage";
import DiscoverPage from "./pages/DiscoverPage";

import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";

import "./App.css";

function PlaceholderPage({ title }: { title: string }) {
  return (
    <section className="content">
      <span className="event-category">BEYOND YOUR BUBBLE</span>

      <h1>{title}</h1>

      <p className="section-subtitle">
        This section is under development. Stay tuned.
      </p>
    </section>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public authentication pages */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Application layout */}
        <Route element={<AppLayout />}>
          {/* Discover page - connected to backend API */}
          <Route index element={<DiscoverPage />} />

          {/* Public destinations */}
          <Route
            path="events"
            element={<PlaceholderPage title="Events" />}
          />

          <Route
            path="media"
            element={<PlaceholderPage title="Event Media" />}
          />

          {/* Protected destinations */}
          <Route element={<ProtectedRoute />}>
            <Route
              path="profile"
              element={<ProfilePage />}
            />

            <Route
              path="profile/edit"
              element={<ProfileSetupPage />}
            />

            <Route
              path="profile/setup"
              element={<ProfileSetupPage />}
            />

            <Route
              path="saved"
              element={<PlaceholderPage title="Saved Events" />}
            />

            <Route
              path="events/create"
              element={<PlaceholderPage title="Create Event" />}
            />

            <Route
              path="organizer"
              element={<PlaceholderPage title="Organizer Dashboard" />}
            />
          </Route>
        </Route>

        {/* Unknown routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
