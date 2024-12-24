import pytest
from app import app, db
from models import User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Create test users with hashed passwords
            users = [
                {
                    'username': 'admin',
                    'password': generate_password_hash('admin123'),
                    'role': User.ROLE_ADMIN
                },
                {
                    'username': 'staff1',
                    'password': generate_password_hash('staff123'),
                    'role': User.ROLE_STAFF
                },
                {
                    'username': 'table1',
                    'password': generate_password_hash('table123'),
                    'role': User.ROLE_TABLE,
                    'table_number': 1
                }
            ]
            
            for user_data in users:
                user = User(
                    username=user_data['username'],
                    password_hash=user_data['password'],
                    role=user_data['role'],
                    table_number=user_data.get('table_number')
                )
                db.session.add(user)
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.drop_all()

def test_admin_login(client):
    """Test admin login functionality"""
    response = client.post('/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert response.json['role'] == User.ROLE_ADMIN

def test_staff_login(client):
    """Test staff login functionality"""
    response = client.post('/auth/login', json={
        'username': 'staff1',
        'password': 'staff123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert response.json['role'] == User.ROLE_STAFF

def test_table_login(client):
    """Test table login functionality"""
    response = client.post('/auth/login', json={
        'username': 'table1',
        'password': 'table123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert response.json['role'] == User.ROLE_TABLE
    assert response.json['table_number'] == 1

def test_invalid_login(client):
    """Test invalid login credentials"""
    response = client.post('/auth/login', json={
        'username': 'staff1',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert 'error' in response.json
