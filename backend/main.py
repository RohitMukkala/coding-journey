from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict
import os
import spacy
import pdfplumber
import uuid  # Unique temp filenames
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor
from reportlab.platypus.paragraph import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT  # Add text alignment constants

app = FastAPI()

# ✅ CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")


# ✅ Extract text from PDF securely
def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            # Enhanced text cleaning
            text = text.replace('\x00', ' ')  # Remove null bytes
            text = ' '.join(text.split())  # Normalize whitespace
            print(f"Extracted text length: {len(text)}")
            print(f"First 200 characters: {text[:200]}")
            return text
    except Exception as e:
        print(f"PDF extraction error: {str(e)}")
        raise HTTPException(500, f"Error reading PDF file: {str(e)}")


# ✅ Extract text from DOCX with secure temp handling
async def extract_text_from_docx(file: UploadFile):
    temp_path = None
    try:
        temp_path = f"temp_{uuid.uuid4().hex}.docx"
        content = await file.read()
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        doc = Document(temp_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        print(f"Extracted DOCX text length: {len(text)}")
        print(f"First 200 characters: {text[:200]}")
        return text
    except Exception as e:
        print(f"DOCX extraction error: {str(e)}")
        raise HTTPException(500, f"Error reading DOCX file: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ✅ Resume Parsing with NLP
def extract_sections(text):
    if not text or not text.strip():
        print("Empty text received in extract_sections")
        return {}
        
    print(f"Processing text of length: {len(text)}")
    doc = nlp(text)
    
    # Initialize with empty values - no defaults
    sections = {
        "name": "",
        "email": "",
        "linkedin": "",
        "phone": "",
        "location": "",
        "education": [],
        "skills": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "awards": [],
        "publications": []
    }

    # Extract contact information using regex
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+'
    phone_pattern = r'\b(?:\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'
    location_pattern = r'(?:^|\n)(?:.*?,\s*)?([A-Za-z\s]+,\s*[A-Z]{2}(?:\s+\d{5})?|[A-Za-z\s]+,\s*[A-Z]{2,})'
    
    # Extract and log contact information
    emails = re.findall(email_pattern, text)
    if emails:
        sections["email"] = emails[0].strip()
        print(f"Found email: {sections['email']}")
    
    linkedin_urls = re.findall(linkedin_pattern, text)
    if linkedin_urls:
        url = linkedin_urls[0].strip()
        if not url.startswith('http'):
            url = "https://" + url
        sections["linkedin"] = url
        print(f"Found LinkedIn: {sections['linkedin']}")
    
    phones = re.findall(phone_pattern, text)
    if phones:
        sections["phone"] = phones[0].strip()
        print(f"Found phone: {sections['phone']}")
        
    locations = re.findall(location_pattern, text, re.MULTILINE)
    if locations:
        sections["location"] = locations[0].strip()
        print(f"Found location: {sections['location']}")

    # Extract name with improved logic
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    print(f"Found {len(lines)} non-empty lines")
    print(f"First 5 lines: {lines[:5]}")
    
    for line in lines[:5]:  # Check first 5 lines for name
        print(f"Checking line for name: {line}")
        # Skip lines that are too long (likely not a name)
        if len(line) > 50:
            print(f"Skipping line (too long): {line}")
            continue
            
        # Check if line looks like a name
        words = line.split()
        if 2 <= len(words) <= 4 and all(word[0].isupper() for word in words):
            # Verify it's not a header or contains contact info
            if not re.search(email_pattern, line) and \
               not re.search(phone_pattern, line) and \
               not re.search(location_pattern, line) and \
               not any(keyword in line.lower() for keyword in ["resume", "cv", "curriculum", "vitae", "profile"]):
                sections["name"] = line.strip()
                print(f"Found name: {sections['name']}")
                break

    # Enhanced section detection with more keywords
    current_section = None
    section_content = []
    
    section_keywords = {
        "education": ["education", "academic background", "academic qualification", "academic history", "degree"],
        "skills": ["skills", "technical skills", "technologies", "competencies", "expertise", "proficiencies", "tools"],
        "experience": ["experience", "work experience", "employment history", "professional experience", "work history"],
        "projects": ["projects", "project experience", "key projects", "personal projects", "academic projects"],
        "certifications": ["certifications", "certificates", "professional certifications", "credentials"],
        "awards": ["awards", "honors", "achievements", "recognition", "accomplishments"],
        "publications": ["publications", "research papers", "papers", "articles", "journals"]
    }

    # Process text line by line with improved section detection
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a section header
        lower_line = line.lower()
        found_section = False
        
        # Look for section headers with improved detection
        for section, keywords in section_keywords.items():
            # Check if line contains section keyword
            if any(keyword in lower_line for keyword in keywords):
                # Verify it's likely a header (short line, possibly followed by separator)
                if len(line) < 50 and (
                    line.endswith(':') or 
                    line.upper() == line or 
                    (i < len(lines)-1 and not lines[i+1].strip())
                ):
                    if current_section and section_content:
                        sections[current_section].extend(section_content)
                    current_section = section
                    section_content = []
                    found_section = True
                    break
                
        if not found_section and current_section and line:
            # Clean and process the line content
            clean_line = line.strip('•-→⚫⚪●○◆◇■□▪▫⬤∙⋄⚬⭐✦✧✪✫✬✭✮✯✰⭐★☆✡︎✦✧✩✪✫✬✭✮✯✰⭐*⁕⁎⁑⋆∗⚝✢✣✤✥✱✲✳✴✵✶✷✸✹✺✻✼✽✾✿❀❁❂❃❄❅❆❇❈❉❊❋⭐ \t')
            if clean_line:
                if current_section == "skills":
                    # Handle various skill separators
                    separators = [',', '|', '•', '|', '/', ';']
                    for sep in separators:
                        if sep in clean_line:
                            skills = [skill.strip() for skill in clean_line.split(sep)]
                            section_content.extend(filter(None, skills))
                            break
                    else:
                        section_content.append(clean_line)
                else:
                    section_content.append(clean_line)

    # Add the last section's content
    if current_section and section_content:
        sections[current_section].extend(section_content)
        print(f"Added final section {current_section} with {len(section_content)} items")

    # Clean up sections
    for section in sections:
        if isinstance(sections[section], list):
            # Remove duplicates while preserving order
            seen = set()
            sections[section] = [x for x in sections[section] if not (x.lower() in seen or seen.add(x.lower()))]
            # Remove empty items and clean up
            sections[section] = [x.strip() for x in sections[section] if x.strip() and len(x.strip()) > 1]
            if sections[section]:
                print(f"Final {section} section has {len(sections[section])} items")

    # Remove empty sections
    sections = {k: v for k, v in sections.items() if v}
    print(f"Final sections found: {list(sections.keys())}")

    # Validate extracted content
    if not any(sections.values()):
        return {}

    return sections


# ✅ Upload LinkedIn Resume (PDF)
@app.post("/upload/linkedin/")
async def upload_linkedin(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Only PDF files are allowed for LinkedIn profile")
            
        file.file.seek(0)
        text = extract_text_from_pdf(file.file)
        if not text.strip():
            raise HTTPException(400, "Could not extract text from the PDF file")
            
        sections = extract_sections(text)
        if not any(sections.values()):
            raise HTTPException(400, "No valid content could be extracted from the file")
            
        return {"data": sections}
    except Exception as e:
        raise HTTPException(500, f"Error processing LinkedIn file: {str(e)}")


# ✅ Upload Resume (PDF/DOCX)
@app.post("/upload/resume/")
async def upload_resume(file: UploadFile = File(...)):
    try:
        filename = file.filename.lower()
        print(f"Processing resume file: {filename}")
        
        if not (filename.endswith('.pdf') or filename.endswith('.docx')):
            raise HTTPException(400, "Invalid file format. Please upload a PDF or DOCX file.")

        file.file.seek(0)
        text = ""
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file.file)
        else:
            text = await extract_text_from_docx(file)
            
        if not text.strip():
            print("No text extracted from file")
            raise HTTPException(400, "Could not extract text from the file")
            
        sections = extract_sections(text)
        if not any(sections.values()):
            print("No sections extracted from text")
            raise HTTPException(400, "No valid content could be extracted from the file")
            
        return {"data": sections}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        raise HTTPException(500, f"Error processing resume: {str(e)}")


# ✅ Define Request Model for JD Matching
class ResumeJDRequest(BaseModel):
    resume: Dict[str, List[str]]
    jd: str


# ✅ Match Resume with Job Description
@app.post("/match_jd/")
async def match_jd(request: ResumeJDRequest):
    try:
        resume = request.resume
        jd = request.jd

        if not resume or not jd:
            raise HTTPException(status_code=400, detail="Resume and JD cannot be empty.")

        # Process JD with NLP
        jd_doc = nlp(jd)
        
        # Enhanced keyword extraction from JD
        jd_keywords = []
        # Extract noun chunks for multi-word terms
        for chunk in jd_doc.noun_chunks:
            if chunk.root.pos_ in ['NOUN', 'PROPN'] and not chunk.root.is_stop:
                jd_keywords.append(chunk.text.lower())
        
        # Add single-word technical terms
        for token in jd_doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                if token.text.lower() not in [k.lower() for k in jd_keywords]:
                    jd_keywords.append(token.lemma_.lower())
        
        # Get skills and experience from resume
        resume_sections = []
        for section in ["skills", "experience", "education", "certifications"]:
            if section in resume:
                if isinstance(resume[section], list):
                    resume_sections.extend(resume[section])
                elif isinstance(resume[section], str):
                    resume_sections.append(resume[section])
        
        resume_text = " ".join(resume_sections)
        resume_doc = nlp(resume_text)
        
        # Enhanced resume keyword extraction
        resume_keywords = []
        # Extract noun chunks for multi-word terms
        for chunk in resume_doc.noun_chunks:
            if chunk.root.pos_ in ['NOUN', 'PROPN'] and not chunk.root.is_stop:
                resume_keywords.append(chunk.text.lower())
        
        # Add single-word technical terms
        for token in resume_doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                if token.text.lower() not in [k.lower() for k in resume_keywords]:
                    resume_keywords.append(token.lemma_.lower())
        
        # Contextual matching using TF-IDF with n-grams
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),  # Include both unigrams and bigrams
            stop_words='english',
            max_features=1000  # Limit features to most important ones
        )
        
        # Transform texts to TF-IDF matrices
        tfidf_matrix = vectorizer.fit_transform([
            " ".join(resume_keywords),
            " ".join(jd_keywords)
        ])
        
        # Compute similarity score
        match_score = (tfidf_matrix[0] @ tfidf_matrix[1].T).toarray()[0][0] * 100
        
        # Find missing keywords with context
        missing_keywords = []
        for keyword in jd_keywords:
            if not any(keyword.lower() in rk.lower() for rk in resume_keywords):
                missing_keywords.append(keyword)
        
        # Sort missing keywords by importance
        missing_keywords_tfidf = vectorizer.transform([" ".join(missing_keywords)])
        keyword_scores = missing_keywords_tfidf.toarray()[0]
        sorted_missing = [kw for _, kw in sorted(zip(keyword_scores, missing_keywords), reverse=True)]
        
        # Generate contextual recommendations
        recommendations = []
        
        # Skills-based recommendations
        if any("skill" in kw.lower() for kw in sorted_missing[:5]):
            recommendations.append("Focus on adding relevant technical skills mentioned in the job description")
        
        # Experience-based recommendations
        if any("experience" in kw.lower() for kw in sorted_missing[:5]):
            recommendations.append("Highlight relevant work experience that matches job requirements")
        
        # Education-based recommendations
        if any(kw.lower() in ["degree", "education", "qualification"] for kw in sorted_missing[:5]):
            recommendations.append("Ensure your educational qualifications are clearly listed")
        
        # Certification-based recommendations
        if any("certification" in kw.lower() for kw in sorted_missing[:5]):
            recommendations.append("Add relevant certifications that align with job requirements")
        
        # Add general recommendations
        recommendations.extend([
            "Incorporate industry-specific terminology from the job description",
            "Highlight quantifiable achievements that demonstrate required skills",
            "Align your technical skills section with the required technologies",
            "Use specific keywords from the job description in your experience section"
        ])

        return {
            "match_score": round(match_score, 2),
            "missing_keywords": sorted_missing[:15],  # Return top 15 missing keywords
            "enhanced_recommendations": recommendations
        }
    
    except Exception as e:
        raise HTTPException(500, f"JD matching failed: {str(e)}")


