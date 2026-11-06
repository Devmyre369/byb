
import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./LaunchPage.css";

function LaunchPage() {
  const { isAuthenticated } = useAuth();
  const [finished, setFinished] = useState(false);
  const [logoLoaded, setLogoLoaded] = useState(false);
  const [logoError, setLogoError] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setFinished(true);
    }, 1800);

    return () => window.clearTimeout(timer);
  }, []);

  if (finished) {
    return (
      <Navigate
        to={isAuthenticated ? "/discover" : "/welcome"}
        replace
      />
    );
  }

  return (
    <main className="launch-screen">
      <div className="launch-content">
        <div className="launch-logo-wrapper">
          {!logoError ? (
            <img
              src="/byb-logo.png"
              alt="BYB — Beyond Your Bubble"
              className="launch-logo"
              onLoad={() => setLogoLoaded(true)}
              onError={() => setLogoError(true)}
              style={{
                opacity: logoLoaded ? 1 : 0,
              }}
            />
          ) : (
            <div className="launch-logo-fallback">
              BYB
            </div>
          )}
        </div>

        <p className="launch-tagline">
          
        </p>

        <div className="launch-loader">
          <span />
        </div>
      </div>

      <p className="launch-footer">
        DISCOVER. CONNECT. EXPERIENCE.
      </p>
    </main>
  );
}

export default LaunchPage;
