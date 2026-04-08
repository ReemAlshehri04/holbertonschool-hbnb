import uuid
from app import db
from .basemodel import BaseModel
from sqlalchemy.orm import validates

# Task 8: Association table for Many-to-Many using the shared db instance
# This replaces the Table(..., Base.metadata, ...) approach
place_amenity = db.Table(
    "place_amenity",
    db.Column("place_id", db.String(36), db.ForeignKey("places.id"), primary_key=True),
    db.Column("amenity_id", db.String(36), db.ForeignKey("amenities.id"), primary_key=True)
)

class Place(BaseModel):
    __tablename__ = "places"

    # Columns using the db instance
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    # Task 8: Relationship Mapping
    # Using strings ("Review", "Amenity") prevents early loading and circular imports
    
    reviews = db.relationship("Review", back_populates="place", cascade="all, delete-orphan")
    amenities = db.relationship("Amenity", secondary=place_amenity, back_populates="places")
    def __init__(self, title=None, description=None, price=0.0, latitude=0.0, longitude=0.0, owner_id=None, **kwargs):
        """
        Modified __init__ with default values to satisfy SQLAlchemy and test scripts
        """
        super().__init__(**kwargs)
        if title:
            self.title = title
        if description:
            self.description = description
        if price is not None:
            self.price = float(price)
        if latitude is not None:
            self.latitude = float(latitude)
        if longitude is not None:
            self.longitude = float(longitude)
        if owner_id:
            self.owner_id = owner_id
    
    # Validation logic using @validates instead of property setters for cleaner ORM behavior
    @validates('title')
    def validate_title(self, key, value):
        if not value or len(value) > 100:
            raise ValueError("title is required and must be <= 100 characters")
        return value

    @validates('price')
    def validate_price(self, key, value):
        if value is None or float(value) < 0:
            raise ValueError("price must be a positive value")
        return float(value)

    @validates('latitude')
    def validate_latitude(self, key, value):
        if value is None or not (-90.0 <= float(value) <= 90.0):
            raise ValueError("latitude must be between -90.0 and 90.0")
        return float(value)

    @validates('longitude')
    def validate_longitude(self, key, value):
        if value is None or not (-180.0 <= float(value) <= 180.0):
            raise ValueError("longitude must be between -180.0 and 180.0")
        return float(value)

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': str(self.owner_id),
            'amenities': [a.id for a in self.amenities],
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None
        }
