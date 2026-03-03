import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. استيراد القاعدة الأساسية (Base)
from app.services.Database.database import Base

# 2. استيراد الموديلات (الترتيب مهم لضمان تسجيل الجداول في Metadata)
from app.models.user import User
from app.models.amenity import Amenity
from app.models.review import Review
from app.models.place import Place, place_amenity

# 3. إعداد المحرك (Engine) والجلسة (Session)
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)
session = Session()

print("--- 🔍 Checking SQLAlchemy Metadata ---")
# التأكد من أن SQLAlchemy رأى كل الجداول قبل البدء
print(f"Registered tables: {list(Base.metadata.tables.keys())}")

print("\n--- 🔨 Creating Tables ---")
try:
    # إنشاء الجداول في الذاكرة
    Base.metadata.create_all(engine)
    print("✅ Tables created successfully!")

    # 4. بدء الاختبار العملي (تجهيز البيانات)
    print("\n--- 🧪 Running Task 8 Relationship Tests ---")

    # أ. إنشاء مستخدم (المالك)
    u = User(
        email="owner@test.com", 
        password="securepassword123", 
        first_name="Ali", 
        last_name="Ahmed"
    )
    session.add(u)
    session.flush() # الحصول على ID المستخدم قبل المتابعة

    # ب. إنشاء مكان (Place) وربطه بالمستخدم
    p = Place(
        title="Luxury Villa", 
        description="A beautiful villa by the sea", 
        price=250.0, 
        latitude=24.7136, 
        longitude=46.6753, 
        owner_id=u.id
    )
    session.add(p)
    session.flush()

    # ج. إضافة ميزة (Amenity) - علاقة Many-to-Many
    wifi = Amenity(name="High Speed WiFi")
    session.add(wifi)
    session.flush()
    p.amenities_rel.append(wifi) # الربط عبر علاقة SQLAlchemy

    # د. إضافة تقييم (Review) - علاقة One-to-Many
    rev = Review(
        text="Amazing stay, highly recommended!", 
        rating=5, 
        user_id=u.id, 
        place_id=p.id
    )
    session.add(rev)
    
    # حفظ التغييرات
    session.commit()
    
    # 5. التحقق من صحة العلاقات (Verification)
    # نستخدم session.refresh لضمان تحديث الكائنات بعد الـ commit
    session.refresh(p)
    session.refresh(u)

    print(f"Testing Place: {p.title}")
    
    # اختبار العلاقة مع المالك
    if p.owner and p.owner.email == "owner@test.com":
        print(f"✅ Relationship (Place -> User) works! Owner: {p.owner.first_name}")

    # اختبار العلاقة مع المميزات (Many-to-Many)
    if len(p.amenities_rel) > 0:
        print(f"✅ Relationship (Place <-> Amenity) works! Found: {p.amenities_rel[0].name}")

    # اختبار العلاقة مع التقييمات (One-to-Many)
    if len(p.reviews_rel) > 0:
        print(f"✅ Relationship (Place -> Review) works! Review: '{p.reviews_rel[0].text}'")

    # اختبار العلاقة العكسية للمستخدم
    if len(u.places) > 0:
        print(f"✅ Back-Relationship (User -> Places) works! User owns {len(u.places)} place(s).")

    print("\n🌟 ALL TASK 8 TESTS PASSED SUCCESSFULLY! 🌟\n")

except Exception as e:
    print(f"\n❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
    session.rollback()
finally:
    # إغلاق الجلسة دائماً في النهاية
    session.close()
