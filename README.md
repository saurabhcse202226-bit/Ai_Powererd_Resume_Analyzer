# 🧠 ResumeAI — AI-Powered Resume Analyzer

> Upload your resume. Pick a job. Get instant AI feedback on skill gaps, experience match, and ATS optimization.

Built with **Python + Flask + Claude AI** as a portfolio/internship project.

---

## 📸 Screenshots

| Landing Page | Dashboard | Analysis Result |
|---|---|---|
| Hero section with live mockup | Stats + recent analyses | Score breakdown + AI feedback |

*(See `/docs/screenshots/` for mockup references)*

---

## ✨ Features

- 📄 **Resume Upload** — PDF, DOCX, DOC, TXT support (up to 5MB)
- 🎯 **Skill Gap Analysis** — Matches your skills against job requirements
- 🤖 **AI Feedback** — Claude AI gives actionable suggestions
- 📊 **Detailed Scoring** — Skills (35%), Experience (25%), Education (20%), Keywords (20%)
- 🔍 **ATS Tips** — Helps you pass Applicant Tracking Systems
- 📁 **History Tracking** — Compare analyses over time
- 🌐 **REST API** — JSON endpoints for all core features
- 🔐 **Auth System** — Register/Login with session management

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/AI_Resume_Analyzer.git
cd AI_Resume_Analyzer
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root:

```env
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=your-claude-api-key-here
```

> **Note:** The app works without an Anthropic API key — it falls back to rule-based feedback automatically.

### 5. Run the app

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

**Demo login:** `demo@resumeai.com` / `demo1234`

---

## 📁 Project Structure

```
AI_Resume_Analyzer/
├── app.py                  # Flask app factory
├── config.py               # Config (DB, uploads, weights)
├── requirements.txt
├── README.md
│
├── models/
│   └── db.py               # SQLAlchemy models + seed data
│
├── routes/
│   ├── main.py             # Home, dashboard, jobs
│   ├── auth.py             # Login, register, logout
│   ├── resume.py           # Upload, analyze, result, history
│   └── api.py              # REST API endpoints
│
├── utils/
│   ├── extractor.py        # PDF/DOCX text extraction
│   ├── analyzer.py         # Skill matching + scoring logic
│   ├── ai_feedback.py      # Claude API integration
│   └── helpers.py          # File upload helpers
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── jobs.html
│   ├── about.html
│   ├── auth/               # login.html, register.html
│   └── resume/             # upload, analyze, result, history, my_resumes
│
├── static/
│   ├── css/style.css
│   └── js/main.js
│
├── database/
│   └── database.db         # SQLite (auto-created)
│
├── uploads/                # Uploaded resume files
├── tests/                  # pytest test files
└── docs/                   # Project report, API docs
```

---

## 🗄️ Database Schema

### Users
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | VARCHAR(100) | |
| email | VARCHAR(150) | Unique |
| password_hash | VARCHAR(256) | Werkzeug hashed |
| role | VARCHAR(20) | 'user' or 'recruiter' |
| created_at | DATETIME | |
| last_login | DATETIME | |

### Resumes
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| user_id | INTEGER FK | → users.id |
| filename | VARCHAR(255) | UUID-based saved name |
| original_name | VARCHAR(255) | Original uploaded name |
| file_type | VARCHAR(10) | pdf/docx/txt |
| raw_text | TEXT | Extracted text |
| uploaded_at | DATETIME | |
| file_size | INTEGER | Bytes |

### JobProfiles
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| title | VARCHAR(150) | |
| description | TEXT | |
| required_skills | TEXT | JSON array |
| preferred_skills | TEXT | JSON array |
| min_experience | INTEGER | Years |
| education_requirement | VARCHAR(100) | |
| category | VARCHAR(100) | Backend/Frontend/etc |

### Analyses
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| user_id | INTEGER FK | → users.id |
| resume_id | INTEGER FK | → resumes.id |
| job_id | INTEGER FK | → job_profiles.id |
| overall_score | FLOAT | 0–100 |
| skill_match_score | FLOAT | |
| experience_score | FLOAT | |
| education_score | FLOAT | |
| keyword_score | FLOAT | |
| extracted_skills | TEXT | JSON |
| matched_skills | TEXT | JSON |
| missing_skills | TEXT | JSON |
| ai_summary | TEXT | |
| suggestions | TEXT | JSON |
| strengths | TEXT | JSON |
| weaknesses | TEXT | JSON |
| analyzed_at | DATETIME | |

---

## 🌐 REST API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/jobs` | No | List all job profiles |
| GET | `/api/jobs/<id>` | No | Single job profile |
| GET | `/api/my/resumes` | Yes | Current user's resumes |
| GET | `/api/my/analyses` | Yes | Current user's analyses |
| GET | `/api/analysis/<id>` | Yes | Detailed analysis |
| GET | `/api/stats` | Yes | User statistics |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_analyzer.py::TestSkillExtraction::test_extracts_python PASSED
tests/test_analyzer.py::TestSkillExtraction::test_extracts_flask PASSED
...
23 passed in 1.4s
```

---

## ⚙️ Scoring Weights

| Component | Weight | How It's Calculated |
|-----------|--------|---------------------|
| Skill Match | 35% | Matched / Required skills × 100 |
| Experience | 25% | Found years vs required years |
| Education | 20% | Detected level vs required level |
| Keyword Density | 20% | Job description word overlap |

Weights can be changed in `config.py`.

---

## 🚢 Deployment

### Option 1 — Render (Free)

1. Push to GitHub
2. Create new Web Service on [render.com](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Add environment variables: `SECRET_KEY`, `ANTHROPIC_API_KEY`

### Option 2 — Railway

```bash
railway init
railway up
```

### Option 3 — Docker

```bash
docker build -t resumeai .
docker run -p 5000:5000 -e SECRET_KEY=xxx resumeai
```

---

## 🔮 Future Enhancements

- [ ] LinkedIn profile import
- [ ] Resume builder / editor
- [ ] Custom job description input (paste JD manually)
- [ ] Email reports with PDF summary
- [ ] Admin panel for managing job profiles
- [ ] Multi-language resume support
- [ ] Interview question suggestions based on gaps

---

## 📝 License

MIT — feel free to use for your own projects or learning.

---

## 👨‍💻 Author

Built by [Your Name] as a final year / internship portfolio project.  
Connect on [LinkedIn](https://linkedin.com/in/yourprofile) | [GitHub](https://github.com/yourusername)
