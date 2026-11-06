
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getEvent, type EventItem } from "../api/events";

function formatDate(dateString: string, timezone: string) {
  if (!dateString) return "Date not specified";

  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return "Date not available";
  }

  try {
    return new Intl.DateTimeFormat("en-IN", {
      dateStyle: "full",
      timeStyle: "short",
      timeZone: timezone || undefined,
    }).format(date);
  } catch {
    return new Intl.DateTimeFormat("en-IN", {
      dateStyle: "full",
      timeStyle: "short",
    }).format(date);
  }
}

function formatLabel(value: string) {
  if (!value) return "Not specified";

  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function getErrorMessage(err: unknown) {
  const error = err as {
    response?: {
      status?: number;
      data?: {
        detail?: string;
      };
    };
  };

  const status = error?.response?.status;

  if (status === 404) {
    return "This event could not be found.";
  }

  if (status === 403) {
    return "You do not have permission to view this event.";
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  return (
    error?.response?.data?.detail ||
    "Unable to load this event. Please try again."
  );
}

function EventDetailPage() {
  const { eventId } = useParams<{ eventId: string }>();

  const [event, setEvent] = useState<EventItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let isMounted = true;

    async function loadEvent() {
      if (!eventId) {
        setError("Invalid event link.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const data = await getEvent(eventId);

        if (isMounted) {
          setEvent(data);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setEvent(null);
          setError(getErrorMessage(err));
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadEvent();

    return () => {
      isMounted = false;
    };
  }, [eventId, retryCount]);

  const handleRetry = () => {
    setRetryCount((previous) => previous + 1);
  };

  if (loading) {
    return (
      <section className="content event-detail-page">
        <div className="event-detail-loading">
          <div className="event-loading-spinner" />
          <p>Loading event...</p>
        </div>
      </section>
    );
  }

  if (error || !event) {
    return (
      <section className="content event-detail-page">
        <Link to="/discover" className="event-back-link">
          ← Back to Discover
        </Link>

        <div className="event-detail-message">
          <span className="event-category">
            BEYOND YOUR BUBBLE
          </span>

          <h2>Event unavailable</h2>

          <p>
            {error || "The requested event could not be loaded."}
          </p>

          {error.includes("session has expired") ? (
            <Link to="/login" className="event-retry-button">
              Sign In Again
            </Link>
          ) : (
            <button
              type="button"
              className="event-retry-button"
              onClick={handleRetry}
            >
              Try Again
            </button>
          )}
        </div>
      </section>
    );
  }

  const location = [
    event.location_name,
    event.city,
  ].filter(Boolean).join(", ");

  const eventType = formatLabel(event.event_type || "event");

  return (
    <section className="content event-detail-page">
      <Link to="/discover" className="event-back-link">
        ← Back to Discover
      </Link>

      <article className="event-detail-card">
        <div className="event-detail-cover-wrapper">
          {event.cover_image ? (
            <img
              src={event.cover_image}
              alt={`${event.title} cover`}
              className="event-detail-cover"
            />
          ) : (
            <div className="event-detail-cover event-detail-cover-fallback">
              <span>BEYOND YOUR BUBBLE</span>
              <h2>{event.title}</h2>
            </div>
          )}
        </div>

        <div className="event-detail-content">
          <div className="event-detail-labels">
            <span className="event-category">
              {eventType}
            </span>

            {event.category && (
              <span className="event-detail-category">
                {formatLabel(event.category)}
              </span>
            )}

            <span className="event-detail-status">
              {formatLabel(event.status)}
            </span>
          </div>

          <h1 className="event-detail-title">
            {event.title}
          </h1>

          {event.description && (
            <p className="event-detail-description">
              {event.description}
            </p>
          )}

          <div className="event-detail-section-heading">
            <h2>Event Information</h2>
            <span>Everything you need to know</span>
          </div>

          <div className="event-detail-information">
            <div className="event-detail-info-item">
              <span className="event-detail-info-label">
                DATE AND TIME
              </span>

              <p>
                {formatDate(event.starts_at, event.timezone)}
              </p>

              {event.ends_at && (
                <p className="event-detail-secondary">
                  Ends: {formatDate(event.ends_at, event.timezone)}
                </p>
              )}
            </div>

            <div className="event-detail-info-item">
              <span className="event-detail-info-label">
                LOCATION
              </span>

              <p>
                {location ||
                  event.location_address ||
                  "Location not specified"}
              </p>

              {event.location_address && location && (
                <p className="event-detail-secondary">
                  {event.location_address}
                </p>
              )}
            </div>

            <div className="event-detail-info-item">
              <span className="event-detail-info-label">
                VISIBILITY
              </span>

              <p>{formatLabel(event.visibility)}</p>
            </div>

            <div className="event-detail-info-item">
              <span className="event-detail-info-label">
                CAPACITY
              </span>

              <p>
                {event.capacity !== null && event.capacity !== undefined
                  ? `${event.capacity} people`
                  : "No capacity limit"}
              </p>
            </div>
          </div>

          {event.event_type === "public" && (
            <div className="event-registration-info">
              <h2>Registration</h2>

              <p>
                {event.registration_enabled
                  ? "Registration is enabled for this event."
                  : "Registration is currently unavailable."}
              </p>

              <p className="event-detail-secondary">
                Registration mode: {formatLabel(event.registration_mode)}
              </p>
            </div>
          )}
        </div>
      </article>
    </section>
  );
}

export default EventDetailPage;
