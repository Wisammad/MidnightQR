import pytest
from app import app, db
from models import User
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test staff user only
            staff_user = User(username='staff1', role='staff')
            staff_user.set_password('staff123')
            db.session.add(staff_user)
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.drop_all()

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
