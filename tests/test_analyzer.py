"""
tests/test_analyzer.py

Basic tests for the resume analysis logic.
Run with: pytest tests/
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from utils.analyzer import (
    extract_skills,
    calculate_skill_match,
    extract_experience_years,
    score_experience,
    extract_education_level,
    keyword_density_score,
    calculate_overall_score,
    get_score_label
)


SAMPLE_RESUME = """
John Doe
john@example.com | LinkedIn: linkedin.com/in/johndoe

SUMMARY
Python developer with 3 years of experience in Flask and Django.
Strong knowledge of SQL, REST API design, and Git.

SKILLS
Languages: Python, JavaScript, SQL, Bash
Frameworks: Flask, Django, React (basic)
Tools: Git, Docker, Postman

EXPERIENCE
Software Developer | TechCorp Pvt Ltd | Jan 2021 - Dec 2023
- Built REST APIs using Flask and PostgreSQL
- Managed deployments on AWS EC2
- Implemented CI/CD pipelines using GitHub Actions

EDUCATION
Bachelor of Technology in Computer Science
XYZ University | 2017 - 2021 | CGPA: 8.2
"""


class TestSkillExtraction:
    def test_extracts_python(self):
        skills = extract_skills(SAMPLE_RESUME)
        assert 'Python' in skills

    def test_extracts_flask(self):
        skills = extract_skills(SAMPLE_RESUME)
        assert 'Flask' in skills

    def test_extracts_sql(self):
        skills = extract_skills(SAMPLE_RESUME)
        assert 'SQL' in skills

    def test_extracts_docker(self):
        skills = extract_skills(SAMPLE_RESUME)
        assert 'Docker' in skills

    def test_extracts_git(self):
        skills = extract_skills(SAMPLE_RESUME)
        assert 'Git' in skills

    def test_no_false_positives(self):
        # should not extract things that aren't there
        skills = extract_skills(SAMPLE_RESUME)
        assert 'Kubernetes' not in skills


class TestSkillMatching:
    def test_perfect_match(self):
        resume_skills = ['Python', 'Flask', 'SQL', 'Git']
        required = ['Python', 'Flask', 'SQL', 'Git']
        score, matched, missing = calculate_skill_match(resume_skills, required)
        assert score == 100.0
        assert len(missing) == 0

    def test_partial_match(self):
        resume_skills = ['Python', 'Flask']
        required = ['Python', 'Flask', 'Docker', 'Kubernetes']
        score, matched, missing = calculate_skill_match(resume_skills, required)
        assert score == 50.0
        assert 'Docker' in missing
        assert 'Kubernetes' in missing

    def test_no_match(self):
        resume_skills = ['Java', 'Spring']
        required = ['Python', 'Flask']
        score, matched, missing = calculate_skill_match(resume_skills, required)
        assert score == 0.0

    def test_empty_required(self):
        score, matched, missing = calculate_skill_match(['Python'], [])
        assert score == 0

    def test_case_insensitive(self):
        resume_skills = ['python', 'flask']
        required = ['Python', 'Flask']
        score, matched, missing = calculate_skill_match(resume_skills, required)
        # our function stores skills as-is but matches case-insensitively
        assert score == 100.0


class TestExperienceExtraction:
    def test_explicit_years(self):
        text = "I have 5 years of experience in software development"
        assert extract_experience_years(text) == 5

    def test_date_range(self):
        text = "Software Engineer | 2020 - 2023"
        years = extract_experience_years(text)
        assert years == 3

    def test_present_date(self):
        text = "Developer | 2022 - Present"
        years = extract_experience_years(text)
        assert years >= 1  # depends on current year

    def test_no_experience(self):
        text = "Fresh graduate looking for first job"
        assert extract_experience_years(text) == 0


class TestScoring:
    def test_score_label_excellent(self):
        label, color = get_score_label(85)
        assert label == 'Excellent'
        assert color == 'success'

    def test_score_label_good(self):
        label, color = get_score_label(70)
        assert label == 'Good'

    def test_score_label_average(self):
        label, color = get_score_label(55)
        assert label == 'Average'

    def test_score_label_needs_work(self):
        label, color = get_score_label(30)
        assert label == 'Needs Work'

    def test_exp_score_meets_requirement(self):
        score = score_experience(3, 2)
        assert score >= 70

    def test_exp_score_below_requirement(self):
        score = score_experience(0, 3)
        assert score < 70

    def test_keyword_score_empty_jd(self):
        score = keyword_density_score("Python developer", "")
        assert score == 50


class TestEducationExtraction:
    def test_bachelor(self):
        text = "Bachelor of Technology in Computer Science from ABC University"
        level, score = extract_education_level(text)
        assert level == 'bachelor'
        assert score == 2

    def test_master(self):
        text = "Master of Science in Data Science"
        level, score = extract_education_level(text)
        assert 'master' in level

    def test_no_education(self):
        text = "I like coding and building things"
        level, score = extract_education_level(text)
        # might be none or low score
        assert score < 2 or level is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
