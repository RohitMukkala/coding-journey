import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import axiosInstance from "../../utils/axios";
import "./styles.css";

const Settings = () => {
  const navigate = useNavigate();
  const { user, logout, updateUser } = useAuth();
  const [formData, setFormData] = useState({
    username: "",
    leetcode_username: "",
    github_username: "",
    codechef_username: "",
    codeforces_username: "",
  });
  const [profilePic, setProfilePic] = useState("/default-avatar.png");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || "",
        leetcode_username: user.leetcode_username || "",
        github_username: user.github_username || "",
        codechef_username: user.codechef_username || "",
        codeforces_username: user.codeforces_username || "",
      });
      if (user.profile_picture) {
        setProfilePic(user.profile_picture);
      }
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleProfilePicChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await axiosInstance.post(
          "/settings/profile-picture",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        setProfilePic(response.data.profile_picture);
        await updateUser(); // Update user data after profile picture change
      } catch (err) {
        setError("Failed to update profile picture");
      }
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      await axiosInstance.put("/settings", formData);
      await updateUser(); // Update user data after saving settings
      setSuccessMessage("Settings saved successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update settings");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="settings-container">
      <div className="settings-content">
        {/* Left Panel - Profile Picture */}
        <div className="profile-section">
          <div className="profile-picture-container">
            <img src={profilePic} alt="Profile" className="profile-picture" />
            <label htmlFor="profile-upload" className="profile-picture-upload">
              <i className="camera-icon">📷</i>
              <input
                id="profile-upload"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleProfilePicChange}
              />
            </label>
          </div>
          <p className="username">{formData.username}</p>
        </div>

        {/* Right Panel - Settings Form */}
        <div className="settings-form">
          {error && <div className="error-message">{error}</div>}
          {successMessage && (
            <div className="success-message">{successMessage}</div>
          )}

          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter username"
            />
          </div>

          <div className="form-group">
            <label>LeetCode Username</label>
            <input
              type="text"
              name="leetcode_username"
              value={formData.leetcode_username}
              onChange={handleChange}
              placeholder="Enter LeetCode username"
            />
          </div>

          <div className="form-group">
            <label>GitHub Username</label>
            <input
              type="text"
              name="github_username"
              value={formData.github_username}
              onChange={handleChange}
              placeholder="Enter GitHub username"
            />
          </div>

          <div className="form-group">
            <label>CodeChef Username</label>
            <input
              type="text"
              name="codechef_username"
              value={formData.codechef_username}
              onChange={handleChange}
              placeholder="Enter CodeChef username"
            />
          </div>

          <div className="form-group">
            <label>CodeForces Username</label>
            <input
              type="text"
              name="codeforces_username"
              value={formData.codeforces_username}
              onChange={handleChange}
              placeholder="Enter CodeForces username"
            />
          </div>

          <div className="button-group">
            <button
              className="save-button"
              onClick={handleSave}
              disabled={loading}
            >
              {loading ? "Saving..." : "Save Changes"}
            </button>
            <button className="logout-button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
