from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db, User
from functools import wraps
from datetime import datetime

auth = Blueprint('auth', __name__)

def role_required(roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            jwt = get_jwt()
            if jwt.get("role") not in roles:
                return jsonify({"error": "Unauthorized"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400
    
    user = User(
        username=data['username'],
        role=User.ROLE_TABLE  # Default role for registration
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "permissions": user.permissions}
    )
    
    return jsonify({
        "message": "User created successfully",
        "access_token": access_token,
        "role": user.role
    }), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role, "table_number": user.table_number}
    )
    
    response = make_response(jsonify({
        "access_token": access_token,
        "role": user.role,
        "table_number": user.table_number
    }))
    
    origin = request.headers.get('Origin')
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@auth.route('/users', methods=['GET'])
@role_required([User.ROLE_ADMIN])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@auth.route('/create-staff', methods=['POST'])
@role_required([User.ROLE_ADMIN])
def create_staff():
    data = request.json
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400
    
    user = User(
        username=data['username'],
        role=User.ROLE_STAFF
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "Staff account created successfully"}), 201

@auth.route('/tables', methods=['POST'])
@role_required([User.ROLE_ADMIN])
def create_table():
    data = request.json
    table_number = data['table_number']
    
    if User.query.filter_by(table_number=table_number).first():
        return jsonify({"error": f"Table {table_number} already exists"}), 400
    
    username = f"table{table_number}"
    password = "table123"  # Same password for all tables
    
    table_user = User(
        username=username,
        role=User.ROLE_TABLE,
        table_number=table_number
    )
    table_user.set_password(password)
    
    db.session.add(table_user)
    db.session.commit()
    
    return jsonify({
        "message": f"Table {table_number} created successfully",
        "username": username,
        "password": password
    }), 201

@auth.route('/tables/<int:table_number>', methods=['DELETE'])
@role_required([User.ROLE_ADMIN])
def delete_table(table_number):
    table_user = User.query.filter_by(table_number=table_number).first()
    if not table_user:
        return jsonify({"error": f"Table {table_number} not found"}), 404
    
    db.session.delete(table_user)
    db.session.commit()
    
    return jsonify({"message": f"Table {table_number} deleted successfully"})

# Add initialization of tables to app.py
def create_initial_tables():
    # Create tables 1 through 5 if they don't exist
    for table_num in range(1, 6):
        if not User.query.filter_by(table_number=table_num).first():
            table_user = User(
                username=f"table{table_num}",
                role=User.ROLE_TABLE,
                table_number=table_num
            )
            table_user.set_password(f"table{table_num}pass")
            db.session.add(table_user)
    db.session.commit()