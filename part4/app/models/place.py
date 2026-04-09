from sqlalchemy.orm import validates
from .basemodel import BaseModel
from app.extensions import db

class Place(BaseModel):
    __tablename__ = "places"

    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    # ✅ استخدام اسم الكلاس "Review" كنص لتجنب الاستيراد الدائري
    reviews = db.relationship("Review", back_populates="place", cascade="all, delete-orphan")
    # إذا كان لديك علاقة مع Amenities:
    # amenities = db.relationship("Amenity", secondary="place_amenity", back_populates="places")

    def __init__(self, title='', description='', price=0.0, latitude=0.0, longitude=0.0, owner_id=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner_id

    @validates('title')
    def validate_title(self, key, value):
        if not value or not str(value).strip():
            raise ValueError("Title is required")
        return str(value).strip()

    @validates('price')
    def validate_price(self, key, value):
        if float(value) < 0:
            raise ValueError("Price must be a positive value")
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }