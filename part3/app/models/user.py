from app.models import BaseModel
from app import bcrypt
import re

class User(BaseModel):
    def __init__(self, email, password, first_name, last_name, is_admin=False, **kwargs):
        super().__init__(**kwargs)
        self.email = self.validate_email(email)
        self.password = password  # Hash this in the facade or here
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin

    @staticmethod
    def validate_email(email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")
        return email

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)
