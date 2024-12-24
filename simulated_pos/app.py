from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db, MenuItem, Order, Payment, User
from routes import routes
from auth import auth
import os

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:3000", "http://192.168.1.168:3000", "http://127.0.0.1:3000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True,
         "send_wildcard": False
     }},
     supports_credentials=True
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'

jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    try:
        user_id = int(identity)
        return User.query.get(user_id)
    except ValueError:
        return None

db.init_app(app)
app.register_blueprint(routes)
app.register_blueprint(auth, url_prefix='/auth')

def create_sample_data():
    # Create admin if doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    # Create two staff members if they don't exist
    staff_members = ['staff1', 'staff2']
    for staff_name in staff_members:
        if not User.query.filter_by(username=staff_name).first():
            staff = User(username=staff_name, role='staff')
            staff.set_password('staff123')
            db.session.add(staff)
    db.session.commit()

    # Create tables 1-5 if they don't exist
    for table_num in range(1, 6):
        if not User.query.filter_by(table_number=table_num).first():
            table_user = User(
                username=f"table{table_num}",
                role='table',
                table_number=table_num
            )
            table_user.set_password('table123')  # Same password for all tables
            db.session.add(table_user)
    db.session.commit()

    # Create menu items if they don't exist
    if not MenuItem.query.first():
        menu_items = [
            # Drinks
            MenuItem(
                name='Mojito',
                price=8.50,
                category='drink',
                stock=100,
                track_stock=True,
                description='Classic Cuban cocktail with rum, mint, and lime'
            ),
            MenuItem(
                name='Vodka',
                price=8.00,
                category='drink',
                stock=100,
                track_stock=True,
                description='Premium vodka'
            ),
            MenuItem(
                name='Gin',
                price=7.00,
                category='drink',
                stock=100,
                track_stock=True,
                description='London dry gin'
            ),
            # Services
            MenuItem(
                name='Empty Glasses',
                price=0.00,
                category='service',
                track_stock=False,
                description='Request clean empty glasses'
            ),
            MenuItem(
                name='Waiter Service',
                price=0.00,
                category='service',
                track_stock=False,
                description='Call a waiter to your table'
            ),
            MenuItem(
                name='Bottle Show Service',
                price=0.00,
                category='service',
                track_stock=False,
                description='Special bottle presentation service'
            )
        ]
        
        for item in menu_items:
            db.session.add(item)
        
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    app.run(host='0.0.0.0', port=5001)
