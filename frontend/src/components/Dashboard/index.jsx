import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import ProfilePanel from "./ProfilePanel";
import PlatformCard from "./PlatformCard";
import AchievementShelf from "./AchievementShelf";
import "./styles.css";

const Dashboard = ({ userProfiles }) => {
  const [profileData, setProfileData] = useState({
    github: null,
    leetcode: null,
    codechef: null,
    codeforces: null,
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [userDetails, setUserDetails] = useState({
    name: "",
    email: "",
    photo: null,
    rank: "Top 15% of Users",
    score: 4,
  });

  useEffect(() => {
    const fetchAllProfiles = async () => {
      setLoading(true);
      try {
        // Fetch data for all platforms
        const responses = await Promise.all([
          fetch(`http://localhost:8000/api/github/${userProfiles.github}`),
          fetch(`http://localhost:8000/api/leetcode/${userProfiles.leetcode}`),
          fetch(`http://localhost:8000/api/codechef/${userProfiles.codechef}`),
          fetch(
            `http://localhost:8000/api/codeforces/${userProfiles.codeforces}`
          ),
        ]);

        const [github, leetcode, codechef, codeforces] = await Promise.all(
          responses.map((r) => r.json())
        );

        setProfileData({
          github,
          leetcode,
          codechef,
          codeforces,
        });
      } catch (error) {
        console.error("Error fetching profile data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllProfiles();
  }, [userProfiles]);

  const handlePhotoUpload = (file) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      setUserDetails((prev) => ({
        ...prev,
        photo: reader.result,
      }));
    };
    reader.readAsDataURL(file);
  };

  const handleDetailsUpdate = (details) => {
    setUserDetails((prev) => ({
      ...prev,
      ...details,
    }));
  };

  return (
    <div className="dashboard-container">
      <aside className="profile-panel">
        <ProfilePanel
          userDetails={userDetails}
          onPhotoUpload={handlePhotoUpload}
          onDetailsUpdate={handleDetailsUpdate}
          profileData={profileData}
        />
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
        </nav>

        <div className="platform-cards">
          {activeTab === "overview" ? (
            <>
              <PlatformCard
                platform="linkedin"
                data={profileData.leetcode}
                loading={loading}
              />
              <PlatformCard
                platform="codechef"
                data={profileData.codechef}
                loading={loading}
              />
              <PlatformCard
                platform="codeforces"
                data={profileData.codeforces}
                loading={loading}
              />
              <PlatformCard
                platform="github"
                data={profileData.github}
                loading={loading}
              />
            </>
          ) : (
            <PlatformCard
              platform={activeTab}
              data={profileData[activeTab]}
              loading={loading}
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
