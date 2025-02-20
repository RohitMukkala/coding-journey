# ✅ Run with:
# uvicorn main:app --reload

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import spacy
import pdfplumber
import uuid
import requests
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus.paragraph import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from routes import coding_profiles
from database import engine, SessionLocal
from models import Base, User as DBUser
from schemas import UserCreate, Token, UserUpdate, User
from auth import hash_password, create_access_token, verify_password, get_current_user
from githubstats import app as github_app
from datetime import datetime, timedelta

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication routes
@app.post("/signup", response_model=Token)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    existing_username = db.query(DBUser).filter(DBUser.username == user_data.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Check if email already exists
    existing_email = db.query(DBUser).filter(DBUser.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        # Hash the password
        hashed_password = hash_password(user_data.password)

        # Create new user
        new_user = DBUser(username=user_data.username, email=user_data.email, password_hash=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate JWT Token
        access_token = create_access_token({"sub": new_user.email})

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred during signup: {str(e)}")

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(DBUser).filter(DBUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate JWT Token
    access_token = create_access_token({"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def read_users_me(current_user: DBUser = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "github_username": current_user.github_username,
        "leetcode_username": current_user.leetcode_username,
        "codechef_username": current_user.codechef_username,
        "codeforces_username": current_user.codeforces_username,
        "profile_picture": current_user.profile_picture
    }

# Coding Profiles Routes
def get_leetcode_data(username: str) -> Dict[str, Any]:
    url = "https://leetcode.com/graphql"
    headers = {"Content-Type": "application/json"}
    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
        tagProblemCounts {
          advanced {
            tagName
            problemsSolved
          }
        }
      }
    }
    """
    variables = {"username": username}
    
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if "data" in data and data["data"]["matchedUser"] is not None:
            user_data = data["data"]["matchedUser"]
            submissions = user_data["submitStatsGlobal"]["acSubmissionNum"]
            
            submission_data = {
                sub["difficulty"].lower(): sub["count"] 
                for sub in submissions
            }
            
            return {
                "totalSolved": submission_data.get("all", 0),
                "easySolved": submission_data.get("easy", 0),
                "mediumSolved": submission_data.get("medium", 0),
                "hardSolved": submission_data.get("hard", 0),
                "easyPercentage": round(submission_data.get("easy", 0) / submission_data.get("all", 1) * 100, 1),
                "mediumPercentage": round(submission_data.get("medium", 0) / submission_data.get("all", 1) * 100, 1),
                "hardPercentage": round(submission_data.get("hard", 0) / submission_data.get("all", 1) * 100, 1)
            }
        else:
            raise HTTPException(status_code=404, detail="LeetCode user not found")
            
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch LeetCode data: {str(e)}")

def get_codeforces_data(username: str) -> Dict[str, Any]:
    user_status_url = f"https://codeforces.com/api/user.status?handle={username}"
    user_rating_url = f"https://codeforces.com/api/user.rating?handle={username}"

    try:
        user_status_response = requests.get(user_status_url)
        user_status_response.raise_for_status()
        user_status_data = user_status_response.json()
        
        if user_status_data.get('status') != 'OK':
            raise HTTPException(status_code=404, detail=user_status_data.get('comment', 'Codeforces user not found'))

        solved_problems = {}
        for submission in user_status_data['result']:
            if submission.get('verdict') == 'OK':
                problem = submission['problem']
                problem_id = f"{problem['contestId']}{problem['index']}"
                if problem_id not in solved_problems:
                    index = problem.get('index', '')
                    name = problem.get('name', 'Unknown')
                    full_name = f"{index}. {name}" if index else name
                    solved_problems[problem_id] = {
                        'name': full_name,
                        'difficulty': problem.get('rating', 'No rating')
                    }

        user_rating_response = requests.get(user_rating_url)
        user_rating_response.raise_for_status()
        user_rating_data = user_rating_response.json()
        
        if user_rating_data.get('status') != 'OK':
            raise HTTPException(status_code=404, detail=user_rating_data.get('comment', 'Codeforces user not found'))

        rating_history = user_rating_data['result']
        current_rating = rating_history[-1]['newRating'] if rating_history else None

        return {
            "problems_solved": len(solved_problems),
            "current_rating": current_rating,
            "example_problems": list(solved_problems.values())[:5]
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Codeforces data: {str(e)}")

def get_codechef_data(username: str) -> Dict[str, Any]:
    url = f"https://codechef-api.vercel.app/handle/{username}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            raise HTTPException(status_code=404, detail="CodeChef user not found")
            
        return {
            "currentRating": data.get("currentRating"),
            "highestRating": data.get("highestRating"),
            "globalRank": data.get("globalRank"),
            "countryRank": data.get("countryRank"),
            "stars": data.get("stars")
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch CodeChef data: {str(e)}")

@app.get("/api/leetcode/{username}")
async def get_leetcode_stats(username: str):
    try:
        return get_leetcode_data(username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/codeforces/{username}")
async def get_codeforces_stats(username: str):
    try:
        return get_codeforces_data(username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/codechef/{username}")
async def get_codechef_stats(username: str):
    try:
        return get_codechef_data(username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# Add coding profiles routes
app.include_router(coding_profiles.router, prefix="/api", tags=["coding_profiles"])

@app.put("/settings", response_model=User)
async def update_settings(
    user_data: UserUpdate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(DBUser).filter(DBUser.id == current_user.id).first()
    
    # Check if new username is taken (if username is being updated)
    if user_data.username and user_data.username != user.username:
        existing_user = db.query(DBUser).filter(DBUser.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Update user fields
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/settings/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/profile_pictures"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
            
        # Update user's profile picture URL
        user = db.query(DBUser).filter(DBUser.id == current_user.id).first()
        user.profile_picture = f"/uploads/profile_pictures/{filename}"
        db.commit()
        
        return {"profile_picture": user.profile_picture}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount the GitHub routes
app.mount("/api/github", github_app)


