from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'recruiter'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    resumes = db.relationship('Resume', backref='owner', lazy=True, cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    file_type = db.Column(db.String(10))
    raw_text = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)  # in bytes

    analyses = db.relationship('Analysis', backref='resume', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Resume {self.original_name}>'


class JobProfile(db.Model):
    __tablename__ = 'job_profiles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text)  # stored as JSON string
    preferred_skills = db.Column(db.Text)
    min_experience = db.Column(db.Integer, default=0)
    education_requirement = db.Column(db.String(100))
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    analyses = db.relationship('Analysis', backref='job', lazy=True)

    def get_required_skills(self):
        if self.required_skills:
            return json.loads(self.required_skills)
        return []

    def set_required_skills(self, skills_list):
        self.required_skills = json.dumps(skills_list)

    def get_preferred_skills(self):
        if self.preferred_skills:
            return json.loads(self.preferred_skills)
        return []

    def __repr__(self):
        return f'<JobProfile {self.title}>'


class Analysis(db.Model):
    __tablename__ = 'analyses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_profiles.id'), nullable=True)

    # scores (0-100)
    overall_score = db.Column(db.Float, default=0)
    skill_match_score = db.Column(db.Float, default=0)
    experience_score = db.Column(db.Float, default=0)
    education_score = db.Column(db.Float, default=0)
    keyword_score = db.Column(db.Float, default=0)

    # extracted info stored as JSON
    extracted_skills = db.Column(db.Text)
    matched_skills = db.Column(db.Text)
    missing_skills = db.Column(db.Text)
    extracted_experience = db.Column(db.Text)
    extracted_education = db.Column(db.Text)

    # AI feedback
    ai_summary = db.Column(db.Text)
    suggestions = db.Column(db.Text)
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)

    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_matched_skills(self):
        return json.loads(self.matched_skills) if self.matched_skills else []

    def get_missing_skills(self):
        return json.loads(self.missing_skills) if self.missing_skills else []

    def get_extracted_skills(self):
        return json.loads(self.extracted_skills) if self.extracted_skills else []

    def get_suggestions(self):
        return json.loads(self.suggestions) if self.suggestions else []

    def get_strengths(self):
        return json.loads(self.strengths) if self.strengths else []

    def get_weaknesses(self):
        return json.loads(self.weaknesses) if self.weaknesses else []

    def __repr__(self):
        return f'<Analysis {self.id} score={self.overall_score}>'


def seed_data():
    """Add some sample job profiles if none exist yet"""
    if JobProfile.query.count() > 0:
        return

    sample_jobs = [
        {
            'title': 'Python Backend Developer',
            'description': 'We need a solid Python developer who can build REST APIs and work with databases.',
            'required_skills': ['Python', 'Flask', 'Django', 'SQL', 'REST API', 'Git'],
            'preferred_skills': ['Docker', 'Redis', 'PostgreSQL', 'AWS'],
            'min_experience': 1,
            'education_requirement': "Bachelor's in CS or related",
            'category': 'Backend'
        },
        {
            'title': 'Data Scientist',
            'description': 'Looking for someone comfortable with ML models and data wrangling.',
            'required_skills': ['Python', 'Machine Learning', 'Pandas', 'NumPy', 'SQL', 'scikit-learn'],
            'preferred_skills': ['TensorFlow', 'PyTorch', 'Spark', 'Tableau', 'R'],
            'min_experience': 1,
            'education_requirement': "Bachelor's in CS/Statistics/Math",
            'category': 'Data Science'
        },
        {
            'title': 'Frontend Developer (React)',
            'description': 'React developer for building fast, accessible UIs.',
            'required_skills': ['JavaScript', 'React', 'HTML', 'CSS', 'Git', 'REST API'],
            'preferred_skills': ['TypeScript', 'Next.js', 'Redux', 'Tailwind CSS', 'Jest'],
            'min_experience': 1,
            'education_requirement': "Bachelor's in CS or related",
            'category': 'Frontend'
        },
        {
            'title': 'Full Stack Developer',
            'description': 'Generalist developer comfortable on both front and back ends.',
            'required_skills': ['JavaScript', 'Python', 'React', 'Node.js', 'SQL', 'Git', 'REST API'],
            'preferred_skills': ['TypeScript', 'Docker', 'MongoDB', 'AWS', 'Redis'],
            'min_experience': 2,
            'education_requirement': "Bachelor's in CS or related",
            'category': 'Full Stack'
        },
        {
            'title': 'DevOps Engineer',
            'description': 'We need someone to manage CI/CD pipelines and cloud infra.',
            'required_skills': ['Linux', 'Docker', 'Kubernetes', 'CI/CD', 'AWS', 'Git', 'Bash'],
            'preferred_skills': ['Terraform', 'Ansible', 'Jenkins', 'Prometheus', 'GCP'],
            'min_experience': 2,
            'education_requirement': "Bachelor's in CS/IT",
            'category': 'DevOps'
        },
        {
            'title': 'Machine Learning Engineer',
            'description': 'Deploy and maintain ML models in production.',
            'required_skills': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'SQL', 'Git'],
            'preferred_skills': ['MLflow', 'Kubernetes', 'Spark', 'Kafka', 'Docker'],
            'min_experience': 2,
            'education_requirement': "Bachelor's/Master's in CS or related",
            'category': 'ML/AI'
        },
    ]

    for job_data in sample_jobs:
        job = JobProfile(
            title=job_data['title'],
            description=job_data['description'],
            preferred_skills=json.dumps(job_data['preferred_skills']),
            min_experience=job_data['min_experience'],
            education_requirement=job_data['education_requirement'],
            category=job_data['category']
        )
        job.set_required_skills(job_data['required_skills'])
        db.session.add(job)

    # add a demo user
    if User.query.filter_by(email='demo@resumeai.com').first() is None:
        demo_user = User(name='Demo User', email='demo@resumeai.com', role='user')
        demo_user.set_password('demo1234')
        db.session.add(demo_user)

    db.session.commit()
    print("Sample data seeded.")
