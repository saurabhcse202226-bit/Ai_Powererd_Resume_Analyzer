from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models.db import db, Resume, Analysis, JobProfile
from utils.extractor import extract_text, clean_text
from utils.analyzer import (extract_skills, calculate_skill_match, extract_experience_years,
                             score_experience, extract_education_level, score_education,
                             keyword_density_score, calculate_overall_score, get_score_label)
from utils.ai_feedback import generate_ai_feedback
from utils.helpers import allowed_file, save_uploaded_file, delete_file
import json
import os

resume_bp = Blueprint('resume', __name__)


@resume_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    jobs = JobProfile.query.filter_by(is_active=True).order_by(JobProfile.title).all()

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected.', 'danger')
            return render_template('resume/upload.html', jobs=jobs)

        file = request.files['resume']

        if file.filename == '':
            flash('No file selected.', 'danger')
            return render_template('resume/upload.html', jobs=jobs)

        if not allowed_file(file.filename):
            flash('Only PDF, DOCX, DOC, and TXT files are allowed.', 'warning')
            return render_template('resume/upload.html', jobs=jobs)

        try:
            saved_name, original_name, file_size, filepath = save_uploaded_file(file)

            # extract text right away
            raw_text = extract_text(filepath)
            raw_text = clean_text(raw_text)

            if not raw_text:
                flash('Could not read text from this file. Make sure it\'s not a scanned image PDF.', 'warning')
                delete_file(saved_name)
                return render_template('resume/upload.html', jobs=jobs)

            resume = Resume(
                user_id=current_user.id,
                filename=saved_name,
                original_name=original_name,
                file_type=original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'unknown',
                raw_text=raw_text,
                file_size=file_size
            )
            db.session.add(resume)
            db.session.commit()

            flash('Resume uploaded successfully!', 'success')

            # if user selected a job, go straight to analysis
            job_id = request.form.get('job_id')
            if job_id:
                return redirect(url_for('resume.analyze', resume_id=resume.id, job_id=job_id))

            return redirect(url_for('resume.my_resumes'))

        except Exception as e:
            current_app.logger.error(f"Upload error: {e}")
            flash('Something went wrong during upload. Please try again.', 'danger')

    return render_template('resume/upload.html', jobs=jobs)


@resume_bp.route('/my-resumes')
@login_required
def my_resumes():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    return render_template('resume/my_resumes.html', resumes=resumes)


@resume_bp.route('/analyze/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def analyze(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    jobs = JobProfile.query.filter_by(is_active=True).order_by(JobProfile.title).all()

    job_id = request.args.get('job_id') or request.form.get('job_id')

    if request.method == 'POST' or job_id:
        if not job_id:
            flash('Please select a job to analyze against.', 'warning')
            return render_template('resume/analyze.html', resume=resume, jobs=jobs)

        job = JobProfile.query.get_or_404(int(job_id))

        # do the actual analysis
        analysis = _run_analysis(resume, job)

        flash('Analysis complete!', 'success')
        return redirect(url_for('resume.result', analysis_id=analysis.id))

    return render_template('resume/analyze.html', resume=resume, jobs=jobs)


def _run_analysis(resume, job):
    """The main analysis pipeline"""
    text = resume.raw_text or ""

    # skill extraction and matching
    extracted = extract_skills(text)
    required_skills = job.get_required_skills()
    preferred_skills = job.get_preferred_skills()

    skill_score, matched, missing = calculate_skill_match(extracted, required_skills, preferred_skills)

    # experience
    years_found = extract_experience_years(text)
    exp_score = score_experience(years_found, job.min_experience or 0)

    # education
    edu_level, edu_score_raw = extract_education_level(text)
    edu_score = score_education(edu_score_raw, job.education_requirement or '')

    # keyword match against job description
    kw_score = keyword_density_score(text, job.description or '')

    overall = calculate_overall_score(skill_score, exp_score, edu_score, kw_score)

    # AI feedback (might be rule-based fallback if no API key)
    feedback = generate_ai_feedback(text, job.title, matched, missing, overall)

    analysis = Analysis(
        user_id=resume.user_id,
        resume_id=resume.id,
        job_id=job.id,
        overall_score=overall,
        skill_match_score=skill_score,
        experience_score=exp_score,
        education_score=edu_score,
        keyword_score=kw_score,
        extracted_skills=json.dumps(extracted),
        matched_skills=json.dumps(matched),
        missing_skills=json.dumps(missing),
        extracted_experience=str(years_found),
        extracted_education=edu_level or 'Not detected',
        ai_summary=feedback.get('summary', ''),
        suggestions=json.dumps(feedback.get('suggestions', [])),
        strengths=json.dumps(feedback.get('strengths', [])),
        weaknesses=json.dumps(feedback.get('weaknesses', []))
    )

    db.session.add(analysis)
    db.session.commit()
    return analysis


@resume_bp.route('/result/<int:analysis_id>')
@login_required
def result(analysis_id):
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    label, color = get_score_label(analysis.overall_score)

    return render_template('resume/result.html',
        analysis=analysis,
        score_label=label,
        score_color=color
    )


@resume_bp.route('/history')
@login_required
def history():
    analyses = (Analysis.query
                .filter_by(user_id=current_user.id)
                .order_by(Analysis.analyzed_at.desc())
                .all())
    return render_template('resume/history.html', analyses=analyses)


@resume_bp.route('/delete/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()

    delete_file(resume.filename)
    db.session.delete(resume)
    db.session.commit()

    flash('Resume deleted.', 'info')
    return redirect(url_for('resume.my_resumes'))
