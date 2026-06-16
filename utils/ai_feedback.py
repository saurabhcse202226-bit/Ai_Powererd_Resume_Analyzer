"""
utils/ai_feedback.py

Uses Claude to generate smart feedback on resumes.
Falls back to rule-based suggestions if API key is missing.
"""

import anthropic
import json
import os
from config import Config


def generate_ai_feedback(resume_text, job_title, matched_skills, missing_skills, overall_score):
    """Get AI-powered resume feedback from Claude"""

    api_key = Config.ANTHROPIC_API_KEY
    if not api_key:
        return _fallback_feedback(matched_skills, missing_skills, overall_score, job_title)

    try:
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""You are an experienced HR professional and resume expert. Analyze this resume for the position of "{job_title}".

Resume text:
{resume_text[:3000]}

Matched skills: {', '.join(matched_skills[:10])}
Missing skills: {', '.join(missing_skills[:10])}
Overall match score: {overall_score}/100

Provide feedback in this exact JSON format (respond ONLY with JSON, no extra text):
{{
  "summary": "2-3 sentence summary of the candidate's profile",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "suggestions": [
    "Specific actionable suggestion 1",
    "Specific actionable suggestion 2", 
    "Specific actionable suggestion 3",
    "Specific actionable suggestion 4"
  ],
  "ats_tips": ["ATS optimization tip 1", "ATS optimization tip 2"]
}}

Be specific, practical, and constructive. Mention actual skills and content from the resume where possible."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = message.content[0].text.strip()
        # sometimes it adds markdown code blocks
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        raw = raw.strip()

        feedback = json.loads(raw)
        return feedback

    except json.JSONDecodeError:
        return _fallback_feedback(matched_skills, missing_skills, overall_score, job_title)
    except anthropic.APIError as e:
        print(f"Anthropic API error: {e}")
        return _fallback_feedback(matched_skills, missing_skills, overall_score, job_title)
    except Exception as e:
        print(f"AI feedback error: {e}")
        return _fallback_feedback(matched_skills, missing_skills, overall_score, job_title)


def _fallback_feedback(matched_skills, missing_skills, score, job_title):
    """Rule-based feedback when API isn't available"""
    strengths = []
    suggestions = []
    weaknesses = []

    if len(matched_skills) >= 5:
        strengths.append(f"Strong skill alignment with {len(matched_skills)} matching skills including {', '.join(matched_skills[:3])}")
    elif len(matched_skills) > 0:
        strengths.append(f"Has foundational skills: {', '.join(matched_skills[:3])}")

    if score >= 70:
        strengths.append("Good overall match for the role")
    elif score >= 50:
        strengths.append("Meets basic requirements for the position")

    if missing_skills:
        weaknesses.append(f"Missing key skills: {', '.join(missing_skills[:4])}")
        suggestions.append(f"Learn or add these missing skills to your resume: {', '.join(missing_skills[:3])}")

    if score < 60:
        suggestions.append("Consider tailoring your resume more specifically for this role")

    suggestions.append("Quantify your achievements with numbers and metrics where possible")
    suggestions.append("Use action verbs at the start of each bullet point")
    suggestions.append("Keep your resume to 1-2 pages with relevant content only")

    return {
        "summary": f"The candidate has a {score}/100 match for the {job_title} role with {len(matched_skills)} out of the required skills present.",
        "strengths": strengths if strengths else ["Resume has been uploaded successfully"],
        "weaknesses": weaknesses if weaknesses else ["Could improve skill visibility"],
        "suggestions": suggestions,
        "ats_tips": [
            "Include exact keywords from the job description",
            "Use standard section headings like 'Experience', 'Education', 'Skills'"
        ]
    }
