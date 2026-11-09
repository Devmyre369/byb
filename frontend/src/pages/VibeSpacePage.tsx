
import {
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";
import { Link } from "react-router-dom";

import {
  getMoments,
  getMyMoments,
  type Moment,
  type MyMoment,
} from "../api/moments";

import {
  getUploadableEvents,
  uploadEventMoment,
  type EventItem,
} from "../api/events";

import "./HomePage.css";
import "./VibeSpacePage.css";

type VibeTab = "explore" | "create" | "mine";

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

function getEventLocation(event: {
  location_name: string;
  city: string;
}): string {
  return (
    [event.location_name, event.city]
      .filter(Boolean)
      .join(", ") || "Location not specified"
  );
}

function getModerationLabel(status: MyMoment["moderation_status"]) {
  const labels = {
    pending: "Pending review",
    approved: "Approved",
    rejected: "Rejected",
    removed: "Removed",
  };

  return labels[status];
}

function VibeSpacePage() {
  const [activeTab, setActiveTab] =
    useState<VibeTab>("explore");

  // Explore state
  const [moments, setMoments] = useState<Moment[]>([]);
  const [exploreLoading, setExploreLoading] = useState(true);
  const [exploreError, setExploreError] = useState("");
  const [explorePage, setExplorePage] = useState(1);
  const [exploreHasMore, setExploreHasMore] = useState(false);
  const [exploreLoadingMore, setExploreLoadingMore] =
    useState(false);

  // Create Vibe state
  const [uploadableEvents, setUploadableEvents] =
    useState<EventItem[]>([]);
  const [eventsLoading, setEventsLoading] = useState(false);
  const [eventsError, setEventsError] = useState("");

  const [selectedEventId, setSelectedEventId] = useState("");
  const [selectedImage, setSelectedImage] = useState<File | null>(
    null
  );
  const [imagePreview, setImagePreview] = useState("");
  const [caption, setCaption] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  // My Vibes state
  const [myMoments, setMyMoments] = useState<MyMoment[]>([]);
  const [myMomentsLoading, setMyMomentsLoading] = useState(false);
  const [myMomentsError, setMyMomentsError] = useState("");
  const [myMomentsPage, setMyMomentsPage] = useState(1);
  const [myMomentsHasMore, setMyMomentsHasMore] = useState(false);
  const [myMomentsLoadingMore, setMyMomentsLoadingMore] =
    useState(false);

  async function loadExplore(pageNumber = 1) {
    try {
      if (pageNumber === 1) {
        setExploreLoading(true);
      } else {
        setExploreLoadingMore(true);
      }

      setExploreError("");

      const response = await getMoments(pageNumber, 20);

      setMoments((previous) =>
        pageNumber === 1
          ? response.results
          : [...previous, ...response.results]
      );

      setExplorePage(pageNumber);
      setExploreHasMore(Boolean(response.next));
    } catch (error) {
      console.error("Failed to load VibeSpace moments:", error);

      setExploreError(
        "We couldn't load community moments. Please try again."
      );
    } finally {
      setExploreLoading(false);
      setExploreLoadingMore(false);
    }
  }

  async function loadUploadableEvents() {
    try {
      setEventsLoading(true);
      setEventsError("");

      const response = await getUploadableEvents(1, 100);

      setUploadableEvents(response.results);

      if (response.results.length === 0) {
        setSelectedEventId("");
      }
    } catch (error) {
      console.error("Failed to load uploadable events:", error);

      setEventsError(
        "We couldn't load your eligible events. Please try again."
      );
    } finally {
      setEventsLoading(false);
    }
  }

  async function loadMyMoments(pageNumber = 1) {
    try {
      if (pageNumber === 1) {
        setMyMomentsLoading(true);
      } else {
        setMyMomentsLoadingMore(true);
      }

      setMyMomentsError("");

      const response = await getMyMoments(pageNumber, 20);

      setMyMoments((previous) =>
        pageNumber === 1
          ? response.results
          : [...previous, ...response.results]
      );

      setMyMomentsPage(pageNumber);
      setMyMomentsHasMore(Boolean(response.next));
    } catch (error) {
      console.error("Failed to load personal moments:", error);

      setMyMomentsError(
        "We couldn't load your Vibes. Please try again."
      );
    } finally {
      setMyMomentsLoading(false);
      setMyMomentsLoadingMore(false);
    }
  }

  useEffect(() => {
    if (activeTab === "explore") {
      void loadExplore(1);
    }

    if (activeTab === "create") {
      void loadUploadableEvents();
    }

    if (activeTab === "mine") {
      void loadMyMoments(1);
    }
  }, [activeTab]);

  useEffect(() => {
    if (!selectedImage) {
      setImagePreview("");
      return;
    }

    const previewUrl = URL.createObjectURL(selectedImage);

    setImagePreview(previewUrl);

    return () => {
      URL.revokeObjectURL(previewUrl);
    };
  }, [selectedImage]);

  function handleImageChange(
    event: ChangeEvent<HTMLInputElement>
  ) {
    const image = event.target.files?.[0] || null;

    setUploadError("");
    setUploadSuccess("");

    if (!image) {
      setSelectedImage(null);
      return;
    }

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(image.type)) {
      setUploadError(
        "Please select a JPEG, PNG or WebP image."
      );

      event.target.value = "";
      setSelectedImage(null);
      return;
    }

    if (image.size > 10 * 1024 * 1024) {
      setUploadError("Image size cannot exceed 10 MB.");

      event.target.value = "";
      setSelectedImage(null);
      return;
    }

    setSelectedImage(image);
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setUploadError("");
    setUploadSuccess("");

    if (!selectedEventId) {
      setUploadError("Please select an event.");
      return;
    }

    if (!selectedImage) {
      setUploadError("Please select an image to upload.");
      return;
    }

    if (caption.trim().length > 500) {
      setUploadError("Caption cannot exceed 500 characters.");
      return;
    }

    try {
      setUploading(true);

      await uploadEventMoment(
        selectedEventId,
        selectedImage,
        caption.trim()
      );

      setUploadSuccess(
        "Your Vibe has been submitted and is awaiting moderation. It will appear in the community feed after approval."
      );

      setSelectedImage(null);
      setCaption("");

      const imageInput = document.getElementById(
        "vibespace-image"
      ) as HTMLInputElement | null;

      if (imageInput) {
        imageInput.value = "";
      }

    } catch (error: unknown) {
      console.error("Failed to upload Vibe:", error);

      setUploadError(
        "Your image could not be uploaded. Please check your access to this event and try again."
      );
    } finally {
      setUploading(false);
    }
  }

  function renderMomentCard(moment: Moment) {
    const uploaderName = getUploaderName(moment);

    return (
      <article className="moment-card" key={moment.id}>
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
                {uploaderName.charAt(0).toUpperCase()}
              </span>
            )}

            <div className="moment-uploader-info">
              <strong>{uploaderName}</strong>
              <span>{formatMomentTime(moment.created_at)}</span>
            </div>
          </div>

          <span className="moment-type-label">VIBE</span>
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
            <p className="moment-caption">{moment.caption}</p>
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
              {getEventLocation(moment.event)}
            </span>
          </Link>
        </div>
      </article>
    );
  }

  return (
    <main className="content vibespace-page">
      <section className="vibespace-header">
        <div>
          <span className="event-category">
            BEYOND YOUR BUBBLE
          </span>

          <h1>VibeSpace.</h1>

          <p>
            Every event has a story. Discover experiences,
            share your moments and bring the BYB community
            closer together.
          </p>
        </div>

        <Link to="/discover" className="home-discover-link">
          Explore events <span aria-hidden="true">→</span>
        </Link>
      </section>

      <nav
        className="vibespace-tabs"
        aria-label="VibeSpace sections"
      >
        <button
          type="button"
          className={
            activeTab === "explore" ? "active" : ""
          }
          onClick={() => setActiveTab("explore")}
        >
          Explore
        </button>

        <button
          type="button"
          className={
            activeTab === "create" ? "active" : ""
          }
          onClick={() => setActiveTab("create")}
        >
          Create a Vibe
        </button>

        <button
          type="button"
          className={
            activeTab === "mine" ? "active" : ""
          }
          onClick={() => setActiveTab("mine")}
        >
          My Vibes
        </button>
      </nav>

      {/* EXPLORE */}
      {activeTab === "explore" && (
        <section className="vibespace-section">
          <div className="section-heading">
            <div>
              <span className="section-eyebrow">
                THE COMMUNITY
              </span>

              <h2>Explore Vibes</h2>

              <p className="section-subtitle">
                Real moments captured at real-world events.
              </p>
            </div>

            {!exploreLoading && !exploreError && (
              <span className="event-count">
                {moments.length}{" "}
                {moments.length === 1 ? "moment" : "moments"}
              </span>
            )}
          </div>

          {exploreLoading ? (
            <div className="profile-loading">
              Loading community moments...
            </div>
          ) : exploreError ? (
            <div className="empty-state">
              <h3>Unable to load Vibes</h3>
              <p>{exploreError}</p>

              <button
                type="button"
                className="reset-filters-button"
                onClick={() => void loadExplore(1)}
              >
                Try again
              </button>
            </div>
          ) : moments.length > 0 ? (
            <>
              <div className="moments-grid">
                {moments.map(renderMomentCard)}
              </div>

              {exploreHasMore && (
                <div className="load-more-container">
                  <button
                    type="button"
                    className="event-action"
                    disabled={exploreLoadingMore}
                    onClick={() =>
                      void loadExplore(explorePage + 1)
                    }
                  >
                    {exploreLoadingMore
                      ? "Loading..."
                      : "Load more Vibes"}
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state home-empty-state">
              <span className="empty-state-icon">✧</span>

              <h3>The community story starts here.</h3>

              <p>
                No approved moments are available yet.
                Be among the first to share an experience
                from an event you attend.
              </p>

              <button
                type="button"
                className="reset-filters-button"
                onClick={() => setActiveTab("create")}
              >
                Create your first Vibe
              </button>
            </div>
          )}
        </section>
      )}

      {/* CREATE A VIBE */}
      {activeTab === "create" && (
        <section className="vibespace-section">
          <div className="section-heading">
            <div>
              <span className="section-eyebrow">
                SHARE YOUR EXPERIENCE
              </span>

              <h2>Create a Vibe</h2>

              <p className="section-subtitle">
                Capture a moment and connect it to the event
                where it happened.
              </p>
            </div>
          </div>

          {eventsLoading ? (
            <div className="profile-loading">
              Loading your eligible events...
            </div>
          ) : eventsError ? (
            <div className="empty-state">
              <h3>Unable to load events</h3>
              <p>{eventsError}</p>

              <button
                type="button"
                className="reset-filters-button"
                onClick={() => void loadUploadableEvents()}
              >
                Try again
              </button>
            </div>
          ) : uploadableEvents.length === 0 ? (
            <div className="empty-state">
              <span className="empty-state-icon">✧</span>

              <h3>No eligible events yet.</h3>

              <p>
                You can share a Vibe when you create an event,
                become an authorised contributor to a personal
                event, join a social event, or confirm your
                registration for a public event.
              </p>

              <Link
                to="/discover"
                className="reset-filters-button"
              >
                Discover events
              </Link>
            </div>
          ) : (
            <form
              className="vibespace-create-form"
              onSubmit={handleUpload}
            >
              <div className="vibespace-form-group">
                <label htmlFor="vibespace-event">
                  Select event
                </label>

                <select
                  id="vibespace-event"
                  value={selectedEventId}
                  onChange={(event) => {
                    setSelectedEventId(event.target.value);
                    setUploadError("");
                    setUploadSuccess("");
                  }}
                  required
                >
                  <option value="">
                    Choose an event...
                  </option>

                  {uploadableEvents.map((event) => (
                    <option key={event.id} value={event.id}>
                      {event.title}
                      {event.city ? ` · ${event.city}` : ""}
                    </option>
                  ))}
                </select>
              </div>

              <div className="vibespace-form-group">
                <label htmlFor="vibespace-image">
                  Upload your moment
                </label>

                <div className="vibespace-upload-area">
                  {imagePreview ? (
                    <div className="vibespace-image-preview">
                      <img
                        src={imagePreview}
                        alt="Selected Vibe preview"
                      />

                      <button
                        type="button"
                        className="vibespace-remove-image"
                        onClick={() => {
                          setSelectedImage(null);

                          const input =
                            document.getElementById(
                              "vibespace-image"
                            ) as HTMLInputElement | null;

                          if (input) {
                            input.value = "";
                          }
                        }}
                      >
                        Remove image
                      </button>
                    </div>
                  ) : (
                    <label
                      htmlFor="vibespace-image"
                      className="vibespace-upload-placeholder"
                    >
                      <span className="vibespace-upload-icon">
                        +
                      </span>

                      <strong>Choose a photo</strong>

                      <span>
                        JPEG, PNG or WebP · Maximum 10 MB
                      </span>
                    </label>
                  )}

                  <input
                    id="vibespace-image"
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleImageChange}
                    hidden
                  />
                </div>
              </div>

              <div className="vibespace-form-group">
                <div className="vibespace-caption-heading">
                  <label htmlFor="vibespace-caption">
                    Add a caption
                  </label>

                  <span>{caption.length}/500</span>
                </div>

                <textarea
                  id="vibespace-caption"
                  value={caption}
                  onChange={(event) => {
                    setCaption(event.target.value);
                    setUploadError("");
                    setUploadSuccess("");
                  }}
                  placeholder="Tell the story behind this moment..."
                  rows={5}
                  maxLength={500}
                />
              </div>

              {uploadError && (
                <div
                  className="vibespace-message vibespace-error"
                  role="alert"
                >
                  {uploadError}
                </div>
              )}

              {uploadSuccess && (
                <div
                  className="vibespace-message vibespace-success"
                  role="status"
                >
                  {uploadSuccess}
                </div>
              )}

              <div className="vibespace-upload-footer">
                <p>
                  Your image will be reviewed before it appears
                  in the public community feed.
                </p>

                <button
                  type="submit"
                  className="event-action"
                  disabled={
                    uploading ||
                    !selectedEventId ||
                    !selectedImage
                  }
                >
                  {uploading ? "Uploading..." : "Share Vibe"}
                </button>
              </div>
            </form>
          )}
        </section>
      )}

      {/* MY VIBES */}
      {activeTab === "mine" && (
        <section className="vibespace-section">
          <div className="section-heading">
            <div>
              <span className="section-eyebrow">
                YOUR CONTRIBUTIONS
              </span>

              <h2>My Vibes</h2>

              <p className="section-subtitle">
                Your event moments and their moderation status.
              </p>
            </div>

            {!myMomentsLoading && !myMomentsError && (
              <span className="event-count">
                {myMoments.length}{" "}
                {myMoments.length === 1 ? "Vibe" : "Vibes"}
              </span>
            )}
          </div>

          {myMomentsLoading ? (
            <div className="profile-loading">
              Loading your Vibes...
            </div>
          ) : myMomentsError ? (
            <div className="empty-state">
              <h3>Unable to load your Vibes</h3>
              <p>{myMomentsError}</p>

              <button
                type="button"
                className="reset-filters-button"
                onClick={() => void loadMyMoments(1)}
              >
                Try again
              </button>
            </div>
          ) : myMoments.length > 0 ? (
            <>
              <div className="moments-grid">
                {myMoments.map((moment) => (
                  <article
                    className="moment-card my-vibe-card"
                    key={moment.id}
                  >
                    <div className="my-vibe-status-row">
                      <span
                        className={`my-vibe-status status-${moment.moderation_status}`}
                      >
                        {getModerationLabel(
                          moment.moderation_status
                        )}
                      </span>

                      <span className="my-vibe-date">
                        {formatMomentTime(moment.created_at)}
                      </span>
                    </div>

                    <Link
                      to={`/events/${moment.event.id}`}
                      className="moment-image-link"
                    >
                      <img
                        className="moment-image"
                        src={moment.cloudinary_url}
                        alt={
                          moment.caption ||
                          `Your moment from ${moment.event.title}`
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
                          {getEventLocation(moment.event)}
                        </span>
                      </Link>
                    </div>
                  </article>
                ))}
              </div>

              {myMomentsHasMore && (
                <div className="load-more-container">
                  <button
                    type="button"
                    className="event-action"
                    disabled={myMomentsLoadingMore}
                    onClick={() =>
                      void loadMyMoments(myMomentsPage + 1)
                    }
                  >
                    {myMomentsLoadingMore
                      ? "Loading..."
                      : "Load more"}
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state home-empty-state">
              <span className="empty-state-icon">✧</span>

              <h3>Your Vibe story begins here.</h3>

              <p>
                You haven't shared any event moments yet.
                Upload your first photo and start building
                your collection of real-world experiences.
              </p>

              <button
                type="button"
                className="reset-filters-button"
                onClick={() => setActiveTab("create")}
              >
                Create a Vibe
              </button>
            </div>
          )}
        </section>
      )}
    </main>
  );
}

export default VibeSpacePage;
