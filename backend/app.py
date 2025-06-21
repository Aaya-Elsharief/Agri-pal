from flask import Flask, jsonify
from pymongo import MongoClient
from config import Config
from routes.auth import auth_bp
from routes.crops import crops_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # MongoDB connection with error handling
    try:
        mongo_client = MongoClient(
            app.config['MONGODB_URI'],
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        # Test connection
        mongo_client.admin.command('ping')
        app.db = mongo_client[app.config['MONGODB_DB']]
        print(f"✅ Connected to MongoDB: {app.config['MONGODB_DB']}")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise e
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/user')
    app.register_blueprint(crops_bp, url_prefix='/api/crops')
    
    @app.route('/')
    def home():
        return "Hello, Agri-pal!"
    
    @app.route('/health')
    def health_check():
        try:
            # Test MongoDB connection
            app.db.command('ping')
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "message": "API is running"
            }), 200
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

# Create app instance for gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)