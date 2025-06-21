from flask import Blueprint, request, jsonify, current_app
from models.user import User
import jwt
from datetime import datetime, timedelta
from bson import ObjectId
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token is invalid"}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True)
    except:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        
        user_model = User(current_app.db)
        
        # Validate user data
        validation = user_model.validate_user_data(data)
        if not validation['valid']:
            if 'missing_fields' in validation:
                return jsonify({"error": f"Missing required fields: {', '.join(validation['missing_fields'])}"}), 400
            return jsonify({"error": validation['error']}), 400
        
        # Create user
        result = user_model.create_user(data)
        
        if result['success']:
            user = result['user']
            
            # Generate JWT token
            payload = {
                'id': user['_id'],
                'role': user['role'],
                'exp': datetime.utcnow() + timedelta(days=7)
            }
            token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                "message": "User registered successfully",
                "token": token,
                "user": user
            }), 201
        else:
            return jsonify({"error": result['error']}), 409
            
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True)
    except:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400
    
    try:
        user_model = User(current_app.db)
        
        # Authenticate user
        result = user_model.authenticate_user(data['username'], data['password'])
        
        if result['success']:
            user = result['user']
            
            # Generate JWT token
            payload = {
                'id': user['_id'],
                'role': user['role'],
                'exp': datetime.utcnow() + timedelta(days=7)
            }
            token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": user
            }), 200
        else:
            return jsonify({"error": result['error']}), 401
            
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    try:
        user = current_app.db.users.find_one(
            {"_id": ObjectId(current_user_id)}, 
            {"password": 0}
        )
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user['_id'] = str(user['_id'])
        return jsonify({"user": user}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500