from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Menu Item Model
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=None)
    track_stock = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'description': self.description,
            'stock': self.stock if self.track_stock else None,
            'track_stock': self.track_stock
        }

# Order Model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    table_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    total_price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_service = db.Column(db.Boolean, default=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    staff = db.relationship('User', foreign_keys=[staff_id], backref='assigned_orders')
    user = db.relationship('User', foreign_keys=[user_id], backref='placed_orders')
    items = db.Column(db.JSON, default=list)

    def to_dict(self):
        return {
            'id': self.id,
            'table_number': self.table_number,
            'items': self.items or [],
            'total_price': self.total_price,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_service': self.is_service,
            'staff_id': self.staff_id,
            'staff_name': self.staff.username if self.staff else None
        }

    # Status constants
    STATUS_PENDING = "Pending"      # Initial state when order is created
    STATUS_ACCEPTED = "Accepted"    # Waiter acknowledged the order
    STATUS_COMPLETED = "Completed"  # Order fulfilled
    STATUS_REFUNDED = "Refunded"    # Order refunded
    
    # Update valid transitions
    VALID_STATUS_TRANSITIONS = {
        STATUS_PENDING: [STATUS_ACCEPTED, STATUS_REFUNDED],  # Can be accepted by waiter or refunded by customer
        STATUS_ACCEPTED: [STATUS_COMPLETED],                 # Once accepted, can only be completed
        STATUS_COMPLETED: [],                               # Final state
        STATUS_REFUNDED: []                                 # Final state
    }
    def can_transition_to(self, new_status):
        return new_status in self.VALID_STATUS_TRANSITIONS.get(self.status, [])
    
    # Relationships
    payments = db.relationship('Payment', backref='order', lazy=True)

# Payment Model
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # admin, staff, or table
    table_number = db.Column(db.Integer, unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Role constants
    ROLE_ADMIN = "admin"
    ROLE_STAFF = "staff"
    ROLE_TABLE = "table"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'table_number': self.table_number
        }

    # Role-based permissions
    @property
    def permissions(self):
        if self.role == self.ROLE_ADMIN:
            return ['read:all', 'write:all', 'manage:users', 'view:reports']
        elif self.role == self.ROLE_STAFF:
            return ['read:orders', 'write:orders', 'update:status']
        else:  # customer
            return ['read:menu', 'create:orders', 'read:own_orders']
