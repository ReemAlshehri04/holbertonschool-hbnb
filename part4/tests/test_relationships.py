from app import create_app, db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

app = create_app()

with app.app_context():
    # 1. Clear existing data for a clean test
    db.drop_all()
    db.create_all()

    print("--- Testing Task 8 Relationships ---")

    # 2. Create a User
    user = User(first_name="Reem", last_name="Alshehri", email="reem@test.com", password="hashed_password")
    db.session.add(user)

    # 3. Create a Place and link to User (One-to-Many)
    place = Place(title="Luxury Villa", description="Beautiful sea view", price=250.0, owner=user)
    db.session.add(place)

    # 4. Create an Amenity and link to Place (Many-to-Many)
    wifi = Amenity(name="High-speed WiFi")
    pool = Amenity(name="Private Pool")
    place.amenities.append(wifi)
    place.amenities.append(pool)

    # 5. Create a Review and link to Place and User (One-to-Many)
    review = Review(text="Amazing stay!", rating=5, user=user, place=place)
    db.session.add(review)

    db.session.commit()

    # --- VERIFICATION ---
    
    # Check User -> Places
    print(f"User '{user.first_name}' owns: {[p.title for p in user.places]}")
    
    # Check Place -> Owner
    print(f"Place '{place.title}' owner is: {place.owner.email}")

    # Check Place -> Amenities
    print(f"Place '{place.title}' has amenities: {[a.name for a in place.amenities]}")

    # Check Place -> Reviews
    print(f"Place '{place.title}' has reviews: {[r.text for r in place.reviews]}")

    # Check Review -> User & Place
    print(f"Review '{review.text}' written by: {review.user.first_name} for: {review.place.title}")

    print("--- Test Completed Successfully ---")

