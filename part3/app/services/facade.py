from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from app.persistence.repository import InMemoryRepository


class HBnBFacade:
    """
    Facade pattern: single entry point for all business logic.
    The Presentation layer talks only to this class.
    """

    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()

    # ------------------------------------------------------------------ #
    #  User                                                              #
    # ------------------------------------------------------------------ #

def create_user(self, user_data):
    user = User(
        first_name=user_data.get('first_name', ''),
        last_name=user_data.get('last_name', ''),
        email=user_data.get('email', ''),
        password='',          # placeholder; will be hashed below
        is_admin=user_data.get('is_admin', False)
    )
    user.hash_password(user_data.get('password', ''))
    self.user_repo.add(user)
    return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        if not user:
            return None
        user.update(user_data)
        return user

    # ------------------------------------------------------------------ #
    #  Amenity                                                           #
    # ------------------------------------------------------------------ #

    def create_amenity(self, amenity_data):
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
        amenity.update(amenity_data)
        return amenity

    # ------------------------------------------------------------------ #
    #  Place                                                             #
    # ------------------------------------------------------------------ #

    def create_place(self, place_data):
        owner_id = place_data.get('owner_id', '')
        if not self.user_repo.get(owner_id):
            raise ValueError("Owner not found")

        price = place_data.get('price', 0)
        latitude = place_data.get('latitude', 0.0)
        longitude = place_data.get('longitude', 0.0)

        if price < 0:
            raise ValueError("Price must be non-negative")
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError("Longitude must be between -180 and 180")

        place = Place(
            title=place_data.get('title', '').strip(),
            description=place_data.get('description', ''),
            price=price,
            latitude=latitude,
            longitude=longitude,
            owner_id=owner_id
        )

        # Validate amenities
        for aid in place_data.get('amenities', []):
            amenity = self.amenity_repo.get(aid)
            if not amenity:
                raise ValueError(f"Amenity '{aid}' not found")
            if amenity not in place.amenities:
                place.amenities.append(amenity)

        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.place_repo.get(place_id)
        if not place:
            return None

        # Validate numeric fields
        if 'price' in place_data and place_data['price'] < 0:
            raise ValueError("Price must be non-negative")
        if 'latitude' in place_data and not (-90.0 <= place_data['latitude'] <= 90.0):
            raise ValueError("Latitude must be between -90 and 90")
        if 'longitude' in place_data and not (-180.0 <= place_data['longitude'] <= 180.0):
            raise ValueError("Longitude must be between -180 and 180")

        # Validate amenities
        if 'amenities' in place_data:
            amenity_ids = place_data.pop('amenities')
            place.amenities = []
            for aid in amenity_ids:
                amenity = self.amenity_repo.get(aid)
                if not amenity:
                    raise ValueError(f"Amenity '{aid}' not found")
                place.amenities.append(amenity)

        place.update(place_data)
        return place

    # ------------------------------------------------------------------ #
    #  Review                                                            #
    # ------------------------------------------------------------------ #

    def create_review(self, review_data):
        user_id = review_data.get('user_id', '')
        place_id = review_data.get('place_id', '')
        text = review_data.get('text', '').strip()
        rating = review_data.get('rating')

        if not self.user_repo.get(user_id):
            raise ValueError("User not found")
        if not self.place_repo.get(place_id):
            raise ValueError("Place not found")
        if not text:
            raise ValueError("Review text is required")
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            raise ValueError("Rating must be an integer between 1 and 5")

        review = Review(text=text, rating=rating, place_id=place_id, user_id=user_id)
        self.review_repo.add(review)

        place = self.place_repo.get(place_id)
        if place:
            place.reviews.append(review)

        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        return [r for r in self.review_repo.get_all() if r.place_id == place_id]

    def update_review(self, review_id, review_data):
        review = self.review_repo.get(review_id)
        if not review:
            return None

        # Validate text
        if 'text' in review_data:
            if not review_data['text'] or not str(review_data['text']).strip():
                raise ValueError("text is required")

        # Validate rating
        if 'rating' in review_data:
            rating = review_data['rating']
            if not isinstance(rating, int) or not (1 <= rating <= 5):
                raise ValueError("Rating must be an integer between 1 and 5")

        # Only allow updating text and rating
        allowed = {k: v for k, v in review_data.items() if k in ('text', 'rating')}
        review.update(allowed)
        return review

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        if not review:
            return False

        place = self.place_repo.get(review.place_id)
        if place:
            place.reviews = [r for r in place.reviews if r.id != review_id]

        self.review_repo.delete(review_id)
        return True
