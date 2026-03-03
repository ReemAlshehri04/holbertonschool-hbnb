import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.services.Database.database import Base
from app.models import BaseModel

class Review(BaseModel, Base):
    __tablename__ = "reviews"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    _text = Column("text", String(1024), nullable=False)
    _rating = Column("rating", Integer, nullable=False)
    place_id = Column(String(36), ForeignKey("places.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="reviews")
    place = relationship("Place", back_populates="reviews_rel")


    def __init__(self, text, rating, place_id: str, user_id: str):
        super().__init__()
        self.text = text
        self.rating = rating

        if not place_id:
            raise ValueError("place_id is required")
        if not user_id:
            raise ValueError("user_id is required")

        self.place_id = str(place_id)
        self.user_id = str(user_id)

        self.created_at = None
        self.updated_at = None

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if not value or not str(value).strip():
            raise ValueError("text is required")
        self._text = str(value).strip()

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        try:
            v = int(value)
        except Exception:
            raise ValueError("rating must be an integer between 1 and 5")
        if not (1 <= v <= 5):
            raise ValueError("rating must be an integer between 1 and 5")
        self._rating = v

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
