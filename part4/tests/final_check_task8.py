from app import create_app, db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
import uuid

app = create_app()

def generate_id():
    return str(uuid.uuid4())

with app.app_context():
    print("--- Start Testing Task 8 Relationships ---")
    
    # تنظيف قاعدة البيانات وإنشاؤها من جديد
    db.drop_all()
    db.create_all()

    try:
        # 1. إنشاء مستخدم (Owner)
        owner = User(id=generate_id(), first_name="Reem", last_name="Alshehri", email="reem@test.com", password="hash")
        db.session.add(owner)

        # 2. إنشاء مكان وربطه بالمستخدم (One-to-Many)
        place = Place(id=generate_id(), title="Beach House", price=150.0, owner=owner)
        db.session.add(place)

        # 3. إنشاء خدمات وربطها بالمكان (Many-to-Many)
        wifi = Amenity(id=generate_id(), name="WiFi")
        pool = Amenity(id=generate_id(), name="Pool")
        place.amenities.append(wifi)
        place.amenities.append(pool)

        # 4. إنشاء تقييم (One-to-Many)
        review = Review(id=generate_id(), text="Great place!", rating=5, user=owner, place=place)
        db.session.add(review)

        db.session.commit()

        # --- التحقق من المخرجات ---
        print(f"SUCCESS: User '{owner.first_name}' has {len(owner.places)} place(s).")
        print(f"SUCCESS: Place '{place.title}' has {len(place.amenities)} amenity(ies).")
        print(f"SUCCESS: Review was written by '{review.user.first_name}' for '{review.place.title}'.")
        
    except Exception as e:
        print(f"ERROR during relationship testing: {e}")
        db.session.rollback()

    print("--- End of Test ---")

