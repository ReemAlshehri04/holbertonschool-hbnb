from app.services.Database.database import Base, get_session
from sqlalchemy import Table, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models import BaseModel

class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner_id: str):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude

        if not owner_id:
            raise ValueError("owner_id is required")
        self.owner_id = str(owner_id)

        self.reviews = []      # list of Review instances
        self.amenities = []    # list of Amenity instances

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not value or len(value) > 100:
            raise ValueError("title is required and must be <= 100 characters")
        self._title = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value is None or value < 0:
            raise ValueError("price must be a positive value")
        self._price = float(value)

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        if value is None or value < -90.0 or value > 90.0:
            raise ValueError("latitude must be between -90.0 and 90.0")
        self._latitude = float(value)

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        if value is None or value < -180.0 or value > 180.0:
            raise ValueError("longitude must be between -180.0 and 180.0")
        self._longitude = float(value)

    def add_review(self, review):
        from app.models.review import Review
        if not isinstance(review, Review):
            raise ValueError("review must be a Review instance")
        self.reviews.append(review)

    def add_amenity(self, amenity):
        from app.models.amenity import Amenity
        if not isinstance(amenity, Amenity):
            raise ValueError("amenity must be an Amenity instance")
        self.amenities.append(amenity)

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': str(self.owner_id),
            'amenities': [str(a.id) for a in self.amenities],
            'created_at': self.created_at.isoformat() if getattr(self, 'created_at', None) else None,
            'updated_at': self.updated_at.isoformat() if getattr(self, 'updated_at', None) else None
        }



place_amenity = Table(
    "place_amenity",
    Base.metadata,
    Column("place_id", String(36), ForeignKey("places.id"), primary_key=True),
    Column("amenity_id", String(36), ForeignKey("amenities.id"), primary_key=True)
)

Place.reviews_rel = relationship(
    "Review",
    back_populates="place",
    cascade="all, delete-orphan"
)

Place.amenities_rel = relationship(
    "Amenity",
    secondary=place_amenity,
    back_populates="places_rel"
)

from app.models.review import Review
Review.place = relationship(
    "Place",
    back_populates="reviews_rel"
)

from app.models.amenity import Amenity
Amenity.places_rel = relationship(
    "Place",
    secondary=place_amenity,
    back_populates="amenities_rel"
)
