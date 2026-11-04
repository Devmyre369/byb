
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
    };
  };
};

function getErrorMessage(error: unknown): string {
  const apiError = error as ApiError;

  return (
    apiError.response?.data?.message ||
    apiError.response?.data?.detail ||
    "Unable to load your profile. Please try again."
  );
}

function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const loadProfile = async () => {
      try {
        const response = await api.get<ProfileResponse>(
          "/accounts/me/"
        );

        if (active) {
          setProfile({
            ...response.data.user,
            interests: response.data.user.interests || [],
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

  const initials = profile
    ? `${profile.first_name?.charAt(0) || ""}${profile.last_name?.charAt(0) || ""}`.toUpperCase()
    : "";

  if (loading) {
    return (
      <main className="content profile-view-page">
        <div className="profile-view-loading">
          <div className="profile-loading-spinner" />
          <p>Loading your profile...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="content profile-view-page">
        <div className="profile-view-error">
          <span className="profile-view-error-icon">!</span>
          <h2>Couldn't load your profile</h2>
          <p>{error}</p>

          <button
            type="button"
            className="profile-view-retry"
            onClick={() => window.location.reload()}
          >
            Try again
          </button>
        </div>
      </main>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <main className="content profile-view-page">
      <header className="profile-view-header">
        <div>
          <span className="event-category">
            BEYOND YOUR BUBBLE
          </span>

          <h1>Your profile</h1>

          <p>
            Your identity in the BYB community.
          </p>
        </div>

        <Link
          to="/profile/edit"
          className="profile-view-edit-button"
        >
          <span>✎</span> Edit profile
        </Link>
      </header>

      <section className="profile-view-card">
        <div className="profile-view-cover">
          <span className="profile-view-cover-brand">BYB.</span>
          <span className="profile-view-cover-caption">
            STEP OUTSIDE YOUR BUBBLE.
          </span>
        </div>

        <div className="profile-view-main">
          <div className="profile-view-avatar">
            {profile.profile_picture ? (
              <img
                src={profile.profile_picture}
                alt={`${profile.first_name}'s profile`}
              />
            ) : (
              <span>{initials || "BYB"}</span>
            )}
          </div>

          <div className="profile-view-identity">
            <div className="profile-view-name-row">
              <div>
                <h2>
                  {[profile.first_name, profile.last_name]
                    .filter(Boolean)
                    .join(" ") || "Your Name"}
                </h2>

                <p className="profile-view-username">
                  @{profile.username}
                </p>
              </div>

              <span className="profile-view-account-type">
                {profile.profile_type === "student"
                  ? "Student"
                  : "Professional"}
              </span>
            </div>

            <p className="profile-view-bio">
              {profile.bio || "No bio added yet."}
            </p>
          </div>
        </div>

        <div className="profile-view-divider" />

        <div className="profile-view-details">
          <div className="profile-view-detail">
            <span className="profile-view-detail-icon">⌂</span>
            <div>
              <span>
                {profile.profile_type === "student"
                  ? "COLLEGE / UNIVERSITY"
                  : "ORGANIZATION / COMPANY"}
              </span>
              <strong>{profile.college || "Not added"}</strong>
            </div>
          </div>

          <div className="profile-view-detail">
            <span className="profile-view-detail-icon">▤</span>
            <div>
              <span>
                {profile.profile_type === "student"
                  ? "COURSE / DEPARTMENT"
                  : "DEPARTMENT / ROLE"}
              </span>
              <strong>{profile.course || "Not added"}</strong>
            </div>
          </div>

          <div className="profile-view-detail">
            <span className="profile-view-detail-icon">◷</span>
            <div>
              <span>
                {profile.profile_type === "student"
                  ? "STUDY YEAR"
                  : "EXPERIENCE"}
              </span>
              <strong>{profile.academic_year || "Not added"}</strong>
            </div>
          </div>

          <div className="profile-view-detail">
            <span className="profile-view-detail-icon">⌖</span>
            <div>
              <span>LOCATION</span>
              <strong>{profile.city || "Not added"}</strong>
            </div>
          </div>
        </div>

        <div className="profile-view-divider" />

        <section className="profile-view-interests">
          <div className="profile-view-section-heading">
            <div>
              <span className="event-category">YOUR PERSONALITY</span>
              <h3>Interests & passions</h3>
            </div>

            <span className="profile-view-interest-count">
              {profile.interests.length} selected
            </span>
          </div>

          {profile.interests.length > 0 ? (
            <div className="profile-view-interest-list">
              {profile.interests.map((interest) => (
                <span
                  className="profile-view-interest-chip"
                  key={interest}
                >
                  {interest}
                </span>
              ))}
            </div>
          ) : (
            <p className="profile-view-empty">
              You haven't added any interests yet.
            </p>
          )}
        </section>

        <div className="profile-view-divider" />

        <footer className="profile-view-footer">
          <div>
            <span className="profile-view-footer-label">
              YOUR BYB IDENTITY
            </span>
            <p>Discover people. Explore experiences. Create opportunities.</p>
          </div>

          <Link
            to="/profile/edit"
            className="profile-view-footer-link"
          >
            Update profile ↗
          </Link>
        </footer>
      </section>
    </main>
  );
}

export default ProfilePage;
