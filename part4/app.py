from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import hashlib
import uuid
from datetime import datetime
import traceback

app = Flask(__name__)

# إعدادات JWT
app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# تفعيل CORS للسماح للمتصفح بالاتصال
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# تفعيل JWT
jwt = JWTManager(app)

# تخزين مؤقت في الذاكرة (بدون قاعدة بيانات)
users = {}  # email -> user object
places = {}  # id -> place object
reviews = {}  # id -> review object

# ============= نماذج البيانات =============
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

# ============= إضافة بيانات تجريبية =============
# إضافة مستخدم تجريبي
test_user = User("user@example.com", "password123", "Test", "User")
users[test_user.email] = test_user

# إضافة أماكن تجريبية
places_data = [
    ("برج إيفل", "France", "برج حديدي شهير في باريس، فرنسا", test_user.id),
    ("تمثال الحرية", "USA", "تمثال ضخم يرمز إلى الحرية في نيويورك", test_user.id),
    ("الكولوسيوم", "Italy", "مدرج روماني قديم في روما", test_user.id),
    ("ساغرادا فاميليا", "Spain", "كنيسة شهيرة في برشلونة", test_user.id),
    ("تاج محل", "India", "ضريح رخامي في أغرا", test_user.id)
]

for name, location, description, user_id in places_data:
    place = Place(name, location, description, user_id)
    places[place.id] = place

# ============= المسارات (Routes) =============

@app.route('/health', methods=['GET'])
def health_check():
    """التحقق من صحة السيرفر"""
    return jsonify({
        "status": "healthy",
        "message": "API is running!",
        "users_count": len(users),
        "places_count": len(places)
    }), 200

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """تسجيل مستخدم جديد"""
    try:
        data = request.get_json()
        print(f"📝 Register attempt: {data}")
        
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        # التحقق من الحقول المطلوبة
        if not all([email, password, first_name, last_name]):
            return jsonify({"error": "All fields are required: email, password, first_name, last_name"}), 400
        
        # التحقق من وجود المستخدم
        if email in users:
            return jsonify({"error": "User with this email already exists"}), 409
        
        # إنشاء مستخدم جديد
        user = User(email, password, first_name, last_name)
        users[email] = user
        
        print(f"✅ User created: {user.email}")
        
        return jsonify({
            "message": "User created successfully",
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        print(f"❌ Error in register: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """تسجيل الدخول والحصول على توكن"""
    try:
        data = request.get_json()
        print(f"🔐 Login attempt: {data.get('email')}")
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # البحث عن المستخدم
        user = users.get(email)
        if not user or not user.verify_password(password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # إنشاء التوكن
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        print(f"✅ User logged in: {user.email}")
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in login: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/places', methods=['GET'])
@jwt_required()
def get_places():
    """الحصول على جميع الأماكن (يتطلب توكن)"""
    try:
        places_list = [place.to_dict() for place in places.values()]
        return jsonify(places_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/places/<place_id>', methods=['GET'])
@jwt_required()
def get_place(place_id):
    """الحصول على تفاصيل مكان محدد"""
    try:
        place = places.get(place_id)
        if not place:
            return jsonify({"error": "Place not found"}), 404
        return jsonify(place.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/places/<place_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(place_id):
    """إضافة تقييم لمكان (يتطلب توكن)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        rating = data.get('rating')
        comment = data.get('comment')
        
        if not rating or not comment:
            return jsonify({"error": "Rating and comment are required"}), 400
        
        # التحقق من وجود المكان
        place = places.get(place_id)
        if not place:
            return jsonify({"error": "Place not found"}), 404
        
        # إنشاء تقييم جديد
        review_id = str(uuid.uuid4())
        review = {
            "id": review_id,
            "place_id": place_id,
            "user_id": user_id,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.utcnow().isoformat()
        }
        reviews[review_id] = review
        
        return jsonify({
            "message": "Review added successfully",
            "review": review
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/places/<place_id>/reviews', methods=['GET'])
@jwt_required()
def get_place_reviews(place_id):
    """الحصول على جميع تقييمات مكان محدد"""
    try:
        place_reviews = [r for r in reviews.values() if r['place_id'] == place_id]
        return jsonify(place_reviews), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """الصفحة الرئيسية للـ API"""
    return jsonify({
        "api": "HBnB API",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "register": "/api/v1/auth/register",
            "login": "/api/v1/auth/login",
            "places": "/api/v1/places",
            "place_details": "/api/v1/places/<place_id>",
            "add_review": "/api/v1/places/<place_id>/reviews"
        }
    }), 200

if __name__ == '__main__':
    print("🚀 Starting HBnB API Server...")
    print(f"📊 Initial data: {len(users)} users, {len(places)} places")
    print("📍 Server running on http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
