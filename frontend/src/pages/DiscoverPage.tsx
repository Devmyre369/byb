
import { useEffect, useMemo, useState } from "react";
import {
  getEvents,
  type EventItem,
} from "../api/events";

function formatEventDate(event: EventItem): string {
  const date = new Date(event.starts_at);

  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  try {
    return new Intl.DateTimeFormat("en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: event.timezone || undefined,
    }).format(date);
  } catch {
    return new Intl.DateTimeFormat("en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  }
}

function getEventLocation(event: EventItem): string {
  return (
    event.location_name ||
    event.city ||
    event.location_address ||
    "Location not specified"
  );
}

function DiscoverPage() {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  async function loadEvents(pageNumber: number) {
    try {
      if (pageNumber === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }

      setError("");

      const response = await getEvents(pageNumber, 20);

      setEvents((previous) =>
        pageNumber === 1
          ? response.results
          : [...previous, ...response.results]
      );

      setHasMore(Boolean(response.next));
      setPage(pageNumber);
    } catch (err: unknown) {
      console.error("Failed to load events:", err);

      setError(
        "We couldn't load events right now. Please try again."
      );
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }

  useEffect(() => {
    void loadEvents(1);
  }, []);

  const categories = useMemo(() => {
    const uniqueCategories = Array.from(
      new Set(
        events
          .map((event) => event.category?.trim())
          .filter((category): category is string => Boolean(category))
      )
    );

    return ["All", ...uniqueCategories.sort()];
  }, [events]);

  const filteredEvents = useMemo(() => {
    const searchTerm = search.trim().toLowerCase();

    return events.filter((event) => {
      const matchesCategory =
        activeCategory === "All" ||
        event.category === activeCategory;

      const searchableText = [
        event.title,
        event.description,
        event.category,
        event.event_type,
        event.city,
        event.location_name,
        event.location_address,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      const matchesSearch =
        !searchTerm || searchableText.includes(searchTerm);

      return matchesCategory && matchesSearch;
    });
  }, [events, search, activeCategory]);

  const resetFilters = () => {
    setSearch("");
    setActiveCategory("All");
  };

  return (
    <div className="content discover-page" id="discover">
      <section className="discover-header">
        <div className="discover-heading-copy">
          <span className="event-category">
            BEYOND YOUR BUBBLE
          </span>

          <h1>Discover your next experience.</h1>

          <p>
            Find what's happening around you. Explore events,
            meet new people and discover experiences beyond
            your everyday bubble.
          </p>
        </div>
      </section>

      <section className="search-section">
        <span className="search-icon" aria-hidden="true">
          ⌕
        </span>

        <input
          type="search"
          className="search-box"
          placeholder="Search events, interests or locations..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          aria-label="Search events"
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

      {!loading && !error && categories.length > 1 && (
        <section className="categories-section">
          <div
            className="category-list"
            aria-label="Filter events by category"
          >
            {categories.map((category) => (
              <button
                type="button"
                key={category}
                className={`category-chip ${
                  activeCategory === category ? "active" : ""
                }`}
                onClick={() => setActiveCategory(category)}
                aria-pressed={activeCategory === category}
              >
                {category}
              </button>
            ))}
          </div>
        </section>
      )}

      <section className="events-section" id="events">
        <div className="section-heading">
          <div>
            <span className="section-eyebrow">
              FIND YOUR NEXT PLAN
            </span>

            <h2>Discover events</h2>

            <p className="section-subtitle">
              Experiences worth stepping out for.
            </p>
          </div>

          {!loading && !error && (
            <span className="event-count">
              {filteredEvents.length}{" "}
              {filteredEvents.length === 1 ? "event" : "events"}
            </span>
          )}
        </div>

        {loading ? (
          <div className="profile-loading">
            Loading events...
          </div>
        ) : error ? (
          <div className="empty-state">
            <h3>Unable to load events</h3>

            <p>{error}</p>

            <button
              type="button"
              className="reset-filters-button"
              onClick={() => void loadEvents(1)}
            >
              Try again
            </button>
          </div>
        ) : filteredEvents.length > 0 ? (
          <>
            <div className="event-grid">
              {filteredEvents.map((event) => (
                <article className="event-card" key={event.id}>
                  <div className="event-placeholder">
                    {event.cover_image ? (
                      <img
                        src={event.cover_image}
                        alt={`${event.title} cover`}
                        loading="lazy"
                      />
                    ) : (
                      <span className="event-image-brand">
                        BYB.
                      </span>
                    )}

                    <span className="event-image-label">
                      {event.event_type}
                    </span>
                  </div>

                  <div className="event-details">
                    <span className="event-category">
                      {event.category || event.event_type}
                    </span>

                    <h3 className="event-title">
                      {event.title}
                    </h3>

                    <p className="event-description">
                      {event.description ||
                        "Discover this experience on BYB."}
                    </p>

                    <div className="event-meta">
                      <span>
                        ◷ {formatEventDate(event)}
                      </span>

                      <span>
                        ⌖ {getEventLocation(event)}
                      </span>
                    </div>

                    <div className="event-card-footer">
                      <span className="attendee-count">
                        {event.status}
                      </span>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            {hasMore && activeCategory === "All" && !search && (
              <div className="load-more-container">
                <button
                  type="button"
                  className="event-action"
                  disabled={loadingMore}
                  onClick={() => void loadEvents(page + 1)}
                >
                  {loadingMore ? "Loading..." : "Load more events"}
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="empty-state">
            <span className="empty-state-icon">
              ⌕
            </span>

            <h3>No events found</h3>

            <p>
              We couldn't find events matching your search.
              Try another keyword or choose a different category.
            </p>

            <button
              type="button"
              className="reset-filters-button"
              onClick={resetFilters}
            >
              Clear filters
            </button>
          </div>
        )}
      </section>

      <section className="discover-footer">
        <span className="discover-footer-brand">BYB.</span>

        <p>
          Step outside your bubble. Discover something new.
        </p>
      </section>
    </div>
  );
}

export default DiscoverPage;
