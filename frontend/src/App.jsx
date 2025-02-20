import { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import "./App.css";
import Navbar from "./components/Navbar";
import ResumeEnhancer from "./components/ResumeEnhancer";
import LandingPage from "./components/LandingPage";
import Dashboard from "./components/Dashboard";
import Login from "./components/Auth/Login";
import SignUp from "./components/Auth/SignUp";
import Settings from "./components/Settings";

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem("token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  const [showResume, setShowResume] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [userProfiles, setUserProfiles] = useState({
    github: "",
    leetcode: "",
    codechef: "",
    codeforces: "",
  });

  const handleProfileSubmit = (profiles) => {
    setUserProfiles(profiles);
    setShowDashboard(true);
  };

  const renderWithContainer = (Component, props) => (
    <div className="page-container page-transition">
      <Component {...props} />
    </div>
  );

  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <div className="content-wrapper">
          <Routes>
            <Route
              path="/"
              element={renderWithContainer(LandingPage, {
                onGetStarted: () => setShowResume(true),
              })}
            />
            <Route path="/login" element={renderWithContainer(Login)} />
            <Route path="/signup" element={renderWithContainer(SignUp)} />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>{renderWithContainer(Settings)}</ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  {renderWithContainer(Dashboard, {
                    userProfiles: userProfiles,
                  })}
                </ProtectedRoute>
              }
            />
            <Route
              path="/resume-enhancer"
              element={
                <ProtectedRoute>
                  {renderWithContainer(ResumeEnhancer, {
                    onBack: () => setShowResume(false),
                  })}
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
