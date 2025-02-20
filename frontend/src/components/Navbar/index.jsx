import React, { useState, useRef, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import {
  FaUser,
  FaChevronDown,
  FaCog,
  FaSignOutAlt,
  FaBars,
  FaTimes,
  FaChartBar,
  FaFileAlt,
} from "react-icons/fa";
import "./styles.css";

const Navbar = () => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const dropdownRef = useRef(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, logout, user } = useAuth();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
    setIsDropdownOpen(false);
    setIsSidebarOpen(false);
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <>
      <nav className="navbar">
        <div className="nav-content">
          {/* Logo Section */}
          <Link to="/" className="logo">
            <div className="logo-text">Logo</div>
          </Link>

          {/* Sidebar Toggle Button */}
          {isAuthenticated && (
            <button className="sidebar-toggle" onClick={toggleSidebar}>
              {isSidebarOpen ? <FaTimes /> : <FaBars />}
            </button>
          )}

          {/* User Profile Section */}
          <div className="user-section" ref={dropdownRef}>
            {isAuthenticated ? (
              <>
                <div
                  className="user-profile"
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  title={user?.username || "Profile"}
                >
                  {user?.profile_picture ? (
                    <img
                      src={user.profile_picture}
                      alt="Profile"
                      className="profile-image"
                    />
                  ) : (
                    <FaUser className="user-icon" />
                  )}
                  <FaChevronDown
                    className={`dropdown-arrow ${isDropdownOpen ? "open" : ""}`}
                  />
                </div>
                {isDropdownOpen && (
                  <div className="dropdown-menu">
                    <Link
                      to="/settings"
                      className="dropdown-item"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      <FaCog className="dropdown-icon" />
                      Settings
                    </Link>
                    <button onClick={handleLogout} className="dropdown-item">
                      <FaSignOutAlt className="dropdown-icon" />
                      Logout
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="auth-buttons">
                <Link to="/signup" className="signup-button">
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Sidebar */}
      {isAuthenticated && (
        <div className={`sidebar ${isSidebarOpen ? "open" : ""}`}>
          <div className="sidebar-content">
            <Link
              to="/dashboard"
              className={`sidebar-item ${
                location.pathname === "/dashboard" ? "active" : ""
              }`}
              onClick={() => setIsSidebarOpen(false)}
            >
              <FaChartBar className="sidebar-icon" />
              <span className="sidebar-text">Dashboard</span>
            </Link>
            <Link
              to="/resume-enhancer"
              className={`sidebar-item ${
                location.pathname === "/resume-enhancer" ? "active" : ""
              }`}
              onClick={() => setIsSidebarOpen(false)}
            >
              <FaFileAlt className="sidebar-icon" />
              <span className="sidebar-text">Resume</span>
            </Link>
            <Link
              to="/settings"
              className={`sidebar-item ${
                location.pathname === "/settings" ? "active" : ""
              }`}
              onClick={() => setIsSidebarOpen(false)}
            >
              <FaCog className="sidebar-icon" />
              <span className="sidebar-text">Settings</span>
            </Link>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
