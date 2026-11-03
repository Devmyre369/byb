
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/client";

type RegistrationResponse = {
  status: string;
  message: string;
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

function RegisterPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirmation, setPasswordConfirmation] = useState("");

  const [otp, setOtp] = useState("");
  const [otpStep, setOtpStep] = useState(false);

  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const sendOTP = async () => {
    setResending(true);
    setError("");
    setMessage("");

    try {
      const response = await api.post(
        "/accounts/send-otp/",
        { email }
      );

      setMessage(response.data.message);
      return true;
    } catch (err) {
      setError(getErrorMessage(err));
      return false;
    } finally {
      setResending(false);
    }
  };

  const handleRegister = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await api.post<RegistrationResponse>(
        "/accounts/register/",
        {
          username,
          email,
          password,
          password_confirmation: passwordConfirmation,
        }
      );

      setMessage(response.data.message);

      // Registration succeeded. Now request email verification OTP.
      const otpSent = await sendOTP();

      if (otpSent) {
        setOtpStep(true);
      } else {
        setMessage(
          "Your account was created. You can request a verification OTP below."
        );
        setOtpStep(true);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await api.post(
        "/accounts/verify-otp/",
        {
          email,
          otp,
        }
      );

      setMessage(response.data.message);

      // Account verified. Send the user to login.
      navigate("/login", {
        state: {
          email,
          verified: true,
        },
      });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app auth-page">
      <header className="topbar">
        <Link to="/" className="brand">
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

          {!otpStep ? (
            <>
              <h1>Create your account</h1>

              <p className="auth-description">
                Join BYB. Discover events, meet people and
                experience something beyond your bubble.
              </p>

              <form onSubmit={handleRegister}>
                <div className="auth-field">
                  <label htmlFor="username">Username</label>
                  <input
                    id="username"
                    type="text"
                    placeholder="Choose a username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    minLength={3}
                    maxLength={30}
                    autoComplete="username"
                    required
                  />
                </div>

                <div className="auth-field">
                  <label htmlFor="email">Email address</label>
                  <input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoComplete="email"
                    required
                  />
                </div>

                <div className="auth-field">
                  <label htmlFor="password">Password</label>
                  <input
                    id="password"
                    type="password"
                    placeholder="Create a strong password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="new-password"
                    required
                  />
                </div>

                <div className="auth-field">
                  <label htmlFor="password-confirmation">
                    Confirm password
                  </label>
                  <input
                    id="password-confirmation"
                    type="password"
                    placeholder="Enter your password again"
                    value={passwordConfirmation}
                    onChange={(e) =>
                      setPasswordConfirmation(e.target.value)
                    }
                    autoComplete="new-password"
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
                  {loading ? "Creating account..." : "Create account"}
                </button>
              </form>

              <p className="auth-switch">
                Already have an account?{" "}
                <Link to="/login">Log in</Link>
              </p>
            </>
          ) : (
            <>
              <h1>Verify your email</h1>

              <p className="auth-description">
                We've sent a verification code to:
              </p>

              <p className="auth-email">{email}</p>

              <form onSubmit={handleVerifyOTP}>
                <div className="auth-field">
                  <label htmlFor="otp">6-digit verification code</label>

                  <input
                    id="otp"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]{6}"
                    maxLength={6}
                    placeholder="Enter OTP"
                    value={otp}
                    onChange={(e) =>
                      setOtp(e.target.value.replace(/\D/g, ""))
                    }
                    autoComplete="one-time-code"
                    required
                  />
                </div>

                {error && (
                  <div className="auth-message error">
                    {error}
                  </div>
                )}

                {message && (
                  <div className="auth-message success">
                    {message}
                  </div>
                )}

                <button
                  type="submit"
                  className="btn btn-primary auth-submit"
                  disabled={loading || otp.length !== 6}
                >
                  {loading ? "Verifying..." : "Verify email"}
                </button>
              </form>

              <button
                type="button"
                className="resend-otp"
                onClick={sendOTP}
                disabled={resending}
              >
                {resending ? "Sending..." : "Resend verification code"}
              </button>

              <p className="auth-switch">
                Already verified?{" "}
                <Link to="/login">Log in</Link>
              </p>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default RegisterPage;
