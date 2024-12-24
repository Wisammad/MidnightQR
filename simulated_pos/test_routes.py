import pytest
from app import app, db
from models import User, Order, MenuItem

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test data
            staff_user = User(username='teststaff', role='staff')
            staff_user.set_password('password123')
            db.session.add(staff_user)
            
            table_user = User(username='table1', role='table', table_number=1)
            db.session.add(table_user)
            
            menu_item = MenuItem(name='Test Item', price=10.0, category='food')
            db.session.add(menu_item)
            
            db.session.commit()
        yield client
        
        with app.app_context():
            db.drop_all()

def test_staff_order_acceptance(client):
    # Login as staff
    response = client.post('/auth/login', json={
        'username': 'teststaff',
        'password': 'password123'
    })
    assert response.status_code == 200
    token = response.json['access_token']
    
    # Create test order
    order = Order(
        user_id=2,  # table user id
        table_number=1,
        status='Pending',
        total_price=10.0
    )
    with app.app_context():
        db.session.add(order)
        db.session.commit()
        order_id = order.id
    
    # Test order acceptance
    response = client.put(
        f'/orders/{order_id}/status',
        json={'status': 'Accepted'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json['status'] == 'Accepted'
    assert response.json['staff_id'] is not None

def test_menu_retrieval(client):
    response = client.get('/menu')
    assert response.status_code == 200
    assert len(response.json) > 0
    assert 'name' in response.json[0]
    assert 'price' in response.json[0]

def test_order_creation(client):
    # Login as table
    with app.app_context():
        table_user = User.query.filter_by(role='table').first()
        token = create_access_token(
            identity=table_user.id,
            additional_claims={'role': 'table', 'table_number': 1}
        )
    
    # Create order
    response = client.post(
        '/orders',
        json={
            'items': [{'id': 1, 'quantity': 1}]
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert 'order_id' in response.json
