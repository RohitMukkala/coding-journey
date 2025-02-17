from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import pdfplumber
from docx import Document

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to extract text from PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = "".join([page.extract_text() + "\n" for page in pdf.pages if page.extract_text()])
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to generate ATS Resume PDF
def generate_resume_pdf(resume_data, jd_match):
    pdf_path = "./generated_resumes/ATS_Optimized_Resume.pdf"
    os.makedirs("./generated_resumes", exist_ok=True)
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>{resume_data.get('name', 'N/A')}</b>", styles["Title"]))
    elements.append(Paragraph(f"📧 {resume_data.get('email', 'N/A')} | 🔗 {resume_data.get('linkedin', 'N/A')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Experience
    elements.append(Paragraph("<b>Work Experience</b>", styles["Heading2"]))
    for exp in resume_data.get("experience", []):
        elements.append(Paragraph(f"• {exp}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Skills
    elements.append(Paragraph("<b>Skills</b>", styles["Heading2"]))
    all_skills = set(resume_data.get("skills", [])) | set(jd_match.get("missing_keywords", []))
    elements.append(Paragraph(", ".join(all_skills), styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"<b>Job Match Score: {jd_match.get('match_score', 'N/A')}%</b>", styles["Normal"]))
    doc.build(elements)
    return pdf_path

# ✅ Fix: Explicitly Handle OPTIONS Requests
@app.options("/generate_resume/")
async def options_generate_resume():
    return {"Allow": "POST, OPTIONS"}

# ✅ Fix: Ensure JSON Request Data Structure is Correct
@app.post("/generate_resume/")
async def generate_resume(request_data: dict):
    resume = request_data.get("resume", {})
    jd_match = request_data.get("jd_match", {})

    resume_path = generate_resume_pdf(resume, jd_match)
    return FileResponse(resume_path, filename="ATS_Optimized_Resume.pdf", media_type="application/pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
