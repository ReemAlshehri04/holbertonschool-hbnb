from app.persistence.repository import SQLAlchemyRepository
from app import db # تأكدي من استيراد db هنا لعمل commit

class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        from app.models.user import User
        super().__init__(User)

    def get_user_by_email(self, email):
        return self.model.query.filter_by(email=email).first()

class AmenityRepository(SQLAlchemyRepository):
    def __init__(self):
        from app.models.amenity import Amenity
        super().__init__(Amenity)

class PlaceRepository(SQLAlchemyRepository):
    def __init__(self):
        from app.models.place import Place
        super().__init__(Place)

class ReviewRepository(SQLAlchemyRepository):
    def __init__(self):
        from app.models.review import Review
        super().__init__(Review)

    def get_by_user_and_place(self, user_id, place_id):
        return self.model.query.filter_by(
            user_id=str(user_id), place_id=str(place_id)
        ).first()

    def get_by_place(self, place_id):
        return self.model.query.filter_by(place_id=str(place_id)).all()

class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.amenity_repo = AmenityRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()

    # --- User Methods ---
    def create_user(self, user_data):
        from app.models.user import User
        import re

        email = user_data.get('email', '')
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValueError("Invalid email format")

        if self.get_user_by_email(email):
            raise ValueError("Email already registered")

        user = User(
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            email=email,
            password=user_data.get('password', ''),
            is_admin=user_data.get('is_admin', False)
        )
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        if not user:
            return None
        
        # استخدام setattr وتحديث قاعدة البيانات مباشرة
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit() # استخدام db المستورد مباشرة
        return user

    # --- Amenity Methods ---
    def create_amenity(self, amenity_data):
        from app.models.amenity import Amenity
        name = amenity_data.get('name', '').strip()
        if not name:
            raise ValueError("Amenity name is required")
        amenity = Amenity(name=name)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None
        for key, value in amenity_data.items():
            setattr(amenity, key, value)
        db.session.commit()
        return amenity

    # --- Place Methods ---
    def create_place(self, place_data):
        from app.models.place import Place
        owner_id = place_data.get('owner_id')
        owner = self.user_repo.get(owner_id)
        if not owner:
            raise ValueError("Owner not found")

        place = Place(
            title=place_data.get('title'),
            description=place_data.get('description'),
            price=place_data.get('price'),
            latitude=place_data.get('latitude'),
            longitude=place_data.get('longitude'),
            owner_id=owner_id
        )
        # ربط الـ Amenities
        for aid in place_data.get('amenities', []):
            amenity = self.amenity_repo.get(aid)
            if amenity:
                place.amenities.append(amenity)

        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()
