
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type AuthUser = {
  id: string;
  email: string;
  username: string;
  [key: string]: unknown;
};

type AuthContextType = {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (
    access: string,
    refresh: string,
    user: AuthUser
  ) => void;
  updateUser: (user: AuthUser) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

const AUTH_EXPIRED_EVENT = "byb:auth-expired";

function clearStoredAuth() {
  sessionStorage.removeItem("byb_access_token");
  sessionStorage.removeItem("byb_refresh_token");
  sessionStorage.removeItem("byb_user");
}

function getStoredUser(): AuthUser | null {
  try {
    const storedUser = sessionStorage.getItem("byb_user");

    return storedUser
      ? (JSON.parse(storedUser) as AuthUser)
      : null;
  } catch {
    sessionStorage.removeItem("byb_user");
    return null;
  }
}

function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const accessToken = sessionStorage.getItem("byb_access_token");
    const refreshToken = sessionStorage.getItem("byb_refresh_token");

    if (!accessToken || !refreshToken) {
      clearStoredAuth();
      return null;
    }

    return getStoredUser();
  });

  const login = useCallback(
    (access: string, refresh: string, loggedInUser: AuthUser) => {
      sessionStorage.setItem("byb_access_token", access);
      sessionStorage.setItem("byb_refresh_token", refresh);
      sessionStorage.setItem("byb_user", JSON.stringify(loggedInUser));

      setUser(loggedInUser);
    },
    []
  );

  const updateUser = useCallback((updatedUser: AuthUser) => {
    sessionStorage.setItem("byb_user", JSON.stringify(updatedUser));
    setUser(updatedUser);
  }, []);

  const logout = useCallback(() => {
    clearStoredAuth();
    setUser(null);
  }, []);

  useEffect(() => {
    const handleAuthExpired = () => {
      clearStoredAuth();
      setUser(null);
    };

    window.addEventListener(
      AUTH_EXPIRED_EVENT,
      handleAuthExpired
    );

    return () => {
      window.removeEventListener(
        AUTH_EXPIRED_EVENT,
        handleAuthExpired
      );
    };
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(
        user &&
        sessionStorage.getItem("byb_access_token") &&
        sessionStorage.getItem("byb_refresh_token")
      ),
      login,
      updateUser,
      logout,
    }),
    [user, login, updateUser, logout]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}

export { AuthProvider, useAuth };
