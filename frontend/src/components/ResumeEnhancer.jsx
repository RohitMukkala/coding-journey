import React, { useState } from "react";
import axios from "axios";
import TextareaAutosize from "react-textarea-autosize";

const ResumeEnhancer = () => {
  const [resumeData, setResumeData] = useState({
    name: "John Doe",
    email: "johndoe@gmail.com",
    linkedin: "https://linkedin.com/in/johndoe",
    experience: ["Software Engineer at XYZ", "Intern at ABC"],
    skills: ["Python", "Java", "Machine Learning"],
    projects: ["AI Chatbot", "Resume Enhancer"],
  });

  const handleFieldChange = (section, index, value) => {
    setResumeData((prevData) => {
      const newData = { ...prevData };
      if (Array.isArray(newData[section])) {
        newData[section][index] = value;
      } else {
        newData[section] = value;
      }
      return newData;
    });
  };

  // ✅ Add the function here (before return)
  const handleDownloadResume = async () => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/generate_resume/",
        {
          resume: resumeData,
          jd_match: { match_score: 85, missing_keywords: ["Deep Learning"] },
        },
        {
          headers: { "Content-Type": "application/json" }, // ✅ Ensure proper JSON header
          responseType: "blob", // ✅ Needed for file downloads
        }
      );

      // ✅ Create a downloadable link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "ATS_Optimized_Resume.pdf");
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to generate resume.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">
        Edit Your Resume Before Download
      </h2>
      {Object.keys(resumeData).map((section) => (
        <div key={section} className="mb-4">
          <h4 className="font-semibold">
            {section.charAt(0).toUpperCase() + section.slice(1)}
          </h4>
          <TextareaAutosize
            className="w-full p-2 border rounded-md"
            value={resumeData[section]}
            onChange={(e) => handleFieldChange(section, 0, e.target.value)}
          />
        </div>
      ))}
      <button
        onClick={handleDownloadResume} // ✅ Call the function here
        className="px-4 py-2 bg-green-600 text-white rounded-md mt-4"
      >
        Download ATS Resume
      </button>
    </div>
  );
};

export default ResumeEnhancer;
