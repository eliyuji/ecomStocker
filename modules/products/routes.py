from flask import Blueprint, request, jsonify
from modules.products.services import ProductService, VALID_CONDITIONS, VALID_RARITIES
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
            category_id=data.get("category_id"),
            description = data.get('description'),
            brand=data.get('brand'),
            stock_quantity=data.get('stock_quantity', 1),
            image_url=data.get('image_url'),

            year_manufactured=data.get('year_manufactured'),
            condition=data.get('condition'),
            material=data.get('material'),
            rarity=data.get('rarity'),
            authenticity_verified=data.get('authenticity_verified', False)

        )
        return jsonify(product.to_dict()),201
    except ValueError as ve:
        # Raised by validate_trinket_fields() in services.py
        return jsonify({'error': str(ve)}), 400
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

        condition = request.args.get('condition')
        rarity    = request.args.get('rarity')
        year_min  = request.args.get('year_min',  type=int)
        year_max  = request.args.get('year_max',  type=int)
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)
        category_id = request.args.get('category_id', type=int)

        if any([condition, rarity, year_min, year_max, price_min, price_max, category_id]):
            products = ProductService.filter_products(
                db, 
                condition=condition,
                rarity=rarity,
                year_min=year_min,
                year_max=year_max,
                price_min=price_min,
                price_max=price_max,
                skip=skip,
                limit=limit,
                category_id=category_id
            )

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

@products_bp.route('/conditions', methods=['GET'])
def get_conditions():
    """
    Returns the list of valid condition values.
    Useful for frontend dropdowns.

    GET /api/products/conditions

    Returns:
        200: { "conditions": ["mint", "near_mint", ...] }
    """
    return jsonify({"conditions": VALID_CONDITIONS}), 200   

def get_rarities():
    """
    Returns the list of valid rarity values.
    Useful for frontend dropdowns.

    GET /api/products/rarities

    Returns:
        200: { "rarities": ["common", "uncommon", ...] }
    """
    return jsonify({"rarities": VALID_RARITIES}), 200

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
