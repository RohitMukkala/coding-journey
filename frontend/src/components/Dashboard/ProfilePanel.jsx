import React from "react";
import { motion } from "framer-motion";
import { FaGithub, FaLinkedin, FaCode } from "react-icons/fa";
import { SiLeetcode, SiCodechef, SiCodeforces } from "react-icons/si";

const ProfilePanel = ({
  userDetails,
  onPhotoUpload,
  onDetailsUpdate,
  profileData,
}) => {
  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onPhotoUpload(file);
    }
  };

  const renderStars = (score) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i} className={`star ${i < score ? "filled" : ""}`}>
        ★
      </span>
    ));
  };

  const getPlatformStatus = (platform) => {
    return profileData[platform] ? "connected" : "disconnected";
  };

  return (
    <div className="profile-panel-content">
      <div className="photo-upload-container">
        <motion.div
          className="photo-circle"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {userDetails.photo ? (
            <img src={userDetails.photo} alt="Profile" />
          ) : (
            <div className="upload-placeholder">
              <FaCode size={40} />
              <p>Upload Photo</p>
            </div>
          )}
          <input
            type="file"
            accept="image/*"
            onChange={handlePhotoChange}
            className="photo-input"
          />
        </motion.div>
      </div>

      <div className="user-details">
        <div className="name-container">
          <motion.input
            type="text"
            value={userDetails.name}
            onChange={(e) => onDetailsUpdate({ name: e.target.value })}
            placeholder="Your Name"
            className="name-input"
            whileFocus={{ scale: 1.02 }}
          />
          {userDetails.name && (
            <span className="verified-badge" title="Verified">
              ✓
            </span>
          )}
        </div>

        <motion.input
          type="email"
          value={userDetails.email}
          onChange={(e) => onDetailsUpdate({ email: e.target.value })}
          placeholder="Your Email"
          className="email-input"
          whileFocus={{ scale: 1.02 }}
        />

        <div className="rank-badge">🏅 {userDetails.rank}</div>

        <div className="composite-score">
          <span>Composite Score:</span>
          <div className="stars">{renderStars(userDetails.score)}</div>
        </div>
      </div>

      <div className="platform-connections">
        <h3>Connected Platforms</h3>
        <div className="connection-grid">
          <div className={`platform-icon ${getPlatformStatus("github")}`}>
            <FaGithub size={24} />
          </div>
          <div className={`platform-icon ${getPlatformStatus("leetcode")}`}>
            <SiLeetcode size={24} />
          </div>
          <div className={`platform-icon ${getPlatformStatus("codechef")}`}>
            <SiCodechef size={24} />
          </div>
          <div className={`platform-icon ${getPlatformStatus("codeforces")}`}>
            <SiCodeforces size={24} />
          </div>
        </div>
      </div>

      <motion.button
        className="export-button"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Export Dashboard
      </motion.button>
    </div>
  );
};

export default ProfilePanel;
