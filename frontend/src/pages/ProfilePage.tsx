import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";

type UserProfile = {
  id: string;
  email: string;
  profile_type: "student" | "professional";
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
          setProfile(response.data.user);
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

  if (loading) {
    return (
      <main className="content profile-setup-page">
        <div className="profile-loading">Loading your profile...</div>
      </main>
    );
  }

  if (error || !profile) {
    return (
      <main className="content profile-setup-page">
        <div className="profile-message error">
          {error || "Your profile could not be loaded."}
        </div>
        <Link className="btn btn-secondary" to="/profile/edit">
          Edit profile
        </Link>
      </main>
    );
  }

  const displayName =
    `${profile.first_name} ${profile.last_name}`.trim() ||
    profile.username ||
    profile.email;

  return (
    <main className="content profile-setup-page">
      <header className="profile-page-header">
        <span className="event-category">BEYOND YOUR BUBBLE</span>
        <h1>{displayName}</h1>
        <p>Your profile and the details you share with the BYB community.</p>
        <Link className="btn btn-primary" to="/profile/edit">
          Edit profile
        </Link>
      </header>

      <section className="profile-form-card">
        <div className="profile-photo-section">
          <div className="profile-avatar">
            {profile.profile_picture ? (
              <img src={profile.profile_picture} alt={`${displayName}'s profile`} />
            ) : (
              <span>{displayName.charAt(0).toUpperCase() || "?"}</span>
            )}
          </div>
          <div className="profile-photo-info">
            <strong>{displayName}</strong>
            <p>@{profile.username}</p>
            <p>{profile.email}</p>
            {profile.byb_signature && (
              <p>{profile.byb_signature}</p>
            )}
          </div>
        </div>

        <section className="profile-form-section">
          <div className="profile-section-heading">
            <span>01</span>
            <div>
              <h2>About you</h2>
              <p>A little about who you are.</p>
            </div>
          </div>
          <p>{profile.bio || "Add a short bio to tell people about yourself."}</p>
        </section>

        <section className="profile-form-section">
          <div className="profile-section-heading">
            <span>02</span>
            <div>
              <h2>
                {profile.profile_type === "student"
                  ? "Your studies"
                  : "Your work"}
              </h2>
              <p>
                {profile.profile_type === "student"
                  ? "Your education and current study year."
                  : "Your organization and experience."}
              </p>
            </div>
          </div>
          <div className="profile-field-grid">
            <div className="profile-field">
              <strong>
                {profile.profile_type === "student"
                  ? "College / University"
                  : "Organization / Company"}
              </strong>
              <p>{profile.college || "Not added yet"}</p>
            </div>
            <div className="profile-field">
              <strong>
                {profile.profile_type === "student"
                  ? "Course / Department"
                  : "Department / Role"}
              </strong>
              <p>{profile.course || "Not added yet"}</p>
            </div>
            <div className="profile-field">
              <strong>
                {profile.profile_type === "student"
                  ? "Study year"
                  : "Experience"}
              </strong>
              <p>{profile.academic_year || "Not added yet"}</p>
            </div>
            <div className="profile-field">
              <strong>City</strong>
              <p>{profile.city || "Not added yet"}</p>
            </div>
          </div>
        </section>

        <section className="profile-form-section">
          <div className="profile-section-heading">
            <span>03</span>
            <div>
              <h2>Interests</h2>
              <p>Topics and experiences you enjoy.</p>
            </div>
          </div>
          {profile.interests.length ? (
            <div className="interest-chip-grid">
              {profile.interests.map((interest) => (
                <span className="interest-chip selected" key={interest}>
                  {interest}
                </span>
              ))}
            </div>
          ) : (
            <p>No interests added yet.</p>
          )}
        </section>
      </section>
    </main>
  );
}

export default ProfilePage;
