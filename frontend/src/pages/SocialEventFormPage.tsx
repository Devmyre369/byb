
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import {
  createEvent,
  type CreateEventPayload,
} from "../api/events";
import EventCoverUploader from "../components/EventCoverUploader";
import "./PersonalEventFormPage.css";

type Visibility = "private" | "selected" | "public";

type SocialEventForm = {
  title: string;
  activity: string;
  description: string;
  starts_at: string;
  ends_at: string;
  location_name: string;
  location_address: string;
  city: string;
  cover_image: string;
  capacity: string;
  visibility: Visibility;
};

const initialForm: SocialEventForm = {
  title: "",
  activity: "",
  description: "",
  starts_at: "",
  ends_at: "",
  location_name: "",
  location_address: "",
  city: "Lucknow",
  cover_image: "",
  capacity: "",
  visibility: "selected",
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

function SocialEventFormPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState<SocialEventForm>(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [uploadingCover, setUploadingCover] = useState(false);
  const [error, setError] = useState("");

  function updateField<K extends keyof SocialEventForm>(
    field: K,
    value: SocialEventForm[K]
  ) {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));

    setError("");
  }

  function validateForm(): string | null {
    if (!form.title.trim()) {
      return "Please give your social event a title.";
    }

    if (form.title.trim().length > 200) {
      return "The event title cannot exceed 200 characters.";
    }

    if (!form.starts_at) {
      return "Please select the date and time of your event.";
    }

    const start = new Date(form.starts_at);

    if (Number.isNaN(start.getTime())) {
      return "Please enter a valid start date and time.";
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
        return "Participant limit must be a positive whole number.";
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
      setError("Please enter a valid start date and time.");
      return;
    }

    const payload: CreateEventPayload = {
      title: form.title.trim(),
      description: form.description.trim(),
      event_type: "social",
      category: form.activity.trim(),
      cover_image: form.cover_image.trim(),
      starts_at: startsAt,
      ends_at: toISODateTime(form.ends_at),
      timezone: getTimezone(),
      location_name: form.location_name.trim(),
      location_address: form.location_address.trim(),
      city: form.city.trim(),
      visibility: form.visibility,
      capacity: form.capacity.trim() ? Number(form.capacity) : null,
      registration_enabled: false,
      registration_mode: "automatic",
      registration_opens_at: null,
      registration_closes_at: null,
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
          BYB / SOCIAL EXPERIENCE
        </span>

        <h1>Bring people together.</h1>

        <p>
          Create a plan, bring your circle together, and turn shared
          experiences into memories. Friends and communities can participate
          through invitations and participation requests.
        </p>
      </header>

      <form className="personal-event-form" onSubmit={handleSubmit}>
        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">01</span>
            <div>
              <h2>What's the plan?</h2>
              <p>Give your gathering a name and tell people what it's about.</p>
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
                placeholder="e.g. Sunday Football with Friends"
                required
              />
            </label>

            <label className="personal-event-field">
              <span>Activity / Category</span>
              <select
                value={form.activity}
                onChange={(e) => updateField("activity", e.target.value)}
              >
                <option value="">Select an activity</option>
                <option value="Hangout">Hangout</option>
                <option value="Food & Dining">Food & Dining</option>
                <option value="Sports">Sports</option>
                <option value="Gaming">Gaming</option>
                <option value="Travel">Travel</option>
                <option value="Outdoor">Outdoor</option>
                <option value="Celebration">Celebration</option>
                <option value="Community">Community</option>
                <option value="Other">Other</option>
              </select>
            </label>

            <label className="personal-event-field">
              <span>Participant limit</span>
              <input
                type="number"
                min="1"
                step="1"
                value={form.capacity}
                onChange={(e) => updateField("capacity", e.target.value)}
                placeholder="No limit"
              />
              <small>Leave empty if everyone can join.</small>
            </label>

            <label className="personal-event-field full-width">
              <span>Description</span>
              <textarea
                value={form.description}
                onChange={(e) => updateField("description", e.target.value)}
                maxLength={5000}
                placeholder="Share the plan, what people can expect, and anything they should know..."
              />
            </label>
          </div>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">02</span>
            <div>
              <h2>When is it happening?</h2>
              <p>Social experiences can be planned or added after they happen.</p>
            </div>
          </div>

          <div className="personal-event-fields two-columns">
            <label className="personal-event-field">
              <span>Start date and time *</span>
              <input
                type="datetime-local"
                value={form.starts_at}
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
              <h2>Where will everyone meet?</h2>
              <p>Add a location so participants know where to go.</p>
            </div>
          </div>

          <div className="personal-event-fields two-columns">
            <label className="personal-event-field">
              <span>Venue / Place</span>
              <input
                type="text"
                value={form.location_name}
                onChange={(e) => updateField("location_name", e.target.value)}
                placeholder="e.g. Gomti Riverfront"
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
                placeholder="Street, area, landmark..."
              />
            </label>
          </div>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">04</span>
            <div>
              <h2>Add a cover image</h2>
              <p>Give your gathering a visual identity.</p>
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
            <span className="personal-event-step">05</span>
            <div>
              <h2>Who can see this gathering?</h2>
              <p>Choose the audience for your social event.</p>
            </div>
          </div>

          <div className="personal-event-visibility">
            <label
              className={`personal-event-visibility-option ${
                form.visibility === "private" ? "active" : ""
              }`}
            >
              <input
                type="radio"
                name="visibility"
                value="private"
                checked={form.visibility === "private"}
                onChange={() => updateField("visibility", "private")}
              />
              <span className="visibility-symbol">◉</span>
              <strong>Only me</strong>
              <small>Keep this gathering private.</small>
            </label>

            <label
              className={`personal-event-visibility-option ${
                form.visibility === "selected" ? "active" : ""
              }`}
            >
              <input
                type="radio"
                name="visibility"
                value="selected"
                checked={form.visibility === "selected"}
                onChange={() => updateField("visibility", "selected")}
              />
              <span className="visibility-symbol">◍</span>
              <strong>Selected people</strong>
              <small>Share with your chosen circle.</small>
            </label>

            <label
              className={`personal-event-visibility-option ${
                form.visibility === "public" ? "active" : ""
              }`}
            >
              <input
                type="radio"
                name="visibility"
                value="public"
                checked={form.visibility === "public"}
                onChange={() => updateField("visibility", "public")}
              />
              <span className="visibility-symbol">◇</span>
              <strong>Everyone</strong>
              <small>Let the wider BYB community discover it.</small>
            </label>
          </div>

          <p className="personal-event-note">
            Invitations, participation requests, and participant management
            will be handled separately after the event is created. A
            participant limit does not automatically send invitations.
          </p>
        </section>

        {error && (
          <div className="personal-event-error" role="alert">
            {error}
          </div>
        )}

        <div className="personal-event-submit-area">
          <div>
            <strong>Good times are better together.</strong>
            <p>You can manage participants and event media after creation.</p>
          </div>

          <button
            type="submit"
            className="personal-event-submit"
            disabled={submitting || uploadingCover}
          >
            {uploadingCover
              ? "Uploading cover..."
              : submitting
                ? "Creating..."
                : "Create Social Event"}
            {!submitting && !uploadingCover && <span>→</span>}
          </button>
        </div>
      </form>
    </main>
  );
}

export default SocialEventFormPage;
