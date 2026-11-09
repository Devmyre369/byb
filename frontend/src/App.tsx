
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
import HomePage from "./pages/HomePage";
import DiscoverPage from "./pages/DiscoverPage";
import HubDiscoverPage from "./pages/HubDiscoverPage";
import EventDetailPage from "./pages/EventDetailPage";
import CreateEventPage from "./pages/CreateEventPage";
import PersonalEventFormPage from "./pages/PersonalEventFormPage";
import SocialEventFormPage from "./pages/SocialEventFormPage";
import PublicEventFormPage from "./pages/PublicEventFormPage";
import LaunchPage from "./pages/LaunchPage";
import WelcomePage from "./pages/WelcomePage";

import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";

import "./App.css";

function PlaceholderPage({ title }: { title: string }) {
  return (
    <section className="content">
      <span className="event-category">
        BEYOND YOUR BUBBLE
      </span>

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
        {/* Startup and welcome experience */}
        <Route path="/" element={<LaunchPage />} />
        <Route path="/welcome" element={<WelcomePage />} />

        {/* Authentication pages */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Main application layout */}
        <Route element={<AppLayout />}>
          {/* Public destinations */}
          <Route
            path="events"
            element={<PlaceholderPage title="Events" />}
          />

          <Route
            path="media"
            element={<PlaceholderPage title="Event Media" />}
          />

          <Route
            path="hubs"
            element={<HubDiscoverPage />}
          />

          {/* Protected destinations */}
          <Route element={<ProtectedRoute />}>
            <Route
              path="home"
              element={<HomePage />}
            />

            <Route
              path="discover"
              element={<DiscoverPage />}
            />

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

            {/* Event creation */}
            <Route
              path="events/create"
              element={<CreateEventPage />}
            />

            <Route
              path="events/create/personal"
              element={<PersonalEventFormPage />}
            />

            <Route
              path="events/create/social"
              element={<SocialEventFormPage />}
            />

            <Route
              path="events/create/public"
              element={<PublicEventFormPage />}
            />

            {/* Event details */}
            <Route
              path="events/:eventId"
              element={<EventDetailPage />}
            />

            <Route
              path="organizer"
              element={<PlaceholderPage title="Organizer Dashboard" />}
            />
          </Route>
        </Route>

        {/* Unknown routes */}
        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
