# ResumeAI — API Documentation

**Base URL:** `http://localhost:5000/api`  
**Version:** 1.0  
**Format:** JSON

---

## Authentication

Most endpoints require the user to be logged in (session-based auth via Flask-Login).  
Login via the web interface at `/auth/login` before making authenticated requests.

---

## Endpoints

---

### GET `/api/jobs`

Returns all active job profiles.

**Auth required:** No

**Response:**
```json
{
  "success": true,
  "message": "",
  "data": [
    {
      "id": 1,
      "title": "Python Backend Developer",
      "category": "Backend",
      "description": "We need a solid Python developer...",
      "required_skills": ["Python", "Flask", "Django", "SQL", "REST API", "Git"],
      "preferred_skills": ["Docker", "Redis", "PostgreSQL", "AWS"],
      "min_experience": 1,
      "education_requirement": "Bachelor's in CS or related"
    }
  ]
}
```

---

### GET `/api/jobs/<job_id>`

Returns a single job profile by ID.

**Auth required:** No

**URL Params:** `job_id` (integer)

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "title": "Data Scientist",
    "category": "Data Science",
    "description": "...",
    "required_skills": ["Python", "Machine Learning", "Pandas"],
    "preferred_skills": ["TensorFlow", "PyTorch"],
    "min_experience": 1
  }
}
```

**Error (404):**
```json
{
  "success": false,
  "error": "Not found"
}
```

---

### GET `/api/my/resumes`

Returns all resumes uploaded by the currently logged-in user.

**Auth required:** Yes

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "original_name": "john_doe_resume.pdf",
      "file_type": "pdf",
      "uploaded_at": "2024-03-15T10:30:00",
      "file_size": 102400
    }
  ]
}
```

---

### GET `/api/my/analyses`

Returns all analyses for the logged-in user, newest first.

**Auth required:** Yes

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 7,
      "resume_id": 3,
      "job_id": 1,
      "overall_score": 73.5,
      "skill_match_score": 83.3,
      "experience_score": 70.0,
      "education_score": 100.0,
      "keyword_score": 61.2,
      "analyzed_at": "2024-03-15T10:35:00"
    }
  ]
}
```

---

### GET `/api/analysis/<analysis_id>`

Full detail of a single analysis including AI feedback.

**Auth required:** Yes (must own the analysis)

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 7,
    "overall_score": 73.5,
    "skill_match_score": 83.3,
    "experience_score": 70.0,
    "education_score": 100.0,
    "keyword_score": 61.2,
    "extracted_skills": ["Python", "Flask", "SQL", "Git", "Docker"],
    "matched_skills": ["Python", "Flask", "SQL", "Git"],
    "missing_skills": ["Django", "REST API"],
    "ai_summary": "The candidate has strong Python and Flask skills with 3 years of experience...",
    "suggestions": [
      "Add Django to your skill set — it's required for this role",
      "Mention REST API design explicitly in your experience section",
      "Quantify your achievements with numbers and impact metrics"
    ],
    "strengths": [
      "Strong Python backend experience",
      "Docker knowledge is a plus for this role"
    ],
    "weaknesses": [
      "Missing Django which is a core requirement",
      "Job description keywords could be better represented"
    ]
  }
}
```

---

### GET `/api/stats`

Summary statistics for the logged-in user.

**Auth required:** Yes

**Response:**
```json
{
  "success": true,
  "data": {
    "total_resumes": 4,
    "total_analyses": 9,
    "average_score": 67.3
  }
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "success": false,
  "message": "",
  "error": "Description of the error"
}
```

| HTTP Code | Meaning |
|-----------|---------|
| 200 | OK |
| 302 | Redirect (usually login redirect) |
| 400 | Bad request |
| 401 | Unauthorized |
| 404 | Not found |
| 500 | Server error |

---

## Rate Limiting

No rate limiting currently implemented. Planned for v2.

---

## Notes

- All timestamps are in UTC ISO 8601 format
- Skill arrays are plain string lists
- Scores are float values between 0 and 100
- File sizes are in bytes
