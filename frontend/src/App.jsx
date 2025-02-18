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
            <Route
              path="/dashboard"
              element={renderWithContainer(Dashboard, {
                userProfiles: userProfiles,
              })}
            />
            <Route
              path="/resume-enhancer"
              element={renderWithContainer(ResumeEnhancer, {
                onBack: () => setShowResume(false),
              })}
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
