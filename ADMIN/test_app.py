import pytest
from flask import session
from app2 import app, db, User, Person

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test user
            user = User(email="testuser@example.com", password="password", is_verified=True)
            db.session.add(user)
            db.session.commit()
        yield client
        db.session.remove()
        db.drop_all()

def test_register(client):
    response = client.post('/register', data={
        'email': 'newuser@example.com',
        'password': 'newpassword'
    }, follow_redirects=True)
    assert b'OTP sent' in response.data
    user = User.query.filter_by(email='newuser@example.com').first()
    assert user is not None

def test_login(client):
    response = client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password'
    }, follow_redirects=True)
    assert b'prediction' in response.data  # Check redirection to prediction page
    assert session.get('user') == 'testuser@example.com'

def test_failed_login(client):
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b'Invalid credentials' in response.data

def test_prediction(client):
    with client.session_transaction() as sess:
        sess['user'] = 'testuser@example.com'
    
    response = client.post('/prediction', data={
        'name': 'John Doe',
        'age': 30,
        'gender': 'Male',
        'income_level': 20000,
        'employment_status': 1,
        'education_level': 2,
        'mental_health_status': 0,
        'substance_abuse': 0,
        'family_status': 1,
        'housing_history': 1,
        'disability': 0,
        'region': 1,
        'social_support': 2
    }, follow_redirects=True)
    assert b'Not Homeless' in response.data or b'Homeless' in response.data  # Based on the model prediction

def test_admin_login(client):
    # Create an admin user for testing
    admin = User(email='admin@example.com', password='adminpassword', is_verified=True)
    db.session.add(admin)
    db.session.commit()

    response = client.post('/admin/login', data={
        'username': 'superadmin',
        'password': 'superpassword'
    }, follow_redirects=True)
    assert b'admin_dashboard' in response.data
    assert session.get('admin_id') is not None
