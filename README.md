# 🌾 Agri-pal - Agricultural Marketplace

A web application that connects **farmers** and **traders** in an agricultural marketplace.  
Farmers can list their crops, traders can browse and submit price offers, creating a competitive marketplace.

---

## 🚀 Features

### 👨‍🌾 Farmer Features
✅ User registration and JWT authentication  
✅ Create, update, delete crop listings  
✅ View trader offers on crops  
✅ Direct contact with traders  

### 👨‍💼 Trader Features
✅ Browse public marketplace  
✅ Filter crops by type, location, price  
✅ Submit competitive price offers  
✅ Manage offer portfolio  

### 🛒 Public Marketplace
✅ View all available crops  
✅ Search and filter functionality  
✅ Farmer contact information  

---

## 🛠 Tech Stack

| Layer       | Technology |
|-------------|------------|
| Frontend    | HTML / CSS / JS (served by Flask) |
| Backend API | Python Flask + JWT |
| Database    | MongoDB Atlas |
| Authentication | bcrypt + JWT tokens |
| Deployment  | Ready for cloud platforms |

---


## 🚀 Quick Start

### Backend API
See detailed setup and API documentation in [`backend/README.md`](./backend/README.md)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

## 📖 Documentation

- **Backend API**: [`backend/README.md`](./backend/README.md) - Complete API documentation with endpoints, authentication, and database schema

## 🔄 User Flow

### Farmer Journey
1. Register/Login → Get authenticated
2. Create crop listings → Manage inventory
3. Receive trader offers → Compare prices
4. Contact best traders → Complete deals

### Trader Journey
1. Register/Login → Get authenticated
2. Browse marketplace → Find crops
3. Submit competitive offers → Bid on crops
4. Manage offer portfolio → Track bids
5. Contact farmers → Negotiate deals

## 🌟 Key Benefits

- **Competitive Pricing**: Multiple traders bid on crops
- **Direct Communication**: Farmers and traders connect directly
- **Market Transparency**: Public marketplace with all listings
- **Secure Platform**: JWT authentication and role-based access
- **Mobile Ready**: Responsive design for all devices

