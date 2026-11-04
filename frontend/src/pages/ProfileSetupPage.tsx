
import {
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

type ProfileType = "student" | "professional";

type UserProfile = {
  id: string;
  email: string;
  profile_type: ProfileType;
  first_name: string;
  last_name: string;
  username: string;
  bio: string;
  byb_signature: string;
  profile_picture: string | null;
  college: string;
  course: string;
  academic_year: string;
  city: string;
  interests: string[];
  is_profile_complete: boolean;
};

type ProfileResponse = {
  status: string;
  user: UserProfile;
};

type ApiError = {
  response?: {
    data?: {
      message?: string;
      detail?: string;
      [key: string]: unknown;
    };
  };
};

const INTEREST_OPTIONS = [
  "Technology",
  "Artificial Intelligence",
  "Startups",
  "Entrepreneurship",
  "Programming",
  "Design",
  "Music",
  "Photography",
  "Gaming",
  "Sports",
  "Business",
  "Marketing",
  "Content Creation",
  "Movies",
  "Travel",
  "Art",
  "Science",
  "Robotics",
  "Networking",
  "Community",
];

const STUDY_YEARS = [
  "1st Year",
  "2nd Year",
  "3rd Year",
  "4th Year",
  "5th Year",
  "Postgraduate",
  "Other",
];

const EXPERIENCE_LEVELS = [
  "Fresher",
  "Less than 1 year",
  "1–2 years",
  "3–5 years",
  "6–10 years",
  "10+ years",
];

const EMPTY_PROFILE: UserProfile = {
  id: "",
  email: "",
  profile_type: "student",
  first_name: "",
  last_name: "",
  username: "",
  bio: "",
  byb_signature: "",
  profile_picture: null,
  college: "",
  course: "",
  academic_year: "",
  city: "",
  interests: [],
  is_profile_complete: false,
};

function getErrorMessage(error: unknown): string {
  const apiError = error as ApiError;
  const data = apiError.response?.data;

  if (data?.message) return data.message;
  if (data?.detail) return data.detail;

  if (data) {
    const firstError = Object.values(data).flat()[0];

    if (typeof firstError === "string") {
      return firstError;
    }
  }

  return "Something went wrong. Please try again.";
}

function ProfileSetupPage() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState<UserProfile>(EMPTY_PROFILE);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [photoPreview, setPhotoPreview] = useState("");

  useEffect(() => {
    let active = true;

    const loadProfile = async () => {
      try {
        const response = await api.get<ProfileResponse>(
          "/accounts/me/"
        );

        if (active) {
          setProfile({
            ...EMPTY_PROFILE,
            ...response.data.user,
            interests: response.data.user.interests || [],
            byb_signature:
              response.data.user.byb_signature || "",
          });
        }
      } catch (err) {
        if (active) {
          setError(getErrorMessage(err));
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadProfile();

    return () => {
      active = false;
    };
  }, []);

  const updateField = <K extends keyof UserProfile>(
    field: K,
    value: UserProfile[K]
  ) => {
    setProfile((current) => ({
      ...current,
      [field]: value,
    }));

    setSuccess("");
  };

  const handleInterestToggle = (interest: string) => {
    setProfile((current) => {
      const selected = current.interests.includes(interest);

      return {
        ...current,
        interests: selected
          ? current.interests.filter((item) => item !== interest)
          : [...current.interests, interest],
      };
    });

    setSuccess("");
  };

  const handlePhotoUpload = async (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setError("Please select a JPG, PNG or WEBP image.");
      event.target.value = "";
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError("Profile photo must be smaller than 5 MB.");
      event.target.value = "";
      return;
    }

    setUploadingPhoto(true);
    setError("");
    setSuccess("");

    try {
      const formData = new FormData();
      formData.append("profile_picture", file);

      const response = await api.post(
        "/accounts/me/profile-picture/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const uploadedUrl =
        response.data.profile_picture ||
        response.data.user?.profile_picture ||
        response.data.url;

      if (!uploadedUrl) {
        throw new Error(
          "The server did not return the uploaded image URL."
        );
      }

      setProfile((current) => ({
        ...current,
        profile_picture: uploadedUrl,
      }));

      setPhotoPreview("");
      setSuccess("Profile photo uploaded successfully.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setUploadingPhoto(false);
      event.target.value = "";
    }
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        profile_type: profile.profile_type,
        first_name: profile.first_name.trim(),
        last_name: profile.last_name.trim(),
        username: profile.username.trim(),
        bio: profile.bio.trim(),
        byb_signature: profile.byb_signature.trim(),
        college: profile.college.trim(),
        course: profile.course.trim(),
        academic_year: profile.academic_year,
        city: profile.city.trim(),
        interests: profile.interests,
      };

      const response = await api.patch<ProfileResponse>(
        "/accounts/me/",
        payload
      );

      const updatedProfile = response.data.user;

      setProfile({
        ...EMPTY_PROFILE,
        ...updatedProfile,
        interests: updatedProfile.interests || [],
        byb_signature: updatedProfile.byb_signature || "",
      });

      sessionStorage.setItem(
        "byb_user",
        JSON.stringify(updatedProfile)
      );

      if (updatedProfile.is_profile_complete) {
        setSuccess("Your profile has been saved successfully.");
        navigate("/profile", { replace: true });
      } else {
        setSuccess(
          "Your profile has been saved. Complete the required fields to finish setup."
        );
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const selectedCount = profile.interests.length;

  const requiredFields = [
    profile.first_name,
    profile.username,
    profile.college,
    profile.course,
    profile.academic_year,
    profile.city,
  ];

  const completedFields = requiredFields.filter(
    (field) => field.trim().length > 0
  ).length;

  const completionPercentage = Math.round(
    (completedFields / requiredFields.length) * 100
  );

  if (loading) {
    return (
      <main className="content profile-setup-page">
        <div className="profile-loading">
          Loading your profile...
        </div>
      </main>
    );
  }

  return (
    <main className="content profile-setup-page">
      <header className="profile-page-header">
        <span className="event-category">
          BEYOND YOUR BUBBLE
        </span>

        <h1>Build your identity.</h1>

        <p>
          Tell the BYB community who you are, what you do
          and what interests you.
        </p>
      </header>

      <div className="profile-setup-layout">
        <section className="profile-form-card">
          <div className="profile-progress">
            <div className="profile-progress-heading">
              <span>PROFILE COMPLETION</span>
              <strong>{completionPercentage}%</strong>
            </div>

            <div className="profile-progress-track">
              <div
                className="profile-progress-fill"
                style={{ width: `${completionPercentage}%` }}
              />
            </div>
          </div>

          {error && (
            <div className="profile-message error">
              {error}
            </div>
          )}

          {success && (
            <div className="profile-message success">
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <section className="profile-form-section">
              <div className="profile-section-heading">
                <span>01</span>
                <div>
                  <h2>Your identity</h2>
                  <p>How should people recognize you?</p>
                </div>
              </div>

              <div className="profile-photo-section">
                <div className="profile-avatar">
                  {photoPreview || profile.profile_picture ? (
                    <img
                      src={photoPreview || profile.profile_picture || ""}
                      alt="Profile"
                    />
                  ) : (
                    <span>
                      {profile.first_name.charAt(0).toUpperCase() || "?"}
                    </span>
                  )}
                </div>

                <div className="profile-photo-info">
                  <strong>Profile photo</strong>
                  <p>JPG, PNG or WEBP. Maximum 5 MB.</p>

                  <label className="profile-upload-button">
                    {uploadingPhoto ? "Uploading..." : "Upload photo"}

                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      onChange={handlePhotoUpload}
                      disabled={uploadingPhoto}
                    />
                  </label>
                </div>
              </div>

              <div className="profile-field-grid">
                <div className="profile-field">
                  <label htmlFor="first-name">
                    First name *
                  </label>

                  <input
                    id="first-name"
                    value={profile.first_name}
                    onChange={(e) =>
                      updateField("first_name", e.target.value)
                    }
                    placeholder="Your first name"
                    maxLength={150}
                    required
                  />
                </div>

                <div className="profile-field">
                  <label htmlFor="last-name">
                    Last name
                  </label>

                  <input
                    id="last-name"
                    value={profile.last_name}
                    onChange={(e) =>
                      updateField("last_name", e.target.value)
                    }
                    placeholder="Your last name"
                    maxLength={150}
                  />
                </div>

                <div className="profile-field profile-field-full">
                  <label htmlFor="username">
                    Username *
                  </label>

                  <div className="username-input-wrapper">
                    <span>@</span>
                    <input
                      id="username"
                      value={profile.username}
                      onChange={(e) =>
                        updateField("username", e.target.value)
                      }
                      placeholder="yourusername"
                      maxLength={30}
                      minLength={3}
                      required
                    />
                  </div>
                </div>

                <div className="profile-field profile-field-full">
                  <label htmlFor="bio">About you</label>

                  <textarea
                    id="bio"
                    value={profile.bio}
                    onChange={(e) =>
                      updateField("bio", e.target.value)
                    }
                    placeholder="Tell people a little about yourself..."
                    maxLength={500}
                    rows={4}
                  />

                  <span className="profile-character-count">
                    {profile.bio.length}/500
                  </span>
                </div>

                {/* BYB Signature */}
                <div className="profile-field profile-field-full byb-signature-editor">
                  <label htmlFor="byb-signature">
                    BYB Signature
                    <span className="byb-signature-optional">
                      OPTIONAL
                    </span>
                  </label>

                  <p className="byb-signature-description">
                    Define yourself in one word. Make it your identity.
                  </p>

                  <input
                    id="byb-signature"
                    type="text"
                    value={profile.byb_signature}
                    onChange={(e) =>
                      updateField(
                        "byb_signature",
                        e.target.value.replace(/\s/g, "")
                      )
                    }
                    placeholder="e.g. Troubleshooter"
                    maxLength={160}
                    autoComplete="off"
                  />

                  <div className="byb-signature-footer">
                    <span>
                      One word. Your identity. Change it anytime.
                    </span>

                    <strong>
                      {profile.byb_signature.length}/160
                    </strong>
                  </div>
                </div>
              </div>
            </section>

            <section className="profile-form-section">
              <div className="profile-section-heading">
                <span>02</span>
                <div>
                  <h2>What do you do?</h2>
                  <p>Choose the profile that best describes you.</p>
                </div>
              </div>

              <div className="profile-type-options">
                <button
                  type="button"
                  className={`profile-type-option ${
                    profile.profile_type === "student" ? "active" : ""
                  }`}
                  onClick={() =>
                    updateField("profile_type", "student")
                  }
                >
                  <strong>Student</strong>
                  <span>I'm currently studying.</span>
                </button>

                <button
                  type="button"
                  className={`profile-type-option ${
                    profile.profile_type === "professional" ? "active" : ""
                  }`}
                  onClick={() =>
                    updateField("profile_type", "professional")
                  }
                >
                  <strong>Professional</strong>
                  <span>I'm working or self-employed.</span>
                </button>
              </div>

              <div className="profile-field-grid">
                <div className="profile-field profile-field-full">
                  <label htmlFor="institution">
                    {profile.profile_type === "student"
                      ? "College / University *"
                      : "Organization / Company *"}
                  </label>

                  <input
                    id="institution"
                    value={profile.college}
                    onChange={(e) =>
                      updateField("college", e.target.value)
                    }
                    placeholder={
                      profile.profile_type === "student"
                        ? "Enter your college or university"
                        : "Enter your organization"
                    }
                    maxLength={200}
                    required
                  />
                </div>

                <div className="profile-field">
                  <label htmlFor="course">
                    {profile.profile_type === "student"
                      ? "Course / Department *"
                      : "Department / Role *"}
                  </label>

                  <input
                    id="course"
                    value={profile.course}
                    onChange={(e) =>
                      updateField("course", e.target.value)
                    }
                    placeholder={
                      profile.profile_type === "student"
                        ? "e.g. BTech CSE"
                        : "e.g. Software Engineer"
                    }
                    maxLength={150}
                    required
                  />
                </div>

                <div className="profile-field">
                  <label htmlFor="academic-year">
                    {profile.profile_type === "student"
                      ? "Study year *"
                      : "Experience level *"}
                  </label>

                  <select
                    id="academic-year"
                    value={profile.academic_year}
                    onChange={(e) =>
                      updateField("academic_year", e.target.value)
                    }
                    required
                  >
                    <option value="">Select an option</option>

                    {(profile.profile_type === "student"
                      ? STUDY_YEARS
                      : EXPERIENCE_LEVELS
                    ).map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </section>

            <section className="profile-form-section">
              <div className="profile-section-heading">
                <span>03</span>
                <div>
                  <h2>Where are you based?</h2>
                  <p>Help people discover what's happening nearby.</p>
                </div>
              </div>

              <div className="profile-field">
                <label htmlFor="city">City *</label>

                <input
                  id="city"
                  value={profile.city}
                  onChange={(e) =>
                    updateField("city", e.target.value)
                  }
                  placeholder="e.g. Lucknow"
                  maxLength={100}
                  required
                />
              </div>
            </section>

            <section className="profile-form-section">
              <div className="profile-section-heading">
                <span>04</span>
                <div>
                  <h2>What interests you?</h2>
                  <p>
                    Choose interests to help BYB recommend relevant
                    events and experiences.
                  </p>
                </div>
              </div>

              <div className="interest-selection-heading">
                <span>Select your interests</span>
                <strong>{selectedCount}/20 selected</strong>
              </div>

              <div className="interest-chip-grid">
                {INTEREST_OPTIONS.map((interest) => {
                  const selected = profile.interests.includes(interest);

                  return (
                    <button
                      key={interest}
                      type="button"
                      className={`interest-chip ${
                        selected ? "selected" : ""
                      }`}
                      onClick={() => handleInterestToggle(interest)}
                      disabled={!selected && selectedCount >= 20}
                      aria-pressed={selected}
                    >
                      {selected ? "✓ " : "+ "}
                      {interest}
                    </button>
                  );
                })}
              </div>
            </section>

            <div className="profile-form-footer">
              <p>
                Fields marked with * are required to complete
                your profile.
              </p>

              <button
                type="submit"
                className="profile-save-button"
                disabled={saving || uploadingPhoto}
              >
                {saving ? "Saving profile..." : "Save and continue"}
                <span>↗</span>
              </button>
            </div>
          </form>
        </section>

        <aside className="profile-sidebar-card">
          <span className="event-category">YOUR BYB IDENTITY</span>

          <h2>Step outside your bubble.</h2>

          <p>
            Your profile helps people, communities and event
            organizers discover and connect with you.
          </p>

          <div className="profile-sidebar-divider" />

          <div className="profile-sidebar-item">
            <span>01</span>
            <div>
              <strong>Discover people</strong>
              <p>Connect with people who share your interests.</p>
            </div>
          </div>

          <div className="profile-sidebar-item">
            <span>02</span>
            <div>
              <strong>Explore experiences</strong>
              <p>Find events across colleges and communities.</p>
            </div>
          </div>

          <div className="profile-sidebar-item">
            <span>03</span>
            <div>
              <strong>Create opportunities</strong>
              <p>Organize events and bring people together.</p>
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
}

export default ProfileSetupPage;
