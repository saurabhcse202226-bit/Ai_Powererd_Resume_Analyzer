"""
utils/analyzer.py

Core resume analysis logic. Handles skill extraction,
scoring, and matching against job profiles.

TODO: maybe add weighted TF-IDF scoring later
"""

import re
import json
from config import Config

# comprehensive skill list - probably should move this to DB later
TECH_SKILLS = [
    # languages
    'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'C', 'Go', 'Rust',
    'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Bash',
    'Shell', 'PowerShell', 'Dart', 'Lua',

    # web
    'HTML', 'CSS', 'React', 'Angular', 'Vue', 'Next.js', 'Node.js', 'Express',
    'Django', 'Flask', 'FastAPI', 'Spring', 'Spring Boot', 'Laravel', 'Ruby on Rails',
    'ASP.NET', 'jQuery', 'Bootstrap', 'Tailwind CSS', 'SASS', 'REST API', 'GraphQL',
    'WebSocket',

    # data / ml
    'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'TensorFlow',
    'PyTorch', 'Keras', 'scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn',
    'Spark', 'Hadoop', 'Tableau', 'Power BI', 'Data Analysis', 'Data Science',
    'Statistics', 'MLflow', 'Hugging Face',

    # databases
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Redis', 'Oracle',
    'Cassandra', 'DynamoDB', 'Elasticsearch', 'Firebase', 'MariaDB',

    # devops / cloud
    'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure', 'CI/CD', 'Jenkins', 'GitHub Actions',
    'Terraform', 'Ansible', 'Linux', 'Nginx', 'Git', 'GitHub', 'GitLab', 'Bitbucket',

    # other tools
    'Jira', 'Agile', 'Scrum', 'Figma', 'Postman', 'Swagger', 'Kafka', 'RabbitMQ',

    # security
    'Cybersecurity', 'Penetration Testing', 'OWASP', 'Network Security',
]

SOFT_SKILLS = [
    'Communication', 'Leadership', 'Teamwork', 'Problem Solving', 'Critical Thinking',
    'Time Management', 'Adaptability', 'Creativity', 'Collaboration', 'Presentation',
    'Project Management', 'Attention to Detail', 'Analytical', 'Self-motivated',
]

EDUCATION_KEYWORDS = {
    'phd': 4,
    'doctorate': 4,
    'master': 3,
    'mtech': 3,
    'msc': 3,
    'mba': 3,
    'bachelor': 2,
    'btech': 2,
    'bsc': 2,
    'be': 2,
    'bca': 2,
    'diploma': 1,
    '12th': 0,
    'high school': 0
}


def extract_skills(text):
    """Find skills mentioned in resume text"""
    found = []
    text_lower = text.lower()

    for skill in TECH_SKILLS:
        # word boundary check so 'C' doesn't match 'C++'
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)

    for skill in SOFT_SKILLS:
        if skill.lower() in text_lower:
            found.append(skill)

    return list(set(found))


def calculate_skill_match(resume_skills, job_required, job_preferred=None):
    """Returns match %, matched list, and missing list"""
    if not job_required:
        return 0, [], []

    resume_lower = [s.lower() for s in resume_skills]
    required_lower = [s.lower() for s in job_required]

    matched = []
    missing = []

    for skill in job_required:
        if skill.lower() in resume_lower:
            matched.append(skill)
        else:
            missing.append(skill)

    score = (len(matched) / len(job_required)) * 100 if job_required else 0

    # give a small bonus for preferred skills (max 10 points extra)
    if job_preferred:
        preferred_lower = [s.lower() for s in job_preferred]
        pref_matched = sum(1 for s in preferred_lower if s in resume_lower)
        bonus = min((pref_matched / len(job_preferred)) * 15, 10)
        score = min(score + bonus, 100)

    return round(score, 1), matched, missing


def extract_experience_years(text):
    """Try to figure out total years of experience from the text"""
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    # count date ranges like "2020 - 2023" or "Jan 2021 - Dec 2022"
    year_pattern = r'\b(20\d{2})\s*[-–]\s*(20\d{2}|present|current)\b'
    matches = re.findall(year_pattern, text, re.IGNORECASE)

    total = 0
    current_year = 2025
    for start, end in matches:
        start_y = int(start)
        end_y = current_year if end.lower() in ('present', 'current') else int(end)
        diff = end_y - start_y
        if 0 < diff < 20:  # sanity check
            total += diff

    return min(total, 30)  # cap at 30 just in case


def score_experience(years_found, years_required):
    if years_required == 0:
        return 85  # entry level - give decent score
    if years_found >= years_required:
        return min(100, 70 + (years_found - years_required) * 5)
    else:
        ratio = years_found / years_required
        return round(ratio * 70, 1)


def extract_education_level(text):
    text_lower = text.lower()
    highest = None
    highest_score = -1

    for keyword, score in EDUCATION_KEYWORDS.items():
        if keyword in text_lower:
            if score > highest_score:
                highest_score = score
                highest = keyword

    return highest, highest_score


def score_education(detected_level_score, required_keyword):
    """Simple scoring based on detected vs required education"""
    if not required_keyword:
        return 75

    req_lower = required_keyword.lower()
    required_score = 0
    for kw, sc in EDUCATION_KEYWORDS.items():
        if kw in req_lower:
            required_score = sc
            break

    if detected_level_score >= required_score:
        return 100
    elif detected_level_score == required_score - 1:
        return 70
    else:
        return 40


def keyword_density_score(resume_text, job_description):
    """Score based on how many job description words appear in resume"""
    if not job_description:
        return 50

    # get meaningful words from JD (skip stop words)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
                  'for', 'of', 'with', 'is', 'are', 'was', 'be', 'have', 'has',
                  'will', 'can', 'should', 'must', 'we', 'you', 'our', 'your'}

    jd_words = set(re.findall(r'\b[a-z]{3,}\b', job_description.lower()))
    jd_words -= stop_words

    if not jd_words:
        return 50

    resume_lower = resume_text.lower()
    matched = sum(1 for w in jd_words if w in resume_lower)

    return round(min((matched / len(jd_words)) * 120, 100), 1)


def calculate_overall_score(skill_score, exp_score, edu_score, keyword_score):
    w = Config.SKILL_MATCH_WEIGHT, Config.EXPERIENCE_WEIGHT, Config.EDUCATION_WEIGHT, Config.KEYWORD_WEIGHT
    total = (
        skill_score * w[0] +
        exp_score * w[1] +
        edu_score * w[2] +
        keyword_score * w[3]
    )
    return round(total, 1)


def get_score_label(score):
    if score >= 80:
        return 'Excellent', 'success'
    elif score >= 65:
        return 'Good', 'primary'
    elif score >= 50:
        return 'Average', 'warning'
    else:
        return 'Needs Work', 'danger'
