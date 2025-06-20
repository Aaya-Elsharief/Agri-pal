from datetime import datetime
import bcrypt
from pymongo.errors import DuplicateKeyError

class User:
    def __init__(self, db):
        self.collection = db.users
        # Create unique index on username
        self.collection.create_index("username", unique=True)
    
    def create_user(self, user_data):
        # Hash password
        password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Prepare user document
        user_doc = {
            "username": user_data['username'],
            "password": password_hash.decode('utf-8'),
            "role": user_data['role'],
            "full_name": user_data['full_name'],
            "phone": user_data['phone'],
            "location": user_data['location'],
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            result = self.collection.insert_one(user_doc)
            user_doc['_id'] = str(result.inserted_id)
            user_doc.pop('password')  # Remove password from response
            return {"success": True, "user": user_doc}
        except DuplicateKeyError:
            return {"success": False, "error": "Username already exists"}
    
    def validate_user_data(self, data):
        required_fields = ['username', 'password', 'role', 'full_name', 'phone', 'location']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return {"valid": False, "missing_fields": missing_fields}
        
        if data['role'] not in ['farmer', 'trader']:
            return {"valid": False, "error": "Role must be 'farmer' or 'trader'"}
        
        return {"valid": True}
    
    def authenticate_user(self, username, password):
        user = self.collection.find_one({"username": username})
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            user['_id'] = str(user['_id'])
            user.pop('password')  # Remove password from response
            return {"success": True, "user": user}
        else:
            return {"success": False, "error": "Invalid password"}