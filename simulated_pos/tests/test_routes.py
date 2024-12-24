import pytest
from app import app, db
from models import User
from flask_jwt_extended import create_access_token

@pytest.fixture
def application():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-key'
    
    # Register the auth blueprint
    from auth import auth
    app.register_blueprint(auth, url_prefix='/auth')
    
    return app

@pytest.fixture
def client(application):
    with application.test_client() as client:
        with application.app_context():
            db.create_all()
            # Create test staff user only
            staff_user = User(username='staff1', role='staff')
            staff_user.set_password('staff123')
            db.session.add(staff_user)
            db.session.commit()
        yield client
        with application.app_context():
            db.drop_all()

@pytest.fixture
def admin_token(client, application):
    with application.app_context():
        # Create admin user
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        # Login as admin
        response = client.post('/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        return response.json['access_token']

def test_staff_login(client):
    """Test staff login functionality"""
    response = client.post('/auth/login', json={
        'username': 'staff1',
        'password': 'staff123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert response.json['role'] == 'staff'

def test_invalid_login(client):
    """Test invalid login credentials"""
    response = client.post('/auth/login', json={
        'username': 'staff1',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert 'error' in response.json

def test_create_staff(client, admin_token):
    """Test staff creation by admin"""
    response = client.post('/auth/create-staff', 
        json={
            'username': 'newstaff',
            'password': 'staffpass'
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    assert response.status_code == 201
    assert response.json['message'] == "Staff account created successfully"

def test_create_staff_unauthorized(client):
    """Test staff creation without admin privileges"""
    response = client.post('/auth/create-staff', 
        json={
            'username': 'newstaff',
            'password': 'staffpass'
        }
    )
    
    assert response.status_code == 401  # Unauthorized without token
