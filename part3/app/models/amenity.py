from app.models import BaseModel

class Amenity(BaseModel):
    def __init__(self, name, **kwargs):
        """
        Initialize Amenity entity for Part 2
        """
        super().__init__(**kwargs)
        self.name = self.validate_name(name)

    @staticmethod
    def validate_name(name):
        """Ensure name is valid and not empty"""
        if not name or len(name.strip()) == 0:
            raise ValueError("Amenity name cannot be empty")
        if len(name) > 50:
            raise ValueError("Amenity name must be under 50 characters")
        return name

    def to_dict(self):
        """
        This method IS REQUIRED for the API and Facade to work.
        It fixes the 'MISSING' error in your evaluation.
        """
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
