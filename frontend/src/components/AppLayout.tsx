
import { useState } from "react";
import {
  NavLink,
  Outlet,
  Link,
  useNavigate,
} from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./AppLayout.css";

const navigation = [
  { label: "Discover", path: "/discover", icon: "⌕" },
  { label: "Hubs", path: "/hubs", icon: "◈" },
  { label: "Events", path: "/events", icon: "▦" },
  { label: "Media", path: "/media", icon: "▣" },
  { label: "Saved", path: "/saved", icon: "♡" },
];

function AppLayout() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const profilePicture =
    typeof user?.profile_picture === "string"
      ? user.profile_picture
      : "";

  const toggleSidebar = () => {
    setIsCollapsed((previous) => !previous);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((previous) => !previous);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const handleLogout = () => {
    logout();
    closeMobileMenu();
    navigate("/login", { replace: true });
  };

  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const query = searchQuery.trim();

    if (query) {
      navigate(`/discover?q=${encodeURIComponent(query)}`);
    }
  };

  const ProfileAvatar = ({ className = "" }: { className?: string }) => (
    <span className={`profile-nav-avatar ${className}`}>
      {profilePicture ? (
        <img
          src={profilePicture}
          alt="Your profile"
          onError={(event) => {
            event.currentTarget.style.display = "none";
          }}
        />
      ) : (
        <span aria-hidden="true">◎</span>
      )}
    </span>
  );

  return (
    <div
      className={`app-layout ${
        isCollapsed ? "sidebar-collapsed" : ""
      } ${isMobileMenuOpen ? "mobile-sidebar-open" : ""}`}
    >
      {/* Desktop and Tablet Top Bar */}
      <header className="app-topbar">
        <div className="topbar-left">
          <button
            type="button"
            className="topbar-sidebar-toggle"
            onClick={toggleSidebar}
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            ☰
          </button>
        </div>

        <Link to="/" className="topbar-brand">
          BYB<span>.</span>
        </Link>

        <div className="topbar-right">
          <form className="topbar-search" onSubmit={handleSearch}>
            <span className="topbar-search-icon" aria-hidden="true">⌕</span>
            <input
              type="search"
              placeholder="Search BYB..."
              aria-label="Search BYB"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
            />
          </form>

          <button
            type="button"
            className="topbar-notifications"
            aria-label="Notifications"
            title="Notifications"
          >
            ♧
            <span className="notification-indicator" />
          </button>
        </div>
      </header>

      {/* Mobile Top Bar */}
      <header className="mobile-topbar">
        <button
          type="button"
          className="mobile-menu-toggle"
          onClick={toggleMobileMenu}
          aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
          aria-expanded={isMobileMenuOpen}
        >
          {isMobileMenuOpen ? "×" : "☰"}
        </button>

        <Link
          to="/"
          className="mobile-brand"
          onClick={closeMobileMenu}
        >
          BYB<span>.</span>
        </Link>

        <div className="mobile-topbar-actions">
          <button
            type="button"
            className="mobile-notifications"
            aria-label="Notifications"
          >
            ♧
          </button>
        </div>
      </header>

      {/* Mobile Backdrop */}
      <button
        type="button"
        className="mobile-sidebar-backdrop"
        onClick={closeMobileMenu}
        aria-label="Close navigation menu"
        tabIndex={isMobileMenuOpen ? 0 : -1}
      />

      {/* Sidebar */}
      <aside className="app-sidebar">
        <div className="sidebar-header">
          <button
            type="button"
            className="mobile-drawer-close"
            onClick={closeMobileMenu}
            aria-label="Close navigation menu"
          >
            ×
          </button>
        </div>

        {/* Main Navigation */}
        <div className="sidebar-section">
          <p className="sidebar-label">MENU</p>

          <nav className="sidebar-navigation">
            {navigation.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                title={isCollapsed ? item.label : undefined}
                onClick={closeMobileMenu}
                className={({ isActive }) =>
                  `app-nav-link ${isActive ? "active" : ""}`
                }
              >
                <span className="app-nav-icon">{item.icon}</span>
                <span className="sidebar-link-text">
                  {item.label}
                </span>
              </NavLink>
            ))}
          </nav>
        </div>

        {/* User Navigation */}
        <div className="sidebar-section">
          <p className="sidebar-label">YOUR SPACE</p>

          <nav className="sidebar-navigation">
            <NavLink
              to="/events/create"
              title={isCollapsed ? "Create Event" : undefined}
              onClick={closeMobileMenu}
              className={({ isActive }) =>
                `app-nav-link ${isActive ? "active" : ""}`
              }
            >
              <span className="app-nav-icon">＋</span>
              <span className="sidebar-link-text">Create Event</span>
            </NavLink>

            <NavLink
              to="/profile"
              title={isCollapsed ? "My Profile" : undefined}
              onClick={closeMobileMenu}
              className={({ isActive }) =>
                `app-nav-link ${isActive ? "active" : ""}`
              }
            >
              <ProfileAvatar />
              <span className="sidebar-link-text">My Profile</span>
            </NavLink>

            <NavLink
              to="/organizer"
              title={isCollapsed ? "Organizer Dashboard" : undefined}
              onClick={closeMobileMenu}
              className={({ isActive }) =>
                `app-nav-link ${isActive ? "active" : ""}`
              }
            >
              <span className="app-nav-icon">◇</span>
              <span className="sidebar-link-text">
                Organizer Dashboard
              </span>
            </NavLink>
          </nav>
        </div>

        {/* Logout */}
        <div className="sidebar-section">
          <button
            type="button"
            className="app-nav-link"
            onClick={handleLogout}
            title={isCollapsed ? "Logout" : undefined}
          >
            <span className="app-nav-icon">↪</span>
            <span className="sidebar-link-text">Logout</span>
          </button>
        </div>

        {/* Sidebar Footer */}
        <div className="sidebar-footer">
          <span className="sidebar-footer-brand">BYB.</span>
          <p>Beyond Your Bubble.</p>
        </div>
      </aside>

      {/* Main Content */}
      <div className="app-main">
        <main className="app-content">
          <Outlet />
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <nav className="mobile-app-navbar" aria-label="Mobile navigation">
        <NavLink
          to="/discover"
          onClick={closeMobileMenu}
          className={({ isActive }) =>
            `mobile-app-nav-item ${isActive ? "active" : ""}`
          }
        >
          <span className="mobile-app-nav-icon">⌕</span>
          <span>Discover</span>
        </NavLink>

        <NavLink
          to="/hubs"
          onClick={closeMobileMenu}
          className={({ isActive }) =>
            `mobile-app-nav-item ${isActive ? "active" : ""}`
          }
        >
          <span className="mobile-app-nav-icon">◈</span>
          <span>Hubs</span>
        </NavLink>

        <NavLink
          to="/events/create"
          onClick={closeMobileMenu}
          className={({ isActive }) =>
            `mobile-create-button ${isActive ? "active" : ""}`
          }
          aria-label="Create Event"
        >
          <span>＋</span>
        </NavLink>

        <NavLink
          to="/events"
          onClick={closeMobileMenu}
          className={({ isActive }) =>
            `mobile-app-nav-item ${isActive ? "active" : ""}`
          }
        >
          <span className="mobile-app-nav-icon">▦</span>
          <span>Events</span>
        </NavLink>

        <NavLink
          to="/profile"
          onClick={closeMobileMenu}
          className={({ isActive }) =>
            `mobile-app-nav-item ${isActive ? "active" : ""}`
          }
        >
          <ProfileAvatar className="mobile-profile-avatar" />
          <span>Profile</span>
        </NavLink>
      </nav>
    </div>
  );
}

export default AppLayout;
