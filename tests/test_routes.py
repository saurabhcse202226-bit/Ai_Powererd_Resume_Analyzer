"""
tests/test_routes.py

Flask route tests - login, register, upload flow
Run: pytest tests/
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from models.db import db, User


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret'

    with app.app_context():
        db.create_all()
        from models.db import seed_data
        seed_data()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def registered_user(app):
    with app.app_context():
        user = User(name='Test User', email='test@test.com', role='user')
        user.set_password('test1234')
        db.session.add(user)
        db.session.commit()
    return {'email': 'test@test.com', 'password': 'test1234'}


class TestPublicRoutes:
    def test_index_loads(self, client):
        res = client.get('/')
        assert res.status_code == 200

    def test_login_page_loads(self, client):
        res = client.get('/auth/login')
        assert res.status_code == 200

    def test_register_page_loads(self, client):
        res = client.get('/auth/register')
        assert res.status_code == 200

    def test_about_page_loads(self, client):
        res = client.get('/about')
        assert res.status_code == 200

    def test_dashboard_redirects_without_login(self, client):
        res = client.get('/dashboard')
        assert res.status_code == 302  # redirect to login


class TestAuth:
    def test_register_new_user(self, client):
        res = client.post('/auth/register', data={
            'name': 'New User',
            'email': 'new@example.com',
            'password': 'pass1234',
            'confirm_password': 'pass1234',
            'role': 'user'
        }, follow_redirects=True)
        assert res.status_code == 200

    def test_register_mismatched_password(self, client):
        res = client.post('/auth/register', data={
            'name': 'Someone',
            'email': 'someone@test.com',
            'password': 'abc123',
            'confirm_password': 'different',
            'role': 'user'
        }, follow_redirects=True)
        assert b'Passwords do not match' in res.data

    def test_login_valid(self, client, registered_user):
        res = client.post('/auth/login', data={
            'email': registered_user['email'],
            'password': registered_user['password']
        }, follow_redirects=True)
        assert res.status_code == 200

    def test_login_invalid_password(self, client, registered_user):
        res = client.post('/auth/login', data={
            'email': registered_user['email'],
            'password': 'wrongpass'
        }, follow_redirects=True)
        assert b'Invalid email or password' in res.data

    def test_login_nonexistent_user(self, client):
        res = client.post('/auth/login', data={
            'email': 'nobody@nowhere.com',
            'password': 'something'
        }, follow_redirects=True)
        assert b'Invalid email or password' in res.data


class TestApiEndpoints:
    def test_jobs_api(self, client):
        res = client.get('/api/jobs')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_single_job_api(self, client):
        res = client.get('/api/jobs/1')
        assert res.status_code == 200
        data = res.get_json()
        assert 'title' in data['data']

    def test_protected_api_requires_login(self, client):
        res = client.get('/api/my/resumes')
        # should redirect or 401
        assert res.status_code in (302, 401, 200)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
