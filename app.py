"""
Main Flask Application
This is the entry point for the e-commerce AI platform API.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config.database import init_db
from modules.auth.routes import user_bp
from modules.orders.routes import orders_bp
from modules.products.routes import products_bp
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

app.register_blueprint(orders_bp)
app.register_blueprint(user_bp)
app.register_blueprint(products_bp)

#root endpoint
@app.route('/')
def home():
    return jsonify({
        'message': "E--commerce AI Platform API is running",
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'users': '/api//users',
            'products': '/api/products',
            'orders': '/api/orders',
            'health': '/api/health',
        },
        'documentation': 'See README.md for full API documentation'
    })
@app.route('/api/health')
def health():
    """
    He check endpoint
    URL GET /health

    Used by monitoring systems to check if the API is running
    Returns:
    200 if the server is healthy
    """
    return jsonify({'status': 'healthy'}), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with a JSON response"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested URL was not found on the server.',
        'status_code': 404
    }), 404
@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with a JSON response"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred on the server.',
        'status_code': 500
    }), 500
@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors with a JSON response"""
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'The method is not allowed for the requested URL.',
        'status_code': 405
    }), 405

if __name__ == '__main__':

    print("E-commerce AI Platform is starting up...")
    print("="*50)
    print("Initializing database...")

    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("  Make sure PostgreSQL is running and the connection settings in .env are correct.")
    
    host = os.getenv('API_HOST', '0.0.0.0')  # Default: listen on all interfaces
    port = int(os.getenv('API_PORT', 5000))   # Default: port 5000
    debug = os.getenv('FLASK_ENV') == 'development'  # Debug mode in development

    print(f"\nStarting server on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"\nAPI available at: http://localhost:{port}")
    print(f"Health check: http://localhost:{port}/health")
    print(f"\nPress CTRL+C to stop the server")
    print("=" * 60)
    print()