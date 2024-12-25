import pytest
from app import app, db
from models import User, MenuItem, Order, Payment
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test users
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            staff = User(username='staff1', role='staff')
            staff.set_password('staff123')
            table = User(username='table1', role='table', table_number=1)
            table.set_password('table123')
            
            # Create test menu items
            mojito = MenuItem(
                name='Mojito',
                price=8.50,
                category='drink',
                stock=100,
                track_stock=True
            )
            waiter_service = MenuItem(
                name='Waiter Service',
                price=0.00,
                category='service',
                track_stock=False
            )
            
            db.session.add_all([admin, staff, table, mojito, waiter_service])
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.drop_all()

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
