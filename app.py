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
        'message': "E--commerce AI Platform API is running"
    })