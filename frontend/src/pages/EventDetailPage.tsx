
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getEvent, type EventItem } from "../api/events";

function formatDate(dateString: string, timezone: string) {
  if (!dateString) return "Date not specified";

  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return "Date not available";
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "full",
    timeStyle: "short",
    timeZone: timezone || undefined,
  }).format(date);
}

function EventDetailPage() {
  const { eventId } = useParams<{ eventId: string }>();

  const [event, setEvent] = useState<EventItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
      } catch (err: any) {
        if (isMounted) {
          const status = err?.response?.status;

          if (status === 404) {
            setError("This event could not be found.");
          } else if (status === 403) {
            setError("You do not have permission to view this event.");
          } else if (status === 401) {
            setError("Your session has expired. Please log in again.");
          } else {
            setError(
              err?.response?.data?.detail ||
              "Unable to load this event. Please try again."
            );
          }
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
  }, [eventId]);

  if (loading) {
    return (
      <section className="content event-detail-page">
        <p className="event-detail-message">Loading event...</p>
      </section>
    );
  }

  if (error || !event) {
    return (
      <section className="content event-detail-page">
        <Link to="/" className="event-back-link">
          ← Back to Discover
        </Link>

        <div className="event-detail-message">
          <h2>Event unavailable</h2>
          <p>{error || "The requested event could not be loaded."}</p>
        </div>
      </section>
    );
  }

  const location = [
    event.location_name,
    event.city,
  ].filter(Boolean).join(", ");

  const eventType = event.event_type || "Event";

  return (
    <section className="content event-detail-page">
      <Link to="/" className="event-back-link">
        ← Back to Discover
      </Link>

      <div className="event-detail-card">
        {event.cover_image ? (
          <img
            src={event.cover_image}
            alt={event.title}
            className="event-detail-cover"
          />
        ) : (
          <div className="event-detail-cover event-detail-cover-fallback">
            <span>BEYOND YOUR BUBBLE</span>
            <h2>{event.title}</h2>
          </div>
        )}

        <div className="event-detail-content">
          <div className="event-detail-labels">
            <span className="event-category">
              {eventType}
            </span>

            {event.category && (
              <span className="event-detail-category">
                {event.category}
              </span>
            )}

            <span className="event-detail-status">
              {event.status}
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

          <div className="event-detail-information">
            <div className="event-detail-info-item">
              <span className="event-detail-info-label">
                DATE AND TIME
              </span>
              <p>
                {formatDate(event.starts_at, event.timezone)}
              </p>

              {event.ends_at && (
                <p>
                  Ends: {formatDate(event.ends_at, event.timezone)}
                </p>
              )}
            </div>

            <div className="event-detail-info-item">
              <span className="event-detail-info-label">
                LOCATION
              </span>
              <p>
                {location || event.location_address || "Location not specified"}
              </p>

              {event.location_address && location && (
                <p>{event.location_address}</p>
              )}
            </div>

            <div className="event-detail-info-item">
              <span className="event-detail-info-label">
                EVENT VISIBILITY
              </span>
              <p>{event.visibility}</p>
            </div>

            <div className="event-detail-info-item">
              <span className="event-detail-info-label">
                CAPACITY
              </span>
              <p>
                {event.capacity
                  ? `${event.capacity} people`
                  : "No capacity limit specified"}
              </p>
            </div>
          </div>

          {event.event_type === "public" && (
            <div className="event-registration-info">
              <h3>Registration</h3>
              <p>
                {event.registration_enabled
                  ? "Registration is enabled for this event."
                  : "Registration is currently unavailable."}
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default EventDetailPage;
