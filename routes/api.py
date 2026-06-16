"""
routes/api.py

REST API endpoints. Useful if someone wants to integrate 
this with a mobile app or other frontend later.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.db import db, Resume, Analysis, JobProfile

api_bp = Blueprint('api', __name__)


def api_response(data=None, message='', status=200, error=None):
    resp = {'success': error is None, 'message': message}
    if data is not None:
        resp['data'] = data
    if error:
        resp['error'] = error
    return jsonify(resp), status


@api_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Get list of all active job profiles"""
    jobs = JobProfile.query.filter_by(is_active=True).all()
    data = [{
        'id': j.id,
        'title': j.title,
        'category': j.category,
        'description': j.description,
        'required_skills': j.get_required_skills(),
        'preferred_skills': j.get_preferred_skills(),
        'min_experience': j.min_experience,
        'education_requirement': j.education_requirement
    } for j in jobs]
    return api_response(data=data)


@api_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = JobProfile.query.get_or_404(job_id)
    return api_response(data={
        'id': job.id,
        'title': job.title,
        'category': job.category,
        'description': job.description,
        'required_skills': job.get_required_skills(),
        'preferred_skills': job.get_preferred_skills(),
        'min_experience': job.min_experience
    })


@api_bp.route('/my/resumes', methods=['GET'])
@login_required
def get_my_resumes():
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    data = [{
        'id': r.id,
        'original_name': r.original_name,
        'file_type': r.file_type,
        'uploaded_at': r.uploaded_at.isoformat(),
        'file_size': r.file_size
    } for r in resumes]
    return api_response(data=data)


@api_bp.route('/my/analyses', methods=['GET'])
@login_required
def get_my_analyses():
    analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.analyzed_at.desc()).all()
    data = [{
        'id': a.id,
        'resume_id': a.resume_id,
        'job_id': a.job_id,
        'overall_score': a.overall_score,
        'skill_match_score': a.skill_match_score,
        'experience_score': a.experience_score,
        'education_score': a.education_score,
        'keyword_score': a.keyword_score,
        'analyzed_at': a.analyzed_at.isoformat()
    } for a in analyses]
    return api_response(data=data)


@api_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
@login_required
def get_analysis_detail(analysis_id):
    a = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    return api_response(data={
        'id': a.id,
        'overall_score': a.overall_score,
        'skill_match_score': a.skill_match_score,
        'experience_score': a.experience_score,
        'education_score': a.education_score,
        'keyword_score': a.keyword_score,
        'extracted_skills': a.get_extracted_skills(),
        'matched_skills': a.get_matched_skills(),
        'missing_skills': a.get_missing_skills(),
        'ai_summary': a.ai_summary,
        'suggestions': a.get_suggestions(),
        'strengths': a.get_strengths(),
        'weaknesses': a.get_weaknesses()
    })


@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    total_resumes = Resume.query.filter_by(user_id=current_user.id).count()
    total_analyses = Analysis.query.filter_by(user_id=current_user.id).count()

    avg_score = 0
    if total_analyses:
        scores = [a.overall_score for a in Analysis.query.filter_by(user_id=current_user.id).all()]
        avg_score = round(sum(scores) / len(scores), 1)

    return api_response(data={
        'total_resumes': total_resumes,
        'total_analyses': total_analyses,
        'average_score': avg_score
    })
