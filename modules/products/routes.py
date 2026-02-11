from flask import Blueprint, request, jsonify
from modules.products.services import ProductService
from config import SessionLocal

#Create a Blueprint for products
products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product
        Endpoint: POST /api/products/

        Expected JSON body:
    {
        "name": "Wireless Headphones",
        "price": 79.99,
        "category": "Electronics",          (optional)
        "subcategory": "Audio",             (optional)
        "description": "High quality...",   (optional)
        "brand": "AudioTech",               (optional)
        "stock_quantity": 50,               (optional, default: 0)
        "image_url": "http://..."           (optional)
        "year_manufactured": 1999
        "condition": "near-mint"
        "material": "plastic"
        "authenticity_verified": true"
    }
    
    Returns:
        201: Product created successfully
        400: Missing required fields
        500: Server error
    """
    db = SessionLocal()
    
    try:
        required_fields = ['name', 'price']
        data = request.get_json()
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        product = ProductService.create_product(
            db,
            name=data['name'],
            price=data['price'],
            category=data.get('category'),
            category=data.get('subcategory'),
            description = data.get('description'),
            brand=data.get('brand'),
            stock_quantity=data.get('stock_quantity', 0),
            image_url=data.get('image_url'),
            year_manufactured=data.get('year_manufactured'),
            condition=data.get('condition'),
            material=data.get('material'),
            authenticity_verified=data.get('authenticity_verified', False)

        )
        return jsonify({product.to_dict()}),201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Gets a product by ID
    Endpoint: GET/api/products/<product_id>
    Returns:
    200: Product found
    404: Product not found
    500: Server error
    """
    db = SessionLocal()
    try:
        product = ProductService.get_product_by_id(db, product_id)
        if product:
            return jsonify(product.to_dict()), 200
        else:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@products_bp.route('/products', methods=['GET'])
def get_all_products():
    """
    Gets all products with pagination
    Endpoint: GET /api/products?skip=0&limit=10
    Query Parameters:
    skip (int): Number of records to skip (default: 0)
    limit (int): Maximum number of records to return (default: 100)
    Returns:
    200: List of products
    """
    db = SessionLocal()
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        category_id = request.args.get('category_id', type=int)
        if category_id is not None:
            products = ProductService.get_products_by_category_id(db, category_id, skip, limit)
        else:
            products = ProductService.get_all_products(db, skip, limit)

        return jsonify([product.to_dict() for product in products]), 200
    finally:
        db.close()
@products_bp.route('/product/search', methods=['GET'])
def search_products():
    """Search for products by name, description, or brand
    Endpoint: GET /api/product/search?query=keyword&skip=0&limit=10
    Query Parameters:
    query (str): Search keyword (required)
    skip (int): Number of records to skip (default: 0)
    limit (int): Maximum number of records to return (default: 100)
    Returns:
    200: List of matching products
    400: Missing required query parameter
    500: Server error
    """
    db = SessionLocal()
    try:
        query = request.args.get('query')
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit',100, type=int)

        if not query:
            return jsonify({"error": "Missing required query parameter 'query'"}), 400
        products = ProductService.search_products(db, query, skip, limit)
        return jsonify([product.to_dict() for product in products]), 200
    finally:
        db.close()

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product information
    Endpoint: PUT /api/products/<product_id>
    URL Parameters:
        product_id: The ID of the product to update

    Expected JSON body: (any of the following fields):
    {
    "name": "Updated Product Name,
    "price": 99.99,
    "category": "Updated Category",
    stock_quantity": 100,}
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided for update"}), 400
        
        product = ProductService.update_product(db, product_id, **data)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(product.to_dict()), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Deletes a product (soft delete by setting is_active to False)

    URL Parameters:
    product_id: The ID of the product to delete

    NOTES: This is a soft delete. The product will not be removed from the database but will be marked as inactive.

    Returns:
    200: Product deleted successfully
    404: Product not found
    500: Server error
    """
    db = SessionLocal()
    try:
        success = ProductService.delete_product(db, product_id)
        if not success:
            return jsonify({"error": "Product not found"}), 404
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
"""
# Trinket-specific search
GET  /api/products/search?condition=mint&rarity=rare
GET  /api/products/trending            # What's selling hot right now
"""
