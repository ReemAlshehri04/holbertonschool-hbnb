from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import hashlib
import uuid
from datetime import datetime
import traceback
import os

app = Flask(__name__)

# --- إعدادات JWT ---
app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# --- تفعيل CORS (مهم جداً للتعامل مع المتصفحات) ---
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- تفعيل JWT ---
jwt = JWTManager(app)

# --- تخزين مؤقت في الذاكرة (In-memory storage) ---
users = {}  # email -> user object
places = {}  # id -> place object
reviews = {} # id -> review object

# ============= نماذج البيانات (Models) =============
class User:
    def __init__(self, email, password, first_name, last_name):
        self.id = str(uuid.uuid4())
        self.email = email
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def verify_password(self, password):
        return self.password == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }

class Place:
    def __init__(self, name, location, description, user_id):
        self.id = str(uuid.uuid4())
        self.name = name
        self.location = location
        self.description = description
        self.user_id = user_id
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'description': self.description
        }

# ============= إضافة بيانات تجريبية (Seed Data) =============
test_user = User("user@example.com", "password123", "Test", "User")
users[test_user.email] = test_user

places_data = [
    ("Eco Forest Cabin", "France", "A cozy cabin in the woods.", test_user.id),
    ("Modern Green Loft", "USA", "Eco-friendly loft in NYC.", test_user.id),
    ("Bamboo House", "Italy", "Sustainable living in Rome.", test_user.id)
]

for name, location, description, user_id in places_data:
    place = Place(name, location, description, user_id)
    places[place.id] = place

# ============= مسارات الواجهة الأمامية (Frontend) =============

@app.route('/')
def serve_index():
    """فتح صفحة تسجيل الدخول تلقائياً عند الدخول للرابط"""
    return send_from_directory('.', 'login.html')

@app.route('/<path:path>')
def serve_static(path):
    """خدمة بقية ملفات المشروع (CSS, JS, HTML)"""
    return send_from_directory('.', path)

# ============= مسارات الـ API =============

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "users_count": len(users),
        "places_count": len(places)
    }), 200

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email, password = data.get('email'), data.get('password')
        fn, ln = data.get('first_name'), data.get('last_name')
        
        if not all([email, password, fn, ln]):
            return jsonify({"error": "Missing fields"}), 400
        if email in users:
            return jsonify({"error": "User exists"}), 409
        
        user = User(email, password, fn, ln)
        users[email] = user
        return jsonify({"message": "User created", "user": user.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = users.get(data.get('email'))
        if not user or not user.verify_password(data.get('password')):
            return jsonify({"error": "Invalid credentials"}), 401
        
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token, "user": user.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/places', methods=['GET'])
@jwt_required()
def get_places():
    return jsonify([p.to_dict() for p in places.values()]), 200

@app.route('/api/v1/places/<place_id>', methods=['GET'])
@jwt_required()
def get_place(place_id):
    place = places.get(place_id)
    return jsonify(place.to_dict()) if place else (jsonify({"error": "Not found"}), 404)

@app.route('/api/v1/places/<place_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(place_id):
    data = request.get_json()
    review_id = str(uuid.uuid4())
    review = {
        "id": review_id,
        "place_id": place_id,
        "user_id": get_jwt_identity(),
        "rating": data.get('rating'),
        "comment": data.get('comment'),
        "created_at": datetime.utcnow().isoformat()
    }
    reviews[review_id] = review
    return jsonify({"message": "Review added", "review": review}), 201

# ============= تشغيل السيرفر =============

if __name__ == '__main__':
    # مهم جداً لـ Render: قراءة المنفذ من نظام التشغيل
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)