
import { Navigate, Outlet, useLocation } from "react-router-dom";

function ProtectedRoute() {
  const location = useLocation();

  const accessToken = sessionStorage.getItem("byb_access_token");
  const refreshToken = sessionStorage.getItem("byb_refresh_token");

  // No stored authentication tokens: redirect to login.
  if (!accessToken || !refreshToken) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location }}
      />
    );
  }

  return <Outlet />;
}

export default ProtectedRoute;
