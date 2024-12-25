import pytest
from app import app, db
from models import User, MenuItem

@pytest.fixture
def application():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(application):
    return application.test_client()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test users
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', role='admin')
                admin.set_password('admin123')
                db.session.add(admin)
            
            if not User.query.filter_by(username='staff1').first():
                staff = User(username='staff1', role='staff')
                staff.set_password('staff123')
                db.session.add(staff)
            
            if not User.query.filter_by(username='table1').first():
                table = User(username='table1', role='table', table_number=1)
                table.set_password('table123')
                db.session.add(table)
            
            # Create test menu items
            if not MenuItem.query.filter_by(name='Mojito').first():
                mojito = MenuItem(
                    name='Mojito',
                    price=8.50,
                    category='drink',
                    stock=100,
                    track_stock=True
                )
                db.session.add(mojito)
            
            if not MenuItem.query.filter_by(name='Waiter Service').first():
                waiter_service = MenuItem(
                    name='Waiter Service',
                    price=0.00,
                    category='service',
                    track_stock=False
                )
                db.session.add(waiter_service)
            
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.drop_all() 