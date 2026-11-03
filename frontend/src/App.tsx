
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
  time: string;
  location: string;
  college: string;
  attendees: string;
  description: string;
  gradient: string;
  featured?: boolean;
};

const events: Event[] = [
  {
    id: 1,
    title: "Campus Tech Fest 2026",
    category: "Technology",
    date: "November 15, 2026",
    time: "10:00 AM",
    location: "Lucknow",
    college: "University Campus",
    attendees: "250+ interested",
    description:
      "A celebration of technology, innovation and ideas. Meet builders, explore new technologies and connect with people who share your curiosity.",
    gradient: "linear-gradient(135deg, #491923, #B83246, #211519)",
    featured: true,
  },
  {
    id: 2,
    title: "The Ultimate Music Night",
    category: "Music",
    date: "November 18, 2026",
    time: "6:00 PM",
    location: "Lucknow",
    college: "University Campus",
    attendees: "180+ interested",
    description: "An evening of live music, performances and good energy.",
    gradient: "linear-gradient(135deg, #32132C, #9D315B, #211519)",
  },
  {
    id: 3,
    title: "Startup & Entrepreneurship Summit",
    category: "Entrepreneurship",
    date: "November 21, 2026",
    time: "11:00 AM",
    location: "Lucknow",
    college: "University Campus",
    attendees: "120+ interested",
    description: "Connect with founders, innovators and aspiring entrepreneurs.",
    gradient: "linear-gradient(135deg, #251B36, #694078, #211519)",
  },
  {
    id: 4,
    title: "Creative Minds Meetup",
    category: "Community",
    date: "November 25, 2026",
    time: "4:00 PM",
    location: "Lucknow",
    college: "University Campus",
    attendees: "90+ interested",
    description: "A space for creative people to exchange ideas and collaborate.",
    gradient: "linear-gradient(135deg, #3B2020, #A64B36, #211519)",
  },
  {
    id: 5,
    title: "Inter-College Sports Meet",
    category: "Sports",
    date: "November 28, 2026",
    time: "9:00 AM",
    location: "Lucknow",
    college: "University Campus",
    attendees: "150+ interested",
    description: "Bring your team and compete in an energetic campus sports meet.",
    gradient: "linear-gradient(135deg, #19382D, #34765A, #15221B)",
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
      activeCategory === "All" || event.category === activeCategory;

    const searchTerm = search.trim().toLowerCase();

    const matchesSearch =
      event.title.toLowerCase().includes(searchTerm) ||
      event.category.toLowerCase().includes(searchTerm) ||
      event.location.toLowerCase().includes(searchTerm) ||
      event.college.toLowerCase().includes(searchTerm);

    return matchesCategory && matchesSearch;
  });

  const featuredEvent = filteredEvents.find((event) => event.featured);
  const upcomingEvents = filteredEvents.filter((event) => !event.featured);

  return (
    <div className="content discover-page" id="discover">
      {/* Page introduction */}
      <section className="discover-header">
        <div className="discover-heading-copy">
          <span className="event-category">BEYOND YOUR BUBBLE</span>

          <h1>Discover your next experience.</h1>

          <p>
            Find what's happening around you. Explore events, meet new people
            and discover experiences beyond your campus.
          </p>
        </div>

        <div className="discover-location">
          <span className="location-indicator">⌖</span>
          <div>
            <span className="location-label">EXPLORING</span>
            <strong>Lucknow, India</strong>
          </div>
        </div>
      </section>

      {/* Search */}
      <section className="search-section">
        <span className="search-icon">⌕</span>

        <input
          type="search"
          className="search-box"
          placeholder="Search events, interests, colleges or locations..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          aria-label="Search events, interests, colleges or locations"
        />

        {search && (
          <button
            type="button"
            className="clear-search"
            onClick={() => setSearch("")}
            aria-label="Clear search"
          >
            ×
          </button>
        )}
      </section>

      {/* Categories */}
      <section className="categories-section">
        <div className="category-list" aria-label="Filter events by category">
          {categories.map((category) => (
            <button
              type="button"
              key={category}
              className={`category-chip ${
                activeCategory === category ? "selected" : ""
              }`}
              onClick={() => setActiveCategory(category)}
              aria-pressed={activeCategory === category}
            >
              {category}
            </button>
          ))}
        </div>
      </section>

      {/* Featured event */}
      {featuredEvent && (
        <section className="featured-section">
          <div className="section-heading">
            <div>
              <span className="section-eyebrow">DON'T MISS OUT</span>
              <h2>Featured experience</h2>
            </div>

            <span className="featured-tag">✦ FEATURED</span>
          </div>

          <article className="featured-event-card">
            <div
              className="featured-event-visual"
              style={{ background: featuredEvent.gradient }}
            >
              <span className="featured-visual-brand">BYB.</span>
              <span className="featured-visual-category">
                {featuredEvent.category}
              </span>
              <span className="featured-visual-caption">
                SOMETHING BIG IS HAPPENING.
              </span>
            </div>

            <div className="featured-event-content">
              <span className="event-category">
                {featuredEvent.category}
              </span>

              <h3>{featuredEvent.title}</h3>

              <p className="featured-description">
                {featuredEvent.description}
              </p>

              <div className="featured-event-meta">
                <span>◷ {featuredEvent.date}</span>
                <span>⌖ {featuredEvent.location}</span>
              </div>

              <div className="featured-event-footer">
                <span className="attendee-count">
                  {featuredEvent.attendees}
                </span>

                <button
                  type="button"
                  className="featured-event-action"
                  onClick={() =>
                    window.alert(`${featuredEvent.title} details coming soon.`)
                  }
                >
                  Explore event <span>↗</span>
                </button>
              </div>
            </div>
          </article>
        </section>
      )}

      {/* Upcoming events */}
      <section className="events-section" id="events">
        <div className="section-heading">
          <div>
            <span className="section-eyebrow">FIND YOUR NEXT PLAN</span>
            <h2>Upcoming events</h2>
            <p className="section-subtitle">
              Experiences worth stepping out for.
            </p>
          </div>

          <span className="event-count">
            {filteredEvents.length}{" "}
            {filteredEvents.length === 1 ? "event" : "events"}
          </span>
        </div>

        {upcomingEvents.length > 0 ? (
          <div className="event-grid">
            {upcomingEvents.map((event) => (
              <article className="event-card" key={event.id}>
                <div
                  className="event-image event-placeholder"
                  style={{ background: event.gradient }}
                >
                  <span className="event-image-label">{event.category}</span>
                  <span className="event-image-brand">BYB.</span>
                </div>

                <div className="event-details">
                  <span className="event-category">{event.category}</span>

                  <h3 className="event-title">{event.title}</h3>

                  <p className="event-description">{event.description}</p>

                  <div className="event-meta">
                    <span>◷ {event.date}</span>
                    <span>⌖ {event.location}</span>
                  </div>

                  <div className="event-card-footer">
                    <span className="attendee-count">
                      {event.attendees}
                    </span>

                    <button
                      type="button"
                      className="event-action"
                      onClick={() =>
                        window.alert(`${event.title} details coming soon.`)
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
            <span className="empty-state-icon">⌕</span>
            <h3>No events found</h3>
            <p>
              We couldn't find events matching your search. Try another
              keyword or choose a different category.
            </p>

            <button
              type="button"
              className="reset-filters-button"
              onClick={() => {
                setSearch("");
                setActiveCategory("All");
              }}
            >
              Clear filters
            </button>
          </div>
        )}
      </section>

      {/* Discovery footer */}
      <section className="discover-footer">
        <span className="discover-footer-brand">BYB.</span>
        <p>Step outside your bubble. Discover something new.</p>
      </section>
    </div>
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
