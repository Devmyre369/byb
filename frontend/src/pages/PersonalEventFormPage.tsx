
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import {
  createEvent,
  type CreateEventPayload,
} from "../api/events";
import "./PersonalEventFormPage.css";

type Visibility = "private" | "selected" | "public";

type PersonalEventForm = {
  title: string;
  occasion: string;
  description: string;
  starts_at: string;
  ends_at: string;
  location_name: string;
  location_address: string;
  city: string;
  cover_image: string;
  visibility: Visibility;
};

const initialForm: PersonalEventForm = {
  title: "",
  occasion: "",
  description: "",
  starts_at: "",
  ends_at: "",
  location_name: "",
  location_address: "",
  city: "",
  cover_image: "",
  visibility: "private",
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

function PersonalEventFormPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState<PersonalEventForm>(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  function updateField<K extends keyof PersonalEventForm>(
    field: K,
    value: PersonalEventForm[K]
  ) {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));

    setError("");
  }

  function validateForm(): string | null {
    if (!form.title.trim()) {
      return "Please give your event a title.";
    }

    if (form.title.trim().length > 200) {
      return "The event title cannot exceed 200 characters.";
    }

    if (!form.starts_at) {
      return "Please select when this experience happened or will happen.";
    }

    const start = new Date(form.starts_at);

    if (Number.isNaN(start.getTime())) {
      return "Please enter a valid date and time.";
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

    if (form.cover_image.trim()) {
      try {
        const image = new URL(form.cover_image.trim());

        if (!["http:", "https:"].includes(image.protocol)) {
          return "The cover image must use an HTTP or HTTPS URL.";
        }
      } catch {
        return "Please enter a valid cover image URL.";
      }
    }

    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

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
      event_type: "personal",
      category: form.occasion.trim(),
      cover_image: form.cover_image.trim(),
      starts_at: startsAt,
      ends_at: toISODateTime(form.ends_at),
      timezone: getTimezone(),
      location_name: form.location_name.trim(),
      location_address: form.location_address.trim(),
      city: form.city.trim(),
      visibility: form.visibility,
      capacity: null,
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
          ← All event types
        </button>

        <span className="personal-event-eyebrow">
          PERSONAL EXPERIENCE · 01
        </span>

        <h1>Give your moment a place.</h1>

        <p>
          Some moments deserve more than a camera roll.
          Create a space to preserve the people, places and memories
          that matter to you.
        </p>
      </header>

      <form className="personal-event-form" onSubmit={handleSubmit}>
        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">01</span>
            <div>
              <h2>Tell us about the moment</h2>
              <p>Start with the story you want to preserve.</p>
            </div>
          </div>

          <div className="personal-event-fields">
            <label className="personal-event-field full-width">
              <span>What should we call this moment? *</span>
              <input
                type="text"
                value={form.title}
                onChange={(event) =>
                  updateField("title", event.target.value)
                }
                placeholder="e.g. A birthday to remember"
                maxLength={200}
                required
              />
            </label>

            <label className="personal-event-field full-width">
              <span>What is the occasion?</span>
              <select
                value={form.occasion}
                onChange={(event) =>
                  updateField("occasion", event.target.value)
                }
              >
                <option value="">Choose an occasion</option>
                <option value="Birthday">Birthday</option>
                <option value="Family Gathering">Family gathering</option>
                <option value="Anniversary">Anniversary</option>
                <option value="Graduation">Graduation</option>
                <option value="Achievement">Personal achievement</option>
                <option value="Travel">Travel memory</option>
                <option value="Celebration">Celebration</option>
                <option value="Other">Something else</option>
              </select>
            </label>

            <label className="personal-event-field full-width">
              <span>Tell the story</span>
              <textarea
                value={form.description}
                onChange={(event) =>
                  updateField("description", event.target.value)
                }
                placeholder="What made this moment special? Add a little context or a memory..."
                maxLength={5000}
                rows={5}
              />
              <small>
                {form.description.length}/5000 characters
              </small>
            </label>
          </div>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">02</span>
            <div>
              <h2>When did it happen?</h2>
              <p>
                This can be a past memory or an upcoming personal occasion.
              </p>
            </div>
          </div>

          <div className="personal-event-fields two-columns">
            <label className="personal-event-field">
              <span>Date and time *</span>
              <input
                type="datetime-local"
                value={form.starts_at}
                onChange={(event) =>
                  updateField("starts_at", event.target.value)
                }
                required
              />
            </label>

            <label className="personal-event-field">
              <span>End date and time</span>
              <input
                type="datetime-local"
                value={form.ends_at}
                min={form.starts_at || undefined}
                onChange={(event) =>
                  updateField("ends_at", event.target.value)
                }
              />
              <small>Optional</small>
            </label>
          </div>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">03</span>
            <div>
              <h2>Where was it?</h2>
              <p>Give your memory a place.</p>
            </div>
          </div>

          <div className="personal-event-fields two-columns">
            <label className="personal-event-field">
              <span>Place name</span>
              <input
                type="text"
                value={form.location_name}
                onChange={(event) =>
                  updateField("location_name", event.target.value)
                }
                placeholder="e.g. Home, a restaurant"
              />
            </label>

            <label className="personal-event-field">
              <span>City</span>
              <input
                type="text"
                value={form.city}
                onChange={(event) =>
                  updateField("city", event.target.value)
                }
                placeholder="e.g. Lucknow"
              />
            </label>

            <label className="personal-event-field full-width">
              <span>Address or additional location details</span>
              <input
                type="text"
                value={form.location_address}
                onChange={(event) =>
                  updateField("location_address", event.target.value)
                }
                placeholder="Enter an address or useful directions"
              />
            </label>
          </div>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">04</span>
            <div>
              <h2>Choose a cover memory</h2>
              <p>
                Add an image that represents this experience.
              </p>
            </div>
          </div>

          <div className="personal-event-fields">
            <label className="personal-event-field full-width">
              <span>Cover image URL</span>
              <input
                type="url"
                value={form.cover_image}
                onChange={(event) =>
                  updateField("cover_image", event.target.value)
                }
                placeholder="https://example.com/your-memory.jpg"
              />
              <small>
                You can leave this empty and add an image later.
              </small>
            </label>

            {form.cover_image.trim() && (
              <div className="personal-event-image-preview">
                <img
                  src={form.cover_image}
                  alt="Event cover preview"
                  onError={(event) => {
                    event.currentTarget.style.display = "none";
                  }}
                />
              </div>
            )}
          </div>
        </section>

        <section className="personal-event-section">
          <div className="personal-event-section-heading">
            <span className="personal-event-step">05</span>
            <div>
              <h2>Who can see this memory?</h2>
              <p>
                You decide how much of this experience you want to share.
              </p>
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
              <small>Keep this memory private.</small>
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
              <span className="visibility-symbol">◎</span>
              <strong>Selected people</strong>
              <small>Share with a chosen audience.</small>
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
              <small>Make this memory publicly visible.</small>
            </label>
          </div>

          <p className="personal-event-note">
            Selected-audience invitations and photo-contributor permissions
            will be configured separately after event creation.
          </p>
        </section>

        {error && (
          <div className="personal-event-error" role="alert">
            {error}
          </div>
        )}

        <div className="personal-event-submit-area">
          <div>
            <strong>Your moment, your story.</strong>
            <p>
              You can manage the event and its media after creating it.
            </p>
          </div>

          <button
            type="submit"
            className="personal-event-submit"
            disabled={submitting}
          >
            {submitting ? "Creating..." : "Create Personal Event"}
            {!submitting && <span>→</span>}
          </button>
        </div>
      </form>
    </main>
  );
}

export default PersonalEventFormPage;
