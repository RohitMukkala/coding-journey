import { useState } from "react";
import "./App.css";
import ResumeEnhancer from "./components/ResumeEnhancer";
import LandingPage from "./components/LandingPage";

function App() {
  const [showResume, setShowResume] = useState(false);

  return (
    <div className="app-container">
      {showResume ? (
        <ResumeEnhancer />
      ) : (
        <LandingPage onGetStarted={() => setShowResume(true)} />
      )}
    </div>
  );
}

export default App;
