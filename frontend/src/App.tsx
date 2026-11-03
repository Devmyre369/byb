
import { useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Link,
} from "react-router-dom";

import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
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

const navigation = [
  { label: "Discover", symbol: "⌕" },
  { label: "Events", symbol: "▦" },
  { label: "Media", symbol: "▣" },
  { label: "Saved", symbol: "♡" },
];

function DiscoverPage() {
  const [activeNav, setActiveNav] = useState("Discover");
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
    <div className="app">
      <header className="topbar">
        <Link to="/" className="brand" aria-label="BYB home">
          BYB<span className="brand-accent">.</span>
        </Link>

        <div className="topbar-actions">
          <a href="#discover" className="nav-link active">
            Discover
          </a>
          <a href="#events" className="nav-link">
            Events
          </a>
          <a href="#media" className="nav-link">
            Media
          </a>

          <Link to="/login" className="avatar" aria-label="Login">
            U
          </Link>
        </div>
      </header>

      <div className="main-layout">
        <aside className="sidebar">
          <p className="sidebar-heading">MENU</p>

          {navigation.map((item) => (
            <button
              key={item.label}
              className={`sidebar-link ${
                activeNav === item.label ? "active" : ""
              }`}
              onClick={() => setActiveNav(item.label)}
            >
              <span aria-hidden="true">{item.symbol}</span>
              {item.label}
            </button>
          ))}

          <p className="sidebar-heading">YOUR SPACE</p>

          <Link to="/profile" className="sidebar-link">
            <span aria-hidden="true">◎</span>
            My Profile
          </Link>

          <Link to="/login" className="sidebar-link">
            <span aria-hidden="true">＋</span>
            Create Event
          </Link>
        </aside>

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
      </div>

      <nav className="mobile-bottom-nav" aria-label="Mobile navigation">
        {navigation.map((item) => (
          <button
            key={item.label}
            className={`mobile-nav-item ${
              activeNav === item.label ? "active" : ""
            }`}
            onClick={() => setActiveNav(item.label)}
          >
            <span aria-hidden="true">{item.symbol}</span>
            <small>{item.label}</small>
          </button>
        ))}
      </nav>
    </div>
  );
}

function ProtectedPlaceholder() {
  return (
    <div className="auth-placeholder">
      <div className="auth-card">
        <h2>Protected page</h2>
        <p>You are authenticated and can access this page.</p>
        <Link to="/" className="auth-switch">
          Back to Discover
        </Link>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<DiscoverPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
          <Route
            path="/profile"
            element={<ProtectedPlaceholder />}
          />
        </Route>

        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
