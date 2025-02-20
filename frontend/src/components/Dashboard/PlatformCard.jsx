import React from "react";
import { motion } from "framer-motion";
import { FaGithub, FaCode } from "react-icons/fa";
import { SiLeetcode, SiCodechef, SiCodeforces } from "react-icons/si";
import { useNavigate } from "react-router-dom";
import "./styles.css";

const PlatformCard = ({ platform, data, loading, username, expanded }) => {
  const navigate = useNavigate();

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

    if (!username) {
      return (
        <div className="empty-state">
          <p>Connect your {platform} profile to see your stats</p>
          <button
            className="connect-button"
            onClick={() => navigate("/settings")}
          >
            Connect {platform}
          </button>
        </div>
      );
    }

    if (!data) {
      return (
        <div className="empty-state">
          <p>Could not fetch data for username: {username}</p>
          <p>Please verify your username in settings</p>
          <button
            className="connect-button"
            onClick={() => navigate("/settings")}
          >
            Update Username
          </button>
        </div>
      );
    }

    switch (platform) {
      case "github":
        return (
          <div className="github-stats">
            <div className="username-display">@{username}</div>
            <div className="stat-row">
              <span>Contributions</span>
              <span>{data.contributions?.total_contributions || 0}</span>
            </div>
            <div className="stat-row">
              <span>Current Streak</span>
              <span>{data.contributions?.current_streak || 0} days</span>
            </div>
            <div className="stat-row">
              <span>Stars</span>
              <span>{data.stats?.stars || 0}</span>
            </div>
            <div className="stat-row">
              <span>Forks</span>
              <span>{data.stats?.forks || 0}</span>
            </div>
            {data.languages && Object.keys(data.languages).length > 0 && (
              <div className="languages">
                <h4>Top Languages</h4>
                {Object.entries(data.languages)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 5)
                  .map(([lang, percent]) => (
                    <div key={lang} className="language-bar">
                      <div className="language-name">{lang}</div>
                      <div className="bar">
                        <div
                          className="fill"
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                      <div className="percentage">{percent}%</div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        );

      case "leetcode":
        return (
          <div className="leetcode-stats">
            <div className="username-display">@{username}</div>
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
            <div className="username-display">@{username}</div>
            <div className="rating">
              <div className="rating-circle">
                <span className="current">
                  Rating: {data.currentRating || 0}
                </span>
                <span className="peak">Peak: {data.highestRating || 0}</span>
              </div>
            </div>
            <div className="ranks">
              <div className="rank-item">
                <span>Global Rank</span>
                <span>#{data.globalRank || "N/A"}</span>
              </div>
              <div className="rank-item">
                <span>Country Rank</span>
                <span>#{data.countryRank || "N/A"}</span>
              </div>
            </div>
            {data.stars && <div className="stars">{data.stars}★</div>}
          </div>
        );

      case "codeforces":
        return (
          <div className="codeforces-stats">
            <div className="username-display">@{username}</div>
            <div className="rating">
              <span>Current Rating: {data.current_rating || 0}</span>
            </div>
            <div className="problems">
              <span>Problems Solved: {data.problems_solved || 0}</span>
            </div>
            {data.example_problems && data.example_problems.length > 0 && (
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
