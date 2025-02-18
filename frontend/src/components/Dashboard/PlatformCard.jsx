import React from "react";
import { motion } from "framer-motion";
import { FaGithub, FaCode } from "react-icons/fa";
import { SiLeetcode, SiCodechef, SiCodeforces } from "react-icons/si";

const PlatformCard = ({ platform, data, loading, expanded }) => {
  const getPlatformIcon = () => {
    switch (platform) {
      case "github":
        return <FaGithub size={24} />;
      case "leetcode":
        return <SiLeetcode size={24} />;
      case "codechef":
        return <SiCodechef size={24} />;
      case "codeforces":
        return <SiCodeforces size={24} />;
      default:
        return <FaCode size={24} />;
    }
  };

  const renderContent = () => {
    if (loading) {
      return <div className="loading-skeleton" />;
    }

    if (!data) {
      return (
        <div className="empty-state">
          <p>No data available</p>
          <button className="connect-button">Connect {platform}</button>
        </div>
      );
    }

    switch (platform) {
      case "github":
        return (
          <div className="github-stats">
            <div className="stat-row">
              <span>Contributions</span>
              <span>{data.contributions?.total_contributions || 0}</span>
            </div>
            <div className="stat-row">
              <span>Current Streak</span>
              <span>{data.contributions?.current_streak || 0} days</span>
            </div>
            <div className="languages">
              {Object.entries(data.languages || {}).map(([lang, percent]) => (
                <div key={lang} className="language-bar">
                  <span>{lang}</span>
                  <div className="bar">
                    <div className="fill" style={{ width: `${percent}%` }} />
                  </div>
                  <span>{percent}%</span>
                </div>
              ))}
            </div>
          </div>
        );

      case "leetcode":
        return (
          <div className="leetcode-stats">
            <div className="submission-matrix">
              <div className="difficulty-bar">
                <div
                  className="easy"
                  style={{ width: `${data.easyPercentage || 0}%` }}
                />
                <div
                  className="medium"
                  style={{ width: `${data.mediumPercentage || 0}%` }}
                />
                <div
                  className="hard"
                  style={{ width: `${data.hardPercentage || 0}%` }}
                />
              </div>
              <div className="counts">
                <span>Easy: {data.easySolved || 0}</span>
                <span>Medium: {data.mediumSolved || 0}</span>
                <span>Hard: {data.hardSolved || 0}</span>
              </div>
            </div>
            <div className="total-solved">
              Total Problems Solved: {data.totalSolved || 0}
            </div>
          </div>
        );

      case "codechef":
        return (
          <div className="codechef-stats">
            <div className="rating">
              <div className="rating-circle">
                <span className="current">{data.currentRating || 0}</span>
                <span className="peak">Peak: {data.highestRating || 0}</span>
              </div>
            </div>
            <div className="ranks">
              <div className="rank-item">
                <span>Global</span>
                <span>#{data.globalRank || "N/A"}</span>
              </div>
              <div className="rank-item">
                <span>Country</span>
                <span>#{data.countryRank || "N/A"}</span>
              </div>
            </div>
            <div className="stars">{data.stars || 0}★</div>
          </div>
        );

      case "codeforces":
        return (
          <div className="codeforces-stats">
            <div className="rating">
              Current Rating: {data.current_rating || 0}
            </div>
            <div className="problems">
              Problems Solved: {data.problems_solved || 0}
            </div>
            {data.example_problems && (
              <div className="recent-problems">
                <h4>Recent Problems</h4>
                {data.example_problems.slice(0, 3).map((problem, index) => (
                  <div key={index} className="problem-item">
                    <span>{problem.name}</span>
                    <span className="difficulty">{problem.difficulty}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      default:
        return <div>Platform not supported</div>;
    }
  };

  return (
    <motion.div
      className={`platform-card ${platform} ${expanded ? "expanded" : ""}`}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <div className="card-header">
        {getPlatformIcon()}
        <h3>{platform.charAt(0).toUpperCase() + platform.slice(1)} Stats</h3>
      </div>
      <div className="card-content">{renderContent()}</div>
    </motion.div>
  );
};

export default PlatformCard;
