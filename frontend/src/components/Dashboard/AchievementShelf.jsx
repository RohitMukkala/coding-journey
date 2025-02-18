import React from "react";
import { motion } from "framer-motion";
import { FaTrophy, FaStar, FaCode, FaFire } from "react-icons/fa";

const AchievementShelf = ({ achievements }) => {
  const calculateAchievements = () => {
    const achievementsList = [];

    // GitHub Achievements
    if (achievements.github) {
      const { contributions, stats } = achievements.github;

      if (contributions?.current_streak >= 7) {
        achievementsList.push({
          icon: <FaFire />,
          title: "Consistent Contributor",
          description: `${contributions.current_streak} day streak!`,
          color: "#ff9800",
        });
      }

      if (stats?.stars >= 10) {
        achievementsList.push({
          icon: <FaStar />,
          title: "Star Collector",
          description: `${stats.stars} repository stars earned`,
          color: "#ffd700",
        });
      }
    }

    // LeetCode Achievements
    if (achievements.leetcode) {
      const { totalSolved, hardSolved } = achievements.leetcode;

      if (totalSolved >= 100) {
        achievementsList.push({
          icon: <FaCode />,
          title: "Century Club",
          description: "100+ problems solved",
          color: "#00b8d4",
        });
      }

      if (hardSolved >= 10) {
        achievementsList.push({
          icon: <FaTrophy />,
          title: "Hard Worker",
          description: "10+ hard problems solved",
          color: "#f50057",
        });
      }
    }

    // CodeChef Achievements
    if (achievements.codechef) {
      const { currentRating } = achievements.codechef;

      if (currentRating >= 1800) {
        achievementsList.push({
          icon: <FaTrophy />,
          title: "CodeChef Expert",
          description: "Rating 1800+",
          color: "#ff5722",
        });
      }
    }

    // Codeforces Achievements
    if (achievements.codeforces) {
      const { current_rating, problems_solved } = achievements.codeforces;

      if (current_rating >= 1400) {
        achievementsList.push({
          icon: <FaTrophy />,
          title: "Codeforces Specialist",
          description: "Rating 1400+",
          color: "#2196f3",
        });
      }

      if (problems_solved >= 50) {
        achievementsList.push({
          icon: <FaCode />,
          title: "Problem Solver",
          description: "50+ problems solved",
          color: "#4caf50",
        });
      }
    }

    return achievementsList;
  };

  const achievementItems = calculateAchievements();

  if (achievementItems.length === 0) {
    return null;
  }

  return (
    <div className="achievement-shelf">
      <h2>Achievements</h2>
      <div className="achievements-grid">
        {achievementItems.map((achievement, index) => (
          <motion.div
            key={index}
            className="achievement-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            style={{ backgroundColor: achievement.color + "20" }}
          >
            <div
              className="achievement-icon"
              style={{ color: achievement.color }}
            >
              {achievement.icon}
            </div>
            <div className="achievement-info">
              <h3>{achievement.title}</h3>
              <p>{achievement.description}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default AchievementShelf;
