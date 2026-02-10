from flask import Blueprint, request, jsonify
from modules.products.services import OrderService
from config import SessionLocal

#Create a Blueprint for orders
orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """
    Create a new order
    
    Endpoint: POST /api/orders/
    
    Expected JSON body:
    {
        "user_id": 1,
        "items": [
            {
                "product_id": 5,
                "quantity": 2
            },
            {
                "product_id": 10,
                "quantity": 1
            }
        ],
        "shipping_address": "123 Main St, City, State 12345"  (optional)
    }
    """
    db = SessionLocal()
    try:
        data = request.get_json()

        required_fields = ['user_id', 'items']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        #validate items
        if not data['items'] or not isinstance(data['items'], list):
            return jsonify({"error": "Items must be a non-empty list"}), 400
        #db: Session, user_id: int, items: List[Dict], shipping_address: str = None) -> Optional[Order]
        order = OrderService.create_order(
            db,
            user_id = data['user_id'],
            items = data['items'],
            shipping_address = data.get('shipping_address')
        )
        if not order:
            return jsonify({"error": "Failed to create order."}), 400
        
        return jsonify({order._to_dict()}), 201
    
    except ValueError as ve:
         # ValueError is raised for business logic errors (e.g., insufficient stock)
        return jsonify({"error": str(ve)}), 400
    
    except Exception as e:
        #Any other unexpected errors
        db.rollback()
        return jsonify({"error": "An error occurred while creating the order."}), 500
    finally:
        db.close()

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Get order details by order ID
    
    Endpoint: GET /api/orders/<order_id>
    """
    db = SessionLocal()
    try:
       order = OrderService.get_order_by_id(db, order_id)
       if not order:
           return jsonify({"error": "Order not found."}), 404
       return jsonify(order.to_dict()), 200
    
    finally:
        db.close()

@orders_bp.route('/orders/<int:user_id>', methods=['GET'])
def get_user_orders(user_id_):
    """
    Get all of the orders for a specific user by user ID
    Endpoint: GET /api/orders/user/5?skip=0&limit=10

    URL Parameters:
    skip: Number of records to skeip (default: 0)
    limit: Number of records to return (default: 10)


    """
    db=SessionLocal()
    try:
        skip = request.args.get('skip', default=0, type=int)
        limit = request.args.get('limit', default= 10, type=int)

        #get all orders
        orders = OrderService.get_all_orders(db,skip,limit)
        return jsonify([order.to_dict() for order in orders]), 200
    finally:
        db.close()

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """
    Update order status
    Engpoint: PUT /api/orders/5/status

    Expected JSON body:
    {
        "status": "shipped"
    }
    valid status values: pending,processing, shipped, delivered, cancelled

    
    Returns:
    200: Updated order details
    400: Missing status field
    404: Order not found
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        if 'status' not in data:
            return jsonify({"error": "Missing status field"}), 400
        order = OrderService.update_order_status(db, order_id, data['status'])
        if not order:
            return jsonify({"error": "Order not found."}), 404
        
        return jsonify(order.to_dict()), 200
    
    except Exception as e:
        db.rollback()
        return jsonify({"error": "An error occurred while updating the order status."}), 500
    finally:
        db.close()

@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """
    Cancel an order and restore stock

    Endpoint: POST /api/orders/5/cancel

    What happens when an order is cancelled:
    1. Check if order exists and is in a cancellable state (pending or processing)
    2. Restore stock for each item in the order
    3. Update order status to cancelled
    
    """
    db = SessionLocal()
    try:
        #call service to cancel order
        # The service handles:
        # - Checking if order exists
        # - Verifying order can be cancelled
        # - Restoring stock
        # - Updating status
        success = OrderService.cancel_order(db, order_id)
        if not success:
            return jsonify({'error': 'Order not found or cannot be cancelled. Only '}), 400
        return jsonify({'message': 'Order cancelled successfully.'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": "An error occurred while cancelling the order."}), 500
    finally:
        db.close()
