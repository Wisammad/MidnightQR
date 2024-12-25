import pytest
from app import app, db
from models import User, MenuItem, Order, Payment
from flask_jwt_extended import create_access_token

@pytest.fixture
def application():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-key'
    
    with app.app_context():
        db.create_all()
        # Assume that the database is pre-populated with users
        yield app
        db.drop_all()

@pytest.fixture
def client(application):
    return application.test_client()

def test_create_order(client):
    """Test order creation by table"""
    # Assume 'table1' user already exists
    response = client.post('/auth/login', json={
        'username': 'table1',
        'password': 'table123'
    })
    token = response.json.get('access_token')
    assert token is not None, f"Login failed: {response.json}"
    
    # Create order
    response = client.post('/orders', 
        json={'items': [{'id': 1, 'quantity': 2}]},
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 201, f"Order creation failed: {response.json}"
    assert 'order_id' in response.json, f"Missing order_id: {response.json}"

def test_update_order_status(client):
    """Test order status updates by staff"""
    # Create initial order as table
    table_token = create_access_token(identity={'id': 3, 'role': 'table'})
    response = client.post('/orders',
        json={'items': [{'id': 1, 'quantity': 1}]},
        headers={'Authorization': f'Bearer {table_token}'}
    )
    order_id = response.json['order_id']
    
    # Login as staff
    staff_token = create_access_token(identity={'id': 2, 'role': 'staff'})
    
    # Update to Preparing
    response = client.put(f'/orders/{order_id}/status',
        json={'status': 'Preparing'},
        headers={'Authorization': f'Bearer {staff_token}'}
    )
    assert response.status_code == 200
    assert response.json['status'] == 'Preparing'
    
    # Update to Completed
    response = client.put(f'/orders/{order_id}/status',
        json={'status': 'Completed'},
        headers={'Authorization': f'Bearer {staff_token}'}
    )
    assert response.status_code == 200
    assert response.json['status'] == 'Completed'

def test_process_payment(client):
    """Test payment processing for an order"""
    # Create order as table
    table_token = create_access_token(identity={'id': 3, 'role': 'table'})
    response = client.post('/orders',
        json={'items': [{'id': 1, 'quantity': 1}]},
        headers={'Authorization': f'Bearer {table_token}'}
    )
    order_id = response.json['order_id']
    
    # Process payment
    response = client.post('/payments',
        json={'order_id': order_id, 'amount': 8.50},
        headers={'Authorization': f'Bearer {table_token}'}
    )
    assert response.status_code == 200
    assert response.json['status'] == 'Success'

def test_process_refund(client):
    """Test refund processing for a paid order"""
    # Create and pay for an order
    table_token = create_access_token(identity={'id': 3, 'role': 'table'})
    response = client.post('/orders',
        json={'items': [{'id': 1, 'quantity': 1}]},
        headers={'Authorization': f'Bearer {table_token}'}
    )
    order_id = response.json['order_id']
    
    client.post('/payments',
        json={'order_id': order_id, 'amount': 8.50},
        headers={'Authorization': f'Bearer {table_token}'}
    )
    
    # Process refund as admin
    admin_token = create_access_token(identity={'id': 1, 'role': 'admin'})
    response = client.post('/refunds',
        json={'order_id': order_id},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    assert response.json['status'] == 'Refunded'

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
    # Assume 'staff1' user already exists
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
    
'''
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
'''