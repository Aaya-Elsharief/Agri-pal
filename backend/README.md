# 🌾 Agri-pal Backend API

A Flask-based REST API for connecting farmers and traders in agricultural marketplace.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB
- pip

### Installation
```bash
# Clone and navigate
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .example.env .env
# Edit .env with your MongoDB URI

# Run the application
python app.py
```

Server runs on `http://localhost:5000`

## 🌐 Live Demo
**API Base URL**: https://agri-pal-1.onrender.com

**Test endpoints:**
- Health check: https://agri-pal-1.onrender.com/health
- Marketplace: https://agri-pal-1.onrender.com/api/crops/marketplace

## 📋 API Features

### 🔐 Authentication
- ✅ Register user (POST /api/user/register)
- ✅ Login user (POST /api/user/login)
- ✅ Get profile (GET /api/user/profile)

### 👨‍🌾 Farmer Features
- ✅ Register/Login with JWT
- ✅ Create crops (POST /api/crops)
- ✅ View my crops (GET /api/crops)
- ✅ Update crops (PUT /api/crops/<crop_id>)
- ✅ Delete crops (DELETE /api/crops/<crop_id>)
- ✅ View offers on my crops (GET /api/crops/<crop_id>/offers)

### 👨‍💼 Trader Features
- ✅ Register/Login with JWT
- ✅ Browse marketplace (GET /api/crops/marketplace)
- ✅ Filter/search crops (query parameters)
- ✅ Submit offers (POST /api/crops/<crop_id>/offer)
- ✅ View my offers (GET /api/crops/offers/)
- ✅ Update offers (PUT /api/crops/offers/<offer_id>)
- ✅ Delete offers (DELETE /api/crops/offers/<offer_id>)

### 🛒 Public Marketplace
- ✅ Browse all crops (no authentication required)
- ✅ Filter by crop_type, location, price range
- ✅ View farmer contact information
`


## 🔒 Security

- **JWT Authentication**: All protected routes require Bearer token
- **Role-based Access**: Farmers and traders have different permissions
- **Ownership Validation**: Users can only access their own resources
- **Password Hashing**: bcrypt for secure password storage

## 📁 Project Structure

```
backend/
├── models/
│   ├── __init__.py
│   └── user.py          # User model with CRUD operations
├── routes/
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   └── crops.py         # Crops and offers routes
├── utils/
│   ├── __init__.py
│   └── verify_token.py  # JWT verification decorator
├── app.py               # Flask application factory
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables
```

## 🌐 Environment Variables

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=agripal
```

## 📝 Response Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate username)
- `500` - Internal Server Error

## 🔄 User Flow

### Farmer Flow
1. Register/Login → Get JWT token
2. Create crops → Manage crop listings
3. View offers → See trader bids
4. Contact traders → Direct communication

### Trader Flow
1. Register/Login → Get JWT token
2. Browse marketplace → Find crops
3. Submit offers → Bid on crops
4. Manage offers → Update/cancel bids
5. Contact farmers → Direct communication

## 🛠️ Development

### Adding New Routes
1. Create route function in appropriate file
2. Use `@verify_token` decorator for protected routes
3. Validate user roles and ownership
4. Follow consistent error response format

### Testing
Use tools like Postman or curl to test endpoints with proper headers and JSON payloads.
