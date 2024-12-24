from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, MenuItem, Order, Payment, User
from auth import role_required
from datetime import datetime
import time
from flask_jwt_extended import create_access_token

routes = Blueprint('routes', __name__)

@routes.route('/menu', methods=['GET'])
def get_menu():
    menu_items = MenuItem.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'price': item.price,
        'category': item.category,
        'description': item.description,
        'stock': item.stock if item.track_stock else None,
        'track_stock': item.track_stock
    } for item in menu_items])

@routes.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    data = request.json
    
    items = []
    total_price = 0
    is_service = False
    
    # First check if we have enough stock for all items
    for item_data in data['items']:
        menu_item = MenuItem.query.get(item_data['id'])
        if not menu_item:
            return jsonify({"error": f"Item not found: {item_data['id']}"}), 404
            
        if menu_item.track_stock and menu_item.stock is not None:
            if menu_item.stock < item_data['quantity']:
                return jsonify({
                    "error": f"Not enough stock for {menu_item.name}. Available: {menu_item.stock}"
                }), 400
    
    # If we have enough stock, process the order
    order_items = []
    for item_data in data['items']:
        menu_item = MenuItem.query.get(item_data['id'])
        
        if menu_item.category == 'service':
            is_service = True
        
        # Update stock if needed
        if menu_item.track_stock and menu_item.stock is not None:
            menu_item.stock -= item_data['quantity']
        
        order_items.append({
            'id': menu_item.id,
            'name': menu_item.name,
            'price': menu_item.price,
            'quantity': item_data['quantity']
        })
        total_price += menu_item.price * item_data['quantity']
    
    order = Order(
        user_id=user.id,
        table_number=user.table_number,
        items=order_items,
        total_price=total_price,
        status='Pending',
        is_service=is_service
    )
    
    db.session.add(order)
    
    try:
        db.session.commit()
        return jsonify({"message": "Order created successfully", "order_id": order.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@routes.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    current_user = get_jwt_identity()
    user = User.query.get(int(current_user))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Filter orders based on user role
    if user.role == 'table':
        orders = Order.query.filter_by(table_number=user.table_number).all()
    else:
        orders = Order.query.all()

    return jsonify([order.to_dict() for order in orders])

# 3. Simulate Payment
@routes.route('/payments', methods=['POST'])
def process_payment():
    data = request.json
    order_id = data['order_id']
    amount = data['amount']

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != Order.STATUS_PENDING:
        return jsonify({
            "error": f"Order is {order.status}. Only pending orders can be paid."
        }), 400

    existing_payment = Payment.query.filter_by(
        order_id=order_id, 
        status="Success"
    ).first()
    
    if existing_payment:
        return jsonify({
            "error": "Order has already been paid",
            "payment_id": existing_payment.id,
            "paid_at": existing_payment.created_at.isoformat()
        }), 400

    if amount < order.total_price:
        return jsonify({"error": "Insufficient payment"}), 400

    payment = Payment(order_id=order_id, amount=amount, status="Success")
    db.session.add(payment)
    order.status = Order.STATUS_PAID  # Order is paid but not yet completed
    db.session.commit()

    return jsonify({
        "order_id": order_id,
        "amount": amount,
        "status": "Success",
        "order_status": order.status,
        "created_at": payment.created_at.isoformat(),
        "updated_at": payment.updated_at.isoformat(),
        "next_steps": ["Mark as completed when order is fulfilled"]
    })

# 4. Update Order Status
@routes.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    try:
        # Get the current user's ID from JWT
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role', None)
        
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        data = request.get_json()
        order = Order.query.get_or_404(order_id)
        
        order.status = data['status']
        
        # Assign staff when accepting order
        if user_role == 'staff' and data['status'] == 'Accepted':
            order.staff_id = user.id
            order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': order.id,
            'status': order.status,
            'staff_id': order.staff_id,
            'staff_name': order.staff.username if order.staff else None
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating order status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@routes.route('/orders/<int:order_id>/status', methods=['OPTIONS'])
def order_status_options(order_id):
    response = jsonify({'message': 'OK'})
    response.headers.add('Access-Control-Allow-Methods', 'PUT')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

@routes.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    return jsonify([{
        "id": payment.id,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "status": payment.status
    } for payment in payments])

# Process Refund
@routes.route('/refunds', methods=['POST'])
@role_required([User.ROLE_ADMIN])
def process_refund():
    data = request.json
    order_id = data['order_id']
    
    # Find the order
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
        
    # Check if order is in a refundable state (must be Paid)
    if order.status != "Paid":
        return jsonify({"error": "Order is not in a refundable state"}), 400
        
    # Find the original payment
    original_payment = Payment.query.filter_by(order_id=order_id, status="Success").first()
    if not original_payment:
        return jsonify({"error": "No successful payment found for this order"}), 400
        
    # Create refund record
    refund = Payment(
        order_id=order_id,
        amount=-original_payment.amount,  # Negative amount indicates refund
        status="Refunded"
    )
    
    order.status = "Refunded"
    db.session.add(refund)
    db.session.commit()
    
    return jsonify({
        "order_id": order_id,
        "refund_amount": original_payment.amount,
        "status": "Refunded",
        "created_at": refund.created_at.isoformat(),
        "updated_at": refund.updated_at.isoformat()
    })

# Get Single Order
@routes.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    return jsonify({
        "id": order.id,
        "items": [{"id": item.id, "name": item.name, "price": item.price} for item in order.items],
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat()
    })

@routes.route('/auth/qr', methods=['POST'])
def qr_auth():
    data = request.json
    table_number = data.get('tableNumber')
    token = data.get('token')
    
    try:
        token_parts = token.split('-')
        if len(token_parts) != 3 or token_parts[0] != str(table_number):
            return jsonify({"error": "Invalid token"}), 401
            
        timestamp = int(token_parts[1])
        if (time.time() * 1000 - timestamp) > 86400000:  # 24 hours in milliseconds
            return jsonify({"error": "Token expired"}), 401
            
        # Find the table user
        table_user = User.query.filter_by(table_number=int(table_number)).first()
        if not table_user:
            return jsonify({"error": "Table not found"}), 404
            
        access_token = create_access_token(
            identity=table_user.id,  # Use the user ID instead of table number
            additional_claims={"role": "table", "table_number": table_number}
        )
        
        response = make_response(jsonify({
            "access_token": access_token,
            "role": "table",
            "table_number": table_number
        }))
        
        origin = request.headers.get('Origin')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
            
    except (ValueError, AttributeError):
        return jsonify({"error": "Invalid token format"}), 401
