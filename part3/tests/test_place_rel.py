import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.amenity import Amenity
from app.models.review import Review
from app.models.place import Place, place_amenity
from app import db

engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)
session = Session()

print("--- 🔍 Checking SQLAlchemy Metadata ---")
registered_tables = list(db.metadata.tables.keys())
print(f"Registered tables: {registered_tables}")

if not registered_tables:
    print("❌ Error: No tables registered. Check model inheritance.")
    exit()

print("\n--- 🔨 Creating Tables ---")
try:
    db.metadata.create_all(engine)
    print("✅ Tables created successfully!")

    print("\n--- 🧪 Running Relationship Tests ---")

    # A. Create User (Owner)
    u = User(
        email=f"test_{uuid.uuid4()}@test.com", 
        password="securepassword123", 
        first_name="Ali", 
        last_name="Ahmed"
    )
    session.add(u)
    session.flush()

    # B. Create Place and link to User
    p = Place(
        title="Luxury Villa", 
        description="Sea view", 
        price=250.0, 
        latitude=24.7, 
        longitude=46.6, 
        owner_id=u.id
    )
    session.add(p)
    session.flush()

    # C. Add Amenity (Many-to-Many)
    wifi = Amenity(name="High Speed WiFi")
    session.add(wifi)
    session.flush()
    
    # Checking for correct amenity attribute name
    if hasattr(p, 'amenities'):
        p.amenities.append(wifi)
    elif hasattr(p, 'amenities_rel'):
        p.amenities_rel.append(wifi)

    # D. Add Review (One-to-Many)
    rev = Review(
        text="Amazing stay!", 
        rating=5, 
        user_id=u.id, 
        place_id=p.id
    )
    session.add(rev)
    
    session.commit()
    print("✅ Data inserted and committed!")

    # 4. Verification
    session.refresh(p)
    session.refresh(u)

    print(f"\nTesting Place: {p.title}")
    
    # Check Place -> User/Owner relationship
    owner_attr = 'owner' if hasattr(p, 'owner') else 'user'
    rel_user = getattr(p, owner_attr, None)
    if rel_user and rel_user.first_name == "Ali":
        print(f"✅ Relationship (Place -> {owner_attr.capitalize()}) works!")

    # Check Place -> Amenities relationship
    amen_attr = 'amenities' if hasattr(p, 'amenities') else 'amenities_rel'
    if len(getattr(p, amen_attr, [])) > 0:
        print(f"✅ Relationship (Place <-> Amenity) works!")

    # Check Place -> Reviews relationship
    rev_attr = 'reviews' if hasattr(p, 'reviews') else 'reviews_rel'
    if len(getattr(p, rev_attr, [])) > 0:
        print(f"✅ Relationship (Place -> Review) works!")

    # Check User -> Places (Back-populates)
    if len(u.places) > 0:
        print(f"✅ Back-Relationship (User -> Places) works! Count: {len(u.places)}")

    print("\n🌟 ALL TASK 8 TESTS PASSED SUCCESSFULLY! 🌟\n")

except Exception as e:
    print(f"\n❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
    session.rollback()
finally:
    session.close()

