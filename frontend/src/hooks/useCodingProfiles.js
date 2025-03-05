import { useState, useEffect } from "react";
import axiosInstance from "../utils/axios";

export const useCodingProfiles = (user) => {
  const [profileData, setProfileData] = useState(() => {
    const cachedData = localStorage.getItem("codingProfile");
    return cachedData
      ? JSON.parse(cachedData)
      : { github: null, leetcode: null, codechef: null, codeforces: null };
  });

  const [loading, setLoading] = useState({
    github: false,
    leetcode: false,
    codechef: false,
    codeforces: false,
  });
  const [updating, setUpdating] = useState(false); // Track background updates

  const fetchPlatformData = async (platform, username) => {
    if (!username) return null;
    try {
      const response = await axiosInstance.get(`/api/${platform}/${username}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching ${platform} data:`, error);
      return null;
    }
  };

  useEffect(() => {
    if (!user) return;

    const platforms = {
      github: user.github_username,
      leetcode: user.leetcode_username,
      codechef: user.codechef_username,
      codeforces: user.codeforces_username,
    };

    // Show cached data instantly (if available)
    const cachedData = localStorage.getItem("codingProfile");
    if (cachedData) {
      setProfileData(JSON.parse(cachedData));
    }

    // Fetch new data in background
    const fetchAllData = async () => {
      setUpdating(true);
      const fetchPromises = Object.entries(platforms)
        .filter(([_, username]) => username)
        .map(async ([platform, username]) => {
          const data = await fetchPlatformData(platform, username);
          return [platform, data];
        });

      try {
        const results = await Promise.all(fetchPromises);

        setProfileData((prev) => {
          const newData = { ...prev };
          results.forEach(([platform, data]) => {
            if (data) {
              newData[platform] = data;
            }
          });

          // Save updated data in localStorage
          localStorage.setItem("codingProfile", JSON.stringify(newData));

          return newData;
        });
      } catch (error) {
        console.error("Error fetching profile data:", error);
      } finally {
        setUpdating(false);
        setLoading({
          github: false,
          leetcode: false,
          codechef: false,
          codeforces: false,
        });
      }
    };

    fetchAllData(); // Run fetch in the background

    // Refresh every 5 minutes
    const refreshInterval = setInterval(fetchAllData, 5 * 60 * 1000);
    return () => clearInterval(refreshInterval);
  }, [user]);

  return { profileData, loading, updating };
};
