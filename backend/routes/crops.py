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

@crops_bp.route('/<crop_id>', methods=['PUT'])
@verify_token
def update_crop(current_user_id, current_user_role, crop_id):
    if current_user_role != "farmer":
        return jsonify({"error": "Only farmers can update crops"}), 403
    
    try:
        data = request.get_json(force=True)
    except:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Check if crop exists and belongs to user
        crop = current_app.db.crops.find_one({
            "_id": ObjectId(crop_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if not crop:
            return jsonify({"error": "Crop not found or access denied"}), 404
        
        # Update crop document
        update_data = {}
        allowed_fields = ['crop_type', 'quantity', 'price', 'location', 'harvest_date']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            current_app.db.crops.update_one(
                {"_id": ObjectId(crop_id)},
                {"$set": update_data}
            )
        
        # Get updated crop
        updated_crop = current_app.db.crops.find_one({"_id": ObjectId(crop_id)})
        updated_crop['_id'] = str(updated_crop['_id'])
        updated_crop['user_id'] = str(updated_crop['user_id'])
        
        return jsonify({
            "message": "Crop updated successfully",
            "crop": updated_crop
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@crops_bp.route('/', methods=['GET'])
@verify_token
def get_crops(current_user_id, current_user_role):
    if current_user_role != "farmer":
        return jsonify({"error": "Only farmers can view crops"}), 403
    
    try:
        crops = list(current_app.db.crops.find(
            {"user_id": ObjectId(current_user_id)}
        ).sort("created_at", -1))
        
        # Convert ObjectIds to strings
        for crop in crops:
            crop['_id'] = str(crop['_id'])
            crop['user_id'] = str(crop['user_id'])
        
        return jsonify({"crops": crops}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@crops_bp.route('/<crop_id>', methods=['DELETE'])
@verify_token
def delete_crop(current_user_id, current_user_role, crop_id):
    if current_user_role != "farmer":
        return jsonify({"error": "Only farmers can delete crops"}), 403
    
    try:
        result = current_app.db.crops.delete_one({
            "_id": ObjectId(crop_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({"error": "Crop not found or access denied"}), 404
        
        return jsonify({"message": "Crop deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@crops_bp.route('/marketplace', methods=['GET'])
def get_marketplace():
    try:
        # Build query filters
        query = {}
        
        # Search filters from query parameters
        crop_type = request.args.get('crop_type')
        location = request.args.get('location')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        
        if crop_type:
            query['crop_type'] = {'$regex': crop_type, '$options': 'i'}
        if location:
            query['location'] = {'$regex': location, '$options': 'i'}
        if min_price:
            query['price'] = query.get('price', {})
            query['price']['$gte'] = float(min_price)
        if max_price:
            query['price'] = query.get('price', {})
            query['price']['$lte'] = float(max_price)
        
        # Get crops with farmer info
        pipeline = [
            {'$match': query},
            {'$lookup': {
                'from': 'users',
                'localField': 'user_id',
                'foreignField': '_id',
                'as': 'farmer'
            }},
            {'$unwind': '$farmer'},
            {'$project': {
                '_id': 1,
                'crop_type': 1,
                'quantity': 1,
                'price': 1,
                'location': 1,
                'harvest_date': 1,
                'created_at': 1,
                'farmer.full_name': 1,
                'farmer.phone': 1,
                'farmer.location': 1
            }},
            {'$sort': {'created_at': -1}}
        ]
        
        crops = list(current_app.db.crops.aggregate(pipeline))
        
        # Convert ObjectIds to strings
        for crop in crops:
            crop['_id'] = str(crop['_id'])
        
        return jsonify({"crops": crops}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@crops_bp.route('/<crop_id>/offer', methods=['POST'])
@verify_token
def create_offer(current_user_id, current_user_role, crop_id):
    if current_user_role != "trader":
        return jsonify({"error": "Only traders can create offers"}), 403
    
    try:
        data = request.get_json(force=True)
    except:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    if not data or not data.get('offered_price'):
        return jsonify({"error": "Offered price is required"}), 400
    
    try:
        # Check if crop exists
        crop = current_app.db.crops.find_one({"_id": ObjectId(crop_id)})
        if not crop:
            return jsonify({"error": "Crop not found"}), 404
        
        # Get trader info
        trader = current_app.db.users.find_one(
            {"_id": ObjectId(current_user_id)},
            {"full_name": 1, "phone": 1}
        )
        
        # Create offer document
        offer_doc = {
            "crop_id": ObjectId(crop_id),
            "trader_id": ObjectId(current_user_id),
            "offered_price": data['offered_price'],
            "trader_name": trader['full_name'],
            "trader_phone": trader['phone'],
            "created_at": datetime.utcnow()
        }
        
        result = current_app.db.offers.insert_one(offer_doc)
        offer_doc['_id'] = str(result.inserted_id)
        offer_doc['crop_id'] = str(offer_doc['crop_id'])
        offer_doc['trader_id'] = str(offer_doc['trader_id'])
        
        return jsonify({
            "message": "Offer created successfully",
            "offer": offer_doc
        }), 201
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@crops_bp.route('/<crop_id>/offers', methods=['GET'])
@verify_token
def get_crop_offers(current_user_id, current_user_role, crop_id):
    if current_user_role != "farmer":
        return jsonify({"error": "Only farmers can view crop offers"}), 403
    
    try:
        # Check if crop exists and belongs to farmer
        crop = current_app.db.crops.find_one({
            "_id": ObjectId(crop_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if not crop:
            return jsonify({"error": "Crop not found or access denied"}), 404
        
        # Get all offers for this crop
        offers = list(current_app.db.offers.find(
            {"crop_id": ObjectId(crop_id)}
        ).sort("offered_price", -1))
        
        # Convert ObjectIds to strings
        for offer in offers:
            offer['_id'] = str(offer['_id'])
            offer['crop_id'] = str(offer['crop_id'])
            offer['trader_id'] = str(offer['trader_id'])
        
        return jsonify({"offers": offers}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@crops_bp.route('/offers/', methods=['GET'])
@verify_token
def get_offers(current_user_id, current_user_role):
    if current_user_role != "trader":
        return jsonify({"error": "Only traders can view their offers"}), 403
    
    try:
        # Get trader's offers with crop details
        pipeline = [
            {'$match': {'trader_id': ObjectId(current_user_id)}},
            {'$lookup': {
                'from': 'crops',
                'localField': 'crop_id',
                'foreignField': '_id',
                'as': 'crop'
            }},
            {'$unwind': '$crop'},
            {'$sort': {'created_at': -1}}
        ]
        
        offers = list(current_app.db.offers.aggregate(pipeline))
        
        # Convert ObjectIds to strings
        for offer in offers:
            offer['_id'] = str(offer['_id'])
            offer['crop_id'] = str(offer['crop_id'])
            offer['trader_id'] = str(offer['trader_id'])
            offer['crop']['_id'] = str(offer['crop']['_id'])
            offer['crop']['user_id'] = str(offer['crop']['user_id'])
        
        return jsonify({"offers": offers}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@crops_bp.route('/offers/<offer_id>', methods=['PUT'])
@verify_token
def update_offer(current_user_id, current_user_role, offer_id):
    if current_user_role != "trader":
        return jsonify({"error": "Only traders can update offers"}), 403
    
    try:
        data = request.get_json(force=True)
    except:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    if not data or not data.get('offered_price'):
        return jsonify({"error": "Offered price is required"}), 400
    
    try:
        # Check if offer exists and belongs to trader
        offer = current_app.db.offers.find_one({
            "_id": ObjectId(offer_id),
            "trader_id": ObjectId(current_user_id)
        })
        
        if not offer:
            return jsonify({"error": "Offer not found or access denied"}), 404
        
        # Update offer
        current_app.db.offers.update_one(
            {"_id": ObjectId(offer_id)},
            {"$set": {
                "offered_price": data['offered_price'],
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Get updated offer
        updated_offer = current_app.db.offers.find_one({"_id": ObjectId(offer_id)})
        updated_offer['_id'] = str(updated_offer['_id'])
        updated_offer['crop_id'] = str(updated_offer['crop_id'])
        updated_offer['trader_id'] = str(updated_offer['trader_id'])
        
        return jsonify({
            "message": "Offer updated successfully",
            "offer": updated_offer
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@crops_bp.route('/offers/<offer_id>', methods=['DELETE'])
@verify_token
def delete_offer(current_user_id, current_user_role, offer_id):
    if current_user_role != "trader":
        return jsonify({"error": "Only traders can delete offers"}), 403
    
    try:
        result = current_app.db.offers.delete_one({
            "_id": ObjectId(offer_id),
            "trader_id": ObjectId(current_user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({"error": "Offer not found or access denied"}), 404
        
        return jsonify({"message": "Offer deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500