import React from "react";
import "../styles/Dashboard.css";

const Dashboard = ({ contributions, stats, languages }) => {
  return (
    <div className="dashboard">
      <h2>⚡ Stats ⚡</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>{contributions.total_contributions || 0}</h3>
          <p>Total Contributions</p>
        </div>

        <div className="stat-card">
          <h3>{contributions.current_streak || 0}</h3>
          <p>Current Streak (Days)</p>
        </div>

        <div className="stat-card">
          <h3>{contributions.longest_streak || 0}</h3>
          <p>Longest Streak (Days)</p>
        </div>

        <div className="stats-details">
          <div className="stat-item">
            <h4>Total Stars Earned:</h4>
            <span>{stats.stars || 0}</span>
          </div>
          <div className="stat-item">
            <h4>Total Commits:</h4>
            <span>{stats.commits || 0}</span>
          </div>
          <div className="stat-item">
            <h4>Total PRs:</h4>
            <span>{stats.prs || 0}</span>
          </div>
          <div className="stat-item">
            <h4>Total Issues:</h4>
            <span>{stats.issues || 0}</span>
          </div>
        </div>
      </div>

      <div className="languages-section">
        <h3>Most Used Languages</h3>
        <div className="language-bars">
          {Object.entries(languages || {}).map(([lang, percent]) => (
            <div key={lang} className="language-bar">
              <div className="bar-label">
                <span>{lang}</span>
                <span>{percent}%</span>
              </div>
              <div className="bar-container">
                <div
                  className="bar-fill"
                  style={{ width: `${percent}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
