import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import ProfilePanel from "./ProfilePanel";
import PlatformCard from "./PlatformCard";
import AchievementShelf from "./AchievementShelf";
import { useAuth } from "../../context/AuthContext";
import axiosInstance from "../../utils/axios";
import "./styles.css";

const Dashboard = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState({
    github: null,
    leetcode: null,
    codechef: null,
    codeforces: null,
  });
  const [loading, setLoading] = useState({
    github: false,
    leetcode: false,
    codechef: false,
    codeforces: false,
  });
  const [activeTab, setActiveTab] = useState("overview");

  const fetchGitHubProfile = async (username) => {
    if (!username) return null;
    setLoading((prev) => ({ ...prev, github: true }));
    try {
      console.log("Fetching GitHub data for username:", username);
      // Use the new optimized endpoint that fetches all data in parallel
      const response = await axiosInstance.get(`/api/github/${username}/all`);
      console.log("GitHub data fetched:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error fetching GitHub profile:", error.response || error);
      return null;
    } finally {
      setLoading((prev) => ({ ...prev, github: false }));
    }
  };

  const fetchLeetCodeProfile = async (username) => {
    if (!username) return null;
    setLoading((prev) => ({ ...prev, leetcode: true }));
    try {
      console.log("Fetching LeetCode data for username:", username);
      const response = await axiosInstance.get(`/api/leetcode/${username}`);
      console.log("LeetCode data fetched:", response.data);
      return response.data;
    } catch (error) {
      console.error(
        "Error fetching LeetCode profile:",
        error.response || error
      );
      return null;
    } finally {
      setLoading((prev) => ({ ...prev, leetcode: false }));
    }
  };

  const fetchCodeChefProfile = async (username) => {
    if (!username) return null;
    setLoading((prev) => ({ ...prev, codechef: true }));
    try {
      console.log("Fetching CodeChef data for username:", username);
      const response = await axiosInstance.get(`/api/codechef/${username}`);
      console.log("CodeChef data fetched:", response.data);
      return response.data;
    } catch (error) {
      console.error(
        "Error fetching CodeChef profile:",
        error.response || error
      );
      return null;
    } finally {
      setLoading((prev) => ({ ...prev, codechef: false }));
    }
  };

  const fetchCodeForcesProfile = async (username) => {
    if (!username) return null;
    setLoading((prev) => ({ ...prev, codeforces: true }));
    try {
      console.log("Fetching CodeForces data for username:", username);
      const response = await axiosInstance.get(`/api/codeforces/${username}`);
      console.log("CodeForces data fetched:", response.data);
      return response.data;
    } catch (error) {
      console.error(
        "Error fetching CodeForces profile:",
        error.response || error
      );
      return null;
    } finally {
      setLoading((prev) => ({ ...prev, codeforces: false }));
    }
  };

  useEffect(() => {
    const fetchAllProfiles = async () => {
      if (!user) return;

      console.log("Current user data:", user);
      console.log("Usernames:", {
        github: user.github_username,
        leetcode: user.leetcode_username,
        codechef: user.codechef_username,
        codeforces: user.codeforces_username,
      });

      const [githubData, leetcodeData, codechefData, codeforcesData] =
        await Promise.all([
          fetchGitHubProfile(user.github_username),
          fetchLeetCodeProfile(user.leetcode_username),
          fetchCodeChefProfile(user.codechef_username),
          fetchCodeForcesProfile(user.codeforces_username),
        ]);

      console.log("All profile data fetched:", {
        github: githubData,
        leetcode: leetcodeData,
        codechef: codechefData,
        codeforces: codeforcesData,
      });

      setProfileData({
        github: githubData,
        leetcode: leetcodeData,
        codechef: codechefData,
        codeforces: codeforcesData,
      });
    };

    fetchAllProfiles();
  }, [user]);

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
