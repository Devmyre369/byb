
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
  { label: "Discover", path: "/", icon: "⌕" },
  { label: "Events", path: "/events", icon: "▦" },
  { label: "Media", path: "/media", icon: "▣" },
  { label: "Saved", path: "/saved", icon: "♡" },
];

function AppLayout() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const { logout } = useAuth();
  const navigate = useNavigate();

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

  return (
    <div
      className={`app-layout ${
        isCollapsed ? "sidebar-collapsed" : ""
      } ${isMobileMenuOpen ? "mobile-sidebar-open" : ""}`}
    >
      {/* Mobile Top Bar */}
      <header className="mobile-topbar">
        <Link
          to="/"
          className="mobile-brand"
          onClick={closeMobileMenu}
        >
          BYB<span>.</span>
        </Link>

        <button
          type="button"
          className="mobile-menu-toggle"
          onClick={toggleMobileMenu}
          aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
          aria-expanded={isMobileMenuOpen}
        >
          {isMobileMenuOpen ? "×" : "☰"}
        </button>
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
          <Link
            to="/"
            className="sidebar-brand"
            onClick={closeMobileMenu}
          >
            BYB<span>.</span>
          </Link>

          <button
            type="button"
            className="sidebar-toggle"
            onClick={toggleSidebar}
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? "☰" : "×"}
          </button>

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
                end={item.path === "/"}
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
              <span className="app-nav-icon">◎</span>
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
          to="/"
          end
          onClick={closeMobileMenu}
          className={({ isActive }) =>
            `mobile-app-nav-item ${isActive ? "active" : ""}`
          }
        >
          <span className="mobile-app-nav-icon">⌕</span>
          <span>Discover</span>
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
          to="/media"
          onClick={closeMobileMenu}
          className={({ isActive }) =>
            `mobile-app-nav-item ${isActive ? "active" : ""}`
          }
        >
          <span className="mobile-app-nav-icon">▣</span>
          <span>Media</span>
        </NavLink>

        <NavLink
          to="/profile"
          onClick={closeMobileMenu}
          className={({ isActive }) =>
            `mobile-app-nav-item ${isActive ? "active" : ""}`
          }
        >
          <span className="mobile-app-nav-icon">◎</span>
          <span>Profile</span>
        </NavLink>
      </nav>
    </div>
  );
}

export default AppLayout;
