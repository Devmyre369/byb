
import { useState, type FormEvent } from "react";
import {
  Link,
  useLocation,
  useNavigate,
} from "react-router-dom";
import api from "../api/client";

type LoginResponse = {
  status: string;
  message: string;
  access: string;
  refresh: string;
  user: {
    id: string;
    email: string;
    username: string;
  };
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

  return "Unable to log in. Please check your credentials.";
}

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const verified = Boolean(
    (location.state as { verified?: boolean } | null)?.verified
  );

  const verifiedEmail = (
    location.state as { email?: string } | null
  )?.email;

  const [email, setEmail] = useState(verifiedEmail || "");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await api.post<LoginResponse>(
        "/accounts/login/",
        {
          email: email.trim().toLowerCase(),
          password,
        }
      );

      const { access, refresh, user } = response.data;

      // Store tokens for the current browser tab.
      sessionStorage.setItem("byb_access_token", access);
      sessionStorage.setItem("byb_refresh_token", refresh);
      sessionStorage.setItem("byb_user", JSON.stringify(user));

      navigate("/", { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app auth-page">
      <header className="topbar">
        <Link to="/" className="brand" aria-label="BYB home">
          BYB<span className="brand-accent">.</span>
        </Link>

        <Link to="/" className="nav-link">
          Back to Discover
        </Link>
      </header>

      <main className="auth-container">
        <div className="auth-card">
          <span className="event-category">
            BEYOND YOUR BUBBLE
          </span>

          <h1>Welcome back.</h1>

          <p className="auth-description">
            Log in to discover events, connect with people
            and explore experiences beyond your bubble.
          </p>

          {verified && (
            <div className="auth-message success">
              Your email has been verified successfully.
              You can now log in.
            </div>
          )}

          <form onSubmit={handleLogin}>
            <div className="auth-field">
              <label htmlFor="login-email">
                Email address
              </label>

              <input
                id="login-email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div className="auth-field">
              <label htmlFor="login-password">
                Password
              </label>

              <input
                id="login-password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />
            </div>

            {error && (
              <div className="auth-message error">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary auth-submit"
              disabled={loading}
            >
              {loading ? "Logging in..." : "Log in"}
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account?{" "}
            <Link to="/register">Create an account</Link>
          </p>
        </div>
      </main>
    </div>
  );
}

export default LoginPage;
