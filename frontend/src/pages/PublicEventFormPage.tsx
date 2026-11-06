
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import {
  createEvent,
  type CreateEventPayload,
} from "../api/events";
import EventCoverUploader from "../components/EventCoverUploader";
import "./PersonalEventFormPage.css";

type RegistrationMode = "automatic" | "approval";

type PublicEventForm = {
  title: string;
  category: string;
  description: string;
  starts_at: string;
  ends_at: string;
  location_name: string;
  location_address: string;
  city: string;
  cover_image: string;
  capacity: string;
  registration_mode: RegistrationMode;
  registration_opens_at: string;
  registration_closes_at: string;
};

const initialForm: PublicEventForm = {
  title: "",
  category: "",
  description: "",
  starts_at: "",
  ends_at: "",
  location_name: "",
  location_address: "",
  city: "Lucknow",
  cover_image: "",
  capacity: "",
  registration_mode: "automatic",
  registration_opens_at: "",
  registration_closes_at: "",
};

function getTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kolkata";
  } catch {
    return "Asia/Kolkata";
  }
}

function toISODateTime(value: string): string | null {
  if (!value) return null;

  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function getErrorMessage(error: unknown): string {
  const apiError = error as {
    response?: { data?: Record<string, unknown> | string };
    message?: string;
  };

  const data = apiError.response?.data;

  if (typeof data === "string") return data;

  if (data && typeof data === "object") {
    return Object.entries(data)
      .map(([field, value]) => {
        const readableField = field
          .replaceAll("_", " ")
          .replace(/^./, (letter) => letter.toUpperCase());

        const detail = Array.isArray(value)
          ? value.join(" ")
          : typeof value === "string"
            ? value
            : JSON.stringify(value);

        return `${readableField}: ${detail}`;
      })
      .join("\n");
  }

  return apiError.message || "Something went wrong. Please try again.";
}

function PublicEventFormPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState<PublicEventForm>(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [uploadingCover, setUploadingCover] = useState(false);
  const [error, setError] = useState("");

  function updateField<K extends keyof PublicEventForm>(
    field: K,
    value: PublicEventForm[K]
  ) {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));

    setError("");
  }

  function validateForm(): string | null {
    if (!form.title.trim()) {
      return "Please enter a title for your public event.";
    }

    if (form.title.trim().length > 200) {
      return "The event title cannot exceed 200 characters.";
    }

    if (!form.starts_at) {
      return "Please select the event start date and time.";
    }

    const start = new Date(form.starts_at);
    const now = new Date();

    if (Number.isNaN(start.getTime())) {
      return "Please enter a valid start date and time.";
    }

    if (start <= now) {
      return "Public events must be scheduled for a future date and time.";
    }

    if (form.ends_at) {
      const end = new Date(form.ends_at);

      if (Number.isNaN(end.getTime())) {
        return "Please enter a valid end date and time.";
      }

      if (end <= start) {
        return "The end time must be after the start time.";
      }
    }

    if (form.capacity.trim()) {
      const capacity = Number(form.capacity);

      if (!Number.isInteger(capacity) || capacity < 1) {
        return "Attendee capacity must be a positive whole number.";
      }
    }

    if (form.registration_opens_at) {
      const opens = new Date(form.registration_opens_at);

      if (Number.isNaN(opens.getTime())) {
        return "Please enter a valid registration opening date.";
      }

      if (opens >= start) {
        return "Registration must open before the event starts.";
      }
    }

    if (form.registration_closes_at) {
      const closes = new Date(form.registration_closes_at);

      if (Number.isNaN(closes.getTime())) {
        return "Please enter a valid registration closing date.";
      }

      if (closes >= start) {
        return "Registration must close before the event starts.";
      }

      if (
        form.registration_opens_at &&
        closes <= new Date(form.registration_opens_at)
      ) {
        return "Registration must close after it opens.";
      }
    }

    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (uploadingCover) {
      setError("Please wait for the cover image to finish uploading.");
      return;
    }

    const validationError = validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }

    const startsAt = toISODateTime(form.starts_at);

    if (!startsAt) {
      setError("Please enter a valid event start date and time.");
      return;
    }

    const payload: CreateEventPayload = {
      title: form.title.trim(),
      description: form.description.trim(),
      event_type: "public",
      category: form.category.trim(),
      cover_image: form.cover_image.trim(),
      starts_at: startsAt,
      ends_at: toISODateTime(form.ends_at),
      timezone: getTimezone(),
      location_name: form.location_name.trim(),
      location_address: form.location_address.trim(),
      city: form.city.trim(),
      visibility: "public",
      capacity: form.capacity.trim() ? Number(form.capacity) : null,
      registration_enabled: true,
      registration_mode: form.registration_mode,
      registration_opens_at: toISODateTime(form.registration_opens_at),
      registration_closes_at: toISODateTime(form.registration_closes_at),
    };

    setSubmitting(true);
    setError("");

    try {
      const createdEvent = await createEvent(payload);
      navigate(`/events/${createdEvent.id}`);
    } catch (submissionError) {
      setError(getErrorMessage(submissionError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="personal-event-page">
      <header className="personal-event-header">
        <button
          type="button"
          className="personal-event-back"
          onClick={() => navigate("/events/create")}
        >
          ← Back to event types
        </button>

        <span className="personal-event-eyebrow">
          BYB / PUBLIC EVENT
        </span>

        <h1>Bring your event to everyone.</h1>

        <p>
          Publish an event, welcome attendees and build a community around
          something worth experiencing. Manage registrations and event media
          through BYB.
        </p>
      </header>

      <form className="personal-event-form" onSubmit={handleSubmit}>
        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">01</span>
            <div>
              <h2>Tell everyone about your event</h2>
              <p>Start with the details people need to know.</p>
            </div>
          </div>

          <div className="personal-event-fields two-columns">
            <label className="personal-event-field full-width">
              <span>Event title *</span>
              <input
                type="text"
                maxLength={200}
                value={form.title}
                onChange={(e) => updateField("title", e.target.value)}
                placeholder="e.g. Lucknow Tech Summit 2026"
                required
              />
            </label>

            <label className="personal-event-field">
              <span>Category</span>
              <select
                value={form.category}
                onChange={(e) => updateField("category", e.target.value)}
              >
                <option value="">Select a category</option>
                <option value="Technology">Technology</option>
                <option value="Hackathon">Hackathon</option>
                <option value="Workshop">Workshop</option>
                <option value="Conference">Conference</option>
                <option value="Education">Education</option>
                <option value="Cultural">Cultural</option>
                <option value="Festival">Festival</option>
                <option value="Business">Business</option>
                <option value="Sports">Sports</option>
                <option value="Other">Other</option>
              </select>
            </label>

            <label className="personal-event-field">
              <span>Attendee capacity</span>
              <input
                type="number"
                min="1"
                step="1"
                value={form.capacity}
                onChange={(e) => updateField("capacity", e.target.value)}
                placeholder="Unlimited"
              />
              <small>Leave empty for no capacity limit.</small>
            </label>

            <label className="personal-event-field full-width">
              <span>Description</span>
              <textarea
                maxLength={5000}
                value={form.description}
                onChange={(e) => updateField("description", e.target.value)}
                placeholder="Describe the event, its purpose, activities and what attendees can expect..."
              />
            </label>
          </div>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">02</span>
            <div>
              <h2>Event schedule</h2>
              <p>Public events must have a future start date.</p>
            </div>
          </div>

          <div className="personal-event-fields two-columns">
            <label className="personal-event-field">
              <span>Start date and time *</span>
              <input
                type="datetime-local"
                value={form.starts_at}
                min={new Date().toISOString().slice(0, 16)}
                onChange={(e) => updateField("starts_at", e.target.value)}
                required
              />
            </label>

            <label className="personal-event-field">
              <span>End date and time</span>
              <input
                type="datetime-local"
                value={form.ends_at}
                min={form.starts_at || undefined}
                onChange={(e) => updateField("ends_at", e.target.value)}
              />
              <small>Optional.</small>
            </label>
          </div>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">03</span>
            <div>
              <h2>Event venue</h2>
              <p>Help attendees find the event location.</p>
            </div>
          </div>

          <div className="personal-event-fields two-columns">
            <label className="personal-event-field">
              <span>Venue / Organisation</span>
              <input
                type="text"
                value={form.location_name}
                onChange={(e) => updateField("location_name", e.target.value)}
                placeholder="e.g. University Auditorium"
              />
            </label>

            <label className="personal-event-field">
              <span>City</span>
              <input
                type="text"
                value={form.city}
                onChange={(e) => updateField("city", e.target.value)}
                placeholder="e.g. Lucknow"
              />
            </label>

            <label className="personal-event-field full-width">
              <span>Full address</span>
              <input
                type="text"
                value={form.location_address}
                onChange={(e) =>
                  updateField("location_address", e.target.value)
                }
                placeholder="Building, street, area and landmark..."
              />
            </label>
          </div>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">04</span>
            <div>
              <h2>Registration settings</h2>
              <p>Choose how attendees can register for your event.</p>
            </div>
          </div>

          <div className="personal-event-fields">
            <div className="personal-event-visibility">
              <label
                className={`personal-event-visibility-option ${
                  form.registration_mode === "automatic" ? "active" : ""
                }`}
              >
                <input
                  type="radio"
                  name="registration_mode"
                  value="automatic"
                  checked={form.registration_mode === "automatic"}
                  onChange={() =>
                    updateField("registration_mode", "automatic")
                  }
                />
                <span className="visibility-symbol">✓</span>
                <strong>Automatic confirmation</strong>
                <small>
                  Attendees are registered automatically when they join.
                </small>
              </label>

              <label
                className={`personal-event-visibility-option ${
                  form.registration_mode === "approval" ? "active" : ""
                }`}
              >
                <input
                  type="radio"
                  name="registration_mode"
                  value="approval"
                  checked={form.registration_mode === "approval"}
                  onChange={() => updateField("registration_mode", "approval")}
                />
                <span className="visibility-symbol">◷</span>
                <strong>Approval required</strong>
                <small>
                  Organisers review registration requests before confirmation.
                </small>
              </label>
            </div>

            <div className="personal-event-fields two-columns">
              <label className="personal-event-field">
                <span>Registration opens</span>
                <input
                  type="datetime-local"
                  value={form.registration_opens_at}
                  max={form.starts_at || undefined}
                  onChange={(e) =>
                    updateField("registration_opens_at", e.target.value)
                  }
                />
                <small>Leave empty to use the default opening behaviour.</small>
              </label>

              <label className="personal-event-field">
                <span>Registration closes</span>
                <input
                  type="datetime-local"
                  value={form.registration_closes_at}
                  max={form.starts_at || undefined}
                  onChange={(e) =>
                    updateField("registration_closes_at", e.target.value)
                  }
                />
                <small>Must be before the event starts.</small>
              </label>
            </div>
          </div>

          <p className="personal-event-note">
            Paid tickets, payments, refunds and QR check-in are not part of
            the current BYB release.
          </p>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">05</span>
            <div>
              <h2>Event cover</h2>
              <p>Add an image that represents your event.</p>
            </div>
          </div>

          <div className="personal-event-fields">
            <div className="personal-event-field full-width">
              <EventCoverUploader
                value={form.cover_image}
                onChange={(url) => updateField("cover_image", url)}
                onUploadingChange={setUploadingCover}
              />
            </div>
          </div>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">06</span>
            <div>
              <h2>Public visibility</h2>
              <p>Your event will be discoverable by the BYB community.</p>
            </div>
          </div>

          <p className="personal-event-note">
            Public events are published with public visibility. Registration
            and attendee management are handled separately from event creation.
            You can configure co-organisers after creating the event.
          </p>
        </section>

        {error && (
          <div className="personal-event-error" role="alert">
            {error}
          </div>
        )}

        <div className="personal-event-submit-area">
          <div>
            <strong>Make it happen.</strong>
            <p>Your event will be published for the BYB community.</p>
          </div>

          <button
            type="submit"
            className="personal-event-submit"
            disabled={submitting || uploadingCover}
          >
            {uploadingCover
              ? "Uploading cover..."
              : submitting
                ? "Publishing..."
                : "Publish Public Event"}
            {!submitting && !uploadingCover && <span>→</span>}
          </button>
        </div>
      </form>
    </main>
  );
}

export default PublicEventFormPage;
