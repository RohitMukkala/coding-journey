import React, { useState, useEffect } from "react";
import axios from "axios";
import TextareaAutosize from "react-textarea-autosize";
import "./ResumeEnhancer.css";

const BACKEND_URL = "http://localhost:8000"; // Add backend URL

// Add icons for different sections
const Icons = {
  Resume: (
    <svg
      className="w-6 h-6"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
      />
    </svg>
  ),
  LinkedIn: (
    <svg
      className="w-6 h-6"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
      />
    </svg>
  ),
  JobDescription: (
    <svg
      className="w-6 h-6"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
      />
    </svg>
  ),
};

const UploadSection = ({
  type,
  label,
  accept,
  description,
  handleFileUpload,
  handleFileRemove,
  handleFileView,
  uploaded,
  currentFile,
}) => {
  // Add ref for the file input
  const fileInputRef = React.useRef(null);

  // Function to reset the file input
  const resetFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="upload-box">
      {/* Header */}
      <div className="upload-box-header">
        <h3>{label}</h3>
        <p>{uploaded ? "File uploaded" : "No file chosen"}</p>
      </div>

      {/* Main Content */}
      <div className="upload-box-content">
        <p className="upload-box-description">{description}</p>
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          onChange={(e) => handleFileUpload(e.target.files[0], type)}
          className="file-input"
          id={type}
        />

        {/* Footer */}
        <div className="upload-box-footer">
          {uploaded ? (
            <div className="uploaded-actions">
              <span className="file-name">{currentFile?.name}</span>
              <div className="action-buttons">
                <button
                  className="action-button view"
                  onClick={() => handleFileView(type)}
                  title="View File"
                >
                  <svg
                    className="w-5 h-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path
                      fillRule="evenodd"
                      d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
                <button
                  className="action-button remove"
                  onClick={() => {
                    handleFileRemove(type);
                    resetFileInput();
                  }}
                  title="Remove File"
                >
                  <svg
                    className="w-5 h-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>
          ) : (
            <label
              htmlFor={type}
              className="upload-button"
              onClick={resetFileInput}
            >
              Drop file here or click to browse
            </label>
          )}
          <p className="supported-formats">
            Supported: {accept.replace(/\./g, "").toUpperCase()}
          </p>
        </div>
      </div>
    </div>
  );
};

