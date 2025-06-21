from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from datetime import datetime
from utils.verify_token import verify_token

crops_bp = Blueprint('crops', __name__)

@crops_bp.route('/', methods=['POST'])
@verify_token
def create_crop(current_user_id, current_user_role):
    if current_user_role != "farmer":
        return jsonify({"error": "Only farmers can create crops"}), 403
    
    try:
        data = request.get_json(force=True)
    except:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ['crop_type', 'quantity', 'price', 'location', 'harvest_date']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    try:
        # Create crop document
        crop_doc = {
            "crop_type": data['crop_type'],
            "quantity": data['quantity'],
            "price": data['price'],
            "location": data['location'],
            "harvest_date": data['harvest_date'],
            "user_id": ObjectId(current_user_id),
            "created_at": datetime.utcnow()
        }
        
        result = current_app.db.crops.insert_one(crop_doc)
        crop_doc['_id'] = str(result.inserted_id)
        crop_doc['user_id'] = str(crop_doc['user_id'])
        
        return jsonify({
            "message": "Crop created successfully",
            "crop": crop_doc
        }), 201
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500