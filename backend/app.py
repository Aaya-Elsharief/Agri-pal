from flask import Flask, jsonify
from pymongo import MongoClient
from config import Config
from routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # MongoDB connection
    mongo_client = MongoClient(app.config['MONGODB_URI'])
    app.db = mongo_client[app.config['MONGODB_DB']]
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/user')
    
    @app.route('/')
    def home():
        return "Hello, Agri-pal!"
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)