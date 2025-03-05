import React, { useState } from "react";
import { motion } from "framer-motion";
import ProfilePanel from "./ProfilePanel";
import PlatformCard from "./PlatformCard";
import AchievementShelf from "./AchievementShelf";
import { useAuth } from "../../context/AuthContext";
import { useCodingProfiles } from "../../hooks/useCodingProfiles";
import { FaSync } from "react-icons/fa";
import "./styles.css";

const Dashboard = () => {
  const { user } = useAuth();
  const { profileData, loading, updating } = useCodingProfiles(user);
  const [activeTab, setActiveTab] = useState("overview");

  // Function to manually trigger a refresh
  const handleSync = () => {
    window.location.reload();
  };

  if (!user) {
    return (
      <div className="dashboard-container">
        <h2>Please log in to view your dashboard</h2>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <aside className="profile-panel">
        <ProfilePanel userDetails={user} profileData={profileData} />
      </aside>

      <main className="main-content">
        <nav className="platform-tabs">
          <motion.button
            className={`tab ${activeTab === "overview" ? "active" : ""}`}
            onClick={() => setActiveTab("overview")}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Overview
          </motion.button>
          {Object.keys(profileData).map((platform) => (
            <motion.button
              key={platform}
              className={`tab ${activeTab === platform ? "active" : ""}`}
              onClick={() => setActiveTab(platform)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {platform.charAt(0).toUpperCase() + platform.slice(1)}
            </motion.button>
          ))}
          <motion.button
            className="sync-button"
            onClick={handleSync}
            disabled={updating}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Sync all profiles"
          >
            <FaSync className={updating ? "rotating" : ""} />
            {updating ? "Syncing..." : "Sync Now"}
          </motion.button>
        </nav>

        <div className="platform-cards">
          {activeTab === "overview" ? (
            <>
              <PlatformCard
                platform="github"
                data={profileData.github}
                loading={loading.github}
                username={user?.github_username}
              />
              <PlatformCard
                platform="leetcode"
                data={profileData.leetcode}
                loading={loading.leetcode}
                username={user?.leetcode_username}
              />
              <PlatformCard
                platform="codechef"
                data={profileData.codechef}
                loading={loading.codechef}
                username={user?.codechef_username}
              />
              <PlatformCard
                platform="codeforces"
                data={profileData.codeforces}
                loading={loading.codeforces}
                username={user?.codeforces_username}
              />
            </>
          ) : (
            <PlatformCard
              platform={activeTab}
              data={profileData[activeTab]}
              loading={loading[activeTab]}
              username={user?.[`${activeTab}_username`]}
              expanded
            />
          )}
        </div>

        <AchievementShelf achievements={profileData} />
      </main>
    </div>
  );
};

export default Dashboard;
