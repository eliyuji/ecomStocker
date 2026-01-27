"""
User API routes
"""
from flask import Blueprint, request, jsonify
from config.database import SessionLocal
from modules.auth.services import UserService
user_bp = Blueprint('users', __name__, url_prefix = '/api/users')

@user_bp.route('/', methods = ['POST'])
def create_user():
    db = SessionLocal()

    try:
        data = request.get_json()

        # Validate required fields
        if not all(k in data for k in['username','email','password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        #check if email already registered
        if UserService.get_user_by_email(db, data['email']):
            return jsonify({'error': 'email already registered'}), 400
        
        #check if username already taken
        if UserService.get_user_by_username(db, data['username']):
            return jsonify({'error': 'Username already used'}), 400
        
        #now safely create user

        user = UserService.create_user(
            db,
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )

        return jsonify ({user.to_dict()}), 201
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db = SessionLocal()

    try:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return jsonify ({'error': 'User not Found'}), 404

        return jsonify ({user.to_dict()}), 200
    finally:
        db.close()

@user_bp.route('/', methods=['GET'])
def get_all_users():
    db = SessionLocal()
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit',100, type=int)

        users = UserService.get_all_users(db,skip, limit)
        return jsonify ([users.to_dict() for user in users]), 200
    finally:
        db.close()

@user_bp.routes('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    db = SessionLocal()
    try:
        data = request.get_json()
        user = UserService.update_user(db, user_id, **data)

        if not user:
            return jsonify ({'error': 'User does not exist'}),404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@user_bp.routes('/<int:user_id', methods=['DELETE'])
def delete_user(user_id):
    db = SessionLocal()
    try:
        success = UserService.delete_user(db,user_id)
        if not success:
            return jsonify({'error': 'User does not exist'}), 404
        return jsonify({'message':'User successfully deleted'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@user_bp.route('/login', methods=['POST'])
def login():
    db = SessionLocal()
    try:
        data = request.get_json()

        if not all(k in data for k in ['email', 'password']):
            return jsonify ({'error': 'Missing email or password'}),400
        
        user = UserService.authenticate_user(db, data['email'],data['password'])
        if not user:
            return jsonify({'error': 'Invalid Credentials'}),401
        return jsonify (user.to_dict()), 200
    finally:
        db.close()

        
