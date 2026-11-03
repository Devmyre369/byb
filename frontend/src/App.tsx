
import { useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";

import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";

import "./App.css";

type Event = {
  id: number;
  title: string;
  category: string;
  date: string;
  location: string;
  attendees: string;
  gradient: string;
};

const events: Event[] = [
  {
    id: 1,
    title: "Campus Tech Fest 2026",
    category: "Technology",
    date: "November 15, 2026",
    location: "Lucknow",
    attendees: "250+ interested",
    gradient: "linear-gradient(135deg, #491923, #B83246, #211519)",
  },
  {
    id: 2,
    title: "The Ultimate Music Night",
    category: "Music",
    date: "November 18, 2026",
    location: "Lucknow",
    attendees: "180+ interested",
    gradient: "linear-gradient(135deg, #32132C, #9D315B, #211519)",
  },
  {
    id: 3,
    title: "Startup & Entrepreneurship Summit",
    category: "Entrepreneurship",
    date: "November 21, 2026",
    location: "Lucknow",
    attendees: "120+ interested",
    gradient: "linear-gradient(135deg, #251B36, #694078, #211519)",
  },
  {
    id: 4,
    title: "Creative Minds Meetup",
    category: "Community",
    date: "November 25, 2026",
    location: "Lucknow",
    attendees: "90+ interested",
    gradient: "linear-gradient(135deg, #3B2020, #A64B36, #211519)",
  },
];

const categories = [
  "All",
  "Technology",
  "Music",
  "Entrepreneurship",
  "Community",
  "Sports",
];

function DiscoverPage() {
  const [activeCategory, setActiveCategory] = useState("All");
  const [search, setSearch] = useState("");

  const filteredEvents = events.filter((event) => {
    const matchesCategory =
      activeCategory === "All" ||
      event.category === activeCategory;

    const matchesSearch =
      event.title.toLowerCase().includes(search.toLowerCase()) ||
      event.category.toLowerCase().includes(search.toLowerCase()) ||
      event.location.toLowerCase().includes(search.toLowerCase());

    return matchesCategory && matchesSearch;
  });

  return (
    <main className="content" id="discover">
      <section className="page-heading">
        <span className="event-category">BEYOND YOUR BUBBLE</span>

        <h1>Discover your next experience.</h1>

        <p>
          Find events, meet new people and explore what's
          happening around you.
        </p>
      </section>

      <section className="search-section">
        <input
          type="search"
          className="search-box"
          placeholder="Search events, interests or locations..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          aria-label="Search events"
        />
      </section>

      <section className="categories-section">
        <div className="category-list">
          {categories.map((category) => (
            <button
              key={category}
              className={`category-chip ${
                activeCategory === category ? "selected" : ""
              }`}
              onClick={() => setActiveCategory(category)}
            >
              {category}
            </button>
          ))}
        </div>
      </section>

      <section className="events-section" id="events">
        <div className="section-heading">
          <div>
            <h2>Discover events</h2>
            <p className="section-subtitle">
              Experiences worth stepping out for.
            </p>
          </div>

          <span className="event-count">
            {filteredEvents.length} events
          </span>
        </div>

        {filteredEvents.length > 0 ? (
          <div className="event-grid">
            {filteredEvents.map((event) => (
              <article className="event-card" key={event.id}>
                <div
                  className="event-image event-placeholder"
                  style={{ background: event.gradient }}
                >
                  <span className="event-image-label">
                    {event.category}
                  </span>
                  <span className="event-image-brand">BYB.</span>
                </div>

                <div className="event-details">
                  <span className="event-category">
                    {event.category}
                  </span>

                  <h3 className="event-title">
                    {event.title}
                  </h3>

                  <div className="event-meta">
                    <span>◷ {event.date}</span>
                    <span>⌖ {event.location}</span>
                  </div>

                  <div className="event-card-footer">
                    <span className="attendee-count">
                      {event.attendees}
                    </span>

                    <button
                      className="event-action"
                      onClick={() =>
                        alert(`${event.title} details coming soon`)
                      }
                    >
                      Explore ↗
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <h3>No events found</h3>
            <p>
              Try another search or choose a different category.
            </p>
          </div>
        )}
      </section>
    </main>
  );
}

// Temporary page until the actual feature is implemented.
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
              element={<PlaceholderPage title="My Profile" />}
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

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
