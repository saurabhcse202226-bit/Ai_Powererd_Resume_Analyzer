from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from models.db import db, Resume, Analysis, JobProfile, User

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).limit(5).all()
    recent_analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.analyzed_at.desc()).limit(5).all()

    # simple stats
    total_resumes = Resume.query.filter_by(user_id=current_user.id).count()
    total_analyses = Analysis.query.filter_by(user_id=current_user.id).count()

    avg_score = 0
    if total_analyses > 0:
        all_scores = [a.overall_score for a in Analysis.query.filter_by(user_id=current_user.id).all()]
        avg_score = round(sum(all_scores) / len(all_scores), 1)

    best_analysis = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.overall_score.desc()).first()

    return render_template('dashboard.html',
        user_resumes=user_resumes,
        recent_analyses=recent_analyses,
        total_resumes=total_resumes,
        total_analyses=total_analyses,
        avg_score=avg_score,
        best_analysis=best_analysis
    )


@main_bp.route('/jobs')
@login_required
def jobs():
    category = request.args.get('category', '')
    query = JobProfile.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    job_list = query.order_by(JobProfile.created_at.desc()).all()

    categories = db.session.query(JobProfile.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    return render_template('jobs.html', jobs=job_list, categories=categories, selected_category=category)


@main_bp.route('/about')
def about():
    return render_template('about.html')


# need to import request for jobs route
from flask import request
