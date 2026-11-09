
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getMoments,
  type Moment,
} from "../api/moments";

function formatMomentTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Recently";
  }

  const seconds = Math.floor(
    (Date.now() - date.getTime()) / 1000
  );

  if (seconds < 60) return "Just now";
  if (seconds < 3600) {
    return `${Math.floor(seconds / 60)}m ago`;
  }
  if (seconds < 86400) {
    return `${Math.floor(seconds / 3600)}h ago`;
  }
  if (seconds < 604800) {
    return `${Math.floor(seconds / 86400)}d ago`;
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date);
}

function getUploaderName(moment: Moment): string {
  return (
    moment.uploader.first_name?.trim() ||
    moment.uploader.username ||
    "BYB member"
  );
}

function HomePage() {
  const [moments, setMoments] = useState<Moment[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  async function loadMoments(pageNumber: number) {
    try {
      if (pageNumber === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }

      setError("");

      const response = await getMoments(pageNumber, 20);

      setMoments((previous) =>
        pageNumber === 1
          ? response.results
          : [...previous, ...response.results]
      );

      setPage(pageNumber);
      setHasMore(Boolean(response.next));
    } catch (err: unknown) {
      console.error("Failed to load moments:", err);

      setError(
        "We couldn't load moments right now. Please try again."
      );
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }

  useEffect(() => {
    void loadMoments(1);
  }, []);

  return (
    <main className="content home-page">
      <section className="home-header">
        <div>
          <span className="event-category">
            BEYOND YOUR BUBBLE
          </span>

          <h1>Vibes &amp; Moments.</h1>

          <p>
            Real people. Real events. Real moments.
            See what is happening beyond your bubble.
          </p>
        </div>

        <Link
          to="/discover"
          className="home-discover-link"
        >
          Explore events <span aria-hidden="true">→</span>
        </Link>
      </section>

      <section className="moments-section">
        <div className="section-heading">
          <div>
            <span className="section-eyebrow">
              THE BYB COMMUNITY
            </span>

            <h2>Moments from the community</h2>

            <p className="section-subtitle">
              Memories shared by people at real-world events.
            </p>
          </div>

          {!loading && !error && (
            <span className="event-count">
              {moments.length}{" "}
              {moments.length === 1 ? "moment" : "moments"}
            </span>
          )}
        </div>

        {loading ? (
          <div className="profile-loading">
            Loading moments...
          </div>
        ) : error ? (
          <div className="empty-state">
            <h3>Unable to load moments</h3>
            <p>{error}</p>

            <button
              type="button"
              className="reset-filters-button"
              onClick={() => void loadMoments(1)}
            >
              Try again
            </button>
          </div>
        ) : moments.length > 0 ? (
          <>
            <div className="moments-grid">
              {moments.map((moment) => (
                <article
                  className="moment-card"
                  key={moment.id}
                >
                  <div className="moment-card-header">
                    <div className="moment-uploader">
                      {moment.uploader.profile_picture ? (
                        <img
                          className="moment-avatar"
                          src={moment.uploader.profile_picture}
                          alt=""
                          loading="lazy"
                        />
                      ) : (
                        <span className="moment-avatar moment-avatar-fallback">
                          {getUploaderName(moment)
                            .charAt(0)
                            .toUpperCase()}
                        </span>
                      )}

                      <div className="moment-uploader-info">
                        <strong>
                          {getUploaderName(moment)}
                        </strong>

                        <span>
                          {formatMomentTime(moment.created_at)}
                        </span>
                      </div>
                    </div>

                    <span className="moment-type-label">
                      VIBE
                    </span>
                  </div>

                  <Link
                    to={`/events/${moment.event.id}`}
                    className="moment-image-link"
                    aria-label={`View event ${moment.event.title}`}
                  >
                    <img
                      className="moment-image"
                      src={moment.cloudinary_url}
                      alt={
                        moment.caption ||
                        `Moment from ${moment.event.title}`
                      }
                      loading="lazy"
                    />
                  </Link>

                  <div className="moment-card-content">
                    {moment.caption && (
                      <p className="moment-caption">
                        {moment.caption}
                      </p>
                    )}

                    <Link
                      to={`/events/${moment.event.id}`}
                      className="moment-event-link"
                    >
                      <span className="moment-event-label">
                        FROM THIS EVENT
                      </span>

                      <strong>{moment.event.title}</strong>

                      <span className="moment-location">
                        {[
                          moment.event.location_name,
                          moment.event.city,
                        ]
                          .filter(Boolean)
                          .join(", ") || "Location not specified"}
                      </span>
                    </Link>
                  </div>
                </article>
              ))}
            </div>

            {hasMore && (
              <div className="load-more-container">
                <button
                  type="button"
                  className="event-action"
                  disabled={loadingMore}
                  onClick={() => void loadMoments(page + 1)}
                >
                  {loadingMore
                    ? "Loading..."
                    : "Load more moments"}
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="empty-state home-empty-state">
            <span className="empty-state-icon">✦</span>

            <h3>The next great moment starts here.</h3>

            <p>
              There are no approved moments to show yet.
              Join an event, capture the experience and
              share your photos with the BYB community.
            </p>

            <Link
              to="/discover"
              className="reset-filters-button"
            >
              Discover events
            </Link>
          </div>
        )}
      </section>
    </main>
  );
}

export default HomePage;

import './HomePage.css';
