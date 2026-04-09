from sqlalchemy.orm import validates
from .basemodel import BaseModel
from app.extensions import db

class Amenity(BaseModel):
    __tablename__ = "amenities"

    name = db.Column(db.String(50), nullable=False)
    
    # ✅ نستخدم اسم الكلاس "Place" كنص واسم الجدول الوسيط "place_amenity" كنص
    # هذا يمنع خطأ "name 'place_amenity' is not defined" ويفك الارتباط الدائري
    places = db.relationship(
        'Place', 
        secondary='place_amenity', 
        back_populates='amenities'
    )
    
    def __init__(self, name="", **kwargs):
        """
        Initialize Amenity entity
        """
        super().__init__(**kwargs)
        self.name = name

    @validates('name')
    def validate_name(self, key, value):
        """Ensure name is valid and not empty"""
        if not value or len(str(value).strip()) == 0:
            raise ValueError("Amenity name cannot be empty")
        if len(str(value)) > 50:
            raise ValueError("Amenity name must be under 50 characters")
        return str(value).strip()

    def to_dict(self):
        """
        Convert the model instance into a dictionary for API responses.
        """
        return {
            'id': str(self.id),
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }