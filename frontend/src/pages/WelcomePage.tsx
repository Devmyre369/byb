
import { useState } from "react";
import { Link } from "react-router-dom";
import "./WelcomePage.css";

function WelcomePage() {
  const [brandLogoError, setBrandLogoError] = useState(false);
  const [heroLogoError, setHeroLogoError] = useState(false);

  return (
    <main className="welcome-page">
      <nav className="welcome-nav">
        <Link to="/welcome" className="welcome-brand">
          {!brandLogoError ? (
            <img
              src="/byb-logo.png"
              alt="BYB"
              onError={() => setBrandLogoError(true)}
            />
          ) : (
            <span>BYB</span>
          )}
        </Link>

        <Link to="/login" className="welcome-nav-login">
          Sign In
        </Link>
      </nav>

      <section className="welcome-hero">
        <div className="welcome-visual">
          <div className="welcome-glow" />

          {!heroLogoError ? (
            <img
              src="/byb-logo.png"
              alt="BYB — Beyond Your Bubble"
              className="welcome-hero-logo"
              onError={() => setHeroLogoError(true)}
            />
          ) : (
            <div className="welcome-logo-fallback">
              <span>BYB</span>
              <small>BEYOND YOUR BUBBLE</small>
            </div>
          )}

          <span className="welcome-orbit orbit-one" />
          <span className="welcome-orbit orbit-two" />
        </div>

        <div className="welcome-copy">
          <span className="welcome-eyebrow">
            YOUR WORLD IS BIGGER THAN YOU THINK
          </span>

          <h1>
            Life happens
            <br />
            <span>Beyond Your Bubble.</span>
          </h1>

          <p>
            Discover experiences. Meet people beyond your
            circle. Explore events, share your stories and
            create memories worth keeping.
          </p>

          <div className="welcome-actions">
            <Link
              to="/register"
              className="welcome-primary-button"
            >
              Get Started
              <span aria-hidden="true">→</span>
            </Link>

            <Link
              to="/login"
              className="welcome-secondary-button"
            >
              I already have an account
            </Link>
          </div>

          <div className="welcome-values">
            <span>DISCOVER</span>
            <i />
            <span>CONNECT</span>
            <i />
            <span>EXPERIENCE</span>
          </div>
        </div>
      </section>

      <footer className="welcome-footer">
        <span>BYB — BEYOND YOUR BUBBLE</span>
        <span>Every experience has a story.</span>
      </footer>
    </main>
  );
}

export default WelcomePage;