const ResumeEnhancer = () => {
  const [resumeData, setResumeData] = useState({
    name: "",
    email: "",
    linkedin: "",
    phone: "",
    location: "",
    experience: [],
    skills: [],
    projects: [],
    certifications: [],
    awards: [],
    education: [],
    publications: [],
  });
  const [jdMatch, setJdMatch] = useState(null);
  const [linkedinData, setLinkedinData] = useState(null);
  const [jdText, setJdText] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState({
    resume: false,
    linkedin: false,
    jd: false,
  });
  const [manualMode, setManualMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [matchScore, setMatchScore] = useState(null);
  const [missingKeywords, setMissingKeywords] = useState([]);
  const [files, setFiles] = useState({
    resume: null,
    linkedin: null,
    jd: null,
  });

  const handleFileUpload = async (file, type) => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const endpoint = type === "jd" ? "/upload/jd" : `/upload/${type}`;
      const response = await axios.post(`${BACKEND_URL}${endpoint}`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setUploadedFiles((prev) => ({ ...prev, [type]: true }));
      setFiles((prev) => ({ ...prev, [type]: file }));

      if (type === "resume") {
        const newData = response.data.data;

        // Validate the data to ensure it's not default/placeholder data
        const isValidData = (data) => {
          if (!data) return false;

          // Check if name contains default values
          if (data.name && data.name.toLowerCase().includes("john doe")) {
            return false;
          }

          // Ensure we have at least some real content
          const hasContent = Object.values(data).some((value) => {
            if (Array.isArray(value)) {
              return value.length > 0;
            }
            return typeof value === "string" && value.trim().length > 0;
          });

          return hasContent;
        };

        if (isValidData(newData)) {
          setResumeData((prevData) => {
            const updatedData = { ...prevData };
            Object.keys(newData).forEach((key) => {
              if (
                newData[key] &&
                (typeof newData[key] === "string"
                  ? newData[key].trim()
                  : newData[key].length > 0)
              ) {
                updatedData[key] = newData[key];
              }
            });
            return updatedData;
          });
        } else {
          // If data is invalid, show an error and reset the upload
          alert(
            "Could not extract valid information from the resume. Please check the file and try again."
          );
          handleFileRemove(type);
        }
      } else if (type === "linkedin") {
        const newData = response.data.data;

        // Similar validation for LinkedIn data
        const isValidData = (data) => {
          if (!data) return false;

          if (data.name && data.name.toLowerCase().includes("john doe")) {
            return false;
          }

          const hasContent = Object.values(data).some((value) => {
            if (Array.isArray(value)) {
              return value.length > 0;
            }
            return typeof value === "string" && value.trim().length > 0;
          });

          return hasContent;
        };

        if (isValidData(newData)) {
          setLinkedinData((prevData) => {
            const updatedData = { ...prevData };
            Object.keys(newData).forEach((key) => {
              if (
                newData[key] &&
                (typeof newData[key] === "string"
                  ? newData[key].trim()
                  : newData[key].length > 0)
              ) {
                updatedData[key] = newData[key];
              }
            });
            return updatedData;
          });
        } else {
          alert(
            "Could not extract valid information from the LinkedIn profile. Please check the file and try again."
          );
          handleFileRemove(type);
        }
      } else if (type === "jd") {
        const jdText = response.data.data;
        if (
          jdText &&
          jdText.trim() &&
          !jdText.toLowerCase().includes("john doe")
        ) {
          setJdText(jdText);
        } else {
          alert(
            "Could not extract valid job description. Please check the file and try again."
          );
          handleFileRemove(type);
        }
      }
    } catch (error) {
      console.error("Upload error:", error.response?.data || error.message);
      alert(
        `Failed to upload ${type}: ${
          error.response?.data?.detail || error.message
        }`
      );
      handleFileRemove(type);
    } finally {
      setLoading(false);
    }
  };

  const handleFileRemove = (type) => {
    setUploadedFiles((prev) => ({ ...prev, [type]: false }));
    setFiles((prev) => ({ ...prev, [type]: null }));

    // Reset corresponding state based on type
    if (type === "resume") {
      setResumeData({
        name: "",
        email: "",
        linkedin: "",
        phone: "",
        location: "",
        experience: [],
        skills: [],
        projects: [],
        certifications: [],
        awards: [],
        education: [],
        publications: [],
      });
    } else if (type === "linkedin") {
      setLinkedinData(null);
    } else if (type === "jd") {
      setJdText("");
      setMatchScore(null);
      setMissingKeywords([]);
    }
  };

  const handleFileView = (type) => {
    const file = files[type];
    if (!file) return;

    // Create a temporary URL for the file
    const fileUrl = URL.createObjectURL(file);

    // Open in new tab
    window.open(fileUrl, "_blank");

    // Clean up the temporary URL
    URL.revokeObjectURL(fileUrl);
  };

  useEffect(() => {
    const mergeData = async () => {
      if (linkedinData && (uploadedFiles.linkedin || uploadedFiles.resume)) {
        setResumeData((prevData) => {
          const mergedData = { ...prevData };

          // Helper function to merge arrays without duplicates
          const mergeArrays = (existing, incoming) => {
            if (!incoming) return existing;
            const incomingArray = Array.isArray(incoming)
              ? incoming
              : incoming.split("\n").filter((item) => item.trim());
            const existingArray = Array.isArray(existing)
              ? existing
              : existing.split("\n").filter((item) => item.trim());

            // Create a Set of lowercase existing items for comparison
            const existingSet = new Set(
              existingArray.map((item) => item.toLowerCase())
            );

            // Add only non-duplicate items
            const newItems = incomingArray.filter(
              (item) => !existingSet.has(item.toLowerCase())
            );
            return [...existingArray, ...newItems];
          };

          // Merge each section
          Object.keys(linkedinData).forEach((key) => {
            if (linkedinData[key]) {
              if (
                Array.isArray(mergedData[key]) ||
                Array.isArray(linkedinData[key])
              ) {
                mergedData[key] = mergeArrays(
                  mergedData[key],
                  linkedinData[key]
                );
              } else if (!mergedData[key] && linkedinData[key]) {
                // Only update string fields if they're empty in current data
                mergedData[key] = linkedinData[key];
              }
            }
          });

          return mergedData;
        });
      }
    };
    mergeData();
  }, [linkedinData, uploadedFiles]);

  useEffect(() => {
    const matchJD = async () => {
      if (
        jdText &&
        resumeData.skills &&
        (uploadedFiles.jd || uploadedFiles.resume)
      ) {
        try {
          const response = await axios.post(`${BACKEND_URL}/match_jd`, {
            resume: resumeData,
            jd: jdText,
          });
          setJdMatch(response.data);
          setMatchScore(response.data.match_score);
          setMissingKeywords(response.data.missing_keywords);
        } catch (error) {
          console.error("JD matching error:", error);
        }
      }
    };
    matchJD();
  }, [jdText, resumeData, uploadedFiles]);

  const handleManualInput = (section, value) => {
    setResumeData((prev) => ({
      ...prev,
      [section]: Array.isArray(prev[section])
        ? value.split("\n").filter((item) => item.trim())
        : value,
    }));
  };

  const handleDownload = async () => {
    try {
      setLoading(true);

      // Format the resume data
      const formattedResumeData = {
        ...resumeData,
        skills: Array.isArray(resumeData.skills)
          ? resumeData.skills
          : resumeData.skills.split("\n").filter((s) => s.trim()),
        experience: Array.isArray(resumeData.experience)
          ? resumeData.experience
          : resumeData.experience.split("\n").filter((e) => e.trim()),
        projects: Array.isArray(resumeData.projects)
          ? resumeData.projects
          : resumeData.projects.split("\n").filter((p) => p.trim()),
        certifications: Array.isArray(resumeData.certifications)
          ? resumeData.certifications
          : resumeData.certifications.split("\n").filter((c) => c.trim()),
        awards: Array.isArray(resumeData.awards)
          ? resumeData.awards
          : resumeData.awards.split("\n").filter((a) => a.trim()),
      };

      const response = await axios.post(
        `${BACKEND_URL}/generate_resume`,
        {
          resume: formattedResumeData,
          match_score: matchScore,
          missing_keywords: missingKeywords,
        },
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "ATS_Optimized_Resume.pdf");
      document.body.appendChild(link);
      link.click();

      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (error) {
      console.error("Download error:", error);
      alert("Failed to generate resume");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="resume-enhancer">
      <div className="container">
        <div className="header">
          <h1>AI-Powered Resume Enhancer</h1>
          <p>Optimize Your Resume for ATS and Get Hired Faster!</p>
        </div>

        <button
          onClick={() => setManualMode(!manualMode)}
          className="mode-switch-btn"
        >
          {manualMode ? "Switch to File Upload" : "Switch to Manual Input"}
        </button>

        {!manualMode ? (
          <div className="upload-section-container">
            <UploadSection
              type="resume"
              label="Resume"
              accept=".pdf,.docx"
              description="Upload your current resume"
              handleFileUpload={handleFileUpload}
              handleFileRemove={handleFileRemove}
              handleFileView={handleFileView}
              uploaded={uploadedFiles.resume}
              currentFile={files.resume}
            />
            <UploadSection
              type="linkedin"
              label="LinkedIn Profile"
              accept=".pdf"
              description="Upload your LinkedIn profile as PDF"
              handleFileUpload={handleFileUpload}
              handleFileRemove={handleFileRemove}
              handleFileView={handleFileView}
              uploaded={uploadedFiles.linkedin}
              currentFile={files.linkedin}
            />
            <UploadSection
              type="jd"
              label="Job Description"
              accept=".pdf"
              description="Upload the job description for comparison"
              handleFileUpload={handleFileUpload}
              handleFileRemove={handleFileRemove}
              handleFileView={handleFileView}
              uploaded={uploadedFiles.jd}
              currentFile={files.jd}
            />
          </div>
        ) : (
          <div className="manual-input-section">
            <div className="manual-input-header">
              <h2>Manual Input</h2>
              <p>Enter your resume information manually</p>
            </div>
            <div className="manual-input-content">
              {Object.keys(resumeData).map((section) => (
                <div key={section} className="input-group">
                  <label className="input-label">{section.toUpperCase()}</label>
                  <TextareaAutosize
                    className="textarea-input"
                    value={
                      Array.isArray(resumeData[section])
                        ? resumeData[section].join("\n")
                        : resumeData[section]
                    }
                    onChange={(e) => handleManualInput(section, e.target.value)}
                    minRows={3}
                    placeholder={`Enter ${section.toLowerCase()} (one per line for lists)`}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {(matchScore !== null || missingKeywords.length > 0) && (
          <div className="analysis-section">
            <div className="analysis-header">
              <h2>Analysis Results</h2>
            </div>
            <div className="analysis-content">
              {matchScore !== null && (
                <div className="score-container">
                  <div className="score-header">
                    <span className="score-label">ATS Match Score</span>
                    <div>
                      <span className="score-value">{matchScore}%</span>
                      <span
                        className={`score-badge ${
                          matchScore >= 80
                            ? "excellent"
                            : matchScore >= 60
                            ? "good"
                            : "needs-improvement"
                        }`}
                      >
                        {matchScore >= 80
                          ? "Excellent Match"
                          : matchScore >= 60
                          ? "Good Match"
                          : "Needs Improvement"}
                      </span>
                    </div>
                  </div>
                  <div className="progress-bar">
                    <div
                      className={`progress-bar-fill ${
                        matchScore >= 80
                          ? "excellent"
                          : matchScore >= 60
                          ? "good"
                          : "needs-improvement"
                      }`}
                      style={{ width: `${matchScore}%` }}
                    ></div>
                  </div>
                </div>
              )}
              {missingKeywords.length > 0 && (
                <div className="keywords-container">
                  <h3 className="keywords-title">Recommended Keywords</h3>
                  <div className="keywords-list">
                    {missingKeywords.map((keyword, index) => (
                      <span key={index} className="keyword-tag">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Generate Button */}
        <div className="generate-section">
          <div className="generate-content">
            <button
              onClick={handleDownload}
              disabled={loading || (!uploadedFiles.resume && !manualMode)}
              className="generate-button"
            >
              {loading
                ? "Generating your optimized resume..."
                : "Generate ATS-Optimized Resume"}
            </button>
            <p className="generate-description">
              Your resume will be optimized for ATS systems and formatted
              professionally
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeEnhancer;
