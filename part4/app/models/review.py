import uuid
from sqlalchemy.orm import validates
from .basemodel import BaseModel
from app.extensions import db  # ✅ استيراد من extensions فقط


class Review(BaseModel):
    __tablename__ = "reviews"

    text = db.Column(db.String(1024), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey("places.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    # ✅ العلاقات
    user = db.relationship("User", back_populates="reviews")
    place = db.relationship("Place", back_populates="reviews")

    def __init__(self, text=None, rating=None, place_id=None, user_id=None, **kwargs):
        super().__init__(**kwargs)
        if text:
            self.text = text
        if rating is not None:
            self.rating = rating
        if place_id:
            self.place_id = place_id
        if user_id:
            self.user_id = user_id

    @validates('text')
    def validate_text(self, key, value):
        if not value or not str(value).strip():
            raise ValueError("Text is required")
        return str(value).strip()

    @validates('rating')
    def validate_rating(self, key, value):
        try:
            v = int(value)
        except (ValueError, TypeError):
            raise ValueError("Rating must be an integer between 1 and 5")
        if not (1 <= v <= 5):
            raise ValueError("Rating must be an integer between 1 and 5")
        return v

    def to_dict(self):
        return {
            'id': str(self.id),
            'text': self.text,
            'rating': self.rating,
            'user_id': str(self.user_id),
            'place_id': str(self.place_id),
            'created_at': self.created_at.isoformat() if getattr(self, 'created_at', None) else None,
            'updated_at': self.updated_at.isoformat() if getattr(self, 'updated_at', None) else None
        }