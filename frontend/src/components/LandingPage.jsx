import React, { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import "./LandingPage.css";
import Particles from "react-particles";
import { loadFull } from "tsparticles";
import { FaGithub, FaCode, FaChartLine, FaBrain } from "react-icons/fa";
import { SiLeetcode } from "react-icons/si";

const LandingPage = ({ onGetStarted }) => {
  const particlesInit = async (main) => {
    await loadFull(main);
  };

  const particlesConfig = {
    fullScreen: false,
    background: {
      color: {
        value: "transparent",
      },
    },
    fpsLimit: 120,
    particles: {
      color: {
        value: "#ffffff",
      },
      links: {
        color: "#ffffff",
        distance: 150,
        enable: true,
        opacity: 0.3,
        width: 1,
      },
      move: {
        enable: true,
        outModes: {
          default: "bounce",
        },
        random: false,
        speed: 1,
        straight: false,
      },
      number: {
        density: {
          enable: true,
          area: 800,
        },
        value: 100,
      },
      opacity: {
        value: 0.4,
      },
      shape: {
        type: "circle",
      },
      size: {
        value: { min: 1, max: 3 },
      },
    },
    detectRetina: true,
  };

  const statsData = [
    { label: "Success Rate", value: 92 },
    { label: "Problems Solved", value: 85 },
    { label: "Profile Growth", value: 88 },
  ];

  const codeSnippet = `
// Your Coding Journey
class Developer {
  analyzeProfiles() {
    // GitHub & LeetCode
  }
  
  getRecommendations() {
    // Smart Practice Plan
  }
  
  optimizeResume() {
    // ATS Enhancement
  }
}`;

  return (
    <div className="landing-page">
      <Particles
        id="tsparticles"
        init={particlesInit}
        options={particlesConfig}
      />

      <div className="content-container">
        <div className="left-section">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="headline"
          >
            Accelerate Your Tech Career
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="subheadline"
          >
            Comprehensive career growth platform with profile analysis,
            personalized practice recommendations, and ATS optimization
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="feature-cards"
          >
            <div className="feature-card">
              <FaChartLine className="feature-icon" />
              <h3>Profile Analysis</h3>
              <p>Deep insights from your GitHub & LeetCode profiles</p>
            </div>
            <div className="feature-card">
              <FaBrain className="feature-icon" />
              <h3>Smart Practice</h3>
              <p>AI-powered problem recommendations</p>
            </div>
            <div className="feature-card">
              <FaCode className="feature-icon" />
              <h3>Resume Enhancer</h3>
              <p>ATS-optimized resume builder</p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="platform-icons"
          >
            <div className="icon-container">
              <FaGithub className="platform-icon" />
              <span>GitHub Analysis</span>
            </div>
            <div className="icon-container">
              <SiLeetcode className="platform-icon" />
              <span>LeetCode Tracking</span>
            </div>
            <div className="icon-container">
              <FaCode className="platform-icon" />
              <span>Skill Growth</span>
            </div>
          </motion.div>

          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="get-started-btn"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onGetStarted}
          >
            Start Your Journey
          </motion.button>
        </div>

        <div className="right-section">
          <div className="stats-container">
            <div className="code-preview">
              <pre>{codeSnippet}</pre>
            </div>

            {statsData.map((stat, index) => (
              <motion.div
                key={stat.label}
                className="stat-bar"
                initial={{ width: 0, opacity: 0 }}
                animate={{ width: `${stat.value}%`, opacity: 1 }}
                transition={{ duration: 1, delay: 0.8 + index * 0.2 }}
              >
                <div className="stat-label">{stat.label}</div>
                <div className="stat-value">{stat.value}%</div>
                <div
                  className="stat-fill"
                  style={{ width: `${stat.value}%` }}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
