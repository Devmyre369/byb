
import axios, {
  type InternalAxiosRequestConfig,
} from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8001/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Separate Axios instance for refreshing tokens.
// This prevents refresh requests from triggering the same interceptor.
const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

type RetryConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

type RefreshResponse = {
  access: string;
  refresh?: string;
};

let refreshPromise: Promise<string> | null = null;

// Attach JWT access token to outgoing requests.
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = sessionStorage.getItem("byb_access_token");

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Refresh expired access tokens after a 401 response.
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as RetryConfig | undefined;

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry
    ) {
      return Promise.reject(error);
    }

    const requestUrl = originalRequest.url || "";

    // Never attempt refresh for authentication endpoints.
    const excludedEndpoints = [
      "/accounts/login/",
      "/accounts/register/",
      "/accounts/send-otp/",
      "/accounts/verify-otp/",
      "/accounts/token/refresh/",
      "/accounts/logout/",
    ];

    if (
      excludedEndpoints.some((endpoint) =>
        requestUrl.includes(endpoint)
      )
    ) {
      return Promise.reject(error);
    }

    const refreshToken = sessionStorage.getItem(
      "byb_refresh_token"
    );

    if (!refreshToken) {
      sessionStorage.clear();
      window.location.assign("/login");
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      // Share one refresh request among concurrent failed requests.
      if (!refreshPromise) {
        refreshPromise = refreshClient
          .post<RefreshResponse>(
            "/accounts/token/refresh/",
            { refresh: refreshToken }
          )
          .then((response) => {
            const newAccessToken = response.data.access;

            sessionStorage.setItem(
              "byb_access_token",
              newAccessToken
            );

            // Django SimpleJWT may rotate the refresh token.
            if (response.data.refresh) {
              sessionStorage.setItem(
                "byb_refresh_token",
                response.data.refresh
              );
            }

            return newAccessToken;
          })
          .finally(() => {
            refreshPromise = null;
          });
      }

      const newAccessToken = await refreshPromise;

      originalRequest.headers.Authorization =
        `Bearer ${newAccessToken}`;

      return api(originalRequest);
    } catch (refreshError) {
      sessionStorage.removeItem("byb_access_token");
      sessionStorage.removeItem("byb_refresh_token");
      sessionStorage.removeItem("byb_user");

      window.location.assign("/login");

      return Promise.reject(refreshError);
    }
  }
);

export default api;