# ✅ Generate Resume PDF
@app.post("/generate_resume/")
async def generate_resume(data: dict):
    try:
        # Get the resume data from the request
        resume_data = data.get("resume", {})
        
        # Validate required fields
        if not resume_data:
            raise HTTPException(400, "Resume data is required")
        
        # Ensure we have at least some content
        if not any(resume_data.get(field) for field in ["name", "email", "experience", "skills", "education"]):
            raise HTTPException(400, "Resume must contain at least basic information (name, contact, skills, or experience)")
        
        pdf_path = f"generated_resume_{uuid.uuid4().hex}.pdf"
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        # Custom Styles
        styles.add(ParagraphStyle(
            name='Header',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=HexColor('#2c5282')
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            leading=14,
            spaceBefore=12,
            spaceAfter=6,
            textColor=HexColor('#1a365d')
        ))

        # Header Section with name
        name = resume_data.get("name", "").strip()
        if name:
            elements.append(Paragraph(name, styles['Header']))
            elements.append(Spacer(1, 12))

        # Contact Information
        contact_info = []
        for field in ["email", "phone", "linkedin", "location"]:
            if resume_data.get(field):
                contact_info.append(resume_data[field].strip())
            
        if contact_info:
            contact_table = Table([
                [Paragraph(", ".join(contact_info), styles['Normal'])]
            ], colWidths=[550])
            contact_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6)
            ]))
            elements.append(contact_table)
            elements.append(Spacer(1, 24))

        # Skills Section
        if resume_data.get("skills"):
            elements.append(Paragraph("SKILLS", styles['SectionHeader']))
            skills = resume_data["skills"]
            if isinstance(skills, str):
                skills = [skill.strip() for skill in skills.split('\n') if skill.strip()]
            
            # Group skills by type if possible
            technical_skills = []
            soft_skills = []
            
            for skill in skills:
                # Simple heuristic: if skill contains technical keywords, it's technical
                technical_keywords = ['python', 'java', 'c++', 'javascript', 'react', 'node', 'aws', 'sql', 'git', 'docker']
                is_technical = any(keyword in skill.lower() for keyword in technical_keywords)
                if is_technical:
                    technical_skills.append(skill)
                else:
                    soft_skills.append(skill)
            
            skills_data = []
            if technical_skills:
                skills_data.append(["Technical Skills:", ", ".join(technical_skills)])
            if soft_skills:
                skills_data.append(["Professional Skills:", ", ".join(soft_skills)])
            
            if skills_data:
                skills_table = Table(skills_data, colWidths=[120, 430])
                skills_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6)
                ]))
                elements.append(skills_table)
                elements.append(Spacer(1, 12))

        # Experience Section
        if resume_data.get("experience"):
            elements.append(Paragraph("EXPERIENCE", styles['SectionHeader']))
            experiences = resume_data["experience"]
            if isinstance(experiences, str):
                experiences = [exp.strip() for exp in experiences.split('\n') if exp.strip()]
            
            for exp in experiences:
                # Try to parse company and role if separated by |
                if '|' in exp:
                    parts = exp.split('|')
                    if len(parts) >= 2:
                        exp_table = Table([
                            [
                                Paragraph(f"<b>{parts[0].strip()}</b>", styles['Normal']),
                                Paragraph(f"<i>{parts[1].strip()}</i>", styles['Normal'])
                            ]
                        ], colWidths=[275, 275])
                        exp_table.setStyle(TableStyle([
                            ('ALIGN', (0,0), (0,0), 'LEFT'),
                            ('ALIGN', (1,0), (1,0), 'RIGHT'),
                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 4)
                        ]))
                        elements.append(exp_table)
                        
                        # Add any additional parts as bullet points
                        for detail in parts[2:]:
                            if detail.strip():
                                elements.append(Paragraph(f"• {detail.strip()}", styles['Normal']))
                else:
                    elements.append(Paragraph(f"• {exp}", styles['Normal']))
            elements.append(Spacer(1, 12))

        # Education Section
        if resume_data.get("education"):
            elements.append(Paragraph("EDUCATION", styles['SectionHeader']))
            education = resume_data["education"]
            if isinstance(education, str):
                education = [edu.strip() for edu in education.split('\n') if edu.strip()]
            
            for edu in education:
                if '|' in edu:
                    parts = edu.split('|')
                    edu_table = Table([
                        [
                            Paragraph(f"<b>{parts[0].strip()}</b>", styles['Normal']),
                            Paragraph(parts[1].strip() if len(parts) > 1 else "", styles['Normal'])
                        ]
                    ], colWidths=[275, 275])
                    edu_table.setStyle(TableStyle([
                        ('ALIGN', (0,0), (0,0), 'LEFT'),
                        ('ALIGN', (1,0), (1,0), 'RIGHT'),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 4)
                    ]))
                    elements.append(edu_table)
                else:
                    elements.append(Paragraph(f"• {edu}", styles['Normal']))
            elements.append(Spacer(1, 12))

        # Projects Section
        if resume_data.get("projects"):
            elements.append(Paragraph("PROJECTS", styles['SectionHeader']))
            projects = resume_data["projects"]
            if isinstance(projects, str):
                projects = [proj.strip() for proj in projects.split('\n') if proj.strip()]
            
            for project in projects:
                if '|' in project:
                    parts = project.split('|')
                    elements.append(Paragraph(f"<b>{parts[0].strip()}</b>", styles['Normal']))
                    for detail in parts[1:]:
                        if detail.strip():
                            elements.append(Paragraph(f"• {detail.strip()}", styles['Normal']))
                else:
                    elements.append(Paragraph(f"• {project}", styles['Normal']))
            elements.append(Spacer(1, 12))

        # Optional Sections
        for section, header in [
            ("certifications", "CERTIFICATIONS"),
            ("awards", "AWARDS & ACHIEVEMENTS"),
            ("publications", "PUBLICATIONS")
        ]:
            if resume_data.get(section):
                elements.append(Paragraph(header, styles['SectionHeader']))
                items = resume_data[section]
                if isinstance(items, str):
                    items = [item.strip() for item in items.split('\n') if item.strip()]
                
                for item in items:
                    elements.append(Paragraph(f"• {item}", styles['Normal']))
                elements.append(Spacer(1, 12))

        # Build PDF
        doc.build(elements)
        
        # Return file and clean up
        response = FileResponse(pdf_path, filename="ATS_Optimized_Resume.pdf")
        
        # Clean up temporary file
        def cleanup_file():
            try:
                os.remove(pdf_path)
            except:
                pass
                
        response.background = cleanup_file
        return response

    except Exception as e:
        if 'pdf_path' in locals() and os.path.exists(pdf_path):
            os.remove(pdf_path)
        raise HTTPException(500, f"Resume generation failed: {str(e)}")

# ✅ Upload Job Description (PDF)
@app.post("/upload/jd")
async def upload_jd(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Only PDF files are allowed for Job Description.")
        
        file.file.seek(0)
        text = extract_text_from_pdf(file.file)
        return {"data": text}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, f"Error processing JD file: {str(e)}")
# ✅ Run with:
# uvicorn main:app --reload
