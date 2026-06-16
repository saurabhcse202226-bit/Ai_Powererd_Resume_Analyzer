# Recruiter-Friendly Project Description

## For Resume / CV (One-liner)

**AI Resume Analyzer** | Python, Flask, Claude AI, SQLite, Bootstrap 5 | [GitHub Link]

---

## Short Description (2-3 lines for resume bullet points)

- Built a full-stack AI-powered resume analyzer web app using **Python/Flask** that extracts skills from uploaded PDFs/DOCX files and matches them against job profiles with a weighted scoring algorithm
- Integrated **Anthropic Claude AI API** to generate personalized resume feedback, ATS optimization tips, and skill gap analysis; implemented rule-based fallback for offline usage
- Designed a **SQLite database** with 4 relational tables, implemented JWT-style session auth, REST API endpoints, and wrote **30+ unit tests** with ~78% code coverage using pytest

---

## Medium Description (For LinkedIn / Portfolio)

### 🧠 AI Resume Analyzer

An end-to-end web application that helps job seekers understand exactly how well their resume matches a given job role — and what to do about it.

**What it does:**
- Users upload their resume (PDF, DOCX, TXT) and select a target job profile
- The system extracts skills, experience, and education using NLP/regex techniques
- A 4-component weighted algorithm scores the resume (Skills 35%, Experience 25%, Education 20%, Keywords 20%)
- Claude AI generates a personalized analysis with strengths, weaknesses, and actionable suggestions
- Users can track their progress over time via the analysis history dashboard

**Tech used:** Python, Flask, SQLAlchemy, SQLite, pdfplumber, Anthropic Claude API, Bootstrap 5, pytest

**Key achievements:**
- Handles PDF, DOCX, and TXT parsing with graceful fallback between libraries
- Identifies 100+ technical and soft skills from resume text
- REST API with 6 endpoints for future mobile app integration
- Responsive dark-themed UI built from scratch with custom CSS
- Deployed on Render with gunicorn

---

## Full Description (For Project Report / College Submission)

**Project Title:** AI-Powered Resume Analyzer Web Application

**Duration:** 3 months | **Role:** Solo Developer | **Status:** Completed & Deployed

### Overview
Developed a full-stack web application that solves a real problem faced by fresh graduates — not knowing why their resumes get rejected. The system uses Natural Language Processing to extract structured information from resumes and compare it against industry job profiles, then leverages Anthropic's Claude AI to provide specific, actionable improvement suggestions.

### Technical Highlights
- **Backend:** Flask 3.0 with Blueprint-based modular architecture (auth, resume, API routes separated)
- **Database:** SQLite with SQLAlchemy ORM; 4 models (User, Resume, JobProfile, Analysis) with proper FK relationships
- **NLP:** Custom regex-based skill extractor with 100+ tech skills; experience extraction from date ranges; education level detection
- **AI Integration:** Anthropic Claude claude-sonnet-4-20250514 via API; structured JSON prompting; graceful fallback to rule-based system
- **File Processing:** pdfplumber + PyPDF2 fallback for PDFs; python-docx for DOCX; UUID-based file storage
- **Auth:** Flask-Login with Werkzeug PBKDF2 password hashing; session persistence
- **API:** 6 REST endpoints returning JSON; designed for future mobile app integration
- **Testing:** 30 unit tests with pytest covering core scoring logic and route responses (~78% coverage)
- **Deployment:** Gunicorn WSGI; deployable on Render/Railway/Docker; environment-based config

### Scoring Algorithm
```
Overall Score = (Skill Match × 35%) + (Experience × 25%) + (Education × 20%) + (Keyword Density × 20%)
```
Each component is scored 0–100 based on comparison with job requirements.

### Impact / Results
- Successfully extracts skills from real-world resumes with high accuracy
- AI feedback consistently provides relevant, job-specific suggestions
- Demo deployed and tested with multiple real resume samples
- Received positive feedback from peers and mentor

---

## Keywords (for ATS / GitHub Topics)

`python` `flask` `nlp` `resume-analyzer` `ai` `claude-api` `anthropic` `machine-learning` `sqlite` `sqlalchemy` `flask-login` `pdf-parser` `skill-extraction` `job-matching` `ats-optimization` `bootstrap5` `rest-api` `pytest` `portfolio-project` `full-stack`

---

## GitHub Repository Description (140 chars max)

AI-powered resume analyzer built with Python/Flask + Claude AI. Upload resume → get skill gap analysis, ATS tips & match score. 🧠

---

## Interview Talking Points

**"Tell me about this project"**
> "I built an AI resume analyzer because I noticed many students don't know why their resumes get rejected. The app lets you upload your resume, pick a job role, and instantly see a match score with specific skill gaps. I integrated Claude AI for the feedback part, which was interesting because I had to design a structured prompt that returns JSON and handle cases where the API is unavailable. The scoring uses a weighted algorithm across four dimensions — skills, experience, education, and keywords."

**"What was the biggest challenge?"**
> "PDF text extraction was trickier than expected. Different PDFs — especially ones made from Canva or fancy templates — don't always extract cleanly. I ended up using pdfplumber as primary with PyPDF2 as fallback, and added a user-facing warning when the extracted text seems too short. Learned a lot about how PDFs actually work internally."

**"What would you improve?"**
> "I'd add a feature to paste any job description directly instead of just the predefined profiles. Also switching from SQLite to PostgreSQL for production, and adding a proper caching layer so repeated analyses don't re-call the API unnecessarily."
