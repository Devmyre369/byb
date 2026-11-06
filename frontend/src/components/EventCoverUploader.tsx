
import { useEffect, useRef, useState } from "react";
import { uploadEventCoverImage } from "../api/events";
import "./EventCoverUploader.css";

type EventCoverUploaderProps = {
  value: string;
  onChange: (url: string) => void;
  onUploadingChange?: (uploading: boolean) => void;
};

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const ALLOWED_TYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
];

export default function EventCoverUploader({
  value,
  onChange,
  onUploadingChange,
}: EventCoverUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [preview, setPreview] = useState(value);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setPreview(value);
  }, [value]);

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) return;

    setError("");

    if (!ALLOWED_TYPES.includes(file.type)) {
      setError("Only JPEG, PNG and WebP images are supported.");
      event.target.value = "";
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError("Image size cannot exceed 10 MB.");
      event.target.value = "";
      return;
    }

    if (file.size === 0) {
      setError("The selected image is empty.");
      event.target.value = "";
      return;
    }

    setUploading(true);
    onUploadingChange?.(true);

    try {
      const response = await uploadEventCoverImage(file);

      setPreview(response.cover_image);
      onChange(response.cover_image);
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : "Unable to upload the cover image. Please try again.";

      setError(message);
    } finally {
      setUploading(false);
      onUploadingChange?.(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleRemove = () => {
    setPreview("");
    setError("");
    onChange("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="event-cover-uploader">
      <div className="event-cover-heading">
        <label className="event-cover-label">
          Event Cover Image
        </label>

        <span className="event-cover-optional">
          Optional
        </span>
      </div>

      <p className="event-cover-description">
        Add a cover image to make your event stand out.
        Recommended: a landscape image.
      </p>

      {preview ? (
        <div className="event-cover-preview">
          <img
            src={preview}
            alt="Event cover preview"
            className="event-cover-preview-image"
          />

          {uploading && (
            <div className="event-cover-upload-overlay">
              <span className="event-cover-spinner" />
              <span>Uploading image...</span>
            </div>
          )}

          {!uploading && (
            <div className="event-cover-actions">
              <button
                type="button"
                className="event-cover-change"
                onClick={() => fileInputRef.current?.click()}
              >
                Change image
              </button>

              <button
                type="button"
                className="event-cover-remove"
                onClick={handleRemove}
              >
                Remove
              </button>
            </div>
          )}
        </div>
      ) : (
        <button
          type="button"
          className="event-cover-dropzone"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? (
            <>
              <span className="event-cover-spinner" />
              <span>Uploading image...</span>
            </>
          ) : (
            <>
              <span className="event-cover-upload-icon">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.7"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <rect x="3" y="3" width="18" height="18" rx="3" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <path d="m21 15-5-5L5 21" />
                </svg>
              </span>

              <span className="event-cover-dropzone-title">
                Click to upload a cover image
              </span>

              <span className="event-cover-dropzone-hint">
                JPEG, PNG or WebP · Maximum 10 MB
              </span>
            </>
          )}
        </button>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="event-cover-file-input"
        onChange={handleFileChange}
        disabled={uploading}
      />

      {error && (
        <p className="event-cover-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
